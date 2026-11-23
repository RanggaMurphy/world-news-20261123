#!/usr/bin/env python3
"""make.fun news-image entrypoint (stdlib only).

Copies entry.png from this repository into MAKEFUN_OUTPUT_DIR.
The image lives in the repo; this program only moves it to the output
folder the grader provides. It never writes into the repository itself,
which the grader mounts read-only.
"""

import os
import shutil
import sys

IMAGE = "entry.png"


def find_source(here):
    """Locate entry.png: prefer MAKEFUN_BOT_DIR when it actually holds the
    image, otherwise fall back to this script's own folder."""
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        candidate = os.path.join(bot_dir, IMAGE)
        if os.path.isfile(candidate):
            return candidate
    return os.path.join(here, IMAGE)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = find_source(here)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or here
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, IMAGE)
    shutil.copyfile(src, dest)
    if not os.path.isfile(dest):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
