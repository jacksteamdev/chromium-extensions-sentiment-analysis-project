from typing import Callable, List, Optional
import json

from posts__claude_util_client import completions_with_backoff


def init_categorize_message(
    model_name,
    system_prompt,
    temperature,
    generate_shots: Optional[Callable[[str], List]] = None,
):
    """Initialize a function to analyze sentiment in a message using an Anthropic model."""

    def categorize_sentiment(body: str):
        """Use an Anthropic model to categorize the message as Development, Publishing, or OffTopic."""
        response = None
        try:
            # Generate few-shot examples if a function is provided
            shots = generate_shots(body) if generate_shots else []

            response = completions_with_backoff(
                model=model_name,
                # system prompt type message isn't supported in the API
                system=system_prompt,
                messages=[
                    # put few-shot examples here
                    *shots,
                    {"role": "user", "content": body},
                ],
                max_tokens=512,  # maximum number of tokens in the response
                # either temperature or top_p can be used, but not both
                temperature=temperature,
                # top_p=1.0,
                stop_sequences=[
                    "}"
                ],  # stop generation when the model predicts the end of the JSON object
            )

            # Extract the message content from the response
            response_text = response.content[0].text

            # Parsing the sentiment and confidence from the response
            response_data = (
                {"category": "None"}
                if response_text is None
                else json.loads(response_text + "}")
            )
            category = response_data["category"]
            reasoning = response_data["reasoning"]

            usage = response.usage if response.usage else None
            input_tokens = usage.input_tokens if usage else 0
            output_tokens = usage.output_tokens if usage else 0

        except Exception as error:
            print(f"Failed to analyze sentiment: {error}")
            if response:
                print(f"Response: {response}")
            return "none", error, 0, 0

        return category, reasoning, input_tokens, output_tokens

    return categorize_sentiment
