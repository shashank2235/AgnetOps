import asyncio

from app.workers.recovery_worker import main


if __name__ == "__main__":
    asyncio.run(main())
