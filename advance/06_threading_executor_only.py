"""Concurrency with *threading* and *concurrent.futures* executors (no asyncio).

This script contrasts three approaches to running work in parallel:

1. **Manual Thread Creation** lower-level; you manage `Thread` objects and
   synchronisation primitives yourself.
2. **ThreadPoolExecutor** higher-level abstraction for I/O-bound work; the
   pool handles thread lifecycle and result collection via *Future*s.
3. **ProcessPoolExecutor** separate processes for CPU-bound tasks to bypass
   the GIL and utilise multiple CPU cores.

Key concepts illustrated:
• Submitting callables with `submit()` returning a *Future*.
• Attaching callbacks with `add_done_callback()`.
• Collecting results as they finish via `concurrent.futures.as_completed()`.

Run:
    python threading_executor_only.py
"""
from __future__ import annotations

import concurrent.futures as cf
import os
import random
import threading
import time
from typing import List

# ---------------------------- helpers ---------------------------------- #

def io_bound_task(x: int) -> str:
    """Pretend I/O-bound work executed synchronously."""
    delay = random.uniform(0.05, 0.3)
    time.sleep(delay)
    return f"io({x}) slept {delay*1000:.0f}ms on thread {threading.get_ident()}"


def cpu_bound_task(n: int = 5_000_000) -> int:
    """CPU-bound calculation: sum of squares up to n."""
    return sum(i * i for i in range(n))


def print_callback(label: str):
    """Return a callback that prints the result of a completed Future."""

    def _cb(fut: cf.Future):
        try:
            print(f"[callback:{label}] -> {fut.result()}")
        except Exception as exc:
            print(f"[callback:{label}] raised: {exc}")

    return _cb

# ---------------------------- demos ------------------------------------ #


def manual_thread_demo(values: List[int]) -> None:
    """Launch threads manually and wait for them."""
    print("\n--- Manual threading demo ---")

    def worker(val: int) -> None:
        result = io_bound_task(val)
        print(result)

    threads = [threading.Thread(target=worker, args=(v,)) for v in values]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def thread_pool_demo(values: List[int]) -> None:
    print("\n--- ThreadPoolExecutor demo (I/O-bound) ---")
    with cf.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(io_bound_task, v) for v in values]
        for f in futures:
            f.add_done_callback(print_callback("thread"))

        # Consume results in completion order
        for f in cf.as_completed(futures):
            _ = f.result()  # already printed by callback


def process_pool_demo(num_jobs: int) -> None:
    print("\n--- ProcessPoolExecutor demo (CPU-bound) ---")
    with cf.ProcessPoolExecutor() as executor:
        futures = [executor.submit(cpu_bound_task) for _ in range(num_jobs)]
        for f in futures:
            f.add_done_callback(print_callback("process"))

        for f in cf.as_completed(futures):
            _ = f.result()


# ---------------------------- main ------------------------------------ #


def main() -> None:
    random.seed(42)
    manual_thread_demo(list(range(5)))
    thread_pool_demo(list(range(10)))
    process_pool_demo(num_jobs=4)


if __name__ == "__main__":
    main() 