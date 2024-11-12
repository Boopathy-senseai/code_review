import csv
import os
import re
from bs4 import BeautifulSoup
from bulk_upload.views import BASE_DIR
from calendarapp.models import Questions_Generation
from jobs.models import *
from zita.settings import BASE_DIR
from datetime import datetime
import json
import ast

VALID_CATEGORIES = [
    "Skills",
    "Roles and Responsibilities",
    "Experience",
    "Technical Tools and Languages",
    "Soft Skills",
    "Qualification",
    "Industry Specific Experience",
    "Domain Specific Experience",
    "Certification",
    "Location Alignment",
    "Cultural Fit",
    "References and Recommendation",
]


def is_category_valid(categories):
    for category in categories:
        if category not in VALID_CATEGORIES:
            return False
    return True


def data_conversion(data, categories):
    try:
        update_categories = {}
        print("categories----------#",categories,"\ndata------#",data)
        for category in categories:
            
            try:
                update_categories[category] = data.get(category)
            except:
                update_categories[category] = None
        data["categories"] = update_categories
    except Exception as e:
        pass
    return data


# takes the updated html overview and updates it in the response json
def html_to_response_json(html_overview, response_json):
    pattern = r"<h6[^>]*>(.*?)</h6>"
    matches = re.findall(pattern, html_overview)
    soup = BeautifulSoup(html_overview, "html.parser")
    remaining_text = soup.find_all(text=True)
    text_list = [text.strip() for text in remaining_text if text.strip()]
    # output_json = {}
    for index in range(len(matches)):
        if index < len(matches) - 1:
            start_index = text_list.index(matches[index])
            end_index = text_list.index(matches[index + 1])
            value = text_list[start_index + 1 : end_index]
            if value:
                if matches[index] == "Work Experience":
                    dict_values = [
                        temp for temp in value[0].split(" ") if temp.isnumeric()
                    ]
                    response_json["Total years of Experience"] = {
                        "Years": dict_values[0],
                        "Months": dict_values[1],
                    }
                elif matches[index] == "Certification/Courses":
                    response_json["Certifications/Courses"] = value
                else:
                    # For Qualificiations, For projects ,
                    response_json[matches[index]] = value
    final_match_index = text_list.index(matches[-1])
    value = text_list[final_match_index + 1 :]

    if matches[-1] == "Work Experience":
        dict_values = [temp for temp in value[0].split(" ") if temp.isnumeric()]
        response_json["Total years of Experience"] = {
            "Years": dict_values[0],
            "Months": dict_values[1],
        }
    elif matches[-1] == "Certification/Courses":
        response_json["Certifications/Courses"] = value
    else:
        # For Qualificiations, For projects etc
        response_json[matches[index]] = value
    return response_json


def del_files_in_folder(folder_path):
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return True
    except Exception as e:
        return False


def downloaded_analysis_csv(response_json, jd_id):
    del_files_in_folder("media/comparision_csv")
    response_jsoni = response_json["analysis"]
    for i in response_jsoni:
        i["Candidate Name"] = i["first_name"] + " " + i["last_name"]
        i["Overall score"] = i["Total_matching_percentage"]
        i["Stage name"] = i["stage_name"]
        i["Overall Score based on the criteria"] = str(
            round(float(i["Average_match_percentage"]))
        )
        candidate_id = i["candidate_id"]
        try:
            recomend_to_hire = (
                Questions_Generation.objects.filter(
                    candidate_id=candidate_id, jd_id=jd_id
                )
                .values("recommend")
                .exclude(recommend=None)
            )
            total_sum = sum(int(item["recommend"]) for item in recomend_to_hire)
            recomend_to_hire = round(total_sum / len(recomend_to_hire))
            if recomend_to_hire == 1:
                recomend_to_hire = "No"
            elif recomend_to_hire == 2:
                recomend_to_hire = "Neutral"
            elif recomend_to_hire == 3:
                recomend_to_hire = "Yes"
            else:
                recomend_to_hire = "Not specified"
        except Exception as e:
            recomend_to_hire = "Not Specified"
        i["Recommended to hire"] = recomend_to_hire
        pros_value = ""
        try:
            for val in i["Pros"]:
                pros_value = val + " " + pros_value
        except:
            pros_value = ""
        if pros_value == "":
            pros_value = "No Data Available"
        try:
            Cons_value = ""
            for val in i["Cons"]:
                Cons_value = val + " " + Cons_value
        except:
            Cons_value = ""
        if Cons_value == "":
            Cons_value = "No Data Available"
        i["Skills Evaluation"] = pros_value
        i["Enhancement Analysis"] = Cons_value
        i["Rating"] = (
            i["overall_scorecard"] if i["overall_scorecard"] else "Not Specified"
        )
        category_values = i.get("categories", {})
        for category, value in category_values.items():
            if value != "null":
                i[category] = value
            else:
                i[category] = "0"
        del i["categories"]
        del i["stage_name"]
        del i["Pros"]
        del i["Cons"]
        del i["Average_match_percentage"]
        del i["Total_matching_percentage"]
        del i["first_name"]
        del i["last_name"]
        del i["stage_color"]
        del i["overall_scorecard"]
        del i["jobid"]
        del i["image"]
    current_date = datetime.now()
    current_date = str(current_date.strftime("%b %d %Y"))
    jd_name = JD_form.objects.get(id=jd_id).job_title
    job_id = JD_form.objects.get(id=jd_id).job_id
    csv_file = (
        BASE_DIR
        + "/media/comparision_csv/"
        + job_id
        + "_"
        + jd_name
        + "_Comparision Analysis"
        + "_"
        + current_date
        + ".csv"
    )
    csv_file_path = csv_file
    headers = response_json["analysis"][0].keys()
    headers = list(headers)
    headers.insert(0, headers.pop(headers.index("Candidate Name")))
    headers = {k: None for k in headers}

    with open(csv_file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for row in response_json["analysis"]:
            writer.writerow(row)
    csv_file = csv_file.name
    csv_file_name = csv_file.split("media/comparision_csv/")[1]
    csv_file_path = csv_file.split("media/")[1]
    return csv_file_name, csv_file_path


# def percentage_matching(perc,score):
#     val = round(int(perc)/100 * int(score))
#     return val


# def weightage_mathching(jd_id,can_id):
#     score = jd_tech_matching.objects.get(jd_id=jd_id)
#     perc = Matched_percentage.objects.filter(jd_id=jd_id,candidate_id=can_id).values("id","title","percentage")
#     try:
#         success = True
#         for i in perc:
#             if i["title"] == "Skills":
#                 val = percentage_matching(i['percentage'],score.skills)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Roles and Responsibilities":
#                 val = percentage_matching(i['percentage'],score.roles)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Experience":
#                 val = percentage_matching(i['percentage'],score.exp)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Educational Qualifications":
#                 val = percentage_matching(i['percentage'],score.qualification)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Technical Tools and Languages":
#                 val = percentage_matching(i['percentage'],score.tech_tools)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Soft Skills":
#                 val = percentage_matching(i['percentage'],score.soft_skills)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Industry-Specific Experience":
#                 val = percentage_matching(i['percentage'],score.industry_exp)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Domain-Specific Experience":
#                 val = percentage_matching(i['percentage'],score.domain_exp)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Certifications":
#                 val = percentage_matching(i['percentage'],score.certification)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Location Alignment":
#                 val = percentage_matching(i['percentage'],score.location)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#             elif i["title"] == "Cultural Fit":
#                 val = percentage_matching(i['percentage'],score.cultural_fit)
#                 Matched_percentage.objects.filter(id=i['id']).update(percentage=val)
#     except:
#         success = False
#         return success


def plan_checking(user_id, access=None):
    if access == "job":
        plan = subscriptions.objects.filter(client_id=user_id).last().plan_id
        features = plan_features.objects.get(plan_id=plan, feature_id=10).feature_value
        # if client_features_balance.objects.filter(client_id=user_id,feature_id = 53).exists():
        #         features =  features + plan_features.objects.get(plan_id=plan,feature_id=53).feature_value
        if client_features_balance.objects.filter(
            client_id=user_id, feature_id=51
        ).exists():
            extra_addons = client_features_balance.objects.get(
                client_id=user_id, feature_id=51
            ).addons_count
            if extra_addons:
                extra_addons = extra_addons * int(
                    addons_plan_features.objects.get(plan_id=plan, addon_id=1).value
                )
                features = features + extra_addons
        return features, plan
    elif access == "resume":
        plan = subscriptions.objects.filter(client_id=user_id).last().plan_id
        features = plan_features.objects.get(plan_id=plan, feature_id=27).feature_value
        # if client_features_balance.objects.filter(client_id=user_id,feature_id = 53).exists():
        #     features =  features + plan_features.objects.get(plan_id=plan,feature_id=53).feature_value
        if client_features_balance.objects.filter(
            client_id=user_id, feature_id=52
        ).exists():
            extra_addons = client_features_balance.objects.get(
                client_id=user_id, feature_id=52
            ).addons_count
            if extra_addons:
                extra_addons = extra_addons * int(
                    addons_plan_features.objects.get(plan_id=plan, addon_id=2).value
                )
                features = features + extra_addons
        if client_features_balance.objects.filter(
            client_id=user_id, feature_id=58
        ).exists():
            extra_addons = client_features_balance.objects.get(
                client_id=user_id, feature_id=58
            ).addons_count
            if extra_addons:
                extra_addons = extra_addons * int(
                    addons_plan_features.objects.get(plan_id=plan, addon_id=4).value
                )
                features = features + extra_addons
        return features, plan
    else:
        plan = subscriptions.objects.filter(client_id=user_id).last().plan_id
        return plan.pk, plan.plan_name


def bulk_matching_user(admin_id, pk):
    matching = None
    if subscriptions.objects.filter(client_id=admin_id, plan_id=7).exists():
        plan_id = subscriptions.objects.filter(client_id=admin_id).last().plan_id.pk
        if (
            plan_id == 7
            or plan_id == "7"
            and client_features_balance.objects.filter(
                client_id=admin_id, feature_id=6
            ).exists()
        ):
            if bulk_matching.objects.filter(jd_id_id=pk).exists():
                matching = bulk_matching.objects.get(jd_id=pk).is_active
    return matching


def add_ons(user_id, product_name, quantity):
    feature_id = 0
    if product_name == "4" or product_name == 4:  # resume unlock
        # addon_jd = int(quantity) + int(client_features_balance.objects.get(client_id=user_id,feature_id_id=53).available_count)
        # client_features_balance.objects.filter(client_id=user_id,feature_id_id=53).update(add_ons=tmeta_addons.objects.get(id=4))
        feature_id = 58

    elif product_name == "1" or product_name == 1:  # jobs
        # addon_jd = int(quantity) + int(client_features_balance.objects.get(client_id=user_id,feature_id_id=10).available_count)
        # client_features_balance.objects.filter(client_id=user_id,feature_id_id=10).update(add_ons=tmeta_addons.objects.get(id=1))
        feature_id = 51
    elif product_name == "2" or product_name == 2:  # resume
        # addon_resume = int(quantity) + int(client_features_balance.objects.get(client_id=user_id,feature_id_id=27).available_count)
        # client_features_balance.objects.filter(client_id=user_id,feature_id_id=27).update(add_ons=tmeta_addons.objects.get(id=2))
        feature_id = 52
    elif product_name == "11" or product_name == 11:  # descriptive analtics
        # addon_resume = int(quantity) + int(client_features_balance.objects.get(client_id=user_id,feature_id_id=27).available_count)
        # client_features_balance.objects.filter(client_id=user_id,feature_id_id=6).update(add_ons=tmeta_addons.objects.get(id=11))
        feature_id = 56
    elif product_name == "3" or product_name == 3:  # AI interview Questions
        feature_id = 60
    elif product_name == "5" or product_name == 5:  # Integrating Jobs Posting credits
        feature_id = 64
    elif product_name == "7" or product_name == 7:  # Interview Question Generations
        feature_id = 59
    elif product_name == "9" or product_name == 9:  # Priority Support credits
        feature_id = 61
    elif (
        product_name == "10" or product_name == 10
    ):  # Resume Matching For Multiple Jobs(AI)
        feature_id = 62
    elif (
        product_name == "11" or product_name == 11
    ):  # AI Resume Matching with Descriptive Analytics
        feature_id = 56
    return feature_id


from datetime import datetime
from dateutil.relativedelta import relativedelta


def one_month_checking(date, month):
    date = datetime.fromisoformat(str(date))
    next_month = date + relativedelta(months=int(month))
    return next_month


def comparative(dat1, dat2):
    date1 = datetime.fromisoformat(str(dat1))
    date2 = datetime.fromisoformat(str(dat2))
    success = None
    if date1.date() > date2.date():
        success = True
    elif date1.date() < date2.date():
        success = False
    else:
        # Dates are the same, compare the times
        if date1.time() > date2.time():
            success = True
        elif date1.time() < date2.time():
            success = False
        else:
            success = False
    return success


def date_exceed_checking(date1_str, date2_str):
    date1 = datetime.fromisoformat(str(date1_str))
    date2 = datetime.fromisoformat(str(date2_str))

    # Compare the dates
    if date2 > date1:
        return True
    else:
        return False


def expire_addons(num):
    if num == "10" or num == 10:
        return 51
    elif num == "27" or num == 27:
        return 52
    elif num == "53" or num == 53:
        return 58
    elif num == "6" or num == 6:
        return 56
    else:
        return 0


def JD_features(result, mandatory_skills, Nice_to_Have):
    if isinstance(result, str):
        result = json.loads(result)
    nicehave, musthave = None, None
    if isinstance(result, dict):
        musthave = result.get("mandatory_skills", None)
        nicehave = result.get("Nice_to_Have", None)
    if mandatory_skills != "":
        mandatory_skills = mandatory_skills.split(",")
    if Nice_to_Have != "":
        Nice_to_Have = Nice_to_Have.split(",")
    try:
        mandatory_skills.extend(musthave)
    except:
        pass
    try:
        Nice_to_Have.extend(nicehave)
    except:
        pass
    return mandatory_skills, Nice_to_Have


def orderby_addons(addon_details):
    feature_order = [10, 27, 53, 6, 62, 60, 59, 61, 11, 12, 14, 65]
    key_function = lambda x: feature_order.index(x["feature_id"])
    sorted_addon_details = sorted(addon_details, key=key_function)
    return sorted_addon_details


def linkedin_unlock(user_id):
    credits = 0
    if client_features_balance.objects.filter(
        client_id=user_id, feature_id=53
    ).exists():
        credits = client_features_balance.objects.get(client_id=user_id, feature_id=53)
        if credits.available_count:
            credits.available_count = credits.available_count - 1
            credits.save()
        credits = credits.available_count
    return credits


def Json_convertion_Core(response):
    json_data = {}
    if isinstance(response, dict):
        json_data["Name"] = (
            response["first_name"]
            if response.get("first_name")
            else response.get("name")
        )
        json_data["Email"] = response.get("Email", None)
        json_data["LinkedIn URL"] = response.get("url", None)
        json_data["Professional Summary"] = response.get("summary", None)
        json_data["Job Type"] = response.get("LinkedIn URL", None)
        if isinstance(response["work_experience"], int):
            exp = response["work_experience"]
            json_data["Total years of Experience"] = {
                "Years": exp,
                "Month": 0,
            }
        json_data["Qualifications"] = response.get("education", None)
        json_data["Technical skills"] = response.get("member_skills_collection", [])
        json_data["Soft skills"] = []
        json_data["Preferred Location"] = response.get("Preferred Location", None)
        json_data["Gender"] = response.get("Gender", None)
        json_data["Date of Birth"] = response.get("Date of Birth", None)
        json_data["Address"] = response.get("Address", None)
        json_data["Highest Qualification"] = response.get("Highest Qualification", None)
        json_data["Code Repository URL"] = response.get("Code Repository URL", None)
        json_data["Current Gross Salary"] = response.get("Current Gross Salary", None)
        json_data["Expected Gross Salary"] = response.get("Expected Gross Salary", None)
        json_data["Roles and Responsibilities"] = response.get(
            "member_experience_collection", []
        )
        json_data["Projects"] = response.get("member_projects_collection", [])
    return json_data
