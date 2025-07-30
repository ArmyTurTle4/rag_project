# utils/saver.py
import os

def save_to_downloads(filename: str, content: str):
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    full_path = os.path.join(downloads, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Saved] File saved to: {"C:/Users/grant/Downloads"}")
