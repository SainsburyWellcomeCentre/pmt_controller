import uasyncio as asyncio
from threadsafe import ThreadSafeQueue
import _thread
from time import sleep_ms

def core_2(getq, putq):  # Run on core 2
    buf = []
    while True:
        while getq.qsize():  # Ensure no exception when queue is empty
            buf.append(getq.get_sync())
        for x in buf:
            putq.put_sync(x, block=True)  # Wait if queue fills.
        buf.clear()
        sleep_ms(30)

async def sender(to_core2):
    x = 0
    while True:
        await to_core2.put(x := x + 1)

async def main():
    to_core2 = ThreadSafeQueue([0 for _ in range(10)])
    from_core2 = ThreadSafeQueue([0 for _ in range(10)])
    _thread.start_new_thread(core_2, (to_core2, from_core2))
    asyncio.create_task(sender(to_core2))
    n = 0
    async for x in from_core2:
        if not x % 1000:
            print(f"Received {x} queue items.")
        n += 1
        assert x == n

asyncio.run(main())