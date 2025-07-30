import csv

# Input: path to your raw TOC text file (copied from the Google Doc)
input_file = "jeremic_toc_raw.txt"
output_file = "jeremic_toc_parsed.csv"

# Optional: use this if you're reading directly from a Google Doc via `gdown` or Google API
# Otherwise, just save the doc as .txt and load from disk

def parse_line(line):
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 3:
        return None
    section, title, page = parts
    return section, title, page

def process_toc_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Section Number", "Title", "Page Number"])  # CSV header

        for line in lines:
            if not line.strip():
                continue
            parsed = parse_line(line)
            if parsed:
                writer.writerow(parsed)

    print(f"✅ CSV file written to: {output_path}")

# Run it
process_toc_file(input_file, output_file)
