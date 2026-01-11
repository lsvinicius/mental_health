import asyncio
import datetime
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.event import EventType
from src.db.repositories.conversation import ConversationRepository
from src.db.repositories.conversation_outbox import ConversationOutboxRepository
from src.genai.risk_analyzer import RiskAnalyzer
from src.genai.risk_analyzer_clients.analyzer_client_factory import (
    create_analyzer_client,
    AnalyzerClientProvider,
)
from src.projector.conversation import ConversationProjector
from src.settings import settings


logger = logging.getLogger(__name__)


async def _do_risk_analysis(
    session: AsyncSession, conversation_id: str, prompt_path: str
) -> None:
    ai_client = create_analyzer_client(
        AnalyzerClientProvider.google_genai,
        api_key=settings.google_api_key,
        model_id="gemini-2.5-flash-lite",
    )
    risk_analyzer = RiskAnalyzer(session, ai_client, prompt_path)
    try:
        await risk_analyzer.analyze(conversation_id)
    except Exception as e:
        logger.error(f"Cannot do risk analysis. Error happened when processing: {e}")


class OutboxProcessor:
    def __init__(
        self,
        session: AsyncSession,
        analyze_request_timeout: int = 5,
        prompt_path: Optional[str] = None,
    ):
        self._session = session
        self._outbox_repository = ConversationOutboxRepository(session)
        self._projector = ConversationProjector(session)
        self._conversation_repository = ConversationRepository(session)
        self._analyze_request_timeout = analyze_request_timeout
        self._prompt_path = prompt_path or str(
            Path.cwd() / ".." / "prompts" / "risk_analyzer.yaml"
        )

    async def process_and_send_to_risk_analyzer(
        self, forever: bool = True, interval: int = 5
    ) -> None:
        logger.info(f"Starting to process forever={forever} messages")
        if forever:
            while True:
                logger.info(f"Processing messages...")
                await self._process_and_send_to_risk_analyzer()
                logger.info(f"Will wait for next {interval} seconds")
                await asyncio.sleep(interval)
        else:
            await self._process_and_send_to_risk_analyzer()
        logger.info("OutboxProcessor exiting...")

    async def _process_and_send_to_risk_analyzer(self) -> None:
        async with self._session.begin():
            to_be_analyzed = await self._process()
            async with asyncio.TaskGroup() as tg:
                for conversation_id in to_be_analyzed:
                    # I hope this doesn't have same issue as asyncio.create_task
                    # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
                    tg.create_task(
                        _do_risk_analysis(
                            self._session, conversation_id, self._prompt_path
                        )
                    )

    async def _process(self) -> list[str]:
        outboxes = await self._outbox_repository.all_unprocessed()
        to_be_analyzed = {}
        failed_to_be_processed: dict[str, bool] = {}
        for outbox in outboxes:
            if failed_to_be_processed.get(outbox.event.conversation_id):
                continue
            if outbox.event.type == EventType.NEW_MESSAGE:
                to_be_analyzed[outbox.event.conversation_id] = True
            elif (
                outbox.event.type == EventType.CONVERSATION_DELETED
                and to_be_analyzed.get(outbox.event.conversation_id)
            ):
                to_be_analyzed[outbox.event.conversation_id] = False
            try:
                await self._projector.project(outbox)
            except Exception as e:
                logger.exception(f"Error happened when processing {outbox}: {e}")
                failed_to_be_processed[outbox.event.conversation_id] = True
            else:
                outbox.is_processed = True
                outbox.updated_at = datetime.datetime.now(datetime.UTC)
                self._session.add(outbox)
        return [conv_id for conv_id, analyze in to_be_analyzed.items() if analyze]
