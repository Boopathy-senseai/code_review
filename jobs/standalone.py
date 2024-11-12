import requests
import json
# from zita.settings import standalone_url,standalone_apikey
standalone_url = 'https://uotxnvwte6.execute-api.us-east-1.amazonaws.com/prod'
# standalone_apikey = 'GORBCX0Mt2aGDalNldL8b2RnDZoTyq12VgILu6hj'

standalone_apikey = 'pgAQAAqprM5Uv8faSkPIq5Quvpx3D6Mg90d5yIIN'

## API NAME USED IN STANDALONE
STANDALONE_MATCHING = 'matching'
STANDALONE_PROFILE  = 'profile_summary'
STANDALONE_RESUME  = 'resume_parser'
STANDALONE_JD  = 'jd_parser'
STANDALONE_COMPARATIVE  = 'comparitive_analysis'
STANDALONE_JDASSISTANCE  = 'jd_generation'
STANDALONE_INTERVIEW  = 'interview_questions'
STANDALONE_USERDETAILS  = 'user_details'




def Standalone_Function(path,files=None,payload=None,api_key = None):
    print("api_key@",api_key,path)
    url = f'{standalone_url}/{path}'
    if path == 'jd_generation':
        headers = {'x-api-key':api_key if api_key else standalone_apikey,'Content-Type': 'application/json'}
    else:
        headers = {'x-api-key':str(api_key) if api_key else standalone_apikey}
    if payload and files:
        response = requests.post(url, headers=headers, files=files, data=payload)
    elif files and payload is None:
        response = requests.post(url, headers=headers, files=files)
    elif payload and files is None:
        response = requests.post(url, headers=headers, data=payload)
    else:
        response = requests.post(url, headers=headers)
    try:
        print("$$$$$$$$$$$",response)
        if  isinstance(response,dict):
            response_json = response
        else:
            response_json = response.json()
        print("Standalone Response--->",response_json,"\n")
        if isinstance(response_json, dict):
            response_json = response_json.get('data', {})
            if response_json.get('response'):
                response_json = response_json.get('response', {})
            response_json = f"""{json.dumps(response_json, indent=4)}"""
    except ValueError:
        response_json = {}
        print("Response is not valid JSON.")
    except Exception as e:
        response_json = {}
        print("Standalone Exceptions--->",e)
    return response_json


class Standalone:
    def __init__(self):
        self.openai_key = []
        self.client = []

    def profile_summary(filedir,api_key = None):
        print("Trigger Profile  Summary")
        path = STANDALONE_PROFILE
        files = {'resume': open(filedir,'rb')}
        response = Standalone_Function(path,files=files,api_key=api_key)
        return response
    
    def jd_parser(filepath,api_key = None):
        print("Trigger JD Parser")
        path= STANDALONE_JD
        files={'jd':open(filepath,'rb')}
        response = Standalone_Function(path,files=files,api_key=api_key)
        return response
    
    def comparitive_analysis(candi_resume_path,job,categories,api_key = None):
        print("Trigger Comparative Analysis")
        payload = {}
        categories = categories.split(",")
        payload["jd"] = job
        for key in categories:
            if key in ['Industry Specific Experience']:
                key = "Industry-Specific Experience"
            payload[key] = True
        path=STANDALONE_COMPARATIVE
        files = {}
        # Iterate over the list and open the files dynamically
        for index, file_path in enumerate(candi_resume_path, start=1):
            files[f'resume{index}'] = open(file_path, 'rb')
        print("$$$$#",payload,"FILES",files)
        response = Standalone_Function(path,payload=payload,files=files,api_key=api_key)
        print("@@@@@@@@@@@@@@$$",response,type(response))
        return response
    
    def resume_parser(filepath,api_key = None):
        print("Trigger Resume")
        path= STANDALONE_RESUME
        files={'resume':open(filepath,'rb')}
        response = Standalone_Function(path,files=files,api_key=api_key)
        return response
    
    def jd_generation(jobTitle,Industry_and_Domain,min_experience,overview,mandatory_skills,api_key = None):
        print("Trigger JD Generation")
        path = STANDALONE_JDASSISTANCE
        payload = {'job_title':jobTitle,'industry_type':Industry_and_Domain,'min_experience':min_experience,
               'overview':overview,
               'skills':mandatory_skills}
        response=Standalone_Function(path, payload=payload,api_key=api_key)
        return response
    
    def matching(candidate,jd,profile,enhanced,api_key = None):
        print("Trigger Matching")
        path=STANDALONE_MATCHING
        payload={"jd": jd ,"profile_matching":json.dumps(profile),"enhanced_matching":json.dumps(enhanced)}
        files={'resume':open(candidate,'rb')}
        print("profile---->",profile,"enhanced--->",enhanced)
        response = Standalone_Function(path,payload=payload,files=files,api_key=api_key)
        response = json.loads(response)
        enhanced_list = response.get('enhanced_compatibility',[])
        profile_list = list(response.get('profile_compatibility',[]))
        final_list = profile_list + enhanced_list 
        return final_list
    
    def interview_questions(criteria,summary,jd,resumepath,role,api_key = None):
        print("Trigger Interview Questions")
        path = STANDALONE_INTERVIEW
        criteria = f"""{json.dumps(criteria, indent=4)}"""
        payload = {"criteria":criteria,"summary":summary,"jd":jd,"role":role}
        files = {'resume':open(resumepath,'rb')}
        response = Standalone_Function(path,payload=payload,files=files,api_key=api_key)
        if isinstance(response,str):
            response = json.loads(response)
        return response
    

    def api_service_userdetails(api_key = None):
        path = STANDALONE_USERDETAILS
        response = Standalone_Function(path,api_key=api_key)
        return response




