# Python Concurrency Fundamentals: Memory Management, GIL, and Concurrent Programming Patterns

> *“Concurrency is not about threads – it is about dealing with lots of things at once.”*
>
> **— Rob Pike**

Welcome! 👋  
This repository accompanies on **writing concurrent programs in Python**.  Before we dive into the hands-on code in the `basics/` and `advance/` folders, it is important to understand **how CPython manages memory** and **why the Global Interpreter Lock (GIL) exists**.  These two topics underpin every design choice you will see in the asynchronous (`asyncio`), multithreaded, and multiprocessing examples that follow.

---

## 1. About

During the session we will

1. Establish a mental model of CPython’s memory manager & garbage collector.
2. Demystify the GIL and its impact on true parallelism.
3. Compare three concurrency strategies available in the standard library:
   - `asyncio` (single-threaded, cooperative multitasking)
   - `threading` (shared-memory, pre-emptive multitasking)
   - `multiprocessing` (multiple processes, true parallelism)
4. Benchmark and discuss real-world trade-offs using the code in this repo.

Use this README as a **hand-out**.  The code listings referenced below double as ready-to-run demos.

---

## 2. CPython Memory Management 101

### 2.1 Reference Counting
* Every object in CPython stores a **reference count**: the number of names/containers pointing to it.
* When the count drops to zero, the memory *can* be reclaimed immediately (fast path).
* Implication: object life-cycle is deterministic **until** reference cycles appear.

### 2.2 Garbage Collector (GC)
CPython supplements reference counting with a **cyclic garbage collector** to break reference cycles (e.g., two lists referring to each other).  Key points:

* Three generation approach (`0`, `1`, `2`) – younger generations are scanned more often.
* Collection pauses all Python execution; in a CPU-bound loop this GC pause *can* be noticeable.
* You can tune or disable GC with the `gc` module (we will experiment with this live).

### 2.3 Memory Arenas & Pools (Advanced)
For small objects (< 512 bytes), CPython uses an internal allocator (`pymalloc`) that avoids expensive `malloc`/`free` syscalls by keeping **pools** inside **arenas**.  You rarely need to worry about it, but it explains why Python sometimes appears to “hold on” to memory after objects go out of scope.

---

## 3. The Global Interpreter Lock (GIL)

> One process ⇢ one interpreter ⇢ **one** global lock

The GIL is a *mutual exclusion* lock that allows **exactly one** thread at a time to execute Python bytecode.  Why?

1. **Simplicity** – eliminates the need for fine-grained locks around all internal data structures.
2. **C API Compatibility** – the venerable C extensions ecosystem relies on the single-threaded assumption.
3. **Performance** – despite its reputation, the GIL can improve single-threaded throughput because the interpreter can avoid atomic operations.

### 3.1 Consequences
* CPU-bound workloads **do not** scale with threads – you still get one CPU core.
* I/O-bound workloads often scale *beautifully* with threads because threads release the GIL when waiting on syscalls.
* True multi-core execution requires **multiple processes** (or alternative interpreters like PyPy-STM, Jython, GraalPy)… but processes come with IPC overhead.

#### Quick Experiment
Open `advance/07_cooperative_vs_preemptive.py` to *feel* the difference between cooperative (`asyncio`) and pre-emptive (`threading`) multitasking under the GIL.

---

## 4. Concurrency Models at a Glance

| Model | Parallel? | Memory Space | Context Switch | Best For |
|-------|-----------|--------------|----------------|----------|
| `asyncio` | ❌ (single thread) | Shared | *Await* (cheap) | High I/O, many connections |
| `threading` | ❌ (GIL) | Shared | OS thread (moderate) | Mixed I/O, legacy APIs |
| `multiprocessing` | ✅ | **Separate** | OS process (expensive) | CPU-bound, true parallelism |

### Rule of Thumb
* **I/O-bound?** Start with `asyncio`; move to threads if blocking libraries are unavoidable.
* **CPU-bound?** Reach for `multiprocessing` (or native extensions) to escape the GIL.

---

## 5. Repository Tour

* `basics/`
  * `asyncio_example.py` – minimal async/await demo
  * `threading_example.py` – incrementing a counter from multiple threads
  * `multiprocessing_example.py` – parallel computation across CPU cores
* `advance/`
  * `01_asyncio_race_condition.py` – yes, you can create race conditions with `asyncio`!
  * `05_asyncio_executor_bridge.py` – mixing async code with thread/process pools
  * `07_cooperative_vs_preemptive.py` – cooperative vs pre-emptive scheduling showdown

Each file is *self-documenting* and can be executed directly:

```bash
python basics/asyncio_example.py
```

---

## 6. Running the Demos

1. Clone the repository (if you haven’t already).
2. Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. (Optional) Install `rich` for nicer output:

   ```bash
   pip install rich
   ```

4. Execute any script with Python 3.10+.

---

## 7. Further Reading

* *“Fluent Python”* – Chapter 17 & 18 on concurrency
* *“Python Concurrency with asyncio”* by Matthew Fowler
* CPython source code (`Objects/obmalloc.c`, `Python/ceval_gil.h`)
* [GC Design DOC](https://github.com/python/cpython/blob/main/InternalDocs/garbage_collector.md)

---

Happy hacking!! 🎓

