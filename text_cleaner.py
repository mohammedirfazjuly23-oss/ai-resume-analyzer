"""
text_cleaner.py - Text Cleaning and Normalization Module for AI Resume Analyzer

This module handles text normalization while explicitly preserving technical terms
and symbols like C++, C#, .NET, Node.js, Vue.js, CI/CD, PL/SQL, etc.
"""

import re

# Technical terms that contain special characters that should NOT be stripped
PRESERVED_TERMS = {
    'c++': 'cplusplus_token',
    'c#': 'csharp_token',
    '.net': 'dotnet_token',
    'node.js': 'nodejs_token',
    'vue.js': 'vuejs_token',
    'react.js': 'reactjs_token',
    'ci/cd': 'cicd_token',
    'pl/sql': 'plsql_token',
    'rest/restful': 'rest_token',
    'scikit-learn': 'scikitlearn_token',
    'hugging face': 'huggingface_token',
    'power bi': 'powerbi_token'
}

REVERSE_PRESERVED_TERMS = {v: k for k, v in PRESERVED_TERMS.items()}


def clean_text(text: str, lowercase: bool = True) -> str:
    """
    Clean and normalize unstructured text from resumes or job descriptions.
    
    Args:
        text (str): Input raw text.
        lowercase (bool): Whether to convert text to lowercase.
        
    Returns:
        str: Cleaned and normalized text.
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = text
    
    # 1. Normalize line endings and whitespace
    cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)

    if lowercase:
        cleaned = cleaned.lower()

    # 2. Temporarily protect special technical tokens
    # Note: sort keys by length descending so multi-word tokens replace first
    sorted_preserved = sorted(PRESERVED_TERMS.keys(), key=len, reverse=True)
    for term in sorted_preserved:
        token = PRESERVED_TERMS[term]
        pattern = re.compile(r'\b' + re.escape(term) + r'\b' if term[0].isalnum() else re.escape(term), re.IGNORECASE)
        cleaned = pattern.sub(f" {token} ", cleaned)

    # 3. Remove unwanted non-alphanumeric characters, keeping spaces, hyphens, pluses for tokens
    # Keep characters: letters, numbers, spaces, and protected tokens
    cleaned = re.sub(r'[^\w\s\-\+\#\.]', ' ', cleaned)

    # 4. Collapse repeated spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # 5. Restore protected technical terms to readable format
    for token, original in REVERSE_PRESERVED_TERMS.items():
        cleaned = cleaned.replace(token, original)

    return cleaned


def extract_clean_words(text: str) -> list[str]:
    """
    Extract clean tokenized word list from text.
    """
    cleaned = clean_text(text, lowercase=True)
    return cleaned.split()


if __name__ == "__main__":
    sample = "Experienced in C++, C#, .NET development, Node.js, and CI/CD pipelines! Worked with PL/SQL & scikit-learn."
    print("Original:", sample)
    print("Cleaned :", clean_text(sample))
