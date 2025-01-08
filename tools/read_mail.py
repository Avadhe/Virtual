import msal
import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

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

# Fetch emails


def fetch_emails():
    token = get_access_token()
    #print(f'get readmail {token}')
    endpoint = "https://graph.microsoft.com/v1.0/me/messages"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    emails = response.json().get("value", [])

    # Filter and include cleaned body in the response
    filtered_emails = []
    for email in emails:
        # Skip Teams notifications
        if email["from"]["emailAddress"]["address"] == "noreply@email.teams.microsoft.com":
            continue

        # Fetch email details to include body
        email_id = email["id"]
        detail_endpoint = f"{endpoint}/{email_id}"
        detail_response = requests.get(detail_endpoint, headers=headers)
        detail_response.raise_for_status()
        email_details = detail_response.json()

        # Extract the body content
        body_content = email_details["body"]["content"]
        if email_details["body"]["contentType"] == "html":
            # Parse HTML content using Beautiful Soup
            soup = BeautifulSoup(body_content, "html.parser")
            body_text = soup.get_text(separator="\n").strip()  # Cleaned plain text
        else:
            # Use plain text directly
            body_text = body_content.strip()

        filtered_emails.append({
            "subject": email["subject"],
            "sender": email["from"]["emailAddress"]["address"],
            "body": body_text
        })

    return filtered_emails


    



# Register tool
def read_mail_tool():
    return fetch_emails()
