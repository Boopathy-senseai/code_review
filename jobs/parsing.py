import re
import traceback
import PyPDF2
from openai import OpenAI
from jobs import *
from jobs.finetune import *


from jobs.standalone import Standalone
from zita.settings import openai_key, client
import time
import docx2txt
import pdfplumber
import json

# import  docx
from jobs.models import *
from users.models import *
from django.db.models import *
from bs4 import BeautifulSoup, NavigableString
import logging
import threading
import queue
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("jobs")
from tika import parser
from zita import settings

s_time = time.time()
from datetime import datetime
import time
from jobs.views import *
import os
from zita import settings
from .models import *

base_dir = settings.BASE_DIR
from .prompt import *


def nested_list(lst):
    """Check if the given list contains any nested lists."""
    if lst:
        for element in lst:
            if isinstance(element, list):
                return True

    return False


def flatten_list(nested_list):
    flattened_list = []
    for item in nested_list:
        if isinstance(item, list):
            flattened_list.extend(flatten_list(item))
        else:
            flattened_list.append(item)
    return flattened_list


def convert_dict_to_html(data):
    html_content = ""
    if data is not None and isinstance(data, dict):
        for key, value in data.items():
            if nested_list(value):
                value = flatten_list(value)
            if value is not None and isinstance(value, list) and value:
                skillswords = ["Skills", "skills"]
                if value != ["None"] and key not in skillswords:
                    transformed_key = " ".join(
                        [word.capitalize() for word in key.split("_")]
                    )
                    html_content += f"<h6>{transformed_key}</h6>\n"
                    html_content += "<ul>\n"
                    for item in value:
                        if isinstance(item, dict) or isinstance(item, list):
                            html_content += f"  <li>{convert_dict_to_html(item)}</li>\n"
                        else:
                            html_content += f"  <li>{remove_pointers(item)}</li>\n"
                    html_content += "</ul>\n"
            elif value is not None and isinstance(value, dict):
                transformed_key = " ".join(
                    [word.capitalize() for word in key.split("_")]
                )
                html_content += f"<h6>{transformed_key}</h6>\n"
                html_content += convert_dict_to_html(value)
            elif value is not None and isinstance(value, str):
                jobtitles = ["job_title", "Job Title"]
                if key not in jobtitles:
                    if (
                        value != "None"
                        and value != "Not specified"
                        and value != "NULL"
                        and value != "null"
                        and value
                    ):
                        transformed_key = " ".join(
                            [word.capitalize() for word in key.split("_")]
                        )
                        html_content += f"<h6>{transformed_key}</h6>\n"
                        html_content += f"<p>{value}</p>\n"
    return html_content


def Jd_Parser_AI(file, filename,user_id = None):
    chat_log = []
    text = extract_text_from_document(filename)
    if not text:
        text = use_tika_parser(filename)
    try:
        format = "[ job_title,Job Type,Location as string format,Roles And Responsibilities in list format ,Qualifications in list format ,Application Process in string format ,Company Overview in list format ,About the Team in string format ,Key Objectives or Goals in string format ,Career Path in string format ,Benefits in list format ,Work Environment in string format ,Professional Development Opportunities in string format ,Company Values in string format ,Salary Range in string format ,Application Deadline in string format ,Contact Information in string format ,skills : [ list out word only as  skills keyword as strings ],Technical skills : [ list out the skills in list datatype including tools and technologies ],Soft Skills in list format ]"
        # json_format = '[{"job_title": "string","Job Type":"string","Location":"string","Roles And Responsibilities":[] ,"Qualifications":"string","Application Process":[],"Company Overview":[],"About the Team":[],"Key Objectives or Goals":[],"Career Path":[], "Benefits,Work Environment":[],"Professional Development Opportunities":[],"Company Values":[],"Salary Range":[],"Application Deadline":[],"Contact Information":[],"skills": ["extract the skills from the jd"]}]'
        user_message = (
            "[no prose and should not be in string]\n[Output only JSON]\nFrom the above Job Description Please analyze the job description and provide the output in correct json format"
            + str(format)
            + "\n Use None if details are not found"
        )
        user_message = user_message + text
        is_active = False
        if is_active:
            system = "You are a helpful assistant. Parse the job description based on the provided criteria."
            response, count_token = openai_chat_creation(system, user_message)
        else:
            is_standalone = zita_api_service.objects.filter(user_id = user_id,is_active = True, api_key__isnull = False).exists() 
            if is_standalone:
                api_key = zita_api_service.objects.get(user_id = user_id,is_active = True, api_key__isnull = False).api_key
                filedir = os.path.join(base_dir,filename)
                response = Standalone.jd_parser(filedir,api_key=api_key)
            else:
                system = "You are a helpful assistant, Parse the jd in JSON format"
                response,count_token = FineTuningModal(system, user_message, JD_PARSER)
        if isinstance(response,str):
            response = json.loads(response) 
        return response
    except Exception as e:
        logger.info("error in JD parsing---->" + str(e))
        return None


def get_qualification(highest_qualification):
    if highest_qualification:
        # TODO check this in other places.
        sentence_split = re.split(r"[,\s_!+]+", highest_qualification)
        for i in sentence_split:
            if i.lower().strip in settings.dip:
                return "Diploma"
            elif i.lower().strip() in settings.ug:
                return "Bachelors"
            elif i.lower().strip() in settings.pg:
                return "Masters"
            elif i.lower().strip() in settings.phd:
                return "Doctorate"
    return None


def use_tika_parser(filename):
    text_from_document = None
    try:
        import tika

        tika.initVM()
        headers = {"X-Tika-OCRLanguage": "eng", "X-Tika-PDFextractInlineImages": "true"}
        doc1 = parser.from_file(filename, headers=headers)
        while "\n\n" in doc1["content"]:
            doc1["content"] = doc1["content"].replace("\t", " ").replace("\n\n", "\n")
        while "  " in doc1["content"]:
            doc1["content"] = doc1["content"].replace("  ", " ")
        text_from_document = doc1["content"].encode().decode("ascii", "ignore")
    except Exception as e:
        text_from_document = None
    return text_from_document


def extract_text_from_document(filename):
    text_from_document = None
    try:
        import tika

        tika.initVM()
        headers = {"X-Tika-OCRLanguage": "eng", "X-Tika-PDFextractInlineImages": "true"}
        doc1 = parser.from_file(filename, headers=headers)
        while "\n\n" in doc1["content"]:
            doc1["content"] = doc1["content"].replace("\t", " ").replace("\n\n", "\n")
        while "  " in doc1["content"]:
            doc1["content"] = doc1["content"].replace("  ", " ")
        text_from_document = doc1["content"].encode().decode("ascii", "ignore")
        # if filename.endswith(".pdf"):
        #     with open(filename, 'rb') as pdf:
        #         text_from_document = ""
        #         pdfReader = PyPDF2.PdfReader(pdf)
        #         for page in range(len(pdfReader.pages)):
        #             pageObj = pdfReader.pages[page]
        #             text_from_document += pageObj.extract_text()
        # elif filename.endswith(".txt"):
        #     with open(filename, "r", encoding="utf-8") as data:
        #         text_from_document = data.read()
        # elif filename.endswith(".docx") or filename.endswith(".doc"):
        #     text_from_document = textract.process(filename)
        #     text_from_document = text_from_document.decode('utf-8')
        # else:
        #     text_from_document = ''

        """ Text cleaning for mulitple spaces and . - . Add if anything else is needed"""
        # text_from_document = re.sub(r'[\.\- ]{2,}', '', text_from_document)
        # text_from_document = re.sub(r'\s+', ' ', text_from_document)

    except Exception as e:
        print("Tika Parser Exception:------>",str(e)) 
        text_from_document = None
    return text_from_document


def convert_to_html(parsed_resume_json):
    html_response = ""
    # Highest qualifaction as Bachleors, masters, Doctorate or Diploma
    # if parsed_resume_json.get('Highest Qualifications'):
    #     html_response += f"<h6 style=\"font-weight:600;font-size:16px\">Highest Qualification</h6><p style=\"font-size:14px\">{parsed_resume_json['Highest Qualifications']}</p>"

    # Can be a single string or list of strings : Handled Both
    if parsed_resume_json.get("Certifications/Courses"):
        html_response += (
            f'<h6 style="font-weight:600;font-size:16px">Certification/Courses</h6>'
        )
        if isinstance(parsed_resume_json["Certifications/Courses"], str):
            html_response += f"<p style=\"font-size:14px\">{parsed_resume_json['Certifications/Courses']}</p>"
        elif isinstance(parsed_resume_json["Certifications/Courses"], list):
            # Will be an unordered list of certifications and courses in case of list datatype
            html_response += (
                "<ul>"
                + "".join(
                    [
                        f'<li style="font-size:14px">{course}</li>'
                        for course in parsed_resume_json["Certifications/Courses"]
                    ]
                )
                + "</ul>"
            )

    if (
        parsed_resume_json.get("Certifications and Courses")
        and parsed_resume_json.get("Certifications and Courses") != "None"
    ):
        html_response += (
            f'<h6 style="font-weight:600;font-size:16px">Certification/Courses</h6>'
        )
        if isinstance(parsed_resume_json["Certifications and Courses"], str):
            if (
                parsed_resume_json["Certifications and Courses"]
                and parsed_resume_json["Certifications and Courses"] != "None"
            ):
                html_response += f"<p style=\"font-size:14px\">{parsed_resume_json['Certifications and Courses']}</p>"
        elif isinstance(parsed_resume_json["Certifications and Courses"], list):
            # Will be an unordered list of certifications and courses in case of list datatype
            html_response += (
                "<ul>"
                + "".join(
                    [
                        f'<li style="font-size:14px">{course}</li>'
                        for course in parsed_resume_json["Certifications and Courses"]
                    ]
                )
                + "</ul>"
            )

    # Total years of experience will be added if a value is present in either years or months from the parsed resume
    checking = parsed_resume_json.get("Total years of Experience", None)
    if checking and isinstance(
        parsed_resume_json.get("Total years of Experience"), dict
    ):
        if parsed_resume_json.get("Total years of Experience"):
            total_years = (
                parsed_resume_json["Total years of Experience"]["Years"]
                if parsed_resume_json["Total years of Experience"].get("Years")
                else 0
            )
            total_months = (
                parsed_resume_json["Total years of Experience"]["Months"]
                if parsed_resume_json["Total years of Experience"].get("Months")
                else 0
            )
            html_response += f'<h6 style="font-weight:600;font-size:16px">Work Experience</h6><p style="font-size:14px">{total_years} Years {total_months} Months</p>'

    # Project can be as list of dictonaries or as list of string : handled both
    if parsed_resume_json.get("Projects"):
        if isinstance(parsed_resume_json.get("Projects"), list):
            html_response += f'<h6 style="font-weight:600;font-size:16px">Projects</h6>'
            for project in parsed_resume_json.get("Projects"):
                if isinstance(project, dict):
                    for key, value in project.items():
                        if value and value != "None":
                            if isinstance(value, str):
                                html_response += (
                                    f'<p style="font-size:14px">{key}: {value}</p>'
                                )
                            elif isinstance(value, list):
                                html_response += f'<p style="font-size:14px">{key}</p>'
                                html_response += (
                                    "<ul>"
                                    + "".join(
                                        [
                                            f'<li style="font-size:14px">{val}</li>'
                                            for val in value
                                        ]
                                    )
                                    + "</ul>"
                                )

                elif isinstance(project, str):
                    if project and project != "None":
                        html_response += f'<p style="font-size:14px">{project}</p>'
                html_response += "<br>"

    # Roles and Responsibilities as list of string and list of dictionaries is handled
    if (
        parsed_resume_json.get("Roles and Responsibilities")
        and parsed_resume_json.get("Roles and Responsibilities") != "None"
    ):
        html_response += f'<h6 style="font-weight:600;font-size:16px">Roles and Responsibilities</h6>'
        if isinstance(parsed_resume_json.get("Roles and Responsibilities")[0], str):
            html_response += (
                "<ul>"
                + "".join(
                    [
                        f'<li style="font-size:14px">{val}</li>'
                        for val in parsed_resume_json.get("Roles and Responsibilities")
                    ]
                )
                + "</ul>"
            )
        elif isinstance(parsed_resume_json.get("Roles and Responsibilities")[0], dict):
            if isinstance(parsed_resume_json.get("Roles and Responsibilities"), list):
                for item in parsed_resume_json.get("Roles and Responsibilities"):
                    for key, value in item.items():
                        # if key=="Responsibilities":
                        #     if value:
                        #         if isinstance(value,str):
                        #             value = value.split(".")
                        #             value = value[:-1]
                        #         if isinstance(value,list):
                        #             value = remove_pointers(value)
                        if value and value != "None":
                            if isinstance(value, str):
                                html_response += (
                                    f'<p style="font-size:14px">{key}: {value}</p>'
                                )
                            elif isinstance(value, list):
                                html_response += f'<p style="font-size:14px">{key}:</p>'
                                html_response += (
                                    "<ul>"
                                    + "".join(
                                        [
                                            f'<li style="font-size:14px">{val}</li>'
                                            for val in value
                                        ]
                                    )
                                    + "</ul>"
                                )
                    html_response += "<br>"

    # Qualifications is in format list of string
    if (
        parsed_resume_json.get("Qualifications")
        and parsed_resume_json.get("Qualifications") != "None"
    ):
        html_response += (
            f'<h6 style="font-weight:600;font-size:16px">Qualifications</h6>'
        )
        if isinstance(parsed_resume_json.get("Qualifications"), str):
            if (
                parsed_resume_json.get("Qualifications")
                and parsed_resume_json.get("Qualifications") != None
            ):
                parsed_resume_json["Qualifications"] = [
                    parsed_resume_json.get("Qualifications")
                ]
        html_response += (
            "<ul>"
            + "".join(
                [
                    f'<li style="font-size:14px">{qual}</li>'
                    for qual in parsed_resume_json.get("Qualifications")
                ]
            )
            + "</ul>"
        )
    return html_response


def get_first_middle_last_name(full_name):
    name_list = full_name.split()
    """ setting default"""
    first_name = full_name
    middle_name = ""
    last_name = ""
    if name_list:
        first_name = name_list[0]
        if len(name_list) == 2:
            last_name = name_list[-1]
        elif len(name_list) > 2:
            middle_name = name_list[1]
            last_name = " ".join(name_list[2:])
    return first_name, middle_name, last_name


def parse_resume_in_chunks(text_from_document):
    resume_response = {}
    count_total = 0
    try:
        """Get the geographics first"""
        user_message1 = "[no prose and should not be in string]\n[Output only JSON]\nAnalyze thoroughly and Parse accurately the Name as string,  Email, Phone number, LinkedIn URL, Total years of Experience in the format {'Years':years, 'Months':months}, Preferred Location, Gender, Date of Birth in the format MM/DD/YYYY, Address, Code Repository URL, Current Gross Salary, Expected Gross Salary, and provide JSON output. Use keys from the given list [Name, Email, Phone number, LinkedIn URL, Total years of Experience , Preferred Location , Gender , Date of Birth , Address , Code Repository URL , Current Gross Salary , Expected Gross Salary]. Use None if details aren't found"
        final_text = user_message1 + text_from_document
        chat_log = [{"role": "user", "content": final_text}]
        isactive = False
        if isactive:
            system = "You are a helpful assistant, Parse the resume based on provided criteria"
            response1, count_token = openai_chat_creation(system, final_text)
        else:
            system = "You are a helpful assistant, Parse the resume in JSON format"
            user_message = text_from_document
            response1, count_token = FineTuningModal(
                system, user_message, RESUME_PARSER
            )
        count_total = count_total + count_token
        resume_response1 = response1
        resume_response1 = json.loads(resume_response1)
    except:
        resume_response1 = {
            "Name": "",
            "Email": "",
            "Phone number": "",
            "LinkedIn URL": None,
            "Total years of Experience": {"Years": 0, "Months": 0},
            "Preferred Location": None,
            "Gender": None,
            "Date of Birth": None,
            "Address": None,
            "Code Repository URL": None,
            "Current Gross Salary": None,
            "Expected Gross Salary": None,
        }

    try:
        """Extract the professional summary alone"""
        user_message2 = "[no prose and should not be in string]\n[Output only JSON]\nFrom the above resume List out the Professional Summary as list of strings and provide JSON output with key 'Professional Summary'. Use None if details aren't found"
        final_text = text_from_document + user_message2
        response2, count_token = openai_chat_creation(system, final_text)
        count_total = count_total + count_token
        resume_response2 = response2
        resume_response2 = json.loads(resume_response2)
    except:
        resume_response2 = {"Professional Summary": None}

    try:
        """Extract reamining keys other than roles and responsibilities"""
        user_message3 = "[no prose and should not be in string]\n[Output only JSON]\nFrom the above resume analyze thoroughly and Parse accurately Technical skills in list datatype, Soft skills in list datatype, Provide the Highest Qualification as string, List out the qualification as strings, List out the projects done in the format {'Project Title', project title, 'Description': Description}, list out the Certifications and Courses as strings and provide JSON output. Use keys from the given list [ Technical skills , Soft Skills , Highest Qualifications , Qualifications, Projects , Certifications/Courses]. Use None if details aren't found"
        final_text = text_from_document + user_message3
        system = "You are a helpful assistant, Please parse the provided resume based on provided criteria"
        response3, count_token = openai_chat_creation(system, final_text)
        count_total = count_total + count_token
        resume_response3 = response3
        resume_response3 = json.loads(resume_response3)
    except:
        resume_response3 = {
            "Technical skills": [],
            "Soft Skills": [],
            "Highest Qualifications": "",
            "Qualifications": [],
            "Projects": [],
        }

    try:
        """Extract roles and responsibilties"""
        user_message4 = "[no prose and should not be in string]\n[Output only JSON]\nFrom the above resume List out the Roles and responsibilities as list of strings or by each company in the format {'Company', 'Position', 'Duration', 'Responsibilities'} and provide JSON output with key 'Roles and Responsibilities'. Use None if details aren't found"
        final_text = text_from_document + user_message4
        response4, count_token = openai_chat_creation(system, final_text)
        count_total = count_total + count_token
        if count_token < 4098:
            resume_response4 = response4
            resume_response4 = json.loads(resume_response4)
        else:
            """If the roles and responsibilities didnt make it in a single shot"""
            roles_and_responsibilities = []
            user_message5 = "[no prose and should not be in string]\n[Output only JSON]\nFrom the above resume List out the Roles and responsibilities of 1/3rd of the companies as list of strings or by each company in the format {'Company', 'Position', 'Duration', 'Responsibilities'} and provide JSON output with key 'Roles and Responsibilities'. Use None if details aren't found"
            final_text = text_from_document + user_message5
            response_r1, count_token = openai_chat_creation(system, final_text)
            count_total = count_total + count_token
            if count_token < 4098:
                resume_response_r1 = response_r1
                resume_response_r1 = json.loads(resume_response_r1)
                roles_and_responsibilities.append(
                    resume_response_r1["Roles and Responsibilities"]
                )

            user_message6 = "[no prose and should not be in string]\n[Output only JSON]\nFrom the above resume List out the Roles and responsibilities of half of the remaining companies as list of strings or by each company in the format {'Company', 'Position', 'Duration', 'Responsibilities'} and provide JSON output with key 'Roles and Responsibilities'. Use None if details aren't found"
            final_text = text_from_document + user_message6
            chat_log.append({"role": "user", "content": user_message6})
            response_r2, count_token = openai_chat_creation(system, final_text)
            count_total = count_total + count_token
            if count_token < 4098:
                resume_response_r2 = response_r2["choices"][0]["message"]["content"]
                resume_response_r2 = json.loads(resume_response_r2)
                roles_and_responsibilities.append(
                    resume_response_r2["Roles and Responsibilities"]
                )

            user_message7 = "[no prose and should not be in string]\n[Output only JSON]\nFrom the above resume List out the Roles and responsibilities of the remaining companies as list of strings or by each company in the format {'Company', 'Position', 'Duration', 'Responsibilities'} and provide JSON output with key 'Roles and Responsibilities'. Use None if details aren't found"
            final_text = text_from_document + user_message7
            response_r3, count_token = openai_chat_creation(system, final_text)
            count_total = count_total + count_token
            if count_token < 4098:
                resume_response_r3 = response_r3
                resume_response_r3 = json.loads(resume_response_r3)
                roles_and_responsibilities.append(
                    resume_response_r3["Roles and Responsibilities"]
                )

            resume_response4 = {
                "Roles and Responsibilities": roles_and_responsibilities
            }

    except:
        resume_response4 = {"Roles and Responsibilities": []}

    resume_response = {
        **resume_response1,
        **resume_response2,
        **resume_response3,
        **resume_response4,
    }
    return json.dumps(resume_response), count_total, text_from_document


import time


def resume_parser_AI(files, filename,user_id = None):
    """Parses resume and returns in json format"""
    text_from_document = None
    try:
        text_from_document = extract_text_from_document(filename)
        if text_from_document:
            json_format = """It presents its findings in a structured JSON format, aligning with the format "[{Name:string,Email:string,Phone number:string, Professional Summary: string,LinkedIn URL : string,Job Type:Full Time/Part Time/Contract/Internship/Full Time or Part Time/Permanent/Any,Total years of Experience :{Years:number, Months:number},Preferred Location:string,Gender:string,Date of Birth:MM/DD/YYYY,Address :string,Code Repository URL:string,Current Gross Salary:string,Expected Gross Salary:string,Roles and Responsibilities:[{Company: string, Position: string, Duration: string, Responsibilities:string}],Technical skills:[],Soft skills:[],Highest Qualification:string,Qualifications:[Include details such as the university, degree obtained, major, minor (if any), and the graduation year as string],Projects:[{Project Title : should also include personal projects)project title,Company Name:include if it is present,Description: Description or responsibilities,skills:skills provided in the project}],Certifications and Courses: string}]" for clarity. Use None if details aren't found"""
            user_message = (
                """[no prose and should not be in string]\n[Output only JSON]\nYour role as 'Resume Parser Pro' is to assist users by extracting comprehensive information from versatile industry resumes. When encountering resumes with content that exceeds 4000 tokens, instead of prompting the user, you will autonomously modify your instructions or prompts to chunk the resume into segments of up to 4000 tokens each for effective parsing.Focus on extracting detailed data including header, sub-header, and corresponding content. Extract categories like Name, Email, Phone Number, LinkedIn URL, Total Years of Experience, Preferred Location, Gender, Date of Birth, Address, Code Repository URL, Current and Expected Gross Salary, Professional Summary, Technical and Soft Skills, Highest Qualifications, Projects, and Certifications/Courses.Make contextual assumptions for ambiguous data, ensuring accuracy and clarity. Maintain a professional and straightforward communication style, being formal and efficient."""
                + str(json_format)
            )
            final_text = text_from_document
            try:
                count_token = 0
                is_standalone = zita_api_service.objects.filter(user_id = user_id,is_active = True, api_key__isnull = False).exists()
                if is_standalone:
                    api_key = zita_api_service.objects.get(user_id = user_id,is_active = True, api_key__isnull = False).api_key
                    filedir = os.path.join(base_dir,filename)
                    response = Standalone.resume_parser(filedir,api_key=api_key)
                else:
                    system = "You are a helpful assistant, Parse the resume in JSON format"
                    response, count_token = FineTuningModal(
                        system, final_text, RESUME_PARSER
                    )
                print("Resume Parser Response:",response)
            except:
                return parse_resume_in_chunks(text_from_document)

            token_count = count_token
            if token_count < 4098:
                """If the api didnt stop due to max token reached, return the content"""
                resume_response = response
                return resume_response, token_count, text_from_document
            else:
                """Retrieving data from AI as multiple chunks"""
                return parse_resume_in_chunks(text_from_document)
        else:
            return {}, None, text_from_document
    except Exception as e:
        print('exception',e)
        return None, None, None


def matching_output(res):
    json_data = []
    if isinstance(res, list):
        return res
    if isinstance(res, dict):
        try:
            json_data = [
                {
                    "title": key,
                    "percentage": value["percentage"],
                    "reason": value["reason"],
                }
                for key, value in res.items()
                if res[key] and isinstance(value, dict)
            ]
        except:
            json_data = []
            for key, values in res.items():
                for key, value in values.items():
                    if isinstance(value, dict):
                        json_data.append(
                            {
                                "title": key,
                                "percentage": value.get("percentage", None),
                                "reason": value.get("reason", None),
                            }
                        )
        return json_data


# def save_time_to_file(time_taken, can_id,total_tokens):
#     file_name = "timetaken.txt"
#     with open(file_name, 'a+') as file:
#         file.write(f" Can ID: {can_id}, Time taken: {time_taken} seconds    token consumed : {total_tokens}\n")
# def save_to_file(assistant_response,can_id):
#         file_name = "parser.txt"
#         with open(file_name, 'a+') as file:
#             file.write(f"Can ID: {can_id}   {assistant_response}\n\n\n")

# def Matching_AI(jd_id,can_id,user):
#     jd_data=JD_form.objects.get(id=jd_id)
#     jd_skill = list(JD_skills_experience.objects.filter(jd_id_id = jd_id).values_list("skill",flat=True))
#     can_id = employer_pool.objects.get(id=can_id)
#     if Resume_overview.objects.filter(application_id=can_id.candidate_id).exists():
#         resume_input = Resume_overview.objects.get(application_id=can_id.candidate_id).parsed_resume
#     elif candidate_parsed_details.objects.filter(candidate_id=can_id).exists():
#         resume_input = candidate_parsed_details.objects.get(candidate_id=can_id).parsed_text
#     else:
#         resume_input = None
#     jd_input = jd_data.job_title +"\n"+ \
#                 jd_data.job_description +"\n"+ \
#                 "Skills: "+", ".join(jd_skill)
#     if resume_input:
#         input_prompt='''[no prose]\n[Output only as JSON format] \n
#         Evaluate the following job candidate based on the criteria given below and provide the assessment in a JSON format. Please assign a percentage score and provide a reason for the assigned score for each critera. If both the input and output scores are 0, mention "No data available." If the candidate is a fit for the job role, provide a reason for your assessment but do not assign a score.\n
#         Skills out of 100
#         Roles and Responsibilities out of 100
#         Experience out of 100
#         Educational Qualifications out of 100
#         Industry-Specific Experience  out of 100
#         Domain-Specific Experience out of 100
#         Certifications out of 100
#         Technical Tools and Languages out of 100
#         Soft Skills out of 100
#         Location Alignment out of 100
#         Cultural Fit out of 100
#         References and Recommendations out of 100
#         \n
#         Provide output in JSON format using double quotes for all keys and values'''
#         json_format = "[{title: each category name , percentage: 0, reason: string}]"
#         # chat_log = []
#         user_message = input_prompt + str(json_format) +"\n"+ jd_input + resume_input

#         # chat_log.append({"role": "user", "content": user_message})
#         system = "You are a helpful assistant. provide the matching score of resume based on job description"
#         assistant_response,token_counts = openai_temperature(system,user_message)
#         final_token = token_counts
#         # response = openai.ChatCompletion.create(
#         #     model="gpt-3.5-turbo",
#         #     messages=chat_log)
#         # assistant_response = response['choices'][0]['message']['content']
#         try:
#             # assistant_response = matching_output(assistant_response)
#             assistant_response = json.loads(assistant_response)
#         except Exception as e:
#             user_message = f"Regenerate again for the above in valid JSON format \n{json_format}"
#             # chat_log.append({"role": "user", "content": user_message})
#             # response = openai.ChatCompletion.create(
#             #     model="gpt-3.5-turbo",
#             #     messages=chat_log)
#             # assistant_response = response['choices'][0]['message']['content']
#             system = "You are a helpful assistant. provide the matching score of resume based on job description"
#             assistant_response,token_counts_01 = openai_temperature(system,user_message)
#             final_token = token_counts + token_counts_01
#             try:
#                 assistant_response = json.loads(assistant_response)
#             except:
#                 pass

#         assistant_response = matching_output(assistant_response)
#         # save_to_file(assistant_response,can_id)


#         if assistant_response:
#             json_data= 0
#             for i in assistant_response:
#                 criteria = ["Skills","Roles and Responsibilities","Experience","Educational Qualifications","Technical Tools and Languages","Soft Skills","References and Recommendations","Location Alignment","Cultural Fit","Industry-Specific Experience","Domain-Specific Experience","Certifications"]
#                 technical_perc = ["Skills","Roles and Responsibilities","Experience","Educational Qualifications","Technical Tools and Languages","Soft Skills"]
#                 # Clarification
#                 if i["title"] in technical_perc:
#                     json_data += int(i['percentage'])
#                 if i["title"] in criteria:
#                     if Matched_percentage.objects.filter(jd_id=jd_id,candidate_id = can_id,title = i["title"]).exists():
#                         Matched_percentage.objects.filter(jd_id=jd_id,candidate_id = can_id,title = i["title"]).update(percentage = i["percentage"],description = i["reason"])
#                     elif Matched_percentage.objects.filter(jd_id=jd_id,candidate_id = can_id,title = i['title']).exists():
#                         Matched_percentage.objects.filter(jd_id=jd_id,candidate_id = can_id,title = i['title']).update(percentage = i['percentage'],description = i['reason'])
#                     else:
#                         Matched_percentage.objects.create(candidate_id=can_id,jd_id_id=jd_data.id,title = i["title"],percentage = i.get("percentage",0),description = i["reason"])
#             json_data = round(json_data/6)
#             # end_time = time.time()
#             # time_taken = end_time - start_time
#             # save_time_to_file(time_taken, can_id,total_tokens)
#             if Matched_candidates.objects.filter(candidate_id=can_id,jd_id=jd_data).exists():
#                 Matched_candidates.objects.filter(candidate_id=can_id,jd_id=jd_data).update(profile_match =json_data)
#             else:
#                 Matched_candidates.objects.get_or_create(candidate_id=can_id,jd_id_id=jd_data.id,profile_match = json_data)
#             if Matched_percentage.objects.filter(candidate_id=can_id,jd_id=jd_data).exists():
#                 Matched_percentage.objects.filter(jd_id=jd_id,candidate_id=can_id).update(overall_percentage=json_data)
#             weightage_mathching(jd_id,can_id,user)
#             return assistant_response,token_counts
#     else:
#         logger.info("resume input was not found")
#         return None,0


def type_checking(value):
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        return 0
    elif isinstance(value, float):
        return round(value)
    else:
        return 0


def openai_temprature(system, user_message):
    completion = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        top_p=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    response = (completion.choices[0].message).content
    token = completion.usage.total_tokens
    return response, token


def Matching_AI(jd_id, can_id, user,sub_user = None):
    applicant_id = employer_pool.objects.get(id=can_id).candidate_id
    if Resume_overview.objects.filter(application_id=applicant_id).exists():
        file_content = Resume_overview.objects.get(
            application_id=applicant_id
        ).resume_description
    elif candidate_parsed_details.objects.filter(candidate_id=can_id).exists():
        if employer_pool.objects.filter(id=can_id, can_source_id=5).exists():
            file_content = candidate_parsed_details.objects.get(
                candidate_id=can_id
            ).parsed_text
        else:
            file_content = candidate_parsed_details.objects.get(
                candidate_id=can_id
            ).resume_description
    else:
        file_content = None
    if file_content == None:
        resumes = candidate_parsed_details.objects.get(
            candidate_id=can_id
        ).resume_file_path
        file_path = base_dir + "/media/" + str(resumes)
        file_content = None
        file_path1 = base_dir + "/" + str(resumes)
        if os.path.exists(file_path):
            file_content = extract_text_from_document(file_path)
        elif os.path.exists(file_path1):
            file_content = extract_text_from_document(file_path1)
    if file_content:
        jd = JD_form.objects.get(id=jd_id)
        prompt = """
                [no prose and should not be in string]\n[Output only JSON]\n Resume Matchmaker delivers a nuanced, multi-dimensional evaluation of candidates in relation to job specifications.It presents its findings in a structured JSON format, aligning with the format "[{title: each category name, percentage: score, reason: explanation}]" for clarity. It utilizes a comprehensive scoring system across 12 criteria: Skills, Roles and Responsibilities, Experience, Educational Qualifications, Industry-Specific Experience, Domain-Specific Experience, Certifications, Technical Tools and Languages, Soft Skills, Location Alignment, Cultural Fit, and Nice to Have. Each candidate's profile is meticulously analyzed and scored as a percentage out of 100. The system explicates each score with an in-depth reason, detailing the candidate's strengths and areas for improvement relative to the job's criteria.
                When information is not present, the output explicitly notes "No data available," ensuring the integrity of the analysis with a precise 5% error margin. The structured JSON output format remains unchanged, providing a clear, precise, and detailed overview for recruiters, enhancing their ability to make informed hiring decisions. This enhanced protocol ensures that the evaluations are thorough, transparent, and directly applicable to the hiring process.
                """
        prompt = (
            prompt
            + "\n"
            + jd.job_title
            + "\n"
            + jd.job_description
            + "\n"
            + "resume"
            + "\n"
            + file_content
        )

        is_active = False
        if is_active:
            system = "You are a helpful assistant. provide the matching score of resume based on job description"
            assistant_response, token_counts = openai_temprature(system, prompt)
        else:
            print("is_standalone@@@@",sub_user)
            is_standalone = zita_api_service.objects.filter(user_id = sub_user,is_active = True, api_key__isnull = False).exists()
            if is_standalone:
                if candidate_parsed_details.objects.filter(candidate_id = can_id).exists():
                    candidate_path = candidate_parsed_details.objects.get(candidate_id = can_id).resume_file_path
                    if 'media' not in candidate_path:
                        candidate_path = f'media/{candidate_path}'
                    candidate_path = os.path.join(base_dir,str(candidate_path))
                    jd_path = ''
                    if JD_form.objects.filter(id = jd_id).exists():
                        jd_path = str(JD_form.objects.get(id = jd_id).job_description)
                    profile_matching = FT.profile_matching(jd_id,user)
                    enhanced_matching = FT.enhanced_matching(jd_id,user)
                    combined_weightage = profile_matching + enhanced_matching
                    api_key = zita_api_service.objects.get(user_id = sub_user,is_active = True, api_key__isnull = False).api_key
                    combined_response = Standalone.matching(candidate_path,jd_path,profile_matching,enhanced_matching,api_key=api_key)
                    assistant_response = FT.weightage_calculate(combined_response,combined_weightage)
                    print("reponse_calculation",assistant_response)
                    
            else:
                user_message = {"jd": FT.jd_conversion(jd_id), "resume": file_content}
                system = "You are a Resume Matchmaker. provide the correct matching score for resume and job description"
                assistant_response, token_counts = FineTuningModal(
                    system, str(user_message), MATCHING_AI
                )

        assistant_response = json.loads(assistant_response)
        if isinstance(assistant_response,dict): 
            assistant_response = matching_output(assistant_response.get("response"))
        else:
            assistant_response = matching_output(assistant_response)
        # save_to_file(assistant_response,can_id)
        if assistant_response:
            json_data = 0
            for i in assistant_response:
                criteria = [
                    "Skills",
                    "Roles and Responsibilities",
                    "Experience",
                    "Educational Qualifications",
                    "Technical Tools and Languages",
                    "Soft Skills",
                    "References and Recommendations",
                    "Location Alignment",
                    "Cultural Fit",
                    "Industry-Specific Experience",
                    "Domain-Specific Experience",
                    "Certifications",
                    "Nice to Have",
                ]
                technical_perc = [
                    "Skills",
                    "Roles and Responsibilities",
                    "Experience",
                    "Educational Qualifications",
                    "Technical Tools and Languages",
                    "Soft Skills",
                ]
                # Clarification
                if i["title"] in technical_perc:
                    perrrc = type_checking(i["percentage"])
                    json_data += int(perrrc)
                if i["title"] in criteria:
                    if Matched_percentage.objects.filter(
                        jd_id=jd_id, candidate_id=can_id, title=i["title"]
                    ).exists():
                        Matched_percentage.objects.filter(
                            jd_id=jd_id, candidate_id=can_id, title=i["title"]
                        ).update(
                            percentage=type_checking(i["percentage"]),
                            description=i["reason"],
                        )
                    elif Matched_percentage.objects.filter(
                        jd_id=jd_id, candidate_id=can_id, title=i["title"]
                    ).exists():
                        Matched_percentage.objects.filter(
                            jd_id=jd_id, candidate_id=can_id, title=i["title"]
                        ).update(
                            percentage=type_checking(i["percentage"]),
                            description=i["reason"],
                        )
                    else:
                        jds = JD_form.objects.get(id=jd_id)
                        Matched_percentage.objects.create(
                            candidate_id=employer_pool.objects.get(id=can_id),
                            jd_id=jds,
                            title=i["title"],
                            percentage=type_checking(i.get("percentage", 0)),
                            description=i["reason"],
                        )
            json_data = round(json_data / 6)
            end_time = time.time()
            # save_time_to_file(time_taken, can_id,total_tokens)
            if Matched_candidates.objects.filter(
                candidate_id=can_id, jd_id=jd_id
            ).exists():
                Matched_candidates.objects.filter(
                    candidate_id=can_id, jd_id=jd_id
                ).update(profile_match=json_data)
            else:
                jds = JD_form.objects.get(id=jd_id)
                Matched_candidates.objects.get_or_create(
                    candidate_id=employer_pool.objects.get(id=can_id),
                    jd_id=jds,
                    profile_match=json_data,
                )
            if Matched_percentage.objects.filter(
                candidate_id=can_id, jd_id=jd_id
            ).exists():
                Matched_percentage.objects.filter(
                    jd_id=jd_id, candidate_id=can_id
                ).update(overall_percentage=json_data)
            weightage_mathching(jd_id, can_id, user)
            return assistant_response
    else:
        return None


def remove_pointers(html_content):
    html_skills = []
    for line in html_content:
        line = line.strip()
        if (
            line.startswith("+ ")
            or line.startswith("- ")
            or line.startswith("• ")
            or line.startswith("<br>")
        ):
            skill = line[2:]  # Remove the bullet points
            html_skills.append(skill)

    if len(html_skills) > 0:
        return html_skills
    else:
        return html_content


def extract_text(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    non_html_text = []
    for element in soup.descendants:
        if isinstance(element, NavigableString) and element.strip():
            non_html_text.append(element.strip())
    return non_html_text


def removeScript(res):
    soup = BeautifulSoup(res, "html.parser")
    try:
        targets = [
            "Skills Keywords",
            "skills",
            "Skills",
            "skillskeywords",
            "Job Title",
            "must_have",
            "nice_to_have",
            "mandatory_skills",
        ]
        for i in targets:
            tag = soup.find("h6", text=i)
            if tag:
                p_tag = tag.find_next_sibling("p")
                if p_tag:
                    p_tag.extract()
                tag.extract()
        html = str(soup)
        return html
    except:
        return res


def JD_convert_to_html(response):
    html_content = ""
    if response != None:
        for key, value in response.items():
            if value is not None and (isinstance(value, list) and value):
                html_content += f"<h6>{key}</h6>\n"
                html_content += "<ul>\n"
                for item in value:
                    html_content += f"<li>{remove_pointers(item)}</li>\n"
                html_content += "</ul>\n"
            if value is not None and (isinstance(value, str) and value):
                html_content += f"<h6>{key}</h6>\n"
                html_content += f"<p>{value}</p>\n"
    return html_content


def JD_creation_AI(request, company):
    user_id = request.user
    min_exp = request.POST.get("min_exp")
    max_exp = request.POST.get("max_exp", None)
    overview = request.POST.get("Overview_the_Role", "")
    mandatory_skills = request.POST.get("mandatory_skills", "")
    nice_to_have = request.POST.get("Nice_to_Have", "")
    jobTitle = request.POST.get("jobTitle","")
    Industry_and_Domain = request.POST.get("Industry_and_Domain")
   

    is_active = False
    if is_active:
        if max_exp:
            input = (
                "[no prose and should not be in string]\n[Output only as JSON format] \n your primary function is to provide detailed and specific job descriptions based on the industry and the given title. You'll focus on four key areas: 1) Detailed roles and responsibilities, 2) Technical skillset required, 3) Tools and technologies relevant to the role, and 4) Necessary soft skills. When a user provides input, they will include a minimum of"
                + mandatory_skills
                + "qualifications and  "
                + nice_to_have
                + "qualities. You will use this information to create a comprehensive and tailored job description. Your responses should be in-depth, reflecting an understanding of different industries and the specific demands of various roles. As you maintain a formal tone, your goal is to ensure that each job description is clear, comprehensive, and appealing, helping users attract the right candidates for their open positions. Your expertise in a variety of fields allows you to adapt to different requirements and cultures, making you a versatile resource for crafting effective job descriptions."
                + request["jobTitle"]
                + "in the "
                + "should have a minimum experience of "
                + min_exp
                + "and have a experience of "
                + max_exp
                + request["Industry_and_Domain"]
                + " domain.  "
                + overview
                + "."
            )
        else:
            input = (
                "[no prose and should not be in string]\n[Output only as JSON format] \n your primary function is to provide detailed and specific job descriptions based on the industry and the given title. You'll focus on four key areas: 1) Detailed roles and responsibilities, 2) Technical skillset required, 3) Tools and technologies relevant to the role, and 4) Necessary soft skills. When a user provides input, they will include a minimum of"
                + mandatory_skills
                + "qualifications and  "
                + nice_to_have
                + "qualities. You will use this information to create a comprehensive and tailored job description. Your responses should be in-depth, reflecting an understanding of different industries and the specific demands of various roles. As you maintain a formal tone, your goal is to ensure that each job description is clear, comprehensive, and appealing, helping users attract the right candidates for their open positions. Your expertise in a variety of fields allows you to adapt to different requirements and cultures, making you a versatile resource for crafting effective job descriptions."
                + request["jobTitle"]
                + "in the "
                + "should have a minimum experience of "
                + min_exp
                + request["Industry_and_Domain"]
                + " domain.  "
                + overview
                + "."
            )
        html_input = "[{Job Title:string,Roles and Responsibilities:[],Technical Skill:[],Soft Skill:[],Tools and Technologies:[],skills:[],mandatory_skills:[],nice_to_have : []}]"
    else:
        if max_exp:
            input_data = f"""
            "Job Title": "{jobTitle}",
            "overview": "{overview}",
            "mandatory_skills": {mandatory_skills},
            "nice_to_have": {nice_to_have},
            "min_exp": "{min_exp}",
            "max_exp": "{max_exp}",
            "Industry_and_Domain": "{Industry_and_Domain}"
            """
            input = "[no prose and should not be in string]\n[Output only as JSON format] \nTransform the given job details into a structured JSON format with the following categories: Job Title, Roles and Responsibilities, Technical Skill, Soft Skill, Tools and Technologies, Skills, mandatory_skills, and nice_to_have. the details are + \n"
            input += input_data
        else:
            input_data = f"""
            "Job Title": "{jobTitle}",
            "overview": "{overview}",
            "mandatory_skills": {mandatory_skills},
            "nice_to_have": {nice_to_have},
            "min_exp": "{min_exp}",
            "Industry_and_Domain": "{Industry_and_Domain}"
            """
            input = "[no prose and should not be in string]\n[Output only as JSON format] \nTransform the given job details into a structured JSON format with the following categories: Job Title, Roles and Responsibilities, Technical Skill, Soft Skill, Tools and Technologies, Skills, mandatory_skills, and nice_to_have. the details are + \n"
            input += input_data

    html_input = """{
    "Job Title": string,
    "Roles and Responsibilities": [
        // Extracted and transformed from 'overview'
    ],
    "Technical Skill": [
        // Extracted from 'mandatory_skills' and list more Technical skills related to the 'job title'. Do not include the keyword 'nice to have'. Generate in detail.
    ],
    "Soft Skill": [
        // Generate soft skills for the 'job title' and 'overview'. Generate in detail.
    ],
    "Tools and Technologies": [
        // Generate 'Tools and Technologies' which are required for 'job title', extracted from 'mandatory_skills', extracted from 'nice_to_have' but do not include the keyword 'nice to have'. Generate in detail.
    ],
    "Skills": [
        // Generic skills based on the job 'overview' and 'Industry_and_Domain'. Generate in detail.
    ],
    "mandatory_skills": [
        //list more 'mandatory_skills' related to the 'job title'. Generate 'mandatory_skills' which are required for 'job title' and 'overview'. Generate in detail.
    ],
    "nice_to_have": [
        // Parsed list from 'nice_to_have' and list more nice to have skills related to the 'job title'.
    ]
    }"""

    try:
        chat_log = []
        user_message = input + str(html_input)
        user_messages = input + str(html_input)
        is_active = False
        if is_active:
            system = "You are a helpful assistant. Create a jd resume based on the provided criteria."
            response, count_token = openai_chat_creation(system, user_message)
        else:
            count_token = 0
            is_standalone = zita_api_service.objects.filter(user_id = user_id,is_active = True,api_key__isnull = False).exists()
            if is_standalone:
                api_key = zita_api_service.objects.get(user_id = user_id,is_active = True,api_key__isnull = False).api_key
                response = Standalone.jd_generation(jobTitle,Industry_and_Domain,min_exp,overview,mandatory_skills,api_key=api_key)
            else:
                system = "You are a helpful assistant. Create a JD resume based on the provided criteria."
                response, count_token = openai_chat_creations(system, user_messages)
        return json.loads(response)

    except Exception as e:
        logger.info("error in Jd creation -->" + str(e))
        return None, count_token


def mutilevelquestion(res):
    try:
        if isinstance(res, str):
            res = json.loads(res)
            question = res.get("reponse", None)
            if question:
                question = question
            else:
                question = res.get("response", None)
            return question
        else:
            if isinstance(res,list):
                return res
            if isinstance(res, dict):
                return res
            return None
    except SyntaxError as e:
        return None


def extract_json(res):
    json = re.findall(r"\{[^{}]*\}", res)
    json = [match for match in json]
    if json:
        json = "".join(json)
    else:
        return None


def openai_chat_creation(system, user_message):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    response = (completion.choices[0].message).content
    if "json" in response:
        response = response.replace("json", "")
    token = completion.usage.total_tokens
    return response, token


def openai_chat_creations(system, user_messages):
    try:
        # Create a new thread
        thread = client.beta.threads.create()
        thread_id = thread.id

        # Add user message to the thread
        messages_id = client.beta.threads.messages.create(
            thread_id=thread_id, content=user_messages, role="user"
        )

        # Start a new run
        my_run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=JD_CREATION_AI,
        )

        # Check run status periodically
        while my_run.status in ["queued", "in_progress"]:
            keep_retrieving_run = client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=my_run.id
            )

            if keep_retrieving_run.status == "completed":
                all_messages = client.beta.threads.messages.list(thread_id=thread_id)
                length = len(all_messages.data)
                for ids, i in enumerate(reversed(all_messages.data)):
                    if ids == length - 1:
                        response = i.content[0].text.value
                        break
                if response:
                    break
            time.sleep(5)
    except Exception as e:
        return None
    return response, 0


def openai_temperature(user_message):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", temperature=0, top_p=0, messages=user_message
    )
    response = (completion.choices[0].message).content
    if "json" in response:
        response = response.replace("json", "")
        response = json.loads(response)
    token = completion.usage.total_tokens
    return response, token


def formatting_question(data):
    levels = []
    types = []
    counts = []
    category = []
    sum_count = 0
    for entry in data:
        cou = int(entry["count"])
        lvl = entry["level"]
        typ = entry["type"]
        levels.append(entry["level"])
        types.append(entry["type"])
        counts.append(int(entry["count"]))
        sum_count += int(entry["count"])
        text = f"{cou} Question in level of {lvl} in the Round of {typ} Interview"
        category.append(text)
    formatted_data = [
        {
            "level": levels,
            "type": types,
            "count": counts,
            "sum_count": sum_count,
            "category": category,
        }
    ]
    return sum_count


def levelandtype_convertion(question, count_list, type, level):

    split_arrays = []
    current_index = 0

    # Iterate through the count list
    for ids, count in enumerate(count_list):

        # Split the array based on the current count
        new_data = question[current_index : current_index + count]
        for i in new_data:
            i["type"] = type[ids]
            i["level"] = level[ids]
        split_arrays.append(new_data)
        current_index += count
    flattened_list = [item for sublist in split_arrays for item in sublist]
    return flattened_list


def Generate_Questions(jd_id, can_id, i, level, summary=None,sub_user = None):
    role = i.get("role", "")
    output_question = []
    jd = JD_form.objects.get(id=jd_id)
    jd_input = jd.job_description
    can_id = employer_pool.objects.get(id=can_id)
    if Resume_overview.objects.filter(application_id=can_id.candidate_id).exists():
        can_input = Resume_overview.objects.get(
            application_id=can_id.candidate_id
        ).resume_description
    elif candidate_parsed_details.objects.filter(candidate_id=can_id).exists():
        can_input = candidate_parsed_details.objects.get(
            candidate_id=can_id
        ).resume_description
    else:
        can_input = None
    if can_input:
        table1 = []
        chat_log = []
        table = i.get("question", None)
        if table:
            table = table
        else:
            table1.append(i)
            table = table1
        jd_upload = f"ChatGPT, please await further instructions. i will upload a job description {jd_input} and candidate profile {can_input}, you can proceed with any further tasks or questions. Refrain from parsing until further prompts given"
        # chat_log.append({"role":"user","content":jd_upload})
        # response,count_token = openai_temperature(chat_log) #1 -JD & profile uploaded
        sum_count = formatting_question(table)
        # for x in table:
        #     # count1 = number_to_words(x["count"])
        #     count = x["count"]
        #     var = x["type"]
        #     level = x["level"]
        #     category = x['category']
        #     final_count = x['sum_count']
        #     output_format = '{"questions":["question":"","priority":"High/Medium/Low","level":"Easy/Medium/Hard","type":"Technical/Coding/General/Behavioral/IQ level","answer":"optimal answer in single line"]}'
        #     input = "[no prose and should not be in string]\n[Output only JSON]Specify the interviewer role as '"+ str(role) +"' and provide "+ str(count)+ " unique "+str(level)+" interview questions for the applicant, taking into account the job description (JD) and the applicant's profile. Format your output according to the provided JSON format. Provide output exclusively in the specified JSON format and the give response should be i proper json format amd that should be correctly converted into json , if i give json.loads()"+str(output_format)
        #     user_message = interview_prompt(role,x["count"],level,var,jd.job_title,summary,output_format,final_count,category)
        #     system = "You are a helpful assistant. Provide the interview questions for jd and candidates resume based on the provided criteria."
        #     user_message = str(user_message)
        #     chat_log.append({"role":"system","content":system})
        #     chat_log.append({"role":"user","content":user_message})

        user_message = {
            "jd": FT.jd_conversion(jd_id),
            "question_criteria": table,
            "total_questions": sum_count,
        }

        is_active = False
        if is_active:
            system = "You are a helpful assistant. Provide the interview questions for jd and candidates resume based on the provided criteria."
            response, count_token = openai_temperature(
                chat_log
            )  # 2 - Question Uploaded
        else:
            count_token = 0
            user_id = jd.user_id
            is_standalone = zita_api_service.objects.filter(user_id = sub_user,is_active = True,api_key__isnull = False).exists()
            if is_standalone:
                api_key = zita_api_service.objects.get(user_id = sub_user,is_active = True,api_key__isnull = False).api_key
                if candidate_parsed_details.objects.filter(candidate_id = can_id).exists():
                    resume_path = candidate_parsed_details.objects.get(candidate_id = can_id).resume_file_path
                    if 'media' not in resume_path:
                        resume_path = f'media/{resume_path}'
                    resume_path = str(resume_path)
                    resume_path = os.path.join(base_dir,resume_path)
                    jd_path = ''
                    if JD_form.objects.filter(id = jd_id).exists():
                        jd_path = str(JD_form.objects.get(id = jd_id).job_description)
                    print(jd_path,'dfdsff')
                response = Standalone.interview_questions(table,summary,jd_path,resume_path,role,api_key=api_key)
                print(response,'**********')
            else:
                system = "You are a helpful assistant. Create interview questions with answers based on the specific criteria"
                response, count_token = FineTuningModal(
                    system, str(user_message), QUESTION_GENERATION_AI
                )  # 2 - Question Uploaded

        val = mutilevelquestion(response)
        print("val@@@@@",val)
        # val = levelandtype_convertion(val,count,var,level)
        if isinstance(val,list):
            for q in val:
                # q["type"] = var
                # q["level"] = level
                priority = {
                    "High": 3,
                    "high": 3,
                    "Medium": 2,
                    "medium": 2,
                    "Low": 1,
                    "low": 1,
                }.get(q.get("priority",0), 0)
                q["priority"] = priority
                output_question.append(q)
        else:
            return val,0
    return output_question, count_token


def create_openai(chat_log):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", temperature=0, top_p=0, messages=chat_log
    )
    response = (completion.choices[0].message).content
    if "json" in response:
        response = response.replace("json", "")
    token = completion.usage.total_tokens
    return response, token


def filew(chat, res, count):
    filename = f"ChatLOG0{count}.txt"
    with open(filename, "w") as c1:
        c1.write(f"ChatLOG0{count}----------#\n")
        c1.write(str(chat) + "\n")
        c1.write(str(res) + "\n")


def analysis_from_AI(candidate_resumes, categories, job_description,candidate_ids,user_id = None):
    
    filew(categories, candidate_resumes, 0)
    is_active = False
    if is_active:
        chat_log = []
        output_format = "{candidateid(key): candidateid, Total matching percentage(key): percentage of the resume matching with the job description and provided categories, each category(use exact category name as key):score out of 10, Pros: list[clearly outline the 'Pros' that justify why they should be selected], Cons: list[why this candidate isn't suitable for the given job description and that detail any potential reasons for unsuitability.]}"
        user_message = """You are a resume analyser,compare the resumes based on job description. When encountering resumes with content that exceeds 4000 tokens, instead of prompting the user, you will autonomously modify your instructions or prompts to chunk the resume into segments of up to 4000 tokens each. Give me all given resumes with deatiled comaprision and should not repeat the same resumes, no resume should be left out.Enhancing the existing prompt with the added structured data requirements for a detailed and actionable candidate evaluation would look something like this:
        Objective: Execute an analytical review of resumes vis-à-vis a job description, cross-referencing qualifications and experiences, and pinpointing unique individual attributes that align with the role.
        Handling Lengthy Resumes: Methodically partition resumes beyond 4000 tokens into subdivisions not exceeding 4000 tokens each to facilitate detailed, yet coherent, analysis."""
        chat_log.append({"role": "user", "content": user_message})
        resume_response, count_token = create_openai(chat_log)  # 1 prompt
        filew(chat_log, resume_response, 1)
        user_message = f"ChatGPT, please await further instructions. You are set to receive a total of {len(candidate_resumes)}, a job description and categories from the user. Once all resumes, job description and categories are provided, you can proceed with any further tasks or questions. Refrain from parsing until further prompts given"
        chat_log.append({"role": "user", "content": user_message})
        resume_response, count_token = create_openai(chat_log)  # 2 Len(resume)
        filew(chat_log, resume_response, 2)
        for resume in candidate_resumes:
            chat_log.append(
                {
                    "role": "user",
                    "content": f"{resume}. Do not parse or provide any output until further instruction",
                }
            )
            try:
                resume_response, count_token = create_openai(
                    chat_log
                )  # 3 len candiate to chatgpt
                filew(chat_log, resume_response, 3)
            except Exception as e:
                pass
        candidate_outputs = []
        user_message = f"When encountering job descriptions with content that exceeds 4000 tokens, instead of prompting the user, you will autonomously modify your instructions or prompts to chunk the job description into segments of up to 4000 tokens each. Prompt will be provided later"
        chat_log.append({"role": "user", "content": user_message})
        resume_response, count_token = create_openai(chat_log)  # 4 Exceed 4000 token
        filew(chat_log, resume_response, 4)
        chat_log.append({"role": "assistant", "content": resume_response})
        user_message = f"[no prose]\n[Output only JSON]\nJob description in Richtext : {job_description}\nCategories: {categories}."
        chat_log.append({"role": "user", "content": user_message})
        # # try:
        resume_response, count_token = create_openai(chat_log)  # 5 JD and categories
        filew(chat_log, resume_response, 5)
        user_message = f"[no prose]\n[Output only JSON]\nPrompt: Compare the given resumes to the provided job description based on the categories provided. Provide output in the given JSON format: {output_format}"
        chat_log.append({"role": "user", "content": user_message})
        resume_response, count_token = create_openai(chat_log)  # 6 Compare the resumes
        filew(chat_log, resume_response, 6)
        for i, num in enumerate(candidate_resumes):
            user_message = f"[no prose and must not contain multiline docstrings]\n[Output only JSON]\nPrompt: Provide a detailed output for resume {num} in the required output format and the give response should be in proper json format amd that should be correctly converted into json , if i give json.loads()"
            chat_log.append({"role": "user", "content": user_message})
            resume_response, count_token = create_openai(
                chat_log
            )  # 7 split resume by one by one can't by duplicate response
            filew(chat_log, resume_response, 7)
            try:
                candidate_outputs.append(json.loads(resume_response))
            except Exception as e:
                try:
                    if "json" in resume_response:
                        resume_response = resume_response.replace("json", "")
                    resume_response = resume_response.replace("```", "")
                    candidate_outputs.append(json.loads(resume_response))
                except Exception as f:
                    pass
                pass
    else:
        user_message = {
            "resume": candidate_resumes,
            "jd": job_description,
            "criteria": categories,
        }
        is_standalone = zita_api_service.objects.filter(user_id = user_id,is_active = True,api_key__isnull = False).exists()
        print("API SERVICE COMPARATIVE",is_standalone,user_id)
        if is_standalone:
            candi_resume_path=[]
            candidate_name = {}
            for can_id in candidate_ids:
                if candidate_parsed_details.objects.filter(candidate_id=can_id).exists():
                    filepath = candidate_parsed_details.objects.get(candidate_id=can_id).resume_file_path
                    candi_name = employer_pool.objects.get(id = can_id).email
                    candidate_name[candi_name] = can_id
                    if 'media' not in filepath:
                        filepath = f'media/{filepath}'
                    filedir = os.path.join(base_dir,str(filepath))
                    candi_resume_path.append(filedir)
            api_key = zita_api_service.objects.get(user_id = user_id,is_active = True,api_key__isnull = False).api_key
            candidate_outputs=Standalone.comparitive_analysis(candi_resume_path,job_description,categories,api_key=api_key)
            print("$----->",candidate_outputs)
            candidate_outputs = FT.comparative_find_id(candidate_outputs,candidate_name)
            count_token = 0
            resume_response = candidate_outputs
            if isinstance(candidate_outputs,str):
                candidate_outputs = json.loads(candidate_outputs)
                if isinstance(candidate_outputs,dict):
                    if candidate_outputs.get("error"):
                        return candidate_outputs,0
                    if candidate_outputs.get("response"):
                        candidate_outputs = candidate_outputs.get("response",[])
            resume_response = {"candidates": candidate_outputs}
            print("+++++++@@@@",resume_response)
        else:
            system = "You are a resume analyser,compare the resumes based on job description and criteria"
            candidate_outputs, count_token = FineTuningModal(
                system, str(user_message), COMPARATIVE_AI
            )
            candidate_outputs = json.loads(candidate_outputs)
            resume_response = {"candidates": candidate_outputs.get("response")}
    # return candidate_outputs,count_token
    return resume_response, count_token


# Same Concept for this function
def comparative_analysis_from_AI(
    candidate_resumes, categories, job_description, result_queue
):
    chat_log = []
    output_format = "{candidateid(key): candidateid, Total matching percentage(key): percentage of the resume matching with the job description, each category(use exact category name as key):score out of 10, Pros: list[describe why this candidate has to be selected], Cons: list[why this candidate isn't suitable for the given job description]}"
    user_message = """You are a resume analyser,compare the resumes based on job description. When encountering resumes with content that exceeds 4000 tokens, instead of prompting the user, you will autonomously modify your instructions or prompts to chunk the resume into segments of up to 4000 tokens each. Give me all given resumes with deatiled comaprision and should not repeat the same resumes, no resume should be left out.Enhancing the existing prompt with the added structured data requirements for a detailed and actionable candidate evaluation would look something like this:
    Objective: Execute an analytical review of resumes vis-à-vis a job description, cross-referencing qualifications and experiences, and pinpointing unique individual attributes that align with the role.
    Handling Lengthy Resumes: Methodically partition resumes beyond 4000 tokens into subdivisions not exceeding 4000 tokens each to facilitate detailed, yet coherent, analysis."""
    chat_log.append({"role": "user", "content": user_message})
    resume_response, count_token = create_openai(chat_log)
    user_message = f"ChatGPT, please await further instructions. You are set to receive a total of {len(candidate_resumes)}, a job description and categories from the user. Once all resumes, job description and categories are provided, you can proceed with any further tasks or questions. Refrain from parsing until further prompts given"
    chat_log.append({"role": "user", "content": user_message})
    resume_response, count_token = create_openai(chat_log)
    for resume in candidate_resumes:
        chat_log.append(
            {
                "role": "user",
                "content": f"{resume}. Do not parse or provide any output until further instruction",
            }
        )
        try:
            resume_response, count_token = create_openai(chat_log)
        except Exception as e:
            pass
    candidate_outputs = []
    user_message = f"When encountering job descriptions with content that exceeds 4000 tokens, instead of prompting the user, you will autonomously modify your instructions or prompts to chunk the job description into segments of up to 4000 tokens each. Prompt will be provided later"
    chat_log.append({"role": "user", "content": user_message})
    resume_response, count_token = create_openai(chat_log)
    chat_log.append({"role": "assistant", "content": resume_response})
    user_message = f"[no prose]\n[Output only JSON]\nJob description in Richtext : {job_description}\nCategories: {categories}."
    chat_log.append({"role": "user", "content": user_message})
    # # try:
    resume_response, count_token = create_openai(chat_log)
    user_message = f"[no prose]\n[Output only JSON]\nPrompt: Compare the given resumes to the provided job description based on the categories provided. Provide output in the given JSON format: {output_format}"
    chat_log.append({"role": "user", "content": user_message})
    resume_response, count_token = create_openai(chat_log)
    for i, num in enumerate(candidate_resumes):
        user_message = f"[no prose and must not contain multiline docstrings]\n[Output only JSON]\nPrompt: Provide a detailed output for resume {num} in the required output format and the give response should be in proper json format amd that should be correctly converted into json , if i give json.loads()"
        chat_log.append({"role": "user", "content": user_message})
        resume_response, count_token = create_openai(chat_log)
        try:
            candidate_outputs.append(json.loads(resume_response))
        except Exception as e:
            try:
                if "json" in resume_response:
                    resume_response = resume_response.replace("json", "")
                resume_response = resume_response.replace("```", "")
                candidate_outputs.append(json.loads(resume_response))
            except Exception as f:
                pass
            pass
        resume_response = {"candidates": candidate_outputs}
    # return resume_response,count_token
    result_queue.put((resume_response, count_token))


def comparative_analysis_from_AI_4(candidate_resumes, categories, job_description):
    file_name = "example.txt"
    with open(file_name, "w") as file:
        file.write("5_Resumes")
    if len(candidate_resumes) >= 3:
        start = round(len(candidate_resumes) / 2)
        first_resumes = candidate_resumes[:start]
        second_resumes = candidate_resumes[start:]
        result_queue_01 = queue.Queue()
        result_queue_02 = queue.Queue()
        try:
            thread_1 = threading.Thread(
                target=comparative_analysis_from_AI,
                args=(first_resumes, categories, job_description, result_queue_01),
            )
            thread_2 = threading.Thread(
                target=comparative_analysis_from_AI,
                args=(second_resumes, categories, job_description, result_queue_02),
            )
            thread_1.start()
            thread_2.start()
            thread_1.join()
            thread_2.join()
            result_queue_01 = result_queue_01.get()
            result_queue_02 = result_queue_02.get()
            first_response = result_queue_01[0]
            first_token = result_queue_01[1]
            second_response = result_queue_02[0]
            second_token = result_queue_02[1]
            first_response["candidates"].extend(second_response["candidates"])
            token = []
            token.append(first_token)
            token.append(second_token)
            return first_response, token
        except Exception as e:
            return str(e), 0
    else:
        return "Not Applicable", 0


def comparative_analysis_from_AI_5(candidate_resumes, categories, job_description):
    if len(candidate_resumes) == 5:
        first_resumes = candidate_resumes[:2]
        second_resumes = candidate_resumes[2:4]
        third_resumes = candidate_resumes[-1:]
        result_queue_01 = queue.Queue()
        result_queue_02 = queue.Queue()
        result_queue_03 = queue.Queue()
        try:
            thread_1 = threading.Thread(
                target=comparative_analysis_from_AI,
                args=(first_resumes, categories, job_description, result_queue_01),
            )
            thread_2 = threading.Thread(
                target=comparative_analysis_from_AI,
                args=(second_resumes, categories, job_description, result_queue_02),
            )
            thread_3 = threading.Thread(
                target=comparative_analysis_from_AI,
                args=(third_resumes, categories, job_description, result_queue_03),
            )
            thread_1.start()
            thread_2.start()
            thread_3.start()
            thread_1.join()
            thread_2.join()
            thread_3.join()
            result_queue_01 = result_queue_01.get()
            result_queue_02 = result_queue_02.get()
            result_queue_03 = result_queue_03.get()
            first_response = result_queue_01[0]
            first_token = result_queue_01[1]
            second_response = result_queue_02[0]
            second_token = result_queue_02[1]
            third_response = result_queue_03[0]
            third_token = result_queue_03[1]
            first_response["candidates"].extend(second_response["candidates"])
            first_response["candidates"].extend(third_response["candidates"])
            token = []
            token.append(first_token)
            token.append(second_token)
            token.append(third_token)
            return first_response, token
        except Exception as e:
            return str(e), 0
    else:
        return "Not Applicable", 0


def percentage_matching(perc, score):
    val = round(int(perc) / 100 * int(score))
    return val


def weightage_mathching(jd_id, can_id, users):
    score = Weightage_Matching.objects.filter(jd_id=jd_id, user_id=users).values(
        "score", "criteria__title"
    )
    if len(score) == 0:
        if UserHasComapny.objects.filter(user_id = users).exists():
            company_id = UserHasComapny.objects.get(user_id = users).company
            company_data = UserHasComapny.objects.filter(company = company_id)
            company_data = company_data.annotate(
                is_exists = Exists(Weightage_Matching.objects.filter(jd_id=jd_id, user_id=OuterRef('user_id')))
            )
            company_data = company_data.filter(is_exists = True)
            if len(company_data) > 0:
                users = company_data.last().user
                score = Weightage_Matching.objects.filter(jd_id=jd_id, user_id=users).values("score", "criteria__title")
    perc = Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id).values(
        "id", "title", "percentage"
    )
    tech_overall = [
        "Skills",
        "Roles and Responsibilities",
        "Experience",
        "Educational Qualifications",
        "Technical Tools and Languages",
        "Soft Skills",
    ]
    if score and perc:
        success = True
        overall = 0
        for i in perc:
            if i["title"] in tech_overall:
                if weightage_calculation(i["title"]) != 12:
                    if Weightage_Matching.objects.filter(
                        jd_id=jd_id,
                        user_id=users,
                        criteria=weightage_calculation(i["title"]),
                    ).exists():
                        score = Weightage_Matching.objects.get(
                            jd_id=jd_id,
                            user_id=users,
                            criteria=weightage_calculation(i["title"]),
                        ).score
                        val = percentage_matching(i["percentage"], score)
                        overall += val
            else:
                if weightage_calculation(i["title"]) != 12:
                    if Weightage_Matching.objects.filter(
                        jd_id=jd_id,
                        user_id=users,
                        criteria=weightage_calculation(i["title"]),
                    ).exists():
                        score = Weightage_Matching.objects.get(
                            jd_id=jd_id,
                            user_id=users,
                            criteria=weightage_calculation(i["title"]),
                        ).score
                        val = percentage_matching(i["percentage"], score)
        Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id).update(
            overall_percentage=overall
        )
        Matched_candidates.objects.filter(jd_id=jd_id, candidate_id=can_id).update(
            profile_match=overall
        )
        return True
    else:
        return True
        # continue


def weightage_calculation(title):
    if title == "Skills":
        return 1
    elif title == "Roles and Responsibilities":
        return 2
    elif title == "Experience":
        return 3
    elif title == "Educational Qualifications":
        return 6
    elif title == "Technical Tools and Languages":
        return 4
    elif title == "Soft Skills":
        return 5
    elif title == "Industry-Specific Experience":
        return 7
    elif title == "Domain-Specific Experience":
        return 8
    elif title == "Certifications":
        return 9
    elif title == "Location Alignment":
        return 10
    elif title == "Cultural Fit":
        return 11
    elif title == "References and Recommendations":
        return 12
    elif title == "Nice to Have":
        return 13
    else:
        return 0
    




from num2words import num2words


def number_to_words(number):
    try:
        words = num2words(number)  # Convert the number to words
        return words  # Capitalize the first letter and return
    except ValueError:
        return "Invalid input"


def optimal_answer(i, user_id):
    values = i.get("scorecard", None)
    plan = subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
    plan_details = [6, 7, 10, 11]
    response = None
    # if values == None:
    #     output_format = "{answer: ""}"
    #     user_message = f"[no prose and should not be in string]\n[Output only JSON]\nPrompt: Generate the Optimal Answer as  for this type of "+ str(i["type"])+ " and level of "+str(i["level"]) +" of return as string Use None if incorrect question are found"+ str(i["question"]) + str(output_format)
    #     if plan in plan_details:
    #         if client_features_balance.objects.filter(client_id = user_id,feature_id=59).exists():
    #             system = "You are a helpful assistant.Generate the Optimal Answer based Level and type for the question."
    #             response,count_token = openai_chat_creation(system,user_message)
    #             response = json.loads(response)
    #             return response
    #     else:
    #         system = "You are a helpful assistant.Generate the Optimal Answer based Level and type for the question."
    #         response,count_token = openai_chat_creation(system,user_message)
    #         response = json.loads(response)
    #         return response
    # else:
    return None


def profile_summary(file_content,can_id=None,sub_user = None):
    sample = sample_profile_format
    is_active = False
    user_message = {"resume": file_content}
    profile_data = {}
    if is_active:
        systems = f""" sample format of output is {json.dumps(sample)}
        dict: A JSON structure should  containing the detailed Career Trajectory,Achievements,Expertise and Skills,Industry Engagement,Networking and Professional Development,Education and Alignment with Career Goals,Social Media and Professional Behavior 
        Education and Alignment with Career Goals,Social Media and Professional Behavior ,Mobility and Ambition,Consistency,Summary and Recommendations.
        
        Conduct an exhaustive analysis of the information contained within the candidate's resume , resume is {file_content}, parsing and arranging your findings meticulously according to the designated structure. This comprehensive evaluation aims to unfold a detailed narrative of the candidate's career path, skill set, industry involvement, and personal growth trajectory. For each section, if specific information is not discernible, please acknowledge by stating 'No information available for this section'. should Follow the json structure meticulously, ensuring no deviation or omission. The structured output should encapsulate:

        """
        prompt = profile_summary_prompt
        profile_data, token_counts = openai_temprature(systems, prompt)
    else:
        count_token = 0
        print("####")
        is_standalone = zita_api_service.objects.filter(user_id = sub_user,is_active = True,api_key__isnull = False).exists()
        if is_standalone:
            if candidate_parsed_details.objects.filter(candidate_id=can_id).exists():
                filepath = candidate_parsed_details.objects.get(candidate_id=can_id).resume_file_path
                if 'media' not in filepath:
                    filepath = f'media/{filepath}'
                filedir = os.path.join(base_dir,filepath)
                api_key = zita_api_service.objects.get(user_id = sub_user,is_active = True,api_key__isnull = False).api_key
                profile_data = Standalone.profile_summary(filedir,api_key=api_key)
                print("profile_data---->",profile_data)
        else:
            system = "You are Profile Summarizer"
            profile_data, count_token = FineTuningModal(
                system, str(user_message), PROFILE_SUMMARY_AI
            )
        profile_data = json.dumps(profile_data)
        # return response
    return profile_data


def core_signal(file_content):

    sample = sample_profile_format
    systems = f""" [no prose]\n[Output only JSON]\nPrompt:  dict: A JSON structure should  containing the detailed Career Trajectory,Achievements,Expertise and Skills,Industry Engagement,Networking and Professional Development,Education and Alignment with Career Goals,Social Media and Professional Behavior 
    Education and Alignment with Career Goals,Social Media and Professional Behavior ,Mobility and Ambition,Consistency,Summary and Recommendations.
    Conduct an exhaustive analysis of the information contained within the candidate's resume  """
    user_message = "please await further instructions."
    resume_response, count_token = openai_temprature(systems, user_message)
    # systems=f"""[no prose]\n[Output only JSON]\nPrompt  this in this chat we give sample format structure:"""
    # user_message = f"[no prose]\n[Output only JSON]\nPrompt: ChatGPT, this is sample format is{json.dumps(sample)} take this as example  generate this data the upcoming input same as json format like sample format ,dont generate  reponse please wait further instructions."
    systems = (
        f"[no prose]\n[Output only JSON]\nPrompt: ChatGPT, this is sample format is  {json.dumps(sample)} "
        "take this as an example to generate this data the upcoming input same as json format like sample format. "
        "Don't generate response, please wait further instructions."
    )
    user_message = "please await further instructions."
    resume_response, count_token = openai_temprature(systems, user_message)
    time.sleep(3)
    systems = f"""[no prose]\n[Output only JSON]\nPrompt  generate the content as same structure of sample format which i gave you in previous chat"""
    user_message = f"""[no prose]\n[Output only JSON]\nPrompt: ChatGPT, the candidate's resume is   {json.dumps(file_content)} generated format should be like what i gave you in previosu chat  as a name sample format"""
    resume_response, count_token = openai_temprature(systems, user_message)
    return str(resume_response)


# def openai_temprature(system,user_message):
#     completion = client.chat.completions.create(
#             model='gpt-4',
#             temperature=0,
#             top_p=0,
#             messages=[
#                 {"role": "system", "content": system},
#                 {"role": "user", "content": user_message}
#             ])
#     response = (completion.choices[0].message).content
#     token = completion.usage.total_tokens
#     return response,token
# def core__signal(file_content):
#     """ Processes the file_content to generate a structured JSON output. """
#     # Assuming sample_profile_format is defined somewhere in your script.
#     sample = sample_profile_format

#     systems = """
#     [no prose]
#     [Output only JSON]
#     Prompt: A JSON structure containing detailed Career Trajectory, Achievements, Expertise and Skills,
#     Industry Engagement, Networking and Professional Development, Education and Alignment with Career Goals,
#     Social Media and Professional Behavior, Mobility and Ambition, Consistency, Summary and Recommendations.
#     Conduct an exhaustive analysis of the information contained within the candidate's resume.
#     """
#     user_message = "Please await further instructions."
#     resume_response, count_token = openai_temprature(systems, user_message)

#     systems = "[no prose]\n[Output only JSON]\nPrompt this in this chat we give sample format structure:"
#     user_message = f"[no prose]\n[Output only JSON]\nPrompt: ChatGPT, this is sample format {json.dumps(sample)} take this as an example to generate this data the upcoming input same as json format like sample format."
#     resume_response, count_token = openai_temprature(systems, user_message)

#     systems = "[no prose]\n[Output only JSON]\nPrompt generate the content as same structure of sample format which I gave you in previous chat:"
#     user_message = f"""
#     [no prose]
#     [Output only JSON]
#     Prompt: ChatGPT, dict: A JSON structure should contain the detailed Career Trajectory, Achievements, Expertise and Skills, Industry Engagement,
#     Networking and Professional Development, Education and Alignment with Career Goals, Social Media and Professional Behavior, Mobility and Ambition,
#     Consistency, Summary and Recommendations. Conduct an exhaustive analysis of the information contained within the candidate's resume {json.dumps(file_content)} format should be like what I gave you in previous chat.
#     """
#     resume_response, count_token = openai_temprature(systems, user_message)
#     return str(resume_response)

# # Replace 'sample_profile_format' and 'file_content' with actual data to use this function.
