import base64
from flask import Flask, request, jsonify, abort
import requests
import json
import hmac
import hashlib

app = Flask(__name__)

with open('src/config.json', 'r', encoding='utf-8')as config:
    config = json.load(config)
    host_server = config['server']['host']
    port_server = config['server']['port']
    user = config['server']['user']
    node_id = config['forum']['node_id']
    api_key = config['forum']['api_key']
    secret = config['secret']

def get_config():
    with open('src/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('src/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def is_valid_signature(payload, signature):
    hashed_payload = hmac.new(secret.encode('utf-8'), payload, hashlib.sha1).hexdigest()
    github_signature = "sha1=" + hashed_payload
    return hmac.compare_digest(github_signature, signature)

@app.route('/client/<string:client_id>/webhook/devcore', methods=['GET', 'POST'])
def webhook(client_id):
    data = get_config()
    github_data = request.get_json()

    title = github_data['repository']['name']
    message = github_data['head_commit']['message']

    payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature')

    if not is_valid_signature(payload, signature):
        abort(403)

    client_data = data['clients']

    if client_data['id'] == client_id:
        client_data = data['clients'][client_id]
        response = None

        if client_data['thread_id'] is False:
            readme_url = f"https://api.github.com/repos/{github_data['repository']['full_name']}/contents/ReadME.md"
            readme_response = requests.get(readme_url)

            if readme_response.status_code == 200:
                rd_content = readme_response.json().get('content', '')
                rd_content = base64.b64decode(rd_content).decode('utf-8')
                
                readme_content = rd_content + f'\n\n Репозиторий: [URL={github_data["repository"]["html_url"]}]{github_data["repository"]["name"]}[/URL]'
            else:
                readme_content = message

            response = requests.post(
                'https://api.devcore.fun/threads/',
                json={'node_id': node_id, 'title': title, 'message': readme_content},
                headers={'Api-Key': api_key}
            )
            response_json = response.json()

            new_thread_id = new_thread_id = response_json['data']['thread_id']
            client_data['thread_id'] = new_thread_id

            save_data(data)
            if response.status_code == 200:
                print('Успех.')
            else:
                print(f'[ERROR] Status code: {response.status_code}')
        else:
            message = f"""Репозиторий: [URL={github_data['repository']['html_url']}]{github_data['repository']['name']}[/URL]
                        Обновил: [URL={github_data['sender']['url']}]{github_data['sender']['login']}[/URL]
                        Информация: [URL={github_data['commits'][0]['url']}]{github_data['commits'][0]['id']}[/URL]\n\n
                        Хочешь так же? Ну так сделай же это! [URL=https://devcore.fun/threads/862/]Клик[/URL]""" # Изменил = хуйло
            thread_id = client_data['thread_id']

            response = requests.post(
                'https://api.devcore.fun/posts',
                json={'thread_id': thread_id, 'message': message},
                headers={'Api-Key': api_key}
            )

            if response.status_code == 200:
                print('Успех.')
            else:
                print(f'[ERROR] Status code: {response.status_code}')

        return jsonify({'message': 'Webhook processed successfully'}), 200
    else:
        abort(400)

if __name__ == '__main__':
    app.run(host='83.147.247.10', port=port_server, debug=True)
