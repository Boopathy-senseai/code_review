from jobs.models import *
from application.models import *
from main.models import *
import django_filters
from django_filters.filters import Filter
from django_filters.fields import Lookup

STATUS = [("1", "Active"), ("2", "Draft"), ("4", "Inactive")]

Notice_l = [
    ("1", "Immediate"),
    ("2", "In a Month"),
    ("3", "Within 3 Months"),
    ("4", "More than 3 Months"),
    ("5", "Unavailable"),
]

type_of_job_l = (
    ("1", "Full Time"),
    ("2", "Part Time"),
    ("3", "Contract"),
    ("4", "Internship"),
    ("5", "Full Time or Part Time"),
)

country_auth_l = (("IN", "India"), ("CA", "Canada"), ("US", "United States"))

validator_l = (
    ("1", "Validated Candidates (Yes)"),
    ("0", "Non-Validated Candidates (No)"),
)

PROCESS = (
    ("8", "Telephone Screen"),
    ("10", "Tele Interview"),
    ("11", "In-Person Interview"),
    ("4", "Offer"),
    ("12", "On-board"),
)

role_l = [
    ("", "Select a role"),
    ("Data Analyst", "Data Analyst"),
    ("Big Data Engineer", "Big Data Engineer"),
    ("Machine Learning Engineer", "Machine Learning Engineer"),
    ("Business Intelligence", "Business Intelligence"),
    ("Devops Engineer", "Devops Engineer"),
]
role_ld = [
    ("1", "Data Analyst"),
    ("3", "Big Data Engineer"),
    ("2", "Machine Learning Engineer"),
    ("4", "Business Intelligence"),
    ("5", "Devops Engineer"),
]
role_ld_2 = [
    ("1", "Data Analyst"),
    ("3", "Big Data Engineer"),
    ("2", "Machine Learning Engineer"),
    ("4", "Business Intelligence"),
    ("5", "Devops Engineer"),
    ("6", "Others"),
]

role_l2 = [
    ("Data Analyst", "Data Analyst"),
    ("Big Data Engineer", "Big Data Engineer"),
    ("Machine Learning Engineer", "Machine Learning Engineer"),
    ("Business Intelligence", "Business Intelligence"),
    ("Devops Engineer", "Devops Engineer"),
]
TYPE_CHOICES = (
    (0, "0"),
    (1, "1"),
)

# roles drop down from meta
# ROLES=[('','---------')]
# ROLES.extend([(i['id'],i['job_title']) for i in list(.values('job_title','id'))])

# class My_database_filter(django_filters.FilterSet):


# 	class Meta:
# 		model = employer_pool

# 		fields = ['job_type''work_exp''relocate''qualification''skills']


class JobFilter(django_filters.FilterSet):

    location = django_filters.CharFilter(lookup_expr="icontains", field_name="location")
    job_id = django_filters.CharFilter(lookup_expr="icontains", field_name="job_id")
    job_title = django_filters.CharFilter(lookup_expr="icontains")
    # jd_status=django_filters.ChoiceFilter(choices = STATUS,empty_label='All' )

    class Meta:
        model = JD_form

        fields = ["job_title", "jd_status"]


class Career_filter(django_filters.FilterSet):
    job_location = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"placeholder": "Location", "class": "search-box_search_input"}
        ),
    )
    job_title = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"placeholder": "Job Title", "class": "search-box_search_input"}
        ),
    )
    job_role = django_filters.ChoiceFilter(
        choices=role_ld_2,
        widget=forms.Select(
            attrs={
                "placeholder": "Job Title",
                "class": "dropdown_item_select search-box_search_input",
            }
        ),
    )

    class Meta:
        model = JD_form
        fields = ["job_title", "job_role"]


class CandidateFilter(django_filters.FilterSet):

    available_to_start = django_filters.ChoiceFilter(choices=Notice_l)
    type_of_job = django_filters.ChoiceFilter(choices=type_of_job_l)
    validation = django_filters.ChoiceFilter(choices=validator_l)
    profile_match = django_filters.RangeFilter(field_name="profile_match")
    # skill_match = django_filters.CharFilter(lookup_expr='icontains',field_name='can_skill')
    total_exp_year = django_filters.RangeFilter(field_name="exp_year")

    class Meta:
        model = Additional_Details

        fields = ["total_exp_year"]


class Zita_Match_Filter(django_filters.FilterSet):

    # available_to_start = django_filters.ChoiceFilter(choices =Notice_l )
    # type_of_job = django_filters.ChoiceFilter(choices = type_of_job_l)
    # validation = django_filters.ChoiceFilter(choices = validator_l,field_name='validation')
    # country_auth = django_filters.ChoiceFilter(choices = country_auth_l,lookup_expr='icontains')
    profile_match = django_filters.RangeFilter(field_name="match")
    # relocate = django_filters.BooleanFilter(widget=forms.CheckboxInput)
    total_exp_year = django_filters.RangeFilter(field_name="total_exp")

    class Meta:
        model = Additional_Details

        fields = ["total_exp_year"]


class HiringFilter(django_filters.FilterSet):

    job_title = django_filters.CharFilter(
        lookup_expr="icontains", field_name="job_title"
    )
    job_location = django_filters.CharFilter(
        lookup_expr="icontains", field_name="applied_location"
    )
    job_id = django_filters.CharFilter(lookup_expr="icontains", field_name="job_id")
    candidate_name = django_filters.CharFilter(
        lookup_expr="icontains", field_name="candidate_name"
    )
    process_status = django_filters.ChoiceFilter(
        choices=PROCESS, field_name="process_status", lookup_expr="icontains"
    )

    class Meta:
        model = JD_form

        fields = ["job_title", "job_id"]


class InterestedCandFilters(django_filters.FilterSet):
    role = django_filters.ChoiceFilter(
        choices=role_l2, field_name="shortlisted_role_name", lookup_expr="icontains"
    )
    available_to_start = django_filters.ChoiceFilter(
        choices=Notice_l, field_name="availability"
    )
    type_of_job = django_filters.ChoiceFilter(
        choices=type_of_job_l, field_name="type_of_job"
    )
    validation = django_filters.ChoiceFilter(
        choices=validator_l, field_name="validation"
    )
    total_exp_year = django_filters.RangeFilter(field_name="total_exp")
    # skill_match = django_filters.CharFilter(lookup_expr='icontains',field_name='tech_skill')
    country_auth = django_filters.ChoiceFilter(
        choices=country_auth_l, lookup_expr="icontains"
    )
    location = django_filters.CharFilter(lookup_expr="icontains", field_name="location")

    class Meta:
        model = User_Info

        fields = ["selected_role"]


# class ListFilter(Filter):
#     def filter(self, queryset, value):
#         try:
#             request = self.parent.request
#         except AttributeError:
#             return None
#         values = request.GET.getlist(self.name)
#         values = {int(item) for item in values}

#         return super(ListFilter, self).filter(queryset, Lookup(values, 'in'))


class ListFilter(Filter):
    def filter(self, qs, value):
        try:
            value_list = value.split(",")
        except:
            value_list = [" "]
        return super(ListFilter, self).filter(qs, Lookup(value_list, "in"))


class SearchFilters(django_filters.FilterSet):
    role = django_filters.ChoiceFilter(
        choices=role_l,
        required=True,
        field_name="role",
        lookup_expr="icontains",
        empty_label=None,
    )
    available_to_start = django_filters.ChoiceFilter(
        choices=Notice_l, field_name="available_to_start_id"
    )
    type_of_job = django_filters.ChoiceFilter(
        choices=type_of_job_l, field_name="type_of_job"
    )
    validation = django_filters.ChoiceFilter(
        choices=validator_l, field_name="validation"
    )
    total_exp_year = django_filters.RangeFilter(field_name="total_exp")
    # skill_match = django_filters.MultipleChoiceFilter(field_name='tech_skill')
    location = django_filters.CharFilter(lookup_expr="icontains", field_name="location")
    country_auth = django_filters.ChoiceFilter(
        choices=country_auth_l, lookup_expr="icontains"
    )

    class Meta:
        model = User_Info

        fields = ["selected_role"]

    # def __init__(self, *args, **kwargs):
    # 	super(SearchFilters, self).__init__(*args, **kwargs) # Call to ModelForm constructor
    # 	self.filters['role'].field.widget.attrs['style'] = 'width:222px;'
    # 	self.filters['validation'].field.widget.attrs['style'] = 'width:222px;'


class SearchFilters2(django_filters.FilterSet):
    role = django_filters.ChoiceFilter(
        choices=role_l,
        required=True,
        field_name="role",
        lookup_expr="icontains",
        empty_label=None,
    )
    available_to_start = django_filters.ChoiceFilter(
        choices=Notice_l, field_name="available_to_start_id"
    )
    type_of_job = django_filters.ChoiceFilter(
        choices=type_of_job_l, field_name="type_of_job"
    )
    validation = django_filters.ChoiceFilter(
        choices=validator_l, field_name="validation"
    )
    total_exp_year = django_filters.RangeFilter(field_name="total_exp")
    country_auth = django_filters.ChoiceFilter(
        choices=country_auth_l, lookup_expr="icontains"
    )

    # skill_match = django_filters.MultipleChoiceFilter(choices=field_name='tech_skill',conjoined=True)
    class Meta:
        model = User_Info

        fields = ["selected_role"]
