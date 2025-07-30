"""Illustrates nondeterministic ordering of list appends in asyncio.

Run:
    python asyncio_ordering_example.py [num_tasks]

We launch several coroutines that *append* their identifier to a shared list
after awaiting a random sleep.  Because they wake up at different times, the
resulting list order generally differs from the natural numeric order.
"""
from __future__ import annotations

import asyncio
import random
import sys
from typing import List, Optional


def parse_cli_int(default: int = 20) -> int:
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            print("Argument must be an integer; falling back to default.")
    return default


async def unordered_append(shared: List[int], value: int) -> None:
    # Random sleep to scramble completion order
    await asyncio.sleep(random.random() * 0.05)
    shared.append(value)


async def ordered_insert(shared: List[Optional[int]], value: int, index: int, lock: asyncio.Lock) -> None:
    # Random sleep again; but we lock and write to a fixed index, preserving order
    await asyncio.sleep(random.random() * 0.05)
    shared[index] = value


async def main() -> None:
    n = parse_cli_int()

    print(f"Running UNORDERED test with {n} tasks …")
    results: List[int] = []
    await asyncio.gather(*(unordered_append(results, i) for i in range(n)))
    print("Unordered result:", results)
    print()

    print("Running ORDERED test with asyncio.Lock and fixed indices …")
    ordered: List[Optional[int]] = [None] * n
    lock = asyncio.Lock()
    await asyncio.gather(*(ordered_insert(ordered, i, i, lock) for i in range(n)))
    print("Ordered result:", ordered)


if __name__ == "__main__":
    asyncio.run(main()) 