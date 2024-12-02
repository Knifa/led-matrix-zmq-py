import logging
from typing import Any, Self, Type

import zmq
import zmq.asyncio

from ._messages import (
    BrightnessArgs,
    ConfigurationArgs,
    GetBrightnessReply,
    GetBrightnessRequest,
    GetConfigurationReply,
    GetConfigurationRequest,
    GetTemperatureReply,
    GetTemperatureRequest,
    NullArgs,
    NullReply,
    ReplyMessageT,
    RequestMessageT,
    SetBrightnessRequest,
    SetTemperatureRequest,
    TemperatureArgs,
)

logger = logging.getLogger(__name__)


class LmzMessageError(Exception):
    pass


class LmzControl:
    def __init__(self, addr: str) -> None:
        self._addr = addr

        self._zmq_context = zmq.Context()
        self._zmq_context.sndtimeo = 1000
        self._zmq_context.rcvtimeo = 1000
        self._zmq_context.linger = 0
        self._zmq_socket: zmq.SyncSocket | None = None

    def __enter__(self) -> Self:
        assert self._zmq_socket is None
        self._reset_socket()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()
            self._zmq_socket = None

    def get_brightness(self) -> int:
        reply = self._send_recv(
            GetBrightnessRequest(NullArgs()),
            GetBrightnessReply,
        )

        return reply.args.brightness

    def set_brightness(self, brightness: int) -> None:
        self._send_recv(
            SetBrightnessRequest(BrightnessArgs(brightness)),
            NullReply,
        )

    def get_configuration(self) -> ConfigurationArgs:
        reply = self._send_recv(
            GetConfigurationRequest(NullArgs()),
            GetConfigurationReply,
        )

        return reply.args

    def get_temperature(self) -> int:
        reply = self._send_recv(
            GetTemperatureRequest(NullArgs()),
            GetTemperatureReply,
        )

        return reply.args.temperature

    def set_temperature(self, temperature: int) -> None:
        self._send_recv(
            SetTemperatureRequest(TemperatureArgs(temperature)),
            NullReply,
        )

    def _reset_socket(self) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()

        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(self._addr)

    def _send_recv(
        self,
        req_msg: RequestMessageT,
        rep_type: Type[ReplyMessageT],
    ) -> ReplyMessageT:
        assert self._zmq_socket
        req_bytes = req_msg.to_bytes()

        try:
            self._zmq_socket.send(req_bytes)
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

        try:
            rep_bytes = self._zmq_socket.recv()
            return rep_type.from_bytes(rep_bytes)
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e


class LmzControlAsync:
    def __init__(self, addr: str) -> None:
        self._addr = addr

        self._zmq_context = zmq.asyncio.Context()
        self._zmq_context.sndtimeo = 1000
        self._zmq_context.rcvtimeo = 1000
        self._zmq_context.linger = 0
        self._zmq_socket: zmq.asyncio.Socket | None = None

    async def __aenter__(self) -> Self:
        assert self._zmq_socket is None
        self._reset_socket()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()
            self._zmq_socket = None

    async def get_brightness(self) -> int:
        reply = await self._send_recv(
            GetBrightnessRequest(NullArgs()),
            GetBrightnessReply,
        )

        return reply.args.brightness

    async def set_brightness(self, brightness: int) -> None:
        await self._send_recv(
            SetBrightnessRequest(BrightnessArgs(brightness)),
            NullReply,
        )

    async def get_configuration(self) -> ConfigurationArgs:
        reply = await self._send_recv(
            GetConfigurationRequest(NullArgs()),
            GetConfigurationReply,
        )

        return reply.args

    async def get_temperature(self) -> int:
        reply = await self._send_recv(
            GetTemperatureRequest(NullArgs()),
            GetTemperatureReply,
        )

        return reply.args.temperature

    async def set_temperature(self, temperature: int) -> None:
        await self._send_recv(
            SetTemperatureRequest(TemperatureArgs(temperature)),
            NullReply,
        )

    def _reset_socket(self) -> None:
        if self._zmq_socket:
            self._zmq_socket.close()

        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect(self._addr)

    async def _send_recv(
        self,
        req_msg: RequestMessageT,
        rep_type: Type[ReplyMessageT],
    ) -> ReplyMessageT:
        assert self._zmq_socket
        req_bytes = req_msg.to_bytes()

        try:
            await self._zmq_socket.send(req_bytes)
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e

        try:
            rep_bytes = await self._zmq_socket.recv()
            return rep_type.from_bytes(rep_bytes)
        except zmq.error.Again as e:
            self._reset_socket()
            raise LmzMessageError("Timeout") from e
        except ValueError as e:
            raise LmzMessageError("Invalid reply") from e
