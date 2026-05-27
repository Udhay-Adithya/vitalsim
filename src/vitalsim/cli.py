"""Command-line interface for VitalsSim."""

from __future__ import annotations

import argparse
import asyncio
import logging
import random

from vitalsim.constants import DEVICE_NAME_DEFAULT
from vitalsim.platform_notes import log_platform_notes
from vitalsim.simulator import VitalsSimulator

LOGGER = logging.getLogger("vitalsim")


def configure_logging(verbose: bool) -> None:
    """Configure process-wide console logging."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse VitalsSim CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Bless-based BLE peripheral simulator for streaming vitals.",
    )
    parser.add_argument(
        "--name",
        default=DEVICE_NAME_DEFAULT,
        help='Device name to advertise (default: "VitalsSim")',
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=1000,
        help="Base tick interval in milliseconds (default: 1000)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible simulation",
    )
    return parser.parse_args()


async def run(args: argparse.Namespace) -> None:
    """Configure and run the simulator."""
    if args.seed is not None:
        random.seed(args.seed)
        LOGGER.debug("Using random seed %s", args.seed)

    simulator = VitalsSimulator(name=args.name, base_interval_ms=args.interval)
    await simulator.setup()

    try:
        await simulator.start()
    finally:
        await simulator.stop()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    configure_logging(args.verbose)
    log_platform_notes()

    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        LOGGER.info("Interrupted by user.")
        return 0
    except (OSError, RuntimeError, PermissionError, ValueError) as exc:
        LOGGER.error("%s", exc)
        return 1

    return 0
