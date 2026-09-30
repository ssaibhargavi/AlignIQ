# AlignIQ — AI-Powered Resume Matching & Tailoring Tool

AlignIQ is a Streamlit-based resume analysis and tailoring application that compares resumes against job descriptions, identifies skill gaps, calculates a weighted match score, and generates a tailored resume.

## 🚀 Live Demo

https://aligniq.streamlit.app/

## 📌 Features

### Candidate Mode
- Analyze a master resume against a job description
- Identify skills required by the job description
- Compare declared resume skills with JD skills
- Calculate a weighted match score
- Identify matched and missing skills
- Generate a tailored resume
- Export the tailored resume as a PDF
- Support career-level selection

### HR Mode

- Upload multiple resumes against a single job description
- Extract resume content from PDF, DOCX, and TXT files
- Analyze each candidate using the same matching logic
- Calculate individual match scores
- Display matched and missing skills
- Categorize candidates based on configurable thresholds
- Rank candidates by match score

## 🧠 Matching Logic

AlignIQ uses a skill taxonomy to identify technical skills from resumes and job descriptions.

Skills can be classified as:

- Required / Mandatory / Essential
- Preferred / Nice to Have / Good to Have / Plus
- Normal / Unclassified

Required skills receive higher weight than preferred and normal skills when calculating the match score.
The application also validates that a candidate has a dedicated Skills section before performing Candidate Mode analysis.

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- PDFPlumber
- python-docx
- ReportLab
- Git
- GitHub

## 📂 Project Structure

```text
AlignIQ/
│
├── app.py
├── extractor.py
├── matcher.py
├── hr_matcher.py
├── tailorer.py
├── pdf_builder.py
├── requirements.txt
├── .gitignore
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
     Tailored Resume
            ↓
        PDF Export
```

### HR Mode
```text
Job Description + Multiple Resumes
                ↓
         Resume Extraction
                ↓
        Skill Matching
                ↓
       Individual Scores
                ↓
      Candidate Comparison
                ↓
          Ranked Results
```

## ⚠️ Disclaimer
AlignIQ is a resume analysis and screening aid.
Match scores are based on the skills detected by the application's matching logic and should not be treated as a complete assessment of a candidate's qualifications.

## 👩‍💻 Author
**Shilam Sai Bhargavi**  
GitHub: https://github.com/ssaibhargavi  
LinkedIn: https://www.linkedin.com/in/ssaibhargavi/
