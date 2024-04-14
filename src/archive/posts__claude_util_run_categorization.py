from tqdm import tqdm
import pandas as pd

from posts__claude_util_categorize_message import init_categorize_message


def run_categorization(
    model_name,
    input_token_cost,
    output_token_cost,
    temperature,
    system_prompt,
    _df: pd.DataFrame,
    generate_shots=None,
):
    """Use an Anthropic model to analyze sentiment in a DataFrame of messages."""

    def calculate_cost(input_tokens, output_tokens):
        return input_token_cost * input_tokens + output_token_cost * output_tokens

    # Create a new DataFrame with only the rows that have the same "id" as "threadId"
    df = _df[_df["id"] == _df["threadId"]].copy()

    # Add new columns to the DataFrame
    df["input_tokens"] = None
    df["output_tokens"] = None
    df["category"] = None

    # Analyze sentiment for each row in the "body" column and store the results
    tqdm.pandas(desc="Processing rows")
    # concatenate the title and body to form the input
    df["analysis_input"] = "Title: " + df["title"] + "\n" + "Body:" + "\n" + df["body"]
    df["analysis_result"] = df["analysis_input"].progress_apply(
        init_categorize_message(model_name, system_prompt, temperature, generate_shots)
    )

    # Now, expand the analysis_result into separate columns
    df[["category", "reasoning", "input_tokens", "output_tokens"]] = pd.DataFrame(
        df["analysis_result"].tolist(), index=df.index
    )

    # Drop the 'analysis_result' column since it's no longer needed
    df.drop("analysis_input", axis=1, inplace=True)
    df.drop("analysis_result", axis=1, inplace=True)

    # Calculate the total cost
    input_tokens = df["input_tokens"].sum()
    output_tokens = df["output_tokens"].sum()
    total_cost = calculate_cost(input_tokens, output_tokens)

    # Merge df with result on 'threadId', applying the 'category' from result to df
    # Since 'threadId' in df matches 'threadId' in df for the original thread messages
    df = _df.merge(df[["threadId", "category"]], on="threadId", how="left")

    return df, input_tokens, output_tokens, total_cost
