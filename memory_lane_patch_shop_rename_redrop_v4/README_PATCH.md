# Memory Lane — Split Pages (Shop rename)

This patch splits the site into pages:
- /services/
- /featured/
- /shop/   (renamed from Gallery)
- /enquire/
- /about/

Placeholders:
- assets/bg1.jpg + assets/bg2.jpg used as hero/background
- assets/placeholder.jpg used for item images so nothing 404s

## Collage chopping helper (optional)
If you have a big "photo grid" image and want it split into individual tiles:

```bash
python tools/split_collage.py path/to/collage.jpg output_tiles/
```

If your grid is uniform:
```bash
python tools/split_collage.py collage.jpg output_tiles/ --rows 10 --cols 12
```

Auto mode works best if the grid has dark borders between tiles.
