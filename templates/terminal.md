# ターミナルコピペ用プロンプト

# Build

## A) Hugo サーバで動作確認

hugo server -D & sleep 1 && open http://localhost:1313/

# 画像の前処理

## 0) 1~4を統合した単一ランナーがある場合はそれを使う

```bash
python run_tool.py
```

## 1) weight, commentを指定した album.csv から data/albums/*.json を生成

```bash
python tools/csv_to_data.py
```

## 2) EXIF のmodel, lens情報などの手動上書き

```bash
python tools/exif_overwrite.py
```

## 3) 画像サイズ最適化

```bash
python tools/optimize_images.py
```

## 4) GPS 削除など

```bash
python tools/delete_gps.py content/gallery/<album>
```

