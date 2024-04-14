import pandas as pd

from posts__claude_util_client import models
from posts__claude_util_run_categorization import run_categorization
from posts__util_fnum import fnum
from posts__util_root_dir import root_dir

INPUT_FILE_NAME = f"{root_dir}/data/raw/jan_2022_dec_2023_gpt-4_sentiment.xlsx"

MODEL_NAME = "claude-3-haiku-20240307"
# MODEL_NAME = "claude-3-sonnet-20240229"
input_token_cost, output_token_cost = models[MODEL_NAME].values()

TEMPERATURE = 0

SYSTEM_PROMPT = """
Your task is to classify developer community messages as one of the following categories:
- Development: Chrome Extension development, web technologies, JavaScript, APIs, authentication, and general software development issues.
- Publishing: the Chrome Extension publishing process, the Chrome Web Store, reviews, approvals, rejections, or violations, and general post-development issues.
- OffTopic: Chrome Extension end user issues or anything unrelated to Chrome Extensions.

Let's think step by step and state your reasoning in a concise manner.
Respond with a JSON object like {"reasoning": "I think this is Development because...", "category": "Development"}

Classify the following message into one of [Development,Publishing,OffTopic]. 
First look at the Title text, and if you're unsure, use the Body text.
If there is any ambiguity, always prefer Publishing over Development, and Development over OffTopic.
"""


def main():
    # Read the Excel file
    df = pd.read_excel(INPUT_FILE_NAME)

    # Print the details of the analysis
    print(f"Model: {MODEL_NAME}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Messages: {len(df)}")
    print(f"Threads: {df['threadId'].nunique()}")
    print(f"Characters: {df['body'].str.len().sum()}")
    print(f"Input cost per token: ${fnum(input_token_cost)}")
    print(f"Output cost per token: ${fnum(output_token_cost)}")

    # Run the sentiment analysis and store the results in the DataFrame without modifying the original DataFrame
    result, input_tokens, output_tokens, total_cost = run_categorization(
        MODEL_NAME, input_token_cost, output_token_cost, TEMPERATURE, SYSTEM_PROMPT, df
    )

    # Print the results of the analysis
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Total cost: ${fnum(total_cost)}")

    # Calculate the number of messages categorized as Development, Publishing, and OffTopic
    category_counts = (
        result["category"]
        .value_counts()
        .reindex(["Development", "Publishing", "OffTopic"], fill_value=0)
    )
    print(f"Development: {category_counts['Development']}")
    print(f"Publishing: {category_counts['Publishing']}")
    print(f"OffTopic: {category_counts['OffTopic']}")

    # Write the DataFrame back to a new Excel file
    output_id = hash((MODEL_NAME, TEMPERATURE, SYSTEM_PROMPT, INPUT_FILE_NAME, len(df)))
    file_name = f"{INPUT_FILE_NAME.replace('data/raw', 'data/processed').replace('.xlsx', '')}_{MODEL_NAME}-t{TEMPERATURE}-{output_id}.xlsx"
    print(f"Writing file: {file_name}")
    result.to_excel(file_name, index=False)
    print(f"Analysis complete.")


if __name__ == "__main__":
    main()
