import re

from matcher import compare_resume_to_jd


def extract_candidate_name(resume_text: str) -> str:
    """
    Extracts a likely candidate name from the resume.

    Uses the first meaningful line and ignores common section headings.
    """

    ignored_lines = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "professional resume",
    }

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    for line in lines[:10]:
        cleaned = re.sub(r"[^A-Za-z .'-]", "", line).strip()

        if not cleaned:
            continue

        if cleaned.lower() in ignored_lines:
            continue

        # Avoid selecting obvious contact information
        if "@" in line:
            continue

        if re.search(r"\+?\d[\d\s-]{7,}", line):
            continue

        # Avoid obvious section headings
        if cleaned.upper() in {
            "EDUCATION",
            "SKILLS",
            "TECHNICAL SKILLS",
            "PROJECTS",
            "EXPERIENCE",
            "INTERNSHIP",
            "INTERNSHIPS",
            "CERTIFICATIONS",
        }:
            continue

        return cleaned.title()

    return "Unknown Candidate"


def calculate_candidate_match(
    candidate_name: str,
    resume_text: str,
    job_description: str
) -> dict:
    """
    Compares one candidate resume against the Job Description.
    """

    result = compare_resume_to_jd(
        resume_text,
        job_description
    )

    return {
        "candidate_name": candidate_name,
        "score": result.get("score", 0),
        "matched": result.get("matched", []),
        "missing": result.get("missing", []),
        "total_jd_skills": result.get("total_jd_skills", 0),
        "resume_total_skills": result.get("resume_total_skills", 0),
        "category_data": result.get("category_data", {}),
        "category_details": result.get("category_details", []),
        "resume_text": resume_text,
    }


def rank_candidates(
    candidates: list,
    job_description: str
) -> list:
    """
    Analyze and rank multiple candidates against one JD.

    candidates format:

    [
        {
            "name": "Candidate Name",
            "text": "Resume text..."
        }
    ]

    Returns candidates sorted by match score.
    """

    results = []

    for candidate in candidates:

        name = candidate.get("name", "").strip()

        resume_text = candidate.get("text", "").strip()

        if not resume_text:
            continue

        if not name:
            name = extract_candidate_name(resume_text)

        result = calculate_candidate_match(
            candidate_name=name,
            resume_text=resume_text,
            job_description=job_description
        )

        results.append(result)

    # Highest score first
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Add ranking
    for index, result in enumerate(results, start=1):
        result["rank"] = index

    return results


def get_candidate_status(score: int, threshold: int = 70) -> str:
    """
    Converts the match score into a simple screening status.
    """

    if score >= threshold:
        return "Strong Match"

    if score >= 40:
        return "Moderate Match"

    return "Low Match"


