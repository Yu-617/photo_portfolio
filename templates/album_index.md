---
# 最下層アルバム `content/gallery/<parent album>/.../<album>/index.md` のテンプレート
title: "Album Title"
date: # YYYY-MM-DDT00:00:00+09:00
description: "album description (markdown)"
weight: # float
params:
  # true にすると、ホームの注目枠に表示する
  featured: false
  # true にすると、URL直踏みでのみ表示
  private: false
resources:
  # カバー画像 (同ディレクトリに格納) を明示する例
  - src: feature_image.jpg # "feature" をファイル名に含めることは必須ではないが推奨
    title: "アルバムの見出しに使う短いキャプション（ライトボックス表示用）"
    params:
      cover: true 
      hidden: false    # true にするとギャラリ表示には出ない（カバー専用）
layout: "gallery"
---

main text (markdown)
