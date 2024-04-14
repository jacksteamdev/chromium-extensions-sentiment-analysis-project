from typing import List
import anthropic
import backoff


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
    anthropic.RateLimitError,
    max_time=60 * 5,
    on_backoff=lambda details: print(
        f"Rate Limit Error, will try again in {details.get('wait', 0)}s"
    ),
)
@backoff.on_exception(
    backoff.expo,
    # retry if we get rate limited or the server is overloaded
    anthropic.InternalServerError,
    max_time=60 * 5,
    on_backoff=lambda details: print(
        f"Internal Server Error, will try again in {details.get('wait', 0)}"
    ),
)
def completions_with_backoff(**kwargs):
    """Call the Anthropic API with exponential backoff to handle rate limits."""
    response = client.messages.create(**kwargs)
    return response


def call_claude_api(
    system_prompt: str,
    messages: List[dict],
    model_name: str,
    temperature=0.2,
    json_output=False,
    max_tokens=512,
):
    """Use an Anthropic model to analyze the topics in a message."""
    response = None
    try:
        if json_output:
            messages.append(
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "{"}],
                },
            )

        response = completions_with_backoff(
            model=model_name,
            temperature=temperature,
            system=system_prompt,
            messages=messages,
            max_tokens=max_tokens,
        )

        # Extract the message content from the response
        response_text = response.content[0].text

        if json_output:
            response_text = "{" + response_text

        usage = response.usage if response.usage else None
        input_tokens = usage.input_tokens if usage else 0
        output_tokens = usage.output_tokens if usage else 0
        model = models.get(model_name, {})
        total_cost = (
            model.get("input_token_cost", 0) * input_tokens
            + model.get("output_token_cost", 0) * output_tokens
        )

    except Exception as error:
        print(f"Failed to call Claude API: {error}")
        if response:
            print(f"Response: {response}")
        return "null", 0, 0, 0

    return response_text, total_cost, input_tokens, output_tokens
