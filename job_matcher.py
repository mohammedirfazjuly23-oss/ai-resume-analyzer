"""
job_matcher.py - Matching and Recommendation Module for AI Resume Analyzer

Combines TF-IDF Vectorization, Cosine Similarity, and Direct Skill Overlap
scoring to recommend suitable job roles and rank candidates.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from text_cleaner import clean_text
from skill_extractor import SkillExtractor

DEFAULT_JOBS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'job_roles.csv')


class JobMatcher:
    def __init__(self, jobs_path: str = DEFAULT_JOBS_PATH, skill_extractor: SkillExtractor = None):
        self.jobs_path = jobs_path
        self.jobs_df = None
        self.skill_extractor = skill_extractor or SkillExtractor()
        self.vectorizer = None
        self.job_tfidf_matrix = None
        self.load_jobs()

    def load_jobs(self):
        """Load job roles dataset and initialize TF-IDF vectorizer."""
        if not os.path.exists(self.jobs_path):
            raise FileNotFoundError(f"Job roles dataset not found at {self.jobs_path}")

        self.jobs_df = pd.read_csv(self.jobs_path)

        # Build clean search corpus for each job
        # Corpus combines description, role title, required skills, and optional skills
        corpus = []
        for _, row in self.jobs_df.iterrows():
            role_text = f"{row['role']} {row['category']} {row['required_skills']} {row['optional_skills']} {row['description']}"
            cleaned_corpus = clean_text(role_text, lowercase=True)
            corpus.append(cleaned_corpus)

        self.jobs_df['clean_corpus'] = corpus

        # Fit TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.job_tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def match_resume(self, resume_text: str, candidate_skills: List[str] = None) -> Dict[str, Any]:
        """
        Match candidate resume against all job roles in dataset.
        
        Args:
            resume_text (str): Extracted resume text.
            candidate_skills (List[str], optional): Extracted skill list.
            
        Returns:
            dict with:
            - 'ranked_roles': List of dicts ordered by match_score descending
            - 'top_3_recommendations': Top 3 job roles
        """
        if candidate_skills is None:
            extracted = self.skill_extractor.extract_skills(resume_text)
            candidate_skills = extracted['found_skills']

        candidate_skills_set = set(s.lower() for s in candidate_skills)
        clean_resume = clean_text(resume_text, lowercase=True)

        # 1. Calculate TF-IDF Cosine Similarity
        resume_vector = self.vectorizer.transform([clean_resume])
        cosine_sims = cosine_similarity(resume_vector, self.job_tfidf_matrix).flatten()

        results = []

        for idx, row in self.jobs_df.iterrows():
            role_title = row['role']
            category = row['category']
            
            # Parse required and optional skills for job
            req_skills_list = [s.strip() for s in str(row['required_skills']).split(',') if s.strip()]
            opt_skills_list = [s.strip() for s in str(row['optional_skills']).split(',') if s.strip()]

            # Determine matching & missing required skills
            matched_required = []
            missing_required = []
            for req in req_skills_list:
                req_lower = req.lower()
                # Check if skill or any of its aliases are present in candidate skills or text
                if any(cand_s == req_lower or cand_s in req_lower or req_lower in cand_s for cand_s in candidate_skills_set):
                    matched_required.append(req)
                else:
                    missing_required.append(req)

            # Determine matching & missing optional skills
            matched_optional = []
            missing_optional = []
            for opt in opt_skills_list:
                opt_lower = opt.lower()
                if any(cand_s == opt_lower or cand_s in opt_lower or opt_lower in cand_s for cand_s in candidate_skills_set):
                    matched_optional.append(opt)
                else:
                    missing_optional.append(opt)

            # 2. Skill Overlap Ratio (Required skills weighted 80%, Optional skills 20%)
            req_ratio = len(matched_required) / len(req_skills_list) if req_skills_list else 1.0
            opt_ratio = len(matched_optional) / len(opt_skills_list) if opt_skills_list else 0.0
            skill_score = (req_ratio * 0.8) + (opt_ratio * 0.2)

            # 3. Combined Final Score (50% TF-IDF Cosine Similarity + 50% Skill Overlap)
            tfidf_score = float(cosine_sims[idx])
            
            # Scaled match percentage (0 to 100)
            combined_raw = (0.45 * tfidf_score) + (0.55 * skill_score)
            match_percentage = min(100.0, max(0.0, round(combined_raw * 100, 1)))

            results.append({
                'role': role_title,
                'category': category,
                'match_score': match_percentage,
                'tfidf_score': round(tfidf_score * 100, 1),
                'skill_overlap_score': round(skill_score * 100, 1),
                'required_skills': req_skills_list,
                'optional_skills': opt_skills_list,
                'matched_required': matched_required,
                'missing_required': missing_required,
                'matched_optional': matched_optional,
                'missing_optional': missing_optional,
                'description': row['description']
            })

        # Rank roles by match_score descending
        ranked_roles = sorted(results, key=lambda x: x['match_score'], reverse=True)

        return {
            'ranked_roles': ranked_roles,
            'top_3_recommendations': ranked_roles[:3]
        }

    def get_role_analysis(self, target_role_name: str, resume_text: str, candidate_skills: List[str] = None) -> Dict[str, Any]:
        """Get detailed analysis for a specific target job role."""
        matches = self.match_resume(resume_text, candidate_skills)
        for role_data in matches['ranked_roles']:
            if role_data['role'].lower() == target_role_name.lower():
                return role_data
        
        # Fallback if not found exact match
        return matches['ranked_roles'][0]


if __name__ == "__main__":
    matcher = JobMatcher()
    sample_text = "Experienced Data Scientist skilled in Python, SQL, Pandas, scikit-learn, Power BI, and Machine Learning."
    sample_skills = ["Python", "SQL", "Pandas", "scikit-learn", "Power BI", "Machine Learning"]
    res = matcher.match_resume(sample_text, sample_skills)
    print("Top 3 Recommendations:")
    for r in res['top_3_recommendations']:
        print(f"- {r['role']}: {r['match_score']}% match")
