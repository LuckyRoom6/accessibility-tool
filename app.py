import openai
from bottle import *
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from utils.aria_helper import generate_aria_tags_for_elements
from utils.gpt_service import get_system_message
from utils.image_recognition import extract_images_without_alt, generate_image_description
import json
import markdown
import time
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# APIキーとエンドポイントURLの設定
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
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

@post('/')
def index():
    try:
        data = request.json
        html_content = data['page']
        styles_content = data.get('styles', '')  # スタイル情報の取得
        scripts_content = data.get('scripts', '')  # スクリプト情報の取得
        base_url = data.get('url')
        
        # 受け取ったデータのログ出力
        logger.info("Received data:")
        logger.info(f"Base URL: {base_url}")
        logger.info(f"Styles content length: {len(styles_content)}")
        logger.info(f"First 500 chars of styles: {styles_content[:500]}")
        logger.info(f"Scripts content length: {len(scripts_content)}")
        
        # システムメッセージの取得
        system = get_system_message()
        
        # システムメッセージ内のプレースホルダーを置換
        if isinstance(system['content'], str):
            system['content'] = system['content'].replace(
                '{HTML_CONTENT}', html_content[:1000]  # HTMLの最初の1000文字
            ).replace(
                '{CSS_CONTENT}', styles_content[:1000]  # CSSの最初の1000文字
            )
            logger.info("System message after replacement:")
            logger.info(f"First 500 chars: {system['content'][:500]}")
        
        aria_tags = generate_aria_tags_for_elements(html_content)
        description_md = gpt(html_content)
        description_html = markdown.markdown(description_md, extensions=['fenced_code'])
        
        # `alt` タグがない画像を抽出して説明文を生成
        image_sources = extract_images_without_alt(html_content)
        image_descriptions = []
        if not image_sources:
            alt_message = "すべての画像にaltタグが設定されています。"
        else:
            for src in image_sources:
                description = generate_image_description(src, api_key, base_url)
                image_descriptions.append({
                    'src': src,
                    'description': description['description'],
                    'alt': description['alt']
                })
            alt_message = None

        aria_message = "すべての要素に適切なARIAタグが設定されています。" if not aria_tags else None

        response.content_type = 'application/json'
        return json.dumps({
            'description': description_html,
            'aria_tags': aria_tags,
            'images_without_alt': image_descriptions,
            'alt_message': alt_message,
            'aria_message': aria_message
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        response.status = 500
        return json.dumps({'error': 'Internal server error', 'details': str(e)})

@route('/favicon.ico')
def favicon():
    return ''

@route('/', method='GET')
def get_request():
    return "Server is running. Please use POST method."

def message(role, text):
    return {'role': role, 'content': text}
system = get_system_message()

def gpt(text):
    for attempt in range(3):
        try:
            response = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[system] + [message('user', text)],
                response_format={"type": "json_object"}
            )
            generated_json = json.loads(response.choices[0].message['content'])
            logger.info("Generated JSON by GPT:")
            logger.info(json.dumps(generated_json, indent=2, ensure_ascii=False)[:500])
            
            # Convert JSON to markdown for existing markdown rendering
            markdown_description = convert_json_to_markdown(generated_json)
            return markdown_description
        except (openai.error.APIConnectionError, json.JSONDecodeError) as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < 2:
                time.sleep(2)
                continue
            else:
                raise e

def convert_json_to_markdown(json_data):
    markdown_output = "\n\n"
    filtered_criteria = [
        criterion for criterion in json_data.get('wcag_analysis', []) 
        if int(criterion['total_issues']) > 0
    ]

    for criterion in filtered_criteria:
        markdown_output += "\n\n"
        markdown_output += f"## 🔍 達成基準: {criterion['criterion']} (レベル: {criterion['level']})\n\n"
        markdown_output += f"- **カテゴリ:** {criterion['category']}\n"
        markdown_output += f"- **重要度:** {criterion['importance']}\n"
        markdown_output += f"- **検出された問題数:** {criterion['total_issues']}\n\n"

        markdown_output += "\n"

        for issue in criterion.get('issues', []):
            markdown_output += "### 🚨 具体的な問題\n\n"
            markdown_output += f"- **問題箇所:** `{issue['location']}`\n"
            markdown_output += f"- **問題点:** {issue['problem_description']}\n"
            markdown_output += f"- **影響:** {issue['impact']}\n"
            markdown_output += f"- **深刻度:** {issue['severity']}\n\n"

            markdown_output += "### 🛠 修正提案\n\n"
            markdown_output += f"**提案内容:** {issue['recommendation']['description']}\n\n"
            markdown_output += f"**修正理由:** {issue['recommendation']['rationale']}\n\n"

            markdown_output += "#### 修正前:\n"
            markdown_output += f"```html\n{issue['recommendation']['code_before']}\n```\n\n"
            markdown_output += "#### 修正後:\n"
            markdown_output += f"```html\n{issue['recommendation']['code_after']}\n```\n\n"

        if criterion.get('best_practices'):
            markdown_output += "### 🚀 長期的な改善戦略\n\n"
            for practice in criterion['best_practices']:
                markdown_output += f"- {practice}\n"
            markdown_output += "\n---\n\n"

    summary = json_data.get('summary', {})
    if summary and int(summary.get('total_issues', 0)) > 0:
        markdown_output += "## 📊 総合サマリー\n\n"
        markdown_output += f"- **全体の問題数:** {summary.get('total_issues', 'N/A')}\n\n"
        markdown_output += "\n---\n\n"
    return markdown_output


# run localhost
try:
    run(host='127.0.0.1', port=8000, reloader=True)
except KeyboardInterrupt:
    pass
