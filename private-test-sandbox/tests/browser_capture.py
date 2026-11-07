#!/usr/bin/env python3
"""Browser capture is not part of the shell scenario.

The shared scenario does not call this file. Running it directly does not
start Chrome or any other browser. A later desktop session can open the
local page on its own. SKIPPED_NOT_RUN is not a test pass.
"""

from __future__ import annotations

import sys


def main() -> int:
    print("SKIPPED_NOT_RUN")
    print("browser capture does not start from the shell scenario")
    return 2


if __name__ == "__main__":
    sys.exit(main())
