profile_summary_prompt = """
Executive Summary: Create a narrative that succinctly outlines the candidate's career, highlighting unique strengths, key milestones, and their professional journey. Aim to captivate and set a compelling tone for the analysis.
 
Career Insights:
 
Roles and Impact: Identify and summarize pivotal roles, leadership, and contributions. Connect these roles to specific outcomes, demonstrating the candidate's impact on organizational growth.
Career Development: Chart the candidate's career progression, including key promotions and shifts. Emphasize achievements and skills that facilitated this advancement.
Achievements:
 
Major Contributions: Focus on significant achievements, underscoring their quantifiable impacts. Highlight how these efforts showcase the candidate's strategic expertise.
Broad Impact: Elucidate the broader implications of these achievements, stressing the candidate's capacity to drive meaningful change across organizations or industries.
Skills and Expertise:
 
Skillset Overview: Detail technical and soft skills, noting proficiency levels. Show how these skills are relevant to industry demands and the candidate’s contributions to projects. Provide an enhanced analysis for a clearer picture of why the candidate is considered an basic,expert or proficient in their field along with the justifcation for the classification.
Project Highlights: Describe key projects that demonstrate the candidate’s skillset, focusing on outcomes and the role played in achieving success.
Professional Engagement:
 
Industry Contributions: Highlight contributions to the industry, such as publications or talks, to underline thought leadership.
Networking and Development: Summarize efforts in networking and continuous learning, connecting these to the candidate's engagement with industry trends and growth.
Educational Background:
 
Relevance and Alignment: Briefly review education, certifications, or training, linking these directly to the candidate’s career path and goals.
Professional Dynamics:
 
Adaptability and Mobility: Discuss career moves in light of industry trends and personal development, emphasizing strategic adaptability.
Consistency and Motivation: Offer insights into the candidate’s career stability or mobility, providing context for their decisions and potential for further growth.
Conclusion and Recommendations:
Conclude with a synthesis of the candidate’s strengths and past achievements, advocating for their strategic fit in future roles. Recommend areas for development or new avenues based on their career trajectory and ambitions.
"""

sample_profile_format = {
    "Professional Profile Analysis": {
        "Career Trajectory": {
            "Roles and Responsibilities": [
                {
                    "Role": "Front End developer",
                    "Organization": "TNQ Technologies",
                    "Tenure": "08/2020 - 01/2022",
                    "Duties": "Developed and implemented a new HR module to manage employee information, recruitment, and benefits administration. Collaborated with the HR team to understand the requirements and design the system. HR and manager functionalities include setting holidays, leave requests, profile modification requests, payslip requests, OT requests, bank details change form, and resignation form etc. Built and tested the module using React, Node.js, and MySQL.",
                },
                {
                    "Role": "Programmer Trainee",
                    "Organization": "iNextLabs Pte Ltd",
                    "Tenure": "06/2022 - 08/2022",
                    "Duties": "No information available for this section",
                },
                {
                    "Role": "Software Developer",
                    "Organization": "Abira Healthcare Solutions Private Limited",
                    "Tenure": "09/2022 - Present",
                    "Duties": "No information available for this section",
                },
            ],
            "Career Progressions and Promotions": "The candidate has shown a steady progression in their career, starting as a Programmer Trainee and currently working as a Software Developer.",
        },
        "Achievements": {
            "Significant Contributions": "The candidate has made significant contributions in their role as a Front End developer at TNQ Technologies, where they developed and implemented a new HR module to manage employee information, recruitment, and benefits administration.",
            "Impact": "The implementation of the HR module has likely improved the efficiency of HR operations at TNQ Technologies.",
        },
        "Expertise and Skills": {
            "Technical Skills and Proficiency Levels": {
                "HTML/CSS": "Expert",
                "JavaScript": "Expert",
                "React": "Expert",
                "Node.js": "Expert",
                "MySQL": "Expert",
            },
            "Projects and Achievements Showcasing Skills": "The development and implementation of the HR module at TNQ Technologies showcases the candidate's skills in HTML/CSS, JavaScript, React, Node.js, and MySQL.",
        },
        "Industry Engagement": {
            "Contributions to the Industry": "No information available for this section",
            "Professional Circles": "No information available for this section",
        },
        "Networking and Professional Development": {
            "Networking Engagement": {
                "Professional Network": "The candidate has a LinkedIn profile, indicating engagement with professional networking.",
                "Engagement in Industry-Relevant Events": "No information available for this section",
            },
            "Continuous Learning and Adaptability": {
                "Ongoing Education and Skill Development": "The candidate has completed a Front-end Developer React Based Udemy Course, indicating a commitment to continuous learning and skill development.",
                "Adaptation to Industry Innovations": "The candidate's proficiency in modern technologies such as React and Node.js indicates their adaptability to industry innovations.",
            },
        },
        "Education and Alignment with Career Goals": "The candidate has a Bachelors in Computer Science from Anna University, aligning with their career in software development.",
        "Behavioral and Social Insights": {
            "Social Media and Professional Behavior": "The candidate has a LinkedIn profile, indicating professional behavior on social media.",
            "Mobility and Ambition": "The candidate has shown mobility and ambition in their career, progressing from a Programmer Trainee to a Software Developer.",
            "Consistency": "The candidate has shown consistency in their career, with no employment discontinuities or frequent role changes.",
        },
        "Summary and Recommendations": "The candidate has a strong background in software development, with expertise in HTML/CSS, JavaScript, React, Node.js, and MySQL. They have shown a steady progression in their career and a commitment to continuous learning and skill development.",
    }
}


def interview_prompt(
    role,
    count1,
    level,
    typeofquestion,
    jobtitle,
    summary,
    output_format,
    final_count,
    category,
):
    summary = summary if summary else ""
    prompt = {
        "prompt_template": f"Generate {final_count} interview questions based on specific criteria.",
        "instructions": "[no prose and should not be in string]\n[Output only JSON] Using the information provided, construct a set of unique interview questions of tailored to the interviewer's role, the job's requirements, and the candidate's profile. Additionally, provide optimal answers for each question. Your output must be in a structured JSON format that can be directly parsed using 'json.loads()' without errors.",
        "input_fields": {
            "role": role,
            "category as Question": category,
            "summary": summary,
        },
        "output_requirements": {
            "format": "JSON",
            "structure": f"[no prose and should not be in string]\n[Output only JSON]Provide the output in the following JSON structure format: {output_format} Replace placeholder text with the appropriate values based on the input fields.",
            "example": {
                "total_questions": f"{final_count}",
            },
            "note": f"Ensure the 'questions' array contains a unique set of questions and answers equal to '{final_count}', and the output JSON is correctly formatted for parsing.",
        },
    }
    return prompt
