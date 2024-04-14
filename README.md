# Chromium Extensions Sentiment Analysis Project

## Overview

This project is designed to generate a comprehensive report based on email threads from the Chromium Extensions Google Group. It utilizes OpenAI's API to analyze and summarize the content of these threads, focusing on developer sentiment, issue resolution, and categorization based on specific criteria. The script also handles data extraction and report generation, saving the results in both Excel and Markdown formats.

You can see [a video onboarding to the project here](https://www.loom.com/share/350d1523bf0941059c3d57ee85304f25?sid=3f835b63-984a-4d9b-9f00-f69d7c087f43).

### Findings

You can view our findings in [this document](https://docs.google.com/document/d/1ety5NT6FVIFtHj_JnzIHjSc2-NpYcy_-sHeDuCr3FsQ/edit?usp=sharing).

Additional experiments and prompts may be found in `src/archive/`. Archived experiments have not been maintained, so they may not work as-is.

### Key Features:

- Email Querying: Fetches thread IDs from Gmail based on a specified date range and query parameters.
- Data Summarization and Extraction: Uses OpenAI's API to summarize threads and messages and extract relevant data like sentiment, APIs mentioned, and resolution status.
- Report Generation: Compiles a developer relations report summarizing insights from the threads, categorizing top posts, and providing key metrics. The report is saved in Markdown format.
- Excel Integration: Data is also saved in an Excel file for further analysis, with the ability to reuse existing files to avoid data loss.

## Getting Started

### Prerequisites

- Python 3.9
- [Conda](https://docs.anaconda.com/free/miniconda/miniconda-install/)
- [Gmail API credentials](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application)
- [OpenAI API key](https://platform.openai.com/docs/quickstart?context=python)
- Optional
  - [Gemini API key](https://ai.google.dev/tutorials/python_quickstart)
  - [Anthropic API key](https://docs.anthropic.com/claude/docs/getting-access-to-claude)

### Installation

1. Clone the repository.
2. Install the required Python packages [using conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file):

```sh
conda env create -f environment.yml
conda activate crx-sentiment
```

3. Place your Gmail API credentials in the project root directory.
4. Set your OpenAI API key as the environment variable "OPENAI_API_KEY".
5. \[Optional\] Set your other API keys as environment variables.

```sh
# Linux/Mac
export OPENAI_API_KEY='your_openai_api_key_here'
export GEMINI_API_KEY='your_gemini_api_key_here'
export ANTHROPIC_API_KEY='your_anthropic_api_key_here'

# Windows
set OPENAI_API_KEY=your_openai_api_key_here
set GEMINI_API_KEY=your_gemini_api_key_here
set ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Conda
conda env config vars set OPENAI_API_KEY='your_openai_api_key_here'
conda env config vars set GEMINI_API_KEY='your_gemini_api_key_here'
conda env config vars set ANTHROPIC_API_KEY='your_anthropic_api_key_here'
```

## Usage

To run the report script, use the following command:

```sh
python src/run_openai.py \
  --date-range="after:2024/01/01 before:2024/01/31" \
  --excel-file="data/reports/report.xlsx" \
  --report-file="data/reports/report.md"
```

Arguments:

- `--date-range` is an optional argument that specifies the date range for the Gmail query. Either `--date-range` or `--gmail-query` must be defined.
- `--gmail-query` is an optional argument that specifies the query to send to Gmail, see https://support.google.com/mail/answer/7190. Default is `list:chromium-extensions@chromium.org` and the date range.
- `--excel-file` is an optional argument that specifies the Excel file containing data to be used for training and testing. The default value is `data/processed/report.xlsx` and is relative to the project root.
- `--report-file` is an optional argument that specifies the Markdown file to save predictions and results. The default value is `data/processed/report.md` and is relative to the project root.
- `--resume` is an optional flag that indicates whether to use the existing Excel file or generate a new one. If specified, the script will load threads from the existing file. If not specified, the script will generate a new Excel file with updated data, overwriting the target file if it exists. The default value is `False`.

## Prompts

The prompts are found in `src/prompts.py`. We found that using a two-step summarization process was most effective for the higher level summarization tasks this project entails. First, a summarization prompt is used to answer questions about the text. A data extraction prompt then specifies JSON object properties for the model to extract from the output of the first prompt. The generated JSON is saved in the Excel file.

There are four main prompt tasks:

1. Thread analysis: Threads are summarized to answer several questions: What was the thread about? Was the thread issue resolved? Is the thread about the Chrome Web Store, extensions development, or was it off-topic? Is there a rejection id? What Chrome extension APIs are mentioned? Results are saved to the Excel file in the "threads" sheet.
2. Message analysis: Sentiment analysis is the main task for messages. Messages are categorized according to guidelines as Positive, Neutral, or Negative (-1, 0, 1). Results are saved to the Excel file in the "messages" sheet.
3. Community report: The community report contains key insights with metrics and the top negative,positive, resolved, and unresolved posts. The report is output as a Markdown file.
4. API tag standardization: When threads are analyzed for extension API mentions, the output is not coherent, which means that API tags may take several forms, and it's impossible to use string matching to analyze the data. During the tag standardization step, the prompt instructs the model to standardize and combine API tags.

## Concepts

### Zero-Shot vs. Few-Shot Learning Explained Simply

#### Zero-Shot Learning

Think of zero-shot learning as the model's ability to tackle tasks it hasn't been directly trained for. For sentiment analysis in our project, this means the model can judge if a text's sentiment is positive or negative without needing examples of sentiment-labeled text. It uses its broad knowledge gained from training on diverse data to make these judgments. Zero-shot learning is perfect when we don't have specific data for the task at hand.

#### Few-Shot Learning

Few-shot learning is about teaching the model with multiple examples. In our sentiment analysis project, we give the model a small set of texts where the sentiment is pre-determined. This small training set helps the model understand what we're looking for and make accurate predictions even when the data is scarce. Few-shot learning lets us fine-tune the model's responses using examples.

### The Basics of Embeddings

#### What Are Embeddings?

Embeddings turn words, phrases, or documents into arrays of numbers called vectors. These numbers capture not just the word but its context and meaning—words with similar meanings get similar number lists. This numerical form is something our AI models can work with, letting them understand and process language.

#### Using Embeddings to Compare Text Samples

Embeddings are useful because we can compare embedding vectors using cosign similarity to determine if two text samples are related. In the most simple use case, a vector store can support text search. In this project, we use embedding text search to find the most similar examples to send in a smaller set of examples. In some situations, using a smaller set of similar examples helps improve the model's performance.

## Unit Tests

This project includes unit tests in the `tests/` directory.
