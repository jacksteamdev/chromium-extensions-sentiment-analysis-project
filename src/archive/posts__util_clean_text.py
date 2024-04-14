import re

import pandas as pd

FLAGS = re.MULTILINE | re.DOTALL

INPUT_FILE_NAME = "107_openai_souce_data.xlsx"
OUTPUT_FILE_NAME = "107_openai_souce_data_1.xlsx"


def clean_author(text):
    # Remove single and double quotes
    text = text.replace("'", "").replace('"', "")

    # Remove email addresses enclosed in angle brackets
    text = re.sub(r"<\S+@\S+\.\S+>", "", text)

    # Remove "via Chromium"
    text = text.replace("via Chromium Extensions", "")

    return text


def clean_title(text):
    # Remove "Re: [crx]" --> [crx] and "[crx] Re:"--> [crx]
    text = re.sub(r"Re: \[crx\]", "[crx]", text)
    text = re.sub(r"\[crx\] Re:", "[crx]", text)

    return text


def clean_message_body(body_text):
    """Clean the email body text."""

    # Handle non-string input
    if not isinstance(body_text, str):
        return body_text

    # Remove non-printing characters, excluding newlines
    body_text = re.sub(r"[^\x20-\x7E\n]", "", body_text)

    # Remove lines that start quotes
    body_text = re.split(r"^On.*wrote:$", body_text, flags=FLAGS)[0]

    # Remove quoted lines
    lines = body_text.split("\n")
    non_quote_lines = [line for line in lines if not re.match(r"^>.*$", line)]
    body_text = "\n".join(non_quote_lines)

    # Remove signature
    body_text = re.split(r"\n--\s*\n?", body_text, 1, flags=FLAGS)[0]

    # Remove image placeholders
    body_text = re.sub(r"\[image:.*\]", "", body_text, flags=FLAGS)

    # Redact URLs, e.g., "<http://example.com>" or "<chrome-extension://...>"
    body_text = re.sub(r"<?(https?://\S+)>?", "<URL>", body_text, flags=FLAGS)
    body_text = re.sub(r"<?(chrome-extension://\S+)>?", "<URL>", body_text, flags=FLAGS)

    # Redact email addresses, e.g., "<me@example.com>" or "me@example.com"
    body_text = re.sub(r"<?(\S+@\S+)>?", "<EMAIL>", body_text, flags=FLAGS)

    # Remove DRE signatures
    body_text = re.sub(r"Oliver Dunk.*GB", "", body_text, flags=FLAGS)
    body_text = re.sub(r"^patrick$", "", body_text, flags=FLAGS)

    # Compact multiple blank lines into one
    body_text = re.sub(r"(\s*\n){2,}", "\n\n", body_text)

    return body_text.strip()


def main():
    df = pd.read_excel(INPUT_FILE_NAME)
    df["body"] = df["body"].apply(clean_message_body)
    df.to_excel(OUTPUT_FILE_NAME, sheet_name="CSV", index=False)


if __name__ == "__main__":
    main()
