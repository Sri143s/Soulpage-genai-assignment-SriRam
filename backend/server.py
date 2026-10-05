import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import router
from common.config import settings
from common.logging_config import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title="Soulpage GenAI Multi-Agent & Knowledge Bot API",
        description="Production-quality technical assignment API featuring LangGraph Multi-Agent Company Intelligence and Conversational Knowledge Bot.",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app

app = create_app()

def start_server():
    logger.info(f"Starting FastAPI server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

if __name__ == "__main__":
    start_server()
