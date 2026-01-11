import pytest

from src.api.user import CreateUserRequest
from src.db.repositories.user import UserRepository


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(db_session, client):
    # given
    user_repository = UserRepository(db_session)

    # when
    payload = CreateUserRequest(username="vini", email="vini@vini.com")
    response = await client.post("/api/v1/users", json=payload.model_dump())

    # then
    assert response.status_code == 201
    user_id = response.json()["user_id"]
    users = await user_repository.all()

    assert len(users) == 1
    assert users[0].id == user_id
    assert users[0].name == "vini"
    assert users[0].email == "vini@vini.com"
