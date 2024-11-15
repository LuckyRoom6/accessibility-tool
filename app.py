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
                image_descriptions.append({'src': src, 'description': description})
            alt_message = None

        response.content_type = 'application/json'
        return json.dumps({
            'description': description_html,
            'aria_tags': aria_tags,
            'images_without_alt': image_descriptions,
            'alt_message': alt_message
        }, ensure_ascii=False)
    except openai.error.APIConnectionError as e:
        response.status = 500
        return json.dumps({'error': 'API connection error', 'details': str(e)})
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
以下はあるウェブページのHTML、JavaScript、およびCSSの内容です。
この内容をもとに、WCAG 2.2ガイドラインに基づく詳細なアクセシビリティ評価を実施してください。評価結果では、各ガイドラインの該当基準に基づいて見つかった問題点を具体的に指摘し、改善提案も併記してください。

特に以下の観点で評価を行い、各観点ごとに例を挙げて詳細に指摘してください：
1. **名前（name），役割（role）及び値（value）の達成基準**：ARIA属性の不足や誤用を指摘し、視覚障害者への支援強化を提案してください。
2. **色の使用**：視覚的に認識しにくい色やコントラストが低い部分の特定と、適切な色設定を推奨してください。
3. **非テキストコンテンツ**：代替テキストやラベルが不足している要素を特定し、補完するための改善案を出してください。
4. **リンクの目的（コンテキスト内）**：リンクのテキストが意味不明な部分や、複数リンクのテキストが同じで役割が曖昧なものについて、わかりやすいリンクラベルを提案してください。

### HTMLコンテンツ
{HTML_CONTENT}

### JavaScriptコンテンツ
{JS_CONTENT}

### CSSコンテンツ
{CSS_CONTENT}

上記内容に基づき、WCAG 2.2の各達成基準を網羅したレポートと改善提案を作成してください。
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
    prompt = f"以下の画像URLの内容を説明してください.さらにこの画像のAltタグを簡潔で分かりやすく生成してください: {image_url}"
    response = openai.ChatCompletion.create(
        model='gpt-4o-mini',
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        },
                    },
                ],
            }
        ],
        max_tokens=1200,
    )
    return response.choices[0].message.content

# run localhost
try:
    run(host='127.0.0.1', port=8000, reloader=True)
except KeyboardInterrupt:
    pass
