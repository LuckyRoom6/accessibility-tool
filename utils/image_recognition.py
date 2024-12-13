import openai
from urllib.parse import urljoin

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
            max_tokens=250,
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
            max_tokens=50,
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

# 画像の `alt` タグがないものを抽出する関数
def extract_images_without_alt(html_content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img', alt=False)  # `alt` がない、もしくは空の画像を抽出
    image_sources = [img['src'] for img in images if 'src' in img.attrs]
    return image_sources
