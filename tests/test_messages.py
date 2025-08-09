from led_matrix_zmq._messages import BrightnessArgs, SetBrightnessRequest


def test_message_serde_identity() -> None:
    message = SetBrightnessRequest(BrightnessArgs(50, 0))

    assert message == SetBrightnessRequest.from_bytes(message.to_bytes())
