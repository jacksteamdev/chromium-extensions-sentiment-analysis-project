import backoff
import anthropic
from typing import Any, Dict

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    # api_key="my_api_key",
)


models = {
    "claude-3-haiku-20240307": {
        "input_token_cost": 0.25 / 1e6,
        "output_token_cost": 1.25 / 1e6,
    },
    "claude-3-sonnet-20240229": {
        "input_token_cost": 3 / 1e6,
        "output_token_cost": 15 / 1e6,
    },
    "claude-3-opus-20240229": {
        "input_token_cost": 15 / 1e6,
        "output_token_cost": 75 / 1e6,
    },
}


@backoff.on_exception(
    backoff.expo,
    # retry if we get rate limited or the server is overloaded
    (anthropic.RateLimitError, anthropic.InternalServerError),
    max_time=60 * 5,
)
def completions_with_backoff(**kwargs):
    """Call the Anthropic API with exponential backoff to handle rate limits."""
    response = client.messages.create(**kwargs)
    return response
