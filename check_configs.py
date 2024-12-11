
import os
import json

def check_configs():
    """检查配置文件是否存在且格式正确"""
    config_dir = 'config'
    required_files = [
        'general_prompts.json',
        'category_prompts.json',
        'role_prompts.json',
        'prompt_context.json'
    ]
    
    errors = []
    
    for filename in required_files:
        filepath = os.path.join(config_dir, filename)
        if not os.path.exists(filepath):
            errors.append(f"缺少配置文件: {filepath}")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError:
            errors.append(f"配置文件格式错误: {filepath}")
    
    if errors:
        for error in errors:
            print(error)
        raise Exception("配置文件检查失败")
    else:
        print("所有配置文件检查通过")

if __name__ == '__main__':
    check_configs()