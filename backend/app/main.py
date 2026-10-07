from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.config.settings import settings
from app.api.dataset import router as dataset_router
from app.api import xai
from app.api import prediction


# Create the FastAPI application
app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    description="Explainable AI for Business Intelligence",
    version=settings.PROJECT_VERSION
)


# Allow the React frontend to communicate with the FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(auth_router)
app.include_router(dataset_router)
app.include_router(xai.router)
app.include_router(prediction.router)


@app.get("/")
def home() -> dict:
    """
    Home endpoint to verify that the ExplainBI backend is running.
    """
    return {
        "message": "Welcome to ExplainBI 🚀",
        "status": "Backend is running successfully!",
        "version": settings.PROJECT_VERSION
    }