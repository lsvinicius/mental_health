import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.api.dependencies import get_db_session
from src.api.schemas.conversation import SendMessageRequest
from src.api.user import CreateUserRequest
from src.db.models.base import Base
from src.main import app

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer


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


@pytest.fixture
def base_url():
    return "http://test"


@pytest_asyncio.fixture
async def client(db_session, base_url):
    transport = ASGITransport(app=app)
    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=transport, base_url=base_url) as ac:
        yield ac


@pytest_asyncio.fixture
async def create_user(db_session, client):
    async def _create_user(username, email):
        payload = CreateUserRequest(username=username, email=email)
        response = await client.post("/api/v1/users", json=payload.model_dump())
        return response.json()

    return _create_user


@pytest_asyncio.fixture
async def create_conversation(db_session, client):
    async def _setup_conversation(user_id) -> dict:
        response = await client.post(f"/api/v1/{user_id}/conversations")
        return response.json()

    return _setup_conversation


@pytest_asyncio.fixture
async def create_message(db_session, client):
    async def _new_conversation(user_id, conversation_id, text, sender) -> dict:
        payload = SendMessageRequest(text=text, sender=sender)
        response = await client.post(
            f"/api/v1/{user_id}/conversations/{conversation_id}/messages",
            json=payload.model_dump(),
        )
        return response.json()

    return _new_conversation
