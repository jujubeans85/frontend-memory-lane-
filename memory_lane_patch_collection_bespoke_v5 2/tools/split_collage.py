"""
Split a collage image into tiles.

Usage:
  python tools/split_collage.py collage.jpg output_tiles/ --rows 10 --cols 12
"""
import argparse, os
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("outdir")
    ap.add_argument("--rows", type=int, required=True)
    ap.add_argument("--cols", type=int, required=True)
    ap.add_argument("--trim", type=int, default=0, help="pixels to trim from each tile edge")
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGB")
    w, h = im.size
    tw = w // args.cols
    th = h // args.rows
    os.makedirs(args.outdir, exist_ok=True)

    n = 0
    for r in range(args.rows):
        for c in range(args.cols):
            left = c * tw
            top = r * th
            tile = im.crop((left, top, left + tw, top + th))
            if args.trim:
                t = args.trim
                tile = tile.crop((t, t, tile.size[0]-t, tile.size[1]-t))
            n += 1
            tile.save(os.path.join(args.outdir, f"tile_{n:04d}.jpg"), quality=88, optimize=True, progressive=True)

    print(f"Saved {n} tiles to {args.outdir}")

if __name__ == "__main__":
    main()
