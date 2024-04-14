import os
from typing import List
import backoff
from openai import BadRequestError, OpenAI, RateLimitError

from num_tokens_from_string import num_tokens_from_string


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

models = {
    "gpt-3.5-turbo-0125": {
        "input_token_cost": 0.5 / 1e6,
        "output_token_cost": 1.50 / 1e6,
        "context_window": 3e3,
    },
    "gpt-4-turbo-preview": {
        "input_token_cost": 10 / 1e6,
        "output_token_cost": 30 / 1e6,
        "context_window": 1.28e5,
    },
}


class TokenLimitExceededError(ValueError):
    """Exception raised when the token count exceeds the model's context window."""

    pass


def build_and_validate_messages(system_prompt: str, messages: list, model_name: str):
    all_messages = [
        {"role": "system", "content": system_prompt},
        *messages,
    ]

    all_text = ""
    for m in all_messages:
        content = m.get("content", "")
        if isinstance(content, list):
            all_text += "".join(c["text"] for c in content if "text" in c)
        elif isinstance(content, str):
            all_text += content

    num_tokens = num_tokens_from_string(all_text)
    context_window = models.get(model_name, {}).get("context_window", 0)
    if num_tokens > context_window:
        raise TokenLimitExceededError(
            f"Token count is greater than the {model_name} context window: {num_tokens} > {context_window}"
        )

    return all_messages


@backoff.on_exception(backoff.expo, RateLimitError)
@backoff.on_exception(backoff.expo, BadRequestError, max_tries=3)
def completions_with_backoff(**kwargs):
    """Call the OpenAI API with exponential backoff to handle rate limits."""
    response = client.chat.completions.create(**kwargs)
    return response


def call_openai_api(
    system_prompt: str,
    messages: List[dict],
    model_name: str,
    temperature=0.2,
    json_output=False,
    **kwargs,
):
    """Use an OpenAI model to analyze the topics in a message."""
    response = None
    try:
        response = completions_with_backoff(
            model=model_name,
            temperature=temperature,
            response_format={"type": "json_object"} if json_output else None,
            messages=build_and_validate_messages(system_prompt, messages, model_name),
            **kwargs,
        )

        # Extract the message content from the response
        response_text = response.choices[0].message.content

        usage = response.usage if response.usage else None
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        model = models.get(model_name, {})
        total_cost = (
            model.get("input_token_cost", 0) * input_tokens
            + model.get("output_token_cost", 0) * output_tokens
        )

    except Exception as error:
        print(f"Failed to call OpenAI API: {error}")
        if response:
            print(f"Response: {response}")
        return "null", 0, 0, 0

    return response_text, total_cost, input_tokens, output_tokens
