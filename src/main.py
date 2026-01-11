import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from src.api.conversation import router as conversation_router
from src.api.dependencies import async_session
from src.api.user import router as user_router
from src.outbox_processor import OutboxProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Start outbox processor in background
    session = async_session()
    processor = OutboxProcessor(session)
    task = asyncio.create_task(
        processor.process_and_send_to_risk_analyzer(forever=True, interval=5)
    )

    yield

    # Shutdown: Cancel background task and cleanup
    task.cancel()
    try:
        await task
    except Exception:
        pass
    await session.close()


app = FastAPI(
    title="Mental Health Crisis Detection System",
    description="Event Sourcing + CQRS system for detecting mental health crises in conversations",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(conversation_router, prefix="/api/v1", tags=["conversations"])
app.include_router(user_router, prefix="/api/v1", tags=["user"])


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
