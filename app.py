from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import requests
from dotenv import load_dotenv
from personality_manager import PersonalityManager

# 加载环境变量
load_dotenv()

# 检查必要的配置文��是否存在
required_configs = [
    'config/general_prompts.json',
    'config/category_prompts.json',
    'config/role_prompts.json',
    'config/prompt_context.json'
]

for config_file in required_configs:
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"缺少必要的配置文件: {config_file}")

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['JSON_AS_ASCII'] = False
personality_manager = PersonalityManager()

# 设置Live2D静态文件目录
@app.route('/static/live2d-widget/<path:path>')
def send_live2d(path):
    return send_from_directory('live2d-widget', path)

@app.route('/')
def home():
    return render_template('index.html', personalities=personality_manager.get_all_roles())

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    prompt_type = data.get('prompt_type')
    prompt_id = data.get('prompt_id')
    
    if not all([user_message, prompt_type, prompt_id]):
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 根据类型获取对应的prompt
    if prompt_type == 'general':
        prompt = personality_manager.get_general_prompt(prompt_id)
    elif prompt_type == 'category':
        prompt = personality_manager.get_category(prompt_id)
    elif prompt_type == 'role':
        prompt = personality_manager.get_role(prompt_id)
    else:
        return jsonify({'error': '无效的prompt类型'}), 400
    
    if not prompt:
        return jsonify({'error': '未找到指定的prompt'}), 404
    
    # 获取prompt内容和上下文
    prompt_content = prompt.get('prompt', '')
    context = prompt.get('context', '')
    
    # 组合prompt和上下文
    system_message = prompt_content
    if context:
        system_message = f"背景信息：{context}\n\n角色设定：{prompt_content}"

    # 调用Deepseek API
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        return jsonify({'error': '未设置API密钥'}), 500
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_message}
        ]
    }
    
    try:
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',  # 替换为实际的API地址
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# 获取所有角色列表
@app.route('/api/personalities', methods=['GET'])
def get_personalities():
    """获取所有角色列表"""
    roles = personality_manager.get_all_roles()
    categories = personality_manager.get_all_categories()
    
    # 为每个角色添加分类名称
    result = {}
    for role_id, role in roles.items():
        category_id = role.get('category')
        if category_id:
            category = categories.get(category_id, {})
            role_info = {
                'id': role_id,
                'name': role.get('name', ''),
                'category': category_id,
                'categoryName': category.get('name', '未分类'),
                'prompt': role.get('prompt', '')
            }
            result[role_id] = role_info
    
    return jsonify(result)

# 添加管理角色的API端点
@app.route('/api/personalities', methods=['POST'])
def manage_personalities():
    data = request.json
    personality_id = data.get('id')
    name = data.get('name')
    prompt = data.get('prompt')
        
    if not all([personality_id, name, prompt]):
        return jsonify({'error': '缺少必要的字段'}), 400
        
    personality_manager.add_role(personality_id, name, prompt)
    return jsonify({'message': '添加成功'}), 201

@app.route('/api/personalities/<personality_id>', methods=['PUT', 'DELETE'])
def update_delete_personality(personality_id):
    if request.method == 'PUT':
        data = request.json
        name = data.get('name')
        prompt = data.get('prompt')
        
        if personality_manager.update_role(personality_id, name, prompt):
            return jsonify({'message': '更新成功'})
        return jsonify({'error': '未找到指定角色'}), 404
    
    if request.method == 'DELETE':
        if personality_manager.delete_role(personality_id):
            return jsonify({'message': '删除成功'})
        return jsonify({'error': '未找到指定角色'}), 404

@app.route('/api/prompt_types', methods=['GET'])
def get_prompt_types():
    """获取所有prompt类型"""
    return jsonify({
        'general': {'name': '通用Prompt', 'description': '基础AI设���和行为准则'},
        'category': {'name': '角色大类Prompt', 'description': '不同类型角色的共同特征'},
        'role': {'name': '具体角色Prompt', 'description': '特定角色的个性化设定'}
    })

@app.route('/api/prompts/<type>', methods=['GET'])
def get_prompts_by_type(type):
    """根据类型获取对应的prompts"""
    if type == 'general':
        return jsonify(personality_manager.get_all_general_prompts())
    elif type == 'category':
        return jsonify(personality_manager.get_all_categories())
    elif type == 'role':
        return jsonify(personality_manager.get_all_roles())
    else:
        return jsonify({'error': '无效的prompt类型'}), 400

@app.route('/api/prompts/search', methods=['GET'])
def search_prompts():
    """搜索prompts"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    results = personality_manager.search_prompts(query)
    return jsonify(results)

@app.route('/api/prompts/<prompt_type>/<prompt_id>', methods=['GET', 'PUT'])
def manage_prompt(prompt_type, prompt_id):
    """获取或更新prompt信息"""
    if request.method == 'GET':
        if prompt_type == 'general':
            prompt = personality_manager.get_general_prompt(prompt_id)
        elif prompt_type == 'category':
            prompt = personality_manager.get_category(prompt_id)
        elif prompt_type == 'role':
            prompt = personality_manager.get_role(prompt_id)
        else:
            return jsonify({'error': '无效的prompt类型'}), 400
        
        if not prompt:
            return jsonify({'error': '未找到指定的prompt'}), 404
        
        return jsonify(prompt)
    
    elif request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({'error': '请提供更新内容'}), 400
        
        try:
            if prompt_type == 'general':
                success = personality_manager.update_general_prompt(
                    prompt_id, 
                    name=data.get('name'),
                    prompt=data.get('prompt'),  # 修改这里：prompt_content -> prompt
                    context=data.get('context', '')  # 确保context为空字符串而不是None
                )
            elif prompt_type == 'category':
                success = personality_manager.update_category_prompt(
                    prompt_id, 
                    name=data.get('name'),
                    prompt=data.get('prompt'),  # 修改这里：prompt_content -> prompt
                    context=data.get('context', '')  # 确保context为空字符串而不是None
                )
            elif prompt_type == 'role':
                success = personality_manager.update_role_prompt(
                    prompt_id, 
                    name=data.get('name'),
                    prompt=data.get('prompt'),  # 修改这里：prompt_content -> prompt
                    context=data.get('context', '')  # 确保context为空字符串而不是None
                )
            else:
                return jsonify({'error': '无效的prompt类型'}), 400

            if success:
                return jsonify({'message': '更新成功'})
            return jsonify({'error': '更新失败'}), 400
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/switch_personality', methods=['POST'])
def switch_personality():
    data = request.get_json()
    personality_id = data.get('id')
    
    try:
        # 获取角色信息
        personality = personality_manager.get_role(personality_id)
        if not personality:
            return jsonify({'error': '未找到指定角色'}), 404
            
        # 切换角色
        personality_manager.switch_role(personality_id)
        
        # 返回成功信息和角色名称
        return jsonify({
            'message': '角色切换成功',
            'name': personality['name']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 修改添加prompt的路由
@app.route('/api/prompts', methods=['POST'])
def add_prompt():
    """添加新的prompt"""
    data = request.json
    prompt_type = data.get('type')
    
    try:
        if prompt_type == 'general':
            personality_manager.add_general_prompt(
                data['id'], data['name'], data['prompt'], data.get('context'))
        elif prompt_type == 'category':
            personality_manager.add_category_prompt(
                data['id'], data['name'], data['prompt'], data.get('context'))
        elif prompt_type == 'role':
            personality_manager.add_role(
                data['id'], data['name'], data['prompt'], data.get('context'))
        else:
            return jsonify({'error': '无效的prompt类型'}), 400
        
        return jsonify({'message': '添加成功'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
