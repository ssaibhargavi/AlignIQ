import io

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle
)

from reportlab.lib.styles import ParagraphStyle

from xml.sax.saxutils import escape


# ============================================================
# BUILD PDF RESUME
# ============================================================

def build_pdf_resume(
    tailored_data: dict
) -> bytes:

    # ========================================================
    # BUFFER
    # ========================================================

    buffer = io.BytesIO()


    # ========================================================
    # DOCUMENT
    # ========================================================

    document = SimpleDocTemplate(

        buffer,

        pagesize=letter,

        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=32
    )


    # ========================================================
    # STYLES
    # ========================================================

    name_style = ParagraphStyle(

        "NameStyle",

        fontName="Helvetica-Bold",

        fontSize=18,

        leading=22,

        alignment=1,

        textColor=colors.HexColor(
            "#111827"
        )
    )


    contact_style = ParagraphStyle(

        "ContactStyle",

        fontName="Helvetica",

        fontSize=8.5,

        leading=11,

        alignment=1,

        textColor=colors.HexColor(
            "#4b5563"
        )
    )


    section_style = ParagraphStyle(

        "SectionStyle",

        fontName="Helvetica-Bold",

        fontSize=10,

        leading=13,

        spaceBefore=8,

        spaceAfter=3,

        textColor=colors.HexColor(
            "#1e3a8a"
        )
    )


    title_style = ParagraphStyle(

        "TitleStyle",

        fontName="Helvetica-Bold",

        fontSize=9,

        leading=12,

        spaceBefore=5,

        spaceAfter=2,

        textColor=colors.HexColor(
            "#111827"
        )
    )


    body_style = ParagraphStyle(

        "BodyStyle",

        fontName="Helvetica",

        fontSize=8.5,

        leading=12,

        spaceAfter=2,

        textColor=colors.HexColor(
            "#1f2937"
        )
    )


    bullet_style = ParagraphStyle(

        "BulletStyle",

        fontName="Helvetica",

        fontSize=8.5,

        leading=12,

        leftIndent=14,

        firstLineIndent=-9,

        spaceAfter=2,

        textColor=colors.HexColor(
            "#1f2937"
        )
    )


    # ========================================================
    # STORY
    # ========================================================

    story = []


    # ========================================================
    # HELPER: CLEAN LIST
    # ========================================================

    def clean_list(items):

        if not items:
            return []


        if isinstance(items, str):
            items = [items]


        if not isinstance(items, list):
            return []


        cleaned = []


        for item in items:

            item = str(item).strip()

            if item:
                cleaned.append(item)


        # Remove duplicates while keeping original order

        return list(
            dict.fromkeys(cleaned)
        )


    # ========================================================
    # HELPER: REMOVE BULLET MARKERS
    # ========================================================

    def remove_bullet_marker(text):

        text = str(text).strip()

        return text.lstrip(
            "•●○◦▪▫►▸▹◆◇■□*-–— "
        ).strip()


    # ========================================================
    # HELPER: ADD SECTION
    # ========================================================

    def add_section(title):

        story.append(

            Paragraph(

                title,

                section_style
            )
        )


        story.append(

            HRFlowable(

                width="100%",

                thickness=0.5,

                color=colors.HexColor(
                    "#d1d5db"
                ),

                spaceAfter=3
            )
        )


    # ========================================================
    # HEADER
    # ========================================================

    name = str(

        tailored_data.get(

            "name",

            "Candidate Name"
        )

    ).strip()


    if not name:
        name = "Candidate Name"


    story.append(

        Paragraph(

            escape(name),

            name_style
        )
    )


    contact = str(

        tailored_data.get(

            "contact",

            ""
        )

    ).strip()


    if contact:

        story.append(

            Spacer(

                1,

                3
            )
        )


        story.append(

            Paragraph(

                escape(contact),

                contact_style
            )
        )


    story.append(

        Spacer(

            1,

            5
        )
    )


    story.append(

        HRFlowable(

            width="100%",

            thickness=0.7,

            color=colors.HexColor(
                "#cbd5e1"
            ),

            spaceAfter=5
        )
    )


    # ========================================================
    # PROFESSIONAL SUMMARY
    # ========================================================

    summary = str(

        tailored_data.get(

            "summary",

            ""
        )

    ).strip()


    if summary:

        add_section(

            "PROFESSIONAL SUMMARY"
        )


        story.append(

            Paragraph(

                escape(summary),

                body_style
            )
        )


    # ========================================================
    # TECHNICAL SKILLS
    # ========================================================

    skills = tailored_data.get(

        "skills",

        {}
    )


    if isinstance(skills, dict):

        valid_skill_categories = []


        for category, skill_list in skills.items():

            cleaned_skills = clean_list(

                skill_list
            )


            if cleaned_skills:

                valid_skill_categories.append(

                    (

                        str(category).strip(),

                        cleaned_skills
                    )
                )


        # Show section ONLY if valid skills exist

        if valid_skill_categories:

            add_section(

                "TECHNICAL SKILLS"
            )


            for category, skill_list in valid_skill_categories:

                skills_text = ", ".join(

                    skill_list
                )


                story.append(

                    Paragraph(

                        f"<b>{escape(category)}:</b> "
                        f"{escape(skills_text)}",

                        body_style
                    )
                )


    # ========================================================
    # SOFT SKILLS + LANGUAGES
    # ========================================================

    soft_skills = clean_list(

        tailored_data.get(

            "soft_skills",

            []
        )
    )


    languages = clean_list(

        tailored_data.get(

            "languages",

            []
        )
    )


    # ========================================================
    # CASE 1: BOTH EXIST
    # SHOW SIDE BY SIDE
    # ========================================================

    if soft_skills and languages:

        soft_skills_text = " • ".join(

            soft_skills
        )


        languages_text = " • ".join(

            languages
        )


        soft_skills_title = Paragraph(

            "SOFT SKILLS",

            section_style
        )


        languages_title = Paragraph(

            "LANGUAGES",

            section_style
        )


        soft_skills_content = Paragraph(

            escape(

                soft_skills_text
            ),

            body_style
        )


        languages_content = Paragraph(

            escape(

                languages_text
            ),

            body_style
        )


        skills_languages_table = Table(

            [

                [

                    soft_skills_title,

                    languages_title
                ],

                [

                    soft_skills_content,

                    languages_content
                ]

            ],

            colWidths=[

                270,

                270
            ]
        )


        skills_languages_table.setStyle(

            TableStyle(

                [

                    (

                        "VALIGN",

                        (0, 0),

                        (-1, -1),

                        "TOP"
                    ),

                    (

                        "LEFTPADDING",

                        (0, 0),

                        (-1, -1),

                        0
                    ),

                    (

                        "RIGHTPADDING",

                        (0, 0),

                        (-1, -1),

                        8
                    ),

                    (

                        "TOPPADDING",

                        (0, 0),

                        (-1, -1),

                        0
                    ),

                    (

                        "BOTTOMPADDING",

                        (0, 0),

                        (-1, -1),

                        4
                    )

                ]
            )
        )


        story.append(

            skills_languages_table
        )


    # ========================================================
    # CASE 2: ONLY SOFT SKILLS
    # ========================================================

    elif soft_skills:

        add_section(

            "SOFT SKILLS"
        )


        soft_skills_text = " • ".join(

            soft_skills
        )


        story.append(

            Paragraph(

                escape(

                    soft_skills_text
                ),

                body_style
            )
        )


    # ========================================================
    # CASE 3: ONLY LANGUAGES
    # ========================================================

    elif languages:

        add_section(

            "LANGUAGES"
        )


        languages_text = " • ".join(

            languages
        )


        story.append(

            Paragraph(

                escape(

                    languages_text
                ),

                body_style
            )
        )


    # ========================================================
    # HELPER: ENTRIES SECTION
    #
    # Used for:
    # - Internships
    # - Work Experience
    # - Projects
    # ========================================================

    def add_entries_section(

        section_title,

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


        # ----------------------------------------------------
        # CLEAN ALL ENTRIES FIRST
        # ----------------------------------------------------

        for entry in entries:


            if not isinstance(

                entry,

                dict
            ):

                continue


            title = str(

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


            bullets = clean_list(

                entry.get(

                    "bullets",

                    []
                )
            )


            # Remove empty bullets

            bullets = [

                remove_bullet_marker(

                    bullet
                )

                for bullet in bullets

                if remove_bullet_marker(

                    bullet
                )
            ]


            # Keep entry only if title or bullets exist

            if title or bullets:

                valid_entries.append(

                    {

                        "title": title,

                        "technologies": technologies,

                        "bullets": bullets
                    }
                )


        # ----------------------------------------------------
        # DO NOT SHOW EMPTY SECTION
        # ----------------------------------------------------

        if not valid_entries:

            return


        # ----------------------------------------------------
        # SHOW SECTION
        # ----------------------------------------------------

        add_section(

            section_title
        )


        # ----------------------------------------------------
        # DISPLAY ALL ENTRIES
        # ----------------------------------------------------

        for entry in valid_entries:


            title = entry.get(

                "title",

                ""
            )


            technologies = entry.get(

                "technologies",

                ""
            ).strip()


            bullets = entry.get(

                "bullets",

                []
            )


            # Entry title

            if title:

                story.append(

                    Paragraph(

                        escape(title),

                        title_style
                    )
                )


            # Project technology metadata

            if technologies:

                story.append(

                    Paragraph(

                        f"<b>Technologies:</b> {escape(technologies)}",

                        body_style

                    )

                )


            # Entry bullets

            for bullet in bullets:


                if not bullet:

                    continue


                story.append(

                    Paragraph(

                        "• "

                        + escape(

                            bullet
                        ),

                        bullet_style
                    )
                )


    # ========================================================
    # INTERNSHIPS
    # ========================================================

    add_entries_section(

        "INTERNSHIPS",

        tailored_data.get(

            "internships",

            []
        )
    )


    # ========================================================
    # WORK EXPERIENCE
    # ========================================================

    add_entries_section(

        "WORK EXPERIENCE",

        tailored_data.get(

            "experience",

            []
        )
    )


    # ========================================================
    # PROJECTS
    # ========================================================

    add_entries_section(

        "PROJECTS",

        tailored_data.get(

            "projects",

            []
        )
    )


    # ========================================================
    # EDUCATION
    # ========================================================

    education = clean_list(

        tailored_data.get(

            "education",

            []
        )
    )


    # Show only if education exists

    if education:

        add_section(

            "EDUCATION"
        )


        for item in education:

            story.append(

                Paragraph(

                    escape(item),

                    body_style
                )
            )


    # ========================================================
    # HELPER: SIMPLE LIST SECTION
    #
    # Used for:
    # - Certifications
    # - Achievements
    # ========================================================

    def add_simple_list_section(

        section_title,

        items
    ):


        items = clean_list(

            items
        )


        # Remove bullet markers

        items = [

            remove_bullet_marker(

                item
            )

            for item in items

            if remove_bullet_marker(

                item
            )
        ]


        # DO NOT SHOW EMPTY SECTION

        if not items:

            return


        # Show section

        add_section(

            section_title
        )


        # Show items

        for item in items:

            story.append(

                Paragraph(

                    "• "

                    + escape(item),

                    bullet_style
                )
            )


    # ========================================================
    # CERTIFICATIONS
    # ========================================================

    add_simple_list_section(

        "CERTIFICATIONS",

        tailored_data.get(

            "certifications",

            []
        )
    )


    # ========================================================
    # ACHIEVEMENTS
    # ========================================================

    add_simple_list_section(

        "ACHIEVEMENTS",

        tailored_data.get(

            "achievements",

            []
        )
    )


    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(

        story
    )


    buffer.seek(

        0
    )


    return buffer.getvalue()

# import io

# from reportlab.lib.pagesizes import letter
# from reportlab.lib import colors

# from reportlab.platypus import (
#     SimpleDocTemplate,
#     Paragraph,
#     Spacer,
#     HRFlowable,
#     Table,
#     TableStyle
# )

# from reportlab.lib.styles import ParagraphStyle

# from xml.sax.saxutils import escape


# # ============================================================
# # BUILD PDF RESUME
# # ============================================================

# def build_pdf_resume(
#     tailored_data: dict
# ) -> bytes:

#     # ========================================================
#     # BUFFER
#     # ========================================================

#     buffer = io.BytesIO()


#     # ========================================================
#     # DOCUMENT
#     # ========================================================

#     document = SimpleDocTemplate(

#         buffer,

#         pagesize=letter,

#         leftMargin=36,
#         rightMargin=36,
#         topMargin=32,
#         bottomMargin=32
#     )


#     # ========================================================
#     # STYLES
#     # ========================================================

#     name_style = ParagraphStyle(

#         "NameStyle",

#         fontName="Helvetica-Bold",

#         fontSize=18,

#         leading=22,

#         alignment=1,

#         textColor=colors.HexColor(
#             "#111827"
#         )
#     )


#     contact_style = ParagraphStyle(

#         "ContactStyle",

#         fontName="Helvetica",

#         fontSize=8.5,

#         leading=11,

#         alignment=1,

#         textColor=colors.HexColor(
#             "#4b5563"
#         )
#     )


#     section_style = ParagraphStyle(

#         "SectionStyle",

#         fontName="Helvetica-Bold",

#         fontSize=10,

#         leading=13,

#         spaceBefore=8,

#         spaceAfter=3,

#         textColor=colors.HexColor(
#             "#1e3a8a"
#         )
#     )


#     title_style = ParagraphStyle(

#         "TitleStyle",

#         fontName="Helvetica-Bold",

#         fontSize=9,

#         leading=12,

#         spaceBefore=5,

#         spaceAfter=2,

#         textColor=colors.HexColor(
#             "#111827"
#         )
#     )


#     body_style = ParagraphStyle(

#         "BodyStyle",

#         fontName="Helvetica",

#         fontSize=8.5,

#         leading=12,

#         spaceAfter=2,

#         textColor=colors.HexColor(
#             "#1f2937"
#         )
#     )


#     bullet_style = ParagraphStyle(

#         "BulletStyle",

#         fontName="Helvetica",

#         fontSize=8.5,

#         leading=12,

#         leftIndent=14,

#         firstLineIndent=-9,

#         spaceAfter=2,

#         textColor=colors.HexColor(
#             "#1f2937"
#         )
#     )


#     # ========================================================
#     # STORY
#     # ========================================================

#     story = []


#     # ========================================================
#     # HELPER: CLEAN LIST
#     # ========================================================

#     def clean_list(items):

#         if not items:
#             return []


#         if isinstance(items, str):
#             items = [items]


#         if not isinstance(items, list):
#             return []


#         cleaned = []


#         for item in items:

#             item = str(item).strip()

#             if item:
#                 cleaned.append(item)


#         # Remove duplicates while keeping original order

#         return list(
#             dict.fromkeys(cleaned)
#         )


#     # ========================================================
#     # HELPER: REMOVE BULLET MARKERS
#     # ========================================================

#     def remove_bullet_marker(text):

#         text = str(text).strip()

#         return text.lstrip(
#             "•●○◦▪▫►▸▹◆◇■□*-–— "
#         ).strip()


#     # ========================================================
#     # HELPER: ADD SECTION
#     # ========================================================

#     def add_section(title):

#         story.append(

#             Paragraph(

#                 title,

#                 section_style
#             )
#         )


#         story.append(

#             HRFlowable(

#                 width="100%",

#                 thickness=0.5,

#                 color=colors.HexColor(
#                     "#d1d5db"
#                 ),

#                 spaceAfter=3
#             )
#         )


#     # ========================================================
#     # HEADER
#     # ========================================================

#     name = str(

#         tailored_data.get(

#             "name",

#             "Candidate Name"
#         )

#     ).strip()


#     if not name:
#         name = "Candidate Name"


#     story.append(

#         Paragraph(

#             escape(name),

#             name_style
#         )
#     )


#     contact = str(

#         tailored_data.get(

#             "contact",

#             ""
#         )

#     ).strip()


#     if contact:

#         story.append(

#             Spacer(

#                 1,

#                 3
#             )
#         )


#         story.append(

#             Paragraph(

#                 escape(contact),

#                 contact_style
#             )
#         )


#     story.append(

#         Spacer(

#             1,

#             5
#         )
#     )


#     story.append(

#         HRFlowable(

#             width="100%",

#             thickness=0.7,

#             color=colors.HexColor(
#                 "#cbd5e1"
#             ),

#             spaceAfter=5
#         )
#     )


#     # ========================================================
#     # PROFESSIONAL SUMMARY
#     # ========================================================

#     summary = str(

#         tailored_data.get(

#             "summary",

#             ""
#         )

#     ).strip()


#     if summary:

#         add_section(

#             "PROFESSIONAL SUMMARY"
#         )


#         story.append(

#             Paragraph(

#                 escape(summary),

#                 body_style
#             )
#         )


#     # ========================================================
#     # TECHNICAL SKILLS
#     # ========================================================

#     skills = tailored_data.get(

#         "skills",

#         {}
#     )


#     if isinstance(skills, dict):

#         valid_skill_categories = []


#         for category, skill_list in skills.items():

#             cleaned_skills = clean_list(

#                 skill_list
#             )


#             if cleaned_skills:

#                 valid_skill_categories.append(

#                     (

#                         str(category).strip(),

#                         cleaned_skills
#                     )
#                 )


#         # Show section ONLY if valid skills exist

#         if valid_skill_categories:

#             add_section(

#                 "TECHNICAL SKILLS"
#             )


#             for category, skill_list in valid_skill_categories:

#                 skills_text = ", ".join(

#                     skill_list
#                 )


#                 story.append(

#                     Paragraph(

#                         f"<b>{escape(category)}:</b> "
#                         f"{escape(skills_text)}",

#                         body_style
#                     )
#                 )


#     # ========================================================
#     # SOFT SKILLS + LANGUAGES
#     # ========================================================

#     soft_skills = clean_list(

#         tailored_data.get(

#             "soft_skills",

#             []
#         )
#     )


#     languages = clean_list(

#         tailored_data.get(

#             "languages",

#             []
#         )
#     )


#     # ========================================================
#     # CASE 1: BOTH EXIST
#     # SHOW SIDE BY SIDE
#     # ========================================================

#     if soft_skills and languages:

#         soft_skills_text = " • ".join(

#             soft_skills
#         )


#         languages_text = " • ".join(

#             languages
#         )


#         soft_skills_title = Paragraph(

#             "SOFT SKILLS",

#             section_style
#         )


#         languages_title = Paragraph(

#             "LANGUAGES",

#             section_style
#         )


#         soft_skills_content = Paragraph(

#             escape(

#                 soft_skills_text
#             ),

#             body_style
#         )


#         languages_content = Paragraph(

#             escape(

#                 languages_text
#             ),

#             body_style
#         )


#         skills_languages_table = Table(

#             [

#                 [

#                     soft_skills_title,

#                     languages_title
#                 ],

#                 [

#                     soft_skills_content,

#                     languages_content
#                 ]

#             ],

#             colWidths=[

#                 270,

#                 270
#             ]
#         )


#         skills_languages_table.setStyle(

#             TableStyle(

#                 [

#                     (

#                         "VALIGN",

#                         (0, 0),

#                         (-1, -1),

#                         "TOP"
#                     ),

#                     (

#                         "LEFTPADDING",

#                         (0, 0),

#                         (-1, -1),

#                         0
#                     ),

#                     (

#                         "RIGHTPADDING",

#                         (0, 0),

#                         (-1, -1),

#                         8
#                     ),

#                     (

#                         "TOPPADDING",

#                         (0, 0),

#                         (-1, -1),

#                         0
#                     ),

#                     (

#                         "BOTTOMPADDING",

#                         (0, 0),

#                         (-1, -1),

#                         4
#                     )

#                 ]
#             )
#         )


#         story.append(

#             skills_languages_table
#         )


#     # ========================================================
#     # CASE 2: ONLY SOFT SKILLS
#     # ========================================================

#     elif soft_skills:

#         add_section(

#             "SOFT SKILLS"
#         )


#         soft_skills_text = " • ".join(

#             soft_skills
#         )


#         story.append(

#             Paragraph(

#                 escape(

#                     soft_skills_text
#                 ),

#                 body_style
#             )
#         )


#     # ========================================================
#     # CASE 3: ONLY LANGUAGES
#     # ========================================================

#     elif languages:

#         add_section(

#             "LANGUAGES"
#         )


#         languages_text = " • ".join(

#             languages
#         )


#         story.append(

#             Paragraph(

#                 escape(

#                     languages_text
#                 ),

#                 body_style
#             )
#         )


#     # ========================================================
#     # HELPER: ENTRIES SECTION
#     #
#     # Used for:
#     # - Internships
#     # - Work Experience
#     # - Projects
#     # ========================================================

#     def add_entries_section(

#         section_title,

#         entries
#     ):


#         if not entries:

#             return


#         if not isinstance(

#             entries,

#             list
#         ):

#             return


#         valid_entries = []


#         # ----------------------------------------------------
#         # CLEAN ALL ENTRIES FIRST
#         # ----------------------------------------------------

#         for entry in entries:


#             if not isinstance(

#                 entry,

#                 dict
#             ):

#                 continue


#             title = str(

#                 entry.get(

#                     "title",

#                     ""
#                 )

#             ).strip()


#             bullets = clean_list(

#                 entry.get(

#                     "bullets",

#                     []
#                 )
#             )


#             # Remove empty bullets

#             bullets = [

#                 remove_bullet_marker(

#                     bullet
#                 )

#                 for bullet in bullets

#                 if remove_bullet_marker(

#                     bullet
#                 )
#             ]


#             # Keep entry only if title or bullets exist

#             if title or bullets:

#                 valid_entries.append(

#                     {

#                         "title": title,

#                         "bullets": bullets
#                     }
#                 )


#         # ----------------------------------------------------
#         # DO NOT SHOW EMPTY SECTION
#         # ----------------------------------------------------

#         if not valid_entries:

#             return


#         # ----------------------------------------------------
#         # SHOW SECTION
#         # ----------------------------------------------------

#         add_section(

#             section_title
#         )


#         # ----------------------------------------------------
#         # DISPLAY ALL ENTRIES
#         # ----------------------------------------------------

#         for entry in valid_entries:


#             title = entry.get(

#                 "title",

#                 ""
#             )


#             bullets = entry.get(

#                 "bullets",

#                 []
#             )


#             # Entry title

#             if title:

#                 story.append(

#                     Paragraph(

#                         escape(title),

#                         title_style
#                     )
#                 )


#             # Entry bullets

#             for bullet in bullets:


#                 if not bullet:

#                     continue


#                 story.append(

#                     Paragraph(

#                         "• "

#                         + escape(

#                             bullet
#                         ),

#                         bullet_style
#                     )
#                 )


#     # ========================================================
#     # INTERNSHIPS
#     # ========================================================

#     add_entries_section(

#         "INTERNSHIPS",

#         tailored_data.get(

#             "internships",

#             []
#         )
#     )


#     # ========================================================
#     # WORK EXPERIENCE
#     # ========================================================

#     add_entries_section(

#         "WORK EXPERIENCE",

#         tailored_data.get(

#             "experience",

#             []
#         )
#     )


#     # ========================================================
#     # PROJECTS
#     # ========================================================

#     add_entries_section(

#         "PROJECTS",

#         tailored_data.get(

#             "projects",

#             []
#         )
#     )


#     # ========================================================
#     # EDUCATION
#     # ========================================================

#     education = clean_list(

#         tailored_data.get(

#             "education",

#             []
#         )
#     )


#     # Show only if education exists

#     if education:

#         add_section(

#             "EDUCATION"
#         )


#         for item in education:

#             story.append(

#                 Paragraph(

#                     escape(item),

#                     body_style
#                 )
#             )


#     # ========================================================
#     # HELPER: SIMPLE LIST SECTION
#     #
#     # Used for:
#     # - Certifications
#     # - Achievements
#     # ========================================================

#     def add_simple_list_section(

#         section_title,

#         items
#     ):


#         items = clean_list(

#             items
#         )


#         # Remove bullet markers

#         items = [

#             remove_bullet_marker(

#                 item
#             )

#             for item in items

#             if remove_bullet_marker(

#                 item
#             )
#         ]


#         # DO NOT SHOW EMPTY SECTION

#         if not items:

#             return


#         # Show section

#         add_section(

#             section_title
#         )


#         # Show items

#         for item in items:

#             story.append(

#                 Paragraph(

#                     "• "

#                     + escape(item),

#                     bullet_style
#                 )
#             )


#     # ========================================================
#     # CERTIFICATIONS
#     # ========================================================

#     add_simple_list_section(

#         "CERTIFICATIONS",

#         tailored_data.get(

#             "certifications",

#             []
#         )
#     )


#     # ========================================================
#     # ACHIEVEMENTS
#     # ========================================================

#     add_simple_list_section(

#         "ACHIEVEMENTS",

#         tailored_data.get(

#             "achievements",

#             []
#         )
#     )

#     # ========================================================
#     # EXTRACURRICULAR ACTIVITIES
#     # ========================================================

#     add_simple_list_section(
#         "EXTRACURRICULAR ACTIVITIES",
#         tailored_data.get(
#             "extracurricular_activities",
#             []
#         )
#     )


#     # ========================================================
#     # ADDITIONAL INFORMATION
#     # ========================================================

#     add_simple_list_section(
#         "ADDITIONAL INFORMATION",
#         tailored_data.get(
#             "additional_information",
#             []
#         )
#     )


#     # ========================================================
#     # BUILD PDF
#     # ========================================================

#     document.build(

#         story
#     )


#     buffer.seek(

#         0
#     )


#     return buffer.getvalue()