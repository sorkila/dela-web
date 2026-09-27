#!/usr/bin/env python3
"""Turns full-screen iPhone captures (1320×2868) into the home page's board crops.

    python3 tools/screens.py draw=/path/a.png halves=/path/b.png twins=/path/c.png hint=/path/d.png

Each capture is cropped to the board (a 4:5 band that leaves out the status bar,
the header and the footer copy), resized to 660×825 and saved as
/shots/<name>.webp. The names are the ones index.html references, so swapping
in new captures is one run of this script.

Not deployed: tools/ is excluded in .github/workflows/deploy.yml.
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "shots"
SIZE = (660, 825)
# The board sits at ~49.5% of the screen height in the app's layout.
CENTRE_Y = 0.495


def crop(src: Path) -> Image.Image:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    ch = round(w * SIZE[1] / SIZE[0])
    top = max(0, min(h - ch, round(h * CENTRE_Y - ch / 2)))
    return im.crop((0, top, w, top + ch)).resize(SIZE, Image.LANCZOS)


def main(args):
    if not args:
        print(__doc__)
        return 1
    OUT.mkdir(exist_ok=True)
    for arg in args:
        name, _, src = arg.partition("=")
        dst = OUT / f"{name}.webp"
        crop(Path(src)).save(dst, "WEBP", quality=80, method=6)
        print(f"{dst.relative_to(ROOT)}  {dst.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
