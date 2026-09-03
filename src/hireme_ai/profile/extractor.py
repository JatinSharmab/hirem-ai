import re

from hireme_ai.schemas.candidate import CandidateFact, CandidateProfile

COMMON_SKILLS = [
    "Python",
    "FastAPI",
    "LangGraph",
    "LangChain",
    "RAG",
    "PostgreSQL",
    "Docker",
    "AWS",
    "React",
    "JavaScript",
    "SQL",
    "PyTorch",
    "TensorFlow",
    "scikit-learn",
]


def demo_extract_profile(text: str, name: str = "Candidate") -> CandidateProfile:
    """Keyword-only extraction; every fact requires candidate review."""
    skills = [skill for skill in COMMON_SKILLS if re.search(rf"\b{re.escape(skill)}\b", text, re.I)]
    facts = [
        CandidateFact(
            id=f"FACT-{i:03d}",
            category="skill",
            subject=name,
            predicate="used",
            value=skill,
            source_section="resume",
            source_text=skill,
            confidence=1.0,
        )
        for i, skill in enumerate(skills, 1)
    ]
    return CandidateProfile(name=name, summary=text[:300], skills=skills, facts=facts)
