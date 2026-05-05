# photo_portfolio

## 概要
本リポジトリは写真ポートフォリオサイトです。
- **[https://Yu-617.github.io/photo_portfolio/](https://Yu-617.github.io/photo_portfolio/)**

[Hugo](https://gohugo.io/) および、そのテーマのひとつ [hugo-theme-gallery](https://github.com/nicokaiser/hugo-theme-gallery) をベースにカスタマイズしています。

PC

<img width="1646" height="790" alt="Image" src="https://github.com/user-attachments/assets/62963ee2-94ac-4ab9-972a-f5bc27d4389b" />
<img width="1641" height="881" alt="Image" src="https://github.com/user-attachments/assets/335fbff8-6f9e-40dc-a650-24ee2bcf9346" />
<img width="1650" height="878" alt="Image" src="https://github.com/user-attachments/assets/5fbac33f-842a-4531-adcb-399d82663dde" />

Mobile

<img width="364" height="655" alt="Image" src="https://github.com/user-attachments/assets/056ee1ed-5044-4445-8a67-c97b2300fada" />



## 運用方法

### 基本手順

1) アルバムに画像を追加する
	- 画像はJPGを想定しています。
	- 新規アルバムを作る際は `content/gallery/<album>/` を作成し、画像を格納します。
	- `content/gallery/<folder>/.../<folder>/<album>/` とすることで階層化も可能です。
	- アルバムに `index.md` (フォルダーなら `_index.md`) を置き、必要情報を記載してください。テンプレートは [`/templates/album_index.md`](https://github.com/Yu-617/photo_portfolio/blob/main/templates/album_index.md), [`/templates/parent__index.md`](https://github.com/Yu-617/photo_portfolio/blob/main/templates/parent__index.md) の通りです。

2) コメント・表示順を編集する (optional)
	- 各アルバムフォルダに `album.csv` を置くことで、各写真の表示順とコメント（画像クリック時のキャプションに記載）を指定できます。
	- テンプレートは [`/templates/album.csv`](https://github.com/Yu-617/photo_portfolio/blob/main/templates/album.csv) の通りです。
	- 表示順とコメントを反映するには、 [`/tools/csv_to_data.py`](https://github.com/Yu-617/photo_portfolio/blob/main/tools/csv_to_data.py) を実行し、JSONを生成する必要があります（後述）。

3) 画像の処理などを行う
	- **commitする前に [`run_tool.py`](https://github.com/Yu-617/photo_portfolio/blob/main/run_tool.py) (もしくは最低でも [`/tools/delete_gps.py`](https://github.com/Yu-617/photo_portfolio/blob/main/tools/delete_gps.py)) を実行することを強く推奨します。**
	- [`run_tool.py`](https://github.com/Yu-617/photo_portfolio/blob/main/run_tool.py) を実行する
	```bash
	python run_tool.py
	```
	ことで、以下の処理がまとめて実行されます。
	1. [`/tools/delete_gps.py`](https://github.com/Yu-617/photo_portfolio/blob/main/tools/delete_gps.py): 画像のEXIFに格納されているGPS情報を削除
	2. [`/tools/exif_overwrite.py`](https://github.com/Yu-617/photo_portfolio/blob/main/tools/exif_overwrite.py): EXIF上書き
		- キャプションに記載される、画像のEXIFに格納されているレンズ情報等を、手動で指定した形に上書き変更します。
		- 変更規則は [`/tools/exif_overwrite_config.json`](https://github.com/Yu-617/photo_portfolio/blob/main/tools/exif_overwrite_config.json) で指定します。
    3.  ~~[`/tools/optimize_images.py`](https://github.com/Yu-617/photo_portfolio/blob/main/tools/optimize_images.py): 画像の軽量化~~ (v1.3.0より `run_tool.py` において無効化中．個別ファイル呼び出しによる実行は可能)
    4.  [`/tools/csv_to_data.py`](https://github.com/Yu-617/photo_portfolio/blob/main/tools/csv_data.py): `album.csv` からのJSON生成

4) ローカルでの確認
```bash
hugo server -D & sleep 1 && open http://localhost:1313/
```
同じインターネット (wifi) を共有する別デバイスでも確認したい場合は
```bash
hugo server --bind 0.0.0.0 --baseURL http://[PC_IP_address] & sleep 1 && open http://localhost:1313      
```
の後に別デバイスで `http://[PC_IP_address]:1313` にアクセス

5) デプロイ
	- 問題がなければpushします。
	- 画像上書き時に生成されるバックアップファイル `*.bak` は `.gitignore` によりcommitされません。
	- [`/.github/workflows/hugo.yml`](https://github.com/Yu-617/photo_portfolio/blob/main/.github/workflows/hugo.yml) により自動的にHugoサイトがビルドされます。

### tag & release
- tag
   - tagの確認
     ```bash
     git tag -l
     ```
   - tagを打つ
     ```bash
     git tag -a v[version] -m "[comment]"  
     ```
   - push tag
   	 ```bash
     git push --tags
     ```
- release
  - githubにアクセスし，code -> releaseを選択
  - releaseに対応するtagを指定し，release



### その他注意
- ドライラン 
  - 末尾に `--dry-run` をつけることで、ツール実行前に挙動を確認できます。
- バックアップ
  - defaultでバックアップ `*.bak` が生成されます
  - `*.bak` を元に戻す場合の例: `mv img.jpg.bak img.jpg`
  - `*.bak` を削除する場合
  ```bash
  find . -type f -path "./content/gallery/*" -name "*.bak" -print -delete
  ```

