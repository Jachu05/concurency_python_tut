# Multiprocessing example demonstrating manual Process spawning and a Pool for parallel CPU-bound work.
# Run: python multiprocessing_example.py

from multiprocessing import Process, Pool, cpu_count
import os


def compute_heavy(n: int = 10_000_000) -> int:
    """CPU-bound task: sum of squares up to n."""
    return sum(i * i for i in range(n))


def worker(identifier: int) -> None:
    result = compute_heavy()
    print(f"[Process {identifier} | pid={os.getpid()}] result: {result}")


def main() -> None:
    # Manual process spawn
    processes = [Process(target=worker, args=(i,)) for i in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    # Using a Pool for convenience
    with Pool(cpu_count()) as pool:
        results = pool.map(compute_heavy, [5_000_000] * cpu_count())
    print("Pool results:", results)


if __name__ == "__main__":
    main() 