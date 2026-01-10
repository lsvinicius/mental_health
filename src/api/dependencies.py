from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from src.command.conversation import ConversationCommandHandler
from src.query.conversation import ConversationQueryHandler
from src.settings import settings

engine = create_async_engine(settings.db_connection_string, echo=settings.log_db)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def get_db_session() -> AsyncSession:
    return async_session()


def get_conversation_command_handler() -> ConversationCommandHandler:
    return ConversationCommandHandler(get_db_session())


def get_conversation_query_handler() -> ConversationQueryHandler:
    return ConversationQueryHandler(get_db_session())


ConversationCommandHandlerDependency = Annotated[
    ConversationCommandHandler, Depends(get_conversation_command_handler)
]

ConversationQueryHandlerDependency = Annotated[
    ConversationQueryHandler, Depends(get_conversation_query_handler)
]
