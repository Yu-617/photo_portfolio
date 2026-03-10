# photo_portfolio

## Image optimization helper

When uploading photos, you can compress/resize them with the included script to keep the site lightweight.

Install dependency:

```bash
pip install Pillow
```

Example usage:

```bash
# overwrite originals (max width 2048px, quality 85)
python tools/optimize_images.py content/gallery/landscapes --max-width 2048 --quality 85

# convert to WebP and write into an output folder
python tools/optimize_images.py content/gallery/landscapes --convert-webp --output-dir=static/optimized
```

Use `--dry-run` to preview changes and `--backup` to keep .bak copies of originals.
