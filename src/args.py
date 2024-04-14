import argparse
import re

# Set up command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument(
    "--date-range",
    type=str,
    help="The date range to search for, e.g., `after:2024/01/01 before:2024/01/31`. Not compatible with --gmail-query",
)
parser.add_argument(
    "--gmail-query",
    type=str,
    help="The Gmail query to search for threads by. Not compatible with --date-range",
)
parser.add_argument(
    "--excel-file",
    type=str,
    default="data/reports/report.xlsx",
    help="The name of the Excel file to save the report to.",
)
parser.add_argument(
    "--report-file",
    type=str,
    default="data/reports/report.md",
    help="The name of the Markdown file to save the report to.",
)
parser.add_argument(
    "--resume",
    action="store_true",
    help="Whether to reuse the existing Excel file or overwrite it.",
)
parser.add_argument(
    "--use-test-data",
    action="store_true",
    help="Use a preselected set of thread ids.",
)
parser.add_argument(
    "--max-thread-count",
    type=int,
    default=0,
    help="The maximun number of threads to process, additional threads will be excluded.",
)
parser.add_argument(
    "--max-thread-token-count",
    type=int,
    default=1e4,
    help="The maximum number of tokens a thread may contain. If the thread contains more than this number of tokens, some messages will be excluded.",
)
parser.add_argument(
    "--max-message-token-count",
    type=int,
    default=1e3,
    help="The maximum number of tokens a message may contain. Messages with more than the max tokens will be ignored.",
)
parser.add_argument(
    "--dre-names",
    type=lambda x: re.split(r",\s*", x),
    default="Oliver Dunk,Patrick Kettner,Sebastian Benz,Simeon Vincent,Amy Steam",
    help="A CSV string of DRE names.",
)
args = parser.parse_args()

# Validate args
if args.date_range and args.gmail_query:
    parser.error("--date_range and --gmail_query cannot be used together.")
if not args.date_range and not args.gmail_query:
    parser.error("one of --date-range or --gmail-query must be defined.")

# Standalone args
excel_file = args.excel_file
report_file = args.report_file
dre_names = args.dre_names
max_thread_token_count = args.max_thread_token_count
max_message_token_count = args.max_message_token_count

# Guard against accidental data loss
resume = args.resume
if not resume:
    proceed = input(
        "This operation may overwrite the existing file. Do you want to proceed? (y/[n]): "
    )
    if proceed.lower() != "y":
        print("Operation cancelled by user.")
        exit()

# Build the Gmail query
date_range = args.date_range
gmail_query = args.gmail_query or f"list:chromium-extensions@chromium.org {date_range}"

max_thread_count = args.max_thread_count
# High quality threads to use for development
thread_ids = (
    [
        "1894e930b6e42900",
        "189bb2b278d284b8",
        "1874a72bdb382df8",
        "186ec9c2334f8495",
        "17d499ce45639308",
        "17ff0ba23ab873d5",
        "180f7200d8d2405a",
        "18485492e7ca6002",
        "1858c8517779fb9a",
        "186dc749d4cad1b5",
        "18aee4ac30136dcc",
        "180a81e8c509ee5a",
        "17ec6a7a13b384f0",
        "181ea0a053aac110",
        "18cae1983e2b21db",
        "18bded1c0e37a34b",
    ]
    if args.use_test_data
    else None
)
