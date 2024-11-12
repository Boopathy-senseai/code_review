# <-------- Convert to The Applicant General ------>
from bulk_upload.api import pre_population
from jobs.models import *
import json
from jobs.views import generate_random_username
from zita.settings import TEMPLATES
from xhtml2pdf import pisa
from django.template.loader import get_template
import zipfile
import io
import os
from datetime import timedelta, datetime
from zita import settings
import phonenumbers

base_dir = settings.BASE_DIR


def Applicant_convertion(can_id, jd_id, user_id):
    pool = employer_pool.objects.get(id=can_id)
    name = pool.first_name
    email = pool.email
    file_dir = candidate_parsed_details.objects.get(candidate_id=can_id)
    LinkedIn = pool.linkedin_url
    from django.utils import timezone

    username = generate_random_username()
    password = generate_random_username(split=8)
    user = User.objects.create(username=username, date_joined=timezone.now())
    user.set_password(password)
    user.save()
    # jd_title = JD_form.objects.get(id=jd_id).job_title
    user = User.objects.get(username=username)
    user_info = User_Info.objects.create(
        user_id=user,
        username=user.username,
        first_name=name,
        password=password,
        employer_id=user_id,
    )
    personal = Personal_Info.objects.create(
        user_id=user, firstname=name, linkedin_url=LinkedIn, email=email
    )
    Myfiles.objects.create(upload_id=user, resume_file=file_dir.resume_file_path)
    pool.candidate_id = personal
    try:
        results = json.loads(result)
        total_exp_year = (results.get("Total years of Experience", {}).get("Years", 0),)
        total_exp_month = results.get("Total years of Experience", {}).get("Months", 0)
        Additional_Details.objects.create(
            application_id=personal,
            total_exp_year=total_exp_year,
            total_exp_month=total_exp_month,
        )
    except Exception as e:
        pass
    file = str(file_dir.resume_file_path)
    file_name = file.rsplit("/", 1)[-1]
    result = pre_population(file_name, personal)
    result = json.loads(file_dir.parsed_text)
    soft_s = result.get("Soft skills", None)
    if soft_s:
        if "Soft skills" in result:
            if result.get("Technical skills", None):
                result["Technical skills"].extend(result["Soft skills"])
    else:
        soft_s = result.get("Soft Skills", None)
        if soft_s:
            if result.get("Technical skills", None):
                result["Technical skills"].extend(result["Soft Skills"])
    t_skills = result.get("Technical skills", None)
    t_skills = list(filter(lambda x: x is not None, t_skills))

    if t_skills:
        skills = ", ".join(t_skills)
    else:
        skills = None
    if Skills.objects.filter(application_id=personal).exists():
        tech_skill = Skills.objects.get(application_id=personal)
        pool.skills = skills
    jd_id = JD_form.objects.get(id=jd_id)
    pool.jd_id_id = jd_id.id
    pool.save()


# <----- Existing Stages Candidates Can create TODO Stages ---->
def Todo_Stages_creation(jd_id):
    if applicants_status.objects.filter(jd_id=jd_id, stage_id__isnull=False).exists():
        data = applicants_status.objects.filter(jd_id=jd_id, stage_id__isnull=False)
        for i in data:
            if not pipeline_status.objects.filter(
                jd_id=i.jd_id, candidate_id=i.candidate_id, pipeline_id=i.stage_id
            ).exists():
                stages = tmeta_stages.objects.get(id=1)
                pipeline_status.objects.create(
                    jd_id=i.jd_id,
                    candidate_id=i.candidate_id,
                    pipeline_id=i.stage_id.id,
                    stage=stages,
                    user_id=i.client_id,
                )
        return True
    return False


def contains_nested_list(lst):
    """Check if the given list contains any nested lists."""
    for element in lst:
        if isinstance(element, list):
            return True
    return False


def replace_spaces(dictionary):
    if isinstance(dictionary, dict):
        return {k.replace(" ", "_"): replace_spaces(v) for k, v in dictionary.items()}
    return dictionary


def fetch_resources(uri, rel):
    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return path


def core_signal_pdf_generate(candidate_id, download_content, user_id):
    print("core_signal_pdf_generate----->",type(download_content))
    data = json.loads(download_content)
    data = replace_spaces(data)
    data = Linkedin_profile(data, candidate_id, user_id)
    template = get_template("pdf/profile_for_linkedin.html")
    candidate_name = candidate_id
    html_string = template.render({"data": data, "name": candidate_name})
    pdf = io.BytesIO()
    pdf_name = (
        f"{base_dir}/media/linkedin_sourcing/candidate_profile_{candidate_id}.pdf"
    )
    with open(pdf_name, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(
            html_string, dest=pdf_file, link_callback=fetch_resources
        )
    if linkedin_data.objects.filter(linkedin_id=candidate_id).exists():
        update_name = pdf_name.split("media", 1)
        if len(update_name) > 1:
            new_pdf_name = "media" + update_name[1]
            linkedin_data.objects.filter(linkedin_id=candidate_id).update(
                resume_file_path=new_pdf_name
            )
            if unlocked_candidate.objects.filter(
                unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
            ).exists():
                unlocked_candidate.objects.filter(
                    unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
                ).update(resume_file_path=new_pdf_name)
    return pdf_name


def Linkedin_profile(content, candidate_id, user_id):
    if linkedin_data.objects.filter(linkedin_id=candidate_id).exists():
        source_data = json.loads(
            linkedin_data.objects.get(linkedin_id=candidate_id).sourcing_data
        )
        if isinstance(content, dict):
            if unlocked_candidate.objects.filter(
                unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
            ).exists():
                content["location"] = source_data.get("location")
                content["education"] = source_data.get("education")
                content["work_experience"] = source_data.get("work_experience")
                content["industry"] = source_data.get("industry")
                content["connections"] = source_data.get("connections")
                content["summary"] = source_data.get("summary")
                content["country"] = source_data.get("country")
                content["Linkedin"] = source_data.get("url")
                content["name"] = source_data.get("name")
            if not unlocked_candidate.objects.filter(
                unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
            ).exists():
                content["Linkedin"] = modify_url(source_data, "url", 28)
                name = source_data.get("name")
                content["hide"] = True
                content["name"] = modify_url(source_data, "name", len(name))

    return content


def modify_url(source_data, key, length):
    url = source_data.get(key)
    if key == "name":
        modified_url = length * "#"
    else:
        modified_url = url[:length] + "#" * (len(url) - length)
    return modified_url


def core_signal_data_generate(candidate_id, user_id):
    datas = json.loads(
        linkedin_data.objects.get(linkedin_id=candidate_id).linkedin_source_data
    )

    data = datas
    keys_to_remove = [
        "id",
        "first_name",
        "last_name",
        "outdated",
        "deleted",
        "country",
        "member_shorthand_name",
        "member_shorthand_name_hash",
        "canonical_url",
        "canonical_hash",
        "member_courses_suggestion_collection",
        "member_interests_collection",
        "member_languages_collection",
        "member_organizations_collection",
        "member_posts_see_more_urls_collection",
        "member_publications_collection",
        "member_recommendations_collection",
        "member_test_scores_collection",
        "member_volunteering_cares_collection",
        "member_volunteering_opportunities_collection",
        "member_volunteering_positions_collection",
        "member_volunteering_supports_collection",
        "member_also_viewed_collection",
        "member_groups_collection",
        "member_similar_profiles_collection",
    ]

    for key in keys_to_remove:
        data.pop(key, None)
    unique_education_entries = {}

    for education in data["member_education_collection"]:
        if education["subtitle"] != None:
            title = f"{education['title']}-{education['subtitle']}"

            if title not in unique_education_entries:
                unique_education_entries[title] = education

    data["member_education_collection"] = list(unique_education_entries.values())

    unique_experience_entries = {}

    for experience in data["member_experience_collection"]:
        title = f"{experience['title']}-{experience['company_name']}"

        if title not in unique_experience_entries:
            unique_experience_entries[title] = experience

    data["member_experience_collection"] = list(unique_experience_entries.values())
    unique_project_entries = {}

    for project in data["member_projects_collection"]:
        title_key = f"{project['name']}"

        if title_key not in unique_project_entries:
            unique_project_entries[title_key] = project

    data["member_projects_collection"] = list(unique_project_entries.values())

    unique_certification_entries = {}

    for project in data["member_certifications_collection"]:
        title_key = f"{project['name']}"

        if title_key not in unique_certification_entries:
            unique_certification_entries[title_key] = project

    data["member_certifications_collection"] = list(
        unique_certification_entries.values()
    )

    template = get_template("pdf/profile_for_linkedin.html")

    if not unlocked_candidate.objects.filter(
        unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
    ).exists():
        data["url"] = modify_url(data, "url", 28)
        name = data.get("name")
        data["hide"] = True
        data["name"] = modify_url(data, "name", len(name))
    html = template.render({"data": data})

    pdf = io.BytesIO()
    pdf_status = pisa.CreatePDF(html, dest=pdf, link_callback=fetch_resources)

    pdf_file_path = os.path.join(
        settings.MEDIA_ROOT, f"linkedin_sourcing/candidate_profile_{candidate_id}.pdf"
    )
    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)
    with open(pdf_file_path, "wb") as output_file:
        output_file.write(pdf.getvalue())

    # pdf_name = f'{base_dir}/linkedin_sourcing/candidate_profile_{candidate_id}.pdf'
    # pdf_name = os.path.join(settings.MEDIA_ROOT, f'/linkedin_sourcing/candidate_profile_{candidate_id}.pdf')
    pdf_name = os.path.join(
        settings.MEDIA_ROOT, f"linkedin_sourcing/candidate_profile_{candidate_id}.pdf"
    )

    if linkedin_data.objects.filter(linkedin_id=candidate_id).exists():
        update_name = pdf_name.split("media", 1)
    if len(update_name) > 1:
        new_pdf_name = "media" + update_name[1]
        linkedin_data.objects.filter(linkedin_id=candidate_id).update(
            resume_file_path=new_pdf_name
        )
        if unlocked_candidate.objects.filter(
            unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
        ).exists():
            unlocked_candidate.objects.filter(
                unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
            ).update(resume_file_path=new_pdf_name)
    return pdf_name


def core_signal_data_generate(candidate_id, user_id):
    datas = json.loads(
        linkedin_data.objects.get(linkedin_id=candidate_id).linkedin_source_data
    )

    data = datas
    keys_to_remove = [
        "id",
        "first_name",
        "last_name",
        "outdated",
        "deleted",
        "country",
        "member_shorthand_name",
        "member_shorthand_name_hash",
        "canonical_url",
        "canonical_hash",
        "member_courses_suggestion_collection",
        "member_interests_collection",
        "member_languages_collection",
        "member_organizations_collection",
        "member_posts_see_more_urls_collection",
        "member_publications_collection",
        "member_recommendations_collection",
        "member_test_scores_collection",
        "member_volunteering_cares_collection",
        "member_volunteering_opportunities_collection",
        "member_volunteering_positions_collection",
        "member_volunteering_supports_collection",
        "member_also_viewed_collection",
        "member_groups_collection",
        "member_similar_profiles_collection",
    ]
    for key in keys_to_remove:
        data.pop(key, None)
    unique_education_entries = {}

    for education in data["member_education_collection"]:
        if education["subtitle"] != None:
            title = f"{education['title']}-{education['subtitle']}"

            if title not in unique_education_entries:
                unique_education_entries[title] = education

    data["member_education_collection"] = list(unique_education_entries.values())

    unique_experience_entries = {}

    for experience in data["member_experience_collection"]:
        title = f"{experience['title']}-{experience['company_name']}"

        if title not in unique_experience_entries:
            unique_experience_entries[title] = experience

    data["member_experience_collection"] = list(unique_experience_entries.values())
    unique_project_entries = {}

    for project in data["member_projects_collection"]:
        title_key = f"{project['name']}"

        if title_key not in unique_project_entries:
            unique_project_entries[title_key] = project

    data["member_projects_collection"] = list(unique_project_entries.values())

    unique_certification_entries = {}

    for project in data["member_certifications_collection"]:
        title_key = f"{project['name']}"

        if title_key not in unique_certification_entries:
            unique_certification_entries[title_key] = project

    data["member_certifications_collection"] = list(
        unique_certification_entries.values()
    )

    template = get_template("pdf/profile_for_linkedin.html")

    if not unlocked_candidate.objects.filter(
        unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
    ).exists():
        data["url"] = modify_url(data, "url", 28)
        name = data.get("name")
        data["hide"] = True
        data["name"] = modify_url(data, "name", len(name))
    html = template.render({"data": data})

    pdf = io.BytesIO()
    pdf_status = pisa.CreatePDF(html, dest=pdf, link_callback=fetch_resources)

    pdf_file_path = os.path.join(
        settings.MEDIA_ROOT, f"linkedin_sourcing/candidate_profile_{candidate_id}.pdf"
    )
    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)
    with open(pdf_file_path, "wb") as output_file:
        output_file.write(pdf.getvalue())

    # pdf_name = f'{base_dir}/linkedin_sourcing/candidate_profile_{candidate_id}.pdf'
    # pdf_name = os.path.join(settings.MEDIA_ROOT, f'/linkedin_sourcing/candidate_profile_{candidate_id}.pdf')
    pdf_name = os.path.join(
        settings.MEDIA_ROOT, f"linkedin_sourcing/candidate_profile_{candidate_id}.pdf"
    )

    if linkedin_data.objects.filter(linkedin_id=candidate_id).exists():
        update_name = pdf_name.split("media", 1)
    if len(update_name) > 1:
        new_pdf_name = "media" + update_name[1]
        linkedin_data.objects.filter(linkedin_id=candidate_id).update(
            resume_file_path=new_pdf_name
        )
        if unlocked_candidate.objects.filter(
            unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
        ).exists():
            unlocked_candidate.objects.filter(
                unlocked_candidate__linkedin_id=candidate_id, user_id=user_id
            ).update(resume_file_path=new_pdf_name)
    return pdf_name


# Phone Number Convertion based on Country Code
def convert_phonenumber(num):
    if "+" not in num:
        num = "+" + num
    try:
        parsed_number = phonenumbers.parse(num, None)
        country_code = parsed_number.country_code
        formatted_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
    except:
        country_code = num[:2]
        area_code = num[2:5]
        part1 = num[5:8]
        part2 = num[8:]
        formatted_number = f"{country_code} ({area_code}) {part1}-{part2}"
    return formatted_number
