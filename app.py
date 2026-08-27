import asyncio
import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Delivery Lab Service",
    version=os.getenv("APP_VERSION", "dev"),
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/")
async def index():
    return {
        "service": "delivery-lab",
        "version": os.getenv("APP_VERSION", "dev"),
        "status": "operational"
    }


@app.get("/health/live")
async def live():
    """Liveness probe endpoint - checks only if process is running"""
    return {"alive": True, "status": "ok"}


@app.get("/health/ready")
async def ready():
    """Readiness probe endpoint - checks if app is ready to serve traffic"""
    # Check external dependencies (none in this app)
    # Could check database connection, etc.
    
    if os.getenv("READY", "true") != "true":
        return JSONResponse(
            {"ready": False, "status": "unavailable"},
            status_code=503
        )
    return {"ready": True, "status": "ok"}


@app.get("/work")
async def work():
    """Simulates work with configurable delay"""
    delay = float(os.getenv("WORK_DELAY", "0"))
    if delay > 0:
        await asyncio.sleep(delay)
    return {"ok": True, "processed": True, "delay_seconds": delay}


@app.get("/config")
async def get_config():
    """Debug endpoint to show current configuration"""
    return {
        "app_version": os.getenv("APP_VERSION", "dev"),
        "work_delay": os.getenv("WORK_DELAY", "0"),
        "ready": os.getenv("READY", "true"),
        "port": os.getenv("PORT", "8080")
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )