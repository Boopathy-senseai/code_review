from django import template
from django.conf import settings
import os, re, time
from zita import settings

base_dir = settings.BASE_DIR
import pandas as pd
from django.utils import timezone
import pytz
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import datetime

register = template.Library()


@register.filter
def replace_pipe(string):
    return string.replace("|", ",")


@register.filter
def replace_space(string):
    return string.replace(" ", "-")


@register.filter
def corr_cut(string):
    return string.split("(")[0].strip()


@register.filter
def replace_underline(string):
    if string == "not_set":
        string = "Not Specified"
    return string


@register.filter
def get_item(dictionary):
    for key, value in dictionary.items():
        return key


@register.filter
def price(string):
    if float(string) < float(0):
        return "-$" + str(string.replace("-", ""))
    else:
        return "$" + str(string)


@register.filter
def discount(string):

    return "-$" + str(string.replace("-", ""))


@register.filter
def positive_price(string):

    return "$" + str(string.replace("-", ""))


@register.filter
def word_split(string):
    if string == None:
        return ""

    return string[0]


@register.filter
def work_ex(string):
    if type(string) == int:
        if string == 0:
            string = "Fresher"
        elif string == 1:
            string = str(string) + " Year"
        elif string == None:
            string = "Not Specified"
        else:
            string = str(string) + " Years"
    else:
        if string == None:
            string = "Not Specified"
        elif "year" in string:
            string = string
        elif string == "0":
            string = "Fresher"
        elif string == "1":
            string = string + " Year"
        elif string == "Not Specified":
            string = "Not Specified"
        else:
            string = string + " Years"

    return string


@register.filter
def salary(string):
    if string == None:
        string = "Not Specified"
        return string
    elif "Not Specified" in string:
        string = "Not Specified"
        return string
    else:
        try:
            string = string.split("-")
            return "$" + string[0] + " - $" + string[1].strip()
        except:
            return "$" + string[0]


@register.filter
def replace_relocate(string):
    if string == "not_set":
        string = "Not Specified"
    elif string == "Not Specified":
        return string
    elif string == None:
        return string
    elif string == False:
        string = "No"
    elif str(string) == "0":
        string = "No"
    elif string == True:
        string = "Yes"
    elif str(string) == "1":
        string = "Yes"
    return string


@register.filter
def answer(string):
    if string == False or string == "0":
        string = "No"
    elif string == True or string == "1":
        string = "Yes"
    else:
        string = string
    return string


@register.filter
def exp(string):
    if string == "not_set":
        string = "Not Specified"
    else:
        string = string + " Years"
    return string


@register.filter
def date_parser(string):

    d1 = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")

    return d1


@register.filter
def word_count(string):
    if string == None or len(string) == 0:
        string = 0
    else:
        string = len(string.split(","))
    return string


@register.filter
def yes_or_no(string):
    if string == None:
        string = "No"
    else:
        string = "Yes"
    return string


@register.filter
def active_inactive(string):
    if string == True:
        string = "Active"
    else:
        string = "Inactive"
    return string


@register.filter
def url_mask(string):
    try:
        string = urlsafe_base64_encode(force_bytes(string)).decode()
    except:
        string = urlsafe_base64_encode(force_bytes(string))
    return string


@register.filter
def email(string):
    if "@" in string:  # email
        first, after = string.split("@")
        return "{}*******{}@{}".format(first[0], first[-1], after).lower()
    else:
        return "No email address"


@register.filter
def brackets(string):
    if string == None:
        string = ""
    elif len(string) > 0:
        string = "(" + string + ")"
    return string


@register.filter
def symbol(string):
    if string == "INR":
        string = "₹"
    elif string == "INR (India)":
        string = "₹"
    else:
        string = "$"
    return string


@register.filter
def split_comma(string):
    if string == None:
        string = ""
    else:
        string = string.replace(",", "\n")
    return string


@register.filter
def states_shortform(string):
    try:
        countries_states = pd.read_csv(base_dir + "/" + "media/countries_states.csv")
    except:
        countries_states = pd.read_csv(os.getcwd() + "/" + "media/countries_states.csv")

        for i in range(len(countries_states["state"])):
            state = str(string)
            if countries_states["state"][i].strip() == state.lower().strip():
                state = countries_states["state_code"][i]
                return state


@register.filter
def countries_shortform(string):
    string = str(string)
    if string == "India":
        string = string
    elif string == "United States of America":
        string = "USA"
    elif string == "Canada":
        string = string

    return string


@register.filter
def years(string):
    if string == None or string == 0:
        string = "Fresher"
    elif string == 1 or string == "1":
        string = str(string) + " Year"
    else:
        string = str(string) + " Years"
    return string


@register.filter
def months(string):
    if string == None or string == 0:
        string = ""
    elif string == 1:
        string = str(string) + " Month"
    else:
        string = str(string) + " Months"
    return string


@register.filter
def length_check(string):
    if string == None or len(string) == 0:
        string = "Not Specified"
    return string


@register.filter
def change_role_names(string):
    changed_roles = []
    try:
        roles = string.split(",")
    except:
        roles = string
    for a in roles:
        if a == "Data Analysis":
            changed_roles.append("Data Analyst")
        elif a.strip() == "Machine Learning":
            changed_roles.append("Machine Learning Engineer")
        elif a == "Data Engineering":
            changed_roles.append("Big Data Engineer")
        elif a == "Dev Ops":
            changed_roles.append("Devops Engineer")
        elif a.strip() == "Devops":
            changed_roles.append("Devops Engineer")
        else:
            changed_roles.append(a)

    return (", ").join(changed_roles)


@register.filter
def change_country_name(country):
    if country.strip() == "United States":
        return "United States of America"
    else:
        return country


@register.filter
def validation(string):
    if string == True:
        string = "Validated"
    else:
        string = "Non-Validated"

    return string


@register.filter
def role_match(string):
    if string == None:
        string = "0 %"
    else:
        try:
            # string =int(string)
            string = str(round(string)) + "%"
        except:
            string = str(round(string)) + "%"
    return string


@register.simple_tag
def percentage(string, value):

    skill = int(string) / int(value)
    skill = skill * 100
    return round(skill)


@register.simple_tag
def total_price(data, value):
    total = int(data) * int(value)
    return total


@register.simple_tag
def total(string, value):

    total = string + value
    return total


@register.simple_tag
def z_score(string, skill1, skill2):
    if string == None:
        return string
    profile = string
    skill = int(skill1) / int(skill2) * 100
    z_score = int(profile) + int(skill)
    z_score = z_score / 2
    if z_score % 1 == 0:
        return int(z_score)
    else:
        return z_score


@register.simple_tag
def define(val=None):
    return val


@register.filter
def parseing(string):
    if string == None:
        string = ""
    else:
        string = str(string.split("&")[0]).replace("role=", "").replace("+", " ")
    return string


@register.filter
def skills(string):
    if string == None or len(string) == 0:
        return "Not Specified"
    else:
        string = string.split(",")
        tools = ""
        for i in string[:5]:
            if len(i) > 0 and i != " ":
                tools = tools + '<skill class="skill">' + i + "</skill>"
        if len(string) > 5:
            return tools + '<skill class="skill">...</skill>'
        else:
            return tools


@register.filter
def skills_list(string):
    if string == None or len(string) == 0:
        return "Not Specified"
    else:

        tools = ""
        for i in string[:5]:
            if len(i) > 0 and i != " ":
                tools = tools + '<skill class="skill">' + i + "</skill>"
        if len(string) > 5:
            return tools + '<skill class="skill">...</skill>'
        else:
            return tools


@register.filter
def offer_interview(string):
    if string == None:
        string = 0
    else:
        string = string.split(",")

        string = len(dict.fromkeys(string))
    return string


@register.filter
def li_tag(string):
    if string == None:
        string = ""
    else:
        string = string.split("\n")
        li_tag = ""
        for i in string:
            if len(i) > 0 and i != " ":
                li_tag = li_tag + "<li>" + i + "</li>"
        li_tag = "<ul>" + li_tag + "</ul>"
    return li_tag


@register.filter
def split(string):
    if string == None:
        string = ""
    else:
        string = string.split(" ")[0]
    return string


@register.filter
def https(string):
    if string == None:
        return string
    if string.startswith("http"):
        string = string
    else:
        string = "https://" + string
    return string


@register.filter
def space_comma(string):
    if string == None:
        string = ""
    else:
        string = string.replace(",", ", ")

        # string=len(dict.fromkeys(string))
    return string


@register.filter
def string(string):
    if string == None or len(string) == 0:
        string = ""
    else:
        string = (
            str(string)
            .replace("]", "")
            .replace("[", "")
            .replace("'", "")
            .replace("_", " ")
        )
    changed_roles = []
    roles = string.split(",")
    for a in roles:
        if a.strip() == "Data Analysis":
            changed_roles.append("Data Analyst")
        elif a.strip() == "Machine Learning":
            changed_roles.append("Machine Learning Engineer")
        elif a.strip() == "Data Engineering":
            changed_roles.append("Big Data Engineer")
        elif a.strip() == "Dev Ops":
            changed_roles.append("Devops Engineer")
        elif a.strip() == "Devops":
            changed_roles.append("Devops Engineer")
        else:
            changed_roles.append(a)
    if len(changed_roles) == 2:
        string = (
            '<b style="color:#581845!important;">'
            + changed_roles[0]
            + '</b> and <b style="color:#581845!important;">'
            + changed_roles[1]
            + " </b>"
        )
        return string
    return (" and ").join(changed_roles)


@register.filter
def location_join(string):
    if string == None:
        string = ""
    else:
        string = (", ").join(string)

        # string=len(dict.fromkeys(string))
    return string


@register.filter
def split_country(string):
    if string == None:
        string = ""
    else:
        string = string.split(",")[:2]

        # string=len(dict.fromkeys(string))
    return (", ").join(string)


@register.filter
def type_str(string):
    if type(string) == int:
        string = True
    else:
        string = False

        # string=len(dict.fromkeys(string))
    return string


@register.filter
def type_file(string):
    string = str(string).split(".")[-1]
    return string


@register.filter
def intersted(string):
    if string == True:
        return "Interested"
    else:
        return "Not Interested"


@register.filter
def usa(string):
    if string == "United States of America":
        return "USA"
    else:
        return string

    return string


@register.filter
def int_string(string):

    return int(string)


@register.filter
def li_tag_download(string):
    if string == None:
        string = ""
    else:
        li_tag = ""
        for i in string:
            if len(i) > 0 and i != " ":
                li_tag = li_tag + "<li>" + i + "</li>"
        li_tag = "<ul>" + li_tag + "</ul>"
    return li_tag


@register.filter
def tools_download(string):
    if string == None:
        tools = ""
    else:
        try:
            string = string.split(",")
        except:
            string = string
        tools = ""
        for i in string:
            if len(i) > 0 and i != " ":
                tools = tools + "<strong>" + i + "</strong>"
        # li_tag= '<ul>'+li_tag+'</ul>'
    return tools


def split_str(string):
    if string == None:
        string = ""
    else:
        string = string.split(",")
    return string


@register.filter
def skill_match_download(string):
    if string == None:
        string = ""
    else:
        try:
            string = string.split(",")
        except:
            string = string
        tools = ""
        for i in string:
            if len(i) > 0 and i != " ":
                tools = (
                    tools
                    + '<strong "><i class="fas fa-thumbs-up mr-3	" style="margin-right: 0.4rem;color:green"></i>'
                    + i.capitalize()
                    + "</strong>"
                )
        # li_tag= '<ul>'+li_tag+'</ul>'
    return tools


@register.filter
def skill_non_match_download(string):
    if string == None:
        string = ""
    else:
        try:
            string = string.split(",")
        except:
            string = string
        tools = ""
        for i in string:
            if len(i) > 0 and i != " ":
                tools = (
                    tools
                    + '<strong "><i class="fas fa-thumbs-down mr-3	" style="margin-right: 0.4rem;color:red"></i>'
                    + i.capitalize()
                    + "</strong>"
                )
        # li_tag= '<ul>'+li_tag+'</ul>'
    return tools


@register.filter
def split_tools_download(string):
    if string == None:
        string = ""
    else:
        if len(string) == 1:
            string = string[0].split(",")
        else:
            string = string

        tools = ""
        for i in string:
            if len(i) > 0 and i != " ":
                tools = tools + "<strong>" + i + "</strong>"
        # li_tag= '<ul>'+li_tag+'</ul>'
    return tools


@register.filter
def check_pl(string):
    pl_list = ["Python", "Ruby", "R", "CPP", "Java", "Javascript"]

    if string in pl_list:
        string = "Programming Language(" + string + ")"

    return string


@register.filter
def acp_tools_download(string):
    if string == None:
        string = ""
    else:

        string = string[0].split(",")

        tools = ""
        for i in string:
            if len(i) > 0 and i != " ":
                tools = tools + "<strong>" + i + "</strong>"
        # li_tag= '<ul>'+li_tag+'</ul>'
    return tools


@register.simple_tag(takes_context=True)
def absolutize_path(context, *args):
    relative_url = "".join(args)
    absolute_paths = context.get("absolute_paths", False)
    if absolute_paths:
        if relative_url.startswith("/"):
            relative_url = relative_url[1:]
        return "{}/{}".format(settings.APPS_DIR, relative_url)
    else:
        return relative_url
