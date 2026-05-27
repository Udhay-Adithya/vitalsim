"""Small compatibility helpers for bless backend differences."""

from __future__ import annotations

import inspect


async def maybe_await(result: object) -> object:
    """Await bless calls on platforms where they return awaitables."""
    if inspect.isawaitable(result):
        return await result  # type: ignore[no-any-return]
    return result
