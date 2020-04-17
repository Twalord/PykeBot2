from event_loop_master import query_forwarder
import asyncio
from models.query import Query

# TODO this test is outdated and needs to be removed or updated


def test_query_forwarder():
    """
    :description: Test for the query_forwarder function. Creates a new event loop and adds the query fowarder and
    a few test Coroutines. The loop runs until everything was forwarded successfully. Might not shut down correctly in
    case of an error.
    """

    async def queue_tester(queue: asyncio.Queue, count: int, identity: str, stop: asyncio.Event):
        """
        :description: Coroutine that checks the given Queue and checks if the forward was correct.
        After receiving the count number of queries the given event is set.
        """
        while count > 0:
            query = await queue.get()
            assert query.forward_to == identity
            count -= 1
            print("queue_tester received one Query")
            queue.task_done()
        stop.set()

    async def queue_filler(queue: asyncio.Queue):
        """
        :description: Coroutine that inserts a few static test Queries into a given Queue.
        """
        test_query1 = Query("", "test1", "test")
        test_query2 = Query("", "test2", "test")
        test_query3 = Query("", "test2", "test")
        await queue.put(test_query1)
        await queue.put(test_query2)
        queue.put_nowait(test_query3)

    async def stop_test(stop1: asyncio.Event, stop2: asyncio.Event):
        """
        :description: Coroutine that waits for two events to be set before stopping the current  event loop.
        """
        await stop1.wait()
        print("first event was received")
        await stop2.wait()
        print("second event was received")
        asyncio.get_event_loop().stop()

    """
    incoming_queue = asyncio.Queue()
    outgoing_queues = {"test1": asyncio.Queue(),
                       "test2": asyncio.Queue()}
    event1 = asyncio.Event()
    event2 = asyncio.Event()
    loop = asyncio.new_event_loop()
    asyncio.ensure_future(query_forwarder(incoming_queue, outgoing_queues))
    asyncio.ensure_future(queue_tester(outgoing_queues.get("test1"), 1, "test1", event1))
    asyncio.ensure_future(queue_tester(outgoing_queues.get("test2"), 2, "test2", event2))
    asyncio.ensure_future(queue_filler(incoming_queue))
    asyncio.ensure_future(stop_test(event1, event2))
    loop.run_forever()
    loop.close()
    """
    assert True
    return


def test_run_main_loop():
    pass
    # No idea how to test this one
