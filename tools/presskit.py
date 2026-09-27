#!/usr/bin/env python3
"""Builds press-kit.zip from the app repo's 2.0 store assets.

    python3 tools/presskit.py [--app ~/Repositories/Dela]

Run from the repo root. Needs pngquant (brew install pngquant) and zip.
Screenshots are palette-quantised to keep the kit under ~25 MB; the icon ships as is.
Not deployed: tools/ is excluded in .github/workflows/deploy.yml.
"""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# App Store order, from store_assets/v2/framed_iphone.
SHOTS = ["landing", "stroke", "miss", "chapters", "seeds", "apart", "thirds", "promise"]
# The posters have no raw capture; only the finished shot goes in.
POSTERS = {"chapters", "promise"}

# pngquant quality per group: the raw captures carry the detail an editor
# might crop into; the framed ones are finished marketing images.
QUALITY = {"iphone": "80-95", "ipad": "75-90", "framed-iphone": "72-90"}

FACT_SHEET = """\
Dela: The art of dividing
Fact sheet

Name          Dela
Developer     Erik Nielsen, Stockholm
Platforms     iPhone and iPad, iOS 17 or later
Price         Free to try. Chapters I and II are free; one in-app purchase
              unlocks everything else, once. Earlier buyers keep everything.
Dela 2.0      September 2026
First release 7 May 2026
Contact       hello@sorkila.com
Website       https://playdela.com
App Store     https://apps.apple.com/app/dela-the-art-of-dividing/id6766864158

About
Dela is a puzzle game about dividing. Draw one line across a shape, edge to
edge, bending where you like, and lift your finger to cut it in two. In
chapter I, Halves (12 boards), the parts must hold the same area. In chapter
II, Twins (13 boards), they must match, turned or mirrored: the gold half
lifts, turns and lands on its ivory twin, or tries anyway and shows you which
cells don't fit. In chapter III, Seeds (12 boards), gold beads sit in the
cells and each half must hold the same number. Then Apart (linked marks on
opposite sides), Two of everything (gold beads and pearls, both fair), Thirds
(two lines, three equal parts) and The exception (one cell doesn't count):
seven chapters, 85 boards. The first Dela, the 137-board lane-cutting game
where it started, is inside too as the legacy levels. Hints wait until you've had
a real go. No ads, no tracking, no login.

Contents
icon/dela-icon-1024.png         App icon, 1024 x 1024
screenshots/iphone/             iPhone 6.9", 1320 x 2868
screenshots/ipad/               iPad 13", 2064 x 2752
screenshots/store-iphone/       App Store screenshots with captions, 1320 x 2868
"""


def quantise(src: Path, dst: Path, quality: str):
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["pngquant", "--quality", quality, "--speed", "1", "--strip", "--force",
                        "--output", str(dst), str(src)])
    if r.returncode != 0:  # quality floor not met: keep the original
        shutil.copyfile(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", type=Path, default=Path.home() / "Repositories" / "Dela")
    args = ap.parse_args()
    v2 = args.app / "store_assets" / "v2"
    icon = args.app / "Resources" / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon.png"

    with tempfile.TemporaryDirectory() as tmp:
        kit = Path(tmp) / "dela-press-kit"
        (kit / "icon").mkdir(parents=True)
        shutil.copyfile(icon, kit / "icon" / "dela-icon-1024.png")
        for i, name in enumerate(SHOTS, 1):
            if name not in POSTERS:
                quantise(v2 / "raw_iphone" / f"{name}.png", kit / "screenshots" / "iphone" / f"{i:02d}-{name}.png", QUALITY["iphone"])
                quantise(v2 / "raw_ipad" / f"{name}.png", kit / "screenshots" / "ipad" / f"{i:02d}-{name}.png", QUALITY["ipad"])
            quantise(v2 / "final_iphone" / f"{i:02d}_{name}.png", kit / "screenshots" / "store-iphone" / f"{i:02d}-{name}.png", QUALITY["framed-iphone"])
        (kit / "fact-sheet.txt").write_text(FACT_SHEET)

        out = ROOT / "press-kit.zip"
        out.unlink(missing_ok=True)
        # -0 for the PNGs (already compressed), deflate for the text.
        subprocess.run(["zip", "-q", "-X", "-r", "-n", ".png", str(out), "dela-press-kit"], cwd=tmp, check=True)
    print(f"{out.name}: {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
