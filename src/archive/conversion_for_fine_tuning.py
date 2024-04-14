import pandas as pd
import json

# Read the CSV file
df = pd.read_csv('your_file.csv')

SYSTEM_PROMPT = "Analyze the sentiment of the user's message and provide a sentiment analysis report in JSON format"

output = []

for _, row in df.iterrows():
    body = row['body']
    expected = row['expected']
    confidence = row['confidence']
    
    message = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": body},
            {"role": "assistant", "content": json.dumps({"sentiment": expected, "confidence": float(confidence)})}
        ]
    }
    
    output.append(message)

# Write the output to a JSON file
with open('output.json', 'w') as outfile:
    json.dump(output, outfile, indent=4)