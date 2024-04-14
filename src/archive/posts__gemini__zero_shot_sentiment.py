import json
import pandas as pd
import random
import string
from tqdm import tqdm
import google.generativeai as genai
from google.colab import userdata

# Configure the Gemini AI API
GOOGLE_API_KEY = userdata.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
MODEL = "gemini-1.0-pro"
model = genai.GenerativeModel(MODEL)
TEMPERATURE = 0.25

SYSTEM_PROMPT = """
Your task is to perform a sentiment analysis (Positive, Neutral, or Negative) and include the numerical confidence score.
The content is a post from a developer forum for Chrome extensions.

Your response is a JSON with the following structure:
{
  "sentiment": "<sentiment>",
  "confidence": <confidence score>
}

If you are not sure of the sentiment, return a JSON with the following structure:
{
  "sentiment": "None",
  "confidence": 0.0
}

Sentiment Analysis Guidelines:
- If the sentiment is unclear or cannot be determined, the sentiment is None.
- If the developer explains a problem in a factual manner, the sentiment is Neutral.
- If the developer expresses gratitude, the sentiment is Positive.
- If the developer expresses appreciation, the sentiment is Positive.
- If the developer expresses satisfaction, the sentiment is Positive.
- If the developer expresses dissatisfaction, the sentiment is Negative.
- If the developer expresses frustration, the sentiment is Negative.
- If the developer expresses disappointment, the sentiment is Negative.

What is the sentiment analysis of the following sentence?
"""


def analyze_sentiment(body):
    try:
        result = model.generate_content(
            SYSTEM_PROMPT + body,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=100, temperature=TEMPERATURE
            ),
        )

        response_text = result.candidates[0].content.parts[0].text
        response_data = (
            json.loads(response_text)
            if response_text
            else {"sentiment": "None", "confidence": 0.0}
        )

        sentiment = response_data["sentiment"]
        confidence = response_data["confidence"]
        print(sentiment, confidence)
        return sentiment, confidence
    except Exception as error:
        print(f"Failed to analyze sentiment: {error}")
        return "None", 0.0


def process_row(row, index, df):
    body = row["body"]
    manual = row["Amy's Manual analysis"]
    sentiment, confidence = analyze_sentiment(body)

    df.at[index, "Sentiment"] = sentiment
    df.at[index, "Confidence Score"] = confidence
    df.at[index, "Match?"] = "TRUE" if sentiment.lower() == manual.lower() else "FALSE"


# Load and process the data
df = pd.read_excel("/content/107_clean_with_manual_review.xlsx")

for i, row in tqdm(df.iterrows(), total=len(df)):
    process_row(row, i, df)

# Calculate and display the accuracy
matches = df["Match?"]
true_count = matches.str.count("TRUE").sum()
true_percent = (true_count / len(df)) * 100
print(f"Accuracy: {int(true_percent)}%")
print(f"Temperature: {TEMPERATURE}")

# Save the results to a new Excel file
file_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
df.to_excel(f"/content/107_gemini_analysis_{TEMPERATURE}_{file_id}.xlsx", index=False)
