from posts__openai import RateLimitError
from typing import Callable, List, Optional
import json

from posts__openai_util_client import client, completions_with_backoff


def init_analyze_sentiment(
    model_name,
    system_prompt,
    temperature,
    generate_shots: Optional[Callable[[str], List]] = None,
):
    """Initialize a function to analyze sentiment in a message using an OpenAI model."""

    def analyze_sentiment(body: str):
        """Use an OpenAI model to analyze sentiment in a message."""
        try:
            # Generate few-shot examples if a function is provided
            shots = generate_shots(body) if generate_shots else []

            response = completions_with_backoff(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    # put few-shot examples here
                    *shots,
                    {"role": "user", "content": body},
                ],
                # either temperature or top_p can be used, but not both
                temperature=temperature,
                # top_p=1.0,
                seed=2,  # makes the response deterministic
                response_format={"type": "json_object"},
            )

            # Extract the message content from the response
            response_text = response.choices[0].message.content

            # Parsing the sentiment and confidence from the response
            response_data = (
                {"sentiment": "none", "confidence": 0.0}
                if response_text is None
                else json.loads(response_text)
            )
            sentiment = str(response_data["sentiment"])
            confidence = float(response_data["confidence"])

            usage = response.usage if response.usage else None
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0

        except Exception as error:
            print(f"Failed to analyze sentiment: {error}")
            return "none", 0.0, 0, 0

        return sentiment, confidence, input_tokens, output_tokens

    return analyze_sentiment
