import re

def parse_toc_file(toc_path):
    with open(toc_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    entries = []
    for raw_line in lines:
        line = str(raw_line).strip()  # Ensure it's a string

        # Only process lines that start with \contentsline
        if not line.startswith(r'\contentsline'):
            continue

        # Match chapter/section lines
        match = re.search(
            r'\\contentsline\s*\{(chapter|section|subsection|subsubsection)\}'
            r'\{\s*\\numberline\s*\{([^}]*)}\s*([^}]*)}'
            r'\{(\d+)}', line)
        if not match:
            continue

        section_type, number, title, page = match.groups()

        # Extract the correct page number just before {chapter.xxx}
        page_match = re.search(r'\{(\d+)}\{(?:chapter|section|subsection|subsubsection)\.[^}]+\}', line)

        if not page_match:
            continue
        page = int(page_match.group(1))

        # Clean title
        title = re.sub(r'\\[a-zA-Z]+\s*', '', title)          # remove LaTeX commands like \relax
        title = re.sub(r'\{[^{}]*\}', '', title)              # remove {...}
        title = re.sub(r'(?<![23])\b\d+\b(?![D])', '', title) # Preserve "2D" and "3D" patterns, remove other stray numbers
        title = re.sub(r'[\\{}]', '', title)                  # remove stray \ or braces
        title = title.strip()

        entries.append({
            'number': number.strip(),
            'title': title,
            'page': int(page)
        })

    return entries

# Example usage (uncomment for standalone test):
# parsed = parse_toc_file("CompMechanicsLectureNotesTOC.toc")
# for entry in parsed[:10]:
#     print(entry)

# Optional test run
if __name__ == "__main__":
    toc_file = "../data/CompMechanicsLectureNotesTOC.toc"
    toc_entries = parse_toc_file(toc_file)
    for e in toc_entries[:1000]:  # Display first 20 entries for inspection
        print(e)
