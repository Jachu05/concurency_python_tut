"""Producer / Consumer pattern with asyncio.Queue.

Run:
    python 08_asyncio_queue_example.py [num_items] [num_producers] [num_consumers]

The script spawns a configurable number of *producer* and *consumer* coroutines
that communicate exclusively through an ``asyncio.Queue``:

• Producers generate ``num_items`` work items (here: random integers) and
  ``queue.put()`` them after a short ``await`` to simulate I/O latency.
• Consumers continuously ``queue.get()`` items, perform (fake) processing, and
  call ``queue.task_done()`` when finished.

The queue guarantees **FIFO order** and **automatic back-pressure** ``put()``
blocks when the queue reaches ``maxsize`` while consumers are slower than
producers.  No extra locks are required because the queue is already designed
for safe, concurrent use within a single event-loop.
"""

from __future__ import annotations

import asyncio
import random
import sys
from typing import Tuple

# ---------------------------- helpers ---------------------------------- #

def parse_cli_args() -> Tuple[int, int, int]:
    """Return (num_items, num_producers, num_consumers) from CLI or defaults."""
    try:
        num_items = int(sys.argv[1]) if len(sys.argv) > 1 else 20
        num_producers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        num_consumers = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    except ValueError:
        print("All arguments must be integers – falling back to defaults (20, 2, 3).")
        return 20, 2, 3
    return num_items, num_producers, num_consumers


async def producer(name: str, count: int, queue: asyncio.Queue[int]) -> None:
    """Produce *count* random integers and put them on *queue*."""
    for i in range(count):
        await asyncio.sleep(random.uniform(0.01, 0.1))  # simulate I/O delay
        item = random.randint(1, 100)
        await queue.put(item)
        print(f"[producer {name}] produced {item} (queue size={queue.qsize()})")

    print(f"[producer {name}] finished – no more items")


async def consumer(name: str, queue: asyncio.Queue[int]) -> None:
    """Continuously process items until a *None* sentinel is received."""
    while True:
        item = await queue.get()
        if item is None:  # sentinel means shutdown
            queue.task_done()
            print(f"[consumer {name}] received sentinel – exiting")
            break

        await asyncio.sleep(random.uniform(0.05, 0.2))  # simulate processing
        print(f"[consumer {name}] consumed {item} (queue size={queue.qsize()})")
        queue.task_done()


# ---------------------------- main logic -------------------------------- #

async def main() -> None:
    num_items, num_producers, num_consumers = parse_cli_args()

    print(
        f"Starting queue demo with {num_producers} producer(s), "
        f"{num_consumers} consumer(s), {num_items} item(s) each"
    )

    queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=10)

    # Spawn producers & consumers
    producers = [
        asyncio.create_task(producer(f"P{i}", num_items, queue))
        for i in range(num_producers)
    ]
    consumers = [
        asyncio.create_task(consumer(f"C{i}", queue)) for i in range(num_consumers)
    ]

    # Wait for all producers to finish
    await asyncio.gather(*producers)

    # Signal consumers to exit (one *None* per consumer)
    for _ in range(num_consumers):
        await queue.put(None)

    # Wait until the queue is fully processed and consumers exit
    await queue.join()
    await asyncio.gather(*consumers)

    print("All producers and consumers have terminated – demo complete ✨")


if __name__ == "__main__":
    random.seed(42)
    asyncio.run(main()) 