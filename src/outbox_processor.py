import asyncio
import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.db.models.event import EventType
from src.db.repositories.conversation_outbox import ConversationOutboxRepository
from src.projector.conversation import ConversationProjector
from src.settings import settings


logger = logging.getLogger(__name__)


class OutboxProcessor:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._outbox_repository = ConversationOutboxRepository(session)
        self._projector = ConversationProjector(session)

    async def process_and_send_to_risk_analyzer(
        self, forever: bool = True, interval: int = 5
    ) -> None:
        if forever:
            await self._process_and_send_to_risk_analyzer()
            while True:
                await asyncio.sleep(interval)
        else:
            await self._process_and_send_to_risk_analyzer()

    async def _process_and_send_to_risk_analyzer(self) -> None:
        to_be_analyzed = await self._process()

        async def request_conversation_risk_analysis(conversation_id_: str):
            pass

        async with asyncio.TaskGroup() as tg:
            for conversation_id in to_be_analyzed:
                # I hope this doesn't have same issue as asyncio.create_task
                # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
                tg.create_task(request_conversation_risk_analysis(conversation_id))

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


async def start(forever: bool = True, interval: int = 5):
    engine = create_async_engine(settings.db_connection_string, echo=settings.log_db)
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        async with session.begin():
            await OutboxProcessor(session).process_and_send_to_risk_analyzer(
                forever, interval
            )


if __name__ == "__main__":
    asyncio.run(start(forever=False))
