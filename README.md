# photo_portfolio

## 概要
本リポジトリは写真ポートフォリオサイトです。

サイトは以下よりアクセスできます。
- **[https://Yu-617.github.io/photo_portfolio/](https://Yu-617.github.io/photo_portfolio/)**

[スクショ1]

[スクショ2]

[スクショ3]

[Hugo](https://gohugo.io/)およびテーマ[hugo-theme-gallery](https://github.com/nicokaiser/hugo-theme-gallery) をベースにカスタマイズしています。

## 構成
### 運用
- **画像配置:** JPG はアルバムごとに `content/gallery/<album>/` 配下に配置してください。
- **表示順・コメント管理:** 各アルバムの並び順やキャプション用コメントは`<album>/` 配下のCSVで管理しています（`data/albums/*.json` は `tools/csv_to_data.py` により生成されます）。
- **画像処理・メタデータ反映:** 画像の最適化、EXIF の上書き、GPS 削除などの処理はすべて `tools/` 以下のスクリプトで行います。手動で個別に実行する代わりに、まとめて実行するには `run_tool.py` を実行してください。

### 主なツールファイル
- 設定・実行ラッパー: [run_tool.py](run_tool.py)
- EXIF 上書き設定: [tools/exif_overwrite_config.json](tools/exif_overwrite_config.json)
- ツール群: `tools/` ディレクトリ内に以下のスクリプトがあります（例）
	- `csv_to_data.py` — CSV → JSON（albums）
	- `exif_overwrite.py` — 条件に応じた EXIF 上書き（ルールは設定ファイル参照）
	- `optimize_images.py` — リサイズ / 再圧縮 / WebP 変換（EXIF を可能な限り保持）
	- `delete_gps.py` — JPEG から GPS 情報を削除

### 使い方
1. 画像を `content/gallery/<album>/` に格納し、`index.md`を作成する。
2. 必要ならアルバム CSV を編集して順序・コメントを指定する。
3. ツールを動かす（まずはドライラン推奨）:

```bash
# ドライラン（安全確認）
python3 run_tool.py --dry-run

# 実際に反映（バックアップを残す）
python3 run_tool.py

# 実行時にバックアップを作らない
python3 run_tool.py --no-backup
```
## 技術的情報
### 注意
- 依存: Python3, Pillow, （オプションで）piexif が必要です。インストール例:

```bash
python3 -m pip install Pillow piexif
```
- `exif_overwrite.py` と `optimize_images.py` は処理前に元ファイルのバックアップ（`.bak`）を作成する設定があります。まずは `--dry-run` で動作を確認してください。
- EXIF タグのルールは `tools/exif_overwrite_config.json` で定義します。例: `Exif:FNumber`（絞り）、`IFD0:Model`（カメラ本体）など。
- キャプション生成はページテンプレート側で EXIF の `LensModel` / `Lens` / `ImageDescription` 等を参照して組み立てています。表示の調整は [layouts/partials/gallery.html](layouts/partials/gallery.html) を編集してください。

### トラブルシュート
- 変更が適用されない場合は、まず対象画像で EXIF を確認してください:

```bash
python3 - <<'PY'
import piexif
ex = piexif.load('content/gallery/<album>/<file>.jpg')
print(ex)
PY
```
- 上書きルールは文字列比較で行われます。真偽判定に問題がある場合は `tools/exif_overwrite.py` を `--dry-run` で実行し、出力メッセージを参照してください。
