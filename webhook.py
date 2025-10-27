from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

VERIFY_TOKEN = "123abc"  # dùng giống lúc đăng ký với Facebook
PAGE_ACCESS_TOKEN = "EAAG..."  # <-- thay bằng token trang Page của bạn
GEMINI_API_KEY = "AIza..."      # <-- thay bằng API key của Gemini bạn đã dán

# Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Xác minh webhook từ Facebook
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Xác minh thất bại", 403

    elif request.method == 'POST':
        data = request.get_json()
        if data['object'] == 'page':
            for entry in data['entry']:
                for messaging_event in entry['messaging']:
                    if 'message' in messaging_event:
                        sender_id = messaging_event['sender']['id']
                        message_text = messaging_event['message'].get('text')
                        if message_text:
                            reply = get_gemini_reply(message_text)
                            send_message(sender_id, reply)
        return "ok", 200

def get_gemini_reply(user_message):
    try:
        response = model.generate_content(user_message)
        return response.text.strip()
    except Exception as e:
        return "Xin lỗi, bot đang bận. Vui lòng thử lại sau."

def send_message(recipient_id, message_text):
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }
    auth = {'access_token': PAGE_ACCESS_TOKEN}
    url = 'https://graph.facebook.com/v17.0/me/messages'
    requests.post(url, params=auth, json=payload)

if __name__ == '__main__':
    app.run(debug=True)
