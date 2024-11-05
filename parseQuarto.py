import os
import json
import re

def clean_text(text):
    # Remove content between curly brackets
    text = re.sub(r'\{[^}]*\}', '', text)
    
    # Remove content between < >
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove :::
    text = text.replace(':::', '')
    
    # Remove ~
    text = text.replace('~', '')
    
    # Remove \n
    text = text.replace('\n', ' ')
    
    # Remove callout-tip, callout-note, callout-important, callout-warning
    text = text.replace('callout-tip', '').replace('callout-note', '').replace('callout-important', '').replace('callout-warning', '')
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text.strip()

def parse_quarto_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Extract sections
    sections = []
    current_section = None
    for line in content.split('\n'):
        if line.startswith('#'):
            if current_section:
                current_section["content"] = clean_text(current_section["content"])
                if current_section["content"]:  # Check if content is not empty
                    sections.append(current_section)
            level = len(line.split()[0])  # Count the number of '#' to determine level
            title = line.lstrip('#').strip()
            current_section = {
                "title": clean_text(title),  # Clean the title
                "level": level,
                "content": ""
            }
        elif current_section is not None:
            current_section["content"] += line + "\n"

    if current_section:
        current_section["content"] = clean_text(current_section["content"])
        if current_section["content"]:  # Check if content is not empty
            sections.append(current_section)

    return {
        "filename": os.path.basename(file_path),
        "sections": sections
    }

def main():
    quarto_folder = "QuartoFiles"
    output_file = "document.json"

    parsed_files = []

    for filename in os.listdir(quarto_folder):
        if filename.endswith(".qmd"):
            file_path = os.path.join(quarto_folder, filename)
            parsed_file = parse_quarto_file(file_path)
            parsed_files.append(parsed_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_files, f, ensure_ascii=False, indent=2)

    print(f"Parsed and cleaned {len(parsed_files)} Quarto files. Output saved to {output_file}")

if __name__ == "__main__":
    main()
