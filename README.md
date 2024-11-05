# chat-with-docs
Make embeddings from documents and ask questions about contents

## About the project
This project is about creating a knowledge base and chatting about these contents to get fast and precise answers to questions related to these contents. Currently, the knowledge base consists of the book "Wissenschaftliches Arbeiten und Kommunizieren" by Nicolas Rothen and Alodie Rey-Mermet ([the Bitbucket project](https://bitbucket.org/nrothen/vorlesungsskript_m01_fs2021_wissarb/src/master/)).

## Getting started
* You need an OpenAI API key saved in the ".env" file (OPENAI_API_KEY = "your-key-comes-here"). The .env file is git-ignored.
* To install all required packages you can run the command in the cmd terminal `pip install -r requirements.txt`
* Then run the command in cmd terminal `python chat.py`. You can ask questions in the terminal about the embedded document (see example questions below). The chat returns relevant passages of the embedded documents. Based on this context, the chat then generates an answer. It should only answer when the question is related to the content of the embedded documents. Otherwise it should answer "Ich weiss es nicht." (I don't know). You can test this with trick questions (see an example below)

### Example questions:
* Um was geht es hier?
* Was sind die wichtigsten vier Fragen?
* Was sind die Formatvorgaben für die Gestaltung eines Posters?
* Was sind die Abschnitte in einer wissenschaftlichen Arbeit?
* Muss ich Inferenzstatistik auf einem Poster berichten? (diese Frage fürt zu einer falschen Antwort, wenn "schliessende Statistik" geschrieben wird. Wenn "schließende" geschrieben wird, dann kommt eine korrekte Antwort. --> CH Deutsch vs. DE Deutsch)
* Was ist die Rezeptmetapher?
* Was ist bei der Wahl des Titels zu beachten?

### Trick question:
* Was ist die Reihenfolge der Planeten in unserem Sonnensystem?

## Detailed description of the chat components
### QuartoParser
This folder contains a script for parsing and cleaning contents from Quarto files and save it in a json file
* `parse.py` parses and cleans contents from Quarto files in the subfolder "QuartoFiles" and saves it as `document.json`. This file is then used for embedding (see `embed.py`).

### `embed.py`
* Loads environment variables and initializes the OpenAI client with the API key.
* Loads document data from a JSON file.
* Computes embeddings for each section of the documents and stores them in a CSV file. This file is then used for chatting (see `chat.py`)

### `chat.py`
* Loads environment variables and initializes the OpenAI client.
* Loads a CSV file containing embeddings.
* Converts string embeddings back to NumPy arrays.
* Loads document data from a JSON file and creates a dictionary for quick access.
* Defines a function to get embeddings from the OpenAI API.
* Defines a chat_with_document_base function to handle user queries by computing embeddings and finding the closest match in the document base.

## Next steps
- [ ] Create a GUI. Shiny app works, but there seems to be no way to upload it on the shiny app server without sharing the OpenAI API key.
- [ ] Fix problems related to Swiss German 

