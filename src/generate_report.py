import json
import re
from functools import partial
from typing import Callable, List

from pandas import DataFrame
from tqdm import tqdm

from client_openai import TokenLimitExceededError
from file_operations import (
    delete_excel_file,
    ensure_excel_file,
    ensure_full_path,
    extract_from_excel,
    load_excel_file,
    save_as_text_file,
    update_excel_file,
)
from get_report_stats import get_report_stats
from gmail_download import get_thread_from_gmail
from num_tokens_from_string import num_tokens_from_string


def summarize_text_and_extract_data(
    text: str, summary_api: Callable, data_api: Callable
) -> dict:
    """
    Summarizes the input text and extracts data from the generated summary using the provided API functions.

    Args:
        text (str): The input text to be summarized and from which data needs to be extracted.
        summary_prompt (str): The prompt to be used for generating the summary.
        data_prompt (str): The prompt to be used for extracting data from the summary.
        summary_api (Callable): A function that takes a summary prompt and content as inputs and returns the generated summary, cost, input tokens, and output tokens.
        data_api (Callable): A function that takes a data prompt, content, and json_output flag as inputs and returns the extracted data, cost, input tokens, and output tokens.

    Returns:
        dict: The extracted data from the generated summary, total cost, total tokens, and the generated summary.
    """
    try:
        # Generate summary
        summary, summary_cost, summary_input_tokens, summary_output_tokens = (
            summary_api(
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": text}],
                    }
                ],
            )
        )

        # Extract data from summary
        data_text, data_cost, data_input_tokens, data_output_tokens = data_api(
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": summary}],
                },
            ],
            json_output=True,
        )

        # Parse extracted data
        try:
            data = json.loads(data_text)
            if not isinstance(data, dict):
                raise TypeError("Parsed JSON is not a dictionary")
        except (json.JSONDecodeError, TypeError) as e:
            print(
                f"Failed to parse extracted data for {text[:25]}: {data_text}. Error: {e}"
            )
            return {}

        # Calculate total cost and total tokens
        total_cost = summary_cost + data_cost
        total_tokens = (
            summary_input_tokens
            + summary_output_tokens
            + data_input_tokens
            + data_output_tokens
        )

        # Return extracted data, total cost, total tokens, and generated summary
        return {
            **data,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "summary": summary,
        }

    except TokenLimitExceededError as e:
        print(f"Token limit error: {e}")
        return {}


def to_kebab_case(text: str):
    """
    Converts a given text to kebab case.

    Args:
        text (str): The text to be converted to kebab case.

    Returns:
        str: The text converted to kebab case.

    Example:
        >>> to_kebab_case("Hello World")
        'hello-world'
        >>> to_kebab_case("Python3 is Awesome!")
        'python3-is-awesome'
    """
    # Insert a hyphen before uppercase letters and convert them to lowercase
    text = re.sub(r"(?<=[a-z])([A-Z])", r"-\1", text)
    # Replace non-alphanumeric characters (excluding letters and digits) with hyphens
    text = re.sub(r"[^a-zA-Z\d]+", "-", text)
    # Remove hyphens from front and back
    text = re.sub(r"(^-+)|(-+$)", "", text)
    return text.lower()


def expand_api_mentions(thread: dict) -> list:
    """
    Expand the list of API mentions in the thread by creating a new dictionary for each API mention
    with additional information such as the date and thread ID.

    Args:
        thread (dict): A dictionary representing a thread with the following keys:
            - 'api_mentions' (list): A list of API mentions in the thread.
            - 'date' (str): The date of the thread.
            - 'thread_id' (str): The ID of the thread.

    Returns:
        list: A list of dictionaries, where each dictionary represents an expanded API mention in the thread.
        Each dictionary has the following keys:
            - 'api' (str): The API mention.
            - 'date' (str): The date of the thread.
            - 'thread_id' (str): The ID of the thread.
    """
    api_mentions = []
    for api in thread["api_mentions"]:
        api_mentions.append(
            {
                "api": to_kebab_case(api),
                "date": thread["date"],
                "thread_id": thread["thread_id"],
            }
        )

    return api_mentions


def standardize_field_values(
    df: DataFrame,
    df_field: str,
    processor: Callable[[str], dict],
    label: str = "Processing...",
    max_batch_tokens: int = 1000,
):
    """
    Standardizes a table of tags using a processor function. The processor takes a string of tags and returns a map of
    the tags to their standardized versions.
    """
    # Deduplicate API tags into a map to use to replace API mentions
    tag_map: dict[str, str] = {api: api for api in df[df_field]}
    # Concatenate API tags into batches
    batches = [""]  # Start with a single empty batch
    for tag in tag_map.values():
        next_tag = f"{tag}\n"
        # Start a new batch if the current batch is too long
        if num_tokens_from_string(batches[-1] + next_tag) >= max_batch_tokens:
            batches.append("")
        # Add the next API tag to the current batch
        batches[-1] += next_tag
    # Process API tags in batches
    for batch in tqdm(batches, label):
        # Map updated API tags to original API tags
        tag_map.update(processor(batch))
    # Update API mentions with standardized tags
    df.loc[:, df_field] = df[df_field].apply(lambda x: tag_map.get(x, x))
    return df


def generate_markdown_report(
    threads: List[dict],
    report_api: Callable,
    data_api: Callable,
) -> dict:
    """
    Generates a markdown report by summarizing and extracting data from a list of threads.

    Args:
        threads (List[dict]): A list of dictionaries representing the threads to be included in the report.
        report_prompt (str): The prompt to be used for generating the report.
        data_prompt (str): The prompt to be used for extracting data from the report.
        report_api (callable): A function that takes a report prompt and content as inputs and returns the generated report.
        data_api (callable): A function that takes a data prompt, content, and json_output flag as inputs and returns the extracted data.

    Returns:
        dict: A dictionary containing the extracted data from the report.

    """
    context = "Developer Community Threads\n\n---\n\n"
    for thread in threads:
        next_thread = ""
        next_thread += f"Subject: {thread['subject']}\n"
        next_thread += f"URL: {thread['url']}\n"
        next_thread += f"Date: {thread['date']}\n"
        next_thread += f"Resolved: {thread['resolved']}\n"
        next_thread += f"Sentiment: {thread['sentiment']}\n"
        next_thread += f"Summary: {thread['summary']}\n"
        next_thread += f"---\n\n"
        if num_tokens_from_string(context + next_thread) > 1e5:
            break
        context += next_thread
    data = summarize_text_and_extract_data(
        text=context,
        summary_api=report_api,
        data_api=data_api,
    )
    return data


def generate_report(
    thread_ids: List[str],
    thread_summary_model: Callable,
    thread_extract_model: Callable,
    message_summary_model: Callable,
    message_extract_model: Callable,
    report_summary_model: Callable,
    report_extract_model: Callable,
    api_summary_model: Callable,
    api_extract_model: Callable,
    max_thread_token_count: int,
    max_message_token_count: int,
    excel_file: str,
    markdown_file: str,
    dre_names: List[str],
    reuse_excel_file: bool = True,
):
    """
    Generate a report based on a list of thread IDs.

    Args:
        thread_ids: A list of thread IDs to process.
        thread_summary_prompt: The prompt to summarize the thread.
        thread_data_prompt: The prompt to extract data from the thread.
        message_summary_prompt: The prompt to summarize a message.
        message_data_prompt: The prompt to extract data from a message.
        report_summary_prompt: The prompt to summarize the report.
        report_data_prompt: The prompt to extract data from the report.
        max_thread_token_count: The maximum number of tokens allowed for a thread.
        max_message_token_count: The maximum number of tokens allowed for a message.
        excel_file: The name of the Excel file to save the data.
        markdown_file: The name of the Markdown file to save the report.
        dre_names: A list of DRE names.
        big_model_api: The model to use for harder tasks.
        small_model_api: The model to use for simple tasks.
        data_extract_api: The model to use for data extraction.
        reuse_excel_file: Whether to reuse data from the existing Excel file.
    """
    if not reuse_excel_file:
        delete_excel_file(excel_file)

    ensure_excel_file(excel_file, {"threads", "messages", "tokens"})

    threads = []
    for thread_id in tqdm(thread_ids, "Processing threads"):
        if reuse_excel_file:
            existing = extract_from_excel(
                properties={"thread_id": thread_id},
                excel_file_name=excel_file,
                sheet_name="threads",
            )
            if len(existing) > 0:
                thread = existing[0]
                thread["total_tokens"] = 0
                thread["total_cost"] = 0
                threads.append(thread)
                continue

        gmail_data = get_thread_from_gmail(
            thread_id=thread_id,
            message_token_max=max_thread_token_count,
            thread_token_max=max_message_token_count,
        )

        # Save thread body to text file
        save_as_text_file(
            text=gmail_data["thread_body"], file_name=f"data/threads/{thread_id}.txt"
        )

        thread_summary_data = summarize_text_and_extract_data(
            text=gmail_data["thread_body"],
            summary_api=thread_summary_model,
            data_api=thread_extract_model,
        )

        thread_data = {
            **thread_summary_data,
            "thread_id": gmail_data["thread_id"],
            "date": gmail_data["date"],
            "duration": gmail_data["duration"],
            "length": gmail_data["length"],
            "subject": gmail_data["subject"],
            "url": gmail_data["url"],
        }

        update_excel_file(
            file_name=excel_file,
            data=thread_data,
            sheet_name="threads",
            exclude_properties={"messages", "body", "total_cost", "total_tokens"},
        )

        # Save messages to Excel
        thread_messages: List[dict] = []
        for message in tqdm(
            gmail_data["messages"], f"Processing messages for {thread_id}"
        ):
            message_summary_data = summarize_text_and_extract_data(
                text=message["body"],
                summary_api=message_summary_model,
                data_api=message_extract_model,
            )

            message_data = {
                **message,
                **message_summary_data,
                "thread_index": len(thread_messages),
                "date": message["date"].isoformat(),
                "sender_is_dre": any(
                    dre_name in message["sender_name"] for dre_name in dre_names
                ),
                "category": thread_data["category"],
                "resolved_thread": thread_data["resolved"],
            }

            # Save messages to Excel
            update_excel_file(
                file_name=excel_file,
                data=message_data,
                sheet_name="messages",
                exclude_properties={"total_cost", "total_tokens", "summary"},
            )

            thread_messages.append(message_data)

        # Save API mentions to Excel
        api_mentions = expand_api_mentions(thread_data)
        update_excel_file(
            file_name=excel_file,
            data=api_mentions,
            sheet_name="api_mentions",
        )

        threads.append({**thread_data, "messages": thread_messages})

    # Standardize API tags
    print()
    api_df = load_excel_file(excel_file, "api_mentions")
    api_df = standardize_field_values(
        df=api_df,
        df_field="api",
        processor=partial(
            summarize_text_and_extract_data,
            summary_api=api_summary_model,
            data_api=api_extract_model,
        ),
        label="Standardizing API tags...",
        max_batch_tokens=1000,
    )
    update_excel_file(
        file_name=excel_file,
        data=api_df.to_dict(orient="records"),  # type: ignore
        sheet_name="api_mentions",
        overwrite_sheet=True,
    )

    # Generate community report for email
    print("Generating community report...")
    markdown_report = generate_markdown_report(
        threads=threads,
        report_api=report_summary_model,
        data_api=report_extract_model,
    )
    save_as_text_file(
        file_name=markdown_file,
        text=markdown_report["summary"],
    )

    # Print operation stats
    stats = get_report_stats(threads, markdown_report)
    update_excel_file(
        file_name=excel_file,
        data=stats,
        sheet_name="tokens",
    )

    print(f"Excel file: {ensure_full_path(excel_file)}")
    print(f"Report: {ensure_full_path(markdown_file)}")
    print(f"Analysis complete.")
