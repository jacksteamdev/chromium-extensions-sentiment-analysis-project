import pandas as pd
from tqdm import tqdm

from posts__openai_util_analyze_sentiment import init_analyze_sentiment


def run_sentiment_analysis(
    model_name,
    input_token_cost,
    output_token_cost,
    temperature,
    system_prompt,
    df: pd.DataFrame,
    generate_shots=None,
):
    """Use an OpenAI model to analyze sentiment in a DataFrame of messages."""

    def calculate_cost(input_tokens, output_tokens):
        return input_token_cost * input_tokens + output_token_cost * output_tokens

    # Add new columns to the DataFrame
    df["input_tokens"] = None
    df["output_tokens"] = None
    df["sentiment"] = None
    df["confidence"] = None

    # Analyze sentiment for each row in the "body" column and store the results
    tqdm.pandas(desc="Processing rows")
    df["analysis_result"] = df["body"].progress_apply(
        init_analyze_sentiment(model_name, system_prompt, temperature, generate_shots)
    )

    # Now, expand the analysis_result into separate columns
    df[["sentiment", "confidence", "input_tokens", "output_tokens"]] = pd.DataFrame(
        df["analysis_result"].tolist(), index=df.index
    )

    # Drop the 'analysis_result' column since it's no longer needed
    df.drop("analysis_result", axis=1, inplace=True)

    # Calculate the total cost
    input_tokens = df["input_tokens"].sum()
    output_tokens = df["output_tokens"].sum()
    total_cost = calculate_cost(input_tokens, output_tokens)

    return df, input_tokens, output_tokens, total_cost
