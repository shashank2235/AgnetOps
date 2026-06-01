import asyncio
import json
import logging

from redis.asyncio import Redis
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.entities import AgentRun, RecoveryAction

logger = logging.getLogger(__name__)

STREAM = "agentops.lifecycle"
GROUP = "recovery-workers"
CONSUMER = "recovery-worker-1"


class RecoveryWorker:
    def __init__(self) -> None:
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def ensure_group(self) -> None:
        try:
            await self.redis.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
        except Exception:
            pass

    async def run_forever(self) -> None:
        await self.ensure_group()
        logger.info("recovery_worker_started")
        while True:
            response = await self.redis.xreadgroup(
                groupname=GROUP,
                consumername=CONSUMER,
                streams={STREAM: ">"},
                count=10,
                block=5000,
            )
            if not response:
                continue

            for _, events in response:
                for message_id, fields in events:
                    await self._handle(fields)
                    await self.redis.xack(STREAM, GROUP, message_id)

    async def _handle(self, fields: dict) -> None:
        event_type = fields.get("event_type", "")
        payload_raw = fields.get("payload", "{}")
        payload = json.loads(payload_raw)

        if event_type not in {"retry_requested", "rollback_requested", "replay_requested"}:
            return

        run_id = payload.get("run_id")
        if not run_id:
            return

        async with AsyncSessionLocal() as db:
            run = await db.get(AgentRun, run_id)
            if run is None:
                return

            if event_type == "retry_requested":
                run.status = "retrying"
                action_type = "retry"
                root = "Async retry job processed"
                to_step = None
            elif event_type == "rollback_requested":
                run.status = "rolled_back"
                action_type = "rollback"
                root = "Async rollback job processed"
                to_step = payload.get("target_step")
            else:
                run.status = "replaying"
                action_type = "replay"
                root = "Async replay with same inputs processed"
                to_step = payload.get("target_step")

            db.add(
                RecoveryAction(
                    run_id=run_id,
                    action_type=action_type,
                    from_step=payload.get("from_step"),
                    to_step=to_step,
                    root_cause_summary=root,
                    metadata_=payload,
                )
            )
            await db.commit()


async def main() -> None:
    worker = RecoveryWorker()
    await worker.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
