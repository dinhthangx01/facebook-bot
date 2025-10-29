from flask import Flask, request
import requests, os
from dotenv import load_dotenv
import google.generativeai as genai

# --- TẢI BIẾN MÔI TRƯỜNG (.env hoặc Render Environment) ---
load_dotenv()

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

    if data.get("object") == "page":
        for entry in data.get("entry", []):  # Duyệt tất cả entry
            page_id = entry.get("id")
            for event in entry.get("messaging", []):  # Duyệt từng event trong entry
                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    user_message = event["message"]["text"]

                    # ✅ Gọi Gemini tạo phản hồi
                    reply_text = generate_reply(user_message)

                    # ✅ Gửi phản hồi lại đúng người
                    send_message(sender_id, reply_text)
    return "OK", 200

# --- XỬ LÝ TRẢ LỜI BẰNG GEMINI ---
def generate_reply(message_text):
    try:
        prompt = f"Người dùng nhắn: {message_text}\nHãy trả lời thân thiện và tự nhiên:"
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
