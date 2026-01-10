import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from src.api.conversation import router


app = FastAPI(
    title="Mental Health Crisis Detection System",
    description="Event Sourcing + CQRS system for detecting mental health crises in conversations",
    version="0.1.0",
)


app.include_router(router, prefix="/api/v1", tags=["conversations"])


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
