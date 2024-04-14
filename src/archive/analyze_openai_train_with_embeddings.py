import functools
import json
from re import T
import pandas as pd
import random
import string

from pandas import DataFrame
from tqdm import tqdm

from SETTINGS import MODEL_NAME, TEMPERATURE
from openai_util_analyze_sentiment import process_row
from openai_util_embeddings import cosine_similarity, get_embedding

NUM_EXAMPLES = 30
TESTING_PERCENTAGE = 0.3


def get_examples(df: DataFrame, body: str):
    """
    Calculate the similarity between the body and the training data using the embeddings.
    Use the most similar examples to create a list of messages for the OpenAI API.
    """

    embedding = get_embedding(body)
    df["similarity"] = df.embeddings.apply(lambda x: cosine_similarity(x, embedding))

    examples = []
    for index, row in (
        df.sort_values("similarity", ascending=False)
        .head(NUM_EXAMPLES)
        .sort_index()
        .iterrows()
    ):
        examples.append({"content": row["body"], "role": "user"})
        examples.append(
            {
                "content": json.dumps(
                    {
                        "reasoning": row["reasoning"],
                        "sentiment": row["expected"],
                        # Get random confidence value between 0.5 and 1.0
                        "confidence": random.uniform(0.5, 1.0),
                    }
                ),
                "role": "assistant",
            }
        )
    return examples


def main():
    unique_id = "2024-01_large"

    # Read the Excel file
    df = pd.read_excel(f"data/processed/{unique_id}_training.xlsx")
    df["correct"] = None
    df["sentiment"] = None
    df["confidence"] = None
    df["tokens"] = None

    # Load the embeddings from the JSON file
    df["embeddings"] = None
    embeddings = json.load(open(f"{unique_id}_embeddings.json", "r"))
    for index, row in df.iterrows():
        id = str(row["id"])
        value = embeddings.get(id, None)

        # fail if the embedding is not found
        if value is None:
            print(f"Failed to find embedding for row {id}")
            return

        df.at[index, "embeddings"] = value

    # Split the DataFrame into training and testing sets
    range = int(len(df) * TESTING_PERCENTAGE)
    # Randomize the DataFrame
    df = df.sample(frac=1)
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
    testing.to_excel(
        f"data/processed/{unique_id}_test_result_{run_id}_{MODEL_NAME}_{TEMPERATURE}.xlsx",
        index=False,
    )


if __name__ == "__main__":
    main()
