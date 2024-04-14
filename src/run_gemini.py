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
from client_gemini import call_gemini_api
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
            call_gemini_api,
            system_prompt=THREAD_SUMMARY_PROMPT,
            model_name="gemini-1.5-pro",
        ),
        thread_extract_model=partial(
            call_gemini_api,
            system_prompt=THREAD_DATA_PROMPT,
            model_name="gemini-1.0-pro",
        ),
        message_summary_model=partial(
            call_gemini_api,
            system_prompt=MESSAGE_SUMMARY_PROMPT,
            model_name="gemini-1.5-pro",
        ),
        message_extract_model=partial(
            call_gemini_api,
            system_prompt=MESSAGE_DATA_PROMPT,
            model_name="gemini-1.0-pro",
        ),
        report_summary_model=partial(
            call_gemini_api,
            system_prompt=REPORT_SUMMARY_PROMPT,
            model_name="gemini-1.5-pro",
        ),
        report_extract_model=partial(
            call_gemini_api,
            system_prompt=REPORT_DATA_PROMPT,
            model_name="gemini-1.0-pro",
        ),
        api_summary_model=partial(
            call_gemini_api,
            system_prompt=API_SUMMARY_PROMPT,
            model_name="gemini-1.5-pro",
        ),
        api_extract_model=partial(
            call_gemini_api,
            system_prompt=API_DATA_PROMPT,
            model_name="gemini-1.0-pro",
        ),
        # General config
        max_thread_token_count=max_thread_token_count,
        max_message_token_count=max_message_token_count,
        excel_file=excel_file,
        markdown_file=report_file,
        dre_names=dre_names,
        reuse_excel_file=resume,
    )
