import abc
import dataclasses
import enum
import struct
from typing import Any, Generic, Iterator, Self, Type, TypeVar


class MessageId(enum.IntEnum):
    NULL_REPLY = 0

    GET_BRIGHTNESS_REQUEST = enum.auto()
    GET_BRIGHTNESS_REPLY = enum.auto()
    SET_BRIGHTNESS_REQUEST = enum.auto()

    GET_TEMPERATURE_REQUEST = enum.auto()
    GET_TEMPERATURE_REPLY = enum.auto()
    SET_TEMPERATURE_REQUEST = enum.auto()

    GET_CONFIGURATION_REQUEST = enum.auto()
    GET_CONFIGURATION_REPLY = enum.auto()


@dataclasses.dataclass
class Args(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def pack_format() -> str:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Any]:
        for field in dataclasses.fields(self):
            yield getattr(self, field.name)


@dataclasses.dataclass
class BrightnessArgs(Args):
    brightness: int
    transition: int

    @staticmethod
    def pack_format() -> str:
        return "BH"


@dataclasses.dataclass
class ConfigurationArgs(Args):
    width: int
    height: int

    @staticmethod
    def pack_format() -> str:
        return "HH"


@dataclasses.dataclass
class NullArgs(Args):
    @staticmethod
    def pack_format() -> str:
        return "x"


@dataclasses.dataclass
class TemperatureArgs(Args):
    temperature: int
    transition: int

    @staticmethod
    def pack_format() -> str:
        return "HH"


ArgsT = TypeVar("ArgsT", bound=Args)


class Message(Generic[ArgsT], abc.ABC):
    id_: MessageId

    args: ArgsT
    args_t: Type[ArgsT]

    def __init__(self, args: ArgsT) -> None:
        self.args = args

    def to_bytes(self) -> bytes:
        return struct.pack(f"<B{self.args_t.pack_format()}", self.id_, *self.args)

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        id_ = data[0]
        if id_ != cls.id_:
            raise ValueError(f"Invalid message ID: {id_}")

        try:
            _, *args_tuple = struct.unpack(f"<B{cls.args_t.pack_format()}", data)
        except struct.error as e:
            raise ValueError(f"Invalid message data: {e}")

        args = cls.args_t(*args_tuple)
        return cls(args)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.id_ == other.id_ and self.args == other.args


class NullReply(Message[NullArgs]):
    id_ = MessageId.NULL_REPLY
    args_t = NullArgs


class GetBrightnessRequest(Message[NullArgs]):
    id_ = MessageId.GET_BRIGHTNESS_REQUEST
    args_t = NullArgs


class GetBrightnessReply(Message[BrightnessArgs]):
    id_ = MessageId.GET_BRIGHTNESS_REPLY
    args_t = BrightnessArgs


class SetBrightnessRequest(Message[BrightnessArgs]):
    id_ = MessageId.SET_BRIGHTNESS_REQUEST
    args_t = BrightnessArgs


class GetTemperatureRequest(Message[NullArgs]):
    id_ = MessageId.GET_TEMPERATURE_REQUEST
    args_t = NullArgs


class GetTemperatureReply(Message[TemperatureArgs]):
    id_ = MessageId.GET_TEMPERATURE_REPLY
    args_t = TemperatureArgs


class SetTemperatureRequest(Message[TemperatureArgs]):
    id_ = MessageId.SET_TEMPERATURE_REQUEST
    args_t = TemperatureArgs


class GetConfigurationRequest(Message[NullArgs]):
    id_ = MessageId.GET_CONFIGURATION_REQUEST
    args_t = NullArgs


class GetConfigurationReply(Message[ConfigurationArgs]):
    id_ = MessageId.GET_CONFIGURATION_REPLY
    args_t = ConfigurationArgs


RequestMessageT = TypeVar(
    "RequestMessageT",
    GetBrightnessRequest,
    GetConfigurationRequest,
    GetTemperatureRequest,
    SetBrightnessRequest,
    SetTemperatureRequest,
)

ReplyMessageT = TypeVar(
    "ReplyMessageT",
    GetBrightnessReply,
    GetConfigurationReply,
    GetTemperatureReply,
    NullReply,
)
