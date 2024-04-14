"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""

import os
from typing import List

import google.generativeai as genai
from google.api_core import retry

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

models = {
    "gemini-1.0-pro": {
        "input_token_cost": 0,
        "output_token_cost": 0,
    }
}


# For convenience, a simple wrapper to let the SDK handle error retries
def generate_with_retry(model, prompt):
    return model.generate_content(prompt, request_options={"retry": retry.Retry()})


def call_gemini_api(
    system_prompt: str,
    messages: List[dict],
    model_name: str,
    temperature=0,
    max_tokens=2048,
    top_p=1,
    top_k=1,
    json_output=False,
):
    """Use a Gemini model to analyze the topics in a message."""
    response = None
    try:
        conversation = "\n\n".join(
            f"Role: {message['role']}\nContent: {message['content']}\n---\n"
            for message in messages
        )
        prompt = f"Your instructions: {system_prompt}\n\n---\n{conversation}"

        model = genai.GenerativeModel(
            "gemini-1.0-pro",
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_tokens,
            },  # type: ignore
            safety_settings=safety_settings,
        )
        response = model.generate_content(
            prompt, request_options={"retry": retry.Retry()}
        )

        # Extract the message content from the response
        response_text = ""
        for part in response.parts:
            response_text += part.text + "\n"
        if json_output:
            # strip characters before the first '{' and after the last '}'
            response_text = response_text[response_text.find("{") :]
            response_text = response_text[: response_text.rfind("}") + 1]

        input_tokens = model.count_tokens(prompt).total_tokens
        output_tokens = model.count_tokens(response_text).total_tokens
        model_data = models.get(model_name, {})
        total_cost = (
            model_data.get("input_token_cost", 0) * input_tokens
            + model_data.get("output_token_cost", 0) * output_tokens
        )

    except Exception as error:
        print(f"Failed to call Gemini API: {error}")
        if response:
            print(f"Response: {response}")
        return "null", 0, 0, 0

    return response_text, total_cost, input_tokens, output_tokens
