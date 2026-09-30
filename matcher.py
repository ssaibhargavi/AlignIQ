import re


# ============================================================
# CENTRAL SKILL TAXONOMY
# ============================================================
# IMPORTANT:
# This taxonomy is used ONLY to DETECT skills that already
# exist in the text being analyzed.
#
# It does NOT add skills.
# It does NOT infer skills.
# It does NOT assume that related skills exist.
# ============================================================

TAXONOMY_MAP = {

    "Programming Languages": {

        "Python": [
            "python",
            "python3"
        ],

        "Java": [
            "java",
            "core java"
        ],

        "C++": [
            "c++",
            "cpp"
        ],

        "C": [
            " c ",
            "\nc\n"
        ],

        "C#": [
            "c#",
            "csharp"
        ],

        "JavaScript": [
            "javascript",
            "js"
        ],

        "TypeScript": [
            "typescript"
        ],

        "SQL": [
            "sql",
            "Structured Query Language"
        ],

        "HTML": [
            "html",
            "html5"
        ],

        "CSS": [
            "css",
            "css3"
        ]
    },


    "Data Analytics": {

        "Excel": [
            "excel",
            "microsoft excel",
            "ms excel"
        ],

        "Power BI": [
            "power bi",
            "powerbi",
            "Microsoft Power BI"
        ],

        "Power Query": [
            "power query"
        ],

        "DAX": [
            "dax"
        ],

        "Pandas": [
            "pandas"
        ],

        "NumPy": [
            "numpy"
        ],

        "Tableau": [
            "tableau"
        ],

        "Data Analysis": [
            "data analysis"
        ],

        "Data Cleaning": [
            "data cleaning",
            "data cleansing"
        ],

        "Data Visualization": [
            "data visualization",
            "data visualisation"
        ]
    },

    "AI & Machine Learning": {
        "Artificial Intelligence": [
            "artificial intelligence",
            "artificial intelligence ai",
            "ai"
        ],
        "Machine Learning": [
            "machine learning",
            "machine-learning",
            "ml"
        ],
        "Deep Learning": [
            "deep learning",
            "deep-learning",
            "dl"
        ],
        "Natural Language Processing": [
            "natural language processing",
            "nlp"
        ],
        "Computer Vision": [
            "computer vision",
            "opencv"
        ],
        "Generative AI": [
            "generative ai",
            "genai"
        ],
        "Large Language Models": [
            "large language models",
            "large language model",
            "llm",
            "llms"
        ],
        "Transformers": [
            "transformers",
            "hugging face",
            "huggingface"
        ],
        "LangChain": [
            "langchain"
        ],
        "LangGraph": [
            "langgraph"
        ],
        "RAG": [
            "rag",
            "retrieval augmented generation",
            "retrieval-augmented generation"
        ]
    },


    "Databases": {

        "MySQL": [
            "mysql"
        ],

        "PostgreSQL": [
            "postgresql",
            "postgres"
        ],

        "MongoDB": [
            "mongodb"
        ],

        "SQLite": [
            "sqlite"
        ],

        "SQL Server": [
            "sql server",
            "mssql"
        ]
    },


    "Python Libraries": {

        "Matplotlib": [
            "matplotlib"
        ],

        "Seaborn": [
            "seaborn"
        ],

        "Scikit-Learn": [
            "scikit-learn",
            "sklearn"
        ]
    },


    "Software Development": {

        "Git": [
            "git"
        ],

        "GitHub": [
            "github"
        ],

        "REST APIs": [
            "rest api",
            "restful api"
        ],

        "Object-Oriented Programming": [
            "object-oriented programming",
            "object oriented programming",
            "oop",
            "oops"
        ],

        "Data Structures": [
            "data structures"
        ],

        "Algorithms": [
            "algorithms"
        ]
    },


    "Web Development": {

        "React": [
            "react.js",
            "reactjs",
            "react"
        ],

        "Node.js": [
            "node.js",
            "nodejs"
        ],

        "Django": [
            "django"
        ],

        "Flask": [
            "flask"
        ],

        "FastAPI": [
            "fastapi"
        ]
    },


    "Cloud & DevOps": {

        "AWS": [
            "aws",
            "amazon web services"
        ],

        "Azure": [
            "microsoft azure",
            "azure"
        ],

        "Docker": [
            "docker"
        ],

        "Linux": [
            "linux"
        ]
    }
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower()

    # Normalize spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SAFE SKILL DETECTION
# ============================================================

def skill_exists(text: str, variation: str) -> bool:
    """
    Checks whether a skill actually exists in text.

    Uses boundaries to reduce false positives.

    Example:

    SQL should not match:
    "NoSQL" accidentally.
    """

    if not text or not variation:
        return False

    normalized_text = normalize_text(text)

    variation = variation.strip().lower()

    # Special handling for single-letter C
    if variation in ["c", " c ", "\nc\n"]:
        return bool(
            re.search(
                r"(?<![a-zA-Z+#])c(?![a-zA-Z+#])",
                normalized_text
            )
        )

    escaped = re.escape(
        variation
    )

    # Word boundary style matching
    pattern = (
        r"(?<![a-zA-Z0-9_+#])"
        + escaped +
        r"(?![a-zA-Z0-9_+#])"
    )

    return bool(
        re.search(
            pattern,
            normalized_text,
            re.IGNORECASE
        )
    )




# ============================================================
# EXTRACT EXPLICIT SKILLS SECTION
# ============================================================
def extract_explicit_skills_section(resume_text: str) -> str:
    """Return only the content belonging to the resume's SKILLS section."""
    if not resume_text:
        return ""

    skill_headings = {
        "skills",
        "technical skills",
        "technical skill",
        "key skills",
        "core skills",
        "core competencies",
        "technical competencies",
        "skills and tools",
    }

    section_headings = skill_headings | {
        "summary", "professional summary", "profile",
        "experience", "work experience", "professional experience",
        "employment history", "work history",
        "projects", "project", "academic projects", "personal projects",
        "education", "academic background", "academic qualifications",
        "certifications", "certification", "certificates", "courses", "training",
        "achievements", "achievement", "awards", "honors", "honours",
        "extracurricular activities", "extracurricular activity", "extracurricular",
        "additional information", "additional details", "other information",
        "soft skills", "professional skills", "interpersonal skills",
        "languages", "languages known", "language skills",
        "personal details", "personal information", "declaration"
    }

    lines = resume_text.splitlines()
    in_skills = False
    collected = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        normalized = re.sub(r"[#:|\-–—]+$", "", line).strip().lower()
        normalized = re.sub(r"^#+\s*", "", normalized).strip()

        if not in_skills:
            if normalized in skill_headings:
                in_skills = True
            continue

        if normalized in section_headings:
            break

        collected.append(line)

    return "\n".join(collected)

# ============================================================
# DETECT SKILLS
# ============================================================

def search_skills(text: str) -> dict:
    """
    Detects ONLY skills physically present in the supplied text.

    Example:

    If text contains:
    Python, SQL, Power BI

    Output:
    {
        "Programming Languages": ["Python", "SQL"],
        "Data Analytics": ["Power BI"]
    }

    No skills are invented.
    """

    if not text:
        return {}

    detected = {}

    for category, skills in TAXONOMY_MAP.items():

        found_skills = []

        for canonical_skill, variations in skills.items():

            for variation in variations:

                if skill_exists(
                    text,
                    variation
                ):

                    found_skills.append(
                        canonical_skill
                    )

                    break

        if found_skills:

            detected[category] = sorted(
                list(
                    set(found_skills)
                )
            )

    return detected


# ============================================================
# FLATTEN SKILLS
# ============================================================

def flatten_skills(skill_dict: dict) -> set:

    skills = set()

    for category_skills in skill_dict.values():

        skills.update(
            category_skills
        )

    return skills


# ============================================================
# JD SKILL WEIGHT
# ============================================================

def get_skill_weight(
    jd_text: str,
    skill: str
) -> int:
    """
    Weight:
    3 = Required / Mandatory
    2 = Preferred / Nice to have
    1 = Normal

    The skill is classified according to the JD section
    in which it appears.
    """

    if not jd_text:
        return 1

    lines = jd_text.splitlines()

    current_weight = 1

    required_terms = [
        "required",
        "must have",
        "mandatory",
        "essential",
        "minimum qualifications",
        "minimum requirement"
    ]

    preferred_terms = [
        "preferred",
        "nice to have",
        "good to have",
        "plus"
    ]

    for line in lines:

        line_clean = line.strip().lower()

        # Detect section heading
        if any(
            term in line_clean
            for term in required_terms
        ):
            current_weight = 3
            continue

        if any(
            term in line_clean
            for term in preferred_terms
        ):
            current_weight = 2
            continue
        # Neutral / normal section
        neutral_terms = [
            "other skills",
            "skills",
            "additional skills",
            "technical skills",
            "skills and tools",
            "responsibilities"
        ]

        if any(
            term in line_clean
            for term in neutral_terms
        ):
            current_weight = 1
            continue
        
        # Check whether this line contains the skill
        if skill.lower() in line_clean:
            return current_weight

    return 1


# ============================================================
# RESUME VS JD MATCHING
# ============================================================

def compare_resume_to_jd(
    resume_text: str,
    jd_text: str
) -> dict:
    """
    Compares skills detected in the Master Resume
    against skills detected in the Job Description.

    IMPORTANT:

    matched =
        JD skills that are ALSO present in Master Resume

    missing =
        JD skills NOT present in Master Resume

    The JD NEVER modifies the Master Resume skill list.
    """

    # Candidate skills must come ONLY from the explicit SKILLS section.
    # This prevents skills mentioned in Summary, Experience, Projects, etc.
    # from becoming candidate-declared skills.
    skills_section_text = extract_explicit_skills_section(resume_text)

    resume_skills_dict = search_skills(
        skills_section_text
    )

    jd_skills_dict = search_skills(
        jd_text
    )

    # Convert to sets
    resume_skills = flatten_skills(
        resume_skills_dict
    )

    jd_skills = flatten_skills(
        jd_skills_dict
    )

    # True intersection only
    matched_skills = sorted(
        resume_skills.intersection(
            jd_skills
        )
    )

    # JD skills missing from resume
    missing_skills = sorted(
        jd_skills.difference(
            resume_skills
        )
    )

    # --------------------------------------------------------
    # WEIGHTED SCORE
    # --------------------------------------------------------

    total_weight = 0

    matched_weight = 0

    skill_weights = {}

    for skill in jd_skills:

        weight = get_skill_weight(
            jd_text,
            skill
        )

        skill_weights[skill] = weight

        total_weight += weight

        if skill in resume_skills:

            matched_weight += weight

    if total_weight > 0:

        score = round(
            (
                matched_weight
                / total_weight
            )
            * 100
        )

    else:

        score = 0


    # --------------------------------------------------------
    # CATEGORY DATA
    # --------------------------------------------------------

    category_data = {

        "Category": [],

        "Matched": [],

        "Missing": []
    }


    category_details = []


    for category in TAXONOMY_MAP:

        category_skills = set(
            TAXONOMY_MAP[
                category
            ].keys()
        )

        relevant_jd_skills = (
            category_skills.intersection(
                jd_skills
            )
        )

        if not relevant_jd_skills:
            continue

        category_matched = sorted(

            relevant_jd_skills.intersection(
                resume_skills
            )
        )

        category_missing = sorted(

            relevant_jd_skills.difference(
                resume_skills
            )
        )

        category_data[
            "Category"
        ].append(
            category
        )

        category_data[
            "Matched"
        ].append(
            len(category_matched)
        )

        category_data[
            "Missing"
        ].append(
            len(category_missing)
        )

        category_details.append({

            "category": category,

            "matched": category_matched,

            "missing": category_missing
        })


    return {

        "score": score,

        "matched": matched_skills,

        "missing": missing_skills,

        "resume_skills": sorted(
            resume_skills
        ),

        "jd_skills": sorted(
            jd_skills
        ),

        "resume_skills_by_category":
            resume_skills_dict,

        "jd_skills_by_category":
            jd_skills_dict,

        "total_jd_skills":
            len(jd_skills),

        "resume_total_skills":
            len(resume_skills),

        "skill_weights":
            skill_weights,

        "category_data":
            category_data,

        "category_details":
            category_details
    }
