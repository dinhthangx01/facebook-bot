from flask import Flask, request
import requests
import google.generativeai as genai

PAGE_ACCESS_TOKEN = 'EAAZAqqAFmC2IBP7KsOhBpHZBY41aMdZCPdNezsxgbQSMhVRj4EjOJvQJgekRJi7h6PqBApTATQ3yHBF3hZC912NaDyqTlBT68c9zjFZCPyXrPs0L6SXDaB8ZCghDRa1GezZANIwqX0xT5h6zCEWtsoFMeH0mQ4MTdUCQkHYdVZA78PEtffrELZBMmY8MeWVTwVkndwwWaYVr7uV2TzFbTc1iQkQVH1AZDZD'
VERIFY_TOKEN = '123abc'  # phải khớp với verify token bạn dùng để đăng ký webhook

GOOGLE_API_KEY = 'AIzaSyDkg1LFm2xqE97UhCocWY3vz6UBIDRE_HU'
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Invalid token", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    user_message = messaging_event["message"].get("text", "")
                    if user_message:
                        # Gửi câu hỏi cho Gemini
                        gemini_response = model.generate_content(user_message)
                        reply = gemini_response.text.strip()

                        # Trả lời lại Facebook
                        send_message(sender_id, reply)
    except Exception as e:
        print("Error:", e)
    return "ok", 200

def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, params=params, headers=headers, json=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
