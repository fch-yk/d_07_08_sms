import asyncio
import os

import aioredis
from dotenv import load_dotenv


async def main():
    redis = aioredis.from_url(
        os.getenv('SMSC_REDIS_URL'), decode_responses=True
    )
    await redis.set("my-phone", 333111)
    value = await redis.get("my-phone")
    print(value)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
