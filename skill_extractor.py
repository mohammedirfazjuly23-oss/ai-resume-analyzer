"""
skill_extractor.py - Skill Extraction Module for AI Resume Analyzer

Identifies technical and domain skills from resume text using a controlled
skill dictionary and regex boundary-aware keyword matching.
"""

import os
import re
import pandas as pd
from typing import Dict, List, Set, Tuple
from text_cleaner import clean_text

DEFAULT_DICT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'skill_dictionary.csv')


class SkillExtractor:
    def __init__(self, dictionary_path: str = DEFAULT_DICT_PATH):
        self.dictionary_path = dictionary_path
        self.skills_df = None
        self.skill_map = {}  # alias_pattern -> (standard_skill_name, category)
        self.category_map = {}  # category -> list of standard_skill_names
        self.load_dictionary()

    def load_dictionary(self):
        """Load skill dictionary CSV and build lookup maps."""
        if not os.path.exists(self.dictionary_path):
            raise FileNotFoundError(f"Skill dictionary not found at {self.dictionary_path}")

        self.skills_df = pd.read_csv(self.dictionary_path)
        self.skill_map = {}
        self.category_map = {}

        for _, row in self.skills_df.iterrows():
            standard_name = str(row['skill']).strip()
            category = str(row['category']).strip()
            aliases_raw = str(row['aliases']).split(',')

            if category not in self.category_map:
                self.category_map[category] = []
            if standard_name not in self.category_map[category]:
                self.category_map[category].append(standard_name)

            # Build list of aliases including standard name
            all_aliases = [standard_name.lower()] + [a.strip().lower() for a in aliases_raw if a.strip()]

            for alias in set(all_aliases):
                if alias:
                    self.skill_map[alias] = (standard_name, category)

    def extract_skills(self, text: str) -> Dict[str, any]:
        """
        Extract technical skills from input resume text.
        
        Returns dict with:
        - 'found_skills': sorted list of unique standard skill names
        - 'categorized_skills': dict mapping category -> list of skills found
        - 'count': total count of unique skills found
        """
        if not text or not text.strip():
            return {
                'found_skills': [],
                'categorized_skills': {},
                'count': 0
            }

        cleaned = clean_text(text, lowercase=True)

        found_skills_set: Set[Tuple[str, str]] = set()

        # Sort aliases by length descending so multi-word aliases match before sub-parts
        sorted_aliases = sorted(self.skill_map.keys(), key=len, reverse=True)

        for alias in sorted_aliases:
            standard_name, category = self.skill_map[alias]

            # Construct boundary-aware regex pattern
            # For special symbols like C++, C#, .NET, escape them properly
            escaped_alias = re.escape(alias)
            
            # If alias starts/ends with alphanumeric, enforce word boundary \b
            prefix_b = r'\b' if alias[0].isalnum() else r'(?:^|\s)'
            
            # Special case for 'c' to avoid matching inside 'c++' or 'c#'
            if alias.lower() == 'c':
                suffix_b = r'\b(?![\+\#])'
            else:
                suffix_b = r'\b' if alias[-1].isalnum() else r'(?:$|\s)'
            
            pattern = re.compile(prefix_b + escaped_alias + suffix_b, re.IGNORECASE)

            if pattern.search(cleaned):
                found_skills_set.add((standard_name, category))

        # Separate out skills that might be substrings of larger matched skills (e.g. Java vs JavaScript)
        # Note: If JavaScript is found, Java should only be kept if 'java' was matched as a distinct word
        # The boundary regex prefix_b and suffix_b already handles 'java' vs 'javascript'.

        found_skills = sorted(list(set(s[0] for s in found_skills_set)))
        
        categorized_skills: Dict[str, List[str]] = {}
        for skill_name, category in found_skills_set:
            if category not in categorized_skills:
                categorized_skills[category] = []
            if skill_name not in categorized_skills[category]:
                categorized_skills[category].append(skill_name)
            categorized_skills[category].sort()

        return {
            'found_skills': found_skills,
            'categorized_skills': categorized_skills,
            'count': len(found_skills)
        }


if __name__ == "__main__":
    extractor = SkillExtractor()
    sample = "I am a Data Scientist proficient in Python, SQL, Pandas, scikit-learn, C++, and Docker."
    res = extractor.extract_skills(sample)
    print("Found skills:", res['found_skills'])
    print("Categorized:", res['categorized_skills'])
