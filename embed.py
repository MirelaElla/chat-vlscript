from dotenv import load_dotenv
import os
import json
import pandas as pd
import numpy as np
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text, model="text-embedding-3-small"):
    if not isinstance(text, str) or not text.strip():
        print("Invalid or empty text input detected, returning zero vector.")
        return np.zeros(1536)  # Return zero vector for invalid input
    text = text.replace("\n", " ")  # Normalize newlines
    try:
        response = client.embeddings.create(input=[text], model=model)
        response_dict = response.to_dict()
        return response_dict['data'][0]['embedding']
    except Exception as e:
        print(f"An error occurred during embedding: {e}")
        return np.zeros(1536)

# Load parsed JSON structure
with open('document.json', 'r', encoding='utf-8') as file:
    documents = json.load(file)

# Collect embedding records
records = []

for doc in documents:
    filename = doc["filename"]
    for section in doc["sections"]:
        section_title = section.get("title", "")
        section_content = section.get("content", "")
        section_level = section.get("level", 1)
        section_weblink = section.get("weblink", "")
        
        if section_content.strip():
            records.append({
                "filename": filename,
                "source_type": "section",
                "section_title": section_title,
                "callout_type": "",
                "callout_title": "",
                "content": section_content,
                "level": section_level,
                "weblink": section_weblink
            })

        # Process callouts
        for callout in section.get("callouts", []):
            callout_type = callout.get("type", "")
            callout_title = callout.get("title", "")
            callout_content = callout.get("content", "")
            if callout_content.strip():
                records.append({
                    "filename": filename,
                    "source_type": "callout",
                    "section_title": section_title,
                    "callout_type": callout_type,
                    "callout_title": callout_title,
                    "content": callout_content,
                    "level": section_level,
                    "weblink": section_weblink
                })

# Embed and collect results
data = {
    "filename": [],
    "source_type": [],
    "section_title": [],
    "callout_type": [],
    "callout_title": [],
    "level": [],
    "content": [],
    "embedding": [],
    "weblink": []
}

for record in records:
    text_to_embed = f"{record['callout_title'] or record['section_title']}. {record['content']}"
    emb = get_embedding(text_to_embed)

    data["filename"].append(record["filename"])
    data["source_type"].append(record["source_type"])
    data["section_title"].append(record["section_title"])
    data["callout_type"].append(record["callout_type"])
    data["callout_title"].append(record["callout_title"])
    data["level"].append(record["level"])
    data["content"].append(record["content"])
    data["embedding"].append(str(list(emb)))
    data["weblink"].append(record["weblink"])

# Save to DataFrame
df = pd.DataFrame(data)
df.to_csv("embeddings.csv", index=False)
print("Embeddings saved to embeddings.csv")
