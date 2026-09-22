"""
resume_parser.py - Resume Parsing Module for AI Resume Analyzer

Extracts text from PDF, DOCX, and TXT resume files, validates file type & size,
and performs basic section segmentation (Skills, Experience, Education, Projects).
"""

import os
import io
import re
from typing import Dict, Tuple, Optional
import pypdf
import docx

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

SECTION_PATTERNS = {
    'skills': re.compile(r'(?i)\b(skills|technical skills|expertise|technologies|proficiencies)\b'),
    'experience': re.compile(r'(?i)\b(experience|work experience|employment history|work history|internships)\b'),
    'education': re.compile(r'(?i)\b(education|academic background|qualifications|academic history)\b'),
    'projects': re.compile(r'(?i)\b(projects|key projects|academic projects|portfolio)\b'),
    'certifications': re.compile(r'(?i)\b(certifications|certificates|licenses|courses)\b')
}


def validate_file(file_obj, filename: str) -> Tuple[bool, str]:
    """
    Validate uploaded resume file size and extension.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.pdf', '.docx', '.txt']:
        return False, f"Unsupported file format '{ext}'. Only PDF, DOCX, and TXT are supported."

    # Check size
    if hasattr(file_obj, 'size'):
        size = file_obj.size
    elif isinstance(file_obj, (bytes, bytearray)):
        size = len(file_obj)
    elif hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell'):
        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
    elif isinstance(file_obj, str) and os.path.exists(file_obj):
        size = os.path.getsize(file_obj)
    else:
        size = 0

    if size > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({size / (1024*1024):.2f} MB) exceeds maximum allowed limit of {MAX_FILE_SIZE_MB} MB."

    return True, "File is valid."


def extract_text_from_pdf(file_input) -> str:
    """Extract text content page-by-page from a PDF file or stream."""
    text_content = []
    try:
        if isinstance(file_input, (str, os.PathLike)):
            reader = pypdf.PdfReader(file_input)
        else:
            if hasattr(file_input, 'read'):
                file_bytes = file_input.read()
                if hasattr(file_input, 'seek'):
                    file_input.seek(0)
            else:
                file_bytes = file_input
            stream = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(stream)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF file: {str(e)}")

    return "\n".join(text_content)


def extract_text_from_docx(file_input) -> str:
    """Extract text from DOCX paragraph by paragraph and tables."""
    text_content = []
    try:
        if isinstance(file_input, (str, os.PathLike)):
            doc = docx.Document(file_input)
        else:
            if hasattr(file_input, 'read'):
                file_bytes = file_input.read()
                if hasattr(file_input, 'seek'):
                    file_input.seek(0)
            else:
                file_bytes = file_input
            stream = io.BytesIO(file_bytes)
            doc = docx.Document(stream)

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text.strip())

        for table in doc.tables:
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_data:
                    text_content.append(" | ".join(row_data))
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX file: {str(e)}")

    return "\n".join(text_content)


def extract_text_from_txt(file_input) -> str:
    """Extract text from a TXT file or stream."""
    try:
        if isinstance(file_input, (str, os.PathLike)):
            with open(file_input, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            if hasattr(file_input, 'read'):
                content = file_input.read()
                if hasattr(file_input, 'seek'):
                    file_input.seek(0)
                if isinstance(content, bytes):
                    return content.decode('utf-8', errors='ignore')
                return str(content)
            elif isinstance(file_input, bytes):
                return file_input.decode('utf-8', errors='ignore')
    except Exception as e:
        raise ValueError(f"Failed to parse TXT file: {str(e)}")

    return ""


def parse_resume(file_input, filename: str) -> Dict[str, str]:
    """
    Main entry point for parsing resume files.
    Returns dictionary with raw_text, filename, character_count, word_count, sections.
    """
    valid, msg = validate_file(file_input, filename)
    if not valid:
        raise ValueError(msg)

    ext = os.path.splitext(filename)[1].lower()
    if ext == '.pdf':
        raw_text = extract_text_from_pdf(file_input)
    elif ext == '.docx':
        raw_text = extract_text_from_docx(file_input)
    elif ext == '.txt':
        raw_text = extract_text_from_txt(file_input)
    else:
        raise ValueError(f"Unsupported extension: {ext}")

    sections = extract_sections(raw_text)

    return {
        'filename': filename,
        'file_type': ext,
        'raw_text': raw_text,
        'char_count': len(raw_text),
        'word_count': len(raw_text.split()),
        'sections': sections
    }


def extract_sections(text: str) -> Dict[str, str]:
    """
    Segment resume text into standard sections based on heading patterns.
    """
    lines = text.split('\n')
    sections = {'header': [], 'skills': [], 'experience': [], 'education': [], 'projects': [], 'certifications': []}
    current_section = 'header'

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if line looks like a section header (short length, matches pattern)
        if len(stripped) < 40:
            matched_section = None
            for sec_name, pattern in SECTION_PATTERNS.items():
                if pattern.search(stripped):
                    matched_section = sec_name
                    break
            if matched_section:
                current_section = matched_section
                continue

        sections[current_section].append(stripped)

    return {k: "\n".join(v) for k, v in sections.items() if v}


if __name__ == "__main__":
    test_text = "John Doe\nSoftware Developer\nSKILLS\nPython, SQL, C++, React\nEXPERIENCE\nWorked at Tech Corp\nEDUCATION\nBS CS"
    sec = extract_sections(test_text)
    print("Parsed Sections:", list(sec.keys()))
