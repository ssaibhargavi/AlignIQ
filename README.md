# AlignIQ — AI-Powered Resume Matching & Tailoring Tool

AlignIQ is a Streamlit-based resume analysis and tailoring application that compares resumes against job descriptions, identifies skill gaps, calculates a weighted match score, and generates a tailored resume. It also enables HR teams to screen and rank multiple candidates against a single job description.

## 🚀 Live Demo

https://aligniq.streamlit.app/

## 📌 Features

### Candidate Mode
- Analyze a master resume against a job description.
- Identify skills required by the job description.
- Compare resume skills with job requirements.
- Calculate a weighted match score.
- Identify matched and missing skills.
- Validate the presence of a dedicated Skills section.
- Generate a tailored resume.
- Export the tailored resume as a PDF.
- Support career-level selection.

### HR Mode
- Upload multiple resumes against a single job description.
- Extract resume content from PDF, DOCX, and TXT files.
- Analyze candidates using consistent matching logic.
- Calculate individual candidate match scores.
- Identify matched and missing skills.
- Categorize candidates using configurable thresholds.
- Rank candidates based on their match scores.

### Database Persistence
- Integrate with Neon PostgreSQL.
- Save candidate analysis records.
- Save HR screening records.
- Maintain persistent records beyond individual application sessions, subject to the implemented database logic.

## 🧠 Matching Logic

AlignIQ uses a skill taxonomy to identify technical skills in resumes and job descriptions.

Skills are classified into three categories:

| Skill Category | Weight |
|---|---:|
| Required / Mandatory / Essential | 3 |
| Preferred / Nice to Have / Good to Have / Plus | 2 |
| Normal / Unclassified | 1 |

**Weighted Match Score:**

`(Total weight of matched JD skills / Total weight of unique JD skills) × 100`

Required skills receive higher weights than preferred and normal skills. Candidate Mode also validates that the resume contains a dedicated Skills section before analysis.

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- PDFPlumber
- python-docx
- ReportLab
- PostgreSQL
- Neon
- psycopg
- Git and GitHub
- Streamlit Community Cloud

## 📂 Project Structure

```text
AlignIQ/
├── app.py
├── extractor.py
├── matcher.py
├── hr_matcher.py
├── tailorer.py
├── pdf_builder.py
├── database.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── secrets.toml
└── README.md
```

## 🔄 Application Workflow

### Candidate Mode

```text
Master Resume + Job Description
              ↓
       Resume Extraction
              ↓
         Skill Detection
              ↓
     Weighted Skill Matching
              ↓
          Match Score
         ↙          ↘
 Matched Skills   Missing Skills
              ↓
       Resume Tailoring
              ↓
          PDF Export
```

### HR Mode

```text
Job Description + Multiple Resumes
                ↓
         Resume Extraction
                ↓
          Skill Detection
                ↓
        Weighted Matching
                ↓
       Individual Scores
                ↓
      Candidate Comparison
                ↓
        Ranked Candidates
                ↓
       Database Persistence
```

## ⚠️ Disclaimer

AlignIQ is a resume analysis and screening aid. Match scores depend on the skills detected by the application's matching logic and should not be treated as a complete assessment of a candidate's qualifications or suitability. Final hiring decisions should involve human review.

## 👩‍💻 Author

**Shilam Sai Bhargavi**

- GitHub: https://github.com/ssaibhargavi
- LinkedIn: https://www.linkedin.com/in/ssaibhargavi/

---

*Built with Python and Streamlit to simplify resume matching, tailoring, and candidate screening.*
