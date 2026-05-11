from typing import Tuple
import os


def _tuple_from_env(name: str, default: Tuple[int, ...]) -> Tuple[int, ...]:
    val = os.getenv(name)
    if not val:
        return default
    return tuple(int(x) for x in val.split(","))
