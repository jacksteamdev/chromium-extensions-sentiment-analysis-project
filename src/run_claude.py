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
from client_claude import call_claude_api
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
    THREAD_SUMMARY_PROMPT,
)

# Include customized prompts here


if __name__ == "__main__":

    thread_ids = thread_ids if thread_ids else query_gmail_for_thread_ids(gmail_query)
    if max_thread_count:
        thread_ids = thread_ids[:max_thread_count]

    generate_report(
        # Use provided thread ids otherwise query gmail
        thread_ids=thread_ids,
        # Partially apply model config here for easy customization
        thread_summary_model=partial(
            call_claude_api,
            system_prompt=THREAD_SUMMARY_PROMPT,
            model_name="claude-3-haiku-20240307",
            max_tokens=1000,
        ),
        thread_extract_model=partial(
            call_claude_api,
            system_prompt=THREAD_DATA_PROMPT,
            model_name="claude-3-haiku-20240307",
        ),
        message_summary_model=partial(
            call_claude_api,
            system_prompt=MESSAGE_SUMMARY_PROMPT,
            model_name="claude-3-sonnet-20240229",
        ),
        message_extract_model=partial(
            call_claude_api,
            system_prompt=MESSAGE_DATA_PROMPT,
            model_name="claude-3-haiku-20240307",
        ),
        report_summary_model=partial(
            call_claude_api,
            system_prompt=REPORT_SUMMARY_PROMPT,
            model_name="claude-3-sonnet-20240229",
            max_tokens=2000,
        ),
        report_extract_model=partial(
            call_claude_api,
            system_prompt=REPORT_DATA_PROMPT,
            model_name="claude-3-haiku-20240307",
            max_tokens=2000,
        ),
        api_summary_model=partial(
            call_claude_api,
            system_prompt=API_SUMMARY_PROMPT,
            model_name="claude-3-haiku-20240307",
            max_tokens=2000,
        ),
        api_extract_model=partial(
            call_claude_api,
            system_prompt=API_DATA_PROMPT,
            model_name="claude-3-haiku-20240307",
            max_tokens=2000,
        ),
        # General config
        max_thread_token_count=max_thread_token_count,
        max_message_token_count=max_message_token_count,
        excel_file=excel_file,
        markdown_file=report_file,
        dre_names=dre_names,
        reuse_excel_file=resume,
    )
