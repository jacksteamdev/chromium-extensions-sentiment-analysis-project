import json
import unittest
from functools import partial

import pandas as pd

from client_openai import (
    TokenLimitExceededError,
    build_and_validate_messages,
    call_openai_api,
)
from generate_report import generate_markdown_report
from run_openai import (
    REPORT_DATA_PROMPT,
    REPORT_SUMMARY_PROMPT,
)


class TestGenerateMarkdownReport(unittest.TestCase):

    # Returns the markdown report as a string
    @unittest.skip("This hits an external api and costs money")
    def test_generate_markdown_report_returns_string(self):

        # Load threads from the Excel file
        threads = pd.read_excel(
            "data/processed/openai-thread-summary-2024Q1.xlsx"
        ).to_dict("records")

        # Call the generate_markdown_report function
        result = generate_markdown_report(
            threads,
            REPORT_SUMMARY_PROMPT,
            REPORT_DATA_PROMPT,
            partial(call_openai_api, model_name="gpt-4-turbo-preview"),
            call_openai_api,
        )

        assert isinstance(result, dict)

        print("Markdown report generated successfully.")
        print("Report:")
        print(json.dumps(result))


class TestBuildAndValidateMessages(unittest.TestCase):

    # Given a list of messages, a system prompt, and a model name, the function should return a list of messages with the system prompt as the first message.
    def test_system_prompt_as_first_message(self):
        # Arrange
        messages = [{"role": "user", "content": "Hello"}]
        system_prompt = "System prompt"
        model_name = "gpt-3.5-turbo-0125"

        # Act
        result = build_and_validate_messages(system_prompt, messages, model_name)

        # Assert
        assert result[0]["role"] == "system"
        assert result[0]["content"] == system_prompt

    # Given an empty list of messages, the function should return a list with only the system prompt.
    def test_empty_list_of_messages(self):
        # Arrange
        messages = []
        system_prompt = "System prompt"
        model_name = "gpt-3.5-turbo-0125"

        # Act
        result = build_and_validate_messages(system_prompt, messages, model_name)

        # Assert
        assert len(result) == 1
        assert result[0]["role"] == "system"
        assert result[0]["content"] == system_prompt

    # Given a list of messages with list content, the function should return a list of messages with the concatenated text content.
    def test_concatenated_text_content(self):
        # Arrange
        messages = [
            {"role": "user", "content": "Hello"},
            {
                "role": "assistant",
                "content": [{"text": "How are you?"}, {"text": "I'm fine, thank you."}],
            },
            {"role": "user", "content": "That's great to hear!"},
        ]
        system_prompt = "System prompt"
        model_name = "gpt-3.5-turbo-0125"

        # Act
        result = build_and_validate_messages(system_prompt, messages, model_name)

        # Assert
        assert len(result) == 4
        assert result[0]["role"] == "system"
        assert result[0]["content"] == system_prompt
        assert result[1]["role"] == "user"
        assert result[1]["content"] == "Hello"
        assert result[2]["role"] == "assistant"
        assert result[2]["content"][0]["text"] == "How are you?"
        assert result[2]["content"][1]["text"] == "I'm fine, thank you."
        assert result[3]["role"] == "user"
        assert result[3]["content"] == "That's great to hear!"

    # Given a system prompt and messages with a total number of tokens greater than the model's context window, the function should raise a TokenLimitExceededError.
    def test_token_limit_exceeded_error(self):
        # Arrange
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "How can I help you?"},
            {"role": "user", "content": "I need assistance with a complex problem."},
            {"role": "assistant", "content": "Sure, I'll do my best to assist you."},
            {"role": "user", "content": "Here are the details:"},
            {
                "role": "assistant",
                "content": [
                    {"text": "First, you need to"},
                    {"text": "solve the equation"},
                    {"text": "and then"},
                    {"text": "analyze the results."},
                    {"text": "Finally,"},
                    {"text": "you can make a decision."},
                ],
            },
        ]
        system_prompt = "System prompt"
        model_name = "test-model"

        # Act and Assert
        with self.assertRaises(TokenLimitExceededError):
            build_and_validate_messages(system_prompt, messages, model_name)
