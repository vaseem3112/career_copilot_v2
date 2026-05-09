import os


def extract_text(filepath: str, file_type: str) -> str:
    """
    Extract raw text from PDF or DOC/DOCX file.
    Returns cleaned plain text.
    """
    ext = file_type.lower().lstrip(".")

    if ext == "pdf":
        return _extract_pdf(filepath)
    elif ext in ("doc", "docx"):
        return _extract_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(filepath: str) -> str:
    try:
        import fitz  # PyMuPDF
        doc  = fitz.open(filepath)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return _clean(text)
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install PyMuPDF")
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {e}")


def _extract_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc   = Document(filepath)
        lines = [p.text for p in doc.paragraphs if p.text.strip()]
        return _clean("\n".join(lines))
    except ImportError:
        raise RuntimeError("python-docx not installed. Run: pip install python-docx")
    except Exception as e:
        raise RuntimeError(f"DOCX extraction failed: {e}")


def _clean(text: str) -> str:
    import re
    # Remove excessive whitespace while preserving structure
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()
