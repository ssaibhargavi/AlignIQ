import re

from matcher import search_skills, TAXONOMY_MAP


# ============================================================
# SECTION DEFINITIONS
# ============================================================

SECTION_SYNONYMS = {

    "SUMMARY": [
        "summary",
        "professional summary",
        "profile",
        "career objective",
        "objective",
        "professional objective"
    ],

    "SKILLS": [
        "skills",
        "technical skills",
        "technical skill",
        "key skills",
        "core skills",
        "core competencies",
        "technical competencies",
        "skills and tools"
    ],

    "PROJECTS": [
        "projects",
        "project",
        "academic projects",
        "personal projects",
        "key projects",
        "major projects"
    ],

    "INTERNSHIPS": [
        "internship",
        "internships",
        "internship experience",
        "internship experiences"
    ],

    "EXPERIENCE": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history"
    ],

    "EDUCATION": [
        "education",
        "academic background",
        "academic qualifications",
        "qualifications"
    ],

    "CERTIFICATIONS": [
        "certifications",
        "certification",
        "certificates",
        "courses",
        "training",
        "licenses and certifications"
    ],

    "ACHIEVEMENTS": [
        "achievements",
        "achievement",
        "awards",
        "honors",
        "honours",
        "accomplishments"
    ],
    "SOFT_SKILLS": [
    "soft skills",
    "professional skills",
    "interpersonal skills",
    "personal skills",
    "strengths"
    ],

    "LANGUAGES": [
        "languages",
        "languages known",
        "language skills",
        "spoken languages"
    ],

    "PERSONAL_DETAILS": [
        "personal details",
        "personal information",
        "personal profile"
    ],

    "DECLARATION": [
        "declaration"
    ]
}


# ============================================================
# BULLET PATTERN
# ============================================================

BULLET_PATTERN = re.compile(
    r"""
    ^\s*
    (
        [•●○◦▪▫►▸▹◆◇■□*]
        |
        [-–—]
        |
        \d+[\.\)]
    )
    \s+
    """,
    re.VERBOSE
)


# ============================================================
# NORMALIZE LINE
# ============================================================

def normalize_line(line):

    if not line:
        return ""

    line = str(line)

    line = line.replace("\u00a0", " ")

    line = re.sub(
        r"\s+",
        " ",
        line
    )

    return line.strip()


# ============================================================
# CLEAN EMOJIS FROM CONTACT LINES
# ============================================================

def remove_contact_icons(text):

    if not text:
        return ""

    return re.sub(
        r"^[^\w@+]+",
        "",
        text
    ).strip()


# ============================================================
# BULLET DETECTION
# ============================================================

def is_bullet_line(line):

    if not line:
        return False

    return bool(
        BULLET_PATTERN.match(line)
    )


# ============================================================
# REMOVE BULLET
# ============================================================

def clean_bullet_marker(line):

    line = normalize_line(line)

    return BULLET_PATTERN.sub(
        "",
        line
    ).strip()


# ============================================================
# CLEAN BULLET TEXT
# ============================================================

def clean_resume_bullet(text):

    text = normalize_line(text)

    if not text:
        return ""

    # Fix spaces before punctuation
    text = re.sub(
        r"\s+([,.!?;:])",
        r"\1",
        text
    )

    # Remove duplicate spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]

    # Add period only when appropriate
    if text and text[-1] not in ".!?":

        # Do not force punctuation for dates
        if not re.search(
            r"\b\d{4}\s*$",
            text
        ):
            text += "."

    return text


# ============================================================
# DETECT SECTION
# ============================================================

def detect_section_type(line):

    cleaned = re.sub(
        r"[^a-zA-Z\s&]",
        "",
        line
    ).strip().lower()

    if not cleaned:
        return None

    if len(cleaned) > 50:
        return None

    for section, aliases in SECTION_SYNONYMS.items():

        if cleaned in aliases:
            return section

    return None


# ============================================================
# SPLIT RESUME INTO SECTIONS
# ============================================================

def parse_resume_sections(master_text):

    sections = {
        "HEADER": []
    }

    current_section = "HEADER"

    for raw_line in master_text.split("\n"):

        line = normalize_line(raw_line)

        if not line:
            continue

        section = detect_section_type(line)

        if section:

            current_section = section

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections[current_section].append(line)

    return sections


# ============================================================
# CONTACT INFORMATION
# ============================================================

def extract_contact_info(master_text):

    lines = [
        normalize_line(line)
        for line in master_text.split("\n")
        if normalize_line(line)
    ]

    name = "Candidate Name"

    if lines:

        possible_name = remove_contact_icons(lines[0])

        # Basic validation
        if (
            len(possible_name.split()) <= 6
            and len(possible_name) <= 60
            and "@" not in possible_name
        ):
            name = possible_name.title()

    contact_items = []

    # Email
    email_match = re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        master_text
    )

    if email_match:
        contact_items.append(
            email_match.group(0)
        )

    # Phone numbers
    phone_match = re.search(
        r"(?:\+91[\s\-]?)?[6-9]\d{4}[\s\-]?\d{5}",
        master_text
    )

    if phone_match:
        contact_items.append(
            phone_match.group(0)
        )

    # LinkedIn
    linkedin_match = re.search(
        r"(?:https?://)?linkedin\.com/in/[\w\.-]+",
        master_text,
        re.IGNORECASE
    )

    if linkedin_match:
        contact_items.append(
            linkedin_match.group(0)
        )

    # GitHub
    github_match = re.search(
        r"(?:https?://)?github\.com/[\w\.-]+",
        master_text,
        re.IGNORECASE
    )

    if github_match:
        contact_items.append(
            github_match.group(0)
        )

    # Location
    location_keywords = [
        "india",
        "andhra pradesh",
        "telangana",
        "vijayawada",
        "hyderabad",
        "bangalore",
        "chennai",
        "mumbai",
        "delhi"
    ]

    for line in lines[:8]:

        clean_line = remove_contact_icons(line)

        if any(
            keyword in clean_line.lower()
            for keyword in location_keywords
        ):

            if (
                "@" not in clean_line
                and "linkedin" not in clean_line.lower()
                and "github" not in clean_line.lower()
                and not re.search(r"\d{8,}", clean_line)
            ):

                contact_items.insert(
                    0,
                    clean_line
                )

                break

    # Remove duplicates
    contact_items = list(
        dict.fromkeys(contact_items)
    )

    return {
        "name": name,
        "contact": " | ".join(contact_items)
    }


# ============================================================
# DATE DETECTION
# ============================================================

def looks_like_date_line(line):

    line_lower = line.lower()

    patterns = [

        r"\b(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|september|oct|october|nov|november|dec|december)\b",

        r"\b(19|20)\d{2}\b",

        r"\bto\b",

        r"\bpresent\b",

        r"\bcurrent\b"
    ]

    return any(
        re.search(pattern, line_lower)
        for pattern in patterns
    )


# ============================================================
# EDUCATION METADATA DETECTION
# ============================================================

def looks_like_education_metadata(line):

    keywords = [

        "cgpa",

        "gpa",

        "percentage",

        "%",

        "college",

        "university",

        "school",

        "institute"
    ]

    line_lower = line.lower()

    return (
        looks_like_date_line(line)
        or any(
            keyword in line_lower
            for keyword in keywords
        )
    )


# ============================================================
# PROJECT DESCRIPTION DETECTION
# ============================================================

def looks_like_description(line):
    """
    Detect paragraph-style descriptions.

    This is what allows the system to work when
    the original resume has NO bullet symbols.
    """

    line_lower = line.lower().strip()

    if not line_lower:
        return False

    # Explicit technologies line is project metadata, not a bullet.
    if line_lower.startswith("technologies"):
        return False

    if line_lower.startswith("tools used"):
        return True

    if line_lower.startswith("skills used"):
        return True

    if line_lower.startswith("environment"):
        return True

    # Common resume action verbs
    action_verbs = [

        "developed",

        "built",

        "created",

        "implemented",

        "designed",

        "analyzed",

        "cleaned",

        "transformed",

        "worked",

        "assisted",

        "collaborated",

        "tested",

        "optimized",

        "managed",

        "automated",

        "integrated",

        "used",

        "improved",

        "maintained",

        "performed",

        "conducted",

        "identified",

        "generated",

        "prepared",

        "supported",

        "responsible",

        "participated",

        "secured"
    ]

    first_word = line_lower.split()[0] if line_lower.split() else ""

    if first_word in action_verbs:
        return True

    # Longer sentence ending in punctuation
    if (
        len(line.split()) >= 5
        and line[-1] in ".!?"
    ):
        return True

    return False


# ============================================================
# ROLE DETECTION
# ============================================================

def looks_like_role_or_job_title(line):

    line_lower = line.lower()

    role_words = [

        "intern",

        "developer",

        "engineer",

        "analyst",

        "associate",

        "trainee",

        "executive",

        "manager",

        "specialist",

        "consultant"
    ]

    return any(
        word in line_lower
        for word in role_words
    )


# ============================================================
# PROJECT TITLE DETECTION
# ============================================================

def looks_like_project_title(line):

    if not line:
        return False

    if is_bullet_line(line):
        return False

    # Long sentences are probably descriptions
    if len(line.split()) > 14:
        return False

    # Explicit description should not become title
    if looks_like_description(line):
        return False

    # Technology lines are not titles
    if line.lower().startswith("technologies"):
        return False

    if line.lower().startswith("tools used"):
        return False

    return True


# ============================================================
# PROJECT TECHNOLOGY METADATA
# ============================================================

def extract_project_metadata(line):
    """Extract technology/tool metadata from a project line."""
    if not line:
        return ""

    patterns = [
        r"^technologies\s*:\s*(.+)$",
        r"^technology\s*:\s*(.+)$",
        r"^tech\s*stack\s*:\s*(.+)$",
        r"^tools\s*used\s*:\s*(.+)$",
        r"^tools\s*:\s*(.+)$",
        r"^skills\s*used\s*:\s*(.+)$",
        r"^environment\s*:\s*(.+)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return ""


# ============================================================
# PARSE PROJECTS
# ============================================================

def parse_projects(lines):
    """
    Supports:

    FORMAT A
    --------
    Project Name
    • Built...
    • Used...

    FORMAT B
    --------
    Project Name
    Built...
    Used...

    FORMAT C
    --------
    Project Name | Python
    Built...
    """

    projects = []

    current_project = None

    current_bullet = None


    def save_bullet():

        nonlocal current_bullet

        if (
            current_project is not None
            and current_bullet
        ):

            cleaned = clean_resume_bullet(
                current_bullet
            )

            if cleaned:
                current_project["bullets"].append(
                    cleaned
                )

        current_bullet = None


    def save_project():

        nonlocal current_project

        save_bullet()

        if current_project is None:
            return

        title = current_project.get(
            "title",
            ""
        ).strip()

        bullets = current_project.get(
            "bullets",
            []
        )

        if title or bullets:

            projects.append({
                "title": title,
                "technologies": current_project.get("technologies", ""),
                "bullets": bullets
            })

        current_project = None


    for raw_line in lines:

        line = normalize_line(raw_line)

        if not line:
            continue

        # Keep project technology metadata separate from bullets.
        metadata = extract_project_metadata(line)
        if metadata:
            if current_project is None:
                current_project = {
                    "title": "",
                    "technologies": "",
                    "bullets": []
                }
            current_project["technologies"] = metadata
            continue


        # ----------------------------------------------------
        # EXPLICIT BULLET
        # ----------------------------------------------------

        if is_bullet_line(line):

            if current_project is None:

                current_project = {
                    "title": "",
                    "technologies": "",
                    "bullets": []
                }

            save_bullet()

            current_bullet = clean_bullet_marker(
                line
            )

            continue


        # ----------------------------------------------------
        # WRAPPED EXPLICIT BULLET
        # ----------------------------------------------------

        if current_bullet is not None:

            # New project title detected
            if (
                looks_like_project_title(line)
                and not looks_like_description(line)
            ):

                save_bullet()
                save_project()

                current_project = {
                    "title": line,
                    "technologies": "",
                    "bullets": []
                }

            else:

                current_bullet += " " + line

            continue


        # ----------------------------------------------------
        # NO CURRENT PROJECT
        # ----------------------------------------------------

        if current_project is None:

            current_project = {
                "title": line,
                "technologies": "",
                "bullets": []
            }

            continue


        # ----------------------------------------------------
        # PARAGRAPH DESCRIPTION
        # ----------------------------------------------------

        if looks_like_description(line):

            current_project["bullets"].append(
                clean_resume_bullet(line)
            )

            continue


        # ----------------------------------------------------
        # NEW PROJECT TITLE
        # ----------------------------------------------------

        if (
            looks_like_project_title(line)
            and current_project["bullets"]
        ):

            save_project()

            current_project = {
                "title": line,
                "bullets": []
            }

            continue


        # ----------------------------------------------------
        # CONTINUATION / WRAPPED LINE
        # ----------------------------------------------------

        if current_project["bullets"]:

            current_project["bullets"][-1] = (

                current_project["bullets"][-1]
                .rstrip(".")
                + " "
                + line
            )

            current_project["bullets"][-1] = clean_resume_bullet(
                current_project["bullets"][-1]
            )

        else:

            # Metadata or continuation of title
            current_project["title"] += " | " + line


    save_project()

    return remove_duplicate_entries(projects)


# ============================================================
# PARSE INTERNSHIPS / EXPERIENCE
# ============================================================

def parse_experience_entries(lines):
    """
    Handles both bullet resumes and paragraph resumes.

    Example:

    Software Development Intern – Company
    May 2025 – July 2025

    Assisted in developing...
    Worked with Python...
    Collaborated with team...

    becomes:

    TITLE:
    Software Development Intern – Company | May 2025 – July 2025

    BULLETS:
    • Assisted...
    • Worked...
    • Collaborated...
    """

    entries = []

    current_entry = None

    current_bullet = None


    def save_bullet():

        nonlocal current_bullet

        if (
            current_entry is not None
            and current_bullet
        ):

            cleaned = clean_resume_bullet(
                current_bullet
            )

            if cleaned:
                current_entry["bullets"].append(
                    cleaned
                )

        current_bullet = None


    def save_entry():

        nonlocal current_entry

        save_bullet()

        if current_entry is None:
            return

        title = current_entry.get(
            "title",
            ""
        ).strip()

        bullets = current_entry.get(
            "bullets",
            []
        )

        if title or bullets:

            entries.append({
                "title": title,
                "bullets": bullets
            })

        current_entry = None


    for raw_line in lines:

        line = normalize_line(raw_line)

        if not line:
            continue


        # ----------------------------------------------------
        # EXPLICIT BULLET
        # ----------------------------------------------------

        if is_bullet_line(line):

            if current_entry is None:

                current_entry = {
                    "title": "",
                    "bullets": []
                }

            save_bullet()

            current_bullet = clean_bullet_marker(
                line
            )

            continue


        # ----------------------------------------------------
        # WRAPPED BULLET
        # ----------------------------------------------------

        if current_bullet is not None:

            if (
                looks_like_role_or_job_title(line)
                and not looks_like_description(line)
            ):

                save_bullet()
                save_entry()

                current_entry = {
                    "title": line,
                    "bullets": []
                }

            else:

                current_bullet += " " + line

            continue


        # ----------------------------------------------------
        # FIRST ENTRY
        # ----------------------------------------------------

        if current_entry is None:

            current_entry = {
                "title": line,
                "bullets": []
            }

            continue


        # ----------------------------------------------------
        # DATE / COMPANY METADATA
        # ----------------------------------------------------

        if (
            looks_like_date_line(line)
            and not current_entry["bullets"]
        ):

            current_entry["title"] += " | " + line

            continue


        # ----------------------------------------------------
        # PARAGRAPH DESCRIPTION
        # ----------------------------------------------------

        if looks_like_description(line):

            current_entry["bullets"].append(
                clean_resume_bullet(line)
            )

            continue


        # ----------------------------------------------------
        # NEW ROLE
        # ----------------------------------------------------

        if (
            looks_like_role_or_job_title(line)
            and current_entry["bullets"]
        ):

            save_entry()

            current_entry = {
                "title": line,
                "bullets": []
            }

            continue


        # ----------------------------------------------------
        # COMPANY / METADATA
        # ----------------------------------------------------

        if not current_entry["bullets"]:

            current_entry["title"] += " | " + line

        else:

            # Wrapped description
            current_entry["bullets"][-1] = (

                current_entry["bullets"][-1]
                .rstrip(".")
                + " "
                + line
            )

            current_entry["bullets"][-1] = clean_resume_bullet(
                current_entry["bullets"][-1]
            )


    save_entry()

    return remove_duplicate_entries(entries)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicate_entries(entries):

    cleaned = []

    seen = set()

    for entry in entries:

        title = entry.get(
            "title",
            ""
        ).strip()

        technologies = entry.get(
            "technologies",
            ""
        )

        bullets = entry.get(
            "bullets",
            []
        )

        key = (
            title.lower(),
            technologies.lower(),
            tuple(
                bullet.lower()
                for bullet in bullets
            )
        )

        if key in seen:
            continue

        seen.add(key)

        cleaned.append({
            "title": title,
            "technologies": technologies,
            "bullets": bullets
        })

    return cleaned


# ============================================================
# PARSE EDUCATION
# ============================================================

def parse_education(lines):
    """
    Groups education instead of simply pasting raw text.
    """

    education = []

    current_item = []

    for raw_line in lines:

        line = normalize_line(raw_line)

        if not line:
            continue

        # A new degree usually starts a new education item
        degree_keywords = [

            "bachelor",

            "master",

            "b.tech",

            "m.tech",

            "bsc",

            "msc",

            "b.e",

            "intermediate",

            "diploma",

            "secondary",

            "ssc",

            "higher secondary"
        ]

        is_new_degree = any(
            keyword in line.lower()
            for keyword in degree_keywords
        )

        if is_new_degree and current_item:

            education.append(
                " | ".join(current_item)
            )

            current_item = []

        current_item.append(line)

    if current_item:

        education.append(
            " | ".join(current_item)
        )

    return education


# ============================================================
# PARSE SIMPLE LIST SECTION
# ============================================================

def parse_simple_list(lines):

    items = []

    current_item = None

    for raw_line in lines:

        line = normalize_line(raw_line)

        if not line:
            continue

        line = clean_bullet_marker(line)

        if line:

            items.append(line)

    return list(
        dict.fromkeys(items)
    )

def parse_soft_skills(lines):

    soft_skills = []

    for raw_line in lines:

        line = normalize_line(raw_line)

        if not line:
            continue

        line = clean_bullet_marker(line)

        # If skills are written like:
        # Communication, Teamwork, Problem Solving

        if "," in line:

            skills = line.split(",")

            for skill in skills:

                skill = skill.strip()

                if skill:
                    soft_skills.append(skill)

        else:

            soft_skills.append(line)

    # Remove duplicates
    return list(dict.fromkeys(soft_skills))

def extract_languages_from_personal_details(lines):

    languages = []

    for raw_line in lines:

        line = normalize_line(raw_line)

        if not line:
            continue

        line_lower = line.lower()

        # Example:
        # Languages Known: English, Telugu, Hindi

        if (
            "languages known" in line_lower
            or line_lower.startswith("languages:")
            or line_lower.startswith("language:")
        ):

            if ":" in line:

                language_text = line.split(
                    ":",
                    1
                )[1]

                for language in language_text.split(","):

                    language = language.strip()

                    if language:
                        languages.append(language)

    return list(dict.fromkeys(languages))



# ============================================================
# GET MASTER RESUME SKILLS
# ============================================================

# ============================================================
# NORMALIZE SECTION HEADING
# ============================================================

def normalize_section_heading(text):

    if not text:
        return ""

    text = str(text).strip().lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()

def parse_skills_section(lines):
    """Parse only the explicit SKILLS section and group skills by matcher taxonomy."""

    declared_skills = []

    for raw_line in lines or []:
        line = normalize_line(raw_line)
        if not line:
            continue

        # Remove common labels such as "Programming:" or "Skills:" while
        # preserving the actual skill values.
        if ":" in line:
            prefix, value = line.split(":", 1)

            normalized_prefix = re.sub(
                r"[^a-z0-9]+",
                " ",
                prefix.strip().lower()
            )

            normalized_prefix = re.sub(
                r"\s+",
                " ",
                normalized_prefix
            ).strip()

            if normalized_prefix in {
                "skills",
                "technical skills",
                "technical skill",
                "key skills",
                "core skills",
                "core competencies",
                "technical competencies",
                "skills and tools",
                "programming",
                "databases",
                "data analytics",
                "libraries",
                "other",
                "tools",
                "technologies",
                "technology",
                "tech stack",
                "skills used",
                "environment"
            }:
                line = value.strip()

        line = re.sub(r"^[\u2022*\-–—]+\s*", "", line).strip()
        if not line:
            continue

        # Support comma/semicolon/pipe separated skill dumps.
        parts = re.split(r"\s*[|,;]\s*", line)
        for part in parts:
            part = part.strip()
            if part:
                declared_skills.append(part)

    # Preserve candidate order while removing duplicates.
    unique_declared = []
    seen = set()
    for skill in declared_skills:
        key = re.sub(r"\s+", " ", skill.lower()).strip()
        if key not in seen:
            seen.add(key)
            unique_declared.append(skill)

    categorized = {}
    taxonomy_order = list(TAXONOMY_MAP.keys())

    for declared in unique_declared:
        detected = search_skills(declared)
        for category in taxonomy_order:
            matched = detected.get(category, [])
            if matched:
                bucket = categorized.setdefault(category, [])
                for skill in matched:
                    if skill not in bucket:
                        bucket.append(skill)
                break

    # Keep explicitly declared skills that are outside the current taxonomy.
    recognized = {skill for skills in categorized.values() for skill in skills}
    other = [skill for skill in unique_declared if skill not in recognized]
    if other:
        categorized["Other Skills"] = other

    return categorized


def get_master_resume_skills(master_text):
    """Return skills only from the explicit SKILLS section."""
    sections = parse_resume_sections(master_text)
    return parse_skills_section(sections.get("SKILLS", []))


# ============================================================
# GET RELEVANT EXISTING SKILLS
# ============================================================

def get_relevant_existing_skills(
    master_skills,
    jd_text
):

    jd_skills = search_skills(jd_text)

    jd_skill_set = set()

    for skills in jd_skills.values():

        jd_skill_set.update(skills)

    relevant = {}

    for category, skills in master_skills.items():

        matched = [
            skill
            for skill in skills
            if skill in jd_skill_set
        ]

        if matched:

            relevant[category] = matched

    return relevant


# ============================================================
# ENTRY RELEVANCE
# ============================================================

def calculate_entry_relevance(
    entry,
    jd_text
):

    entry_text = (
        entry.get("title", "")
        + " "
        + " ".join(
            entry.get("bullets", [])
        )
    )

    entry_skills_dict = search_skills(
        entry_text
    )

    jd_skills_dict = search_skills(
        jd_text
    )

    entry_skills = set()
    jd_skills = set()

    for skills in entry_skills_dict.values():
        entry_skills.update(skills)

    for skills in jd_skills_dict.values():
        jd_skills.update(skills)

    return len(
        entry_skills.intersection(jd_skills)
    )


# ============================================================
# SORT ENTRIES
# ============================================================

def sort_entries_by_relevance(
    entries,
    jd_text
):

    return sorted(
        entries,
        key=lambda entry: calculate_entry_relevance(
            entry,
            jd_text
        ),
        reverse=True
    )


# ============================================================
# DETECT TARGET ROLE
# ============================================================

def detect_target_role(jd_text):

    if not jd_text:
        return "Target Role"

    jd_lower = jd_text.lower()

    roles = [

        ("data analyst", "Data Analyst"),

        ("business analyst", "Business Analyst"),

        ("data engineer", "Data Engineer"),

        ("data scientist", "Data Scientist"),

        ("software developer", "Software Developer"),

        ("software engineer", "Software Engineer"),

        ("python developer", "Python Developer"),

        ("backend developer", "Backend Developer"),

        ("frontend developer", "Frontend Developer"),

        ("full stack developer", "Full Stack Developer"),

        ("machine learning engineer", "Machine Learning Engineer"),

        ("ai engineer", "AI Engineer")
    ]

    for keyword, role in roles:

        if keyword in jd_lower:
            return role

    return "Target Role"


# ============================================================
# BUILD DETAILED SUMMARY
# ============================================================

def build_detailed_summary(
    target_role,
    master_skills,
    matched_skills,
    projects,
    internships,
    is_fresher=True
):
    """
    Creates a 3-4 sentence summary.

    IMPORTANT:
    Only uses:
    - Skills detected from Master Resume
    - Existing projects
    - Existing internships

    No fake skills.
    No fake experience.
    """

    all_skills = []

    for skills in master_skills.values():

        all_skills.extend(skills)

    # Prefer skills that are explicitly matched to the JD.
    # Then add other skills from the Master Resume.
    # Do not invent skills or use a hard-coded six-skill cutoff.
    priority_skills = []

    for skill in matched_skills:
        if skill in all_skills and skill not in priority_skills:
            priority_skills.append(skill)

    for skill in all_skills:
        if skill not in priority_skills:
            priority_skills.append(skill)

    # Keep the summary readable while allowing more than six skills.
    # The Technical Skills section remains the complete source of truth.
    priority_skills = priority_skills[:10]

    skills_text = ", ".join(priority_skills)

    project_text = ""

    if projects:

        project_names = []

        for project in projects[:2]:

            title = project.get(
                "title",
                ""
            )

            if title:

                project_names.append(
                    title.split("|")[0].strip()
                )

        if project_names:

            project_text = (
                ", ".join(project_names)
            )

    internship_text = ""

    if internships:

        internship_title = internships[0].get(
            "title",
            ""
        )

        if internship_title:

            internship_text = internship_title.split(
                "|"
            )[0].strip()

    sentences = []

    # Sentence 1
    if is_fresher:

        sentences.append(
            f"Motivated entry-level {target_role} candidate "
            f"with a foundation in computer science and "
            f"hands-on exposure through academic projects and "
            f"practical learning."
        )

    else:

        sentences.append(
            f"{target_role} candidate with relevant technical "
            f"experience and practical project exposure."
        )

    # Sentence 2
    if skills_text:

        sentences.append(
            f"Skilled in {skills_text}."
        )

    # Sentence 3
    if project_text:

        sentences.append(
            f"Developed projects including {project_text}, "
            f"applying technical knowledge to practical "
            f"problem-solving and implementation."
        )

    # Sentence 4
    if internship_text:

        sentences.append(
            f"Gained additional practical exposure through the "
            f"{internship_text} experience, working with "
            f"real-world development and team-based tasks."
        )

    # Final sentence if needed
    if len(sentences) < 4:

        sentences.append(
            f"Seeking an opportunity to contribute existing "
            f"skills, learn from experienced professionals, "
            f"and grow in a {target_role} role."
        )

    return " ".join(
        sentences[:4]
    )


# ============================================================
# GENERATE TAILORED RESUME
# ============================================================

def generate_tailored_resume(
    master_text,
    matched_skills,
    job_description,
    is_fresher=True
):

    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    contact_info = extract_contact_info(
        master_text
    )

    # --------------------------------------------------------
    # TARGET ROLE
    # --------------------------------------------------------

    target_role = detect_target_role(
        job_description
    )

    # --------------------------------------------------------
    # SECTIONS
    # --------------------------------------------------------

    sections = parse_resume_sections(
        master_text
    )

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    projects = parse_projects(
        sections.get(
            "PROJECTS",
            []
        )
    )

    # --------------------------------------------------------
    # INTERNSHIPS
    # --------------------------------------------------------

    internships = parse_experience_entries(
        sections.get(
            "INTERNSHIPS",
            []
        )
    )

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    experience = parse_experience_entries(
        sections.get(
            "EXPERIENCE",
            []
        )
    )

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    education = parse_education(
        sections.get(
            "EDUCATION",
            []
        )
    )

    # --------------------------------------------------------
    # CERTIFICATIONS
    # --------------------------------------------------------

    certifications = parse_simple_list(
        sections.get(
            "CERTIFICATIONS",
            []
        )
    )

    # --------------------------------------------------------
    # ACHIEVEMENTS
    # --------------------------------------------------------

    achievements = parse_simple_list(
        sections.get(
            "ACHIEVEMENTS",
            []
        )
    )
    # --------------------------------------------------------
    # SOFT SKILLS
    # STRICTLY FROM MASTER RESUME
    # --------------------------------------------------------

    soft_skills = parse_soft_skills(
        sections.get(
            "SOFT_SKILLS",
            []
        )
    )


    # --------------------------------------------------------
    # LANGUAGES
    # FROM LANGUAGES SECTION
    # --------------------------------------------------------

    languages = parse_simple_list(
        sections.get(
            "LANGUAGES",
            []
        )
    )


    # --------------------------------------------------------
    # LANGUAGES INSIDE PERSONAL DETAILS
    #
    # Example:
    # Languages Known: English, Telugu, Hindi
    # --------------------------------------------------------

    personal_languages = (
        extract_languages_from_personal_details(
            sections.get(
                "PERSONAL_DETAILS",
                []
            )
        )
    )


    # Combine both and remove duplicates

    languages = list(
        dict.fromkeys(
            languages + personal_languages
        )
    )

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------
    #
    # STRICT:
    # Skills ONLY from Master Resume
    # --------------------------------------------------------

    master_skills = get_master_resume_skills(
        master_text
    )

    relevant_existing_skills = (
        get_relevant_existing_skills(
            master_skills,
            job_description
        )
    )

    # --------------------------------------------------------
    # SORT PROJECTS / INTERNSHIPS
    # --------------------------------------------------------

    projects = sort_entries_by_relevance(
        projects,
        job_description
    )

    internships = sort_entries_by_relevance(
        internships,
        job_description
    )

    experience = sort_entries_by_relevance(
        experience,
        job_description
    )

    # --------------------------------------------------------
    # DETAILED SUMMARY
    # --------------------------------------------------------

    summary = build_detailed_summary(
        target_role=target_role,
        master_skills=master_skills,
        matched_skills=matched_skills,
        projects=projects,
        internships=internships,
        is_fresher=is_fresher
    )

    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    return {

        "target_role": target_role,

        "name": contact_info["name"],

        "contact": contact_info["contact"],

        "summary": summary,

        "skills": master_skills,

        "relevant_skills": relevant_existing_skills,

        "soft_skills": soft_skills,

        "languages": languages,

        "internships": internships,

        "experience": experience,

        "projects": projects,

        "education": education,

        "certifications": certifications,

        "achievements": achievements
    }