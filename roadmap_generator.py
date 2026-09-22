"""
roadmap_generator.py - Learning Roadmap Generation Module for AI Resume Analyzer

Generates structured 4-week personalized learning roadmaps based on identified
skill gaps for a selected target job role.
"""

from typing import Dict, List, Any

# Knowledge base mapping skills to learning topics, practice tasks, and resources
SKILL_LEARNING_MAP = {
    'FastAPI': {
        'topic': 'Building RESTful APIs with FastAPI and Pydantic',
        'key_concepts': ['Async endpoints', 'Request validation', 'Dependency injection', 'Swagger OpenAPI docs'],
        'project_idea': 'Create a REST API for a book store or user management microservice.'
    },
    'Docker': {
        'topic': 'Containerization Fundamentals with Docker',
        'key_concepts': ['Dockerfiles', 'Images vs Containers', 'Docker Compose', 'Multi-stage builds'],
        'project_idea': 'Containerize a Python application with a database service.'
    },
    'MLflow': {
        'topic': 'MLOps & Experiment Tracking with MLflow',
        'key_concepts': ['Metric logging', 'Artifact tracking', 'Model Registry', 'Model Deployment'],
        'project_idea': 'Track hyperparameters and log artifacts for an ML model training pipeline.'
    },
    'Kubernetes': {
        'topic': 'Container Orchestration with Kubernetes (k8s)',
        'key_concepts': ['Pods & Deployments', 'Services & Ingress', 'ConfigMaps', 'Cluster Scaling'],
        'project_idea': 'Deploy a microservice app on a local Minikube cluster.'
    },
    'PyTorch': {
        'topic': 'Deep Learning with PyTorch',
        'key_concepts': ['Tensors & Autograd', 'Neural Network Modules', 'Dataset & DataLoaders', 'Model Evaluation'],
        'project_idea': 'Train an image classifier or text classification model.'
    },
    'TensorFlow': {
        'topic': 'Deep Learning Frameworks with TensorFlow & Keras',
        'key_concepts': ['Sequential & Functional APIs', 'Custom Layers', 'TensorBoard', 'Model Export'],
        'project_idea': 'Build and evaluate a deep neural network for prediction.'
    },
    'LLM': {
        'topic': 'Large Language Models & Prompt Engineering',
        'key_concepts': ['Transformer architecture', 'Prompt design', 'Fine-tuning basics', 'Model APIs'],
        'project_idea': 'Build a Q&A chatbot using open-source or API-based language models.'
    },
    'RAG': {
        'topic': 'Retrieval-Augmented Generation (RAG) Architecture',
        'key_concepts': ['Embeddings', 'Vector Databases', 'Document Chunking', 'Context Retrieval'],
        'project_idea': 'Build a Chat-with-your-PDF document search tool.'
    },
    'LangChain': {
        'topic': 'LLM Application Orchestration with LangChain',
        'key_concepts': ['Chains & Agents', 'Prompt Templates', 'Memory Management', 'Tools & Output Parsers'],
        'project_idea': 'Create an autonomous AI agent capable of web search and summarizing.'
    },
    'Transformers': {
        'topic': 'Hugging Face Transformers & Pretrained Models',
        'key_concepts': ['AutoModels & Tokenizers', 'Hugging Face Hub', 'Fine-tuning with Trainer API', 'BERT/RoBERTa'],
        'project_idea': 'Fine-tune BERT for custom sentiment classification.'
    },
    'spaCy': {
        'topic': 'Production Natural Language Processing with spaCy',
        'key_concepts': ['Tokenization & POS tagging', 'Named Entity Recognition (NER)', 'Custom Pipelines', 'Matcher'],
        'project_idea': 'Build a resume information extractor for contact info and skills.'
    },
    'OpenCV': {
        'topic': 'Computer Vision Basics & Image Processing with OpenCV',
        'key_concepts': ['Image transformations', 'Contour detection', 'Color spaces', 'Video streaming'],
        'project_idea': 'Build an automated object or face tracking system.'
    },
    'YOLO': {
        'topic': 'Real-Time Object Detection with YOLO',
        'key_concepts': ['YOLOv8 architecture', 'Bounding boxes', 'Bounding box metrics (IoU, mAP)', 'Custom dataset training'],
        'project_idea': 'Train a YOLO model to detect objects in live video streams.'
    },
    'Power BI': {
        'topic': 'Business Intelligence & Dashboards with Power BI',
        'key_concepts': ['DAX formulas', 'Data modeling', 'Interactive visual reports', 'Power Query ETL'],
        'project_idea': 'Build an interactive executive sales performance dashboard.'
    },
    'Tableau': {
        'topic': 'Data Visualization & Storytelling with Tableau',
        'key_concepts': ['Calculated fields', 'LOD expressions', 'Interactive dashboards', 'Storyboards'],
        'project_idea': 'Design an analytics dashboard visualizing regional business metrics.'
    },
    'Spark': {
        'topic': 'Big Data Processing with Apache Spark & PySpark',
        'key_concepts': ['Spark DataFrames', 'RDDs', 'Spark SQL', 'Distributed Transformations'],
        'project_idea': 'Process multi-gigabyte log datasets using PySpark.'
    },
    'Airflow': {
        'topic': 'Workflow Orchestration with Apache Airflow',
        'key_concepts': ['DAG construction', 'Operators & TaskFlow API', 'Scheduling & Backfilling', 'Hooks'],
        'project_idea': 'Build an automated daily ETL pipeline fetching API data into a database.'
    },
    'React': {
        'topic': 'Modern Frontend Development with React',
        'key_concepts': ['JSX & Components', 'Hooks (useState, useEffect)', 'State Management', 'API Integration'],
        'project_idea': 'Build a responsive web application connecting to a Python backend.'
    },
    'AWS': {
        'topic': 'Cloud Infrastructure with Amazon Web Services',
        'key_concepts': ['EC2 & S3', 'IAM Roles & Policies', 'Lambda Serverless', 'CloudWatch'],
        'project_idea': 'Deploy a containerized application to AWS EC2/ECS with S3 storage.'
    },
    'CI/CD': {
        'topic': 'Automated CI/CD Pipelines with GitHub Actions',
        'key_concepts': ['Workflows & Triggers', 'Automated Testing', 'Linting & Build Checks', 'Auto Deployment'],
        'project_idea': 'Set up a GitHub Action to automatically run pytest and build Docker images.'
    }
}


def generate_roadmap(target_role: str, missing_required: List[str], missing_optional: List[str] = None) -> Dict[str, Any]:
    """
    Generate a 4-week structured learning roadmap based on missing skills.
    
    Args:
        target_role (str): Name of the target job role.
        missing_required (List[str]): Missing mandatory skills.
        missing_optional (List[str], optional): Missing optional skills.
        
    Returns:
        dict containing 'target_role', 'weeks' (list of weekly plans), and 'summary'.
    """
    missing_optional = missing_optional or []
    all_missing = missing_required + missing_optional

    if not all_missing:
        return {
            'target_role': target_role,
            'summary': f"Congratulations! You possess all key skills listed for {target_role}.",
            'weeks': [
                {
                    'week': 1,
                    'title': 'Advanced System Optimization & Portfolio Refinement',
                    'skills': ['Portfolio Projects'],
                    'objective': 'Build end-to-end production projects to demonstrate mastery.',
                    'key_concepts': ['Code refactoring', 'Comprehensive unit testing', 'CI/CD deployment'],
                    'project_idea': 'Publish an open-source project showcasing your complete skill set.'
                },
                {
                    'week': 2,
                    'title': 'System Design & Scalability Architecture',
                    'skills': ['System Design'],
                    'objective': 'Master high-level architecture and system scalability concepts.',
                    'key_concepts': ['Load balancing', 'Caching strategies', 'Database sharding'],
                    'project_idea': 'Write an architectural design document for a distributed application.'
                },
                {
                    'week': 3,
                    'title': 'Mock Interviews & Technical Resume Polishing',
                    'skills': ['Interview Prep'],
                    'objective': 'Practice technical coding questions and behavioral responses.',
                    'key_concepts': ['LeetCode problem solving', 'STAR method responses', 'System design walkthroughs'],
                    'project_idea': 'Conduct 3 peer mock interviews and update resume metrics.'
                },
                {
                    'week': 4,
                    'title': 'Open Source Contributions & Networking',
                    'skills': ['Open Source'],
                    'objective': 'Engage with developer communities and contribute to repos.',
                    'key_concepts': ['Pull request reviews', 'Issue tracking', 'Documentation writing'],
                    'project_idea': 'Submit bug fixes or feature additions to a popular GitHub repository.'
                }
            ]
        }

    # Distribute missing skills across 4 weeks
    weeks_plan = []
    num_skills = len(all_missing)
    skills_per_week = max(1, (num_skills + 3) // 4)

    for week_num in range(1, 5):
        start_idx = (week_num - 1) * skills_per_week
        end_idx = min(start_idx + skills_per_week, num_skills)
        week_skills = all_missing[start_idx:end_idx]

        if not week_skills:
            # If fewer missing skills than 4 weeks, fill remaining week with capstone/deployment
            week_skills = ['Capstone Integration & Deployment']
            title = f"Week {week_num}: Capstone Project & Cloud Deployment"
            objective = "Synthesize all learned skills into a cohesive portfolio project."
            concepts = ["End-to-end integration", "Cloud hosting", "Documentation & Readme"]
            project = "Deploy your capstone project and write technical documentation."
        else:
            skill_titles = ", ".join(week_skills)
            title = f"Week {week_num}: Core Focus on {skill_titles}"
            
            # Aggregate topics and concepts from SKILL_LEARNING_MAP
            concepts = []
            projects = []
            objectives = []
            
            for sk in week_skills:
                info = SKILL_LEARNING_MAP.get(sk, {
                    'topic': f'Mastering {sk} fundamentals and practical applications',
                    'key_concepts': [f'{sk} core syntax', f'Working with {sk} libraries', 'Best practices'],
                    'project_idea': f'Build a mini project utilizing {sk}.'
                })
                objectives.append(info['topic'])
                concepts.extend(info['key_concepts'])
                projects.append(info['project_idea'])

            objective = "; ".join(objectives)
            project = " ".join(projects)

        weeks_plan.append({
            'week': week_num,
            'title': title,
            'skills': week_skills,
            'objective': objective,
            'key_concepts': list(dict.fromkeys(concepts)),  # preserve order & remove dupes
            'project_idea': project
        })

    return {
        'target_role': target_role,
        'summary': f"Identified {len(missing_required)} missing required skills and {len(missing_optional)} missing optional skills.",
        'weeks': weeks_plan
    }


if __name__ == "__main__":
    roadmap = generate_roadmap("Machine Learning Engineer", ["FastAPI", "Docker"], ["MLflow"])
    print("Roadmap Summary:", roadmap['summary'])
    for w in roadmap['weeks']:
        print(f"\n{w['title']}")
        print(f" Objective: {w['objective']}")
        print(f" Project: {w['project_idea']}")
