import asyncio
import logging
import uuid

from collections.abc import Callable
from typing import Any
from typing import Dict
from typing import List
from typing import TypeVar


class WorkQueue:
    """An unbounded queue of async tasks. Has a maximum concurrency level."""

    def __init__(self, max_concurrency: int):
        # TODO dunder these?
        self.max_concurrency = max_concurrency
        self.queue: asyncio.Queue = asyncio.Queue()  # TODO why not use a regular queue?
        self.workers: List[asyncio.Task] = []
        self.results: Dict[uuid.UUID, Any] = {}
        # TODO must we store the asyncio loop?

    def _generate_new_task_uuid(self) -> uuid.UUID:
        u = uuid.uuid4()
        while u in self.results:
            u = uuid.uuid4()
        return u

    T = TypeVar("T")

    async def do(self, f: Callable[[T], asyncio.Task], arg: T):
        """returns when the task is done"""
        u = self._generate_new_task_uuid()
        cv = asyncio.Condition()
        await self.queue.put((u, cv, f, arg))
        async with cv:
            await cv.wait()
        result = self.results[u]
        del self.results[u]
        if isinstance(
            result, Exception
        ):  # TODO is this the right way to do this? what about a wrapper class? (because their code might *generate* an exception
            # without them intending to raise it)
            raise result
        return result

    """
        task_result = self.results[u]  # TODO dunder?
        del self.results[u]
        # TODO maybe better error handling here
        # TODO check for cancelling
        match task_result.exception():
            case None: return task_result.result()
            case e: raise e"""

    def start(self):
        for _ in range(self.max_concurrency):
            self.workers.append(asyncio.create_task(self._work()))

    async def stop(self):
        # TODO is this really 'force stop'?
        for worker in self.workers:
            worker.cancel()

    async def _work(self):
        while True:
            uuid, cv, f, arg = await self.queue.get()
            try:
                task = f(arg)
                logging.debug(f"about to await with {arg}")
                await task
                logging.debug(f"got result for {arg}")
                self.results[uuid] = task.result()
            except Exception as e:
                self.results[uuid] = e
            finally:
                async with cv:
                    cv.notify_all()