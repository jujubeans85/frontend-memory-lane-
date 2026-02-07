#!/usr/bin/env python3
"""
split_collage.py
----------------
Chops a collage/grid image into individual tiles.

Two modes:
1) Auto (default): tries to detect dark grid lines and split on them.
2) Manual: provide --rows and --cols for a uniform grid.

Usage:
  python tools/split_collage.py input.jpg out_dir
  python tools/split_collage.py input.jpg out_dir --rows 10 --cols 12
  python tools/split_collage.py input.jpg out_dir --auto-thresh 45 --min-tile 120

Tips:
- Works best when the collage has clear dark borders between tiles.
- If your collage has mixed tile sizes, auto mode is your best bet.
- If auto misses, use manual rows/cols.
"""
import argparse, os
from PIL import Image

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def save_tiles(img, xs, ys, out_dir, prefix="img"):
    n = 0
    for yi in range(len(ys)-1):
        for xi in range(len(xs)-1):
            x0,x1 = xs[xi], xs[xi+1]
            y0,y1 = ys[yi], ys[yi+1]
            if (x1-x0) < 20 or (y1-y0) < 20:
                continue
            tile = img.crop((x0,y0,x1,y1))
            n += 1
            tile.save(os.path.join(out_dir, f"{prefix}_{n:04d}.jpg"), "JPEG", quality=88, optimize=True)
    return n

def manual_splits(w, h, rows, cols, pad=0):
    xs = [0]
    for c in range(1, cols):
        xs.append(int(round(c*w/cols)))
    xs.append(w)
    ys = [0]
    for r in range(1, rows):
        ys.append(int(round(r*h/rows)))
    ys.append(h)
    # optional pad trim (crop inside each tile by pad pixels)
    if pad>0:
        xs = [max(0, x+pad) if i not in (0,len(xs)-1) else x for i,x in enumerate(xs)]
        ys = [max(0, y+pad) if i not in (0,len(ys)-1) else y for i,y in enumerate(ys)]
    return xs, ys

def auto_detect_splits(img, auto_thresh=45, min_tile=120):
    # Convert to grayscale small preview for speed, then map back.
    g = img.convert("L")
    w, h = g.size

    # Downscale for faster scanning
    scale = 1
    target = 1400
    if max(w,h) > target:
        scale = target / max(w,h)
        g2 = g.resize((int(w*scale), int(h*scale)))
    else:
        g2 = g

    w2, h2 = g2.size
    px = g2.load()

    # Compute mean brightness per column/row
    col = [0]*w2
    row = [0]*h2
    for y in range(h2):
        s = 0
        for x in range(w2):
            v = px[x,y]
            s += v
            col[x] += v
        row[y] = s / w2
    col = [c / h2 for c in col]

    # Find "dark" lines where mean brightness is below threshold
    vlines = [i for i,v in enumerate(col) if v < auto_thresh]
    hlines = [i for i,v in enumerate(row) if v < auto_thresh]

    def compress(lines, gap=3):
        if not lines:
            return []
        out = [lines[0]]
        for i in lines[1:]:
            if i - out[-1] <= gap:
                continue
            out.append(i)
        return out

    vlines = compress(vlines)
    hlines = compress(hlines)

    # Convert line positions to split boundaries.
    # We want tile boundaries BETWEEN lines, so we build segments around them.
    def to_splits(lines, maxv):
        if not lines:
            return [0, maxv]
        # group into bands (gridlines have thickness)
        bands = []
        band = [lines[0]]
        for p in lines[1:]:
            if p - band[-1] <= 4:
                band.append(p)
            else:
                bands.append(band)
                band = [p]
        bands.append(band)

        centers = [int(round(sum(b)/len(b))) for b in bands]
        splits = [0]
        for c in centers:
            splits.append(c)
        splits.append(maxv)
        splits = sorted(set(splits))
        return splits

    xs2 = to_splits(vlines, w2)
    ys2 = to_splits(hlines, h2)

    # If we got too many tiny tiles, fall back to no split
    def prune(splits, maxv):
        splits = sorted(set(splits))
        # remove near-duplicates
        pr = [splits[0]]
        for s in splits[1:]:
            if s - pr[-1] >= 6:
                pr.append(s)
        # ensure ends
        if pr[0] != 0: pr = [0] + pr
        if pr[-1] != maxv: pr = pr + [maxv]
        return pr

    xs2 = prune(xs2, w2)
    ys2 = prune(ys2, h2)

    # Convert back to original scale
    xs = [int(round(x/scale)) for x in xs2]
    ys = [int(round(y/scale)) for y in ys2]

    # Prune splits that create tiles smaller than min_tile
    def prune_min(splits):
        out = [splits[0]]
        for s in splits[1:]:
            if s - out[-1] < min_tile and s != splits[-1]:
                continue
            out.append(s)
        return out

    xs = prune_min(xs)
    ys = prune_min(ys)

    # Always clamp
    xs[0] = 0; xs[-1] = w
    ys[0] = 0; ys[-1] = h

    return xs, ys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("out_dir")
    ap.add_argument("--rows", type=int, default=0)
    ap.add_argument("--cols", type=int, default=0)
    ap.add_argument("--pad", type=int, default=0)
    ap.add_argument("--auto-thresh", type=int, default=45, help="lower = stricter dark-line detection")
    ap.add_argument("--min-tile", type=int, default=120)
    ap.add_argument("--prefix", default="img")
    args = ap.parse_args()

    ensure_dir(args.out_dir)
    img = Image.open(args.input).convert("RGB")
    w,h = img.size

    if args.rows and args.cols:
        xs, ys = manual_splits(w,h,args.rows,args.cols,args.pad)
    else:
        xs, ys = auto_detect_splits(img, auto_thresh=args.auto_thresh, min_tile=args.min_tile)

    n = save_tiles(img, xs, ys, args.out_dir, prefix=args.prefix)
    print(f"Saved {n} tiles to: {args.out_dir}")

if __name__ == "__main__":
    main()
