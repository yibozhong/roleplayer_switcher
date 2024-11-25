import json
import os

class PersonalityManager:
    def __init__(self, config_path='config/personalities.json'):
        self.config_path = config_path
        self.personalities = self._load_personalities()

    def _load_personalities(self):
        """从配置文件加载角色设定"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 未找到配置文件 {self.config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"错误: 配置文件 {self.config_path} 格式不正确")
            return {}

    def save_personalities(self):
        """保存角色设定到配置文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.personalities, f, ensure_ascii=False, indent=4)

    def get_all_personalities(self):
        """获取所有角色设定"""
        return self.personalities

    def get_personality(self, personality_id):
        """获取指定角色的设定"""
        return self.personalities.get(personality_id)

    def add_personality(self, personality_id, name, prompt):
        """添加新的角色设定"""
        self.personalities[personality_id] = {
            "name": name,
            "prompt": prompt
        }
        self.save_personalities()

    def update_personality(self, personality_id, name=None, prompt=None):
        """更新现有角色的设定"""
        if personality_id not in self.personalities:
            return False
        
        if name is not None:
            self.personalities[personality_id]["name"] = name
        if prompt is not None:
            self.personalities[personality_id]["prompt"] = prompt
        
        self.save_personalities()
        return True

    def delete_personality(self, personality_id):
        """删除指定的角色设定"""
        if personality_id in self.personalities:
            del self.personalities[personality_id]
            self.save_personalities()
            return True
        return False
