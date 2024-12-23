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

`.env` を追加し、 `OPENAI_API_KEY='[GPT_API_KEI]'` を入力し自分の OpenAI API キーに置き換えてください。

### 4. Google の拡張機能として、Chrome にインポート

1. [Chrome のメニュー](chrome://extensions/)から 拡張機能 を選択します。
2. ページ右上で デベロッパーモード を有効にします。
3. パッケージ化されていない拡張機能を読み込む をクリックし、プロジェクトのフォルダを選択します。

## 起動方法

次のコマンドでアプリケーションを起動します。

```
python app.py
```

拡張機能がオンになっている場合左下にアクセシビリティチェック開始ボタンが表示されますので、クリックすることでチェックが実行され、モーダルが表示されます。
