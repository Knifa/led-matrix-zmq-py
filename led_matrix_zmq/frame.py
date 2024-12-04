import logging
from typing import Any, Self

from ._consts import DEFAULT_TIMEOUT_MS
from ._zmq import SafeZmq, SafeZmqAsync

logger = logging.getLogger(__name__)


class LmzFrame:
    def __init__(self, endpoint: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
        self._zmq = SafeZmq(endpoint, timeout_ms)

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def connect(self) -> None:
        self._zmq.connect()

    def close(self) -> None:
        self._zmq.close()

    def send(self, frame: bytes) -> None:
        self._zmq.send_recv(frame)


class LmzFrameAsync:
    def __init__(self, endpoint: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
        self._zmq = SafeZmqAsync(endpoint, timeout_ms)

    async def __aenter__(self) -> Self:
        self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        self.close()

    def connect(self) -> None:
        self._zmq.connect()

    def close(self) -> None:
        self._zmq.close()

    async def send(self, frame: bytes) -> None:
        await self._zmq.send_recv(frame)
