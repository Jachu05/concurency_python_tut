"""Asyncio race-condition demonstration.

Run:
    python asyncio_race_condition.py [num_tasks]

The script launches many concurrent coroutines that increment a shared
counter.  In the *unsafe* version we insert an ``await`` between reading and
writing the counter so the scheduler can switch tasks, causing lost updates
and an incorrect final value.

The *safe* version protects the critical section with ``asyncio.Lock`` so the
final counter equals the number of tasks.
"""
from __future__ import annotations

import asyncio
import sys
from typing import Optional

# Type alias for readability
Number = int


async def unsafe_increment(counter: list[Number]) -> None:
    """Increment shared counter without locking (race condition expected)."""
    tmp = counter[0]               # read
    await asyncio.sleep(0.01)         # yield to event-loop (context switch)
    counter[0] = tmp + 1           # write – another task may have overwritten tmp


async def safe_increment(counter: list[Number], lock: asyncio.Lock) -> None:
    """Increment shared counter safely using a lock."""
    async with lock:
        counter[0] += 1


async def run_test(num_tasks: int = 1000) -> None:
    print(f"Running UNSAFE test with {num_tasks} tasks …")
    shared_counter = [0]  # use list for mutability across coroutines
    tasks = [unsafe_increment(shared_counter) for _ in range(num_tasks)]
    await asyncio.gather(*tasks)
    print(f"  Expected {num_tasks}, got {shared_counter[0]}  (lost {num_tasks - shared_counter[0]})\n")

    print("Running SAFE test with asyncio.Lock …")
    shared_counter = [0]
    lock = asyncio.Lock()
    tasks = [safe_increment(shared_counter, lock) for _ in range(num_tasks)]
    await asyncio.gather(*tasks)
    print(f"  Expected {num_tasks}, got {shared_counter[0]}  (all increments accounted for)")


if __name__ == "__main__":
    # Optional CLI arg for task count
    tasks_arg: Optional[str] = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        num = int(tasks_arg) if tasks_arg else 1000
    except (TypeError, ValueError):
        print("[!] num_tasks must be an integer")
        sys.exit(1)

    asyncio.run(run_test(num)) 