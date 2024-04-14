import os
import backoff
from posts__openai import OpenAI, RateLimitError


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

models = {
    "gpt-3.5-turbo-0125": {
        "input_token_cost": 0.5 / 1e6,
        "output_token_cost": 1.50 / 1e6,
    },
    "gpt-4-turbo-preview": {
        "input_token_cost": 10 / 1e6,
        "output_token_cost": 30 / 1e6,
    },
}


@backoff.on_exception(backoff.expo, RateLimitError)
def completions_with_backoff(**kwargs):
    """Call the OpenAI API with exponential backoff to handle rate limits."""
    response = client.chat.completions.create(**kwargs)
    return response
