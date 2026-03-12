#!/usr/bin/env python3
"""
画像最適化スクリプト（EXIF メタデータを保持）

機能:
- 画像のリサイズ（幅・高さの上限指定）
- JPEG の品質指定（progressive / optimize）
- 任意で WebP への変換
- EXIF をできる限り保持（Pillow の exif bytes を保存、可能なら piexif で Orientation を正規化）

依存:
  pip install Pillow
  （より正確に EXIF を扱うなら）pip install piexif

使い方（ローカルターミナルで手動実行を想定）:
  python tools/optimize_images.py content/gallery/landscapes --max-width 2048 --quality 85 --recursive

オプション: --convert-webp, --backup, --dry-run, --output-dir
"""

from PIL import Image, UnidentifiedImageError, ImageOps, PngImagePlugin
import argparse
import os
from pathlib import Path
import sys

try:
    import piexif
except Exception:
    piexif = None


def _get_exif_bytes(img: Image.Image):
    exif = img.info.get('exif')
    if exif:
        return exif
    return None


def _normalize_orientation(img: Image.Image, exif_bytes: bytes | None):
    img = ImageOps.exif_transpose(img)
    if piexif and exif_bytes:
        try:
            exif_dict = piexif.load(exif_bytes)
            if '0th' in exif_dict and piexif.ImageIFD.Orientation in exif_dict['0th']:
                exif_dict['0th'][piexif.ImageIFD.Orientation] = 1
                exif_bytes = piexif.dump(exif_dict)
        except Exception:
            pass
    return img, exif_bytes


def process_image(path: Path, max_width: int, max_height: int, quality: int, convert_webp: bool, backup: bool, dry_run: bool, output_dir: Path | None):
    try:
        with Image.open(path) as img:
            original_format = img.format
            # Get EXIF bytes and normalize orientation first so size/ratio are computed
            exif_bytes = _get_exif_bytes(img)
            img, exif_bytes = _normalize_orientation(img, exif_bytes)

            w, h = img.size
            ratio = min(1, max_width / w if max_width else 1, max_height / h if max_height else 1)
            new_size = (int(w * ratio), int(h * ratio))

            if dry_run:
                print(f"[DRY] {path} -> {w}x{h} -> {new_size}, format={original_format}, exif={'yes' if exif_bytes else 'no'}")
                return True

            if ratio < 1:
                img = img.resize(new_size, Image.LANCZOS)

            # 出力先パス
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                out_path = output_dir / path.name
            else:
                out_path = path

            if backup and out_path.exists():
                bak = out_path.with_suffix(out_path.suffix + '.bak')
                if not bak.exists():
                    out_path.replace(bak)

            # WebP へ変換
            if convert_webp:
                webp_path = out_path.with_suffix('.webp')
                save_kwargs = {'quality': quality}
                if exif_bytes:
                    save_kwargs['exif'] = exif_bytes
                try:
                    img.save(webp_path, 'WEBP', **save_kwargs)
                except TypeError:
                    img.save(webp_path, 'WEBP', quality=quality)

                if not output_dir and path.exists() and webp_path.exists():
                    try:
                        path.unlink()
                    except Exception:
                        pass
                print(f"WROTE: {webp_path}")
                return True

            fmt = original_format.upper() if original_format else None
            if fmt in ('JPEG', 'JPG'):
                save_kwargs = {'quality': quality, 'optimize': True, 'progressive': True}
                if exif_bytes:
                    save_kwargs['exif'] = exif_bytes
                img.save(out_path, 'JPEG', **save_kwargs)
            elif fmt == 'PNG':
                pnginfo = None
                if isinstance(img.info, dict) and img.info:
                    pnginfo = PngImagePlugin.PngInfo()
                    for k, v in img.info.items():
                        if isinstance(v, str):
                            pnginfo.add_text(k, v)
                if pnginfo:
                    img.save(out_path, 'PNG', optimize=True, pnginfo=pnginfo)
                else:
                    img.save(out_path, 'PNG', optimize=True)
            else:
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
    p = argparse.ArgumentParser(description='Optimize images (resize, recompress, optional WebP) while preserving EXIF')
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
