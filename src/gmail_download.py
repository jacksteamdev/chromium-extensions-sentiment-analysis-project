import base64
import os
import re
from datetime import datetime
from typing import List, Tuple

from bs4 import BeautifulSoup
from dateutil.parser import parse as dateutil_parse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from num_tokens_from_string import num_tokens_from_string


def get_gmail_service(scopes=["https://www.googleapis.com/auth/gmail.readonly"]):
    """Get Gmail service"""
    creds = None
    if os.path.exists("./token.json"):
        creds = Credentials.from_authorized_user_file("./token.json", scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "./credentials.json", scopes
            )  # Adjust the file path as needed
            creds = flow.run_local_server(port=0)
        with open("./token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def query_gmail_for_thread_ids(query: str) -> List[str]:
    """Query Gmail for Google Group threads by date range"""
    service = get_gmail_service()
    thread_ids = []
    page_token = None
    while True:
        response = (
            service.users()
            .threads()
            .list(userId="me", q=query, pageToken=page_token)
            .execute()
        )
        thread_ids.extend(response.get("threads", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return [thread["id"] for thread in thread_ids]


def decode_body(data):
    """Decode email body data from base64."""
    return base64.urlsafe_b64decode(data).decode("utf-8")


EMAIL_PAYLOAD_MIME_TYPES = {
    "text/html",
    "text/plain",
    "multipart/related",
    "multipart/mixed",
    "multipart/alternative",
}


def find_body_in_payload(
    payload, mime_types=["text/html", "text/plain"]
) -> Tuple[str, str]:
    """
    Recursively search for the email body in message parts.
    """
    # Check that MIME type is an expected email MIME type
    if payload["mimeType"] not in EMAIL_PAYLOAD_MIME_TYPES:
        print(f"Unexpected mimeType: {payload['mimeType']}")
        return "", ""
    # Find email body by order of preferred MIME type
    for mime_type in mime_types:
        # Decode email payload
        if payload["mimeType"] == mime_type:
            body_data = payload.get("body", {}).get("data", "")
            if body_data:
                return decode_body(body_data), mime_type
            else:
                raise ValueError("Invalid email payload structure.")
        # Find target type in payload parts
        if "parts" in payload:
            for part in payload["parts"]:
                body = find_body_in_payload(part, [mime_type])
                if body[1] == mime_type:
                    return body
    # Couldn't find body in this payload node
    return "", ""


def clean_message_sender(sender_name: str) -> str:
    """Remove unwanted text from the email sender's name"""
    # Remove "via Chromium Extensions" from author name
    sender_name = sender_name.removesuffix(" via Chromium Extensions")
    return sender_name


def parse_message_sender(sender: str) -> tuple[str, str]:
    """Get the sender name and email address"""
    name = ""
    email = ""
    if "<" in sender:
        email, name = [
            part[::-1].strip().replace('"', "") for part in sender[::-1].split("<")
        ]
        email = email[:-1]  # remove closing >
    else:
        email = sender
    return name, email


def parse_message_date(date_string: str) -> datetime:
    """Parse the email date string into a datetime object without the timezone."""
    parsed_date = dateutil_parse(date_string)
    return parsed_date.replace(tzinfo=None)


def parse_message_html(message_html: str):
    """Extract the email body and post url from the message HTML."""
    # The footer is preceeded by a break tag
    message_parts = message_html.split("-- <br />")
    # The footer is the last section of the email
    footer_html = message_parts[-1]
    # Recombine the other sections
    body_html = "-- <br />".join(message_parts[:-1])

    # Parse the HTML with BeautifulSoup
    body_soup = BeautifulSoup(body_html, "html.parser")
    # Remove all div.gmail_quote elements
    for div in body_soup.find_all("div", class_="gmail_quote"):
        div.decompose()
    # Get the body text
    body = body_soup.get_text()

    # Parse the HTML with BeautifulSoup
    footer_soup = BeautifulSoup(footer_html, "html.parser")
    # Get the last URL in the footer
    last_url = footer_soup.find_all("a")[-1].get("href")

    return body, last_url


def clean_text_whitespace(body_text):
    """Clean the thread message body text."""

    FLAGS = re.MULTILINE | re.DOTALL

    # Handle non-string input
    if not isinstance(body_text, str):
        return body_text

    # Remove non-printing characters, excluding newlines
    body_text = re.sub(r"[^\x20-\x7E\n]", "", body_text)

    # Compact multiple blank lines into one
    body_text = re.sub(r"(\s*\n){2,}", "\n\n", body_text)

    # Remove Windows-style newlines
    body_text = body_text.replace("\r", "")

    return body_text.strip()


def clean_message_subject(subject_text: str):
    """
    Remove unwanted text from an email subject line.

    Args:
        subject_text (str): The email subject line to be cleaned.

    Returns:
        str: The cleaned email subject line.
    """
    # Remove [crx] from email subject lines
    subject_text = subject_text.removeprefix("[crx] ")
    return subject_text


def get_message_header(header_name: str, first_message: dict) -> str:
    for header in first_message.get("payload", {}).get("headers", []):
        if header["name"] == header_name:
            subject = header["value"]
            break
    return subject


def get_thread_from_gmail(
    thread_id: str,
    thread_token_max: int,
    message_token_max: int,
) -> dict:
    """
    Get the final email in a thread from Gmail, which contains the full thread.
    Returns a thread data dict:
    - thread_id: id of the thread
    - subject: subject line of the first email in the thread
    - messages: list of dicts containing message body and sender
    - body: single text representing the full email thread
    """
    service = get_gmail_service()
    response = (
        service.users()
        .threads()
        .get(userId="me", id=thread_id, format="full")
        .execute()
    )

    # For each message in the thread, get the body and sender
    messages = []
    for message in response["messages"]:
        message_body, body_mime_type = find_body_in_payload(message["payload"])
        if body_mime_type == "text/html":
            message_body, message_url = parse_message_html(message_body)
        else:
            message_url = ""
        # skip the message if it has too many tokens
        message_token_count = num_tokens_from_string(message_body)
        if message_token_count > message_token_max:
            print(
                f"Skipping message with {message_token_count} tokens: {message['id']}"
            )
            continue
        message_date = parse_message_date(get_message_header("Date", message))
        sender_name, sender_email = parse_message_sender(
            get_message_header("From", message)
        )
        message_subject = clean_message_subject(get_message_header("Subject", message))
        messages.append(
            {
                "id": message["id"],
                "thread_id": thread_id,
                "sender_name": sender_name,
                "sender_email": sender_email,
                "body": message_body,
                "date": message_date,
                "url": message_url,
                "subject": message_subject,
            }
        )

    # Get subject from first message
    subject = messages[0]["subject"]

    # Combine all messages into a single thread body
    # Stop if the thread is too long
    thread_body = f"Subject: {subject}\n\n---\n\n"
    thread_token_count = 0
    for message in messages:
        message_body = clean_text_whitespace(message["body"])
        message_token_count = num_tokens_from_string(message_body)
        if thread_token_count + message_token_count > thread_token_max:
            break
        thread_body += f"Sender: {message['sender_name']} <{message['sender_email']}>\n\nMessage:{message_body}\n\n---\n\n"
        thread_token_count += message_token_count

    return {
        "thread_id": thread_id,
        "subject": subject,
        "thread_body": thread_body,
        "date": messages[0]["date"].isoformat(),
        "duration": (messages[-1]["date"] - messages[0]["date"]).days,
        "length": len(messages),
        "messages": messages,
        "url": messages[0]["url"],
    }
