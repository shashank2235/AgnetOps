import json
import logging

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class EventBusService:
    def __init__(self) -> None:
        self.stream_name = "agentops.lifecycle"
        self._client: Redis | None = None

    async def _get_client(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(settings.redis_url, decode_responses=True)
        return self._client

    async def publish(self, event_type: str, payload: dict) -> None:
        try:
            client = await self._get_client()
            await client.xadd(self.stream_name, {"event_type": event_type, "payload": json.dumps(payload)})
        except Exception as exc:  # pragma: no cover
            logger.warning("event_publish_failed", extra={"event_type": event_type, "error": str(exc)})
