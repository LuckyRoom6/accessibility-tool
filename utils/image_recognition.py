import requests

def recognize_image(image_url):
    # 画像認識APIのURLとAPIキー
    api_url = 'https://api.openai.iniad.org/api/v1/images/generate-description'
    api_key = '[GPT_API_KEI]'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'image_url': image_url
    }
    
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result.get('description', 'No description available')
    else:
        return 'Failed to get description'
