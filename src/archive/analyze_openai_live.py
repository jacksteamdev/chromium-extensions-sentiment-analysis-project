import pandas as pd
import random
import string
from tqdm import tqdm
from SETTINGS import MODEL_NAME, TEMPERATURE

import json
import backoff

from openai import RateLimitError

from SETTINGS import MODEL_NAME, SYSTEM_PROMPT_MICRO, TEMPERATURE
from openai_util_embeddings import cosine_similarity, get_embedding
from openai_util_client import client


@backoff.on_exception(backoff.expo, RateLimitError)
def completions_with_backoff(**kwargs):
    response = client.chat.completions.create(**kwargs)
    return response


def analyze_sentiment(examples, body):
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_MICRO},
            *examples,
            {"role": "user", "content": body},
        ]

        response = completions_with_backoff(
            model=MODEL_NAME,
            messages=messages,
            # either temperature or top_p can be used, but not both
            temperature=TEMPERATURE,
            # top_p=1.0,
            # seed=42,  # makes the response deterministic
            response_format={"type": "json_object"},
        )

        # Extract the message content from the response
        response_text = response.choices[0].message.content

        # Parsing the sentiment and confidence from the response
        response_data = (
            {"sentiment": "none", "confidence": 0.0, "reasoning": "none"}
            if response_text is None
            else json.loads(response_text)
        )
        sentiment = str(response_data["sentiment"])
        confidence = float(response_data["confidence"])
        reasoning = str(response_data["reasoning"])

        usage = response.usage if response.usage else None
        tokens = usage.total_tokens if usage else 0
    except Exception as error:
        print(f"Failed to analyze sentiment: {error}")
        return "none", 0.0, 0, str(error)
    return sentiment, confidence, tokens, reasoning


# Create a function to process each row
def process_row(examples, data, index):
    try:
        row = data.loc[index]
        body = row["body"]

        sentiment, confidence, tokens, reasoning = analyze_sentiment(examples, body)

        # Update the row in the DataFrame
        data.at[index, "sentiment"] = sentiment
        data.at[index, "confidence"] = confidence
        data.at[index, "tokens"] = tokens
        data.at[index, "reasoning"] = reasoning

        return True, reasoning
    except Exception as error:
        return False, str(error)


def main():
    unique_id = "2024-01"

    # Read the data for analysis Excel file
    data = pd.read_excel(f"data/processed/{unique_id}_gmail_messages.xlsx")
    data["sentiment"] = None
    data["confidence"] = None
    data["tokens"] = None
    data["reasoning"] = None

    # Read the training data Excel file
    training = pd.read_excel(f"data/processed/{unique_id}_training_data.xlsx").head(40)

    # Transform the training DataFrame into a list of messages, one user and one assistant for each row:
    examples = []
    for index, row in training.iterrows():
        examples.append({"content": row["body"], "role": "user"})
        examples.append({"content": row["expected"], "role": "assistant"})
    print(f"Examples: {(examples)}")

    # Iterate over the testing DataFrame with a progress bar
    for index, row in tqdm(
        data.iterrows(), total=len(data), desc="Analyzing sentiment"
    ):
        success, reasoning = process_row(examples, data, index)
        if not success:
            print(f"Failed to process row {index}, {reasoning}")
            break

    print(f"Temperature: {TEMPERATURE}")
    print(f"Total tokens used: {data.tokens.sum()}")

    # Write the DataFrame back to a new Excel file
    file_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    data.to_excel(
        f"data/processed/{unique_id}_test_result_{file_id}_{len(data)}_{MODEL_NAME}_{TEMPERATURE}.xlsx",
        index=False,
    )


if __name__ == "__main__":
    main()
