from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import requests
from dotenv import load_dotenv
from personality_manager import PersonalityManager

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['JSON_AS_ASCII'] = False
personality_manager = PersonalityManager()

# 设置Live2D静态文件目录
@app.route('/static/live2d-widget/<path:path>')
def send_live2d(path):
    return send_from_directory('live2d-widget', path)

@app.route('/')
def home():
    return render_template('index.html', personalities=personality_manager.get_all_personalities())

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    personality_id = data.get('personality')
    
    if not user_message or not personality_id:
        return jsonify({'error': '缺少消息或角色选择'}), 400
    
    personality = personality_manager.get_personality(personality_id)
    if not personality:
        return jsonify({'error': '无效的角色选择'}), 400
    
    # 获取角色提示词
    personality_prompt = personality['prompt']
    
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
            {'role': 'system', 'content': personality_prompt},
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

# 添加管理角色的API端点
@app.route('/api/personalities', methods=['GET', 'POST'])
def manage_personalities():
    if request.method == 'GET':
        return jsonify(personality_manager.get_all_personalities())
    
    if request.method == 'POST':
        data = request.json
        personality_id = data.get('id')
        name = data.get('name')
        prompt = data.get('prompt')
        
        if not all([personality_id, name, prompt]):
            return jsonify({'error': '缺少必要的字段'}), 400
        
        personality_manager.add_personality(personality_id, name, prompt)
        return jsonify({'message': '添加成功'}), 201

@app.route('/api/personalities/<personality_id>', methods=['PUT', 'DELETE'])
def update_delete_personality(personality_id):
    if request.method == 'PUT':
        data = request.json
        name = data.get('name')
        prompt = data.get('prompt')
        
        if personality_manager.update_personality(personality_id, name, prompt):
            return jsonify({'message': '更新成功'})
        return jsonify({'error': '未找到指定角色'}), 404
    
    if request.method == 'DELETE':
        if personality_manager.delete_personality(personality_id):
            return jsonify({'message': '删除成功'})
        return jsonify({'error': '未找到指定角色'}), 404

@app.route('/switch_personality', methods=['POST'])
def switch_personality():
    data = request.get_json()
    personality_id = data.get('id')
    
    try:
        # 获取角色信息
        personality = personality_manager.get_personality(personality_id)
        if not personality:
            return jsonify({'error': '未找到指定角色'}), 404
            
        # 切换角色
        personality_manager.switch_personality(personality_id)
        
        # 返回成功信息和角色名称
        return jsonify({
            'message': '角色切换成功',
            'name': personality['name']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
