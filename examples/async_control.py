import argparse
import asyncio

from led_matrix_zmq import LmzControlAsync


async def main() -> None:
    args = parse_args()

    async with LmzControlAsync(args.endpoint) as lmzc:
        config = await lmzc.get_configuration()
        print(f"Resolution: {config.width}x{config.height}")

        brightness = await lmzc.get_brightness()
        print(f"Brightness: {brightness}")

        temperature = await lmzc.get_temperature()
        print(f"Temperature: {temperature}K")

        if args.brightness is not None:
            await lmzc.set_brightness(args.brightness)
            print(f"Set brightness to {args.brightness}")

        if args.temperature is not None:
            await lmzc.set_temperature(args.temperature)
            print(f"Set temperature to {args.temperature}K")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="ipc:///run/lmz/control.sock")
    parser.add_argument("--brightness", type=int)
    parser.add_argument("--temperature", type=int)
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main())
