import functools
from pdb import run
import pandas as pd
import random
import string

from pandas import DataFrame
from tqdm import tqdm

from SETTINGS import MODEL_NAME, TEMPERATURE
from openai_util_analyze_sentiment import process_row

NUM_EXAMPLES = 41
TESTING_PERCENTAGE = 0.3


def get_examples(df: DataFrame, body: str):
    """Transform the training DataFrame into a list of messages, one user and one assistant for each row."""

    examples = []
    for index, row in df.head(NUM_EXAMPLES).sort_index().iterrows():
        examples.append({"content": row["body"], "role": "user"})
        examples.append({"content": row["expected"], "role": "assistant"})
    return examples


def main():
    unique_id = "2024-01"

    # Read the Excel file
    df = pd.read_excel(f"data/processed/{unique_id}_training_data.xlsx")
    df["correct"] = None
    df["sentiment"] = None
    df["confidence"] = None
    df["tokens"] = None
    df["reasoning"] = None

    # Split the DataFrame into training and testing sets
    range = int(len(df) * TESTING_PERCENTAGE)
    testing, training = df[:range].copy(), df[range:].copy()
    print(f"Training set: {len(training)}")
    print(f"Testing set: {len(testing)}")

    get_training_examples = functools.partial(get_examples, df=training)
    run_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))

    # Iterate over the testing DataFrame with a progress bar
    for index, row in tqdm(
        testing.iterrows(), total=len(testing), desc="Analyzing sentiment"
    ):
        success, reasoning = process_row(get_training_examples, testing, index, run_id)
        if not success:
            print(f"Failed to process row {index}, {reasoning}")
            break

    # Calculate the percentage of matches == TRUE
    matches = testing["correct"]
    total = len(matches)
    true_count = matches.str.count("TRUE").sum()
    true_percent = (true_count / total) * 100
    total_tokens = testing["tokens"].sum()

    print(f"Accuracy: {int(true_percent)}%")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Total tokens used: {total_tokens}")

    # Write the DataFrame back to a new Excel file
    df.to_excel(
        f"data/processed/{unique_id}_test_result_{run_id}_{MODEL_NAME}_{TEMPERATURE}.xlsx",
        index=False,
    )


if __name__ == "__main__":
    main()
