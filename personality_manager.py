import json
import os

class PersonalityManager:
    def __init__(self, config_dir='config'):
        self.config_dir = config_dir
        # 加载各类prompts配置文件
        self.general_prompts = self._load_config('general_prompts.json')
        self.category_prompts = self._load_config('category_prompts.json')
        self.role_prompts = self._load_config('role_prompts.json')
        self.prompt_context = self._load_config('prompt_context.json')

    def _load_config(self, filename):
        """从配置文件加载设定"""
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"错误: 找不到配置文件 {filepath}")
            raise FileNotFoundError(f"配置文件 {filepath} 不存在")
        except json.JSONDecodeError:
            print(f"错误: 配��文件 {filepath} 格式不正确")
            raise json.JSONDecodeError(f"配置文件 {filepath} 格式不正确")

    def _save_config(self, data, filename):
        """保存设定到配置文件"""
        filepath = os.path.join(self.config_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _get_context(self, prompt_type, prompt_id):
        """获取prompt的上下文信息"""
        try:
            return self.prompt_context.get(prompt_type, {}).get(prompt_id, {}).get('context', '')
        except Exception:
            return ''

    def get_all_general_prompts(self):
        """获取所有通用prompt"""
        return self.general_prompts

    def get_general_prompt(self, prompt_id):
        """获取指定的通用prompt"""
        prompt = self.general_prompts.get(prompt_id, {})
        if prompt:
            context = self._get_context('general', prompt_id)
            if context:
                prompt['context'] = context
        return prompt

    def add_general_prompt(self, prompt_id, name, prompt, context=None):
        """添加新的通用prompt"""
        self.general_prompts[prompt_id] = {
            "name": name,
            "prompt": prompt
        }
        if context:
            self._save_prompt_context('general', prompt_id, context)
        self._save_config(self.general_prompts, 'general_prompts.json')

    def get_all_categories(self):
        """���取所有角色大类"""
        return self.category_prompts

    def get_category(self, category_id):
        """获取指定角色大类的设定"""
        category = self.category_prompts.get(category_id, {})
        if category:
            context = self._get_context('category', category_id)
            if context:
                category['context'] = context
        return category

    def add_category(self, category_id, name, prompt):
        """添加新的角色大类"""
        self.category_prompts[category_id] = {
            "name": name,
            "prompt": prompt
        }
        self._save_config(self.category_prompts, 'category_prompts.json')

    def add_category_prompt(self, prompt_id, name, prompt, context=None):
        """添加新的角色大类prompt"""
        self.category_prompts[prompt_id] = {
            "name": name,
            "prompt": prompt
        }
        if context:
            self._save_prompt_context('category', prompt_id, context)
        self._save_config(self.category_prompts, 'category_prompts.json')

    def _save_prompt_context(self, prompt_type, prompt_id, context):
        """保存prompt的上下文信息"""
        if prompt_type not in self.prompt_context:
            self.prompt_context[prompt_type] = {}
        self.prompt_context[prompt_id] = {'context': context}
        self._save_config(self.prompt_context, 'prompt_context.json')

    # 具体角色Prompt相关方法
    def get_all_roles(self):
        """获取所有具体角色设定"""
        return self.role_prompts

    def get_role(self, role_id):
        """获取指定具体角色的设定，包括类别信息"""
        role = self.role_prompts.get(role_id, {})
        if role:
            # 添加类别信息
            category_id = role.get('category')
            if category_id:
                category = self.category_prompts.get(category_id, {})
                role['categoryName'] = category.get('name', '未分类')
            
            # 获取上下文信息
            context = self._get_context('role', role_id)
            if context:
                role['context'] = context
        return role

    def add_role(self, role_id, name, prompt, category=None, context=None):
        """添加新的具体角色prompt，支持类别和上下文"""
        self.role_prompts[role_id] = {
            "name": name,
            "prompt": prompt,
            "category": category
        }
        if context:
            self._save_prompt_context('role', role_id, context)
        self._save_config(self.role_prompts, 'role_prompts.json')
        return True

    def update_role(self, role_id, name=None, prompt=None, category=None, context=None):
        """更新现有具体角色的设定，包括类别和上下文"""
        if role_id not in self.role_prompts:
            return False
        
        if name is not None:
            self.role_prompts[role_id]["name"] = name
        if prompt is not None:
            self.role_prompts[role_id]["prompt"] = prompt
        if category is not None:
            self.role_prompts[role_id]["category"] = category
        if context is not None:
            self._save_prompt_context('role', role_id, context)
        
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
        """获取角色的完整prompt，包括通用、类别和具体角色的prompt"""
        role = self.get_role(role_id)
        if not role:
            return None

        prompts = []
        contexts = []
        
        # 添加通用prompt和上下文
        for general_id, general_prompt in self.general_prompts.items():
            if general_prompt.get("prompt"):
                prompts.append(general_prompt["prompt"])
                context = self._get_context('general', general_id)
                if context:
                    contexts.append(context)

        # 添加角色大类prompt和上下文
        category_id = role.get("category")
        if category_id:
            category = self.get_category(category_id)
            if category and category.get("prompt"):
                prompts.append(category["prompt"])
                context = self._get_context('category', category_id)
                if context:
                    contexts.append(context)

        # 添加具体角色prompt和上下文
        if role.get("prompt"):
            prompts.append(role["prompt"])
            context = self._get_context('role', role_id)
            if context:
                contexts.append(context)

        # 组合上下文和prompt
        final_prompt = ""
        if contexts:
            final_prompt += "背景信息：\n" + "\n".join(contexts) + "\n\n"
        final_prompt += "角色设定：\n" + "\n\n".join(prompts)

        return final_prompt

    def update_prompt_content(self, prompt_type, prompt_id, new_content):
        """更新指定prompt的内容"""
        if prompt_type == 'general':
            if prompt_id in self.general_prompts:
                self.general_prompts[prompt_id]['prompt'] = new_content
                self._save_config(self.general_prompts, 'general_prompts.json')
                return True
        elif prompt_type == 'category':
            if prompt_id in self.category_prompts:
                self.category_prompts[prompt_id]['prompt'] = new_content
                self._save_config(self.category_prompts, 'category_prompts.json')
                return True
        elif prompt_type == 'role':
            if prompt_id in self.role_prompts:
                self.role_prompts[prompt_id]['prompt'] = new_content
                self._save_config(self.role_prompts, 'role_prompts.json')
                return True
        return False

    def update_prompt_context(self, prompt_type, prompt_id, new_context):
        """更新指定prompt的上下文信息"""
        if prompt_type not in self.prompt_context:
            self.prompt_context[prompt_type] = {}
        if prompt_id not in self.prompt_context[prompt_type]:
            self.prompt_context[prompt_type][prompt_id] = {}
        
        self.prompt_context[prompt_type][prompt_id]['context'] = new_context
        self._save_config(self.prompt_context, 'prompt_context.json')
        return True

    def search_prompts(self, query):
        """搜索所有prompts，支持按类别搜索"""
        results = {
            'general': {},
            'category': {},
            'role': {}
        }
        
        # 搜索通用prompts
        for id, prompt in self.general_prompts.items():
            if (query.lower() in prompt['name'].lower() or 
                query.lower() in prompt.get('prompt', '').lower()):
                results['general'][id] = prompt.copy()
                context = self._get_context('general', id)
                if context:
                    results['general'][id]['context'] = context

        # 搜索角色���类
        for id, prompt in self.category_prompts.items():
            if (query.lower() in prompt['name'].lower() or 
                query.lower() in prompt.get('prompt', '').lower()):
                results['category'][id] = prompt.copy()
                context = self._get_context('category', id)
                if context:
                    results['category'][id]['context'] = context

        # 搜索具体角色
        for id, prompt in self.role_prompts.items():
            if (query.lower() in prompt['name'].lower() or 
                query.lower() in prompt.get('prompt', '').lower()):
                role = prompt.copy()
                # 添加类别名称
                category_id = role.get('category')
                if category_id and category_id in self.category_prompts:
                    role['categoryName'] = self.category_prompts[category_id]['name']
                context = self._get_context('role', id)
                if context:
                    role['context'] = context
                results['role'][id] = role

        return results

    def update_general_prompt(self, prompt_id, name=None, prompt=None, context=None):
        """更新通用prompt"""
        if prompt_id not in self.general_prompts:
            return False
        
        if name:
            self.general_prompts[prompt_id]['name'] = name
        if prompt:
            self.general_prompts[prompt_id]['prompt'] = prompt
        if context is not None:  # 允许清空context
            self._save_prompt_context('general', prompt_id, context)
        
        self._save_config(self.general_prompts, 'general_prompts.json')
        return True

    def update_category_prompt(self, prompt_id, name=None, prompt=None, context=None):
        """更新角色大类prompt"""
        if prompt_id not in self.category_prompts:
            return False
        
        if name:
            self.category_prompts[prompt_id]['name'] = name
        if prompt:
            self.category_prompts[prompt_id]['prompt'] = prompt
        if context is not None:
            self._save_prompt_context('category', prompt_id, context)
        
        self._save_config(self.category_prompts, 'category_prompts.json')
        return True

    def update_role_prompt(self, prompt_id, name=None, prompt=None, context=None):
        """更新角色prompt"""
        if prompt_id not in self.role_prompts:
            return False
        
        if name:
            self.role_prompts[prompt_id]['name'] = name
        if prompt:
            self.role_prompts[prompt_id]['prompt'] = prompt
        if context is not None:
            self._save_prompt_context('role', prompt_id, context)
        
        self._save_config(self.role_prompts, 'role_prompts.json')
        return True

    def _get_context(self, prompt_name):
        """直接通过prompt名称获取背景知识"""
        return self.prompt_context.get(prompt_name, '')

    def _save_context(self, prompt_name, context):
        """保存prompt的背景知识"""
        self.prompt_context[prompt_name] = context
        self._save_config(self.prompt_context, 'prompt_context.json')
        return True

    def update_prompt(self, prompt_type, name, content, context=''):
        """统一的更新prompt方法"""
        prompt_data = {
            "name": name,
            "prompt": content
        }
        
        if prompt_type == 'general':
            self.general_prompts[name] = prompt_data
            self._save_config(self.general_prompts, 'general_prompts.json')
        elif prompt_type == 'category':
            self.category_prompts[name] = prompt_data
            self._save_config(self.category_prompts, 'category_prompts.json')
        elif prompt_type == 'role':
            self.role_prompts[name] = prompt_data
            self._save_config(self.role_prompts, 'role_prompts.json')
        else:
            return False
            
        if context is not None:
            self._save_context(name, context)
        return True
