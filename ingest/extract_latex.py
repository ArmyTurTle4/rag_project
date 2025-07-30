import re

LATEX_SECTION_PATTERN = r"\\(chapter|section|subsection|subsubsection)\\*?\\{(.+?)\\}"
LATEX_EQUATION_PATTERN = r"\\$\\$(.*?)\\$\\$|\\\\\\[(.*?)\\\\\\]|\\\\begin\\{equation\\}(.*?)\\\\end\\{equation\\}"
LATEX_FIGURE_PATTERN = r"\\\\begin\\{figure\\}(.*?)\\\\end\\{figure\\}"

def extract_latex_sections(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()

    matches = list(re.finditer(LATEX_SECTION_PATTERN, content))
    sections = []

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_text = content[start:end].strip()

        equations = re.findall(LATEX_EQUATION_PATTERN, section_text, re.DOTALL)
        figures = re.findall(LATEX_FIGURE_PATTERN, section_text, re.DOTALL)
        eq_cleaned = ["".join(eq).strip() for eq in equations if any(eq)]

        sections.append({
            "title": match.group(2),
            "type": match.group(1),
            "text": section_text,
            "equations": eq_cleaned,
            "figures": figures,
            "source": file_path
        })
    return sections
