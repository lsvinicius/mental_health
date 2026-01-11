from typing import Any, Protocol, Type, Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class ModelWithId(Protocol):
    id: Any


class BaseRepository[T: ModelWithId]:
    def __init__(self, session: AsyncSession, model: Type[T]):
        self._session = session
        self._model = model

    @property
    def session(self) -> AsyncSession:
        return self._session

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

    async def all(self) -> List[T]:
        result = await self._session.execute(select(self._model))
        return list(result.scalars().all())

    async def update(self, id_: Any, **kwargs) -> None:
        stmt = update(self._model).where(self._model.id == id_).values(**kwargs)
        await self._session.execute(stmt)
