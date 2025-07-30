###
### THIS IS NO LONGER  NEEDED. ALL FUNCTIONALITY NOW IN PREPROCESS_PIPELINE ###
###

import fitz  # PyMuPDF
import os

def extract_pdf_sections(file_path):
    doc = fitz.open(file_path)
    chunks = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        images = [
            {"ext": img[1], "xref": img[0]}
            for img in page.get_images(full=True)
        ]

        for i, block in enumerate(blocks):
            if "lines" not in block:
                continue

            text = ""
            max_font_size = 0
            fonts = set()
            for line in block["lines"]:
                for span in line["spans"]:
                    span_text = span["text"].strip()
                    if not span_text:
                        continue
                    text += span_text + " "
                    max_font_size = max(max_font_size, span["size"])
                    fonts.add(span["font"].lower())

            text = text.strip()
            if len(text) < 50:
                continue  # Skip tiny or noisy blocks

            # Basic heuristics
            is_bold = any("bold" in font for font in fonts)
            is_heading = max_font_size >= 13 or is_bold  # You can adjust threshold

            chunks.append({
                "text": text,
                "page": page_num,
                "source": os.path.basename(filepath),
                "font_size": max_font_size,
                "is_bold": is_bold,
                "type": "heading" if is_heading else "paragraph"
            })

            return chunks

            page = doc.load_page(page_num)
            text = page.get_text("text")
            images = []

            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                images.append({
                    "ext": image_ext,
                    "xref": xref
                })

            pages.append({
                "text": text if text.strip() else "[No text extracted]",
                "page": page_num + 1,
                "images": images,
                "source": file_path
            })
        except Exception as e:
            print(f"[!] Skipping page {page_num + 1} due to error: {e}")
            pages.append({
                "text": "[Error extracting text]",
                "page": page_num + 1,
                "images": [],
                "source": file_path,
                "error": str(e)
            })

    doc.close()
    return pages
