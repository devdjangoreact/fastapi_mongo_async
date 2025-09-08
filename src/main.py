from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import close_db, init_db
from .core.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await init_db()

        await setup_scheduler_and_routers()

        log.success("Application started successfully")

    except Exception as e:
        log.error(f"Failed to start application: {str(e)}")
        raise

    yield

    # Shutdown
    try:
        await close_db()
        log.info("Application shutdown complete")
    except Exception as e:
        log.error(f"Error during shutdown: {str(e)}")


app = FastAPI(
    title="Hotline Parser API",
    description="Async service for parsing products and news",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hotline Parser API"}


# Import routers after app creation to avoid circular imports
async def setup_scheduler_and_routers():
    from .core.auth import get_api_key
    from .routers import admin, news, products
    from .services.scheduler import scheduler_service

    # Import and initialize scheduler after database is ready
    # await scheduler_service.start_scheduler()
    # Include routers with dependencies
    app.include_router(
        products.router,
        prefix="/products",
        tags=["products"],
        dependencies=[Depends(get_api_key)],
    )
    app.include_router(
        news.router,
        prefix="/news",
        tags=["news"],
        dependencies=[Depends(get_api_key)],
    )
    app.include_router(
        admin.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=[Depends(get_api_key)],
    )

    log.success("Routers initialized successfully")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
