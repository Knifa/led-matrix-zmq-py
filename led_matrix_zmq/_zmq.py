import zmq
import zmq.asyncio

from ._consts import DEFAULT_TIMEOUT_MS
from .exceptions import LmzMessageError


class SafeZmq:
    def __init__(self, endpoint: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
        self._endpoint = endpoint

        self._zmq_context = zmq.Context()
        self._zmq_context.sndtimeo = timeout_ms
        self._zmq_context.rcvtimeo = timeout_ms
        self._zmq_context.linger = 0
        self._zmq_socket: zmq.SyncSocket | None = None

    def connect(self) -> None:
        self._reset_socket()

    def close(self) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()

    def send_recv(self, data: bytes) -> bytes:
        assert self._zmq_socket

        try:
            self._zmq_socket.send(data)
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

        try:
            return self._zmq_socket.recv()
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

    def _reset_socket(self) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()

        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(self._endpoint)


class SafeZmqAsync:
    def __init__(self, endpoint: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
        self._endpoint = endpoint

        self._zmq_context = zmq.asyncio.Context()
        self._zmq_context.sndtimeo = timeout_ms
        self._zmq_context.rcvtimeo = timeout_ms
        self._zmq_context.linger = 0
        self._zmq_socket: zmq.asyncio.Socket | None = None

    def connect(self) -> None:
        self._reset_socket()

    def close(self) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()

    async def send_recv(self, data: bytes) -> bytes:
        assert self._zmq_socket

        try:
            await self._zmq_socket.send(data)
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

        try:
            return await self._zmq_socket.recv()
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

    def _reset_socket(self) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()

        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(self._endpoint)
