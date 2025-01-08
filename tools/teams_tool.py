import msal
import requests

CLIENT_ID = "e0a89cbc-8f4c-45bf-8b8a-6f5d6bd1f3bd"
AUTHORITY = "https://login.microsoftonline.com/d70cb4db-69c4-4a49-aaf3-f1e7ac277686"
SCOPES = ["Chat.ReadWrite"]
CHAT_ID = "19:0ad5c835-cad8-4103-a05f-1abef2c6cdc3_483d8231-30ff-416a-8799-f176cb490f45@unq.gbl.spaces"

app = msal.PublicClientApplication(
    CLIENT_ID,
    authority=AUTHORITY
)

def get_access_token():
    try:
        result = app.acquire_token_interactive(scopes=SCOPES)
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Authentication failed! Error: {result.get('error_description', result)}")
    except Exception as e:
        print(f"Failed to acquire token: {str(e)}")
        raise e
message="Hello from the Teams Tool!"
def send_teams_message(chat_id: str, message: str) -> str:
    try:
        token = get_access_token()
        endpoint = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        message_data = {"body": {"content": message}}

        print("Sending request to Microsoft Graph...")
        response = requests.post(endpoint, headers=headers, json=message_data)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()

        return "Message sent successfully to Teams chat!"
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise e

def notify_teams_tool(chat_id: str, message: str) -> str:
    return send_teams_message(chat_id, message)

# Test the function


