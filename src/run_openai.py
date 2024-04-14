from functools import partial

from args import (
    dre_names,
    excel_file,
    gmail_query,
    max_message_token_count,
    max_thread_count,
    max_thread_token_count,
    report_file,
    resume,
    thread_ids,
)
from client_openai import call_openai_api
from generate_report import generate_report
from gmail_download import query_gmail_for_thread_ids
from prompts import (
    API_DATA_PROMPT,
    API_SUMMARY_PROMPT,
    MESSAGE_DATA_PROMPT,
    MESSAGE_SUMMARY_PROMPT,
    REPORT_DATA_PROMPT,
    REPORT_SUMMARY_PROMPT,
    THREAD_DATA_PROMPT,
)

# Include customized prompts here

# Use repetition to get the model to use chrome-web-store when possible
THREAD_SUMMARY_PROMPT = """
You will receive an email thread from the Chromium Extensions Google Group.
Summarize the thread to provide the following for a developer advocacy team:
- What was the thread about? Was the thread issue resolved?
- What was the average developer sentiment of the thread? Positive, Negative, Neutral
- Categorize the thread into one of the following categories:
    - If the thread mentions the Chrome Web Store in any way, the category is "chrome-web-store"
    - If the thread mentions the Chrome Web Store in any way, the category is "chrome-web-store"
    - If the thread mentions the Chrome Web Store in any way, the category is "chrome-web-store"
    - If the thread is not about Chrome Extensions, the category is "off-topic"
    - Else, the thread category is "development"
- If the category is "chrome-web-store", is a rejection ID mentioned? e.g., "Purple Titanium", "Gray Copper"
- If the category is "development", what web and chrome extension APIs are mentioned? e.g., chrome.storage.local, Navigator API, etc...
"""


def self_regulate(prompt):
    """Use self-regulation to improve the model's comprehension of the prompt"""
    return f"{prompt}\nStop and read the prompt again:\n{prompt}"


if __name__ == "__main__":

    thread_ids = thread_ids if thread_ids else query_gmail_for_thread_ids(gmail_query)
    if max_thread_count:
        thread_ids = thread_ids[:max_thread_count]

    generate_report(
        # Use provided thread ids otherwise query gmail
        thread_ids=thread_ids,
        # Partially apply model config here for easy customization
        thread_summary_model=partial(
            call_openai_api,
            system_prompt=THREAD_SUMMARY_PROMPT,
            model_name="gpt-3.5-turbo-0125",
        ),
        thread_extract_model=partial(
            call_openai_api,
            system_prompt=THREAD_DATA_PROMPT,
            model_name="gpt-3.5-turbo-0125",
        ),
        message_summary_model=partial(
            call_openai_api,
            system_prompt=MESSAGE_SUMMARY_PROMPT,
            model_name="gpt-4-turbo-preview",
        ),
        message_extract_model=partial(
            call_openai_api,
            system_prompt=MESSAGE_DATA_PROMPT,
            model_name="gpt-3.5-turbo-0125",
        ),
        report_summary_model=partial(
            call_openai_api,
            system_prompt=REPORT_SUMMARY_PROMPT,
            model_name="gpt-4-turbo-preview",
        ),
        report_extract_model=partial(
            call_openai_api,
            system_prompt=REPORT_DATA_PROMPT,
            model_name="gpt-3.5-turbo-0125",
        ),
        api_summary_model=partial(
            call_openai_api,
            system_prompt=API_SUMMARY_PROMPT,
            model_name="gpt-4-turbo-preview",
        ),
        api_extract_model=partial(
            call_openai_api,
            system_prompt=API_DATA_PROMPT,
            model_name="gpt-3.5-turbo-0125",
        ),
        # General config
        max_thread_token_count=max_thread_token_count,
        max_message_token_count=max_message_token_count,
        excel_file=excel_file,
        markdown_file=report_file,
        dre_names=dre_names,
        reuse_excel_file=resume,
    )
