import re
import pandas as pd
import streamlit as st

from extractor import extract_text_from_file
from matcher import compare_resume_to_jd
from tailorer import generate_tailored_resume
from pdf_builder import build_pdf_resume
from hr_matcher import rank_candidates, get_candidate_status


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AlignIQ - Smart Resume Alignment",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded")


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
        .aligniq-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.05;
        margin: 0;
    }

    .aligniq-subtitle {
        text-align: center;
        font-size: 1.05rem;
        font-weight: 500;
        opacity: 0.72;
        margin-top: 5px;
        margin-bottom: 5px;
    }

    .aligniq-note {
        text-align: center;
        font-size: 0.82rem;
        opacity: 0.62;
        margin-bottom: 14px;
    }

    /* ---------- WHOLE PAGE ---------- */

    .stApp {
        background-color: #D8EBF0;
        color: #000000; 
    }


    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background-color: #D8EBD0;
        color: #000000;
    }

    /* ---------- HEADINGS ---------- */

    h1, h2, h3, h4, h5, h6 {
        color: #00000;
    }


    /* ---------- NORMAL TEXT ---------- */

    .stMarkdown,
    .stCaption,
    label,
    p {
        color: #000000;
    }

    /* ---------- TEXT AREAS ---------- */

    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #6E658B;
        border-radius: 10px;
    }


    /* Text area placeholder */

    div[data-testid="stTextArea"] textarea::placeholder {
        color: #6E658B;
        opacity: 0.75;
    }


    /* Text area focus */

    div[data-testid="stTextArea"] textarea:focus {
        border-color: #CDDCD1;
        box-shadow: 0 0 0 1px #CDDCD1;
    }


    /* ---------- BUTTONS ---------- */

    div[data-testid="stButton"] > button {
        background-color: #D8EBF0;
        color: #000000;
        border: none;
        border-radius: 1px;
        font-weight: 650;
    }


    /* Button hover */

    div[data-testid="stButton"] > button:hover {
        background-color: #E9EBF0;
        color: #000000;
        border-color: #CDDCD1;
    }


    /* ---------- PRIMARY BUTTON ---------- */

    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #8E86C3;
        color: #000000;
        border: none;
        border-radius: 10px;
        font-weight: 650;
    }


    /* Primary button hover */

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #CEDCD9;
        color: #000000;
    }

    /* Download PDF button */
    div[data-testid="stDownloadButton"] > button {
        background-color: #8E86C3 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px;
        font-weight: 650;
    }

    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #CEDCD9 !important;
        color: #FFFFFF !important;
    }

    /* ---------- RADIO BUTTONS ---------- */

    div[data-testid="stRadio"] {
        color: #CDDCD1;
    }

    /* Selected radio accent */

    div[data-testid="stRadio"] input:checked + div {
        border-color: #CDDCD1;
    }


    /* ---------- SLIDER ---------- */

    /* Slider track */

    div[data-testid="stSlider"] [data-baseweb="slider"] div {
        color: #000000;
    }


    /* ---------- METRIC CARDS ---------- */

    div[data-testid="stMetric"] {
        background-color: #CDDCD1; 
        border: 1px solid #CDDCD1;
        border-radius: 12px;
        padding: 10px 12px;
    }

    /* ---------- FILE UPLOADER ---------- */

    div[data-testid="stFileUploader"] {
        background-color: #FFFFF0
        border-radius: 10px;
    }

    /* ---------- ALERT / INFO CARDS ---------- */

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }


    /* ---------- DIVIDERS ---------- */

    hr {
        border-color: #CDDCD1;
        opacity: 0.5;
    }

    .matched-skill {
            display: inline-block;
            background-color: #d1fae5;
            color: #065f46;
            padding: 6px 14px;
            margin: 4px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid #a7f3d0;
        }
    .missing-skill {
            display: inline-block;
            background-color: #fee2e2;
            color: #991b1b;
            padding: 6px 14px;
            margin: 4px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid #fecaca;

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.18);
        border-radius: 12px;
        padding: 10px 12px;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


# Initialize session state for persistent results
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = None
if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = ""
if "tailored_data" not in st.session_state:
    st.session_state["tailored_data"] = None

# 3. Sidebar: Settings & Controls

# ============================================================
# SESSION STATE
# ============================================================

if "results" not in st.session_state:
    st.session_state["results"] = None


if "tailored_resume" not in st.session_state:
    st.session_state["tailored_resume"] = None


if "master_resume_text" not in st.session_state:
    st.session_state["master_resume_text"] = ""


if "hr_results" not in st.session_state:
    st.session_state["hr_results"] = None

if "has_candidate_skills_section" not in st.session_state:
    st.session_state["has_candidate_skills_section"] = False



# ============================================================
# CHECK FOR AN EXPLICIT SKILLS SECTION
# ============================================================

def has_explicit_skills_section(resume_text):
    """
    Returns True only when the Master Resume contains a
    dedicated Skills heading.

    Skills mentioned inside Summary, Projects, Experience,
    Education, etc. do not count as a Skills section.
    """

    if not resume_text:
        return False

    return bool(
        re.search(
            r"(?im)^\s*(?:"
            r"skills|"
            r"technical\s+skills|"
            r"technical\s+skill|"
            r"key\s+skills|"
            r"core\s+skills|"
            r"core\s+competencies|"
            r"technical\s+competencies|"
            r"skills\s+and\s+tools"
            r")\s*:?\s*$",
            str(resume_text)
        )
    )


# ============================================================
# HEADER
# ============================================================
st.title("🎯 AlignIQ")
st.markdown("#### *Smart Resume Matcher & Tailoring Engine*")
st.caption("Upload your Master Resume, paste the Job Description, and get an instant alignment audit.")

# ============================================================
# MODE SELECTION
# ============================================================

mode = st.radio(
    "Choose Mode",
    [
        "🎓 Candidate Mode",
        "🏢 HR Mode"
    ],
    horizontal=True
)

# 3. Sidebar: Settings & Controls
with st.sidebar:
    st.image("https://api.iconify.design/fluent-emoji:bullseye.svg", width=64)
    st.title("AlignIQ Settings")
    
    match_threshold = st.slider(
        "Target Match Threshold (%)",
        min_value=0,
        max_value=100,
        value=70,
        step=5,
        help="Target percentage required for a strong candidate recommendation."
    )
    st.divider()

    if st.button(
        "🧹 Clear Results",
        use_container_width=True
    ):

        st.session_state["results"] = None
        st.session_state["tailored_resume"] = None
        st.session_state["hr_results"] = None

        st.rerun()
    
    st.divider()

    st.markdown("### 📌 Alignment Principles")
    
    if mode == "🎓 Candidate Mode":
        st.info(
            "**Master Resume is Source of Truth**\n\n"
            "AlignIQ evaluates your real skills against the Job Description and never invents experience or achievements."
        )
    else:
        st.info(
            "**Resume Screening Principle**\n\n"
            "AlignIQ compares each candidate resume with the Job Description. The match score is a screening aid, not a final hiring decision."
        )


# ============================================================
# ============================================================
# CANDIDATE MODE
# ============================================================
# ============================================================

if mode == "🎓 Candidate Mode":

    # ========================================================
    # INPUT SECTION
    # ========================================================

    left_column, right_column = st.columns(
        2
    )


    # ========================================================
    # MASTER RESUME
    # ========================================================

    with left_column:

        st.markdown(
            "### 📄 Master Resume"
        )

        st.markdown(
            "**Paste your Master Resume as clean, plain text.** "
            "Keep each section heading on its own line and bullet points on separate lines for accurate section detection."
        )

        st.caption(
            "Tip: Avoid tables, multi-column layouts, icons, or merged lines. "
        )

        pasted_text = st.text_area(
            "Paste Master Resume",
            height=250,
            key="candidate_resume_text",
            placeholder="Paste your full master resume content (Name, Contact, Education, Skills, Experience, Projects..."
            )

        career_level = st.radio(
            "Your Career Level:",
            ["🎓 Fresher / Entry-Level (0-1 yrs)", "💼 Experienced Professional (2+ yrs)"],
            index=0,
            horizontal=True,
            help="Select Fresher for an academic-grounded, project-focused summary."
        )


    # ========================================================
    # JOB DESCRIPTION
    # ========================================================

    with right_column:

        st.markdown(
            "### 📋 Job Description"
        )


        job_description = st.text_area(
            "Paste Job Description",
            height=355,
            key="candidate_job_description",
            placeholder="Paste requirements, qualifications, and role responsibilities here...",
        )

    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    st.write("")


    analyze = st.button(
        "🚀 Analyze Resume",
        type="primary",
        use_container_width=True,
        key="candidate_analyze_button"
    )

    # ========================================================
    # ANALYZE RESUME
    # ========================================================

    if analyze:

        # ----------------------------------------------------
        # CLEAR PREVIOUS ANALYSIS
        # ----------------------------------------------------

        st.session_state["results"] = None
        st.session_state["tailored_resume"] = None
        st.session_state["tailored_data"] = None

        # ----------------------------------------------------
        # GET INPUT VALUES
        # ----------------------------------------------------

        master_resume_text = pasted_text.strip()
        job_description_text = job_description.strip()

        # ----------------------------------------------------
        # VALIDATE INPUTS
        # ----------------------------------------------------

        if not master_resume_text and not job_description_text:

            st.error(
                "Please enter both your Master Resume and Job Description."
            )

        elif not master_resume_text:

            st.error(
                "Please paste your Master Resume text."
            )

        elif not job_description_text:

            st.error(
                "Please paste the Job Description."
            )

        # ----------------------------------------------------
        # PROCESS RESUME
        # ----------------------------------------------------

        else:

            try:

                with st.spinner(
                    "Analyzing resume and generating tailored version..."
                ):

                    # ------------------------------------------------
                    # SAVE MASTER RESUME
                    # ------------------------------------------------

                    st.session_state[
                        "master_resume_text"
                    ] = master_resume_text

                    # ------------------------------------------------
                    # COMPARE RESUME WITH JD
                    # ------------------------------------------------

                    results = compare_resume_to_jd(
                        master_resume_text,
                        job_description_text
                    )
                    if results is not None:

                        if results["total_jd_skills"] == 0:

                            st.warning(
                                "⚠️ No recognized skills detected in the Job Description. "
                                "Try adding standard technical/professional keywords."
                            )

                            st.session_state["results"] = None
                            st.session_state["tailored_resume"] = None
                            st.session_state["master_resume_text"] = ""

                            st.stop()

                    # ------------------------------------------------
                    # SKILLS SECTION CHECK
                    # ------------------------------------------------
                    has_skills_section = has_explicit_skills_section(
                        master_resume_text
                    )

                    # Check whether the Skills section actually contains skills
                    has_candidate_skills = bool(
                        results.get("resume_skills")
                    )

                    # Save this separately so the UI knows whether
                    # Skills Breakdown is applicable.
                    st.session_state[
                        "has_candidate_skills_section"
                    ] = has_skills_section

                    # IMPORTANT:
                    # If the Master Resume has NO dedicated Skills
                    # section, do not show skills detected from
                    # Projects, Summary, Experience, etc. as the
                    # candidate's declared skills.
                    if not has_skills_section:
                        st.warning(
                            "⚠️ No dedicated Skills section found in the Master Resume. "
                            "Please add a Skills section so AlignIQ can evaluate your skills against the Job Description."
                        )
                        st.session_state["results"] = None
                        st.session_state["tailored_resume"] = None
                        st.stop()
                        
                    if not has_candidate_skills:

                        st.warning(
                            "⚠️ Your Skills section is empty. "
                            "Please add at least one skill to your Master Resume before analyzing."
                        )

                        st.session_state["results"] = None
                        st.session_state["tailored_resume"] = None

                        st.stop()

                    if not has_candidate_skills:
                        st.warning(
                            "⚠️ Your Skills section is empty. "
                            "Please add at least one skill to your Master Resume before analyzing."
                        )
                        st.session_state["results"] = None
                        st.session_state["tailored_resume"] = None
                        st.stop()

                    # All validation passed
                    st.success(
                        "🎉 Alignment audit & Tailored Resume ready!"
                    )

                    st.divider()

                    st.session_state["results"] = results

                    # ------------------------------------------------
                    # CAREER LEVEL
                    # ------------------------------------------------

                    is_fresher = (
                        career_level.startswith("🎓 Fresher")
                    )

                    # ------------------------------------------------
                    # GENERATE TAILORED RESUME
                    # ------------------------------------------------

                    tailored_resume = generate_tailored_resume(
                        master_resume_text,
                        results.get(
                            "matched",
                            []
                        ),
                        job_description_text,
                        is_fresher=is_fresher
                    )

                    st.session_state[
                        "tailored_resume"
                    ] = tailored_resume

            except Exception as error:

                st.error(
                    "Something went wrong while analyzing the resume."
                )

                st.exception(error)

    # ========================================================
    # GET SAVED RESULTS
    # ========================================================

    results = st.session_state.get(
        "results"
    )


    tailored_resume = st.session_state.get(
        "tailored_resume"
    )


    # ========================================================
    # HELPER FUNCTIONS
    # ========================================================

    def clean_list(items):

        if not items:
            return []


        if isinstance(
            items,
            str
        ):

            items = [
                items
            ]


        cleaned_items = []


        for item in items:

            item = str(
                item
            ).strip()


            if item:

                cleaned_items.append(
                    item
                )


        # Remove duplicates while preserving order

        return list(
            dict.fromkeys(
                cleaned_items
            )
        )


    # ========================================================
    # HELPER:
    # DISPLAY SIMPLE SECTION
    # ========================================================

    def show_simple_section(
        title,
        items,
        one_line=False
    ):

        items = clean_list(
            items
        )


        if not items:
            return


        st.markdown(
            f"### {title}"
        )


        # ----------------------------------------------------
        # DISPLAY ON ONE LINE
        # ----------------------------------------------------

        if one_line:

            st.write(
                " • ".join(
                    items
                )
            )


        # ----------------------------------------------------
        # DISPLAY AS BULLETS
        # ----------------------------------------------------

        else:

            for item in items:

                st.markdown(
                    f"• {item}"
                )


    # ========================================================
    # HELPER:
    # DISPLAY SKILLS
    # ========================================================

    def show_skills(
        skills
    ):

        if not skills:
            return


        if not isinstance(
            skills,
            dict
        ):

            return


        valid_skills_found = False


        # First check whether valid skills exist

        for category, skill_list in skills.items():

            if isinstance(
                skill_list,
                list
            ):

                if any(
                    str(skill).strip()
                    for skill in skill_list
                ):

                    valid_skills_found = True
                    break


            elif str(
                skill_list
            ).strip():

                valid_skills_found = True
                break


        if not valid_skills_found:
            return


        st.markdown(
            "### TECHNICAL SKILLS"
        )


        for category, skill_list in skills.items():

            # ------------------------------------------------
            # IF SKILLS ARE A LIST
            # ------------------------------------------------

            if isinstance(
                skill_list,
                list
            ):

                cleaned_skills = clean_list(
                    skill_list
                )


                skills_text = ", ".join(
                    cleaned_skills
                )


            # ------------------------------------------------
            # IF SKILLS ARE A STRING
            # ------------------------------------------------

            else:

                skills_text = str(
                    skill_list
                ).strip()


            if not skills_text:
                continue


            st.markdown(
                f"**{category}:** {skills_text}"
            )


    # ========================================================
    # HELPER:
    # DISPLAY INTERNSHIPS / EXPERIENCE / PROJECTS
    # ========================================================

    def show_entries(
        title,
        entries
    ):

        if not entries:
            return


        if not isinstance(
            entries,
            list
        ):

            return


        valid_entries = []


        for entry in entries:

            if not isinstance(
                entry,
                dict
            ):

                continue


            entry_title = str(
                entry.get(
                    "title",
                    ""
                )
            ).strip()

            technologies = str(
                entry.get(
                    "technologies",
                    ""
                )
            ).strip()

            bullets = entry.get(
                "bullets",
                []
            )


            if isinstance(
                bullets,
                str
            ):

                bullets = [
                    bullets
                ]


            bullets = clean_list(
                bullets
            )


            if entry_title or bullets:

                valid_entries.append(
                    {
                        "title": entry_title,
                        "technologies": technologies,
                        "bullets": bullets
                    }
                )


        if not valid_entries:
            return


        # ----------------------------------------------------
        # SECTION TITLE
        # ----------------------------------------------------

        st.markdown(
            f"### {title}"
        )

        # ----------------------------------------------------
        # DISPLAY ALL ENTRIES
        # ----------------------------------------------------

        for entry in valid_entries:

            entry_title = entry.get(
                "title",
                ""
            )
            technologies = str(
                entry.get(
                    "technologies",
                    ""
                )
            ).strip()

            bullets = entry.get(
                "bullets",
                []
            )


            # Entry Title

            if entry_title:

                st.markdown(
                    f"**{entry_title}**"
                )

            technologies = entry.get(
                "technologies",
                ""
            ).strip()

            if technologies:
                st.markdown(
                    f"**Technologies:** {technologies}"
                )

            # Bullets

            for bullet in bullets:

                bullet = str(
                    bullet
                ).strip()


                if not bullet:
                    continue


                # Remove duplicate bullet symbols

                bullet = bullet.lstrip(
                    "•●○◦▪▫►▸▹◆◇■□*-–— "
                ).strip()


                if bullet:

                    st.markdown(
                        f"• {bullet}"
                    )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    if results:

        # ====================================================
        # ALIGNMENT SUMMARY
        # ====================================================

        st.markdown(
            "## 📊 Resume Alignment Results"
        )


        score = results.get(
            "score",
            0
        )


        matched_skills = clean_list(
            results.get(
                "matched",
                []
            )
        )


        missing_skills = clean_list(
            results.get(
                "missing",
                []
            )
        )


        total_jd_skills = results.get(
            "total_jd_skills",
            0
        )
        # ====================================================
        # METRICS
        # ====================================================
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        kpi1.metric(
                    label="Match Score",
                    value=f"{score}%",
                    delta=f"{score - match_threshold}% Target"
                )

        kpi2.metric(
            label="Matched Skills",
            value=len(matched_skills),
            delta="In Resume",
            delta_color="normal"
        )

        kpi3.metric(
            label="Missing Skills",
            value=len(missing_skills),
            delta="- Gap in Resume",
            delta_color="inverse"
        )

        kpi4.metric(
            label="Total JD Skills Identified",
            value=results["total_jd_skills"]
        )

        # ====================================================
        # PROGRESS BAR
        # ====================================================

        progress_value = max(
            0,
            min(
                score / 100,
                1
            )
        )


        st.progress(
            progress_value
        )

        st.caption(
            f"Your match: {score}%  •  Selected minimum: {match_threshold}%"
        )

        # ====================================================
        # RESULT MESSAGE
        # ====================================================

        if score >= match_threshold:

            st.success(
                f"### 🟢 Strong Match ({score}%): Recommended to Apply!\n"
                f"Your Master Resume covers **{len(matched_skills)} of {results['total_jd_skills']}** key skills required by this role."
            )
        elif score >= 40:
            st.warning(
                f"### 🟡 Moderate Match ({score}%): Tailor Before Applying.\n"
                f"You have good foundational overlap ({len(matched_skills)} skills), but you are missing **{len(missing_skills)}** key terms. Review them below."
            )
        else:
            st.error(
                f"### 🔴 Low Match ({score}%): Significant Skill Gap.\n"
                f"You match {len(matched_skills)} skill(s). We suggest bridging the missing skill gaps before applying."
            )
        st.divider()


        # ====================================================
        # TABS
        # ====================================================

        has_skills_section = st.session_state.get(
            "has_candidate_skills_section",
            False
        )

        if has_skills_section:

            tab_resume, tab_skills, tab_source = st.tabs(
                [
                    "📄 Tailored Resume",
                    "🔍 Skills Breakdown",
                    "📋 Master Resume Text"
                ]
            )

        else:

            tab_resume, tab_source = st.tabs(
                [
                    "📄 Tailored Resume",
                    "📋 Master Resume Text"
                ]
            )

            tab_skills = None


        # ====================================================
        # TAB 1:
        # TAILORED RESUME
        # ====================================================

        with tab_resume:

            st.markdown(
                "## 🎯 Tailored Resume"
            )
            st.caption("Professionally aligned with the target role. No robotic boilerplate, duplicate bullets, or synthetic tags.")

            if not tailored_resume:

                st.warning(
                    "Tailored resume could not be generated."
                )

            else:

                # =================================================
                # PDF DOWNLOAD
                # =================================================

                try:

                    pdf_data = build_pdf_resume(
                        tailored_resume
                    )


                    candidate_name = str(
                        tailored_resume.get(
                            "name",
                            "Candidate"
                        )
                    ).strip()


                    candidate_name = re.sub(
                        r"[^a-zA-Z0-9]+",
                        "_",
                        candidate_name
                    ).strip(
                        "_"
                    )


                    if not candidate_name:

                        candidate_name = "Candidate"


                    filename = (
                        f"{candidate_name}_Tailored_Resume.pdf"
                    )


                    st.download_button(
                        "📥 Download PDF Resume",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )


                except Exception as error:

                    st.error(
                        "Could not generate the PDF."
                    )

                    st.exception(
                        error
                    )


                st.divider()


                # =================================================
                # HEADER
                # =================================================

                st.markdown(
                    f"# {tailored_resume.get('name', 'Candidate Name')}"
                )


                contact = tailored_resume.get(
                    "contact",
                    ""
                )


                if contact:

                    st.caption(
                        contact
                    )


                # =================================================
                # SUMMARY
                # =================================================

                summary = str(
                    tailored_resume.get(
                        "summary",
                        ""
                    )
                ).strip()


                if summary:

                    st.markdown(
                        "### PROFESSIONAL SUMMARY"
                    )


                    st.write(
                        summary
                    )


                # =================================================
                # TECHNICAL SKILLS
                # =================================================

                show_skills(
                    tailored_resume.get(
                        "skills",
                        {}
                    )
                )


                # =================================================
                # SOFT SKILLS
                #
                # Displayed on ONE line
                # =================================================

                show_simple_section(
                    "SOFT SKILLS",
                    tailored_resume.get(
                        "soft_skills",
                        []
                    ),
                    one_line=True
                )


                # =================================================
                # LANGUAGES
                #
                # Displayed on ONE line
                # =================================================

                show_simple_section(
                    "LANGUAGES",
                    tailored_resume.get(
                        "languages",
                        []
                    ),
                    one_line=True
                )


                # =================================================
                # INTERNSHIPS
                # =================================================

                show_entries(
                    "INTERNSHIPS",
                    tailored_resume.get(
                        "internships",
                        []
                    )
                )


                # =================================================
                # WORK EXPERIENCE
                # =================================================

                show_entries(
                    "WORK EXPERIENCE",
                    tailored_resume.get(
                        "experience",
                        []
                    )
                )


                # =================================================
                # PROJECTS
                # =================================================

                show_entries(
                    "PROJECTS",
                    tailored_resume.get(
                        "projects",
                        []
                    )
                )


                # =================================================
                # EDUCATION
                # =================================================

                education = clean_list(
                    tailored_resume.get(
                        "education",
                        []
                    )
                )


                if education:

                    st.markdown(
                        "### EDUCATION"
                    )


                    for item in education:

                        st.markdown(
                            f"• {item}"
                        )


                # =================================================
                # CERTIFICATIONS
                # =================================================

                show_simple_section(
                    "CERTIFICATIONS",
                    tailored_resume.get(
                        "certifications",
                        []
                    )
                )


                # =================================================
                # ACHIEVEMENTS
                # =================================================

                show_simple_section(
                    "ACHIEVEMENTS",
                    tailored_resume.get(
                        "achievements",
                        []
                    )
                )


                # =================================================
                # EXTRACURRICULAR ACTIVITIES
                # =================================================

                show_simple_section(
                    "EXTRACURRICULAR ACTIVITIES",
                    tailored_resume.get(
                        "extracurricular_activities",
                        []
                    )
                )


                # =================================================
                # ADDITIONAL INFORMATION
                # =================================================

                show_simple_section(
                    "ADDITIONAL INFORMATION",
                    tailored_resume.get(
                        "additional_information",
                        []
                    )
                )


        # ====================================================
        # TAB 2:
        # SKILLS BREAKDOWN
        # ====================================================

        if has_skills_section:

            with tab_skills:

                left_skill_column, right_skill_column = st.columns(
                    2
                )


                # ------------------------------------------------
                # MATCHED SKILLS
                # ------------------------------------------------

                with left_skill_column:

                    st.markdown(
                        "### ✅ Matched Skills"
                    )


                    if matched_skills:

                        matched_html = ""


                        for skill in matched_skills:

                            matched_html += (
                                f'<span class="matched-skill">'
                                f'{skill}'
                                f'</span>'
                            )


                        st.markdown(
                            matched_html,
                            unsafe_allow_html=True
                        )


                    else:

                        st.info(
                            "No matched skills found."
                        )


                # ------------------------------------------------
                # MISSING SKILLS
                # ------------------------------------------------

                with right_skill_column:

                    st.markdown(
                        "### ❌ Missing Skills"
                    )


                    if missing_skills:

                        missing_html = ""


                        for skill in missing_skills:

                            missing_html += (
                                f'<span class="missing-skill">'
                                f'{skill}'
                                f'</span>'
                            )


                        st.markdown(
                            missing_html,
                            unsafe_allow_html=True
                        )


                    else:

                        st.success(
                            "No missing skills found."
                        )


        # ====================================================
        # TAB 3:
        # MASTER RESUME TEXT
        # ====================================================

        with tab_source:

            master_text = st.session_state.get(
                "master_resume_text",
                ""
            )


            if master_text:

                st.text_area(
                    "Extracted Master Resume Text",
                    value=master_text,
                    height=500,
                    disabled=True
                )


            else:

                st.info(
                    "No master resume text available."
                )


else:

    # ========================================================
    # HR HEADER
    # ========================================================

    st.markdown(
        "## 🏢 HR Mode"
    )


    st.caption(
        "Upload one Job Description and multiple resumes. "
        "AlignIQ ranks resumes by resume-to-JD skill match. "
        "The score is a screening aid, not a final hiring decision."
    )


    # ========================================================
    # HR INPUT SECTION
    # ========================================================

    hr_left_column, hr_right_column = st.columns(
        2
    )


    # ========================================================
    # JOB DESCRIPTION
    # ========================================================

    with hr_left_column:

        st.markdown(
            "### 📋 Job Description"
        )


        hr_jd = st.text_area(
            "Paste Job Description",
            height=250,
            key="hr_job_description"
        )


    # ========================================================
    # CANDIDATE RESUMES
    # ========================================================

    with hr_right_column:

        st.markdown(
            "### 📄 Candidate Resumes"
        )


        hr_uploaded_files = st.file_uploader(
            "Upload Candidate Resumes",
            type=[
                "pdf",
                "docx",
                "txt"
            ],
            accept_multiple_files=True,
            key="hr_resume_uploader",
            help=(
                "Upload multiple resumes for the same Job Description."
            )
        )


        if hr_uploaded_files:

            st.caption(
                f"{len(hr_uploaded_files)} resume(s) selected"
            )


    # ========================================================
    # TARGET MATCH THRESHOLD
    # ========================================================

    st.caption(
        f"Target threshold: {match_threshold}%. Candidates scoring "
        f"{match_threshold}% or above will be marked as Strong Match."
    )


    # ========================================================
    # RANK BUTTON
    # ========================================================

    analyze_hr = st.button(
        "🔎 Rank Candidates",
        type="primary",
        use_container_width=True,
        key="rank_candidates_button"
    )


    # ========================================================
    # PROCESS HR INPUT
    # ========================================================

    if analyze_hr:
        # ----------------------------------------------------
        # CLEAR PREVIOUS HR RESULTS
        # ----------------------------------------------------

        st.session_state["hr_results"] = None

        # ----------------------------------------------------
        # VALIDATE JD
        # ----------------------------------------------------

        if not hr_jd.strip():

            st.error(
                "Please paste the Job Description."
            )


        # ----------------------------------------------------
        # VALIDATE RESUMES
        # ----------------------------------------------------

        elif not hr_uploaded_files:

            st.error(
                "Please upload at least one candidate resume."
            )


        else:

            candidate_inputs = []
            extraction_errors = []


            # =================================================
            # EXTRACT ALL RESUMES
            # =================================================

            with st.spinner(
                "Extracting resumes and calculating match scores..."
            ):

                for uploaded_resume in hr_uploaded_files:

                    try:

                        resume_text = extract_text_from_file(
                            uploaded_resume
                        )


                        if (
                            resume_text
                            and resume_text.strip()
                        ):

                            candidate_inputs.append(
                                {
                                    "name": "",
                                    "text": resume_text.strip()
                                }
                            )


                        else:

                            extraction_errors.append(
                                f"{uploaded_resume.name}: "
                                "no readable text found"
                            )


                    except Exception as error:

                        extraction_errors.append(
                            f"{uploaded_resume.name}: {error}"
                        )


                # =================================================
                # RANK CANDIDATES
                # =================================================

                if candidate_inputs:

                    try:

                        # ------------------------------------------------
                        # CHECK FOR RECOGNIZED JD SKILLS
                        # ------------------------------------------------

                        jd_check = compare_resume_to_jd(
                            "",
                            hr_jd
                        )

                        total_jd_skills = jd_check.get(
                            "total_jd_skills",
                            0
                        )

                        # ------------------------------------------------
                        # STOP IF JD HAS NO RECOGNIZED SKILLS
                        # ------------------------------------------------

                        if total_jd_skills == 0:

                            st.warning(
                                "⚠️ No recognized skills detected in the Job Description. "
                                "Try adding standard technical/professional keywords."
                            )

                            st.session_state[
                                "hr_results"
                            ] = None

                        else:

                            # ------------------------------------------------
                            # RANK CANDIDATES
                            # ------------------------------------------------

                            ranked_results = rank_candidates(
                                candidate_inputs,
                                hr_jd
                            )

                            st.session_state[
                                "hr_results"
                            ] = ranked_results

                            if ranked_results:

                                st.success(
                                    f"🎉 Candidate screening completed successfully! "
                                    f"{len(ranked_results)} resume(s) analyzed and ranked."
                                )

                            else:

                                st.warning(
                                    "⚠️ No candidates could be ranked from the uploaded resumes."
                                )

                    except Exception as error:

                        st.session_state[
                            "hr_results"
                        ] = None

                        st.error(
                            "Something went wrong while ranking the resumes."
                        )

                        st.exception(
                            error
                        )


                else:

                    st.session_state[
                        "hr_results"
                    ] = None


            # =================================================
            # EXTRACTION WARNINGS
            # =================================================

            if extraction_errors:

                st.warning(
                    "Some resumes could not be processed:\n\n"
                    + "\n".join(
                        f"• {error}"
                        for error in extraction_errors
                    )
                )


    # ========================================================
    # GET HR RESULTS
    # ========================================================

    hr_results = st.session_state.get(
        "hr_results"
    )


    # ========================================================
    # DISPLAY HR RESULTS
    # ========================================================

    if hr_results:

        st.divider()


        st.markdown(
            "## 📊 Candidate Ranking"
        )


        # ====================================================
        # HR SUMMARY KPI CARDS
        # ====================================================

        strong_count = sum(
            1
            for candidate in hr_results
            if candidate.get(
                "score",
                0
            ) >= match_threshold
        )


        average_score = round(
            sum(
                candidate.get(
                    "score",
                    0
                )
                for candidate in hr_results
            )
            / len(hr_results),
            1
        )


        top_score = hr_results[0].get(
            "score",
            0
        )


        metric_1, metric_2, metric_3, metric_4 = st.columns(
            4
        )


        # ----------------------------------------------------
        # CANDIDATES
        # ----------------------------------------------------

        metric_1.metric(
            "Candidates",
            len(hr_results)
        )


        # ----------------------------------------------------
        # SHORTLIST MATCHES
        # ----------------------------------------------------

        metric_2.metric(
            "Shortlist Matches",
            strong_count
        )


        # ----------------------------------------------------
        # AVERAGE SCORE
        # ----------------------------------------------------

        metric_3.metric(
            "Average Score",
            f"{average_score}%"
        )


        # ----------------------------------------------------
        # TOP MATCH
        # ----------------------------------------------------

        metric_4.metric(
            "Top Match",
            f"{top_score}%"
        )


        # ====================================================
        # CSV EXPORT
        # ====================================================

        csv_rows = []


        for candidate in hr_results:

            csv_rows.append(
                {
                    "Rank": candidate.get(
                        "rank",
                        ""
                    ),

                    "Candidate": candidate.get(
                        "candidate_name",
                        "Unknown Candidate"
                    ),

                    "Match Score": candidate.get(
                        "score",
                        0
                    ),

                    "Status": get_candidate_status(
                        candidate.get(
                            "score",
                            0
                        ),
                        match_threshold
                    ),

                    "JD Skills": candidate.get(
                        "total_jd_skills",
                        0
                    ),

                    "Matched Skills Count": len(
                        candidate.get(
                            "matched",
                            []
                        )
                    ),

                    "Missing Skills Count": len(
                        candidate.get(
                            "missing",
                            []
                        )
                    ),

                    "Matched Skills": ", ".join(
                        candidate.get(
                            "matched",
                            []
                        )
                    ),

                    "Missing Skills": ", ".join(
                        candidate.get(
                            "missing",
                            []
                        )
                    )
                }
            )


        ranking_df = pd.DataFrame(
            csv_rows
        )


        csv_data = ranking_df.to_csv(
            index=False
        ).encode(
            "utf-8"
        )


        st.download_button(
            "📥 Download Candidate Ranking CSV",
            data=csv_data,
            file_name="AlignIQ_Candidate_Ranking.csv",
            mime="text/csv",
            use_container_width=True
        )


        st.divider()


        # ====================================================
        # RANKED CANDIDATE CARDS
        # ====================================================

        for candidate in hr_results:

            score = candidate.get(
                "score",
                0
            )


            name = candidate.get(
                "candidate_name",
                "Unknown Candidate"
            )


            matched = [
                str(skill).strip()
                for skill in candidate.get(
                    "matched",
                    []
                )
                if str(skill).strip()
            ]


            missing = [
                str(skill).strip()
                for skill in candidate.get(
                    "missing",
                    []
                )
                if str(skill).strip()
            ]


            status = get_candidate_status(
                score,
                match_threshold
            )


            # =================================================
            # CANDIDATE CONTAINER
            # =================================================

            with st.container(
                border=True
            ):

                rank_col, name_col, score_col = st.columns(
                    [1, 5, 2]
                )


                # ---------------------------------------------
                # RANK
                # ---------------------------------------------

                with rank_col:

                    st.markdown(
                        f"### #{candidate.get('rank', '')}"
                    )


                # ---------------------------------------------
                # NAME + STATUS
                # ---------------------------------------------

                with name_col:

                    st.markdown(
                        f"### {name}"
                    )


                    if status == "Strong Match":

                        st.success(
                            f"##### 🟢 Strong Match ({score}%): Recommended for Review!\n"
                            f"This candidate matches **{len(matched)} of "
                            f"{candidate.get('total_jd_skills', 0)}** "
                            f"key skills identified in the Job Description."
                        )

                    elif status == "Moderate Match":

                        st.warning(
                            f"##### 🟡 Moderate Match ({score}%): Review Before Shortlisting.\n"
                            f"This candidate matches **{len(matched)} skills**, "
                            f"but is missing **{len(missing)}** key terms. "
                            f"Review the skill gaps below."
                        )

                    else:

                        st.error(
                            f"##### 🔴 Low Match ({score}%): Significant Skill Gap.\n"
                            f"This candidate matches **{len(matched)} skill(s)** "
                            f"and is missing **{len(missing)}** identified skills."
                        )


                # ---------------------------------------------
                # SCORE
                # ---------------------------------------------

                with score_col:

                    st.metric(
                        "Match Score",
                        f"{score}%"
                    )


                # ---------------------------------------------
                # PROGRESS
                # ---------------------------------------------

                st.progress(
                    max(
                        0,
                        min(
                            score / 100,
                            1
                        )
                    )
                )


                # =================================================
                # QUICK SKILL SUMMARY
                # =================================================

                quick_col_1, quick_col_2, quick_col_3 = st.columns(
                    3
                )


                quick_col_1.metric(
                    "JD Skills",
                    candidate.get(
                        "total_jd_skills",
                        0
                    )
                )


                quick_col_2.metric(
                    "Matched",
                    len(matched)
                )


                quick_col_3.metric(
                    "Missing",
                    len(missing)
                )


                st.caption(
                    f"{len(matched)} of "
                    f"{candidate.get('total_jd_skills', 0)} "
                    "required JD skills matched"
                )


                # =================================================
                # VIEW DETAILS
                # =================================================

                with st.expander(
                    "🔎 View Candidate Details"
                ):

                    st.divider()


                    # ---------------------------------------------
                    # MATCHED SKILLS
                    # ---------------------------------------------

                    st.markdown(
                        "#### ✅ Matched Skills for This Candidate"
                    )


                    if matched:

                        matched_html = ""


                        for skill in matched:

                            matched_html += (
                                f'<span class="matched-skill">'
                                f'{skill}'
                                f'</span>'
                            )


                        st.markdown(
                            matched_html,
                            unsafe_allow_html=True
                        )


                    else:

                        st.info(
                            "This candidate does not match "
                            "any recognized JD skills."
                        )


                    st.write("")


                    # ---------------------------------------------
                    # MISSING SKILLS
                    # ---------------------------------------------

                    st.markdown(
                        "#### ❌ Missing Skills for This Candidate"
                    )


                    if missing:

                        missing_html = ""


                        for skill in missing:

                            missing_html += (
                                f'<span class="missing-skill">'
                                f'{skill}'
                                f'</span>'
                            )


                        st.markdown(
                            missing_html,
                            unsafe_allow_html=True
                        )


                    else:

                        st.success(
                            "This candidate has all "
                            "recognized JD skills."
                        )


                    st.divider()


                    # ---------------------------------------------
                    # EXTRACTED RESUME
                    # ---------------------------------------------

                    resume_text = candidate.get(
                        "resume_text",
                        ""
                    )


                    if resume_text:

                        with st.expander(
                            "📄 View Extracted Resume Text"
                        ):

                            st.text_area(
                                "Resume Text",
                                value=resume_text,
                                height=400,
                                disabled=True,
                                key=(
                                    f"resume_text_"
                                    f"{candidate.get('rank', 0)}"
                                )
                            )