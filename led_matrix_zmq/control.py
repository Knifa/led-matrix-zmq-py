import logging
from typing import Any, Self, Type

from ._consts import DEFAULT_TIMEOUT_MS
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
from ._zmq import SafeZmq, SafeZmqAsync

logger = logging.getLogger(__name__)


class LmzControl:
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

    def get_brightness(self) -> int:
        reply = self._send_recv(
            GetBrightnessRequest(NullArgs()),
            GetBrightnessReply,
        )

        return reply.args.brightness

    def set_brightness(self, brightness: int, transition: int = 0) -> None:
        self._send_recv(
            SetBrightnessRequest(BrightnessArgs(brightness, transition)),
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

    def set_temperature(self, temperature: int, transition: int = 0) -> None:
        self._send_recv(
            SetTemperatureRequest(TemperatureArgs(temperature, transition)),
            NullReply,
        )

    def _send_recv(
        self,
        rep_msg: RequestMessageT,
        rep_cls: Type[ReplyMessageT],
    ) -> ReplyMessageT:
        rep_data = self._zmq.send_recv(rep_msg.to_bytes())
        return rep_cls.from_bytes(rep_data)


class LmzControlAsync:
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

    async def get_brightness(self) -> int:
        reply = await self._send_recv(
            GetBrightnessRequest(NullArgs()),
            GetBrightnessReply,
        )

        return reply.args.brightness

    async def set_brightness(self, brightness: int, transition: int = 0) -> None:
        await self._send_recv(
            SetBrightnessRequest(BrightnessArgs(brightness, transition)),
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

    async def set_temperature(self, temperature: int, transition: int = 0) -> None:
        await self._send_recv(
            SetTemperatureRequest(TemperatureArgs(temperature, transition)),
            NullReply,
        )

    async def _send_recv(
        self,
        rep_msg: RequestMessageT,
        rep_cls: Type[ReplyMessageT],
    ) -> ReplyMessageT:
        rep_data = await self._zmq.send_recv(rep_msg.to_bytes())
        return rep_cls.from_bytes(rep_data)
