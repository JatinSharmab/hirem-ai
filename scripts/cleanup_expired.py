"""Delete expired anonymous rows. Run hourly as a scheduled maintenance job."""

import asyncio

from hireme_ai.db.repositories.workspaces import cleanup
from hireme_ai.db.session import engine


async def main() -> None:
    await cleanup()
    await engine.dispose()
    print("Expired workspace data and usage buckets removed.")


if __name__ == "__main__":
    asyncio.run(main())
