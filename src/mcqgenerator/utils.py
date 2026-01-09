import json
import traceback

# PyPDF2 is optional at import time; we handle its absence at runtime
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


def read_file(file):
    """Read text from an uploaded file-like object.

    Supports PDF (requires PyPDF2) and plain text files.
    Raises a clear exception when reading fails or when required packages are missing.
    """
    name = getattr(file, "name", "")
    if name.lower().endswith(".pdf"):
        if PyPDF2 is None:
            raise RuntimeError("PyPDF2 is not installed; please install dependencies to read PDF files")
        try:
            # Prefer the modern PdfReader API, fall back to PdfFileReader for older PyPDF2
            try:
                reader = PyPDF2.PdfReader(file)
                pages = reader.pages
            except AttributeError:
                reader = PyPDF2.PdfFileReader(file)
                pages = reader.pages

            text = ""
            for page in pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            raise RuntimeError("error reading the PDF file") from e

    elif name.lower().endswith(".txt"):
        try:
            content = file.read()
            if isinstance(content, bytes):
                return content.decode("utf-8")
            return content
        except Exception as e:
            raise RuntimeError("error reading the text file") from e

    else:
        raise ValueError("unsupported file format: only .pdf and .txt files supported")


def get_table_data(quiz_str):
    """Convert a quiz JSON string into a table-friendly list of dicts.

    Returns False on parse errors.
    """
    try:
        quiz_dict = json.loads(quiz_str)
    except json.JSONDecodeError as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False

    quiz_table_data = []
    for value in quiz_dict.values():
        mcq = value.get("mcq", "")
        options = " || ".join(
            [f"{opt}-> {val}" for opt, val in value.get("options", {}).items()]
        )
        correct = value.get("correct", "")
        quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})

    return quiz_table_data


