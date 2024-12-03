import asyncio

from led_matrix_zmq import LmzMatrixAsync


async def main() -> None:
    matrix = LmzMatrixAsync(
        control_endpoint="ipc:///run/lmz/control.sock",
        frame_endpoint="ipc:///run/lmz/frame.sock",
    )
    await matrix.connect()

    print(f"Resolution: {matrix.config.width}x{matrix.config.height}")

    brightness = await matrix.get_brightness()
    print(f"Brightness: {brightness}")

    temperature = await matrix.get_temperature()
    print(f"Temperature: {temperature}K")

    await matrix.set_brightness(128)
    await matrix.set_temperature(5000)

    await matrix.send_frame(b"\xff" * (matrix.config.width * matrix.config.height * 4))


if __name__ == "__main__":
    asyncio.run(main())
