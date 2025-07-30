"""Demonstrates bridging between synchronous (blocking) and asynchronous code using executors.

Key concepts illustrated:
1. Running blocking (sync) functions from async code using `loop.run_in_executor`.
2. Using asyncio event loop to offload I/O-bound synchronous work to a thread pool.
3. Collecting results as they complete with `asyncio.as_completed`.

Run:
    python asyncio_executor_bridge.py
"""
from __future__ import annotations

import asyncio
import concurrent.futures as cf
import random
import time
from typing import List

# ---------------------------- helpers ---------------------------------- #

def blocking_io(x: int) -> str:
    """Pretend I/O-bound work executed *synchronously*."""
    delay = random.uniform(0.05, 0.3)
    time.sleep(delay)
    return f"blocking_io({x}) slept {delay*1000:.0f}ms on thread"


async def async_compute(x: int) -> str:
    """A trivial coroutine that awaits on asyncio.sleep()."""
    delay = random.uniform(0.05, 0.3)
    await asyncio.sleep(delay)
    return f"async_compute({x}) slept {delay*1000:.0f}ms inside event-loop"


# ------------------ Run *sync* code from *async* -------------------- #

async def demo_run_blocking_in_async(values: List[int]) -> None:
    print("\n--- Running blocking functions in async context ---")

    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, blocking_io, v) for v in values]

    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(result)


# ---------------------------- main ------------------------------------ #


def main() -> None:
    random.seed(42)

    # async → sync (run blocking code in a thread pool)
    asyncio.run(demo_run_blocking_in_async(list(range(10))))


if __name__ == "__main__":
    main() 