# main 파일
from fastapi import FastAPI

from app.api.recommendations import router as recommendations_router


app = FastAPI(
    title="Recopo AI Server",
    description="GitHub repository recommendation API server",
    version="0.1.0",
)


@app.get("/")
def root() -> dict:
    return {"message": "Recopo AI Server is running"}


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(recommendations_router)