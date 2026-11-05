"""Local text extraction for documents used by the assistant's document tools."""

import io
import zipfile
from pathlib import Path


MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
MAX_EXTRACTED_CHARACTERS = 12_000
TEXT_EXTENSIONS = {
    "txt", "md", "rst", "csv", "tsv", "json", "jsonl", "xml", "yaml",
    "yml", "toml", "ini", "log", "html", "htm", "py", "js", "ts", "css", "sql",
}


def extract_text_document(filename, raw):
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ValueError("Each uploaded file must be 10 MB or smaller.")
    suffix = Path(filename).suffix.lower().lstrip(".")

    if suffix == "pdf":
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError

        if not raw.startswith(b"%PDF-"):
            raise ValueError(f"{filename} is not a valid PDF file.")
        try:
            reader = PdfReader(io.BytesIO(raw))
            if reader.is_encrypted:
                raise ValueError(f"{filename} is encrypted; upload an unprotected PDF.")
            parts = []
            total = 0
            for page in reader.pages:
                text = page.extract_text() or ""
                parts.append(text[: max(0, MAX_EXTRACTED_CHARACTERS - total)])
                total += len(parts[-1])
                if total >= MAX_EXTRACTED_CHARACTERS:
                    break
        except (OSError, ValueError, PdfReadError) as error:
            raise ValueError(f"Could not read {filename}: {error}") from error
        extracted = "\n".join(parts).strip()
        if not extracted:
            raise ValueError(
                f"No selectable text was found in {filename}. Scanned PDFs need OCR and are not supported yet."
            )
        return extracted

    if suffix == "docx":
        from docx import Document
        from docx.opc.exceptions import PackageNotFoundError

        try:
            document = Document(io.BytesIO(raw))
        except (OSError, ValueError, zipfile.BadZipFile, PackageNotFoundError) as error:
            raise ValueError(f"Could not read {filename}: {error}") from error
        text_parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
        text_parts.extend(
            " | ".join(cell.text for cell in row.cells)
            for table in document.tables
            for row in table.rows
        )
        extracted = "\n".join(text_parts).strip()
        if not extracted:
            raise ValueError(f"No text was found in {filename}.")
        return extracted[:MAX_EXTRACTED_CHARACTERS]

    if suffix in TEXT_EXTENSIONS:
        try:
            return raw.decode("utf-8-sig")[:MAX_EXTRACTED_CHARACTERS]
        except UnicodeDecodeError as error:
            raise ValueError(f"{filename} is not valid UTF-8 text.") from error

    return (
        f"[Attached {Path(filename).name} ({len(raw):,} bytes). This file type can be uploaded, "
        "but this tool does not extract its contents.]"
    )
