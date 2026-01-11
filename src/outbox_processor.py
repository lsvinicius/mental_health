import argparse
import asyncio
import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

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


async def _do_risk_analysis(session: AsyncSession, conversation_id: str) -> None:
    ai_client = create_analyzer_client(
        AnalyzerClientProvider.google_genai,
        api_key=settings.google_api_key,
        model_id="gemini-2.5-flash-lite",
    )
    risk_analyzer = RiskAnalyzer(session, ai_client)
    try:
        await risk_analyzer.analyze(conversation_id)
    except Exception as e:
        logger.error(f"Cannot do risk analysis. Error happened when processing: {e}")


class OutboxProcessor:
    def __init__(
        self, session: AsyncSession, api_base_url: str, analyze_request_timeout: int = 5
    ):
        self._session = session
        self._outbox_repository = ConversationOutboxRepository(session)
        self._projector = ConversationProjector(session)
        self._conversation_repository = ConversationRepository(session)
        self._analyze_request_timeout = analyze_request_timeout
        self._api_base_url = api_base_url

    async def process_and_send_to_risk_analyzer(
        self, forever: bool = True, interval: int = 5
    ) -> None:
        if forever:
            while True:
                await self._process_and_send_to_risk_analyzer()
                await asyncio.sleep(interval)
        else:
            await self._process_and_send_to_risk_analyzer()

    async def _process_and_send_to_risk_analyzer(self) -> None:
        async with self._session.begin():
            to_be_analyzed = await self._process()
            async with asyncio.TaskGroup() as tg:
                for conversation_id in to_be_analyzed:
                    # I hope this doesn't have same issue as asyncio.create_task
                    # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
                    tg.create_task(_do_risk_analysis(self._session, conversation_id))

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


async def start(
    forever: bool = True, interval: int = 5, analyze_request_timeout: int = 5
):
    engine = create_async_engine(settings.db_connection_string, echo=settings.log_db)
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    api_base_url = settings.api_base_url
    async with async_session() as session:
        await OutboxProcessor(
            session, api_base_url, analyze_request_timeout
        ).process_and_send_to_risk_analyzer(forever, interval)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Outbox Processor - Process events and send to risk analyzer"
    )
    parser.add_argument(
        "--forever",
        action="store_true",
        default=False,
        help="Run continuously in a loop (default: False, run once)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Interval in seconds between processing cycles when running forever (default: 5)",
    )
    parser.add_argument(
        "--analyze-request-timeout",
        type=int,
        default=5,
        help="Amount of seconds to wait for a risk analysis request (default: 5)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logger.info(
        f"Starting Outbox Processor (forever={args.forever}, interval={args.interval}s)"
    )
    asyncio.run(
        start(
            forever=args.forever,
            interval=args.interval,
            analyze_request_timeout=args.analyze_request_timeout,
        )
    )
