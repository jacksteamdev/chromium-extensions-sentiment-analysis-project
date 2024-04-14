import math
import random
import string
import sys
import os

import pandas as pd

from posts__util_fnum import fnum
from posts__openai_util_client import models
from posts__openai_util_run_sentiment_analysis import run_sentiment_analysis
from posts__util_root_dir import root_dir

TESTING_FILE_NAME = "data/raw/2024-01_large_training.xlsx"
TRAINING_FILE_NAME = TESTING_FILE_NAME
TRAINING_RATIO = 0.5 # % of data to be used for training

MODEL_NAME = "gpt-3.5-turbo-0125"
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
    """Run the sentiment analysis with few-shot examples."""

    # Read the Excel file
    testing_file_name = f"{root_dir}/{TESTING_FILE_NAME}"
    df = pd.read_excel(testing_file_name).head(10)

    # Split the data into training and testing sets
    is_self_training = TRAINING_FILE_NAME == TESTING_FILE_NAME
    range = int(len(df) * TRAINING_RATIO)
    training = (
        df[:range].copy()
        if is_self_training
        else pd.read_excel(f"{root_dir}/{TRAINING_FILE_NAME}")
    )
    testing = df[range:].copy() if is_self_training else df
    print(f"Testing on {len(testing)} rows from {TESTING_FILE_NAME}")
    print(f"Training on {len(training)} rows from {TRAINING_FILE_NAME}")

    # Transform the training DataFrame into a list of examples, one user and one assistant for each row:
    messages = []
    for index, row in training.iterrows():
        messages.append({"content": row["body"], "role": "user"})
        messages.append({"content": row["expected"], "role": "assistant"})
    print(f"Examples: {(messages)}")

    # Print the details of the analysis
    print(f"Model: {MODEL_NAME}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Rows to analyze: {len(testing)}")
    print(f"Characters to analyze: {df['body'].str.len().sum()}")

    input_token_cost, output_token_cost = models[MODEL_NAME].values()
    print(f"Input cost per token: ${fnum(input_token_cost)}")
    print(f"Output cost per token: ${fnum(output_token_cost)}")

    # Run the sentiment analysis and store the results in the DataFrame
    results, input_tokens, output_tokens, total_cost = run_sentiment_analysis(
        MODEL_NAME,
        input_token_cost,
        output_token_cost,
        TEMPERATURE,
        SYSTEM_PROMPT,
        testing,
        # No-op function to always use the same few-shot examples
        generate_shots=lambda x: messages,
    )

    # Print the results of the analysis
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Total cost: ${fnum(total_cost)}")

    # Compare the results with the expected sentiment
    results["correct"] = results["sentiment"] == results["expected"]
    print(f"Correct: {results['correct'].sum()} out of {len(results)}")
    print(f"Accuracy: {results['correct'].mean():.0%}")

    # Calculate the F1 score by comparing the accuracy of each class of sentiment
    neg_mean = results[results["expected"] == "Negative"]["correct"].mean()
    neu_mean = results[results["expected"] == "Neutral"]["correct"].mean()
    pos_mean = results[results["expected"] == "Positive"]["correct"].mean()
    print(f"Negative mean: {neg_mean:.0%}")
    print(f"Neutral mean: {neu_mean:.0%}")
    print(f"Positive mean: {pos_mean:.0%}")

    scores = [neg_mean, neu_mean, pos_mean]
    harmonic_mean = sum(scores) / len(scores)
    print(f"Harmonic mean: {harmonic_mean:.0%}")

    # Write the DataFrame back to a new Excel file
    output_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    file_name = f"{testing_file_name.replace('data/raw', 'data/processed').replace('.xlsx', '')}_{MODEL_NAME}-t{TEMPERATURE}-{output_id}.xlsx"
    print(f"Writing file: {file_name}")
    results.to_excel(file_name, index=False)
    print(f"Analysis complete.")


if __name__ == "__main__":
    main()
