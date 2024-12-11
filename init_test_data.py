
import json
import os

def init_test_data():
    config_dir = 'config'
    os.makedirs(config_dir, exist_ok=True)
    
    test_data = {
        'general_prompts.json': {
            'test_general': {
                'name': '测试通用Prompt',
                'prompt': '这是一个测试用的通用prompt'
            }
        },
        'category_prompts.json': {
            'test_category': {
                'name': '测试角色大类',
                'prompt': '这是一个测试用的角色大类prompt'
            }
        },
        'role_prompts.json': {
            'test_role': {
                'name': '测试角色',
                'prompt': '这是一个测试用的具体角色prompt'
            }
        },
        'prompt_context.json': {}
    }
    
    for filename, data in test_data.items():
        filepath = os.path.join(config_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    init_test_data()