import openai
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# GPTを使って画像の説明文を取得する関数
def generate_image_description(image_url, api_key, base_url=None):
    openai.api_key = api_key
    
    # 相対パスの画像URLを絶対パスに変換
    if not image_url.startswith(('http://', 'https://')):
        if base_url:
            image_url = urljoin(base_url, image_url)
        else:
            return {
                'description': '画像の絶対パスを特定できませんでした。',
                'alt': '画像の詳細を読み取れません'
            }

    try:
        # 画像の詳細な説明を生成
        description_prompt = f"以下の画像URLの内容を簡潔に分かりやすい説明を50文字以内で生成してください: {image_url}"
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
            max_tokens=80,
        )
        detailed_description = description_response.choices[0].message.content

        # Alt タグの簡潔な説明を生成
        alt_prompt = f"以下の画像URLの適切で簡潔な画像が見えない人でもわかるようなAltタグを10文字以内で生成してください: {image_url}"
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
            max_tokens=18,
        )
        alt_text = alt_response.choices[0].message.content

        return {
            'description': detailed_description,
            'alt': alt_text
        }
    except Exception as e:
        return {
            'description': f'画像の説明を生成できませんでした: {str(e)}',
            'alt': '画像の詳細を読み取れません'
        }

# 画像の `alt` タグがないものを抽出する関数 (Next.js Image対応)
def extract_images_without_alt(html_content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 標準の <img> タグで alt がないものを抽出
    standard_images = soup.find_all('img', alt=lambda x: x is None or x.strip() == '')
    
    # Next.js の Image コンポーネントで alt がないものを抽出
    # Next.js Image は通常 next/image から来るので、特定の属性を持つ要素を探す
    next_images = soup.find_all('img', {
        'data-next-image': True,
        'alt': lambda x: x is None or x.strip() == ''
    })
    
    # すべての画像のソースを収集
    image_sources = []
    
    # 標準の <img> タグのソース
    image_sources.extend([img['src'] for img in standard_images if 'src' in img.attrs])
    
    # Next.js Image コンポーネントのソース
    image_sources.extend([img['src'] for img in next_images if 'src' in img.attrs])
    
    return image_sources