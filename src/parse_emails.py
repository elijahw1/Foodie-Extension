from pyexpat.errors import messages
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import email
import re

SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly"
        ]
KEYWORDS = [
    "free", "discount", "% off", "save", "limited time", "combo meal", "deal",
    "value meal", "exclusive offer", "new", "fresh", "hot", "crispy", "delicious",
    "tasty", "order now", "fast delivery", "grab yours", "special", "meal deal",
    "family pack", "free drink", "extra", "upgrade", "add-on", "coupon",
    "promo code", "savings", "today only", "best price", "limited offer", "hot deal"
]

def contains_fast_food_promo(text, pattern):
    keyword_patterns = []
    for kw in KEYWORDS:
        if kw == "% off":
            keyword_patterns.append(r"%\s*off")  # allow optional space
        else:
            # Replace spaces with \s+ to allow flexible spacing
            pattern = re.sub(r'\s+', r'\\s+', re.escape(kw))
            keyword_patterns.append(pattern)
    return bool(pattern.search(text))

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, max_results=10):
    results = service.users().messages().list(
        userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    return messages

def get_message(service, user_id, msg_id):
    message = service.users().messages().get(
        userId=user_id, id=msg_id, format="raw").execute()
    msg_str = base64.urlsafe_b64decode(message["raw"].encode("ASCII"))
    msg = email.message_from_bytes(msg_str)
    return msg

def main():
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in KEYWORDS) + r')\b', re.IGNORECASE)
    service = authenticate_gmail()
    messages = list_messages(service, 10)
    for message in messages:
        msg = get_message(service, 'me', message['id'])
        print("")
        if contains_fast_food_promo(msg["subject"], pattern) == True:
            print(f"Subject: {msg['subject']}")


if __name__ == "__main__":
    main()