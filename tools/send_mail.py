import msal
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
AUTHORITY = os.getenv("AUTHORITY")
SCOPES = os.getenv("SCOPES").split(",")

# Authenticate and get access token
def get_access_token():
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    result = app.acquire_token_interactive(scopes=SCOPES)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Authentication failed: {result.get('error_description', result)}")

# Send email
def send_email(recipient, subject, body):
    token = get_access_token()
    #print(f'get sendmail {token}')
    endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    email_data = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": recipient}}],
        }
    }
    response = requests.post(endpoint, headers=headers, json=email_data)
    response.raise_for_status()
    return "Email sent successfully!"

# Register tool
def send_mail_tool(recipient: str, subject: str, body: str):
    return send_email(recipient, subject, body)
