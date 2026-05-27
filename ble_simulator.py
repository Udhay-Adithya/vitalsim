#!/usr/bin/env python3
"""Compatibility wrapper for running the VitalsSim BLE peripheral from source.

Prefer the packaged command after installing with uv:
    uv run vitalsim

This wrapper remains for users who expect:
    sudo uv run python ble_simulator.py
"""

from __future__ import annotations

from vitalsim.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
