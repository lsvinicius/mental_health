from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from src.command.conversation import ConversationCommandHandler
from src.db.repositories.conversation_analysis import ConversationRiskAnalysisRepository
from src.db.repositories.user import UserRepository
from src.query.conversation import ConversationQueryHandler
from src.settings import settings

engine = create_async_engine(settings.db_connection_string, echo=settings.log_db)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session():
    async with async_session() as session:
        yield session


def get_conversation_command_handler(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationCommandHandler:
    return ConversationCommandHandler(session)


def get_conversation_query_handler(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationQueryHandler:
    return ConversationQueryHandler(session)


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(session)


def get_conversation_risk_analysis_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationRiskAnalysisRepository:
    return ConversationRiskAnalysisRepository(session)


ConversationCommandHandlerDependency = Annotated[
    ConversationCommandHandler, Depends(get_conversation_command_handler)
]

ConversationQueryHandlerDependency = Annotated[
    ConversationQueryHandler, Depends(get_conversation_query_handler)
]

UserRepositoryDependency = Annotated[UserRepository, Depends(get_user_repository)]


ConversationRiskAnalysisRepositoryDependency = Annotated[
    ConversationRiskAnalysisRepository,
    Depends(get_conversation_risk_analysis_repository),
]
