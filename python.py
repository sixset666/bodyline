from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    print("Ошибка: Не установлены переменные окружения TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID")
    exit()


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")
        return {'ok': False, 'error': str(e)}


@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print("Полученные данные:", data)

            # Правильное извлечение данных с учетом структуры JSON
            params = data.get('params', {})
            name = params.get('name', 'Не указано')
            phone = params.get('phone', 'Не указано')
            service = params.get('service', 'Не указано')

            # Декодирование Unicode
            name = name.encode('latin1').decode('unicode_escape') if name != 'Не указано' else 'Не указано'
            phone = phone.encode('latin1').decode('unicode_escape') if phone != 'Не указано' else 'Не указано'
            service = service.encode('latin1').decode('unicode_escape') if service != 'Не указано' else 'Не указано'

            message = f"*Новая заявка:*\n" \
                      f"*Имя:* {name}\n" \
                      f"*Телефон:* {phone}\n" \
                      f"*Услуга:* {service}"

            response = send_telegram_message(message)
            print(f"Ответ от Telegram API: {response}")

            if response.get('ok'):
                return jsonify({'status': 'success'}), 200
            else:
                print(f"Ошибка при отправке сообщения: {response.get('description')}")
                return jsonify({'status': 'error', 'message': response.get('description')}), 400

        except Exception as e:
            print(f"Ошибка обработки запроса: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 400
    else:
        return 'Method not allowed', 405


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
