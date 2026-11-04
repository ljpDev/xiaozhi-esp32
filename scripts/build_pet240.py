#!/usr/bin/env python3
"""Pack project-owned 240px expressions, then build the pet240 board variant."""

import argparse
import json
import struct
import subprocess
import sys
from pathlib import Path

import build_default_assets as assets


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "custom_assets" / "pet240"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-only", action="store_true")
    args = parser.parse_args()
    images = PACK / "images"
    files = sorted(images.glob("*.png"))
    if not files or not (images / "neutral.png").is_file():
        raise ValueError("images must contain the expressions, including neutral.png")
    for image in files:
        data = image.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", data[16:24]) != (240, 240):
            raise ValueError(f"Expected a 240x240 PNG: {image}")
    fonts = ROOT / "managed_components" / "78__xiaozhi-fonts"
    font = fonts / "cbin" / "font_noto_sans_common_20_4.bin"
    if not font.is_file():
        raise FileNotFoundError("Install project dependencies first (idf.py reconfigure)")
    bundle = json.loads((fonts / "manifest.json").read_text())["bundle_id"]
    output = PACK / "assets.bin"
    # UI and Chinese font are packed here; CMake configure_assets_models inserts
    # speech models from the active SDK configuration before flashing.
    if not assets.build_assets_integrated(
        None, None, str(font), str(images), None, str(output),
        font_bundle_id=bundle, max_size=8 * 1024 * 1024,
    ):
        raise RuntimeError("Custom UI resource packing failed")
    entries = assets.read_assets_entries(output)
    for image in files:
        if entries[image.name][0] != image.read_bytes():
            raise ValueError(f"Packed image differs from source: {image}")
    print(f"Verified {len(files)} images in {output}", flush=True)
    if not args.pack_only:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build.py"),
             "alientek/atk-dnesp32s3", "--name", "atk-dnesp32s3-pet240",
             "--language", "zh-CN", "--zip"],
            cwd=ROOT, check=True,
        )


if __name__ == "__main__":
    main()
