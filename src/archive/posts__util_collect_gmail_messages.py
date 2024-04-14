import os.path
import base64
import random
import re
import string

from dateutil import parser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from tqdm import tqdm
import pandas as pd

from posts__util_clean_text import clean_author, clean_message_body

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )  # Adjust the file path as needed
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def decode_body(data):
    """Decode email body data from base64."""
    return base64.urlsafe_b64decode(data).decode("utf-8")


def find_body_in_parts(parts):
    """Recursively search for the email body in message parts."""
    for part in parts:
        if part["mimeType"] in ["text/plain", "text/html"]:
            return decode_body(part["body"]["data"])
        # Recursively search in subparts
        if "parts" in part:
            return find_body_in_parts(part["parts"])
    return ""


def get_message_body(message):
    """Extract and clean the email body."""
    body_text = ""
    if "data" in message["payload"]["body"]:
        body_text = decode_body(message["payload"]["body"]["data"])
    elif "parts" in message["payload"]:
        body_text = find_body_in_parts(message["payload"]["parts"])
    return body_text


def extract_header_value(headers, name):
    return next(
        (
            header["value"]
            for header in headers
            if header["name"].lower() == name.lower()
        ),
        "",
    )


def get_messages(service, user_id, messages):
    detailed_messages = []
    for msg in tqdm(messages, desc="Getting message details"):
        details = get_message_details(service, user_id, msg["id"])
        if details:
            detailed_messages.append(details)
    return detailed_messages


def format_date(date_str):
    try:
        dt = parser.parse(date_str)
        formatted_date = dt.strftime("%Y-%m-%d")
        return formatted_date
    except ValueError as e:
        print(f"Error: {e}")
        return None


def get_message_details(service, user_id, message_id):
    try:
        message = (
            service.users()
            .messages()
            .get(userId=user_id, id=message_id, format="full")
            .execute()
        )
        headers = message["payload"]["headers"]
        msg_body = get_message_body(message)

        # Extract header values in a functional approach
        author = extract_header_value(headers, "From")
        date = extract_header_value(headers, "Date")
        title = extract_header_value(headers, "Subject")

        return {
            "id": message["id"],
            "threadId": message["threadId"],
            "author": author,
            "date": date,
            "title": title,
            "body": msg_body,
        }
    except Exception as error:
        # Consider raising an exception or handling it in a more functional way
        return {"error": str(error)}


def list_messages(service, user_id, query):
    try:
        messages = []
        page_token = None
        while True:
            response = (
                service.users()
                .messages()
                .list(userId=user_id, q=query, pageToken=page_token)
                .execute()
            )
            messages.extend(response.get("messages", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        print(f"Found {len(messages)} messages")
        return messages
    except Exception as error:
        print(f"Failed to list messages: {error}")
        return []


def main():
    unique_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    service = get_gmail_service()
    user_id = "me"
    query = "list:chromium-extensions@chromium.org after:2024/01/01 before:2024/01/03"

    # Retrieve a list of messages
    messages = list_messages(service, user_id, query)
    detailed_messages = get_messages(service, user_id, messages)

    # Convert the detailed messages to a DataFrame
    df = pd.DataFrame(detailed_messages)

    # Clean the message body
    df["body"] = df["body"].apply(clean_message_body)
    # Remove messages with empty bodies
    df = df[df["body"].str.len() > 0]
    # Format the date column
    df["date"] = df["date"].apply(format_date)
    #
    df["author"] = df["author"].apply(clean_author)

    # Sort the DataFrame by 1) the "threadId" column, and 2) the "id" column
    df = df.sort_values(by=["threadId", "id"])

    # Save the detailed messages to an Excel file
    df.to_excel(f"quick_gmail_messages.xlsx", index=False)

    print(f"Saved {len(df)} messages to {unique_id}_gmail_messages_list.xlsx")


if __name__ == "__main__":
    main()
