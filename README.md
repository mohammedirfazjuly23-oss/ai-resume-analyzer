# AI Resume Analyzer & Job Recommendation System 📄🚀

An NLP-powered application built with Python and Streamlit that helps students and job seekers evaluate how well their resumes match industry job roles, identify missing skills, and generate tailored 4-week learning roadmaps.

---

## 📌 Features

- **Multi-Format Resume Parsing:** Supports PDF (`pypdf`), DOCX (`python-docx`), and plain text TXT files with file format and size validation (<10 MB).
- **Syntax-Preserving Text Normalization:** Preserves critical technical symbols and names such as `C++`, `C#`, `.NET`, `Node.js`, `Vue.js`, `CI/CD`, and `PL/SQL`.
- **Boundary-Aware Skill Extraction:** Uses a controlled skill dictionary (`data/skill_dictionary.csv`) with alias lookup and regex word-boundary matching to categorize skills (Programming, ML/AI, Web/Backend, Databases, Cloud/DevOps, Data/Tools).
- **Hybrid Matching Engine:** Combines **TF-IDF Cosine Similarity** (text semantics) and **Direct Skill Overlap Ratio** (required vs optional skills) to rank suitable job roles.
- **Skill-Gap Analysis:** Identifies present skills, missing required skills, and missing optional skills for a selected target job role.
- **Personalized 4-Week Learning Roadmap:** Generates an action-oriented weekly learning plan with key concepts, practice tasks, and project ideas.
- **Downloadable Analysis Reports:** Export comprehensive PDF and Markdown reports.
- **Responsible AI Safeguards:** Excludes protected personal information (age, gender, ethnicity, photo) from score calculations and includes AI transparency disclaimers.

---

## 🏗️ System Architecture & Workflow

```
                   +------------------------+
                   |  Upload PDF/DOCX/TXT   |
                   +-----------+------------+
                               |
                               v
                   +------------------------+
                   |  Resume Parsing & Text |
                   |  Normalization Module  |
                   +-----------+------------+
                               |
                               v
                   +------------------------+
                   |  Skill Extraction Engine|
                   | (Boundary Regex Match) |
                   +-----------+------------+
                               |
                               v
                   +------------------------+
                   |   Job Role Matching    |
                   | (TF-IDF + Cosine Sim)  |
                   +-----------+------------+
                               |
                               v
                   +------------------------+
                   |   Skill Gap Analysis   |
                   |  & Roadmap Generation  |
                   +-----------+------------+
                               |
                               v
                   +------------------------+
                   |   Streamlit Interactive|
                   | Dashboard & PDF Export |
                   +------------------------+
```

---

## 📁 Suggested Folder Structure

```
ai_resume_analyzer/
├── app.py                      # Main Streamlit web application
├── resume_parser.py            # PDF, DOCX, TXT parser & section splitter
├── text_cleaner.py             # Normalization preserving C++, .NET, etc.
├── skill_extractor.py          # Boundary-aware skill extraction engine
├── job_matcher.py              # TF-IDF vectorizer & cosine similarity matcher
├── roadmap_generator.py        # 4-week weekly learning roadmap generator
├── report_generator.py         # Markdown and PDF report builder
├── generate_sample_resumes.py  # Utility to create benchmark sample resumes
├── requirements.txt            # Project Python dependencies
├── pytest.ini                  # Pytest configuration
├── README.md                   # Project documentation & sitemap
├── .env                        # Environment settings
├── .gitignore                  # Git ignore rules
├── data/
│   ├── job_roles.csv           # Job role definitions & skill requirements
│   └── skill_dictionary.csv    # Skill master dictionary & aliases
├── sample_resumes/             # Pre-built benchmark sample resumes
├── reports/                    # Generated PDF reports output folder
└── tests/
    ├── test_cases.csv          # Evaluation criteria & benchmark sheet
    └── test_analyzer.py        # Pytest test suite
```

---

## ⚡ Quick Start & Installation

### 1. Clone or Navigate to Directory
```bash
cd "e:/New folder (2)"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
pytest tests/test_analyzer.py -v
```

### 4. Launch Streamlit Web Application
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser to use the application.

---

## ⚖️ Responsible AI Guidelines

1. **Guidance, Not Automation:** This system is an educational tool designed to assist candidates with self-assessment and skill improvement. Scores are estimates and do not represent recruiter decisions.
2. **Protected Attributes:** Age, gender, nationality, marital status, disability, and photographs are explicitly ignored during evaluation.
3. **Privacy Protection:** Uploaded resumes are processed in-memory and temporary files are deleted after session completion.

---

## 🎓 Viva Voce Questions & Answers

- **Q1: How do you extract text from PDF and DOCX files?**  
  *Answer:* We use `pypdf` for page-by-page PDF text extraction and `python-docx` for extracting paragraphs and table contents from DOCX files.

- **Q2: What is TF-IDF?**  
  *Answer:* Term Frequency-Inverse Document Frequency evaluates word importance within a document relative to a corpus. In our system, TF-IDF vectorizes resume text and job descriptions.

- **Q3: What does Cosine Similarity measure?**  
  *Answer:* Cosine similarity measures the angle between two TF-IDF feature vectors, yielding a score between 0 and 1 indicating textual and contextual similarity.

- **Q4: Why can simple keyword matching fail?**  
  *Answer:* Keyword matching can fail due to synonym variations (e.g. `Postgres` vs `PostgreSQL`), sub-word collisions (e.g. `C` matching inside `C++`), or special character stripping (e.g. `.NET`). We solve this with alias mapping and boundary regex rules.
