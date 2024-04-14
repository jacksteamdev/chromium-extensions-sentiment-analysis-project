from args import date_range

THREAD_SUMMARY_PROMPT = """
You will receive an email thread from the Chromium Extensions Google Group.
Summarize the thread to provide the following for a developer advocacy team:
- What was the thread about? Was the thread issue resolved?
- What was the average developer sentiment of the thread? Positive, Negative, Neutral
- Categorize the thread into one of the following categories:
    - If the thread mentions the Chrome Web Store in any way, the category is "chrome-web-store"
    - If the thread is not about Chrome Extensions, the category is "off-topic"
    - Else, the thread category is "development"
- If the category is "chrome-web-store", is a rejection ID mentioned? e.g., "Purple Titanium", "Gray Copper"
- If the category is "development", what web and chrome extension APIs are mentioned? e.g., chrome.storage.local, Navigator API, etc...
"""

THREAD_DATA_PROMPT = """
Return a JSON object with the following keys:
- sentiment: -1, 0, or 1; The average developer sentiment of the thread.
- resolved: 0 for false or 1 for true; Whether the thread issue was resolved.
- api_mentions: List of strings; The web and chrome extension APIs mentioned in the thread.
- rejection_id: String or null; The rejection ID mentioned in the thread.
- short_summary: String < 50 characters; A 50-character summary of the thread.
- category: String; off-topic, chrome-web-store, or development.
"""

MESSAGE_SUMMARY_PROMPT = """
You are a data analyst specializing in sentiment analysis for software developer communities. 
You will be provided a post from a developer forum. 
Perform a sentiment analysis (Positive, Neutral, or Negative) and include the numerical confidence score. 
Respond in 25 characters or less.

Evaluate sentence by sentence, and follow these guidelines:
- If sentiment is unclear or mixed is it Neutral
- If the user is asking a question it is Neutral
- if the user shares information without emotion it is Neutral
- If the user is asking for help, without being rude it is Neutral
- If no emotion expressed is it Neutral
- If the user solves a problem it is Positive
- If a user provides a solution it is Positive
- If the user is friendly or encouraging it is Positive
- If the user was unable to solve their issue it is Negative
- If the user expresses frustration is it Negative
- If the user expresses confusion is it Negative
- If the user expresses disappointment it is Negative
"""

MESSAGE_DATA_PROMPT = """
Return JSON with the following properties:
- sentiment: -1, 0, or 1; The sentiment analysis result.
- confidence: int; The confidence score of the sentiment analysis.
"""

REPORT_SUMMARY_PROMPT = f"""
Write a developer relations report based on these developer community forum threads.
The title of the report should include a summary of this date range (e.g., January 2024 or Q1 2024): "{date_range}"
Create a key insights section with 3-6 significant observations based on measurable metrics. 
Create a top posts section with subcategories, using Markdown footnotes to identify posts by URL. Give your reason that each post was selected as a top post.
Top post subcategories are: top 3 negative posts, top 3 unresolved posts, top 3 positive posts, and top 3 resolved posts.
"""

REPORT_DATA_PROMPT = """
Return JSON with the following properties:
- insights: list[str]; The key insights gathered from the developer community thread summaries.
- top_negative_posts: dict; Map of the top 3 negative posts by thread ID.
- top_resolved_posts: dict; Map of the top 3 resolved posts by thread ID.
- top_positive_posts: dict; Map of the top 3 positive posts by thread ID.
- top_unresolved_posts: dict; Map of the top 3 unresolved posts by thread ID.
"""

API_SUMMARY_PROMPT = """
You will receive a list of tags extracted from Chrome Extension developer community forum threads. 
Use your extensive knowledge of web and Chrome Extension taxonomy to standardize the tags. 
Process each tag in the list into a table with two columns: original and renamed. 
If the tag seems obscure or highly specific, try to consolidate it as one of the more general tags. 
Consolidate tags representing methods into the namespace tag, e.g., `chrome-scripting-register-content-scripts -> scripting-api`.
"""

API_DATA_PROMPT = """
Transform this table into a JSON object of key-value pairs.
"""