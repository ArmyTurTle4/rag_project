import os
import fitz  # PyMuPDF
import pickle
import re
import nltk
from embed.embedder import embed_chunks
from embed.vector_store import VectorStore
from ingest.toc_parser import parse_toc_file

nltk.download('punkt')

TOC_CACHE_PATH = "./vector_index/toc.pkl"
VECTOR_DB_PATH = "./vector_index/index.pkl"

#SECTION_HEADER_PATTERN = re.compile(r"^((chapter|section|part)\s+\d+[:.]?|\d+(\.\d+)*)\s+.+$", re.IGNORECASE)
#EMAIL_PATTERN = re.compile(r"@|\.edu|gmail\.com|google\.com|research")


import os
import re
import fitz  # PyMuPDF

EMAIL_PATTERN = re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b")
AFFILIATION_PATTERN = re.compile(r"(university|department|institute|faculty of|school of)", re.IGNORECASE)
SECTION_HEADER_PATTERN = re.compile(r"^((chapter|section|part)\s+\d+[:.]?|\d+(\.\d+)*)\s+.+$", re.IGNORECASE)

def extract_structured_sections(filepath, toc_lookup=None):
    doc = fitz.open(filepath)
    chunks = []
    seen_texts = set()
    current_section = "Unknown Section"

    section_by_page = {}
    if toc_lookup:
        sorted_toc = sorted(toc_lookup, key=lambda x: x["page"])
        for i, entry in enumerate(sorted_toc):
            start = entry["page"]
            end = sorted_toc[i + 1]["page"] if i + 1 < len(sorted_toc) else 10_000
            for p in range(start, end):
                section_by_page[p] = entry["title"]

    for page_num, page in enumerate(doc, start=1):
        current_section = section_by_page.get(page_num, current_section)

        blocks = page.get_text("dict")["blocks"]
        images = [{"ext": img[1], "xref": img[0]} for img in page.get_images(full=True)]

        page_paragraphs = []
        for block in blocks:
            if "lines" not in block:
                continue

            cleaned_lines = []
            for line in block["lines"]:
                line_text = " ".join(span["text"] for span in line["spans"]).strip()
                if not line_text or len(line_text) < 10:
                    continue
                if EMAIL_PATTERN.search(line_text.lower()) or AFFILIATION_PATTERN.search(line_text.lower()):
                    continue
                cleaned_lines.append(line_text)

            text = " ".join(cleaned_lines).strip()
            if not text or len(text) < 10:
                continue

            if SECTION_HEADER_PATTERN.match(text):
                current_section = text.strip()
                continue

            page_paragraphs.append(text)

        # Paragraph grouping
        grouped = []
        current_group = []
        word_count = 0

        for para in page_paragraphs:
            wc = len(para.split())
            if para in seen_texts or wc < 10:
                continue
            seen_texts.add(para)

            current_group.append(para)
            word_count += wc

            if word_count >= 300:
                grouped.append(" ".join(current_group))
                current_group = []
                word_count = 0

        if current_group:
            grouped.append(" ".join(current_group))

        for para_group in grouped:
            eqs = []
            if "=" in para_group or any(w in para_group for w in ["∇", "∂", "→", "∫", "Σ", "π", "λ"]):
                eqs.append(para_group)

            chunks.append({
                "text": para_group,
                "page": page_num,
                "source": os.path.basename(filepath),
                "section": current_section,
                "type": "paragraph-group",
                "images": images,
                "equations": eqs,
                "mode": "page-paragraph"
            })

    doc.close()
    return chunks



def stitch_by_section(texts, metadata):
    from collections import defaultdict
    grouped = defaultdict(list)

    for text, meta in zip(texts, metadata):
        key = meta.get("section", "Unknown")
        grouped[key].append((text, meta))

    stitched_texts = []
    stitched_metadata = []

    for section, chunks in grouped.items():
        combined_text = "\n\n".join([chunk[0] for chunk in chunks])
        base_meta = chunks[0][1].copy()
        base_meta["stitched_chunks"] = len(chunks)
        base_meta["type"] = "stitched"
        stitched_texts.append(combined_text)
        stitched_metadata.append(base_meta)

    return stitched_texts, stitched_metadata


def build_index():
    if os.path.exists(VECTOR_DB_PATH):
        os.remove(VECTOR_DB_PATH)
        print("🔁 Old vector index deleted.")

    all_chunks, metadata = [], []
    toc_titles = None

    # ✅ Mapping for page offset by file
    start_page_offset = {
        "Jeremic_et_al_CompMech_LectureNotes-1.pdf": 1,
        "Jeremic_et_al_CompMech_LectureNotes-2.pdf": 301,
        "Jeremic_et_al_CompMech_LectureNotes-3.pdf": 601,
        "Jeremic_et_al_CompMech_LectureNotes-4.pdf": 901,
        "Jeremic_et_al_CompMech_LectureNotes-5.pdf": 1201,
        "Jeremic_et_al_CompMech_LectureNotes-6.pdf": 1501,
        "Jeremic_et_al_CompMech_LectureNotes-7.pdf": 1801,
        "Jeremic_et_al_CompMech_LectureNotes-8.pdf": 2101,
        "Jeremic_et_al_CompMech_LectureNotes-9.pdf": 2401,
        "Jeremic_et_al_CompMech_LectureNotes-10.pdf": 2701,
        "Jeremic_et_al_CompMech_LectureNotes-11.pdf": 3001
    }

    for i, file in enumerate(sorted(os.listdir("data/raw"))):
        if not file.endswith(".pdf"):
            continue

        path = os.path.join("data/raw", file)

        if toc_titles is None and "LectureNotes-1.pdf" in file:
            from ingest.toc_parser import parse_toc_file
            toc_titles = parse_toc_file("./data/CompMechanicsLectureNotesTOC.toc")
            with open(TOC_CACHE_PATH, "wb") as f:
                pickle.dump(toc_titles, f)
            print(f"📘 TOC parsed with {len(toc_titles)} entries.")
        elif toc_titles is None:
            with open(TOC_CACHE_PATH, "rb") as f:
                toc_titles = pickle.load(f)
            print(f"📘 TOC loaded from cache with {len(toc_titles)} entries.")

        # 🛠️ Filter TOC entries to match current file's local page range
        doc = fitz.open(path)
        page_count = doc.page_count
        doc.close()

        filtered_toc = [entry for entry in toc_titles if 0 <= entry["page"] < page_count]

        try:
            sections = extract_structured_sections(path, filtered_toc)
        except Exception as e:
            print(f"⚠️ Error processing {file}: {e}")
            continue

        offset = start_page_offset.get(file, 0)

        for i, section in enumerate(sections):
            local_page = section.get("page", 0)
            global_page = offset + local_page

            section_number = next((entry["number"] for entry in toc_titles if entry["title"] == section["section"]), "Unknown")
            metadata.append({
                "chunk_id": f"{file}-p{section['page']}-c{i + 1}",
                "page": global_page,
                "source": section["source"],
                "section": section["section"],
                "section_number": section_number,
                "type": section["type"],
                "images": section["images"],
                "equations": section["equations"],
                "mode": section["mode"]
            })
            all_chunks.append(section["text"])

    if not all_chunks:
        print("⚠️ No valid chunks extracted. Index not created.")
        return

    all_chunks, metadata = stitch_by_section(all_chunks, metadata)
    vectors = embed_chunks(all_chunks)

    vs = VectorStore(dim=vectors.shape[1])
    vs.add(vectors, all_chunks, metadata)

    os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
    with open(VECTOR_DB_PATH, "wb") as f:
        pickle.dump(vs, f)

    print(f"✅ Index built with {len(all_chunks)} stitched sections.")