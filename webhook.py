from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = "123abc"
PAGE_ACCESS_TOKEN = "EAAZAqqAFmC2IBP8drQ7c6dT24UFh0cKbXCvQ5nQwy5C3OOtcVuB9CNHqqNCoDHprLNPkUrDBQAgUGu2qfG0iwIwbZAa660NLpsLtpEd55U1kWKON1P3lGijVyWUQY3CexqszNatPpeFP3Sv7rouuuhhONLrQMvl7xKFXCvBU6KXbuUWZB75nwBwS4DFk16iBdFKxLACce8TjD5R37FDNS1R2gZDZD"

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token"
    elif request.method == 'POST':
        data = request.get_json()
        for entry in data.get("entry", []):
            for messaging in entry.get("messaging", []):
                sender = messaging["sender"]["id"]
                if "message" in messaging:
                    text = messaging["message"].get("text", "")
                    send_message(sender, f"Bot nhận được: {text}")
        return "ok"

def send_message(recipient_id, message):
    url = "https://graph.facebook.com/v18.0/me/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
        "messaging_type": "RESPONSE"
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    requests.post(url, headers=headers, params=params, json=payload)

if __name__ == '__main__':
    app.run(port=5000)
