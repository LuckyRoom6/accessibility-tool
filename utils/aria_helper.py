from bs4 import BeautifulSoup

def convert_element_to_text(element):
    if element.name == 'button':
        return f'ボタン: {element.get_text(strip=True) or "ボタンの機能を説明してください。"}'
    elif element.name == 'input':
        placeholder = element.attrs.get('placeholder', '入力フィールドの説明を追加してください。')
        return f'入力フィールド: {placeholder}'
    # elif element.name == 'a':
    #     return f'リンク: {element.get_text(strip=True) or "リンクの説明を追加してください。"}'
    else:
        return '要素の説明が不足しています。'

def generate_aria_tags_for_elements(html):
    soup = BeautifulSoup(html, 'html.parser')
    aria_tags = []
    interactive_elements = soup.find_all(['img', 'button', 'a', 'input'])
    for elem in interactive_elements:
        # ARIA属性やroleが設定されていない場合のみ抽出
        if not any(attr in elem.attrs for attr in ['aria-label', 'aria-labelledby', 'role']):
            element_info = convert_element_to_text(elem)
            if elem.name == 'button':
                aria_tags.append({
                    'element': 'button',
                    'info': element_info,
                    'suggested_aria_tag': 'role="button" aria-label="ボタンの機能を説明してください。"'
                })
            elif elem.name == 'input':
                aria_tags.append({
                    'element': 'input',
                    'info': element_info,
                    'suggested_aria_tag': 'role="textbox" aria-label="入力フィールドの説明を追加してください。"'
                })
            # elif elem.name == 'a':
            #     aria_tags.append({
            #         'element': 'a',
            #         'info': element_info,
            #         'suggested_aria_tag': 'role="link" aria-label="リンクの説明を追加してください。"'
            #     })
    return aria_tags
