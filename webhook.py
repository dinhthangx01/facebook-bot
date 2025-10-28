from flask import Flask, request
import requests, os
from dotenv import load_dotenv
import google.generativeai as genai

# --- TẢI BIẾN MÔI TRƯỜNG (.env hoặc Render Environment) ---
load_dotenv()

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("EAAZAqqAFmC2IBP8vpzMHGSXaGVURXb6fgpTLsZBWtGQpq4jV0WYf0c6BUrttoWL6xy7hE0qjH6E93gJELrrxiPOMSwQdZCGjyiZBnQZBcT6o0ybayyKlGG6WZA3Ob7lu3brj39qXWebcHel3LC2cMDBsaVEZB3PFIunYpqB49ZCq8nXFljV0V1Kap2rWjGok0kDBTDm0XkaikjZC5IdPvnWfvS2YMJQZDZD")
VERIFY_TOKEN = os.getenv("123abc")
GEMINI_API_KEY = os.getenv("AIzaSyDkg1LFm2xqE97UhCocWY3vz6UBIDRE_HU")

# --- CẤU HÌNH GEMINI ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- ROUTE KIỂM TRA HOẠT ĐỘNG ---
@app.route("/", methods=["GET"])
def home():
    return "✅ Heaven Facebook Bot (Gemini 2.0 Flash) đang hoạt động!"

# --- ROUTE KIỂM TRA WEBHOOK (FACEBOOK YÊU CẦU) ---
@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Token không hợp lệ ❌", 403

# --- ROUTE NHẬN TIN NHẮN TỪ FACEBOOK ---
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    if data and data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry["messaging"]:
                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    user_message = event["message"]["text"]
                    reply_text = generate_reply(user_message)
                    send_message(sender_id, reply_text)
    return "OK", 200

# --- XỬ LÝ TRẢ LỜI BẰNG GEMINI ---
def generate_reply(message_text):
    try:
        prompt = f"Hãy trả lời khách hàng một cách thân thiện, tự nhiên và ngắn gọn:\n\nKhách: {message_text}\nBot:"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("⚠️ Gemini error:", e)
        return "Xin lỗi, hiện tại tôi đang gặp sự cố, vui lòng thử lại sau."

# --- GỬI PHẢN HỒI LẠI FACEBOOK ---
def send_message(recipient_id, text):
    try:
        url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ Lỗi gửi tin nhắn: {response.text}")
    except Exception as e:
        print("⚠️ Send error:", e)

# --- CHẠY ỨNG DỤNG FLASK ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
