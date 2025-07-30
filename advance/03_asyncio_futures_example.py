"""Demonstrates the basics of asyncio.Future and Task objects.

Key points illustrated:
1. Scheduling coroutines with asyncio.create_task() which returns a Task (subclass of Future).
2. Creating a bare asyncio.Future and resolving it from another coroutine.
3. Attaching callbacks to Futures with add_done_callback().
4. Gathering results as they complete using asyncio.as_completed().

Run:
    python asyncio_futures_example.py
"""
from __future__ import annotations

import asyncio
import random
from typing import List

# ---------------------------- helpers ---------------------------------- #

async def async_io_task(x: int) -> str:
    """Simulated async I/O by awaiting on asyncio.sleep()."""
    delay = random.uniform(0.05, 0.3)
    await asyncio.sleep(delay)
    return f"async_io({x}) slept {delay*1000:.0f}ms"


def print_callback(label: str):
    """Return a callback that prints the result of a completed Future/Task."""

    def _callback(fut: asyncio.Future):
        try:
            result = fut.result()
            print(f"[callback:{label}] -> {result}")
        except Exception as exc:
            print(f"[callback:{label}] raised: {exc}")

    return _callback


# ---------------------------- demo sections ---------------------------- #

async def task_demo(values: List[int]) -> None:
    print("\n--- asyncio.create_task demo (simulated I/O) ---")
    tasks: List[asyncio.Task] = [asyncio.create_task(async_io_task(v)) for v in values]

    # Attach a callback to every task to print when done
    for t in tasks:
        t.add_done_callback(print_callback("task"))

    # asyncio.as_completed yields awaitables in completion order
    for coro in asyncio.as_completed(tasks):
        await coro  # result already printed by callback


async def bare_future_demo() -> None:
    print("\n--- Bare asyncio.Future demo ---")
    loop = asyncio.get_running_loop()
    fut: asyncio.Future[str] = loop.create_future()

    async def compute_and_set() -> None:
        await asyncio.sleep(0.1)
        fut.set_result("bare Future resolved by compute_and_set()")

    # Schedule helper coroutine
    asyncio.create_task(compute_and_set())

    # Register callback and await the future
    fut.add_done_callback(print_callback("bare"))
    result = await fut
    print(f"awaited bare Future got: {result}")


async def main() -> None:
    random.seed(42)
    await task_demo(list(range(10)))
    await bare_future_demo()


if __name__ == "__main__":
    asyncio.run(main()) 