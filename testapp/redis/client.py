import json
import logging
import redis

from .constants import (
    DEFAULT_TTL_SECONDS,
    JsonSerializable,
    Namespace,
)

logger = logging.getLogger(__name__)


# This is a singleton client that will be shared across all Redis instances.
_redis_client = redis.Redis(
    host="redis.redis.svc.cluster.local",
    port=6379,
    ssl=False,
    db=0,
    socket_timeout=5,
    socket_connect_timeout=5,
    socket_keepalive=True,
)


class Redis:
    """
    Wrapper around redis.Redis with namespaced keys and JSON serialization.

    Only use this class to interact with Redis, to ensure a shared
    client for connection pooling and key namespacing.
    """

    def __init__(self, namespace: Namespace):
        self.client = _redis_client
        self.namespace = namespace

    def get(
        self, key: str, default: JsonSerializable = None
    ) -> JsonSerializable:
        """
        Redis GET with JSON deserialization and namespaced key.
        """
        if value := self.client.get(self.__key_with_namespace(key)):
            return json.loads(value)  # type: ignore
        return default

    def set(
        self, key: str, value: JsonSerializable, ttl: int = DEFAULT_TTL_SECONDS
    ) -> None:
        """
        Redis SET with expiration, JSON serialization and namespaced key.
        """
        self.client.set(self.__key_with_namespace(key), json.dumps(value), ex=ttl)

    def delete(self, key: str) -> None:
        """
        Redis DEL with namespaced key.
        """
        self.client.delete(self.__key_with_namespace(key))

    def incr(self, key: str, amount: int = 1) -> int:
        """
        Redis INCRBY with namespaced key.
        """
        return int(self.client.incr(self.__key_with_namespace(key), amount=amount))  # type: ignore

    def setex(self, key: str, ttl: int, value: JsonSerializable) -> None:
        """
        Redis SETEX with namespaced key.
        """
        self.client.setex(self.__key_with_namespace(key), ttl, json.dumps(value))

    def __key_with_namespace(self, key: str) -> str:
        return f"{self.namespace.value}:{key}"