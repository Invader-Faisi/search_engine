from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
import os
from flask import current_app
from app.services.file_service import extract_text   # ✅ IMPORTANT


def get_schema():
    return Schema(
        title=ID(stored=True),
        path=ID(stored=True),
        content=TEXT(stored=True)
    )


def create_index():
    index_dir = current_app.config['WHOOSH_INDEX']

    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
        ix = create_in(index_dir, get_schema())
    else:
        try:
            ix = open_dir(index_dir)
        except:
            ix = create_in(index_dir, get_schema())

    return ix


def index_document(filename, filepath):
    ix = create_index()
    writer = ix.writer()

    # 🔥 FIX: Convert relative → correct full path
    full_path = os.path.join(current_app.root_path, "..", filepath)
    full_path = os.path.normpath(full_path)

    print(f"[DEBUG] Reading file: {full_path}")

    # 🔥 FIX: Use extractor instead of open()
    content = extract_text(full_path)

    print(f"[DEBUG] Extracted length: {len(content)}")

    if not content.strip():
        print(f"[WARNING] No content extracted from {filename}")
        writer.cancel()
        return

    writer.add_document(
        title=filename,
        path=filepath,
        content=content
    )

    writer.commit()

    print(f"[INFO] Indexed successfully: {filename}")