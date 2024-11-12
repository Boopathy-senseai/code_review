from django.db import models
from application.models import *
from calendarapp.models import CalEvents

from main.models import *
from django.contrib.auth.models import User
from enum import Enum
from django.core.exceptions import ValidationError

# from PIL import Image
from django.core.validators import FileExtensionValidator

# ROLES = (
from django.db.models import CharField

# from jobspipeline.models import pipeline_stages
from django.core.validators import *
from jobspipeline.models import *
from calendarapp.models import *

from jobspipeline.models import *

# JOB_TYPE = (
#   ('full_time', 'FULL TIME'),
#   ('part_time', 'PART TIME'),
#   ('contract', 'CONTRACT'),
# )

# JOB_STATUS = (
#   ('active', 'ACTIVE'),
#   ('closed', 'CLOSED'),
#   ('draft', 'DRAFT'),
# )

# from django_mysql.models import ListCharField

# class test(models.Model):
#     name = CharField(max_length=100)
#     post_nominals = ListCharField(base_field=CharField(max_length=10), size=6, max_length=(6 * 11)  # 6 * 10 character nominals, plus commas
#     )


class candidate_status(Enum):
    viewed = 1
    applied = 2
    shortlisted = 3
    interviewed = 4
    rejected = 5
    hired = 6


class recom_cand_status(Enum):
    notshortlisted = 0
    shortlisted = 3
    interviewed = 4
    rejected = 5
    hired = 6


class tmeta_jd_candidate_status(models.Model):
    value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=1)
    description = models.CharField(max_length=1000)
    label_name = models.CharField(max_length=100, null=True)
    created_on = models.DateField(auto_now_add=True)


class tmeta_skills_category(models.Model):
    value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=1)
    description = models.CharField(max_length=1000)
    label_name = models.CharField(max_length=100, null=True)
    created_on = models.DateField(auto_now_add=True)


class tmeta_field_types(models.Model):
    value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=1)
    description = models.CharField(max_length=1000)
    label_name = models.CharField(max_length=100, null=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.label_name


class tmeta_currency_type(models.Model):
    value = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    label_name = models.CharField(max_length=100)
    sequence = models.IntegerField()

    def __str__(self):
        return self.value


class tmeta_career_page_plan(models.Model):
    value = models.CharField(max_length=100)
    price = models.IntegerField()
    job_posting = models.BooleanField(default=True)
    questionnaire = models.BooleanField(default=True)
    career_page = models.BooleanField(default=True)
    has_external_posting = models.BooleanField(default=True)
    zita_match = models.BooleanField(default=True)
    applicant_access = models.BooleanField(default=True)
    job_featuring = models.BooleanField()
    has_external_promotion = models.BooleanField()
    tailored_email = models.BooleanField(default=False)
    label_name = models.CharField(max_length=100)
    validity_days = models.IntegerField(default=0)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.value


class tmeta_job_posting_plan(models.Model):
    value = models.CharField(max_length=100)
    price = models.IntegerField()
    invites_count = models.IntegerField(null=True)
    view_contact_count = models.IntegerField(null=True)
    validity_days = models.IntegerField(null=True)
    featured_days = models.IntegerField(null=True)
    applicant_count = models.IntegerField(null=True)
    has_external_promotion = models.BooleanField(default=False)
    label_name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.value


class tmeta_job_posting_add_on(models.Model):
    value = models.CharField(max_length=100)
    price = models.FloatField()
    applicant_count = models.IntegerField(null=True)
    label_name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.value


class tmeta_email_preference(models.Model):
    stage_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    inactivated_date = models.DateTimeField(null=True)
    updated_by = models.CharField(max_length=255)


class tmeta_jd_templates(models.Model):
    job_description = models.TextField()
    job_title = models.CharField(max_length=1000, null=True)
    qualification = models.CharField(max_length=1000, null=True)
    experience = models.CharField(max_length=1000, null=True)
    created_on = models.DateField(auto_now_add=True)
    is_ds_role = models.BooleanField(null=True)
    skills = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.job_title


class tmeta_jd_status(models.Model):
    value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=1)
    description = models.CharField(max_length=1000, null=True)
    label_name = models.CharField(max_length=100, null=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.label_name


class tmeta_candidate_source(models.Model):
    value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=1)
    description = models.CharField(max_length=1000, null=True)
    label_name = models.CharField(max_length=100, null=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.value


# Create your models here.
class JD_form(models.Model):
    job_posted_on = models.DateTimeField(auto_now_add=True)
    job_reposted_on = models.DateTimeField(null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=60)
    job_id = models.CharField(max_length=50)
    visa_sponsor = models.BooleanField(max_length=10, default=True)
    company_name = models.CharField(max_length=60)
    company_website = models.URLField(max_length=100)
    no_of_vacancies = models.IntegerField(null=True)
    company_logo = models.FileField(
        upload_to="company_logo/", default="default_logo.png"
    )
    job_role = models.ForeignKey(tmeta_ds_main_roles, on_delete=models.CASCADE)
    org_info = models.TextField(max_length=10000, null=True)
    min_exp = models.FloatField(null=False)
    max_exp = models.IntegerField(null=True)
    work_remote = models.BooleanField(default=False, null=True)
    is_ds_role = models.BooleanField(null=True)
    is_eeo_comp = models.BooleanField(null=True)
    work_remote = models.BooleanField(default=False, null=True)
    role_res = models.TextField(max_length=10000, null=False)
    job_description = models.TextField(max_length=10000, null=True)
    richtext_job_description = models.TextField(max_length=1000, null=True)
    tech_req = models.TextField(max_length=1000)
    non_tech_req = models.TextField(max_length=1000)
    updated_by = models.CharField(max_length=100, null=True)
    industry_type = models.ForeignKey(
        tmeta_industry_type, null=True, on_delete=models.CASCADE
    )
    add_info = models.TextField(max_length=1000, blank=True, null=True)
    salary_min = models.FloatField(null=True, validators=[MaxValueValidator(9999999)])
    salary_max = models.FloatField(null=True, validators=[MaxValueValidator(9999999)])
    salary_curr_type = models.ForeignKey(
        tmeta_currency_type, on_delete=models.CASCADE, blank=True, null=True
    )
    show_sal_to_candidate = models.BooleanField(null=True, blank=True, default=False)
    job_type = models.ForeignKey(tmeta_job_type, null=False, on_delete=models.CASCADE)
    jd_status = models.ForeignKey(
        tmeta_jd_status, default=1, null=False, on_delete=models.CASCADE
    )
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    work_space_type = models.CharField(max_length=100, null=True)
    # success = models.BooleanField(default= False)


class tmeta_message_templates(models.Model):
    name = models.CharField(max_length=100)
    templates = models.TextField()
    templates_text = models.TextField(null=True)
    created_on = models.DateField(auto_now_add=True)
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    subject = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=False)
    stage = models.IntegerField(null=True)
    status = models.BooleanField(null=True)
    stage = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class JD_locations(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    lat = models.FloatField(max_length=50, null=True)
    lng = models.FloatField(max_length=50, null=True)
    location = models.CharField(max_length=200, null=True)


class JD_skills_experience(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE)
    category = models.ForeignKey(
        "tmeta_skills_category", on_delete=models.CASCADE, null=True
    )
    skill = models.TextField(max_length=100)
    experience = models.CharField(max_length=20, default=0)


class JD_qualification(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True, null=True)


class JD_profile(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    business_intelligence = models.CharField(max_length=200, blank=True, default=0)
    data_analysis = models.CharField(max_length=200, blank=True, default=0)
    data_engineering = models.CharField(max_length=200, blank=True, default=0)
    devops = models.CharField(max_length=200, blank=True, default=0)
    machine_learning = models.CharField(max_length=200, blank=True, default=0)
    others = models.CharField(max_length=200, blank=True, default=0)
    recommended_role = models.ForeignKey(tmeta_ds_main_roles, on_delete=models.CASCADE)
    dst_or_not = models.CharField(max_length=20, blank=True, default=2)
    role_acceptence = models.BooleanField(default=False)
    # dst_or_not = models.CharField(max_length=20, blank=True, default = 2)
    updated_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver_messages"
    )
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    is_read = models.BooleanField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} to {}".format(self.sender.username, self.receiver.username)


class Message_non_applicants(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        "employer_pool",
        on_delete=models.CASCADE,
    )
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)


class daily_visualise(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE)
    date = models.DateTimeField()
    y = models.CharField(max_length=2000, blank=True, default=0)
    v_type = models.CharField(max_length=2000, blank=True, default=0)


class JDUploads(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    application_id = models.ForeignKey("JD_form", on_delete=models.CASCADE)
    jd_path = models.CharField(max_length=500, blank=True)
    photo_path = models.CharField(max_length=500, blank=True, default=0)
    parsed_file = models.CharField(max_length=1000, blank=True, default=0)


class jd_parsed_details(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)s_requests_created"
    )
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    parsed_text = models.TextField(max_length=50000, null=True)
    resume_file_path = models.TextField(max_length=2000, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class job_view_count(models.Model):
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    count = models.IntegerField(null=True)
    source = models.CharField(max_length=500, null=True)
    created_at = models.DateField(auto_now_add=True)


class JDfiles(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)s_requests_created"
    )
    jd_file = models.FileField(upload_to="uploaded_jds/", default=0)
    # jd_id = models.ForeignKey('JD_form',on_delete=models.CASCADE,null=True)
    # parsed_text = models.TextField(max_length=50000, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Missing_Skills_Table(models.Model):
    miss_skill_id = models.AutoField(primary_key=True)
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE)
    missingskill_mand = models.TextField("Mandatory Skills*", max_length=5000)
    missingskill_pl = models.TextField("", blank=True, max_length=5000)
    missingskill_db = models.TextField("", blank=True, max_length=5000)
    missingskill_tl = models.TextField("", blank=True, max_length=5000)
    missingskill_pf = models.TextField("", blank=True, max_length=5000)
    missingskill_ot = models.TextField("", blank=True, max_length=5000)


class jd_candidate_analytics(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey(Personal_Info, on_delete=models.CASCADE)
    recruiter_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status_id = models.ForeignKey(tmeta_jd_candidate_status, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(auto_now_add=True)
    applied_location = models.CharField(max_length=500, null=True, default="")
    interested = models.BooleanField(default=0)
    contacted = models.BooleanField(default=0)
    rejected = models.BooleanField(default=0)
    shortlisted_role_id = models.ForeignKey(
        tmeta_ds_main_roles, on_delete=models.CASCADE, null=True
    )


class Candi_invite_to_apply(models.Model):
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    is_interested = models.BooleanField(null=True)
    updated_by = models.CharField(max_length=100, null=True)
    created_at = models.DateField(auto_now_add=True)
    responded_date = models.DateTimeField(null=True)


class Candidate_notes(models.Model):
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    notes = models.TextField(max_length=2000, null=True)
    updated_by = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# class Mention_Candidate_notes(models.Model):
# 	client_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
# 	candidate_id = models.ForeignKey('employer_pool',on_delete=models.CASCADE)
# 	candidate_names = models.CharField(max_length=1000, null = True)
# 	updated_by = models.CharField(max_length=100,null=True)
# 	created_at = models.DateTimeField(auto_now_add=True)


class Zita_match_count(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class Feedback_form(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=500, null=True)
    email = models.CharField(max_length=500, null=True)
    rating = models.IntegerField(default=0)
    comments = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# not needed
class recuriter_payment_history(models.Model):
    recruiter_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    plan_id = models.ForeignKey(
        "tmeta_job_posting_plan", on_delete=models.CASCADE, null=True
    )
    add_on_id = models.ForeignKey(
        "applicant_add_on_plan", on_delete=models.CASCADE, null=True
    )
    job_posting_plan_id = models.ForeignKey(
        "recuriter_job_posting_plan", on_delete=models.CASCADE, null=True
    )
    is_paid = models.BooleanField(default=True)
    price = models.IntegerField(null=True)
    invoice_id = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)


class recuriter_job_posting_plan(models.Model):
    recruiter_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    plan_id = models.ForeignKey(
        "tmeta_job_posting_plan", on_delete=models.CASCADE, null=True
    )
    available_invites = models.IntegerField(null=True)
    available_applicants = models.IntegerField(null=True)
    featured_days = models.IntegerField(null=True)
    available_days = models.IntegerField(null=True)
    has_external_promotion = models.BooleanField(default=False)
    available_view_contacts = models.IntegerField(null=True)
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True)


class applicant_add_on_plan(models.Model):
    recruiter_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    add_on_id = models.ForeignKey(
        "tmeta_job_posting_add_on", on_delete=models.CASCADE, null=True
    )
    available_count = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    # def __str__(self):
    #   return self.label_name


class applicant_questionnaire(models.Model):
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    field_type = models.ForeignKey(
        "tmeta_field_types", on_delete=models.CASCADE, null=True
    )
    question = models.CharField(max_length=1000, null=True)
    description = models.TextField(max_length=10000, null=True)
    is_required = models.BooleanField(null=True)
    option1 = models.CharField(max_length=1000, null=True)
    option2 = models.CharField(max_length=1000, null=True)
    option3 = models.CharField(max_length=1000, null=True)
    option4 = models.CharField(max_length=1000, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)


class applicant_questionnaire_template(models.Model):

    field_type = models.ForeignKey(
        "tmeta_field_types", on_delete=models.CASCADE, null=True
    )
    question = models.CharField(max_length=1000, null=True)
    is_required = models.BooleanField(null=True)
    description = models.TextField(max_length=10000, null=True)
    option1 = models.CharField(max_length=1000, null=True)
    option2 = models.CharField(max_length=1000, null=True)
    option3 = models.CharField(max_length=1000, null=True)
    option4 = models.CharField(max_length=1000, null=True)


class employer_pool(models.Model):
    can_source = models.ForeignKey(
        "tmeta_candidate_source", on_delete=models.CASCADE, null=True
    )
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="user_id"
    )
    candidate_id = models.ForeignKey(Personal_Info, on_delete=models.CASCADE, null=True)
    job_type = models.ForeignKey(tmeta_job_type, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    contact = models.CharField(max_length=200, null=True)
    login_shared = models.BooleanField(null=True)
    linkedin_url = models.CharField(max_length=200, null=True)
    work_exp = models.CharField(max_length=200, null=True)
    relocate = models.BooleanField(null=True)
    qualification = models.CharField(max_length=200, null=True)
    exp_salary = models.CharField(max_length=200, null=True)
    job_title = models.CharField(max_length=2000, null=True)
    candi_ref_id = models.CharField(max_length=200, null=True)
    skills = models.TextField(max_length=10000, null=True)
    location = models.CharField(max_length=2000, null=True)
    updated_on = models.DateField(auto_now_add=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, null=True)
    favourite = models.ManyToManyField(
        "JD_form", related_name="favourite", through="favourites", blank=True
    )


class favourites(models.Model):
    candidate_id = models.ForeignKey(
        "employer_pool", on_delete=models.CASCADE, null=True
    )
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    updated_on = models.DateTimeField(null=True, blank=True, auto_now_add=True)


class candidate_parsed_details(models.Model):
    candidate_id = models.ForeignKey(
        "employer_pool", on_delete=models.CASCADE, null=True
    )
    parsed_text = models.TextField(max_length=50000, blank=True)
    resume_file_path = models.FileField(upload_to="candidate_resume/", default=0)
    updated_on = models.DateTimeField(auto_now_add=True)
    resume_description = models.TextField(null=True)


class Matched_candidates(models.Model):
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE)
    profile_match = models.FloatField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)


class interview_scorecard(models.Model):
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.FloatField(default=0)
    comments = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    interview_id = models.ForeignKey(CalEvents, on_delete=models.CASCADE, null=True)


class score_categories(models.Model):
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating1 = models.FloatField(default=0)
    rating2 = models.FloatField(default=0)
    rating3 = models.FloatField(default=0)
    rating4 = models.FloatField(default=0)
    rating5 = models.FloatField(default=0)
    overall_percentage = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    interview_id = models.ForeignKey(CalEvents, on_delete=models.CASCADE, null=True)


class application_form(models.Model):
    candidate_id = models.ForeignKey(Personal_Info, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=2000, blank=True)
    last_name = models.CharField(max_length=2000, blank=True)
    email = models.CharField(max_length=2000, blank=True)
    contact = models.CharField(max_length=2000, blank=True)
    location = models.CharField(max_length=2000, blank=True)
    linkedin_url = models.URLField(max_length=2000, blank=True)
    cv_file = models.FileField(upload_to="applicant_Resume/", default=0)


class applicant_cover_letter(models.Model):
    candidate_id = models.ForeignKey(Personal_Info, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    cover_letter = models.TextField(max_length=20000, blank=True)
    source = models.CharField(max_length=1000, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)


class applicant_answers(models.Model):
    qus_id = models.ForeignKey("applicant_questionnaire", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(Personal_Info, on_delete=models.CASCADE)
    answer = models.CharField(max_length=10000, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)


class company_details(models.Model):
    recruiter_id = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    company_website = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)
    contact = models.CharField(max_length=200)
    industry_type = models.ForeignKey(
        tmeta_industry_type, null=True, on_delete=models.CASCADE
    )
    no_of_emp = models.IntegerField(null=True)
    address = models.CharField(max_length=500, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    zipcode = models.CharField(max_length=500, null=True)
    updated_by = models.CharField(max_length=100, null=True)
    logo = models.FileField(null=True, upload_to="company_logo")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    # def save(self, *args, **kwargs):
    # 	super(company_details, self).save(*args, **kwargs)

    # 	img = Image.open(self.logo.path)

    # 	if img.height > 300 or img.width > 300:
    # 		output_size = (300, 300)
    # 		img.thumbnail(output_size)
    # 		img.save(self.logo.path)


class career_page_setting(models.Model):
    recruiter_id = models.ForeignKey(User, on_delete=models.CASCADE)
    page_font = models.CharField(max_length=200, null=True)
    header_font_size = models.IntegerField(null=True)
    header_color = models.CharField(max_length=200, null=True)
    menu_1 = models.CharField(max_length=200, null=True)
    menu_1_url = models.CharField(max_length=200, null=True)
    menu_2 = models.CharField(max_length=200, null=True)
    menu_2_url = models.CharField(max_length=200, null=True)
    menu_3 = models.CharField(max_length=200, null=True)
    menu_3_url = models.CharField(max_length=200, null=True)
    page_font_size = models.IntegerField(null=True)
    banner_img = models.FileField(default="slider1.jpg", upload_to="banner_img")
    banner_header_text = models.CharField(max_length=200, null=True)
    banner_text = models.CharField(max_length=2000, null=True)
    banner_font_size = models.IntegerField(null=True)
    banner_heading_size = models.IntegerField(null=True)
    about_us = models.CharField(max_length=500)
    button_color = models.CharField(max_length=200, null=True)
    footer_color = models.CharField(max_length=200, null=True)
    font_color = models.CharField(max_length=200, null=True)
    updated_by = models.CharField(max_length=100, null=True)
    career_page_url = models.CharField(max_length=200, null=True)


# class StripeCustomer(models.Model):
# 	user = models.OneToOneField(to=User, on_delete=models.CASCADE)
# 	stripeCustomerId = models.CharField(max_length=255)

# 	def __str__(self):
# 		return self.user.username


#### subscriptions releated tables ####
class tmeta_features(models.Model):
    feature_id = models.AutoField(primary_key=True)
    feature_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    inactivated_date = models.DateTimeField(null=True)
    updated_by = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, null=True)


class tmeta_plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=255)
    subscription_value_days = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    currency = models.CharField(max_length=255)
    stripe_id = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    inactived_date = models.DateTimeField(null=True)
    updated_by = models.CharField(max_length=255)


class plan_features(models.Model):
    plan_feature_id = models.AutoField(primary_key=True)
    plan_id = models.ForeignKey("tmeta_plan", on_delete=models.CASCADE)
    feature_id = models.ForeignKey("tmeta_features", on_delete=models.CASCADE)
    feature_value = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class subscriptions(models.Model):
    subscription_id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_id = models.ForeignKey("tmeta_plan", on_delete=models.CASCADE)
    subscription_start_ts = models.DateTimeField(auto_now_add=True)
    subscription_valid_till = models.DateTimeField(null=True)
    subscription_end_ts = models.DateTimeField(null=True)
    # subscription_end_ts  = models.DateTimeField(null=True)
    subscription_changed_date = models.DateTimeField(null=True)
    subscription_changed_to = models.IntegerField(null=True)
    no_of_users = models.IntegerField(null=True)
    subscription_remains_days = models.IntegerField(null=True)
    auto_renewal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    has_client_changed_subscription = models.BooleanField(default=False)
    updated_by = models.CharField(max_length=255)
    grace_period_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class tmeta_addons(models.Model):
    name = models.TextField(null=True)
    currency = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    feature_id = models.ForeignKey(tmeta_features, null=True, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, null=True)
    is_carry = models.BooleanField(default=False, null=True)


class client_features_balance(models.Model):
    client_id = models.ForeignKey(User, on_delete=models.CASCADE)
    feature_id = models.ForeignKey("tmeta_features", on_delete=models.CASCADE)
    available_count = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    add_ons = models.ForeignKey(tmeta_addons, null=True, on_delete=models.CASCADE)
    plan_count = models.IntegerField(null=True)
    addons_count = models.IntegerField(null=True)


class reparsing_count(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    count = models.IntegerField(default=1)


class bulk_matching(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    count = models.IntegerField(default=1)
    is_active = models.BooleanField(default=False)


class candidates_ai_matching(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey(
        "employer_pool", on_delete=models.CASCADE, null=True
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    count = models.IntegerField(default=1)
    is_active = models.BooleanField(default=False)


class addons_plan_features(models.Model):
    plan_id = models.ForeignKey("tmeta_plan", null=True, on_delete=models.CASCADE)
    addon = models.ForeignKey(tmeta_addons, null=True, on_delete=models.CASCADE)
    price = models.IntegerField(null=True)
    value = models.IntegerField(null=True)
    carry_forward = models.BooleanField(default=False)
    stripe_id = models.TextField(null=True)
    content = models.TextField(null=True)


class client_addons_purchase_history(models.Model):
    client_addon_id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(User, on_delete=models.CASCADE)
    feature_id = models.ForeignKey("tmeta_features", on_delete=models.CASCADE)
    purchased_count = models.IntegerField(null=True)
    purchased_date = models.DateField(auto_now_add=True)
    plan_id = models.ForeignKey("tmeta_plan", null=True, on_delete=models.CASCADE)


## Are we maintain the Claim the Coupon By user
class discount_codes_claimed(models.Model):
    client_id = models.ForeignKey(User, on_delete=models.CASCADE)
    discount_id = models.ForeignKey("discounts", on_delete=models.CASCADE,null=True)
    discount_addon = models.ForeignKey("discounts_addon", on_delete=models.CASCADE,null=True)
    subscription_id = models.ForeignKey(
        "subscriptions", on_delete=models.CASCADE, null=True
    )
    is_claimed = models.BooleanField(default=False)
    claimed_date = models.DateTimeField(auto_now_add=True)

### Here Its Discounts For User Only
class discount_user(models.Model):
    client_id = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    discount_id = models.ForeignKey("discounts", on_delete=models.CASCADE,null=True)
    discount_addon = models.ForeignKey("discounts_addon", on_delete=models.CASCADE,null=True)
    is_claimed = models.BooleanField(default=False)
    claimed_date = models.DateTimeField(auto_now_add=True)
    discount_start_date = models.DateTimeField(null=True)
    discount_end_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)

class discounts_features(models.Model):
    discount_id = models.ForeignKey("discounts", on_delete=models.CASCADE,null=True)
    discount_addon = models.ForeignKey("discounts_addon", on_delete=models.CASCADE,null=True)
    addon_id = models.ForeignKey(tmeta_addons, null=True, on_delete=models.CASCADE)
    plan_id = models.ForeignKey("tmeta_plan", null=True, on_delete=models.CASCADE)


## Are we handling the Model for Specific Subscription Coupon Only
class discounts(models.Model):
    discount_id = models.AutoField(primary_key=True)
    plan_id = models.ForeignKey("tmeta_plan", null=True, on_delete=models.CASCADE)
    discount_name = models.CharField(max_length=255)
    discount_code = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=255)
    discount_value = models.IntegerField(default=0)
    discount_currency = models.CharField(max_length=255)
    discount_start_date = models.DateTimeField(null=True)
    discount_end_date = models.DateTimeField(null=True)
    usage_per_client = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    min_amount = models.IntegerField(default=0)
    days = models.IntegerField(default=0)

## Are handling the Model for Specific Addons Coupon Only 
class discounts_addon(models.Model):
    discount_id = models.AutoField(primary_key=True)
    addon_id = models.ForeignKey(tmeta_addons, null=True, on_delete=models.CASCADE)
    plan_id = models.ForeignKey("tmeta_plan", null=True, on_delete=models.CASCADE)
    discount_name = models.CharField(max_length=255)
    discount_code = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=255)
    discount_value = models.IntegerField(default=0)
    discount_currency = models.CharField(max_length=255)
    discount_start_date = models.DateTimeField(null=True)
    discount_end_date = models.DateTimeField(null=True)
    usage_per_client = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    min_amount = models.IntegerField(default=0)
    days = models.IntegerField(default=0)


class zita_talent_sourcing_channels(models.Model):
    ts_channel_id = models.AutoField(primary_key=True)
    ts_channel_name = models.CharField(max_length=255)
    ts_cost_per_talent = models.IntegerField(default=0)


class tmeta_external_jobposting_detail(models.Model):
    ext_jp_site_id = models.AutoField(primary_key=True)
    ext_jp_site_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    applicant_intake_format = models.CharField(max_length=255, null=True)
    added_date = models.DateTimeField(null=True)
    inactivated_date = models.DateTimeField(null=True)
    jobposting_format = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)


class external_jobpostings_by_client(models.Model):
    client_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ext_jp_site_id = models.ForeignKey(
        "tmeta_external_jobposting_detail", on_delete=models.CASCADE
    )
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE)
    posted_on = models.DateTimeField(auto_now_add=True)
    posted_by = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    jobposting_url = models.CharField(max_length=255, null=True)
    job_posting_ref_id = models.CharField(max_length=255, null=True)
    job_inactivated_on = models.DateTimeField(null=True)
    job_inactivated_by = models.CharField(max_length=255, null=True)


class candidate_resume(models.Model):
    file = models.FileField("Document", upload_to="candidate_resume/")
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_parsed = models.BooleanField(default=False)
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    updated_by = models.CharField(max_length=100, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        name = self.file.name.split("/")[1].replace("_", " ").replace("-", " ")
        return name

    def get_absolute_url(self):
        return reverse("jobs:candi_bulk_upload", kwargs={"pk": self.pk})


class pipeline_view(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    emp_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    workflow_id = models.ForeignKey(
        Employee_workflow, on_delete=models.CASCADE, null=True
    )
    # stage_id = models.CharField(max_length=100,null=True)
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=500, null=True)
    stage_order = models.CharField(max_length=100, null=True)
    stage_name = models.CharField(max_length=100, null=True)
    stage_color = models.CharField(max_length=100, null=True)
    stage_length = models.IntegerField(default=0)
    is_disabled = models.BooleanField(default=False)
    email_toggle = models.BooleanField(default=False)


class applicants_status(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status_id = models.ForeignKey(tmeta_jd_candidate_status, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=500, null=True)
    source = models.CharField(max_length=500, null=True)
    stage_id = models.ForeignKey(pipeline_view, on_delete=models.CASCADE, null=True)


class applicants_screening_status(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # status_id = models.ForeignKey(tmeta_jd_candidate_status, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=500, null=True)
    stage_id = models.ForeignKey(pipeline_view, on_delete=models.CASCADE, null=True)


class zita_match_candidates(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status_id = models.ForeignKey(tmeta_jd_candidate_status, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=500, null=True)


class subscriptions_feedback(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    subscription_id = models.ForeignKey(
        "subscriptions", on_delete=models.CASCADE, null=True
    )
    feedback = models.CharField(max_length=500, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class jobs_eeo(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey(Personal_Info, on_delete=models.CASCADE)
    gender = models.CharField(
        max_length=500,
        null=True,
        choices=(
            ("Male", "Male"),
            ("Female", "Female"),
            ("Decline to Self identify", "Decline to Self identify"),
        ),
    )
    hispanic_latino = models.CharField(
        max_length=500,
        null=True,
        choices=(
            ("Yes", "Yes"),
            ("No", "No"),
            ("Decline to Self identify", "Decline to Self identify"),
        ),
    )
    veteran_status = models.CharField(
        max_length=500,
        null=True,
        choices=(
            ("I am not a protected Veteran", "I am not a protected Veteran"),
            (
                "I identify as one or more of the classifications of a protected veteran",
                "I identify as one or more of the classifications of a protected veteran",
            ),
            ("I don`t wish to answer", "I don`t wish to answer"),
        ),
    )
    disability_status = models.CharField(
        max_length=500,
        null=True,
        choices=(
            (
                "Yes, I have a disability or have a history/record of having a disability",
                "Yes, I have a disability or have a history/record of having a disability",
            ),
            (
                "No, I don`t have a disability or a history/record of having a disability",
                "No, I don`t have a disability or a history/record of having a disability",
            ),
            ("I don`t wish to answer", "I don`t wish to answer"),
        ),
    )
    identify_race = models.CharField(max_length=500, null=True)


class email_preference(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stage_id = models.ForeignKey(tmeta_email_preference, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)


class Matched_percentage(models.Model):
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE)
    candidate_id = models.ForeignKey("employer_pool", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True)
    percentage = models.FloatField(max_length=25)
    description = models.TextField(null=True)
    overall_percentage = models.FloatField(max_length=25, null=True)


class whatjob_activity(models.Model):
    jd_id = models.IntegerField(null=True)
    whatjob = models.BooleanField(default=False)


class jd_tech_matching(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    skills = models.IntegerField(default=0)
    roles = models.IntegerField(default=0)
    exp = models.IntegerField(default=0)
    qualification = models.IntegerField(default=0)
    tech_tools = models.IntegerField(default=0)
    soft_skills = models.IntegerField(default=0)
    industry_exp = models.IntegerField(default=0)
    domain_exp = models.IntegerField(default=0)
    certification = models.IntegerField(default=0)
    location = models.IntegerField(default=0)
    cultural_fit = models.IntegerField(default=0)
    ref = models.IntegerField(default=0)


class tmeta_Weightage_Criteria(models.Model):
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Weightage_Matching(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    criteria = models.ForeignKey(tmeta_Weightage_Criteria, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class subscription_content(models.Model):
    plan_id = models.ForeignKey("tmeta_plan", null=True, on_delete=models.CASCADE)
    rich_text_content = models.TextField(null=True)
    subscription_content = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    is_difference = models.TextField(null=True)


class applicant_descriptive(models.Model):
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey(
        "employer_pool", on_delete=models.CASCADE, null=True
    )
    is_active = models.BooleanField(default=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class jd_nice_to_have(models.Model):
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    must_have = models.TextField(null=True)
    nice_to_have = models.TextField(null=True)
    is_active = models.BooleanField(default=False)


class applicants_list(models.Model):
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey(
        "employer_pool", on_delete=models.CASCADE, null=True
    )
    is_active = models.BooleanField(default=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class matching_loader(models.Model):
    jd_id = models.ForeignKey("JD_form", on_delete=models.CASCADE, null=True)
    # candidate_id = models.ForeignKey(
    #     "employer_pool", on_delete=models.CASCADE, null=True
    # )
    is_active = models.BooleanField(default=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    initial_count = models.IntegerField(default=0)
    reduce_count = models.IntegerField(default=0)


class tmete_pages(models.Model):
    description = models.CharField(max_length=255)
    default_value = models.IntegerField(default=0, null=True)


class pagination(models.Model):
    pages = models.IntegerField(null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    page_id = models.ForeignKey("tmete_pages", on_delete=models.CASCADE, null=True)


class tmeta_stages(models.Model):
    stage = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    user_based = models.BooleanField(default=False)


class stages_customization(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stage = models.ForeignKey(tmeta_stages, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_compelted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class pipeline_status(models.Model):
    candidate_id = models.ForeignKey(employer_pool, on_delete=models.CASCADE, null=True)
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stage = models.ForeignKey(tmeta_stages, on_delete=models.CASCADE, null=True)
    pipeline = models.ForeignKey(pipeline_view, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    interview_id = models.ForeignKey(CalEvents, on_delete=models.CASCADE, null=True)
    status_on = models.TextField(null=True)


class candidate_profile_detail(models.Model):
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey(employer_pool, on_delete=models.CASCADE, null=True)
    profile_summary = models.TextField(null=True)


class tmeta_automation_template(models.Model):
    subject = models.TextField(null=True)
    template = models.TextField(null=True)
    template_content = models.TextField(null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True, null=True)
    stage = models.TextField(null=True)
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    stages = models.ForeignKey(pipeline_view, on_delete=models.CASCADE, null=True)


class email_automation_template(models.Model):
    stages = models.ForeignKey(pipeline_view, on_delete=models.CASCADE, null=True)
    templates = models.ForeignKey(
        tmeta_automation_template, on_delete=models.CASCADE, null=True
    )
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    candidate_id = models.ForeignKey(employer_pool, on_delete=models.CASCADE, null=True)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class tour_data(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_first_login = models.BooleanField(null=True)
    skip_id = models.IntegerField(null=True)
    feedback_rating = models.IntegerField(null=True)
    feedback_notes = models.TextField(null=True)
    is_steps = models.BooleanField(null=True)


class template_stage(models.Model):
    stages = models.ForeignKey(pipeline_view, on_delete=models.CASCADE, null=True)
    templates = models.ForeignKey(
        tmeta_message_templates, on_delete=models.CASCADE, null=True
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class tour_feedback(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    feedback_rating = models.IntegerField(null=True)
    feedback_notes = models.TextField(null=True)


class linkedin_data(models.Model):
    linkedin_id = models.IntegerField(null=True)
    sourcing_data = models.TextField(null=True)
    linkedin_source_data = models.TextField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=500, null=True)
    is_unlocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    candidate_id = models.ForeignKey(employer_pool, on_delete=models.CASCADE, null=True)
    resume_file_path = models.TextField(null=True)


class unlocked_candidate(models.Model):
    unlocked_candidate = models.ForeignKey(
        linkedin_data, on_delete=models.CASCADE, null=True
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    email = models.TextField(null=True)
    candidate_id = models.ForeignKey(employer_pool, on_delete=models.CASCADE, null=True)
    resume_file_path = models.TextField(null=True)
    is_active = models.BooleanField(default=False)


# class tmeta_coresignal_data(models.Model):
# 	linkedin_id=models.IntegerField(null=True)
# 	sourcing_data=models.TextField(null=True)
# 	linkedin_source_data=models.TextField(null=True)
# 	created_on = models.DateTimeField(auto_now_add=True)
# 	updated_by = models.CharField(max_length=500, null=True)
# 	is_active = models.BooleanField(default=False)
class jd_message_templates(models.Model):
    name = models.TextField(null=True)
    message = models.ForeignKey(
        tmeta_message_templates, on_delete=models.CASCADE, null=True
    )
    created_on = models.DateField(auto_now_add=True)
    subject = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=False)
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    stage = models.IntegerField(null=True)
    status = models.BooleanField(null=True)
    templates = models.TextField(null=True)
    templates_text = models.TextField(null=True)

    def __str__(self):
        return self.name


class tmeta_email_tags(models.Model):
    name = models.TextField(null=True)
    tag = models.TextField(null=True)
    is_active = models.BooleanField(default=False)
class job_board_list(models.Model):
    name = models.TextField(null=True)
    job_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    job_board_id=models.IntegerField(null=True)
    is_active = models.BooleanField(default=False)


class zita_api_service(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(null=True)
    api_key = models.TextField(null=True)
    email = models.TextField(null=True)

