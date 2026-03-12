import os
import sys
import argparse
import piexif


def remove_gps_from_images_in_dir(directory, dry_run=False):
    # パスの存在確認
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return 0

    valid_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    files = [f for f in os.listdir(directory) if f.endswith(valid_extensions)]

    if not files:
        return 0

    fixed = 0
    for filename in files:
        file_path = os.path.join(directory, filename)
        try:
            exif_dict = piexif.load(file_path)

            # GPS情報があれば削除
            if "GPS" in exif_dict and exif_dict["GPS"]:
                if dry_run:
                    print(f"[DRY] Would remove GPS: {file_path}")
                else:
                    exif_dict["GPS"] = {}
                    exif_bytes = piexif.dump(exif_dict)
                    piexif.insert(exif_bytes, file_path)
                    print(f"Fixed: {file_path}")
                fixed += 1
            else:
                print(f"Skip (No GPS): {file_path}")
        except Exception as e:
            print(f"Error ({file_path}): {e}")
    return fixed


def remove_gps_recursive(root_dir, dry_run=False):
    total_fixed = 0
    for dirpath, dirs, files in os.walk(root_dir):
        fixed = remove_gps_from_images_in_dir(dirpath, dry_run=dry_run)
        total_fixed += fixed
    print(f"Total fixed: {total_fixed}")
    return total_fixed


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Remove GPS EXIF from JPEG files (optionally recursive)')
    p.add_argument('target', nargs='?', default='.', help='Target directory')
    p.add_argument('--recursive', action='store_true', help='Recurse into subdirectories')
    p.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = p.parse_args()

    if args.recursive:
        remove_gps_recursive(args.target, dry_run=args.dry_run)
    else:
        remove_gps_from_images_in_dir(args.target, dry_run=args.dry_run)
    print("Done.")