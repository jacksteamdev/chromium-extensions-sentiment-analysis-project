import base64
import unittest

from gmail_download import find_body_in_payload


class TestFindBodyInPayload(unittest.TestCase):
    # The function returns the email body in the expected MIME type.
    def test_returns_email_body_in_expected_mime_type(self):
        # Test input
        payload = {
            "mimeType": "text/html",
            "body": {
                "data": base64.urlsafe_b64encode(
                    "Test email body".encode("utf-8")
                ).decode("utf-8")
            },
        }

        # Expected output
        expected_body = "Test email body"
        expected_mime_type = "text/html"

        # Invoke the function
        actual_body, actual_mime_type = find_body_in_payload(payload)

        # Assertion
        assert actual_body == expected_body
        assert actual_mime_type == expected_mime_type

    # Handles payload with nested parts
    def test_handles_payload_with_multipart_alternative(self):
        # Test input
        payload = {
            "mimeType": "multipart/mixed",
            "body": {"size": 0},
            "parts": [
                {
                    "mimeType": "multipart/alternative",
                    "body": {"size": 0},
                    "parts": [
                        {
                            "mimeType": "text/plain",
                            "body": {
                                "data": base64.urlsafe_b64encode(
                                    "Plain email body".encode("utf-8")
                                ).decode("utf-8")
                            },
                        },
                        {
                            "mimeType": "text/html",
                            "body": {
                                "data": base64.urlsafe_b64encode(
                                    "HTML email body".encode("utf-8")
                                ).decode("utf-8")
                            },
                        },
                    ],
                }
            ],
        }

        # Expected output
        expected_body = "HTML email body"
        expected_mime_type = "text/html"

        # Invoke the function
        actual_body, actual_mime_type = find_body_in_payload(payload)

        # Assertion
        assert actual_body == expected_body
        assert actual_mime_type == expected_mime_type
