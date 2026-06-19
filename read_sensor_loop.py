#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path


DEVICE_ROOT = Path("/sys/bus/w1/devices")


def get_device_file(device_file: Path | None) -> Path:
    if device_file is not None:
        return device_file

    devices = sorted(DEVICE_ROOT.glob("28-*/w1_slave"))
    if not devices:
        raise FileNotFoundError("No DS18B20 sensor found under /sys/bus/w1/devices.")

    return devices[0]


def read_temperature_c(device_file: Path) -> float:
    lines = device_file.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2 or not lines[0].strip().endswith("YES"):
        raise ValueError("Sensor data is invalid or CRC check failed.")

    marker = "t="
    temperature_index = lines[1].find(marker)
    if temperature_index == -1:
        raise ValueError("Temperature value not found in sensor output.")

    return float(lines[1][temperature_index + len(marker) :]) / 1000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a DS18B20 sensor value in a loop until stopped."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between reads (default: 5).",
    )
    parser.add_argument(
        "--device-file",
        type=Path,
        help="Optional path to a w1_slave file. Defaults to the first 28-* sensor.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.interval <= 0:
        print("Interval must be greater than 0 seconds.", file=sys.stderr, flush=True)
        return 1

    try:
        device_file = get_device_file(args.device_file)
    except FileNotFoundError as error:
        print(error, file=sys.stderr, flush=True)
        return 1

    try:
        while True:
            try:
                temperature_c = read_temperature_c(device_file)
                timestamp = datetime.now().isoformat(timespec="seconds")
                print(f"{timestamp} {temperature_c:.3f} °C", flush=True)
            except (FileNotFoundError, ValueError) as error:
                print(f"Read failed: {error}", file=sys.stderr, flush=True)

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
