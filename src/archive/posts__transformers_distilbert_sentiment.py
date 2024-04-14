import pandas as pd
from transformers.pipelines import pipeline

from posts__util_root_dir import root_dir

# Load Excel file
file_path = f"{root_dir}/data/raw/gmail_messages.xlsx"
text_column = "body"
df = pd.read_excel(file_path)

# Initialize sentiment analysis pipeline
sentiment_pipeline = pipeline(
    "text-classification",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)


# Define a function to get sentiment and confidence score
def get_sentiment(text):
    max_length = 512  # DistilBERT's max token limit
    truncated_text = " ".join(text.split()[:max_length])

    result = list(sentiment_pipeline(truncated_text))[0]
    return result["label"], result["score"]


# Apply sentiment analysis
df[["Sentiment", "Confidence"]] = df[text_column].apply(
    lambda x: pd.Series(get_sentiment(x))
)

# Save the updated DataFrame back to an Excel file
output_file_path = "DistilBERT_analysis.xlsx"  # Choose your output file name
df.to_excel(output_file_path, index=False)

print("Sentiment analysis completed and results added to:", output_file_path)
