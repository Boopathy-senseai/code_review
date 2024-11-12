from application.models import *
from login.models import *
from main.models import *
from jobs.models import jd_candidate_analytics
from login.models import Profile as user_profile_image
from django.db.models.expressions import *
from django.db.models import *
import datetime as dt

# Backend Quewry for the preview,profile, and download pages


def get_app_prof_details(u_id, for_exp=False, jd_id=None, epf=False, user_id=None):
    resume_details = {}
    user = User_Info.objects.get(user_id_id=u_id)
    P_info = Personal_Info.objects.get(user_id_id=u_id)
    if epf:
        is_applicant = jd_candidate_analytics.objects.filter(
            candidate_id_id=P_info.application_id, status_id_id=1, jd_id_id=jd_id
        ).exists()
    else:
        is_applicant = True
    try:
        view_contact = jd_candidate_analytics.objects.filter(
            status_id_id=17, candidate_id_id=P_info.application_id, jd_id=jd_id
        ).exists()
    except:
        view_contact = False

    from login.models import Profile as user_profile_image

    resume_details["profile_url"] = str(
        user_profile_image.objects.get(user_id=u_id).image
    )
    role = Recommended_Role.objects.filter(application_id=P_info.application_id)
    role = role.annotate(
        role=Subquery(
            tmeta_ds_main_roles.objects.filter(id=OuterRef("recommended_role")).values(
                "tag_name"
            )[:1]
        )
    )
    resume_details["recommended_role"] = list(role.values_list("role", flat=True))
    if P_info.lastname == None:
        lastname = ""
    else:
        lastname = P_info.lastname
    try:
        resume_details["full_name"] = P_info.firstname + " " + lastname
        resume_details["email"] = P_info.email
    except:
        resume_details["full_name"] = "Not Given"
        resume_details["email"] = "Not Given"
    if P_info.contact_no == None:
        resume_details["phone_no"] = "Not Given"
    else:
        resume_details["phone_no"] = P_info.contact_no
    if P_info.linkedin_url != None:

        resume_details["linkedin_url"] = P_info.linkedin_url
    if P_info.code_repo != None:
        resume_details["repo"] = P_info.code_repo
    if P_info.career_summary != None:
        resume_details["summary"] = P_info.career_summary

    # projects other
    try:
        projects = []
        pro = Projects.objects.filter(
            work_proj_org_id_id=None,
            application_id_id=P_info.application_id,
            work_proj_type=False,
        )
        for i in pro:
            temp = {}
            temp["org"] = ""
            temp["project_name"] = i.work_proj_name
            temp["client"] = i.work_proj_client
            if i.work_proj_describe != None:
                temp["desc"] = i.work_proj_describe
            else:
                temp["desc"] = ""
            roless = i.work_proj_role
            # roless=roless.replace('1).','').replace('Description :','')
            # for z in range(2,50):
            #     roless=roless.replace(str(z)+').',' \n')
            temp["responsibilities"] = roless.split("\n")
            temp["role"] = i.work_proj_desig
            temp["dur"] = i.work_proj_duration

            if i.work_proj_domain != None:

                temp["domain"] = i.work_proj_domain
            else:
                temp["domain"] = ""
            temp["loc"] = i.work_proj_location
            skills = i.work_proj_skills
            skills = skills.replace("1).", "").replace("<br>", "")
            for z in range(2, 50):
                skills = skills.replace(str(z) + ").", " \n")
            temp["skills"] = skills.split("\n")

            projects.append(temp)
        resume_details["projects"] = projects
    except:
        a = 0

    exp = []
    exp_info = Experiences.objects.filter(
        application_id_id=P_info.application_id
    ).order_by("-is_present", "-from_exp")
    for n, i in enumerate(exp_info):
        temp = {}
        temp["exp_id"] = i.exp_id
        if is_applicant == True or view_contact == True:
            temp["org"] = i.organisations
        elif i.is_present == True:
            temp["org"] = "XXXXXXXXXX"
        elif n == 0 and not is_applicant:
            temp["org"] = "XXXXXXXXXX"
        else:
            temp["org"] = i.organisations
        if len(i.designation.split(" ")) > 3:
            temp["des"] = " ".join(i.designation.split(" ")[:3])
        else:
            temp["des"] = " ".join(i.designation.split(" "))
        if i.work_location != None:

            temp["loc"] = i.work_location
        else:
            temp["loc"] = ""
        if i.from_exp == None:
            temp["from_exp"] = ""
        else:
            temp["from_exp"] = i.from_exp.strftime("%b %d,  %Y")
        if i.org_domain != None:

            temp["domain"] = i.org_domain
        else:
            temp["domain"] = ""
        if i.to_exp == None:
            if i.is_present:
                temp["to_exp"] = "Till Date"
            else:
                temp["to_exp"] = ""
        else:
            temp["to_exp"] = i.to_exp.strftime("%b %d,  %Y")
        roless = i.work_role
        roless = roless.replace("1).", "")
        for a in range(2, 50):
            roless = roless.replace(str(a) + ").", " \n")
        temp["roles"] = roless.split("\n")
        temp["exp_tools"] = i.work_tools
        if i.is_present:
            temp["is_present"] = 1
        else:
            temp["is_present"] = 0
        projects = []
        pro = Projects.objects.filter(work_proj_org_id_id=i.exp_id)
        if len(pro) > 0:
            for z in pro:
                temp1 = {}
                if i.organisations != None:
                    temp1["org"] = i.organisations
                else:
                    temp1["org"] = ""
                temp1["project_name"] = z.work_proj_name
                temp1["client"] = z.work_proj_client
                if z.work_proj_describe != None:

                    temp1["desc"] = z.work_proj_describe
                else:
                    temp1["desc"] = ""
                roless = z.work_proj_role
                roless = roless.replace("1).", "").replace("Description :", "")
                for b in range(2, 50):
                    roless = roless.replace(str(b) + ").", " \n")
                temp1["responsibilities"] = roless.split("\n")
                temp1["role"] = z.work_proj_desig
                temp1["dur"] = z.work_proj_duration
                if z.work_proj_domain != None:

                    temp1["domain"] = z.work_proj_domain
                else:
                    temp1["domain"] = ""
                temp1["loc"] = z.work_proj_location
                skills = z.work_proj_skills
                skills = skills.replace("1).", "").replace("<br>", "")
                for z in range(2, 50):
                    skills = skills.replace(str(z) + ").", " \n")
                temp1["skills"] = skills.split("\n")
                projects.append(temp1)
            temp["projects"] = projects
        exp.append(temp)
    resume_details["exp"] = exp

    edu = []
    try:
        edu_info = Education.objects.filter(application_id_id=P_info.application_id)
        for n, i in enumerate(edu_info):
            temp = {}
            temp["edu_id"] = i.edu_id
            temp["title_spec"] = i.qual_spec
            temp["inst_name"] = i.institute_name
            temp["inst_loc"] = i.institute_location
            temp["qual_title"] = i.qual_title
            temp["percentage"] = i.percentage
            temp["year"] = i.year_completed
            edu.append(temp)
        resume_details["edu"] = edu
    except:
        a = 0

    # skills&tools
    try:
        temp = []
        temp_soft = []
        skill_l = Skills.objects.filter(application_id_id=P_info.application_id)
        skill_id = skill_l.values("id")[0]
        for i in skill_l:
            if i.tech_skill != None and len(i.tech_skill) > 0:
                temp.extend(i.tech_skill.split(","))

            if i.soft_skill != None:
                if len(i.soft_skill) > 0 and i.soft_skill != " ":
                    temp_soft.extend(i.soft_skill.split(","))
                else:
                    temp_soft = 0
            else:
                temp_soft = 0
        temp = sorted(temp)
        resume_details["skills"] = temp
        resume_details["skill_id"] = skill_id
        resume_details["soft_skills"] = temp_soft
    except:
        a = 0

    # certifications&courses
    certi = []
    try:
        courses_info = Certification_Course.objects.filter(
            application_id_id=P_info.application_id
        )
        for i in courses_info:
            temp = {}
            temp["cert_id"] = i.id
            temp["certification_name"] = i.certificate_name
            temp["certificate_by"] = i.certificate_by
            temp["certificate_year"] = str(i.certificate_year)
            certi.append(temp)
        resume_details["certi"] = certi
    except:
        a = 0

    # academic projects
    ac_projects = []

    try:
        ac_proj = Projects.objects.filter(
            application_id_id=P_info.application_id,
            work_proj_type=1,
            work_proj_org_id=None,
        )
        for i in ac_proj:

            if i.work_proj_type == True:
                temp = {}
                if i.work_proj_org_id_id == None:
                    if i.work_proj_type == False or i.work_proj_type == None:
                        temp["org"] = "Private Project"
                    else:
                        temp["org"] = "Academic Project"
                else:
                    exp = Experiences.objects.get(
                        exp_id=i.work_proj_org_id_id
                    ).organisations

                    temp["org"] = exp

                temp["pro_id"] = i.project_id
                temp["project_name"] = i.work_proj_name
                temp["client"] = i.work_proj_client
                if i.work_proj_describe != None:
                    temp["desc"] = i.work_proj_describe
                else:
                    temp["desc"] = " "
                roless = i.work_proj_role
                roless = roless.replace("1).", "").replace("Description :", "")
                for z in range(2, 50):
                    roless = roless.replace(str(z) + ").", " \n")
                temp["responsibilities"] = roless.split("\n")
                temp["role"] = i.work_proj_desig
                temp["dur"] = i.work_proj_duration
                if i.work_proj_domain != None:

                    temp["domain"] = i.work_proj_domain
                else:
                    temp["domain"] = ""
                temp["loc"] = i.work_proj_location
                skills = i.work_proj_skills
                skills = skills.replace("1).", "").replace("<br>", "")
                for z in range(2, 50):
                    skills = skills.replace(str(z) + ").", " \n")
                temp["skills"] = skills.split("\n")
                ac_projects.append(temp)
            resume_details["ac_projects"] = ac_projects

    except:
        a = 0

    proj_list = []
    try:
        ac_proj = Projects.objects.filter(application_id_id=P_info.application_id)

        for i in ac_proj:
            temp = {}
            if i.work_proj_org_id_id == None:
                if i.work_proj_type == False or i.work_proj_type == None:
                    temp["org"] = "Private Project"
                else:
                    temp["org"] = "Academic Project"
            else:
                exp = Experiences.objects.get(
                    exp_id=i.work_proj_org_id_id
                ).organisations

                temp["org"] = exp
            temp["pro_id"] = i.project_id
            temp["project_name"] = i.work_proj_name
            temp["client"] = i.work_proj_client
            if i.work_proj_describe != None:
                temp["desc"] = i.work_proj_describe
            else:
                temp["desc"] = " "
            roless = i.work_proj_role
            roless = roless.replace("1).", "").replace("Description :", "")
            for z in range(2, 50):
                roless = roless.replace(str(z) + ").", " \n")
            temp["responsibilities"] = roless.split("\n")
            temp["role"] = i.work_proj_desig
            temp["dur"] = i.work_proj_duration
            if i.work_proj_domain != None:

                temp["domain"] = i.work_proj_domain
            else:
                temp["domain"] = ""
            temp["loc"] = i.work_proj_location
            skills = i.work_proj_skills
            skills = skills.replace("1).", ",").replace("<br>", ",")
            temp["skills"] = skills
            proj_list.append(temp)
        resume_details["proj_list"] = proj_list
    except:
        a = 0

    # Contributions
    contribs = []
    try:
        contrib = Contributions.objects.filter(application_id_id=P_info.application_id)
        for i in contrib:
            temp = {}
            temp["cont_id"] = i.contributions_id
            temp["contrib_text"] = i.contrib_text
            temp["contrib_type"] = i.contrib_type.value
            contribs.append(temp)
        resume_details["contribs"] = contribs
    except:
        a = 0
    # Internships
    internships = []
    try:
        internship = Fresher.objects.filter(application_id_id=P_info.application_id)
        for i in internship:
            temp = {}
            temp["fre_id"] = i.id
            temp["org"] = i.intern_org
            temp["project_name"] = i.intern_project
            temp["client"] = i.intern_client
            roless = i.intern_proj_describe.split("\n")
            temp["desc"] = roless
            temp["role"] = i.intern_role
            temp["dur"] = i.intern_duration
            temp["domain"] = i.intern_domain
            temp["loc"] = i.intern_location
            temp["tools"] = i.intern_tools_prg_lng

            internships.append(temp)
        resume_details["internships"] = internships
    except:
        a = 0

    if for_exp:
        prof = list(
            Visualize.objects.filter(application_id_id=P_info.application_id).values(
                "business_intelligence",
                "data_analysis",
                "data_engineering",
                "devops",
                "machine_learning",
                "others",
            )
        )
        return (user, resume_details, prof)
    else:

        return (user, resume_details)
