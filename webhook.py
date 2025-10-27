from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# ======= THÔNG TIN CỦA BẠN (điền vào đây) =======
VERIFY_TOKEN = "123abc"   # Token xác minh webhook với Facebook
PAGE_ACCESS_TOKEN = "EAAZAqqAFmC2IBPZBJHVzvgv9UGjQZB3AIaFSIRJmSNngSrziOYtCLAwvmLs13J8caTsGXVdXGA3jfqVBC3B7Anr1TyoMTzvLo51HFNMSPkLrUhluJWhCkBRbIZChR0BccCwBlUVflwqmgp2J2mqk1IsXlM87IbKzwTDYZCxjTemY3L6dj7ZCTuRDw4Yx428oHEJHSdfHtQXdERYNRrqUc0NizACAZDZD"
GEMINI_API_KEY = "AIzaSyDkg1LFm2xqE97UhCocWY3vz6UBIDRE_HU"
# ================================================

# Cấu hình Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# ----------------- ROUTE FACEBOOK VERIFY -----------------
@app.route("/webhook", methods=['GET'])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Invalid verification token", 403


# ----------------- ROUTE NHẬN TIN NHẮN -----------------
@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    print("📩 Dữ liệu nhận được:", data)

    if "entry" in data:
        for entry in data["entry"]:
            for messaging_event in entry.get("messaging", []):
                if "message" in messaging_event:
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text", "")

                    if message_text:
                        reply = get_gemini_reply(message_text)
                        send_message(sender_id, reply)

    return "OK", 200


# ----------------- HÀM GỌI GEMINI -----------------
def get_gemini_reply(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Lỗi Gemini:", e)
        return "Xin lỗi, hiện tại tôi đang gặp sự cố, vui lòng thử lại sau."


# ----------------- HÀM GỬI TIN NHẮN FACEBOOK -----------------
def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    print("📤 Gửi trả:", response.text)


@app.route("/", methods=['GET'])
def home():
    return "✅ Facebook-Gemini bot đang hoạt động!", 200


if __name__ == "__main__":
    app.run(port=10000)
