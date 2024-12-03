import logging
from typing import Any, Self

import zmq
import zmq.asyncio

from .exceptions import LmzMessageError

logger = logging.getLogger(__name__)


class LmzFrame:
    def __init__(self, endpoint: str) -> None:
        self._endpoint = endpoint

        self._zmq_context = zmq.Context()
        self._zmq_context.sndtimeo = 1000
        self._zmq_context.rcvtimeo = 1000
        self._zmq_context.linger = 0
        self._zmq_socket: zmq.SyncSocket | None = None

    def connect(self) -> None:
        self._reset_socket()

    def send(self, frame: bytes) -> None:
        assert self._zmq_socket

        try:
            self._zmq_socket.send(frame)
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

        try:
            self._zmq_socket.recv()
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

    def _reset_socket(self) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()

        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(self._endpoint)

    def __enter__(self) -> Self:
        assert self._zmq_socket is None
        self._reset_socket()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()
            self._zmq_socket = None


class LmzFrameAsync:
    def __init__(self, endpoint: str) -> None:
        self._endpoint = endpoint

        self._zmq_context = zmq.asyncio.Context()
        self._zmq_context.sndtimeo = 1000
        self._zmq_context.rcvtimeo = 1000
        self._zmq_context.linger = 0
        self._zmq_socket: zmq.asyncio.Socket | None = None

    async def connect(self) -> None:
        self._reset_socket()

    async def send(self, frame: bytes) -> None:
        assert self._zmq_socket

        try:
            await self._zmq_socket.send(frame)
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

        try:
            await self._zmq_socket.recv()
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

    def _reset_socket(self) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()

        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(self._endpoint)

    async def __aenter__(self) -> Self:
        assert self._zmq_socket is None
        self._reset_socket()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()
            self._zmq_socket = None
