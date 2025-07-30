# Asynchronous Programming, Multithreading & Multiprocessing in Python

This folder contains runnable code examples and concise theory notes for an introductory lecture on modern concurrency techniques in Python.

## Table of Contents
1. Introduction
2. Multithreading
3. Multiprocessing
4. Asyncio
5. Quick Comparison
6. Running the Examples

---

### 1. Introduction
Concurrency lets a program make progress on multiple tasks seemingly at the same time, while **parallelism** means tasks are truly running simultaneously on different CPU cores. Choosing the right approach depends on whether your workload is **I/O-bound** (waiting for external resources) or **CPU-bound** (heavy computation).

---

### 2. Multithreading
* Threads share the same memory space inside a single process.
* Python’s **Global Interpreter Lock (GIL)** allows only one thread at a time to execute Python byte-code, which limits throughput for CPU-bound work but is fine for I/O-bound workloads.
* See `basics/threading_example.py` for a hands-on demonstration.

---

### 3. Multiprocessing
* Each process has its own Python interpreter and memory space, bypassing the GIL, so it scales well for CPU-bound work.
* Inter-Process Communication (IPC) is slower and more memory-hungry than in-process memory sharing.
* See `basics/multiprocessing_example.py`.

---

### 4. Asyncio
* Event-loop based, single-threaded but uses **cooperative multitasking** (`async`/`await`).
* Excellent for high-latency I/O such as networking without the overhead of threads or processes.
* See `basics/asyncio_example.py`.

---

### 5. Quick Comparison

| Technique        | Best for      | GIL impact | Memory model |
|------------------|--------------|-----------|--------------|
| Multithreading   | I/O-bound     | Blocked    | Shared       |
| Multiprocessing  | CPU-bound     | None       | Separate     |
| asyncio          | I/O-bound     | None       | Single thread|

---

### 6. Running the Examples

1. Ensure you have **Python ≥3.9** installed.
2. Install the single external dependency required by the async example:

```bash
pip install aiohttp
```

3. Run the scripts from this directory:

```bash
python basics/threading_example.py
python basics/multiprocessing_example.py
python basics/asyncio_example.py
```

Each script prints progress messages so you can observe the differences in execution behaviour. Feel free to modify the code and experiment – try increasing the number of threads, processes, or URLs to fetch to see how performance changes. 