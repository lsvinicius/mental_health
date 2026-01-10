from fastapi import APIRouter
from pydantic import BaseModel

from src.api.dependencies import UserRepositoryDependency
from src.db.models.user import User
from src.db.models.conversation import Conversation

router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    email: str


@router.post("/users", status_code=201)
async def new_user(
    request: CreateUserRequest,
    user_repository: UserRepositoryDependency,
):
    """Start a new conversation."""
    user = User(email=request.email, name=request.username)
    async with user_repository.session.begin():
        user = await user_repository.save(user)
    return {
        "user_id": user.id,
    }
