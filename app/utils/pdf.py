import fitz


def extract_text_from_pdf(file_path: str) -> str:
    document = fitz.open(file_path)

    try:
        text = ""

        for page in document:
            text += page.get_text()

        return text.strip()

    finally:
        document.close()