import os
import sys
import piexif

def remove_gps_from_images(directory):
    # パスの存在確認
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    valid_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    files = [f for f in os.listdir(directory) if f.endswith(valid_extensions)]

    if not files:
        print("No JPEG images found in the directory.")
        return

    for filename in files:
        file_path = os.path.join(directory, filename)
        try:
            exif_dict = piexif.load(file_path)
            
            # GPS情報があれば削除
            if "GPS" in exif_dict and exif_dict["GPS"]:
                exif_dict["GPS"] = {}
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, file_path)
                print(f"Fixed: {filename}")
            else:
                print(f"Skip (No GPS): {filename}")
        except Exception as e:
            print(f"Error ({filename}): {e}")

if __name__ == "__main__":
    # 引数があればそれを使用、なければカレントディレクトリ
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    remove_gps_from_images(target)
    print("Done.")