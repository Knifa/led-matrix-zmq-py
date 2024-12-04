# led-matrix-zmq-py

![PyPI - Version](https://img.shields.io/pypi/v/led_matrix_zmq)

A Python library for interacting with [led-matrix-zmq-server](https://github.com/knifa/led-matrix-zmq-server).

## Installation

The package is called `led-matrix-zmq` and is available on [PyPI](https://pypi.org/project/led-matrix-zmq/) as is tradition.

## Usage

Check out the [examples](./examples) directory for some example code!

You'll probably want to use the `LmzMatrix` class which is a higher-level construct around the `LmzControl` and `LmzFrame` classes.

```python
from led_matrix_zmq import LmzMatrix

matrix = LmzMatrix(
    control_endpoint="ipc:///run/lmz-control.sock",
    frame_endpoint="ipc:///run/lmz-frame.sock",
)

print(f"Resolution: {matrix.config.width}x{matrix.config.height}")
print(f"Brightness: {matrix.brightness}")
print(f"Temperature: {matrix.temperature}")

matrix.brightness = 128
matrix.temperature = 2500

matrix.send_frame(
    b'\xFF' * (matrix.config.width * matrix.config.height * 4)
)
```
