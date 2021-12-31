# STDLIB
import sys
from typing import Any, Callable


def get_pretty_printer() -> Callable[[Any], str]:
    is_before_python38 = (sys.version_info.major, sys.version_info.minor) < (3, 8)
    if is_before_python38:
        import pprint3x as pprint  # type: ignore
    else:
        import pprint  # type: ignore
    pp = pprint.PrettyPrinter(sort_dicts=False).pprint
    return pp  # type: ignore
