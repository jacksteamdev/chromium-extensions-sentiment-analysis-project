from typing import List
from httpx import get
import pandas as pd
from pandas import Series

from posts__claude_util_client import models
from posts__claude_util_analyze_topics import analyze_topics
from posts__util_fnum import fnum
from posts__util_root_dir import root_dir

INPUT_FILE_NAME = f"{root_dir}/data/raw/jan_2022_dec_2023_gpt-4_sentiment_claude-3-haiku_categorization.xlsx"

MODEL_NAME = "claude-3-haiku-20240307"
# MODEL_NAME = "claude-3-sonnet-20240229"
input_token_cost, output_token_cost = models[MODEL_NAME].values()

TEMPERATURE = 0.2


def get_system_prompt(df: pd.DataFrame) -> str:
    # Explode the "topics" column to count each topic individually
    exploded_topics = df.explode("topics")

    # Count the occurrences of each topic
    topic_counts = exploded_topics["topics"].value_counts().reset_index()
    topic_counts.columns = ["topic", "count"]

    return f"""
You are a Google Chrome Extensions Developer Advocate who is looking for insight into the developer community. 
You will receive a forum thread comprised of a title and body. 
Your task is to identify the sub-categories in the thread related to the main category.
Sub-categories are kebab-case strings, but you may assign any sub-category.
Sub-categories should be insightful and relevant to the main category.
Sub-categories should not be obvious, like "chrome-extension", "chrome-extensions", "chrome-web-store" or "google".
Use these sub-categories if appropriate: {','.join(topic_counts['topic'].unique())}
Feel free to add new categories if none of the existing ones are appropriate.
Your response should be a raw comma-separated list starting with the category and continuing with sub-categories.
""".strip()


def get_messages(row: Series) -> List:
    title = row["title"]
    body = row["body"]
    category = row["category"]
    return [
        {
            "role": "user",
            "content": [{"type": "text", "text": f"Title:{title}\nBody:\n{body}"}],
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": f"{category.lower()},"}],
        },
    ]


def parse_response(response: str) -> List[str]:
    return response.split(",")


def main():
    # Read the Excel file
    df = pd.read_excel(INPUT_FILE_NAME).tail(100)

    # Print the details of the analysis
    print(f"Model: {MODEL_NAME}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Messages: {len(df)}")
    print(f"Threads: {df['threadId'].nunique()}")
    print(f"Characters: {df['body'].str.len().sum()}")
    print(f"Input cost per token: ${fnum(input_token_cost)}")
    print(f"Output cost per token: ${fnum(output_token_cost)}")

    # Run the sentiment analysis and store the results in the DataFrame without modifying the original DataFrame
    result, input_tokens, output_tokens, total_cost = analyze_topics(
        MODEL_NAME,
        input_token_cost,
        output_token_cost,
        TEMPERATURE,
        df,
        get_system_prompt,
        parse_response=parse_response,
        get_messages=get_messages,
    )

    # Print the results of the analysis
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Total cost: ${fnum(total_cost)}")

    print(f"Columns: {result.columns}")

    # Aggregate the full list of topics
    topics = result["topics"].explode().value_counts().reset_index()
    topics.columns = ["topic", "count"]
    print(f"Topics: {topics}")
    print(f"Total topics: {len(topics)}")

    result["topics"] = result["topics"].apply(
        lambda x: ",".join(x) if isinstance(x, list) else x
    )

    # Write the DataFrame back to a new Excel file
    output_id = hash(
        (MODEL_NAME, TEMPERATURE, get_system_prompt(result), INPUT_FILE_NAME, len(df))
    )
    file_name = f"{INPUT_FILE_NAME.replace('data/raw', 'data/processed').replace('.xlsx', '')}_{MODEL_NAME}-t{TEMPERATURE}-{output_id}.xlsx"

    print(f"Writing file: {file_name}")
    with pd.ExcelWriter(file_name) as writer:
        result.to_excel(writer, sheet_name="result")
        topics.to_excel(writer, sheet_name="topics")
    print(f"Analysis complete.")


if __name__ == "__main__":
    main()
