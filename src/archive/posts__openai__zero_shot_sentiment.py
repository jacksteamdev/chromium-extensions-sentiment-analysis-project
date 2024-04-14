import random
import string

import pandas as pd

from posts__util_fnum import fnum
from posts__openai_util_client import models
from posts__openai_util_run_sentiment_analysis import run_sentiment_analysis
from posts__util_root_dir import root_dir


INPUT_FILE_NAME = f"{root_dir}/data/processed/2024-01_gmail_messages.xlsx"

MODEL_NAME = "gpt-4-turbo-preview"
input_token_cost, output_token_cost = models[MODEL_NAME].values()

TEMPERATURE = 0

SYSTEM_PROMPT = """
You are a data analyst specializing in sentiment analysis for software developer communities. You will be provided a post from a developer forum. 

Perform a sentiment analysis (Positive, Neutral, or Negative) and include the numerical confidence score. 
Return the response in JSON with the following structure:
{
  "sentiment": "<sentiment>",
  "confidence": <confidence>
}

Evaluate sentence by sentence, and follow these guidelines
- If sentiment is unclear or mixed is it Neutral
- If the user is asking a question it is Neutral
- if the user shares information without emotion it is Neutral
- If the user is asking for help, without being rude it is Neutral
- If no emotion expressed is it Neutral
- If the user solves a problem it is Positive
- If a user provides a solution it is Positive
- If the user is friendly or encouraging it is Positive
- If the user was unable to solve their issue it is Negative
- If the user expresses frustration is it Negative
- If the user expresses confusion is it Negative
- If the user expresses disappointment it is Negative
"""


def main():
    # Read the Excel file
    df = pd.read_excel(INPUT_FILE_NAME).head(2)

    # Print the details of the analysis
    print(f"Model: {MODEL_NAME}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Rows to analyze: {len(df)}")
    print(f"Characters to analyze: {df['body'].str.len().sum()}")
    print(f"Input cost per token: ${fnum(input_token_cost)}")
    print(f"Output cost per token: ${fnum(output_token_cost)}")

    # Run the sentiment analysis and store the results in the DataFrame
    df, input_tokens, output_tokens, total_cost = run_sentiment_analysis(
        MODEL_NAME, input_token_cost, output_token_cost, TEMPERATURE, SYSTEM_PROMPT, df
    )

    # Print the results of the analysis
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Total cost: ${fnum(total_cost)}")

    # Write the DataFrame back to a new Excel file
    output_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    file_name = f"{INPUT_FILE_NAME.replace('.xlsx', '')}_{MODEL_NAME}-t{TEMPERATURE}-{output_id}.xlsx"
    print(f"Writing file: {file_name}")
    df.to_excel(file_name, index=False)
    print(f"Analysis complete.")


if __name__ == "__main__":
    main()
