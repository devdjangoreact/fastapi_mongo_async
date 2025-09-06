from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.auth import get_api_key
from .core.config import settings
from .core.database import init_db
from .routers import news, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Hotline Parser API",
    description="Async service for parsing products and news",
    version="0.1.0",
    lifespan=lifespan,
    dependencies=[Depends(get_api_key)],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(news.router, prefix="/news", tags=["news"])


@app.get("/")
async def root():
    return {"message": "Hotline Parser API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
