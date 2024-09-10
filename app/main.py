from contextlib import asynccontextmanager

from aiocache.serializers import PickleSerializer
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqladmin import Admin

from .database import Base, engine
from .service.admin_panel import admin_panel_apply
from .service.redis_service import get_redis, get_cache
from .utils.middlewares import handle_integrity_errors
from app.user.routes import user_router
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load the redis connection
    _app.redis = await get_redis()

    try:

        redis_cache = await get_cache()
        FastAPICache.init(RedisBackend(redis_cache), prefix="fastapi-cache")
        yield

    finally:
        await _app.redis.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(BaseHTTPMiddleware, dispatch=handle_integrity_errors)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

app.include_router(user_router)

admin = Admin(app, Base)

admin_panel_apply(admin)
