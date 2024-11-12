from zita.settings import openai_key, client
import json
from .models import *
from .standalone import * 


RESUME_PARSER = "ft:gpt-3.5-turbo-1106:sense7ai-inc:resume-parser:9lsJM0QZ"
CHATBOT_AI = "ft:gpt-3.5-turbo-1106:sense7ai-inc::9PoTbqwA"
COMPARATIVE_AI = "ft:gpt-4o-mini-2024-07-18:sense7ai-inc:ca:AH4SIbAv"
JD_PARSER = "ft:gpt-3.5-turbo-1106:sense7ai-inc:jdparser04:9WJU7aXN"
MATCHING_AI = "ft:gpt-3.5-turbo-1106:sense7ai-inc::9X6qLMMG"
QUESTION_GENERATION_AI = (
    "ft:gpt-3.5-turbo-1106:sense7ai-inc:interview-question:9mboFK3x"
)
JD_CREATION_AI = "asst_Ir3N5zu7DjUBQzKSBo8lbYlW"
PROFILE_SUMMARY_AI = "ft:gpt-4o-mini-2024-07-18:sense7ai-inc:profile-summary:9xqgwIcw"


def FineTuningModal(system, user_message, modal):
    """
    1) This is Main FineTuning Function Does Not Modify Inside this Function Do Change a Before Function
    """
    try:
        completion = client.chat.completions.create(
            model=modal,
            temperature=0,
            top_p=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
        )
        response = (completion.choices[0].message).content
        token = completion.usage.total_tokens
        # response = json.dumps(response)
    except:
        response = None
        token = 0
    return response, token


class FT:
    """
    1) The class Will Be Used For All Finetuning Related Function You can Add Inside this
    """

    def __init__(self):
        self.openai_key = openai_key
        self.client = client

    def text_to_json_string(txt):
        formatted_data = {"content": txt}
        json_string = json.dumps(formatted_data.get("content"), indent=2)
        return json_string

    def generate_system_message(system):
        if system == "resume_parser":
            return "You are a helpful assistant, Parse the resume in JSON format"
        if system == "chatbot":
            return "You are a helpful assistant, generate the response in JSON format"
        if system == "comparative":
            return "You are a resume analyser, compare the resumes based on job description and criteria"
        return system

    def write_to_jsonl(filename, data):
        with open(filename, "w") as f:
            for item in data:
                json.dump(item, f)
                f.write("\n")

    def jd_conversion(jd_id):
        jd_id = JD_form.objects.get(id=jd_id)

        Country_Name = (
            JD_locations.objects.filter(jd_id_id=jd_id)
            .exclude(country_id__name=None)
            .values_list("country_id__name", flat=True)
        )
        country = "".join(Country_Name)
        State_Name = (
            JD_locations.objects.filter(jd_id_id=jd_id)
            .exclude(state_id__name=None)
            .values_list("state_id__name", flat=True)
        )
        state = "".join(State_Name)
        City_Name = (
            JD_locations.objects.filter(jd_id_id=jd_id)
            .exclude(city_id__name=None)
            .values_list("city_id__name", flat=True)
        )
        city = "".join(City_Name)

        location_details = country + ", " + state + ", " + city

        Qualifications = (
            JD_qualification.objects.filter(jd_id_id=jd_id)
            .exclude(qualification=None)
            .values_list("qualification", flat=True)
        )
        Specializations = (
            JD_qualification.objects.filter(jd_id_id=jd_id)
            .exclude(specialization=None)
            .values_list("specialization", flat=True)
        )
        qualification = "".join(Qualifications)
        specialization = "".join(Specializations)

        Job_Description = jd_id.job_description
        Job_Type = jd_id.job_type.label_name

        NiceToHaveSkills = (
            jd_nice_to_have.objects.filter(jd_id_id=jd_id)
            .exclude(nice_to_have=None)
            .values_list("nice_to_have", flat=True)
        )
        Nice_to_have_Competencies = ", ".join(NiceToHaveSkills)

        Skills = (
            JD_skills_experience.objects.filter(jd_id_id=jd_id)
            .exclude(skill=None)
            .values_list("skill", flat=True)
        )
        Mandatory_Competencies = ", ".join(Skills)

        work_space_type = jd_id.work_space_type
        if work_space_type == "1":
            Work_Space = "Onsite"
            location = f"{Work_Space} - {location_details}"
        elif work_space_type == "2":
            Work_Space = "Hybrid"
            location = f"{Work_Space} - {location_details}"
        elif work_space_type == "3":
            Work_Space = "Remote"
            location = Work_Space
        else:
            location = ""

        raw_text = f"""

        Job Title : {jd_id.job_title}
        Job Description : {Job_Description}
        Jd Skills : {Mandatory_Competencies}
        Nice to have Competencies : {Nice_to_have_Competencies} 
        Jd Locaiton : {location}
        Jd qualification : {qualification} - {specialization}
        jd experience : {round(jd_id.min_exp)} - {jd_id.max_exp} years

        """
        return raw_text

    def resume_conversion(can_id):
        candidate_id = candidate_parsed_details.objects.get(candidate_id_id=can_id)
        resume_descriptions = candidate_id.resume_description

        raw_text = f"""
        candidate_id : {can_id}\n{resume_descriptions}
        """

        return raw_text
    
    def get_title_from_criteria_id(title):
        if title == 1:
            return "Skills"
        elif title == 2:
            return "Roles and Responsibilities"
        elif title == 3:
            return "Experience"
        elif title == 6:
            return "Educational Qualifications"
        elif title == 4:
            return "Technical Tools and Languages"
        elif title == 5:
            return "Soft Skills"
        elif title == 7:
            return "Industry-Specific Experience"
        elif title == 8:
            return "Domain-Specific Experience"
        elif title == 9:
            return "Certification"
        elif title == 10:
            return "Location Alignment"
        elif title == 11:
            return "Cultural Fit"
        elif title == 12:
            return "References and Recommendation"
        elif title == 13:
            return "Nice to Have"
        else:
            return "Unknown Title"

    def profile_matching(jd_id,user):
        if Weightage_Matching.objects.filter(jd_id = jd_id,user_id = user).exists():
            skills = Weightage_Matching.objects.get(jd_id = jd_id,user_id = user,criteria_id = 1).score
            tech = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 4,user_id = user).score
            roles = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 2,user_id = user).score
            soft_skills = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 5,user_id = user).score
            exp = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 3,user_id = user).score
            education = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 6,user_id = user).score
            profile_matching = [{"Skills":skills},{"Technical Tools and Languages":tech},{"Roles and Responsibilities":roles},{"Soft Skills":soft_skills},{"Experience":exp},{"Educational Qualifications":education}]
            return profile_matching

    def enhanced_matching(jd_id,user):
        if Weightage_Matching.objects.filter(jd_id = jd_id,user_id = user).exists():
            enhanced_matching = []
            industry = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 7,user_id = user).score
            domain = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 8,user_id = user).score
            location = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 10,user_id = user).score
            certification = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 9,user_id = user).score
            cultural_fit = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 11,user_id = user).score
            reference = Weightage_Matching.objects.get(jd_id = jd_id,criteria_id = 6,user_id = user).score
            total_score = industry + domain + location + certification + cultural_fit
            if total_score != 100:
                addlocation = 100 - total_score
                location = location + addlocation
            enhanced_matching = [{"Industry-Specific Experience":industry},{"Domain-Specific Experience":domain},{"Certification":certification},{"Cultural Fit":cultural_fit},{"Location Alignment":location}]
            return enhanced_matching
        
    def weightage_calculate(lst,weightage_list):
        if isinstance(lst,list):
            for i in lst:
                perc = int(i.get("percentage",0))
                title = i.get("title","")
                for y in weightage_list:
                    if y.get(title):
                        i["percentage"] =  (perc / y.get(title,0)) * 100 
            response =  f"""{json.dumps(lst, indent=4)}"""      
            return response
        
    def comparative_find_id(resp,candidates):
        if isinstance(resp,str):
            resp = json.loads(resp)
        if isinstance(resp,list):
            for i in resp:
                if i.get("Industry-Specific Experience"):
                    i["Industry Specific Experience"] = i.pop("Industry-Specific Experience")
                if i.get('References and Recommendation') == None:
                    i["References and Recommendation"] = 0
                if i.get('Email'):
                    email = i.get('Email')
                    i['candidate_id'] = int(candidates.get(email))
                if i.get('email'):
                    email = i.get('email')
                    i['candidate_id'] = int(candidates.get(email))
            response =  f"""{json.dumps(resp, indent=4)}""" 
            return response
        if isinstance(resp,dict):
            return resp


    def standalone_userdetails(user_id):
        data = None
        if zita_api_service.objects.filter(user_id = user_id,is_active = True,api_key__isnull = False).exists():
            data = zita_api_service.objects.filter(user_id = user_id,api_key__isnull = False).last()
            if data: 
                data = data.api_key
                data = Standalone.api_service_userdetails(data)
        return data

    def identify_api_name(apis):
        if apis == 'resume_parser':
            return 27
        # if apis == 'jd_parser':
        #     return 10
        # if apis == 'profile_summary':
        #     return 27
        # if apis == 'jd_generation':
        #     return 6
        if apis == 'matching':
            return 6
        # if apis == 'comparitive_analysis':
        #     return 27
        # if apis == 'interview_questions':
        #     return 27
        return None
    