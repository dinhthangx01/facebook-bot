from flask import Flask, request
import requests, os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("EAAZAqqAFmC2IBPZCUZCFY7Ks1wh3ZCVn8uZAihZCaJKRp5bB1OltYp3gnOo91ZCyD9iz4QkX31FqPn3RVWPHrX7X2ZApfO3CX6NjFuB4GDw8hrWRruKz8X7UeinWy8uNfqLGsw54EGlKIWyZCrG6DwHfU6KXZCUExEtFulbtbNbq0DtkshOnqoZCR3k1AcvbITzRH6Tb2OAOsq4F5N69mojNZCRBrpV2mgZDZD")
VERIFY_TOKEN = os.getenv("123abc")
GEMINI_API_KEY = os.getenv("GAIzaSyDkg1LFm2xqE97UhCocWY3vz6UBIDRE_HU")

# Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

@app.route("/", methods=["GET"])
def home():
    return "Gemini Facebook Bot đang hoạt động!"

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Token không hợp lệ", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for msg_event in entry["messaging"]:
                if "message" in msg_event:
                    sender_id = msg_event["sender"]["id"]
                    if "text" in msg_event["message"]:
                        user_message = msg_event["message"]["text"]
                        reply = generate_reply(user_message)
                        send_message(sender_id, reply)
    return "OK", 200

def generate_reply(message_text):
    try:
        prompt = f"Hãy trả lời tin nhắn của khách hàng một cách thân thiện, tự nhiên, dễ hiểu:\n\nKhách: {message_text}\nBot:"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini error:", e)
        return "Xin lỗi, hiện tôi đang gặp sự cố khi trả lời. ❤️"

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

