from typing import Callable, List, Optional

from pandas import DataFrame, Series

from posts__claude_util_client import completions_with_backoff


def init_call_claude_api(
    model_name,
    get_system_prompt: Callable[[DataFrame], str],
    temperature,
    df: DataFrame,
    parse_response: Callable[[str], List],
    get_messages: Optional[Callable[[Series], List]] = None,
) -> Callable:
    """Initialize a function to analyze topics in a message using an Anthropic model."""

    def call_claude_api(row):
        """Use an Anthropic model to analyze the topics in a message."""
        response = None
        try:
            # Generate few-shot examples if a function is provided
            messages = get_messages(row) if get_messages else []
            system_prompt = get_system_prompt(df)

            response = completions_with_backoff(
                model=model_name,
                # system prompt type message isn't supported in the API
                system=system_prompt,
                messages=messages,
                max_tokens=512,  # maximum number of tokens in the response
                # either temperature or top_p can be used, but not both
                temperature=temperature,
                # top_p=1.0,
            )

            # Extract the message content from the response
            response_text = response.content[0].text

            # Parsing the topics from the response text
            parsed = parse_response(response_text)

            usage = response.usage if response.usage else None
            input_tokens = usage.input_tokens if usage else 0
            output_tokens = usage.output_tokens if usage else 0

        except Exception as error:
            print(f"Failed to call Claude API: {error}")
            if response:
                print(f"Response: {response}")
            return "none", error, 0, 0

        return parsed, input_tokens, output_tokens

    return call_claude_api
