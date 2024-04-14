# MODEL_NAME = "gpt-4-turbo-preview"
MODEL_NAME = "gpt-3.5-turbo-0125"
TEMPERATURE = 0

SYSTEM_PROMPT = """
You will be provided a post from a developer forum. 

Perform these tasks in this order:
1. Read the post.
2. Perform a sentiment analysis (Positive, Neutral, or Negative).
3. Record your reasoning for the sentiment analysis.
4. Provide a confidence score for the sentiment analysis.
5. Return the response in JSON with the following structure:
{
  "sentiment": "<sentiment>",
  "confidence": <confidence>,
  "reasoning: "<reasoning>"
}

If you cannot perform a sentiment analysis on the content, return JSON using the following structure:
{
  "sentiment": "None",
  "confidence": 0.0,
  "reasoning: "<reasoning>"
}
"""

SYSTEM_PROMPT_SHORT = """
You will be provided a post from a developer forum. 
Perform a sentiment analysis (Positive, Neutral, or Negative), include a confidence score, and your reasoning.

Return the response in JSON with this structure:
{
  "sentiment": "<sentiment>",
  "confidence": <confidence>,
  "reasoning: "<reasoning>"
}

If you cannot perform a sentiment analysis, return this JSON:
{
  "sentiment": "None",
  "confidence": 0.0,
  "reasoning: "<reasoning>"
}
"""


SYSTEM_PROMPT_MICRO = """
This is a developer forum post. 
Perform a sentiment analysis (Positive, Neutral, or Negative), add confidence score, and a very short reasoning.

Respond in this JSON format:
{
  "sentiment": "<sentiment>",
  "confidence": <confidence>,
  "reasoning: "<reasoning>"
}

Return this JSON if no sentiment is found:
{
  "sentiment": "None",
  "confidence": 0.0,
  "reasoning: "<reasoning>"
}
"""