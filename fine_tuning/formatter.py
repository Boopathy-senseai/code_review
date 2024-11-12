import json


def format_to_json(raw_text):
    # Create a dictionary with the content key and the raw text as its value
    formatted_data = {"content": raw_text}
    # Convert the dictionary to a JSON string
    json_string = json.dumps(formatted_data, indent=2)
    return json_string


# Example usage:
raw_text = """

job_title : HR Manager / Recruitment Lead

Join Our Team at Sense7ai
At Sense7ai, we are committed to driving sustainable innovation and revolutionizing business operations with our cutting-edge software solutions. As a market leader in intelligent software product development, we specialize in empowering businesses with the tools they need to thrive in a dynamic digital landscape.
What We Offer:

A collaborative environment where creativity meets strategy, producing software solutions optimized for maximum impact.
A diverse portfolio of purpose-built software solutions, backed by case studies demonstrating our expertise in web application development and more.
A commitment to staying ahead of the curve with our software offerings, harnessing the power of AI and ML to deliver optimized services.

Why Sense7ai?

You'll be part of a team that values innovation and is passionate about making a real difference in the way businesses operate.
We offer opportunities to grow and learn within a supportive and dynamic workplace.
Our approach is holistic &mdash; we believe in nurturing both individual talent and collective success.

We're Looking For:

Innovative thinkers who are eager to contribute to developing next-generation software solutions.
Professionals with a knack for problem-solving and a passion for technology.
Team players who thrive in a fast-paced environment and are dedicated to delivering excellence.

Roles and Responsibilities
Manage all aspects of the recruitment processSourcing and attracting talentGenerating recruitment plansExtending offers and onboardingIdentifying and developing recruitment strategiesConducting interviews and screening candidatesBuild and maintain relationships with hiring managersManage applicant tracking system and recruitment softwareEnsure compliance with hiring laws and regulations
Technical Skill
Experience in recruitment processes and best practicesKnowledge of applicant tracking systems and recruitment software
Soft Skill
Excellent communication and interpersonal skillsStrong organizational and time management abilitiesAbility to work well under pressure and meet deadlinesDetail-oriented and able to multitaskAdaptability and flexibilityProblem-solving and decision-making skillsEthical and professional behaviorStrong leadership and team management skills
Tools and Technologies
Applicant tracking systemsRecruitment software

Jd Skills : CANDIDATE ANALYTICS,CANDIDATE ENGAGEMENT,SOURCING,STRESS MANAGEMENT,TIME MANAGEMENT,ABILITY TO USE MODERN TECHNOLOGIES,SCREENING,COMMUNICATION



Jd Location : Remote

Jd Qualifcation : Bachelors - Human Resources

Jd Experience : 3 - 5  years

"""


def Input_convertion(text, ft):
    if ft == "resume_parser":
        return text
    if ft == "chatbot":
        query = "Support and Assistance"
        alter_text = None
        prompt = f"Could you provide a response  must be a max three lines and if the content not exist in context or non meaningfully return as {alter_text} and Questions is {query}"
        raw_text = {"prompt": prompt, "context": str(text)}
        return raw_text
    if ft == "comparative":
        return text
    if ft == "matching":
        return text


ft = "matching"
raw_text = Input_convertion(raw_text, ft)
json_data = format_to_json(raw_text)
