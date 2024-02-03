import json
import secrets

with open('src/config.json', 'r', encoding='utf-8')as config:
    config = json.load(config)

def generate_keys(length=24):
    id = secrets.token_urlsafe(length)
    return id

print('Insaller software\n')

host = input('Введите ip-сервера: ')
port = int(input('Введите порт сервера: '))
api_key = input('Введите API ключ от форума: ')
node_id = int(input('Введите ID раздела для создания темы: '))
user_name = input('Введите имя пользователя: ')

secret_key = generate_keys()
id = generate_keys()

config['server']['host'] = host
config['server']['port'] = port
config['server']['user'] = user_name
config['forum']['node_id'] = node_id
config['forum']['api_key'] = api_key
config['secret'] = secret_key

with open('src/config.json', 'w', encoding='utf-8') as file:
    json.dump(config, file, ensure_ascii=False, indent=4)

data = {
    "clients": {
        "id": f"{id}",
        f"{id}": {
            "name": "reques6e",
            "thread_id": False,
            "post_id": False
        }
    }
}

with open('src/data.json', 'w+', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print(f'\nВаши данные:\nㅤㅤСсылка: http://{host}:{port}/client/{id}/webhook/devcore\nㅤㅤВаш секретный ключ: {secret_key}\nㅤㅤТип контента: application/json')