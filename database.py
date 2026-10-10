import json
import streamlit as st
import psycopg

def get_connection():
    """Connect to the Neon PostgreSQL database."""

    database_url = st.secrets.get("NEON_DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "NEON_DATABASE_URL is missing from Streamlit secrets."
        )

    return psycopg.connect(database_url)


def init_db():
    """Create AlignIQ database tables if they do not exist."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    resume_id BIGSERIAL PRIMARY KEY,
                    file_name TEXT,
                    resume_text TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    jd_id BIGSERIAL PRIMARY KEY,
                    job_title TEXT,
                    jd_text TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS candidate_analyses (
                    analysis_id BIGSERIAL PRIMARY KEY,
                    resume_id BIGINT NOT NULL
                        REFERENCES resumes(resume_id),
                    jd_id BIGINT NOT NULL
                        REFERENCES job_descriptions(jd_id),
                    career_level TEXT,
                    match_score NUMERIC(5, 2) NOT NULL,
                    matched_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
                    missing_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
                    total_jd_skills INTEGER NOT NULL DEFAULT 0,
                    tailored_resume JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS hr_screenings (
                    screening_id BIGSERIAL PRIMARY KEY,
                    jd_id BIGINT NOT NULL
                        REFERENCES job_descriptions(jd_id),
                    match_threshold INTEGER NOT NULL DEFAULT 70,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS hr_results (
                    result_id BIGSERIAL PRIMARY KEY,
                    screening_id BIGINT NOT NULL
                        REFERENCES hr_screenings(screening_id)
                        ON DELETE CASCADE,
                    resume_id BIGINT NOT NULL
                        REFERENCES resumes(resume_id),
                    candidate_name TEXT,
                    candidate_rank INTEGER NOT NULL,
                    match_score NUMERIC(5, 2) NOT NULL,
                    status TEXT NOT NULL,
                    matched_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
                    missing_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

    return True

def save_candidate_analysis(
    resume_text,
    job_description,
    career_level,
    results,
    tailored_resume,
):
    """Save one Candidate Mode analysis and return its ID."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            # 1. Save the Master Resume
            cur.execute(
                """
                INSERT INTO resumes (resume_text, mode)
                VALUES (%s, %s)
                RETURNING resume_id;
                """,
                (resume_text, "Candidate"),
            )
            resume_id = cur.fetchone()[0]

            # 2. Save the Job Description
            cur.execute(
                """
                INSERT INTO job_descriptions (jd_text)
                VALUES (%s)
                RETURNING jd_id;
                """,
                (job_description,),
            )
            jd_id = cur.fetchone()[0]

            # 3. Save the analysis results
            cur.execute(
                """
                INSERT INTO candidate_analyses (
                    resume_id,
                    jd_id,
                    career_level,
                    match_score,
                    matched_skills,
                    missing_skills,
                    total_jd_skills,
                    tailored_resume
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING analysis_id;
                """,
                (
                    resume_id,
                    jd_id,
                    career_level,
                    results.get("score", 0),
                    json.dumps(results.get("matched", [])),
                    json.dumps(results.get("missing", [])),
                    results.get("total_jd_skills", 0),
                    json.dumps(tailored_resume, default=str),
                ),
            )

            analysis_id = cur.fetchone()[0]

    return analysis_id

def save_hr_screening(
    job_description,
    match_threshold,
    ranked_results,
):
    """Save an HR screening and its ranked candidate results."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            # 1. Save the job description
            cur.execute(
                """
                INSERT INTO job_descriptions (jd_text)
                VALUES (%s)
                RETURNING jd_id;
                """,
                (job_description,),
            )
            jd_id = cur.fetchone()[0]

            # 2. Create the screening record
            cur.execute(
                """
                INSERT INTO hr_screenings (
                    jd_id,
                    match_threshold
                )
                VALUES (%s, %s)
                RETURNING screening_id;
                """,
                (jd_id, match_threshold),
            )
            screening_id = cur.fetchone()[0]

            # 3. Save each ranked candidate
            for candidate in ranked_results:
                cur.execute(
                    """
                    INSERT INTO resumes (
                        file_name,
                        resume_text,
                        mode
                    )
                    VALUES (%s, %s, %s)
                    RETURNING resume_id;
                    """,
                    (
                        candidate.get("candidate_name", "Unknown Candidate"),
                        candidate.get("resume_text", ""),
                        "HR",
                    ),
                )
                resume_id = cur.fetchone()[0]

                score = candidate.get("score", 0)

                if score >= match_threshold:
                    status = "Strong Match"
                elif score >= 40:
                    status = "Moderate Match"
                else:
                    status = "Low Match"

                cur.execute(
                    """
                    INSERT INTO hr_results (
                        screening_id,
                        resume_id,
                        candidate_name,
                        candidate_rank,
                        match_score,
                        status,
                        matched_skills,
                        missing_skills
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    );
                    """,
                    (
                        screening_id,
                        resume_id,
                        candidate.get("candidate_name", "Unknown Candidate"),
                        candidate.get("rank", 0),
                        score,
                        status,
                        json.dumps(candidate.get("matched", [])),
                        json.dumps(candidate.get("missing", [])),
                    ),
                )

    return screening_id

