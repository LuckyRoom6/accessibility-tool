import openai
from bottle import *
from bs4 import BeautifulSoup
from utils.aria_helper import generate_aria_tags_for_elements
import json
import markdown
import time

# APIキーとエンドポイントURLの設定
api_key = '[GPT_API_KEI]'
openai.api_key = api_key
openai.api_base = 'https://api.openai.com/v1'

BaseRequest.MEMFILE_MAX = 1024 * 1024

# --- CORSへの対応
@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'

@route('/', method='OPTIONS')
def response_for_options(**kwargs):
    return {}

# --- CORSへの対応ここまで

@post('/')
def index():
    try:
        html_content = request.json['page']
        page_text = html_to_text(html_content)
        aria_tags = generate_aria_tags_for_elements(html_content)

        description_md = gpt(page_text)
        description_html = markdown.markdown(description_md, extensions=['fenced_code'])

        # `alt` タグがない画像を抽出して説明文を生成
        image_sources = extract_images_without_alt(html_content)
        image_descriptions = []

        if not image_sources:
            alt_message = "すべての画像にaltタグが設定されています。"
        else:
            for src in image_sources:
                description = generate_image_description(src)
                image_descriptions.append({
                    'src': src, 
                    'description': description['description'],
                    'alt': description['alt']
                })
            alt_message = None

        response.content_type = 'application/json'
        return json.dumps({
            'description': description_html,
            'aria_tags': aria_tags,
            'images_without_alt': image_descriptions,
            'alt_message': alt_message
        }, ensure_ascii=False)
    except Exception as e:
        response.status = 500
        return json.dumps({'error': 'Internal server error', 'details': str(e)})

@route('/favicon.ico')
def favicon():
    return ''

@route('/', method='GET')
def get_request():
    return "Server is running. Please use POST method."

# ChatGPTのAPIを使う準備
def message(role, text):
    return {'role': role, 'content': text}

system = message('system', """
                 あなたはウェブアクセシビリティの専門家として、提供されたHTMLコードを分析し、具体的なコード修正を提案します。
ウェブページのアクセシビリティ評価: JIS X 8341-3:2016 (WCAG 2.2) 準拠
提供されたウェブページのHTML、JavaScript、およびCSSコンテンツを、以下の観点から詳細に分析してください。各達成基準について、具体的な問題点と実践的な改善提案を提示してください。

### 詳細な評価観点:
   1.3.1 情報及び関係性 (レベルA):
   - 視覚的な書式や構造が、支援技術でも正確に解釈可能かを分析
   - フォーム要素とラベルの関連性
   - データテーブルのマークアップと構造
   - セマンティックなHTML要素の適切な使用

    1.3.2 意味のある順序 (レベルA):
   - コンテンツの論理的な読み取り順序を検証
   - CSSによるレイアウト変更が、意味の伝達に影響しないかを確認

    3. 理解可能性 (Understandable)
   3.1.1 ページの言語 (レベルA):
   - HTML言語属性の正確な設定
   - ページの主要言語が明確に宣言されているか
                
4. 堅牢性 (Robust)
   4.1.1 構文解析 (レベルA):
   - HTMLの妥当性
   - 重複するID
   - 開始タグと終了タグの整合性


### HTMLコンテンツ
{HTML_CONTENT}

### CSSコンテンツ
{CSS_CONTENT}

## 応答フォーマット:
1. 発見された問題
   場所: [問題のある箇所のコード]
   問題点: [具体的な説明]
   修正案: [具体的なコード]
   
2. WCAG達成基準
   - 違反している基準: [具体的な基準番号]
   - 重要度: [高/中/低]

3. コード修正
   ```html
   # 修正前
   [問題のあるコード]
   
   # 修正後
   [修正したコード]
   ```

4. 影響範囲
   - 影響を受けるユーザー: [具体的なユーザー層]
   - 支援技術への影響: [具体的な影響]

入力されたコードに対して、上記の形式で具体的な問題点と修正案を提示してください。
例示的な提案ではなく、実際のコードに基づいた具体的な修正を提供してください。
複数ある場合は複数お願いします。また修正する箇所がない場合はそのように書いてください。
""")

def gpt(text):
    for attempt in range(3):
        try:
            response = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[system] + [message('user', text)]
            )
            generated_text = response.choices[0].message['content']
            print("Generated Text by GPT:", generated_text)
            return generated_text
        except openai.error.APIConnectionError as e:
            if attempt < 2:
                time.sleep(2)
                continue
            else:
                raise e

# HTMLファイルの加工
def html_to_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    return '\n'.join(soup.stripped_strings)

# 画像の `alt` タグがないものを抽出する関数
def extract_images_without_alt(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img', alt=False)  # `alt` がない、もしくは空の画像を抽出
    image_sources = [img['src'] for img in images if 'src' in img.attrs]
    return image_sources

# GPTを使って画像の説明文を取得する関数
def generate_image_description(image_url):
    openai.api_key = api_key
    
    # 画像の詳細な説明を生成
    description_prompt = f"以下の画像URLの内容を説明してください: {image_url}"
    description_response = openai.ChatCompletion.create(
        model='gpt-4o-mini',
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": description_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        },
                    },
                ],
            }
        ],
        max_tokens=250,  # 詳細な説明用のトークン数
    )
    detailed_description = description_response.choices[0].message.content

    # Alt タグの簡潔な説明を生成
    alt_prompt = f"以下の画像URLのAltタグを簡潔で分かりやすく生成してください: {image_url}"
    alt_response = openai.ChatCompletion.create(
        model='gpt-4o-mini',
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": alt_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        },
                    },
                ],
            }
        ],
        max_tokens=50,  # Alt タグは簡潔に
    )
    alt_text = alt_response.choices[0].message.content

    return {
        'description': detailed_description,
        'alt': alt_text
    }


# run localhost
try:
    run(host='127.0.0.1', port=8000, reloader=True)
except KeyboardInterrupt:
    pass
