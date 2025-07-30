# Asyncio example showing awaitable coroutines and parallel HTTP fetches.
# Requires: pip install aiohttp
# Run: python asyncio_example.py

import asyncio
import time
from typing import List

import aiohttp

URLS: List[str] = ["https://www.example.com"] * 10


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        text = await response.text()
        print(f"Downloaded {url} ({len(text)} bytes)")
        return text


async def main() -> None:
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in URLS]
        await asyncio.gather(*tasks)
    end = time.perf_counter()
    print(f"Fetched {len(URLS)} pages in {end - start:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main()) 