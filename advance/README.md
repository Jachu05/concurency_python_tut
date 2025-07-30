# Advanced Concurrency Demos

This directory contains **self-contained, runnable** examples that go one step beyond the material shown in `basics/`.  Each script focuses on a single concept so that you can copy-paste the relative _path_ (`advance/<script>.py`) into the terminal and immediately _see_ the effect on the console.

```
python advance/01_asyncio_race_condition.py       # race-condition demo           
python advance/02_asyncio_ordering_example.py     # unpredictable ordering        
python advance/03_asyncio_futures_example.py      # asyncio.Future / Task usage   
python advance/04_futures_example.py              # concurrent.futures overview   
python advance/05_asyncio_executor_bridge.py      # bridge blocking ↔ async code  
python advance/06_threading_executor_only.py      # pure threading / executors    
python advance/07_cooperative_vs_preemptive.py    # co-op vs. pre-emptive sched.  
python advance/08_asyncio_queue_example.py      # producer–consumer queue   
```

All examples run on the standard library (Python ≥ 3.10, no 3rd-party deps).

---

## Table of Contents
1. [Race conditions – shared state gone wrong](#1-race-conditions)
2. [Nondeterministic ordering](#2-nondeterministic-ordering)
3. [`asyncio.Future` and `Task`](#3-asynciofuture-and-task)
4. [`concurrent.futures` thread & process pools](#4-concurrentfutures-thread--process-pools)
5. [Bridging sync and async worlds](#5-bridging-sync-and-async-worlds)
6. [Threading & executors only](#6-threading--executors-only)
7. [Cooperative vs. pre-emptive scheduling](#7-cooperative-vs-pre-emptive-scheduling)
8. [Producer / Consumer queues](#8-producer--consumer-queues)
9. [Picking the right tool](#9-picking-the-right-tool)

---

## 1. Race conditions
_File: `01_asyncio_race_condition.py`_

We launch **1000 coroutines** that each read → modify → write to a shared counter **without locking**.  Inserting a single `await` between read and write gives the event-loop a chance to reschedule another task – classic _lost update_ scenario.

The script then re-runs the experiment with an `asyncio.Lock`, proving that proper critical-section protection restores correctness.

> Take-away: Async code is not magically safe.  Shared mutable state needs the _same_ protection primitives you would use in threaded code.

---

## 2. Nondeterministic ordering
_File: `02_asyncio_ordering_example.py`_

Appending to a list seems harmless, yet if N coroutines `await` a random sleep before `list.append()` the completion order becomes unpredictable.  By contrast, writing to **fixed indices** while holding a lock yields a deterministic result.

This simple demo is great for emphasising that _completion order_ is rarely guaranteed in concurrent systems unless explicitly enforced.

---

## 3. `asyncio.Future` and `Task`
_File: `03_asyncio_futures_example.py`_

Shows how **`asyncio.create_task()`** returns a `Task` (sub-class of `Future`), how to create a _bare_ `Future`, attach callbacks via `add_done_callback()`, and consume results with `asyncio.as_completed()`.

Useful if only ever used `await`/`gather` and never touched the underlying primitive.

---

## 4. `concurrent.futures` thread & process pools
_File: `04_futures_example.py`_

Twin demos:
1. **`ThreadPoolExecutor`** – suitable for blocking I/O.  10 fake I/O jobs illustrate callback & completion order.
2. **`ProcessPoolExecutor`** – bypasses the GIL; runs CPU-bound `sum(i*i)` workloads in parallel processes.

Highlights the identical API surface (`submit()`, `Future`, `as_completed()`) regardless of the executor type.

---

## 5. Bridging sync and async worlds
_File: `05_asyncio_executor_bridge.py`_

Pure async code can delegate _blocking_ work to a thread pool using **`loop.run_in_executor()`**.  The coroutine spawns tasks that run the synchronous `blocking_io()` function on worker threads while the event-loop remains responsive.

Great illustration why purely converting every function to `async def` is unnecessary – sometimes offloading to a thread is fine.

---

## 6. Threading & executors only
_File: `06_threading_executor_only.py`_

Contrasts three approaches on the _threading_ side of the story:
* Manual `threading.Thread` creation
* `ThreadPoolExecutor` for I/O
* `ProcessPoolExecutor` for CPU work

Running this after the async examples helps compare mental models and APIs.

---

## 7. Cooperative vs. pre-emptive scheduling
_File: `07_cooperative_vs_preemptive.py`_

A brilliant live-coding moment:
* **asyncio – no yield** → CPU-bound coroutines hog the interpreter, running _sequentially_.
* **asyncio – cooperative** → insert `await asyncio.sleep(0)` and see them gently interleave.
* **threading – pre-emptive** → three OS threads interleave _without_ any explicit yield thanks to the OS scheduler.

Even though Python’s GIL prevents true CPU parallelism, the difference in _who_ decides when to switch contexts (your code vs. the OS) becomes obvious.

---

## 8. Producer / Consumer queues
_File: `08_asyncio_queue_example.py`_

Shows how **`asyncio.Queue`** enables safe communication between concurrent coroutines without explicit locks.  Multiple *producers* `put()` random integers into the queue while *consumers* `get()` them, simulating I/O and processing delays.  The queue’s built-in back-pressure (``maxsize``) automatically balances the flow.

---

## 9. Picking the right tool

| Workload type | Recommended primitive                      | Example here |
|---------------|---------------------------------------------|--------------|
| I/O-bound, many connections | `asyncio` coroutines / `ThreadPoolExecutor` | files 01-05, 06 (thread-pool) |
| CPU-bound but moderate | `ProcessPoolExecutor` (multi-process)          | files 04, 06 |
| High contention shared state | Locks, queues, atomics                       | files 01, 02 |

The goal is not to crown a single winner but to give you intuition so you can _mix & match_ techniques in real projects.

---

Enjoy hacking concurrency! 🎉 