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
