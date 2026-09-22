"""
test_analyzer.py - Unit and Integration Tests for AI Resume Analyzer Pipeline
"""

import os
import pytest
from text_cleaner import clean_text
from resume_parser import parse_resume, validate_file
from skill_extractor import SkillExtractor
from job_matcher import JobMatcher
from roadmap_generator import generate_roadmap

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sample_resumes')


def test_text_cleaner_preserves_symbols():
    """Verify special technical symbols like C++, C#, .NET, Node.js are preserved."""
    raw = "Proficient in C++, C#, .NET framework, Node.js, and CI/CD tools!"
    cleaned = clean_text(raw)
    assert 'c++' in cleaned
    assert 'c#' in cleaned
    assert '.net' in cleaned
    assert 'node.js' in cleaned
    assert 'ci/cd' in cleaned


def test_resume_parser_txt():
    """Test parsing plain text resume."""
    txt_path = os.path.join(SAMPLE_DIR, 'sample_resume_data_analyst.txt')
    assert os.path.exists(txt_path)
    parsed = parse_resume(txt_path, 'sample_resume_data_analyst.txt')
    assert parsed['file_type'] == '.txt'
    assert 'Python' in parsed['raw_text']
    assert 'skills' in parsed['sections']


def test_resume_parser_docx():
    """Test parsing DOCX resume."""
    docx_path = os.path.join(SAMPLE_DIR, 'sample_resume_ml_engineer.docx')
    assert os.path.exists(docx_path)
    parsed = parse_resume(docx_path, 'sample_resume_ml_engineer.docx')
    assert parsed['file_type'] == '.docx'
    assert 'scikit-learn' in parsed['raw_text']


def test_resume_parser_pdf():
    """Test parsing PDF resume."""
    pdf_path = os.path.join(SAMPLE_DIR, 'sample_resume_nlp_engineer.pdf')
    assert os.path.exists(pdf_path)
    parsed = parse_resume(pdf_path, 'sample_resume_nlp_engineer.pdf')
    assert parsed['file_type'] == '.pdf'
    assert 'Hugging Face' in parsed['raw_text'] or 'Transformers' in parsed['raw_text']


def test_skill_extractor():
    """Test boundary-aware skill extraction and categorization."""
    extractor = SkillExtractor()
    sample_text = "Experienced with Python, SQL, C++, Docker, PyTorch, and Power BI."
    res = extractor.extract_skills(sample_text)
    
    assert 'Python' in res['found_skills']
    assert 'SQL' in res['found_skills']
    assert 'C++' in res['found_skills']
    assert 'Docker' in res['found_skills']
    assert 'PyTorch' in res['found_skills']
    assert 'Power BI' in res['found_skills']
    assert 'c' not in [s.lower() for s in res['found_skills']]  # Ensure 'c' is not mistakenly matched from 'C++'


def test_job_matcher_ranking():
    """Test top role recommendation logic."""
    matcher = JobMatcher()
    
    # 1. Test Data Analyst profile
    da_text = "Proficient in Python, SQL, Excel, Pandas, Power BI, and Tableau for data analytics."
    da_res = matcher.match_resume(da_text)
    top_role = da_res['top_3_recommendations'][0]['role']
    assert top_role == 'Data Analyst'

    # 2. Test NLP Engineer profile
    nlp_text = "Experienced in Python, NLP, Transformers, Hugging Face, spaCy, PyTorch, and BERT."
    nlp_res = matcher.match_resume(nlp_text)
    top_role_nlp = nlp_res['top_3_recommendations'][0]['role']
    assert top_role_nlp == 'NLP Engineer'


def test_roadmap_generator():
    """Test 4-week roadmap generation for missing skills."""
    roadmap = generate_roadmap("Machine Learning Engineer", ["FastAPI", "Docker"], ["MLflow"])
    assert len(roadmap['weeks']) == 4
    assert 'FastAPI' in roadmap['weeks'][0]['title'] or 'Docker' in roadmap['weeks'][0]['title']
