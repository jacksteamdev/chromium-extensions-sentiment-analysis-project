from typing import Callable, List, Optional, Union
from httpx import get
from pandas import Series
from tqdm import tqdm
import pandas as pd

from posts__claude_util_call_claude_api import init_call_claude_api


def analyze_topics(
    model_name,
    input_token_cost,
    output_token_cost,
    temperature,
    _df: pd.DataFrame,
    get_system_prompt: Callable[[pd.DataFrame], str],
    parse_response: Callable[[str], List],
    get_messages: Optional[Callable[[Series], List]] = None,
):
    """Use an Anthropic model to analyze topics in a DataFrame of messages."""

    def calculate_cost(input_tokens, output_tokens):
        return input_token_cost * input_tokens + output_token_cost * output_tokens

    # Create a new DataFrame with only the rows that have the same "id" as "threadId"
    df = _df[_df["id"] == _df["threadId"]].copy()

    # Add new columns to the DataFrame
    df["input_tokens"] = None
    df["output_tokens"] = None
    df["topics"] = [[] for _ in range(len(df))]

    # Analyze sentiment for each row in the "body" column and store the results
    tqdm.pandas(desc="Processing thread topics...")
    # concatenate the title and body to form the input
    df["analysis_result"] = df.progress_apply(
        init_call_claude_api(
            model_name,
            get_system_prompt,
            temperature,
            df,
            parse_response,
            get_messages=get_messages,
        ),
        axis=1,
    )  # type: ignore

    # Now, expand the analysis_result into separate columns
    df[["topics", "input_tokens", "output_tokens"]] = pd.DataFrame(
        df["analysis_result"].tolist(), index=df.index
    )

    # Drop the 'analysis_result' column since it's no longer needed
    df.drop("analysis_result", axis=1, inplace=True)

    # Calculate the total cost
    input_tokens = df["input_tokens"].sum()
    output_tokens = df["output_tokens"].sum()
    total_cost = calculate_cost(input_tokens, output_tokens)

    # Merge df with result on 'threadId', applying the 'category' from result to df
    # Since 'threadId' in df matches 'threadId' in df for the original thread messages
    df = _df.merge(df[["threadId", "topics"]], on="threadId", how="left")

    return df, input_tokens, output_tokens, total_cost
