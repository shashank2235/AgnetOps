import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError

from app.api.routes.agents import router as agents_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.checkpoints import router as checkpoints_router
from app.api.routes.platform import router as platform_router
from app.core.logging import configure_logging
from app.core.telemetry import configure_tracing
from app.db.base import Base
from app.db.session import engine


async def wait_for_database(timeout_seconds: int = 60) -> None:
    deadline = asyncio.get_event_loop().time() + timeout_seconds
    last_error: Exception | None = None

    while True:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except OperationalError as exc:
            last_error = exc
            if asyncio.get_event_loop().time() >= deadline:
                raise last_error
            await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    configure_tracing()
    await wait_for_database()
    yield


app = FastAPI(title="AgentOps Runtime", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router, prefix="/api/v1")
app.include_router(checkpoints_router, prefix="/api/v1")
app.include_router(approvals_router, prefix="/api/v1")
app.include_router(platform_router, prefix="/api/v1")

FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
