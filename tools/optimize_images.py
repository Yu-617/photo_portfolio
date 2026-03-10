#!/usr/bin/env python3
"""
画像最適化スクリプト

使い方: フォルダ内の JPEG/PNG を指定した幅・品質で縮小・圧縮します。
オプションで WebP に変換できます。

依存: Pillow
  pip install Pillow

例:
  python tools/optimize_images.py content/gallery/landscapes --max-width 2048 --quality 85 --convert-webp

安全: デフォルトでは上書きしますが、`--backup` を付けると元ファイルを .bak として残します。
"""

from PIL import Image, UnidentifiedImageError
import argparse
import os
from pathlib import Path
import sys


def process_image(path: Path, max_width: int, max_height: int, quality: int, convert_webp: bool, backup: bool, dry_run: bool, output_dir: Path | None):
    try:
        with Image.open(path) as img:
            original_format = img.format
            w, h = img.size
            ratio = min(1, max_width / w if max_width else 1, max_height / h if max_height else 1)
            new_size = (int(w * ratio), int(h * ratio))

            if dry_run:
                print(f"[DRY] {path} -> size {w}x{h} -> {new_size}, format={original_format}")
                return True

            if ratio < 1:
                img = img.resize(new_size, Image.LANCZOS)

            # 出力先
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                out_path = output_dir / path.name
            else:
                out_path = path

            if backup and out_path.exists():
                bak = out_path.with_suffix(out_path.suffix + '.bak')
                if not bak.exists():
                    out_path.replace(bak)
                    # rewrite img to original path below

            # WebP へ変換
            if convert_webp:
                webp_path = out_path.with_suffix('.webp')
                img.save(webp_path, 'WEBP', quality=quality, method=6)
                # remove original if overwriting and no output_dir
                if not output_dir and path.exists() and webp_path.exists():
                    try:
                        path.unlink()
                    except Exception:
                        pass
                print(f"WROTE: {webp_path}")
                return True

            # PNG/JPEG の扱い
            fmt = original_format.upper() if original_format else None
            if fmt in ('JPEG', 'JPG'):
                img.save(out_path, 'JPEG', quality=quality, optimize=True)
            elif fmt == 'PNG':
                # PNG は透過を保持しつつ圧縮
                img.save(out_path, 'PNG', optimize=True)
            else:
                # そのまま保存（フォーマット未対応の場合）
                img.save(out_path)

            print(f"WROTE: {out_path}")
            return True

    except UnidentifiedImageError:
        print(f"SKIP (not image): {path}")
        return False
    except Exception as e:
        print(f"ERROR processing {path}: {e}")
        return False


def iter_images(folder: Path, recursive: bool):
    exts = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    if recursive:
        for p in folder.rglob('*'):
            if p.suffix in exts and p.is_file():
                yield p
    else:
        for p in folder.iterdir():
            if p.suffix in exts and p.is_file():
                yield p


def main():
    p = argparse.ArgumentParser(description='Optimize images (resize, recompress, optional WebP)')
    p.add_argument('folder', type=Path, help='Folder containing images')
    p.add_argument('--max-width', type=int, default=2048, help='Maximum width (px)')
    p.add_argument('--max-height', type=int, default=2048, help='Maximum height (px)')
    p.add_argument('--quality', type=int, default=85, help='JPEG/WebP quality (1-100)')
    p.add_argument('--convert-webp', action='store_true', help='Convert images to WebP')
    p.add_argument('--backup', action='store_true', help='Keep backup of original files with .bak')
    p.add_argument('--dry-run', action='store_true', help='Show what would be done without writing files')
    p.add_argument('--recursive', action='store_true', help='Process subdirectories')
    p.add_argument('--output-dir', type=Path, default=None, help='Write results to this directory (keeps originals)')

    args = p.parse_args()

    folder = args.folder
    if not folder.exists() or not folder.is_dir():
        print('Folder does not exist or is not a directory:', folder)
        sys.exit(1)

    total = 0
    success = 0
    for img_path in iter_images(folder, args.recursive):
        total += 1
        if process_image(img_path, args.max_width, args.max_height, args.quality, args.convert_webp, args.backup, args.dry_run, args.output_dir):
            success += 1

    print(f"Processed {success}/{total} images")


if __name__ == '__main__':
    main()
