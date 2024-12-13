from bs4 import BeautifulSoup

def convert_element_to_text(element):
    if element.name == 'button':
        return 'ボタン要素'
    elif element.name == 'input':
        input_type = element.attrs.get('type', 'text')
        return f'入力フィールド (type="{input_type}")'
    else:
        return '要素情報が不足しています。'

def generate_aria_tags_for_elements(html):
    soup = BeautifulSoup(html, 'html.parser')
    aria_tags = []
    interactive_elements = soup.find_all(['button', 'input'])
    for elem in interactive_elements:
        # ARIA属性やroleが設定されていない場合のみ抽出
        # 以下の属性がない場合のみ提案を生成
        aria_attributes = ['aria-label', 'aria-labelledby', 'aria-controls', 'aria-expanded', 'role']
        if not any(attr in elem.attrs for attr in aria_attributes):
            element_info = convert_element_to_text(elem)
            suggested_role = 'role="button"' if elem.name == 'button' else 'role="textbox"'
            aria_tags.append({
                'element': elem.name,
                'info': element_info,
                'suggested_aria_tag': suggested_role,
                'html_snippet': str(elem)
            })
    return aria_tags
