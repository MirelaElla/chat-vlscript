from dotenv import load_dotenv
import os
import json
import pandas as pd
import numpy as np
import re
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text, model="text-embedding-3-small"):
    if not isinstance(text, str) or not text.strip():
        print("Invalid or empty text input detected, returning zero vector.")
        return np.zeros(1536)  # Return a zero vector for invalid input
    text = text.replace("\n", " ")  # Normalize newlines
    try:
        response = client.embeddings.create(input=[text], model=model)
        response_dict = response.to_dict()  # Convert the response object to a dictionary
        embedding_vector = response_dict['data'][0]['embedding']
        return embedding_vector
    except Exception as e:
        print(f"An error occurred: {e}")
        return np.zeros(1536)  # Return a zero vector if there's an error


# Load JSON data from file
with open('document.json', 'r', encoding='utf-8') as file:
    documents = json.load(file)

# Extract contents for embedding
data = {
    'filename': [],
    'section_title': [],
    'embedding': []
}

for document in documents:
    for section in document['sections']:
        content = section['content']
        if isinstance(content, str):  # Check if content is a string
            embedding = get_embedding(content)
            data['filename'].append(document['filename'])
            data['section_title'].append(section['title'])
            data['embedding'].append(str(list(embedding)))  # Convert embedding to string for storage
        else:
            print(f"Ignored non-string content in {document['filename']} under the title '{section['title']}'")

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('embeddings.csv', index=False)
