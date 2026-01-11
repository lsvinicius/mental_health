import functools
from typing import Annotated, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from src.command.conversation import ConversationCommandHandler
from src.db.repositories.conversation_analysis import ConversationRiskAnalysisRepository
from src.db.repositories.user import UserRepository
from src.genai.risk_analyzer import RiskAnalyzer
from src.genai.risk_analyzer_clients.analyzer_client_factory import (
    create_analyzer_client,
    AnalyzerClientProvider,
)
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


def get_risk_analyzer_creator(
    session: AsyncSession = Depends(get_db_session),
) -> Callable[[str], RiskAnalyzer]:
    def _risk_analyzer_creator(model: str) -> RiskAnalyzer:
        analyzer_client = create_analyzer_client(
            provider=AnalyzerClientProvider.google_genai,
            api_key=settings.google_api_key,
            model=model,
        )
        return RiskAnalyzer(session, analyzer_client)

    return _risk_analyzer_creator


ConversationCommandHandlerDependency = Annotated[
    ConversationCommandHandler, Depends(get_conversation_command_handler)
]

ConversationQueryHandlerDependency = Annotated[
    ConversationQueryHandler, Depends(get_conversation_query_handler)
]

UserRepositoryDependency = Annotated[UserRepository, Depends(get_user_repository)]


RiskAnalyzerCreatorDependency = Annotated[
    Callable[[str], RiskAnalyzer], Depends(get_risk_analyzer_creator)
]


ConversationRiskAnalysisRepositoryDependency = Annotated[
    ConversationRiskAnalysisRepository,
    Depends(get_conversation_risk_analysis_repository),
]
