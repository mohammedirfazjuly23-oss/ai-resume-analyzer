"""
app.py - High-Performance & Visually Enhanced Streamlit Application
for AI Resume Analyzer and Job Recommendation System

Run with: streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from resume_parser import parse_resume, validate_file
from skill_extractor import SkillExtractor
from job_matcher import JobMatcher
from roadmap_generator import generate_roadmap
from report_generator import generate_markdown_report, generate_pdf_report

# Page Configuration
st.set_page_config(
    page_title="AI Resume Analyzer & Career Advisor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Background & Padding */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 95%;
    }
    
    /* Header Gradient & Card */
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 1.8rem 2.2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25);
        margin-bottom: 1.8rem;
    }
    
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #E0E7FF;
        margin-top: 0.4rem;
        margin-bottom: 0;
        font-weight: 400;
    }
    
    /* Metric Cards */
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.06);
    }
    .stat-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 0.3rem;
    }
    
    /* Custom Skill Pill Badges */
    .skill-pill {
        display: inline-flex;
        align-items: center;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 500;
        margin: 3px 4px 4px 0px;
        transition: all 0.2s ease;
    }
    .skill-pill:hover {
        background-color: #DBEAFE;
    }
    
    .skill-pill-missing-req {
        display: inline-flex;
        align-items: center;
        background-color: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FCA5A5;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        margin: 3px 4px 4px 0px;
    }
    
    .skill-pill-missing-opt {
        display: inline-flex;
        align-items: center;
        background-color: #FFFBEB;
        color: #D97706;
        border: 1px solid #FDE68A;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 500;
        margin: 3px 4px 4px 0px;
    }
    
    /* Category Badges */
    .cat-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #334155;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Roadmap Week Card */
    .roadmap-card {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 2px solid #E2E8F0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-size: 0.95rem;
        font-weight: 600;
        color: #64748B;
        border-radius: 8px 8px 0 0;
        padding: 0 20px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #1E3A8A !important;
        border-bottom: 3px solid #1E3A8A !important;
        background-color: #F1F5F9;
    }

    .stDataFrame {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_components():
    """Cache core NLP engine components."""
    extractor = SkillExtractor()
    matcher = JobMatcher(skill_extractor=extractor)
    return extractor, matcher


extractor, matcher = load_components()


# --- SIDEBAR UI ---
st.sidebar.markdown("## ⚙️ Navigation & Input")
st.sidebar.markdown("---")

sample_resumes = {
    "None (Upload my own file)": None,
    "Sample 1: Data Analyst (TXT)": os.path.join("sample_resumes", "sample_resume_data_analyst.txt"),
    "Sample 2: ML Engineer (DOCX)": os.path.join("sample_resumes", "sample_resume_ml_engineer.docx"),
    "Sample 3: NLP Engineer (PDF)": os.path.join("sample_resumes", "sample_resume_nlp_engineer.pdf")
}

selected_sample = st.sidebar.selectbox("📂 Select Benchmark Sample:", list(sample_resumes.keys()))

uploaded_file = st.sidebar.file_uploader(
    "📤 Or Upload Resume File (PDF, DOCX, TXT):",
    type=["pdf", "docx", "txt"],
    help="Supports PDF, DOCX, and TXT up to 10 MB."
)

st.sidebar.markdown("---")

job_roles_list = matcher.jobs_df['role'].tolist()
target_role = st.sidebar.selectbox("🎯 Target Job Role:", job_roles_list, index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Matching Weight Controls")
tfidf_weight = st.sidebar.slider("Semantic Similarity (TF-IDF)", 0.0, 1.0, 0.45, 0.05)
skill_weight = 1.0 - tfidf_weight
st.sidebar.caption(f"Direct Skill Overlap Weight: **{skill_weight:.2f}**")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Adjusting the weights lets you emphasize keyword precision vs semantic text matching.")


# Active File Detection
active_file = None
active_filename = ""

if uploaded_file is not None:
    active_file = uploaded_file
    active_filename = uploaded_file.name
elif selected_sample and sample_resumes[selected_sample]:
    sample_path = sample_resumes[selected_sample]
    if os.path.exists(sample_path):
        active_file = sample_path
        active_filename = os.path.basename(sample_path)


# --- MAIN UI HEADER ---
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">AI Resume Analyzer & Job Recommendation System</h1>
    <p class="hero-subtitle">Instant match scoring, skill gap detection, and personalized 4-week learning roadmaps powered by NLP.</p>
</div>
""", unsafe_allow_html=True)


if not active_file:
    # Landing View when no file uploaded
    st.info("👈 **Get Started:** Upload a resume file (PDF, DOCX, TXT) or select one of the sample resumes from the left sidebar.")

    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size:2rem; margin-bottom:0.5rem;">📄</div>
            <div class="stat-label">Multi-Format Parsing</div>
            <p style="font-size:0.9rem; color:#475569; margin-top:0.5rem;">Extract text cleanly from PDF, DOCX, and TXT files while protecting technical symbols like C++, C#, .NET, and CI/CD.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_f2:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size:2rem; margin-bottom:0.5rem;">🎯</div>
            <div class="stat-label">Hybrid Matching Engine</div>
            <p style="font-size:0.9rem; color:#475569; margin-top:0.5rem;">Combines TF-IDF Vector Cosine Similarity and Direct Skill Overlap ratios to rank candidates against industry standards.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_f3:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size:2rem; margin-bottom:0.5rem;">🗺️</div>
            <div class="stat-label">Learning Roadmap</div>
            <p style="font-size:0.9rem; color:#475569; margin-top:0.5rem;">Generates a week-by-week action plan for missing skills with objectives, key concepts, and hands-on project ideas.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Benchmark Job Roles Available")
    
    roles_summary_df = matcher.jobs_df[['role', 'category', 'required_skills']].copy()
    roles_summary_df.columns = ['Job Role', 'Industry Category', 'Core Expected Skills']
    st.dataframe(roles_summary_df, use_container_width=True, hide_index=True)

else:
    with st.spinner("⚡ Running NLP Pipeline & Analyzing Resume..."):
        try:
            parsed_data = parse_resume(active_file, active_filename)
        except Exception as e:
            st.error(f"❌ Error parsing resume file: {str(e)}")
            st.stop()

        raw_text = parsed_data['raw_text']
        
        # Skill Extraction
        skill_res = extractor.extract_skills(raw_text)
        found_skills = skill_res['found_skills']

        # Job Matching
        match_results = matcher.match_resume(raw_text, found_skills)
        ranked_roles = match_results['ranked_roles']
        top_3 = match_results['top_3_recommendations']

        # Target Role Analysis
        target_data = matcher.get_role_analysis(target_role, raw_text, found_skills)

        # Roadmap Generation
        roadmap_data = generate_roadmap(target_role, target_data['missing_required'], target_data['missing_optional'])

    # --- TOP METRIC SUMMARY STRIP ---
    m_c1, m_c2, m_c3, m_c4, m_c5 = st.columns(5)

    score = target_data['match_score']
    score_color = "#166534" if score >= 75 else ("#854D0E" if score >= 55 else "#991B1B")
    match_status = "High Match" if score >= 75 else ("Moderate" if score >= 55 else "Skill Gap")

    with m_c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Candidate Resume</div>
            <div class="stat-value" style="font-size:1.2rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{active_filename}">{active_filename}</div>
        </div>
        """, unsafe_allow_html=True)

    with m_c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Target Role</div>
            <div class="stat-value" style="font-size:1.2rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{target_role}">{target_role}</div>
        </div>
        """, unsafe_allow_html=True)

    with m_c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Overall Match Score</div>
            <div class="stat-value" style="color:{score_color};">{score}%</div>
        </div>
        """, unsafe_allow_html=True)

    with m_c4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Match Category</div>
            <div class="stat-value" style="font-size:1.2rem; color:{score_color};">{match_status}</div>
        </div>
        """, unsafe_allow_html=True)

    with m_c5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Skills Detected</div>
            <div class="stat-value">{len(found_skills)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TAB NAVIGATION ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Match Score & Ranking",
        "🛠️ Extracted Skills & Sections",
        "🔍 Skill Gap Analysis",
        "🗺️ Learning Roadmap",
        "📥 Export Reports",
        "⚖️ Responsible AI & Viva Prep"
    ])

    # --- TAB 1: MATCH SCORE & RANKING ---
    with tab1:
        col_g1, col_g2 = st.columns([1.1, 1.9])

        with col_g1:
            st.markdown("### 🎯 Match Score Gauge")

            # High Quality Semi-Circle Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={'suffix': '%', 'font': {'size': 38, 'color': '#0F172A', 'family': 'Inter'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                    'bar': {'color': "#1E40AF", 'thickness': 0.3},
                    'bgcolor': "#F8FAFC",
                    'borderwidth': 1,
                    'bordercolor': "#E2E8F0",
                    'steps': [
                        {'range': [0, 45], 'color': "#FEE2E2"},
                        {'range': [45, 70], 'color': "#FEF08A"},
                        {'range': [70, 100], 'color': "#DCFCE7"}
                    ],
                    'threshold': {
                        'line': {'color': "#DC2626", 'width': 3},
                        'thickness': 0.8,
                        'value': 75
                    }
                }
            ))
            fig_gauge.update_layout(
                height=260,
                margin=dict(l=30, r=30, t=30, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            # Metrics Breakdown Sub-cards
            sub_m1, sub_m2 = st.columns(2)
            sub_m1.metric("TF-IDF Semantic Similarity", f"{target_data['tfidf_score']}%")
            sub_m2.metric("Direct Skill Overlap", f"{target_data['skill_overlap_score']}%")

        with col_g2:
            st.markdown("### 🏆 Top 3 Role Recommendations")
            top_df = pd.DataFrame(top_3)

            fig_bar = px.bar(
                top_df,
                x='match_score',
                y='role',
                orientation='h',
                text='match_score',
                color='match_score',
                color_continuous_scale=['#93C5FD', '#2563EB', '#1E3A8A'],
                labels={'match_score': 'Match Score (%)', 'role': 'Job Role'}
            )
            fig_bar.update_layout(
                yaxis=dict(autorange="reversed", title=""),
                xaxis=dict(range=[0, 105], title="Match Percentage (%)"),
                height=260,
                margin=dict(l=10, r=20, t=20, b=20),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig_bar.update_traces(texttemplate='  %{text}%', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📈 Comprehensive Role Ranking Table")
        
        all_roles_df = pd.DataFrame(ranked_roles)[['role', 'category', 'match_score', 'tfidf_score', 'skill_overlap_score']]
        all_roles_df.columns = ['Job Role Title', 'Industry Category', 'Overall Match Score (%)', 'TF-IDF Similarity (%)', 'Skill Overlap (%)']
        
        st.dataframe(
            all_roles_df.style.background_gradient(cmap="Blues", subset=['Overall Match Score (%)']),
            use_container_width=True,
            hide_index=True
        )


    # --- TAB 2: EXTRACTED SKILLS & SECTIONS ---
    with tab2:
        col_s1, col_s2 = st.columns([1.3, 1.0])

        with col_s1:
            st.markdown("### 🛠️ Extracted Technical Skills Breakdown")
            
            if not found_skills:
                st.warning("⚠️ No technical skills recognized in the resume text.")
            else:
                cat_skills = skill_res['categorized_skills']
                
                category_icons = {
                    'programming': '💻',
                    'databases': '🗄️',
                    'ml_ai': '🤖',
                    'cloud_devops': '☁️',
                    'web_backend': '🌐',
                    'data_tools': '📊'
                }
                
                for cat, sks in cat_skills.items():
                    cat_name = cat.replace("_", " ").title()
                    icon = category_icons.get(cat, '🏷️')
                    st.markdown(f"<div class='cat-header'>{icon} {cat_name} ({len(sks)})</div>", unsafe_allow_html=True)
                    
                    pills_html = "".join([f"<span class='skill-pill'>✓ {sk}</span>" for sk in sks])
                    st.markdown(pills_html, unsafe_allow_html=True)
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        with col_s2:
            st.markdown("### 📊 Skill Distribution Chart")
            
            cat_counts = [{'Category': k.replace("_", " ").title(), 'Count': len(v)} for k, v in skill_res['categorized_skills'].items()]
            if cat_counts:
                df_cat = pd.DataFrame(cat_counts)
                fig_pie = px.pie(
                    df_cat,
                    names='Category',
                    values='Count',
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📄 Parsed Resume Sections")
        
        sec_col1, sec_col2, sec_col3 = st.columns(3)
        sec_col1.metric("File Format", parsed_data['file_type'].upper())
        sec_col2.metric("Total Word Count", f"{parsed_data['word_count']:,}")
        sec_col3.metric("Character Count", f"{parsed_data['char_count']:,}")

        sections = parsed_data['sections']
        for sec_name, content in sections.items():
            with st.expander(f"📌 Section: {sec_name.title()}", expanded=(sec_name in ['skills', 'experience'])):
                st.text_area(f"Content for {sec_name}", content, height=140, key=f"sec_area_{sec_name}")


    # --- TAB 3: SKILL GAP ANALYSIS ---
    with tab3:
        st.markdown(f"### 🔍 Detailed Skill-Gap Analysis for **{target_role}**")
        st.caption(f"Job Description Overview: {target_data['description']}")
        st.markdown("<br>", unsafe_allow_html=True)

        col_gap1, col_gap2 = st.columns(2)

        with col_gap1:
            st.markdown("#### ⚡ Required Role Skills")
            
            st.markdown("**Found in Candidate Resume:**")
            if target_data['matched_required']:
                p_html = "".join([f"<span class='skill-pill'>✓ {sk}</span>" for sk in target_data['matched_required']])
                st.markdown(p_html, unsafe_allow_html=True)
            else:
                st.write("None detected")

            st.markdown("<br>**Missing Required Skills (Action Needed):**", unsafe_allow_html=True)
            if target_data['missing_required']:
                p_html = "".join([f"<span class='skill-pill-missing-req'>❌ {sk}</span>" for sk in target_data['missing_required']])
                st.markdown(p_html, unsafe_allow_html=True)
            else:
                st.success("🎉 Excellent! All required skills for this role are present in your resume.")

        with col_gap2:
            st.markdown("#### ⭐ Optional & Bonus Skills")
            
            st.markdown("**Found in Candidate Resume:**")
            if target_data['matched_optional']:
                p_html = "".join([f"<span class='skill-pill'>✓ {sk}</span>" for sk in target_data['matched_optional']])
                st.markdown(p_html, unsafe_allow_html=True)
            else:
                st.write("None detected")

            st.markdown("<br>**Missing Optional Skills:**", unsafe_allow_html=True)
            if target_data['missing_optional']:
                p_html = "".join([f"<span class='skill-pill-missing-opt'>⚠️ {sk}</span>" for sk in target_data['missing_optional']])
                st.markdown(p_html, unsafe_allow_html=True)
            else:
                st.success("🎉 Great! All optional skills are present.")


    # --- TAB 4: LEARNING ROADMAP ---
    with tab4:
        st.markdown(f"### 🗺️ Tailored 4-Week Action-Oriented Learning Roadmap")
        st.info(f"📋 **Target Role:** {target_role} | {roadmap_data['summary']}")

        for week in roadmap_data.get('weeks', []):
            st.markdown(f"""
            <div class="roadmap-card">
                <h4 style="color:#1E3A8A; margin-top:0; margin-bottom:0.4rem;">{week['title']}</h4>
                <p style="color:#475569; font-size:0.95rem; margin-bottom:0.8rem;"><b>🎯 Weekly Objective:</b> {week['objective']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            w_col1, w_col2 = st.columns([1.2, 1.0])
            with w_col1:
                st.markdown("**💡 Key Topics & Checklist:**")
                for concept in week['key_concepts']:
                    st.checkbox(f"{concept}", key=f"road_check_{week['week']}_{concept}")
            
            with w_col2:
                st.markdown("**🚀 Suggested Hands-on Project:**")
                st.markdown(f"> *{week['project_idea']}*")
            
            st.markdown("<hr style='margin: 1rem 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)


    # --- TAB 5: REPORT & EXPORT ---
    with tab5:
        st.markdown("### 📥 Downloadable Evaluation Reports")
        st.write("Generate and download a comprehensive, professional summary report in PDF or Markdown format.")

        md_report = generate_markdown_report(active_filename, target_data, top_3, found_skills, roadmap_data)
        pdf_path = generate_pdf_report(active_filename, target_data, top_3, found_skills, roadmap_data)
        
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            st.download_button(
                label="📄 Download Official PDF Report",
                data=pdf_bytes,
                file_name=f"Resume_Analysis_{target_role.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col_exp2:
            st.download_button(
                label="📝 Download Markdown Report (.md)",
                data=md_report,
                file_name=f"Resume_Analysis_{target_role.replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("#### 📄 Report Preview")
        st.markdown(md_report)


    # --- TAB 6: RESPONSIBLE AI & VIVA PREP ---
    with tab6:
        st.markdown("### ⚖️ Responsible AI Guidelines & Principles")
        
        st.markdown("""
        > [!IMPORTANT]
        > **1. Decision Support, Not Automated Hiring:** This tool provides objective skill guidance for candidates and recruiters. Match scores are automated recommendations, not hiring decisions.
        > **2. Non-Discrimination Safeguards:** Protected demographic characteristics (age, gender, ethnicity, photo, religion, disability) are completely excluded from text analysis and scoring algorithms.
        > **3. Data Privacy:** Uploaded resumes are evaluated securely in memory and temporary files are purged.
        """)

        st.markdown("---")
        st.markdown("### 🎓 Student Viva Voce Preparation Guide (Project Q&A)")

        viva_qa = [
            ("Q1: How do you extract text from PDF and DOCX resumes?", 
             "We use `pypdf` to parse text page-by-page from PDF documents and `python-docx` to extract text from paragraphs and table structures in DOCX files."),
            
            ("Q2: What is TF-IDF and why is it used?", 
             "TF-IDF (Term Frequency-Inverse Document Frequency) measures term importance relative to a corpus. In our application, TF-IDF converts resume text and job descriptions into high-dimensional vector representations."),
            
            ("Q3: What does Cosine Similarity measure?", 
             "Cosine similarity measures the angle between TF-IDF feature vectors, yielding a score between 0 and 1 indicating semantic text similarity."),
            
            ("Q4: Why can keyword matching miss skills?", 
             "Simple keyword searches fail when candidates use acronyms, variations (e.g. 'sklearn' vs 'scikit-learn'), or special technical symbols (e.g. 'C++', '.NET'). We address this with a controlled skill dictionary and boundary-aware regex patterns."),
            
            ("Q5: How is the final Match Score computed?", 
             "The match score is a weighted combination of TF-IDF Cosine Similarity (45% weight) and Direct Skill Overlap ratio (55% weight, where required skills are weighted 80% and optional skills 20%)."),
            
            ("Q6: When would Sentence Transformers be preferred over TF-IDF?", 
             "Sentence Transformers capture deep semantic context and phrase meaning. They are ideal for complex conceptual matching when GPU/CPU compute resources allow.")
        ]

        for q, a in viva_qa:
            with st.expander(q):
                st.write(a)
