import json
import os

class PersonalityManager:
    def __init__(self, config_dir='config'):
        self.config_dir = config_dir
        self.general_prompts = self._load_config('general_prompts.json')
        self.category_prompts = self._load_config('category_prompts.json')
        self.role_prompts = self._load_config('role_prompts.json')

    def _load_config(self, filename):
        """从配置文件加载设定"""
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 未找到配置文件 {filepath}")
            return {}
        except json.JSONDecodeError:
            print(f"错误: 配置文件 {filepath} 格式不正确")
            return {}

    def _save_config(self, data, filename):
        """保存设定到配置文件"""
        filepath = os.path.join(self.config_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # 通用Prompt相关方法
    def get_all_general_prompts(self):
        """获取所有通用prompt"""
        return self.general_prompts

    def get_general_prompt(self, prompt_id):
        """获取指定的通用prompt"""
        return self.general_prompts.get(prompt_id)

    def add_general_prompt(self, prompt_id, name, prompt):
        """添加新的通用prompt"""
        self.general_prompts[prompt_id] = {
            "name": name,
            "prompt": prompt
        }
        self._save_config(self.general_prompts, 'general_prompts.json')

    # 角色大类Prompt相关方法
    def get_all_categories(self):
        """获取所有角色大类"""
        return self.category_prompts

    def get_category(self, category_id):
        """获取指定角色大类的设定"""
        return self.category_prompts.get(category_id)

    def add_category(self, category_id, name, prompt):
        """添加新的角色大类"""
        self.category_prompts[category_id] = {
            "name": name,
            "prompt": prompt
        }
        self._save_config(self.category_prompts, 'category_prompts.json')

    # 具体角色Prompt相关方法
    def get_all_roles(self):
        """获取所有具体角色设定"""
        return self.role_prompts

    def get_role(self, role_id):
        """获取指定具体角色的设定"""
        return self.role_prompts.get(role_id)

    def add_role(self, role_id, name, category, prompt):
        """添加新的具体角色设定"""
        self.role_prompts[role_id] = {
            "name": name,
            "category": category,
            "prompt": prompt
        }
        self._save_config(self.role_prompts, 'role_prompts.json')

    def update_role(self, role_id, name=None, prompt=None):
        """更新现有具体角色的设定"""
        if role_id not in self.role_prompts:
            return False
        
        if name is not None:
            self.role_prompts[role_id]["name"] = name
        if prompt is not None:
            self.role_prompts[role_id]["prompt"] = prompt
        
        self._save_config(self.role_prompts, 'role_prompts.json')
        return True

    def delete_role(self, role_id):
        """删除指定的具体角色"""
        if role_id in self.role_prompts:
            del self.role_prompts[role_id]
            self._save_config(self.role_prompts, 'role_prompts.json')
            return True
        return False

    def switch_role(self, role_id):
        """切换到指定角色（如果需要特殊处理）"""
        return self.get_role(role_id) is not None

    def get_combined_prompt(self, role_id):
        """获取角色的完整prompt（组合通用prompt、大类prompt和具体角色prompt）"""
        role = self.get_role(role_id)
        if not role:
            return None

        prompts = []
        
        # 添加所有通用prompt
        for general_prompt in self.general_prompts.values():
            if general_prompt.get("prompt"):
                prompts.append(general_prompt["prompt"])

        # 添加角色大类prompt
        category_id = role.get("category")
        if category_id:
            category = self.get_category(category_id)
            if category and category.get("prompt"):
                prompts.append(category["prompt"])

        # 添加具体角色prompt
        if role.get("prompt"):
            prompts.append(role["prompt"])

        return "\n\n".join(prompts)
