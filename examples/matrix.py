from led_matrix_zmq import LmzMatrix


def main() -> None:
    matrix = LmzMatrix(
        control_endpoint="ipc:///run/lmz/control.sock",
        frame_endpoint="ipc:///run/lmz/frame.sock",
    )
    matrix.connect()

    print(f"Resolution: {matrix.config.width}x{matrix.config.height}")
    print(f"Brightness: {matrix.brightness}")
    print(f"Temperature: {matrix.temperature}K")

    matrix.brightness = 128
    matrix.temperature = 5000

    matrix.send_frame(b"\xff" * (matrix.config.width * matrix.config.height * 4))


if __name__ == "__main__":
    main()
