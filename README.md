# README

## プロジェクト概要

このアプリケーションは、ウェブページの HTML コンテンツを入力として、アクセシビリティの評価と改善提案を行います。
ページに含まれるテキスト、画像、ARIA 属性などを解析し、WCAG 2.2 に基づくアクセシビリティ診断を行います。

## 環境構築

### 1. Python インストール

Python 3.x が必要です。未インストールの場合、[公式サイト](https://www.python.org/downloads/)からダウンロードしてください。

### 2. 依存ライブラリのインストール

以下のコマンドで必要なライブラリをインストールします。

```
pip install openai bottle beautifulsoup4 markdown
```

### 3. API キー設定

`utils\image_recognition.py]` と `app.py` にある `[GPT_API_KEI]` の部分を自分の OpenAI API キーに置き換えてください。

## 起動方法

次のコマンドでアプリケーションを起動します。

```
python app.py
```
