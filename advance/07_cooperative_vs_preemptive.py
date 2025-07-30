"""Cooperative (asyncio) vs. Preemptive (threading) concurrency demonstration.

Run:
    python 07_cooperative_vs_preemptive.py

The script launches two equivalent scenarios:

1. **asyncio cooperative scheduling** three coroutines perform CPU-bound work.
   They only run concurrently when *they choose* to ``await`` and yield control
   back to the event-loop.  Omitting the ``await`` turns the so-called
   "concurrency" into plain, sequential execution.

2. **threading preemptive scheduling** three OS threads perform the exact
   same work.  The operating system's scheduler interrupts and context-switches
   between them *automatically* (preemption), so they appear to run in parallel
   even without explicit yielding in the user code.

Observe how the printed timestamps interleave in each section and how the total
runtime changes:
• asyncio WITHOUT explicit ``await`` → tasks run one after another.
• asyncio WITH ``await`` (cooperative) → tasks willingly interleave.
• threading (preemptive) → tasks are interleaved by the OS regardless of the
  user code.

Note: Because the tasks are CPU-bound, Python's Global Interpreter Lock (GIL)
prevents true parallel execution of Python bytecode.  Nevertheless, the OS
still pre-emptively time-slices the active thread, so their outputs interleave
and no single thread can starve the others.
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Callable, List, Sequence

# ---------------------------- helpers ---------------------------------- #

COUNT = 10_000_000  # workload per iteration (≈50 ms on modern CPU)
ITERATIONS = 5     # how many times each worker repeats the workload


def cpu_bound_work(n: int = COUNT) -> int:
    """Busy-loop to consume CPU cycles (dummy calculation)."""
    acc = 0
    for i in range(n):
        acc += i * i
    return acc


# ---------------------------- asyncio demo ----------------------------- #

async def async_worker(label: str, cooperative: bool) -> None:
    for i in range(ITERATIONS):
        cpu_bound_work()  # heavy work – holds the GIL
        if cooperative:
            # Explicitly yield to the event-loop so other tasks can run.
            await asyncio.sleep(0)
        print(f"[async {label}] iteration {i} (t={time.perf_counter():.3f}s)")


async def run_async_demo(cooperative: bool) -> None:
    title = "COOPERATIVE" if cooperative else "NO-YIELD (sequential)"
    print(f"\n--- asyncio demo: {title} ---")
    start = time.perf_counter()

    tasks = [async_worker(ch, cooperative) for ch in ("A", "B", "C")]
    await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    print(f"asyncio ({title}) finished in {elapsed:.2f}s")


# ---------------------------- threading demo --------------------------- #

def thread_worker(label: str) -> None:
    for i in range(ITERATIONS):
        cpu_bound_work()
        print(
            f"[thread {label}] iteration {i} (t={time.perf_counter():.3f}s on id={threading.get_ident()})"
        )


def run_thread_demo() -> None:
    print("\n--- threading demo: PREEMPTIVE ---")
    start = time.perf_counter()

    threads: List[threading.Thread] = [
        threading.Thread(target=thread_worker, args=(label,), daemon=False)
        for label in ("1", "2", "3")
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    elapsed = time.perf_counter() - start
    print(f"threading (preemptive) finished in {elapsed:.2f}s")


# ---------------------------- main ------------------------------------- #


def main() -> None:
    # 1. asyncio without explicit yielding – sequential execution
    asyncio.run(run_async_demo(cooperative=False))

    # 2. asyncio with explicit yielding – cooperative concurrency
    asyncio.run(run_async_demo(cooperative=True))

    # 3. preemptive threading demo
    run_thread_demo()


if __name__ == "__main__":
    main() 