from flask import Flask, request
import requests, os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd

# --- TẢI BIẾN MÔI TRƯỜNG (.env hoặc Render Environment) ---
load_dotenv()

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- CẤU HÌNH GEMINI ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- (TÙY CHỌN) TẠO BẢNG TOKEN CHO NHIỀU PAGE ---
# Nếu chỉ có 1 page, có thể để trống
PAGE_TOKENS = {
    # "467766493076266": os.getenv("PAGE_TOKEN_MOM"),
    # "230499322269144": os.getenv("PAGE_TOKEN_GOD")
}

# --- (TÙY CHỌN) ĐỌC DỮ LIỆU SẢN PHẨM / QUOTES TỪ EXCEL ---
excel_path = "quotes_links.xlsx"
if os.path.exists(excel_path):
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print("⚠️ Không đọc được file Excel:", e)
        df = pd.DataFrame(columns=["Quote", "Link"])
else:
    df = pd.DataFrame(columns=["Quote", "Link"])

def find_quote_link(user_message):
    """Tìm quote hoặc link phù hợp trong file Excel"""
    try:
        results = df[df["Quote"].str.contains(user_message, case=False, na=False)]
        if not results.empty:
            row = results.iloc[0]
            return f"{row['Quote']}\n👉 Link sản phẩm: {row['Link']}"
        return None
    except Exception as e:
        print("⚠️ Lỗi tìm trong Excel:", e)
        return None

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
        for entry in data.get("entry", []):  # ⚡ duyệt tất cả entry
            page_id = entry.get("id")        # lấy ID của page gửi đến
            for event in entry.get("messaging", []):  # ⚡ duyệt tất cả event
                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    user_message = event["message"]["text"]

                    # ✅ xử lý logic trả lời (AI hoặc Excel)
                    excel_reply = find_quote_link(user_message)
                    if excel_reply:
                        reply_text = excel_reply
                    else:
                        reply_text = generate_reply(user_message)

                    # ✅ gửi phản hồi lại đúng người, đúng page
                    send_message(sender_id, reply_text, page_id)
    return "OK", 200

# --- XỬ LÝ TRẢ LỜI BẰNG GEMINI ---
def generate_reply(message_text):
    try:
        prompt = f"""
        Bạn là chuyên viên tư vấn bán hàng thân thiện của Heaven Shop.
        Hãy trả lời khách hàng tự nhiên, cảm xúc và ngắn gọn.
        Nếu khách hỏi về sản phẩm, hãy gợi ý nhẹ nhàng, không ép mua.

        Khách: {message_text}
        Bot:"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("⚠️ Gemini error:", e)
        return "Xin lỗi, hiện tại tôi đang gặp sự cố, vui lòng thử lại sau."

# --- GỬI PHẢN HỒI LẠI FACEBOOK ---
def send_message(recipient_id, text, page_id=None):
    try:
        token = PAGE_TOKENS.get(page_id, PAGE_ACCESS_TOKEN)  # nếu chỉ 1 page
        url = f"https://graph.facebook.com/v17.0/me/messages?access_token={token}"

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
