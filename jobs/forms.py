from .models import *
from main.models import *
from application.forms import MyModelChoiceField

# from application.models import tmeta_job_type
from django import forms
from django.forms import TextInput
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# roles drop down from meta
# ROLES=[('','---------')]
# ROLES.extend([(i['id'],i['label_name']) for i in list(tmeta_ds_main_roles.objects.filter(is_active=True).values('label_name','id'))])
# # ROLES=tuple(ROLES)

# Currency_type drop down from meta
currency_type = []
user_type = [(1, "User"), (2, "Member"), (3, "Admin")]
# currency_type.extend([(i['id'],i['label_name']) for i in list(tmeta_currency_type.objects.filter(is_active=True).values('id','label_name').order_by('-label_name'))])

# #Type of job drop down from meta
# choices_of_type_of_job=[]
# choices_of_type_of_job.extend([(i['id'],i['label_name']) for i in list(tmeta_job_type.objects.filter(is_active=True).values('id','label_name'))])
currency_l = [("241", "USD")]
# visa_sponsor_l= [('Yes', 'Yes'),('No', 'No')]
font_size_list = [(x, x) for x in range(1, 35)]
font_list = [
    ("Arial", "Arial"),
    ("Helvetica", "Helvetica"),
    ("Verdana", "Verdana"),
    ("Calibri", "Calibri"),
    ("Noto", "Noto"),
    ("Lucida Sans", "Lucida Sans"),
    ("Gill Sans", "Gill Sans"),
    ("Century Gothic", "Century Gothic"),
    ("Candara", "Candara"),
    ("proxima nova alt rg", "proxima nova alt rg"),
    ("Futara", "Futara"),
    ("Franklin Gothic Medium", "Franklin Gothic Medium"),
    ("Trebuchet MS", "Trebuchet MS"),
    ("Geneva", "Geneva"),
    ("Segoe UI", "Segoe UI"),
    ("Optima", "Optima"),
    ("Avanta Garde", "Avanta Garde"),
]


class jd_qualification_form(forms.ModelForm):
    qualification = forms.ChoiceField(
        choices=(
            ("Bachelors", "Bachelors"),
            ("Masters", "Masters"),
            ("Doctorate", "Doctorate"),
        )
    )

    class Meta:
        model = JD_qualification
        fields = ["qualification", "specialization"]


class user_profile_form(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
    )
    last_name = forms.CharField(
        max_length=30,
    )
    username = forms.CharField(
        max_length=30,
    )

    # image = models.ImageField(default='default.jpg', null=True, upload_to='profile_pics')
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["readonly"] = True


class jd_skills_experience_form(forms.ModelForm):
    skill = forms.CharField()

    class Meta:
        model = JD_skills_experience
        fields = ["skill", "experience"]


class interview_scorecard_form(forms.ModelForm):
    class Meta:
        model = interview_scorecard
        fields = ["comments"]


class applicant_cover_letter_form(forms.ModelForm):
    class Meta:
        model = applicant_cover_letter
        fields = ["cover_letter", "source"]

        labels = {
            "cover_letter": "Cover Letter",
        }


class company_details_form(forms.ModelForm):
    email = forms.EmailField()
    company_website = forms.CharField(
        required=False,
    )
    contact = forms.CharField(
        required=False,
    )
    address = forms.CharField(
        required=False,
    )
    no_of_emp = forms.FloatField(
        required=False,
    )
    zipcode = forms.CharField(
        required=False,
    )
    logo = forms.FileField(required=False)

    class Meta:
        model = company_details
        fields = [
            "company_name",
            "company_website",
            "email",
            "address",
            "contact",
            "industry_type",
            "no_of_emp",
            "country",
            "state",
            "city",
            "zipcode",
            "logo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # super().__init__(*args, **kwargs)
        unused_files = Country.objects.all()
        self.fields["country"].queryset = unused_files
        self.fields["country"].empty_label = None
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["company_name"].widget.attrs["readonly"] = True
        # self.fields['contact'].widget.attrs['readonly'] = True
        self.fields["country"].initial = (Country.objects.get(id=231).pk,)
        self.fields["state"].queryset = State.objects.filter(country_id=231)
        if "country" in self.data:
            try:
                country_id = int(self.data.get("country"))
                self.fields["state"].queryset = State.objects.filter(
                    country_id=country_id
                ).order_by("name")
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            try:
                self.fields["state"].queryset = (
                    self.instance.country.state_set.order_by("name")
                )
            except:
                self.fields["state"].queryset = State.objects.filter(country_id=231)

        else:
            pass

        self.fields["city"].queryset = City.objects.none()
        if "state" in self.data:
            try:
                state_id = int(self.data.get("state"))
                self.fields["city"].queryset = City.objects.filter(
                    state_id=state_id
                ).order_by("name")
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            try:
                self.fields["city"].queryset = self.instance.state.city_set.order_by(
                    "name"
                )
            except:
                self.fields["city"].queryset = City.objects.none()
        else:
            pass


class jd_locations_form(forms.ModelForm):
    class Meta:
        model = JD_locations
        fields = ["country", "state", "city"]


class jobs_eeo_form(forms.ModelForm):
    class Meta:
        model = jobs_eeo
        fields = ["gender", "hispanic_latino", "veteran_status", "disability_status"]


class career_page_setting_form(forms.ModelForm):
    about_us = forms.CharField(
        min_length=150,
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    banner_text = forms.CharField(
        min_length=150,
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    page_font = forms.ChoiceField(choices=font_list, required=False)
    header_font_size = forms.ChoiceField(choices=font_size_list, required=False)
    header_color = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "eg: #255684 or red"}),
        required=False,
    )
    page_font_size = forms.ChoiceField(choices=font_size_list, required=False)
    banner_img = forms.FileField(required=False)
    banner_header_text = forms.CharField(
        max_length=100, widget=forms.TextInput(), required=False
    )
    menu_1 = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "eg: About Us, Contact..."}),
        required=False,
    )
    menu_1_url = forms.CharField(
        widget=forms.URLInput(attrs={"placeholder": "eg: https://example.com/"}),
        required=False,
    )
    menu_2 = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "eg: About Us, Contact..."}),
        required=False,
    )
    menu_2_url = forms.CharField(
        widget=forms.URLInput(attrs={"placeholder": "eg: https://example.com/"}),
        required=False,
    )
    menu_3 = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "eg: About Us, Contact..."}),
        required=False,
    )
    menu_3_url = forms.CharField(
        widget=forms.URLInput(attrs={"placeholder": "eg: https://example.com/"}),
        required=False,
    )
    banner_font_size = forms.ChoiceField(choices=font_size_list, required=False)
    banner_heading_size = forms.CharField(required=False)
    button_color = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "eg: #255684 or red"}),
        required=False,
    )
    font_color = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "eg: #255684 or red"}),
        required=False,
    )
    footer_color = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "eg: #255684 or red"}),
        required=False,
    )
    career_page_url = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "company name"}), required=False
    )

    class Meta:
        model = career_page_setting
        fields = [
            "page_font",
            "header_font_size",
            "header_color",
            "page_font_size",
            "banner_img",
            "menu_1",
            "menu_1_url",
            "menu_2",
            "menu_2_url",
            "menu_3",
            "menu_3_url",
            "banner_header_text",
            "banner_text",
            "banner_font_size",
            "about_us",
            "career_page_url",
            "button_color",
            "footer_color",
            "banner_heading_size",
            "font_color",
        ]


class jd_form(forms.ModelForm):

    salary_curr_type = forms.ChoiceField(choices=currency_l)
    show_sal_to_candidate = forms.ChoiceField(
        widget=forms.CheckboxInput, required=False
    )
    job_type = MyModelChoiceField(
        queryset=tmeta_job_type.objects.filter(is_active=True)
    )
    visa_sponsor = forms.ChoiceField(choices=((True, "Yes"), (False, "No")))
    job_id = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={"onkeypress": "return event.charCode!=32"}),
    )
    richtext_job_description = forms.CharField(
        min_length=150, required=True, widget=forms.Textarea(attrs={"rows": 30})
    )
    tech_req = forms.CharField(min_length=150, widget=forms.Textarea(attrs={"rows": 5}))
    salary_min = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "type": "number",
                "min": "1000",
                "max": "9000000",
                "onkeypress": "return event.charCode >= 48 && event.charCode <= 57",
            }
        )
    )
    salary_max = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "type": "number",
                "min": "1000",
                "max": "9000000",
                "onkeypress": "return event.charCode >= 48 && event.charCode <= 57",
            }
        )
    )
    min_exp = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "type": "number",
                "onkeypress": "return event.charCode != 43 && event.charCode != 45 && event.which!=17",
            }
        )
    )
    max_exp = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "type": "number",
                "onkeypress": "return event.charCode != 43 && event.charCode != 45 && event.which!=17",
            }
        )
    )

    non_tech_req = forms.CharField(
        max_length=3000,
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "ex., Other requirements like:\nStrong communication skills and team collaboration.\nStrong problem solving and troubleshooting skills.",
            }
        ),
    )

    class Meta:
        model = JD_form
        fields = [
            "job_title",
            "job_id",
            "visa_sponsor",
            "no_of_vacancies",
            "job_role",
            "min_exp",
            "max_exp",
            "work_remote",
            "role_res",
            "salary_min",
            "salary_max",
            "salary_curr_type",
            "show_sal_to_candidate",
            "tech_req",
            "non_tech_req",
            "job_type",
            "job_description",
            "richtext_job_description",
            "industry_type",
        ]

    # def clean_job_id(self):
    # 	# Get the email
    # 	job_id = self.cleaned_data.get('job_id')

    # 	# Check to see if any users already exist with this email as a username.
    # 	if JD_form.objects.filter(job_id=job_id).exists():
    # 		raise forms.ValidationError('This job_id address is already in use.')
    # 	else:
    # 		return job_id

    def __init__(self, *args, **kwargs):
        super(jd_form, self).__init__(*args, **kwargs)  # Call to ModelForm constructor
        self.fields["job_role"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px;border-color:light-dark;height:30px;-webkit-appearance: menulist;"
        self.fields["industry_type"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px;border-color:light-dark;height:30px;-webkit-appearance: menulist;"
        self.fields["job_title"].widget.attrs["style"] = "width:100%;padding-left:8px"
        self.fields["job_id"].widget.attrs["style"] = "width:100%;padding-left:8px"
        self.fields["job_id"].widget.attrs["placeholder"] = "GV_DA_001"
        self.fields["job_type"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px;height:30px;-webkit-appearance: menulist"
        # self.fields['org_info'].widget.attrs['style']  = 'width:100%;padding-left:8px'
        self.fields["richtext_job_description"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px"
        self.fields["tech_req"].widget.attrs["style"] = "width:100%;padding-left:8px"
        # self.fields['add_info'].widget.attrs['style']  = 'width:100%;padding-left:8px'
        self.fields["min_exp"].widget.attrs["style"] = "width:100%;padding-left:8px"
        self.fields["max_exp"].widget.attrs["style"] = "width:100%;padding-left:8px"
        self.fields["salary_min"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px;height:30px"
        self.fields["no_of_vacancies"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px"
        self.fields["salary_max"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px;height:30px"
        self.fields["visa_sponsor"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px;height:30px;-webkit-appearance: menulist"
        self.fields["salary_curr_type"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px;height:30px;-webkit-appearance: menulist"
        self.fields["non_tech_req"].widget.attrs[
            "style"
        ] = "width:100%;padding-left:8px"
        self.fields["richtext_job_description"].widget.attrs["wrap"] = "soft"
        self.fields["richtext_job_description"].widget.attrs["rows"] = 30
        # self.fields['org_info'].widget.attrs['rows']  = 5
        # self.fields['org_info'].required = False
        self.fields["non_tech_req"].widget.attrs["rows"] = 5
        self.fields["tech_req"].widget.attrs["rows"] = 5
        # self.fields['add_info'].widget.attrs['rows']  = 5
        # self.fields['add_info'].widget.attrs['maxlength']  = 5000
        # self.fields['org_info'].widget.attrs['maxlength']  = 5000
        # self.fields['add_info'].widget.attrs['placeholder']='(ex., Local employment regulation specific statements, if applicable).';
        self.fields["non_tech_req"].widget.attrs["wrap"] = "soft"
        self.fields["tech_req"].widget.attrs["wrap"] = "soft"
        # self.fields['add_info'].widget.attrs['wrap']  = 'soft'
        # self.fields['org_info'].widget.attrs['wrap']  = 'soft'


class Upload_jd(forms.ModelForm):
    class Meta:
        model = JDfiles
        fields = ["jd_file"]


class Application_Form(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    location = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    contact = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    linkedin_url = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"})
    )

    # class Meta:
    # 	model = application_form
    # 	fields = ['first_name','last_name','email','location','contact','linkedin_url','cv_file']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['firstname'].widget.attrs['readonly'] = True
        # self.fields['lastname'].widget.attrs['readonly'] = True
        self.fields["first_name"].widget.attrs["readonly"] = True
        self.fields["last_name"].widget.attrs["readonly"] = True
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["location"].widget.attrs["readonly"] = True
        self.fields["contact"].widget.attrs["readonly"] = True
        self.fields["linkedin_url"].widget.attrs["readonly"] = True


class Candidates_notes_form(forms.ModelForm):
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Add your notes here..."})
    )

    class Meta:
        model = Candidate_notes
        fields = ["notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].label = ""


class Missing_Skill_Form(forms.ModelForm):
    class Meta:
        model = Missing_Skills_Table
        fields = (
            "missingskill_mand",
            "missingskill_pl",
            "missingskill_db",
            "missingskill_tl",
            "missingskill_pf",
            "missingskill_ot",
        )


# class billing_address_form(forms.ModelForm):
# 	class Meta:
# 		model= billing_address
# 		fields= ('first_name',
# 'last_name',
# 'email',
# 'alternative_email',
# 'contact_no',
# 'company_name',
# 'address_1',
# 'address_2',
# 'city',
# 'state',
# 'country',
# 'zipcode',
# 			)


class user_creation_form(forms.ModelForm):
    permission = forms.ChoiceField(choices=user_type)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["last_name"].required = True
        self.fields["first_name"].required = True
        self.fields["email"].required = True
        self.fields["username"].help_text = None


class UploadFileForm(forms.Form):

    file = forms.FileField()
