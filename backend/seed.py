import asyncio

from app.db.base import Base
from app.db.session import engine


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Schema initialized")


if __name__ == "__main__":
    asyncio.run(seed())
