import pytest
import asyncio

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer

from src.api.dependencies import get_db_session
from src.db.models.base import Base
from src.main import app
from src.db.models.conversation import Conversation
from src.db.models.user import User
from src.db.models.event import ConversationEvent
from src.db.models.conversation_outbox import ConversationOutbox

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer


# 1. Garante um único loop para toda a sessão de testes
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def postgres_url():
    with PostgresContainer("postgres:16-alpine") as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        url = f"postgresql+asyncpg://{postgres.username}:{postgres.password}@{host}:{port}/{postgres.dbname}"
        yield url


@pytest_asyncio.fixture(scope="session")
async def engine(postgres_url):
    # Criamos a engine no escopo de sessão
    engine = create_async_engine(postgres_url, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    # Abrimos uma conexão física com o banco
    connection = await engine.connect()

    # Iniciamos uma transação real no banco
    transaction = await connection.begin()

    # Criamos a sessão vinculada a ESTA conexão específica
    # join_transaction_mode="create_savepoint" faz com que qualquer
    # session.commit() no seu código de produção apenas libere um SAVEPOINT,
    # mantendo a transação externa aberta para nós.
    Session = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with Session() as session:
        yield session
        # Após o teste sair do contexto, limpamos TUDO
        await session.rollback()

    # Rollback na transação externa garante limpeza total
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def client(db_session):
    transport = ASGITransport(app=app)
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
