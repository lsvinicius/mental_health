import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from src.api.conversation import router as conversation_router
from src.api.user import router as user_router


app = FastAPI(
    title="Mental Health Crisis Detection System",
    description="Event Sourcing + CQRS system for detecting mental health crises in conversations",
    version="0.1.0",
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
