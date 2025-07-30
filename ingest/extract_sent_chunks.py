# ingest/extract_sent_chunks.py
import os
import re
import fitz  # PyMuPDF

# Basic sentence splitting using punctuation
def simple_sentence_split(text):
    return re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)

def extract_sent_chunks(filepath, window_size=3, stride=1):
    doc = fitz.open(filepath)
    section_pattern = re.compile(r"^\d+(\.\d+)*\s+[A-Z].*")

    all_chunks = []
    current_section = "Unknown"
    chunk_id = 0

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        sentences = simple_sentence_split(text)

        # Detect new section heading
        for line in text.splitlines():
            if section_pattern.match(line.strip()):
                current_section = line.strip()

        images = [
            {"ext": img[1], "xref": img[0]}
            for img in page.get_images(full=True)
        ]

        for i in range(0, len(sentences) - window_size + 1, stride):
            window = " ".join(sentences[i:i + window_size]).strip()
            if len(window) < 30:
                continue

            has_equation = bool(re.search(r"[\^=\\]+|\\begin\{equation\}", window))
            is_reference_like = bool(re.search(r"\[\d+\]|\(.+?, \d{4}\)", window))

            chunk = {
                "chunk_id": f"{os.path.basename(filepath)}-p{page_num}-c{chunk_id}",
                "text": window,
                "page": page_num,
                "source": os.path.basename(filepath),
                "section": current_section,
                "has_equation": has_equation,
                "is_reference": is_reference_like,
                "images": images if i == 0 else [],
            }
            all_chunks.append(chunk)
            chunk_id += 1

    doc.close()
    return all_chunks
