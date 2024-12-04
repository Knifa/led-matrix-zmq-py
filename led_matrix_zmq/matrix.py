from typing import Self

from ._consts import DEFAULT_TIMEOUT_MS
from ._messages import ConfigurationArgs
from .control import LmzControl, LmzControlAsync
from .frame import LmzFrame, LmzFrameAsync


class LmzMatrix:
    def __init__(
        self,
        control_endpoint: str = "ipc:///run/lmz-control.sock",
        frame_endpoint: str = "ipc:///run/lmz-frame.sock",
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
    ):
        self._control = LmzControl(control_endpoint, timeout_ms)
        self._frame = LmzFrame(frame_endpoint, timeout_ms)

        self._config: ConfigurationArgs | None = None
        self._expected_frame_size: int | None = None

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self) -> None:
        self.close()

    def connect(self) -> None:
        self._control.connect()
        self._frame.connect()

        self._config = self._control.get_configuration()
        self._expected_frame_size = self._config.width * self._config.height * 4

    def close(self) -> None:
        self._control.close()
        self._frame.close()

    @property
    def brightness(self) -> int:
        return self._control.get_brightness()

    @brightness.setter
    def brightness(self, value: int) -> None:
        if value < 0 or value > 255:
            raise ValueError("Brightness value must be between 0 and 255")

        self._control.set_brightness(value)

    @property
    def config(self) -> ConfigurationArgs:
        assert self._config is not None
        return self._config

    @property
    def temperature(self) -> int:
        return self._control.get_temperature()

    @temperature.setter
    def temperature(self, value: int) -> None:
        if value < 2000 or value > 6500:
            raise ValueError("Temperature value must be between 2000K and 6500K")

        self._control.set_temperature(value)

    def send_frame(self, frame: bytes) -> None:
        assert self._expected_frame_size is not None

        if len(frame) != self._expected_frame_size:
            raise ValueError(
                "Frame size doesn't match expected size (%d != %d)"
                % (len(frame), self._expected_frame_size)
            )

        self._frame.send(frame)


class LmzMatrixAsync:
    def __init__(
        self,
        control_endpoint: str = "ipc:///run/lmz-control.sock",
        frame_endpoint: str = "ipc:///run/lmz-frame.sock",
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
    ):
        self._control = LmzControlAsync(control_endpoint, timeout_ms)
        self._frame = LmzFrameAsync(frame_endpoint, timeout_ms)

        self._config: ConfigurationArgs | None = None
        self._expected_frame_size: int | None = None

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self) -> None:
        self.close()

    async def connect(self) -> None:
        self._control.connect()
        self._frame.connect()

        self._config = await self._control.get_configuration()
        self._expected_frame_size = self._config.width * self._config.height * 4

    def close(self) -> None:
        self._control.close()
        self._frame.close()

    async def get_brightness(self) -> int:
        return await self._control.get_brightness()

    async def set_brightness(self, value: int) -> None:
        if value < 0 or value > 255:
            raise ValueError("Brightness value must be between 0 and 255")

        await self._control.set_brightness(value)

    @property
    def config(self) -> ConfigurationArgs:
        assert self._config is not None
        return self._config

    async def get_temperature(self) -> int:
        return await self._control.get_temperature()

    async def set_temperature(self, value: int) -> None:
        if value < 2000 or value > 6500:
            raise ValueError("Temperature value must be between 2000K and 6500K")

        await self._control.set_temperature(value)

    async def send_frame(self, frame: bytes) -> None:
        assert self._expected_frame_size is not None

        if len(frame) != self._expected_frame_size:
            raise ValueError(
                "Frame size doesn't match expected size (%d != %d)"
                % (len(frame), self._expected_frame_size)
            )

        await self._frame.send(frame)
