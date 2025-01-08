import msal
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
AUTHORITY = os.getenv("AUTHORITY")
SCOPES = ["Calendars.ReadWrite"]

def get_access_token():
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    result = app.acquire_token_interactive(scopes=SCOPES)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Authentication failed: {result.get('error_description', result)}")

def check_availability():
    token = get_access_token()
    #print(f'get calendar {token}')
    endpoint = "https://graph.microsoft.com/v1.0/me/events"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    events = response.json().get("value", [])

    busy_slots = [(event["start"]["dateTime"], event["end"]["dateTime"]) for event in events]
    current_time = datetime.now()
    free_slots = []

    for i in range(1, 7):  # Check for next 6 hours
        start = current_time + timedelta(hours=i)
        end = start + timedelta(hours=1)
        if all(not (start.isoformat() < busy[1] and end.isoformat() > busy[0]) for busy in busy_slots):
            free_slots.append({"start": start.isoformat(), "end": end.isoformat()})

    return free_slots

def schedule_meeting(subject, attendees, start_time, end_time):
    token = get_access_token()
    endpoint = "https://graph.microsoft.com/v1.0/me/events"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    event_data = {
        "subject": subject,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
        "attendees": [{"emailAddress": {"address": email}, "type": "required"} for email in attendees],
    }
    response = requests.post(endpoint, headers=headers, json=event_data)
    response.raise_for_status()
    return "Meeting scheduled successfully!"

def find_free_time_tool():
    return check_availability()

def schedule_meeting_tool(subject: str, attendees: list, start_time: str, end_time: str):
    return schedule_meeting(subject, attendees, start_time, end_time)
