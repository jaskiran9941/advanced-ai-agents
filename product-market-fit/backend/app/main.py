"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import init_database
from app.api.routes import ideas, research, personas, chat

# Initialize database
init_database()

# Create FastAPI app
app = FastAPI(
    title="Product Market Fit API",
    description="API for product validation platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ideas.router, prefix="/api", tags=["ideas"])
app.include_router(research.router, prefix="/api", tags=["research"])
app.include_router(personas.router, prefix="/api", tags=["personas"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
def read_root():
    return {
        "message": "Product Market Fit API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.BACKEND_HOST, port=settings.BACKEND_PORT)
