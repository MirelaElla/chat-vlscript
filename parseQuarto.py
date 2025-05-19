import os
import json
import re
import urllib.parse  # ✅ For URL encoding

def clean_inline(text):
    """Clean inline syntax but preserve meaningful text."""
    # Remove {#id} or {.class}
    text = re.sub(r'\{[^}]*\}', '', text)
    # Remove HTML-like tags
    text = re.sub(r'<[^>]*>', '', text)
    return text.strip()

def clean_block(text):
    """Clean full blocks (content or callouts)."""
    text = clean_inline(text)
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_callout(lines, start_index):
    """
    Extract a callout block starting at start_index.
    Returns the callout dict and the index of the next line after the block.
    """
    header_line = lines[start_index].strip()
    match = re.search(r'callout-([\w-]+)', header_line)
    callout_type = match.group(1) if match else "note"

    callout_lines = []
    i = start_index + 1
    while i < len(lines):
        if lines[i].strip() == ':::':
            break
        callout_lines.append(lines[i])
        i += 1
    i += 1  # Skip closing :::

    # Extract optional title from first heading inside callout
    callout_title = ""
    callout_content = []
    for j, line in enumerate(callout_lines):
        if line.strip().startswith('#'):
            callout_title = clean_inline(line.lstrip('#').strip())
            callout_content = callout_lines[j + 1:]
            break
    else:
        callout_content = callout_lines

    return {
        "type": callout_type,
        "title": callout_title,
        "content": clean_block('\n'.join(callout_content))
    }, i

def slugify(text):
    """Generate an anchor-compatible slug from German titles, keeping umlauts."""
    text = text.lower()
    text = re.sub(r'[^\w\säöüß.-]', '', text)  # Keep German characters
    text = re.sub(r'\s+', '-', text)  # Replace spaces with hyphens
    return text.strip('-')

def parse_quarto_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    sections = []
    current_section = None
    current_anchor = ""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    html_file = f"{base_name}.html"

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # New section
        if line.startswith('#'):
            if current_section:
                current_section["content"] = clean_block(current_section["content"])
                if current_section["content"] or current_section["callouts"]:
                    sections.append(current_section)

            level = len(line.split()[0])
            raw_title = line.lstrip('#').strip()

            # Extract anchor (e.g., {#avp})
            anchor_match = re.search(r'\{#([\w-]+)\}', raw_title)
            anchor = anchor_match.group(1) if anchor_match else ""

            title = clean_inline(raw_title)

            # Generate anchor from title if missing, then URL encode
            if anchor:
                encoded_anchor = urllib.parse.quote(anchor, safe='')
            else:
                generated_anchor = slugify(title)
                encoded_anchor = urllib.parse.quote(generated_anchor, safe='')

            if level == 1:
                weblink = f"https://wissarbkom.bitbucket.io/{html_file}"
            else:
                weblink = f"https://wissarbkom.bitbucket.io/{html_file}#{encoded_anchor}"


            current_section = {
                "title": title,
                "level": level,
                "content": "",
                "callouts": [],
                "weblink": weblink
            }
            i += 1
            continue

        # Callout block
        if line.startswith(':::') and 'callout' in line:
            if current_section is None:
                current_section = {
                    "title": "",
                    "level": 1,
                    "content": "",
                    "callouts": [],
                    "weblink": f"https://wissarbkom.bitbucket.io/{html_file}"
                }
            callout, next_index = parse_callout(lines, i)
            current_section["callouts"].append(callout)
            i = next_index
            continue

        # Regular content
        if current_section is not None:
            current_section["content"] += line + '\n'

        i += 1

    # Append last section
    if current_section:
        current_section["content"] = clean_block(current_section["content"])
        if current_section["content"] or current_section["callouts"]:
            sections.append(current_section)

    return {
        "filename": os.path.basename(file_path),
        "sections": sections
    }

def main():
    quarto_folder = "QuartoFiles"
    output_file = "document2.json"

    parsed_files = []

    for filename in os.listdir(quarto_folder):
        if filename.endswith(".qmd"):
            file_path = os.path.join(quarto_folder, filename)
            parsed_file = parse_quarto_file(file_path)
            parsed_files.append(parsed_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_files, f, ensure_ascii=False, indent=2)

    print(f"Parsed and structured {len(parsed_files)} Quarto files. Output saved to {output_file}")

if __name__ == "__main__":
    main()
