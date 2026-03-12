---
# 親アルバム (`content/gallery/<parent>/.../<parent>/_index.md`) のテンプレート
title: "Parent Album Title"
description: "parent album description (markdown)"
weight: # float
menus: "main"    # メニューに表示したい場合
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
