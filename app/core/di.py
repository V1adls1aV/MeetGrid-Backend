from redis.asyncio import Redis
from app.core import config
import inject


def _bind_redis(binder: inject.Binder) -> None:
    binder.bind(Redis, Redis.from_url(config.REDIS.URL))


def configure_di() -> None:
    inject.configure(_bind_redis)
