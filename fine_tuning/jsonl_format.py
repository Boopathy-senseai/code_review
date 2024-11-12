import json


def systematic(system):
    if system == "resume_parser":
        return "You are a helpful assistant, Parse the resume in JSON format"
    if system == "chatbot":
        return "You are a helpful assistant, generate the response in JSON format"
    if system == "comparative":
        return "You are a resume analyser,compare the resumes based on job description and criteria"
    if system == "matching":
        return "You are a Resume Matchmaker. provide the correct matching score for resume and job description"


# Function to convert data to JSONL format
def convert_to_jsonl(list2, list3, name):
    jsonl_data = []
    for item2, item3 in zip(list2, list3):
        message = {"messages": []}
        array = []
        if systematic(name):
            system = systematic(name)
            array.append({"role": "system", "content": system})
            if item2:
                item2 = item2["content"]
                if name == "chatbot":
                    item2 = str(item2["content"])
                if name == "comparative":
                    item2 = str(item2)
                if name == "matching":
                    item2 = str(item2)
                array.append({"role": "user", "content": item2})
            if item3:
                doc_string = f"""{json.dumps(item3, indent=4)}"""
                array.append({"role": "assistant", "content": doc_string})
            message = {"messages": array}
            jsonl_data.append(message)
        else:
            return None
    return jsonl_data


# Function to write data to JSONL file
def write_jsonl(filename, data):
    with open(filename, "w") as f:
        for item in data:
            json.dump(item, f)
            f.write("\n")


readfile = "fine_tuning/matching_ft/match04.json"
with open(readfile, "r") as f:
    json_data = json.load(f)
list2 = json_data["raw_text"]
list3 = json_data["parsed_text"]

purpose = "matching"
# jsonl_data = convert_to_jsonl(list2,list3,purpose)  #JSONL converter
# if jsonl_data:
#     writefile = 'fine_tuning/matching_ft/match03.jsonl'
#     write_jsonl(writefile, jsonl_data)
