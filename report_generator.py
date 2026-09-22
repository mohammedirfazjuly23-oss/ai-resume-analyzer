"""
report_generator.py - Report Generation Module for AI Resume Analyzer

Generates detailed Markdown and PDF analysis reports containing match scores,
extracted skills, skill gaps, and learning roadmaps.
"""

import os
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_markdown_report(candidate_name: str, target_role_data: Dict[str, Any], top_recommendations: list, found_skills: list, roadmap_data: Dict[str, Any]) -> str:
    """Generate Markdown format analysis report."""
    md = []
    md.append(f"# AI Resume Analysis Report")
    md.append(f"**Candidate / File:** {candidate_name}")
    md.append(f"**Target Role:** {target_role_data['role']}")
    md.append(f"**Overall Match Score:** {target_role_data['match_score']}%\n")

    md.append("---")
    md.append("## 1. Score Breakdown")
    md.append(f"- **TF-IDF Semantic Similarity Score:** {target_role_data['tfidf_score']}%")
    md.append(f"- **Direct Skill Overlap Score:** {target_role_data['skill_overlap_score']}%\n")

    md.append("---")
    md.append("## 2. Extracted Technical Skills")
    if found_skills:
        md.append(", ".join(found_skills) + "\n")
    else:
        md.append("No technical skills detected.\n")

    md.append("---")
    md.append("## 3. Skill Gap Analysis for " + target_role_data['role'])
    md.append("### Skills Present:")
    if target_role_data['matched_required']:
        md.append("- **Required:** " + ", ".join(target_role_data['matched_required']))
    if target_role_data['matched_optional']:
        md.append("- **Optional:** " + ", ".join(target_role_data['matched_optional']))

    md.append("\n### Missing Skills to Learn:")
    if target_role_data['missing_required']:
        md.append("- **Required:** " + ", ".join(target_role_data['missing_required']))
    if target_role_data['missing_optional']:
        md.append("- **Optional:** " + ", ".join(target_role_data['missing_optional']))
    if not target_role_data['missing_required'] and not target_role_data['missing_optional']:
        md.append("None! You meet all listed requirements.")

    md.append("\n---")
    md.append("## 4. Top Recommended Job Roles")
    for idx, rec in enumerate(top_recommendations, 1):
        md.append(f"{idx}. **{rec['role']}** ({rec['category']}) - **{rec['match_score']}% Match**")

    md.append("\n---")
    md.append("## 5. Learning Roadmap")
    for week in roadmap_data.get('weeks', []):
        md.append(f"### {week['title']}")
        md.append(f"- **Objective:** {week['objective']}")
        md.append(f"- **Key Concepts:** {', '.join(week['key_concepts'])}")
        md.append(f"- **Suggested Project:** {week['project_idea']}\n")

    md.append("---")
    md.append("> *Disclaimer: Match scores are automated estimates for guidance only and do not guarantee hiring outcomes.*")

    return "\n".join(md)


def generate_pdf_report(candidate_name: str, target_role_data: Dict[str, Any], top_recommendations: list, found_skills: list, roadmap_data: Dict[str, Any], output_filename: str = None) -> str:
    """Generate PDF format analysis report using ReportLab."""
    if not output_filename:
        safe_name = candidate_name.replace(" ", "_").replace(".", "_")
        output_filename = os.path.join(REPORTS_DIR, f"resume_analysis_{safe_name}.pdf")

    doc = SimpleDocTemplate(output_filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor("#1E3A8A"))
    heading2 = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor("#1E3A8A"))
    heading3 = ParagraphStyle('Heading3', parent=styles['Heading3'], fontSize=11, leading=14, textColor=colors.HexColor("#2563EB"))
    body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9.5, leading=13)
    bullet = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=9, leading=12, leftIndent=15)
    disclaimer = ParagraphStyle('Disclaimer', parent=styles['Italic'], fontSize=8, leading=10, textColor=colors.gray)

    story = []

    # Title Banner
    story.append(Paragraph("AI Resume Analysis Report", title_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceAfter=12))

    # Meta Table
    meta_data = [
        [Paragraph(f"<b>Candidate / File:</b> {candidate_name}", body), Paragraph(f"<b>Target Role:</b> {target_role_data['role']}", body)],
        [Paragraph(f"<b>Overall Match Score:</b> <font color='#166534'><b>{target_role_data['match_score']}%</b></font>", body), Paragraph(f"<b>TF-IDF Score:</b> {target_role_data['tfidf_score']}% | <b>Skill Overlap:</b> {target_role_data['skill_overlap_score']}%", body)]
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # Section 1: Detected Skills
    story.append(Paragraph("1. Extracted Technical Skills", heading2))
    story.append(Spacer(1, 4))
    skills_text = ", ".join(found_skills) if found_skills else "No technical skills detected."
    story.append(Paragraph(skills_text, body))
    story.append(Spacer(1, 12))

    # Section 2: Skill Gap Analysis
    story.append(Paragraph(f"2. Skill Gap Analysis for {target_role_data['role']}", heading2))
    story.append(Spacer(1, 4))
    
    gap_data = [
        [Paragraph("<b>Status</b>", heading3), Paragraph("<b>Skills</b>", heading3)],
        [Paragraph("<font color='#166534'><b>Matched Required</b></font>", body), Paragraph(", ".join(target_role_data['matched_required']) or "None", body)],
        [Paragraph("<font color='#991B1B'><b>Missing Required</b></font>", body), Paragraph(", ".join(target_role_data['missing_required']) or "None", body)],
        [Paragraph("<font color='#1E40AF'><b>Matched Optional</b></font>", body), Paragraph(", ".join(target_role_data['matched_optional']) or "None", body)],
        [Paragraph("<font color='#854D0E'><b>Missing Optional</b></font>", body), Paragraph(", ".join(target_role_data['missing_optional']) or "None", body)],
    ]
    t_gap = Table(gap_data, colWidths=[140, 400])
    t_gap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_gap)
    story.append(Spacer(1, 14))

    # Section 3: Top Recommended Roles
    story.append(Paragraph("3. Top Recommended Job Roles", heading2))
    story.append(Spacer(1, 4))
    rec_rows = [[Paragraph("<b>Rank</b>", heading3), Paragraph("<b>Job Role</b>", heading3), Paragraph("<b>Category</b>", heading3), Paragraph("<b>Match Score</b>", heading3)]]
    for idx, rec in enumerate(top_recommendations, 1):
        rec_rows.append([
            Paragraph(str(idx), body),
            Paragraph(rec['role'], body),
            Paragraph(rec['category'], body),
            Paragraph(f"<b>{rec['match_score']}%</b>", body)
        ])
    t_rec = Table(rec_rows, colWidths=[40, 200, 180, 120])
    t_rec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_rec)
    story.append(Spacer(1, 14))

    # Section 4: Learning Roadmap
    story.append(Paragraph("4. Recommended Learning Roadmap", heading2))
    story.append(Spacer(1, 4))
    for week in roadmap_data.get('weeks', []):
        story.append(Paragraph(f"<b>{week['title']}</b>", heading3))
        story.append(Paragraph(f"• <b>Objective:</b> {week['objective']}", bullet))
        story.append(Paragraph(f"• <b>Key Concepts:</b> {', '.join(week['key_concepts'])}", bullet))
        story.append(Paragraph(f"• <b>Suggested Project:</b> {week['project_idea']}", bullet))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=6))
    story.append(Paragraph("Disclaimer: This AI analysis is intended solely for educational guidance and skill self-assessment. Scores do not guarantee recruitment outcomes.", disclaimer))

    doc.build(story)
    return output_filename


if __name__ == "__main__":
    target = {
        'role': 'Machine Learning Engineer',
        'match_score': 74.5,
        'tfidf_score': 68.0,
        'skill_overlap_score': 80.0,
        'matched_required': ['Python', 'scikit-learn'],
        'missing_required': ['FastAPI', 'Docker'],
        'matched_optional': ['SQL'],
        'missing_optional': ['MLflow']
    }
    recs = [
        {'role': 'Data Analyst', 'category': 'Data & Analytics', 'match_score': 86.0},
        {'role': 'Machine Learning Engineer', 'category': 'ML & AI', 'match_score': 74.5},
        {'role': 'Python Developer', 'category': 'Software Engineering', 'match_score': 69.0}
    ]
    skills = ['Python', 'SQL', 'Pandas', 'scikit-learn']
    rm = {
        'weeks': [
            {'week': 1, 'title': 'Week 1: Core Focus on FastAPI', 'objective': 'REST APIs', 'key_concepts': ['Endpoints'], 'project_idea': 'Build API'}
        ]
    }
    path = generate_pdf_report("Test_Candidate.pdf", target, recs, skills, rm)
    print("Generated PDF at:", path)
