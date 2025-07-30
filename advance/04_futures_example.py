"""Demonstrates the basics of *Future* objects via `concurrent.futures`.

Key points illustrated:
1. Submitting callables to both `ThreadPoolExecutor` (I/O-bound) and
   `ProcessPoolExecutor` (CPU-bound).
2. The *Future* object returned by `submit()` representing an eventual result.
3. Attaching callbacks to Futures with `add_done_callback()`.
4. Gathering results as they complete using `concurrent.futures.as_completed()`.

Run:
    python futures_example.py
"""
from __future__ import annotations

import concurrent.futures as cf
import os
import random
import time
from typing import List

# ---------------------------- helpers ---------------------------------- #

def io_bound_task(x: int) -> str:
    """Pretend I/O by sleeping a random amount of time and returning a string."""
    delay = random.uniform(0.05, 0.3)
    time.sleep(delay)
    return f"io({x}) slept {delay*1000:.0f}ms on thread {os.getpid()}"


def cpu_bound_task(n: int = 5_000_000) -> int:
    """CPU-bound task: compute sum of squares; expensive for demonstration."""
    return sum(i * i for i in range(n))


def print_callback(label: str):
    """Return a callback that prints the result of a completed future."""

    def _callback(fut: cf.Future):
        try:
            result = fut.result()
            print(f"[callback:{label}] -> {result}")
        except Exception as exc:
            print(f"[callback:{label}] raised: {exc}")

    return _callback


# ---------------------------- main demo -------------------------------- #

def thread_pool_demo(values: List[int]) -> None:
    print("\n--- ThreadPoolExecutor demo (simulated I/O) ---")
    with cf.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(io_bound_task, v) for v in values]
        # Attach a callback to every future to print when done
        for f in futures:
            f.add_done_callback(print_callback("thread"))

        # as_completed yields futures in completion order
        for f in cf.as_completed(futures):
            # Extra handling if we need result in main loop
            _ = f.result()  # already printed by callback


def process_pool_demo(num_jobs: int) -> None:
    print("\n--- ProcessPoolExecutor demo (CPU-bound) ---")
    with cf.ProcessPoolExecutor() as executor:
        futures = [executor.submit(cpu_bound_task) for _ in range(num_jobs)]
        for f in futures:
            f.add_done_callback(print_callback("process"))

        for f in cf.as_completed(futures):
            _ = f.result()


if __name__ == "__main__":
    random.seed(42)
    thread_pool_demo(list(range(10)))
    process_pool_demo(num_jobs=4) 