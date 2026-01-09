from typing import Any, Protocol, Type, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ModelWithId(Protocol):
    id: Any


class BaseRepository[T: ModelWithId]:
    def __init__(self, session: AsyncSession, model: Type[T]):
        self._session = session
        self._model = model

    async def save(self, obj: T) -> T:
        self._session.add(obj)
        return obj

    async def get(self, id_: Any) -> Optional[T]:
        if not hasattr(self._model, "id"):
            raise ValueError(f"Need id in model {self._model}")
        result = await self._session.execute(
            select(self._model).where(self._model.id == id_)
        )
        return result.scalar()
