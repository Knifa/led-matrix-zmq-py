import asyncio
import tempfile
import threading

import pytest
import zmq

from led_matrix_zmq import LmzMessageError
from led_matrix_zmq._zmq import SafeZmq, SafeZmqAsync


class ZmqFixture(threading.Thread):
    def __init__(self, endpoint: str) -> None:
        super().__init__(daemon=True)
        self._endpoint = endpoint

    def run(self) -> None:
        ctx = zmq.Context()
        ctx.sndtimeo = 5000
        ctx.rcvtimeo = 5000
        ctx.linger = 0
        sock = ctx.socket(zmq.REP)

        sock.bind(self._endpoint)
        sock.recv()
        sock.send(b"")


def test_safe_zmq() -> None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        endpoint = f"ipc://{tmpdirname}/test_zmq"
        test_zmq = ZmqFixture(endpoint)

        zmq = SafeZmq(endpoint, timeout_ms=1000)
        zmq.connect()

        with pytest.raises(LmzMessageError):
            zmq.send_recv(b"")

        test_zmq.start()

        assert zmq.send_recv(b"") == b""

        test_zmq.join()

        with pytest.raises(LmzMessageError):
            zmq.send_recv(b"")


@pytest.mark.asyncio
async def test_safe_zmq_async() -> None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        endpoint = f"ipc://{tmpdirname}/test_zmq"
        test_zmq = ZmqFixture(endpoint)

        zmq = SafeZmqAsync(endpoint, timeout_ms=1000)
        zmq.connect()

        with pytest.raises(LmzMessageError):
            await zmq.send_recv(b"")

        test_zmq.start()

        assert await zmq.send_recv(b"") == b""

        test_zmq.join()

        with pytest.raises(LmzMessageError):
            await zmq.send_recv(b"")


class ZmqEchoFixture(threading.Thread):
    def __init__(self, endpoint: str, count: int) -> None:
        super().__init__(daemon=True)
        self._endpoint = endpoint
        self._count = count

    def run(self) -> None:
        ctx = zmq.Context()
        ctx.sndtimeo = 5000
        ctx.rcvtimeo = 5000
        ctx.linger = 0
        sock = ctx.socket(zmq.REP)

        sock.bind(self._endpoint)
        for _ in range(self._count):
            sock.send(sock.recv())


@pytest.mark.asyncio
async def test_safe_zmq_async_concurrent() -> None:
    count = 20

    with tempfile.TemporaryDirectory() as tmpdirname:
        endpoint = f"ipc://{tmpdirname}/test_zmq"
        test_zmq = ZmqEchoFixture(endpoint, count)
        test_zmq.start()

        zmq = SafeZmqAsync(endpoint, timeout_ms=1000)
        zmq.connect()

        replies = await asyncio.gather(
            *(zmq.send_recv(str(i).encode()) for i in range(count))
        )

        assert replies == [str(i).encode() for i in range(count)]

        test_zmq.join()


class ZmqStallFixture(threading.Thread):
    def __init__(self, endpoint: str) -> None:
        super().__init__(daemon=True)
        self._endpoint = endpoint
        self.release = threading.Event()

    def run(self) -> None:
        ctx = zmq.Context()
        ctx.sndtimeo = 5000
        ctx.rcvtimeo = 5000
        ctx.linger = 0
        sock = ctx.socket(zmq.REP)

        sock.bind(self._endpoint)
        sock.recv()
        self.release.wait(5)
        sock.send(b"")
        sock.send(sock.recv())


@pytest.mark.asyncio
async def test_safe_zmq_async_cancelled() -> None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        endpoint = f"ipc://{tmpdirname}/test_zmq"
        test_zmq = ZmqStallFixture(endpoint)
        test_zmq.start()

        zmq = SafeZmqAsync(endpoint, timeout_ms=1000)
        zmq.connect()

        task = asyncio.create_task(zmq.send_recv(b"first"))
        await asyncio.sleep(0.1)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        test_zmq.release.set()

        assert await zmq.send_recv(b"second") == b"second"

        test_zmq.join()
