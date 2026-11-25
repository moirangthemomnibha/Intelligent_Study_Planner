import io
from pathlib import Path

from pypdf import PdfReader
from docx import Document
from pptx import Presentation


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt",
    ".md",
}


MAX_FILE_SIZE = 15 * 1024 * 1024


def extract_document_text(
    filename: str,
    file_bytes: bytes,
) -> dict:

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported document format.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds 15 MB.")

    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    text = ""

    if extension == ".pdf":
        reader = PdfReader(io.BytesIO(file_bytes))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif extension == ".docx":
        document = Document(io.BytesIO(file_bytes))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
        ]

        text = "\n".join(paragraphs)

    elif extension == ".pptx":
        presentation = Presentation(io.BytesIO(file_bytes))

        slides = []

        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    slides.append(shape.text)

        text = "\n".join(slides)

    elif extension in {".txt", ".md"}:
        text = file_bytes.decode("utf-8-sig")

    if not text.strip():
        raise ValueError("No readable text found in document.")

    return {
        "filename": filename,
        "extension": extension,
        "text": text,
        "characters": len(text),
    }