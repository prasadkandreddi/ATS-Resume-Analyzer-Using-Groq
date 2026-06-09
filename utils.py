from pypdf import PdfReader
from docx import Document


def extract_text(uploaded_file):

    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":

        reader = PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    elif file_type == "docx":

        doc = Document(uploaded_file)

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )

        return text

    elif file_type == "txt":

        return uploaded_file.read().decode("utf-8")

    return ""