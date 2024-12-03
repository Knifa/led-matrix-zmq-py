import math
import time

from led_matrix_zmq import LmzFrame


def main() -> None:
    width = 64
    height = 128
    delay = 1 / 60
    scale = 0.05

    img = bytearray(width * height * 4)
    t = 0.0

    with LmzFrame("ipc:///run/lmz/frame.sock") as lmzf:
        while True:
            for y in range(height):
                for x in range(width):
                    i = (y * width + x) * 4

                    v = (
                        math.sin(x * scale + t)
                        + math.cos(y * scale + t)
                        + math.sin(
                            math.hypot(x - width / 2, y - height / 2) * scale * 4 + t
                        )
                    )

                    r = (math.sin(v * math.pi) + 1) * 127
                    g = (math.sin(v * math.pi + 0.75) + 1) * 127
                    b = (math.sin(v * math.pi + 1.5) + 1) * 127

                    img[i + 0] = int(r)
                    img[i + 1] = int(g)
                    img[i + 2] = int(b)
                    img[i + 3] = 0

            lmzf.send(img)
            t += delay
            time.sleep(delay)


if __name__ == "__main__":
    main()
