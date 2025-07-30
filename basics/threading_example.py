# Threading example demonstrating basic thread creation and safe shared-state access via a Lock.
# Run: python threading_example.py

import threading
import time

# Shared resource
counter = 0
lock = threading.Lock()

def worker(identifier: int, iterations: int = 5) -> None:
    """Increment a global counter while simulating I/O work."""
    global counter
    for _ in range(iterations):
        # Simulate an I/O wait so the scheduler can switch threads
        time.sleep(0.1)
        with lock:
            counter += 1
            print(f"[Thread {identifier}] counter -> {counter}")

def main() -> None:
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("All threads finished, final counter:", counter)

if __name__ == "__main__":
    main() 