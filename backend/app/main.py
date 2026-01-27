from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .config import config
from .routes import voice_router, generation_router

# Create FastAPI application
app = FastAPI(
    title="TTS Voice Cloning API",
    description="Text-to-Speech API with voice cloning capabilities using MLX/PyTorch",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voice_router)
app.include_router(generation_router)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "TTS Voice Cloning API",
        "version": "0.2.0",
        "backend": config.BACKEND,
        "platform": f"{config.SYSTEM} {config.MACHINE}",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "backend": config.BACKEND,
        "platform": config.SYSTEM,
        "machine": config.MACHINE
    }


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print(f"Starting TTS API server...")
    print(f"Platform: {config.SYSTEM} {config.MACHINE}")
    print(f"Backend: {config.BACKEND}")
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Voices directory: {config.VOICES_DIR}")
    print(f"Generations directory: {config.GENERATIONS_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print("Shutting down TTS API server...")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
