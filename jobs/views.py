from django.shortcuts import render, redirect

# from pyresparser import ResumeParser


from jobs.parsing import Matching_AI, get_qualification, resume_parser_AI
from schedule_event.views import *
from .forms import *
from .models import *
from main.models import *
from payment.models import *
from django.views.generic.base import TemplateView
from application.models import *

# from usecase.models import *
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseNotModified, HttpResponseRedirect
import json
from django.contrib.auth import login, authenticate, logout
import os, re, time
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from media.candidate_matcher.candidate_matcher2 import candidate_matcher,search_matcher
from django.contrib.auth.decorators import login_required
import datetime
from login.decorators import *
import requests
from django.db.models import *
from jobs.filters import *
from login.models import *
from users.models import *
from calendarapp.models import *

global countries_to_be_displayed
countries_to_be_displayed = [
    "USA"
]  # if we need to add more countries, the text should be same as the meta of country table in application
from zita.settings import (
    matching_api_url,
    matching_auth_token,
    matching_application_jd_endpoint,
)

global base_dir
from datetime import timedelta, datetime
from zita import settings

base_dir = settings.BASE_DIR
from django.db.models import Aggregate, CharField, Value
from django.core.exceptions import FieldError
from django.db.models.expressions import Subquery
from django.utils import timezone
import pytz
from collections import Counter

# import pdfkit
from jobs.candidate_data import get_app_prof_details
import logging

# logging.basicConfig(level=logging.INFO)
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from collections.abc import Iterable
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

# import xhtml2pdf.pisa as pisa
from django.views.generic import View
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

email_main = settings.EMAIL_HOST_USER
EMAIL_TO = settings.EMAIL_TO
# from main.views import mail_notification,logo_data
from django.views.decorators.cache import never_cache
import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

# from matplotlib_venn import venn2
import numpy as np
import pandas as pd
from django.http import HttpResponse
from django.template.loader import render_to_string

try:
    from weasyprint import HTML
except:
    pass
from django.http.response import (
    JsonResponse,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotModified,
)
from django.urls import reverse
from random import choice
from string import ascii_lowercase, digits
import time
import ast
import base64
import xmltodict
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from math import pi
import tempfile
import zipfile
import socket

# from scipy.interpolate import interp1d
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("jobs")
import operator
from django.db.models import Q
from functools import reduce
import requests
import json
from requests.auth import HTTPBasicAuth
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.models import Permission
from users.models import UserHasComapny, CompanyHasInvite, UserDetail
from rest_framework.decorators import api_view
from knox.models import AuthToken
from jobs.parsing import *
from django.contrib.staticfiles import finders
from email.mime.image import MIMEImage


def logo_data(img):
    # image_data =['facebook.png','twitter.png','linkedin.png','youtube.png','new_zita.png']
    with open(finders.find("images/" + img), "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", img)
    return logo


def user_management(request):
    try:
        company = company_details.objects.get(recruiter_id=request.user)
        token = AuthToken.objects.create(request.user)[1]
        url = settings.CLIENT_URL + "?t=" + token
        return redirect(url)
    except company_details.DoesNotExist:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})


# Random username and password creation
def generate_random_username(
    length=8, chars=ascii_lowercase + digits, split=4, delimiter="_"
):

    username = "".join([choice(chars) for i in range(length)])

    if split:
        username = delimiter.join(
            [
                username[start : start + split]
                for start in range(0, len(username), split)
            ]
        )

    try:
        User.objects.get(username=username)
        return generate_random_username(
            length=length, chars=chars, split=split, delimiter=delimiter
        )
    except User.DoesNotExist:
        return username


# User Permission Check function
def user_permission(request, page=None):
    user = request.user
    if company_details.objects.filter(recruiter_id=user).exists():
        return True
    if Permission.objects.filter(user=user, codename=page).exists():
        return True
    else:
        return False


# User admin user check function
def admin_account(request):
    try:
        user = request.user
        if user.last_name:
            updated_by = request.user.first_name + " " + request.user.last_name
        else:
            updated_by = request.user.first_name
        if company_details.objects.filter(recruiter_id=user).exists():
            return user, updated_by
        else:
            admin = UserHasComapny.objects.get(user=user).company
            return admin.recruiter_id, updated_by
    except Exception as e:
        user = request
        if user.last_name:
            updated_by = user.first_name + " " + user.last_name
        else:
            updated_by = user.first_name
        if company_details.objects.filter(recruiter_id=user).exists():
            return user, updated_by
        else:
            admin = UserHasComapny.objects.get(user=user).company
            return admin.recruiter_id, updated_by


def mail_notification(
    user_id,
    template,
    message,
    jd_id=None,
    count=None,
    can_id=None,
    code=None,
    company_name=None,
    domain="",
):
    try:
        user = User_Info.objects.get(user_id=user_id)
    except:
        user = user_id
    htmly = get_template("email_templates/" + template)
    if code != None:
        subject, from_email, to = message, email_main, user.email
        html_content = htmly.render(
            {"user": user, "domain": domain, "code": code, "company_name": company_name}
        )
    elif jd_id == None:
        subject, from_email, to = message, email_main, user.email
        html_content = htmly.render(
            {"user": user, "domain": domain, "company_name": company_name}
        )
    else:
        if can_id == None:
            subject, from_email, to = message, email_main, user.email
            jd_form = JD_form.objects.get(id=jd_id)
            html_content = htmly.render(
                {
                    "user": user,
                    "domain": domain,
                    "jd_form": jd_form,
                    "count": count,
                }
            )
        else:
            jd_form = JD_form.objects.get(id=jd_id)
            count = (
                jd_candidate_analytics.objects.filter(jd_id=jd_id, status_id_id=1)
                .values("candidate_id_id")
                .distinct()
                .count()
            )
            subject, from_email, to = message, email_main, jd_form.user_id.email
            can_id = Personal_Info.objects.get(application_id=can_id)
            html_content = htmly.render(
                {
                    "user": jd_form.user_id,
                    "domain": domain,
                    "jd_form": jd_form,
                    "count": count,
                    "can_id": can_id,
                }
            )
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = "related"
    image_data = ["twitter.png", "linkedin.png", "youtube.png", "new_zita_white.png"]
    for i in image_data:
        msg.attach(logo_data(i))

    try:
        msg.send()
    except:
        pass


def validate_job_id(request):
    user_id, updated_by = admin_account(request)
    job_id = request.GET.get("job_id_val", None)
    jd_id = request.GET.get("jd_id", None)
    data = {"is_taken": JD_form.objects.filter(user_id=user_id, job_id=job_id).exists()}
    return JsonResponse(data)


def flatten(lis):
    for item in lis:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in flatten(item):
                yield x.lower().strip()
        else:
            yield item.lower().strip()


class Concats(Aggregate):
    function = "GROUP_CONCAT"
    template = "%(function)s(%(distinct)s%(expressions)s)"

    def __init__(self, expression, distinct=False, **extra):
        super(Concats, self).__init__(
            expression,
            distinct="DISTINCT " if distinct else "",
            output_field=CharField(),
            **extra,
        )


def feedback_form(request, pk=None):

    if request.method == "POST":
        if not "rating" in request.POST:
            rating = 0
        else:
            rating = request.POST["rating"]
        user = JD_form.objects.get(id=pk)
        Feedback_form.objects.create(
            user_id=user.user_id,
            name=user.user_id.first_name,
            jd_id=user,
            rating=rating,
            email=user.user_id.email,
            comments=request.POST["comments"],
        )
        return HttpResponseNotModified()

    return render(request, "jobs/feedback.html")


# This function is to list the jobs posted by the user in job listing page.
@login_required
@recruiter_required
def create_job_listing(request, **kwargs):

    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass

    #  page permission check function

    admin_id, updated_by = admin_account(request)
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    user = User.objects.get(username=request.user).id
    logger.info("In create_job_listing function - User ID: " + str(user))
    jd_list = JD_form.objects.filter(user_id=admin_id)
    jd_ids = jd_list.filter(jd_status_id=1).values_list("id", flat=True).distinct()
    for i in jd_ids:

        try:
            # result=matching_api_to_db(request,jd_id=i,can_id=None)
            pass
        except Exception as e:
            pass
    title = list(jd_list.values_list("job_title", flat=True).distinct())
    job_ids = list(jd_list.values_list("job_id", flat=True).distinct())
    location = JD_locations.objects.filter(
        jd_id__in=jd_list.values_list("id", flat=True).distinct()
    )
    location = location.annotate(
        countries=Subquery(
            Country.objects.filter(id=OuterRef("country"))[:1].values("name")
        ),
        states=Subquery(State.objects.filter(id=OuterRef("state"))[:1].values("name")),
        cities=Subquery(City.objects.filter(id=OuterRef("city"))[:1].values("name")),
    )
    location = location.annotate(
        loc=Concat(
            "cities", V(", "), "states", V(", "), "countries", output_field=CharField()
        )
    )

    Jobs_List = 0
    if jd_list.exists():
        Jobs_List = 1

    location_list = list(
        location.values_list("loc", flat=True).exclude(loc__isnull=True).distinct()
    )
    job_title = list(jd_list.values_list("job_title", flat=True).distinct())
    filters = JobFilter(request.GET, queryset=jd_list)

    context = {
        "filters": filters,
        "Jobs_List": Jobs_List,
        "permission": permission,
        "location_list": json.dumps(location_list, cls=DjangoJSONEncoder),
        "job_ids": json.dumps(job_ids, cls=DjangoJSONEncoder),
        "job_title": json.dumps(job_title, cls=DjangoJSONEncoder),
    }

    return render(request, "jobs/jobs_listing.html", context)


def create_job_listing_ajax(request):
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    user = User.objects.get(username=request.user).id
    logger.info("In create_job_listing function - User ID: " + str(user))
    admin_id, updated_by = admin_account(request)
    jd_list = JD_form.objects.filter(user_id=admin_id)
    jd_ids = jd_list.values_list("id", flat=True).distinct()
    location = JD_locations.objects.filter(
        jd_id__in=jd_list.values_list("id", flat=True).distinct()
    )
    location = location.annotate(
        countries=Subquery(
            Country.objects.filter(id=OuterRef("country"))[:1].values("name")
        ),
        states=Subquery(State.objects.filter(id=OuterRef("state"))[:1].values("name")),
        cities=Subquery(City.objects.filter(id=OuterRef("city"))[:1].values("name")),
    )
    location = location.annotate(
        loc=Concat(
            "cities", V(", "), "states", V(", "), "countries", output_field=CharField()
        )
    )
    try:
        career_page_url = career_page_setting.objects.get(
            recruiter_id=admin_id
        ).career_page_url
    except:
        career_page_url = None

    Jobs_List = 0
    if jd_list.exists():
        Jobs_List = 1
    jd_list = jd_list.annotate(
        applicant=Subquery(
            applicants_status.objects.filter(
                jd_id=OuterRef("id"), status_id_id__in=[1, 2, 3, 4, 7]
            )
            .values("client_id")
            .annotate(name=Concats("id"))[:1]
            .values("name")
        ),
        selected=Subquery(
            applicants_status.objects.filter(jd_id=OuterRef("id"), status_id_id=4)
            .values("client_id")
            .annotate(name=Concats("id"))[:1]
            .values("name")
        ),
        rejected=Subquery(
            applicants_status.objects.filter(jd_id=OuterRef("id"), status_id_id=7)
            .values("client_id")
            .annotate(name=Concats("id"))[:1]
            .values("name")
        ),
        shortlisted=Subquery(
            applicants_status.objects.filter(jd_id=OuterRef("id"), status_id_id=2)
            .values("client_id")
            .annotate(name=Concats("id"))[:1]
            .values("name")
        ),
        location_jd=Subquery(
            location.filter(jd_id=OuterRef("id"))
            .values("jd_id")
            .annotate(name=Concats("state"))
            .values("name")[:1]
        ),
        views=Subquery(
            jd_candidate_analytics.objects.filter(jd_id=OuterRef("id"), status_id=6)
            .values("status_id")
            .annotate(cout=Count("candidate_id"))[:1]
            .values("cout")
        ),
        invite_to_apply=Subquery(
            Candi_invite_to_apply.objects.filter(jd_id=OuterRef("id"))
            .values("jd_id")
            .annotate(name=Concats("candidate_id"))[:1]
            .values("name")
        ),
        interested=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id=OuterRef("id"), status_id=5
            ).values("interested")[:1]
        ),
        plan=Subquery(
            recuriter_job_posting_plan.objects.filter(
                jd_id=OuterRef("id"), is_active=True
            ).values("plan_id__label_name")[:1]
        ),
        plan_id=Subquery(
            recuriter_job_posting_plan.objects.filter(
                jd_id=OuterRef("id"), is_active=True
            ).values("plan_id")[:1]
        ),
        available_days=Subquery(
            recuriter_job_posting_plan.objects.filter(
                jd_id=OuterRef("id"), is_active=True
            ).values("available_days")[:1]
        ),
        location=Subquery(
            location.filter(jd_id=OuterRef("id"))
            .values("jd_id")
            .annotate(name=Concats("loc"))[:1]
            .values("name"),
            output_field=CharField(),
        ),
        profile_match=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("id"))[:1].values(
                "recommended_role_id__label_name"
            )
        ),
        job_posted_on_date=Case(
            When(job_reposted_on__isnull=False, then="job_reposted_on"),
            default=F("job_posted_on"),
        ),
    ).order_by("-job_posted_on_date")

    jd_list = jd_list.annotate(
        zita_match=Subquery(
            zita_match_candidates.objects.filter(
                status_id_id=5,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
                jd_id=OuterRef("id"),
            )
            .values("status_id")
            .annotate(cout=Count("candidate_id"))[:1]
            .values("cout"),
            output_field=CharField(),
        ),
    )
    zita_count = []
    for jd_id in jd_ids:
        jd_states = JD_locations.objects.filter(jd_id=jd_id).values_list(
            "state_id", flat=True
        )
        cand_count = (
            zita_match_candidates.objects.filter(
                status_id=5,
                jd_id=jd_id,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
            )
            .values("candidate_id")
            .distinct()
            .count()
        )
        zita_count.append((jd_id, cand_count))

    filters = JobFilter(request.GET, queryset=jd_list)
    final_list = filters.qs
    if "date_posted" in request.GET and request.GET["date_posted"] != "":
        date_posted = request.GET["date_posted"]
        today = timezone.now()
        date = today - timezone.timedelta(days=int(date_posted))
        final_list = final_list.filter(job_posted_on__range=(date, today))
    if "jd_status" in request.GET and request.GET["jd_status"] != "":
        status = request.GET["jd_status"].split(",")
        final_list = final_list.filter(jd_status_id__in=status)
    len_list = final_list.count()
    page = request.GET.get("page", 1)
    paginator = Paginator(final_list, 10)

    try:
        final_list = paginator.page(page)
    except PageNotAnInteger:
        final_list = paginator.page(1)

    except EmptyPage:
        final_list = paginator.page(paginator.num_pages)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()

    context = {
        "final_list": final_list,
        "filters": filters,
        "career_page_url": career_page_url,
        "len_list": len_list,
        "Jobs_List": Jobs_List,
        "params": params,
        "permission": permission,
        "location": location,
        "zita_count": zita_count,
    }
    return render(request, "jobs/jobs_listing_ajax.html", context)


@never_cache
@login_required
@recruiter_required
def dashboard(request):
    admin_id, updated_by = admin_account(request)
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    try:
        user_info = Signup_Form.objects.get(user_id=admin_id).company_name
    except:
        user_info = "-"
    total_jobs = (
        JD_form.objects.filter(user_id=admin_id, jd_status_id__in=[1, 4])
        .values_list("id", flat=True)
        .distinct()
    )
    applicants = applicants_status.objects.filter(
        client_id=admin_id, status_id_id=1
    ).count()
    selected = applicants_status.objects.filter(client_id=admin_id, status_id=4).count()
    job_count = (
        job_view_count.objects.filter(jd_id_id__in=total_jobs)
        .values("source")
        .annotate(count=Sum("count"))
        .order_by("-count")
    )
    viewed = employer_pool.objects.filter(client_id=admin_id, can_source_id=2).count()
    rejected = applicants_status.objects.filter(client_id=admin_id, status_id=7).count()
    invite_to_apply = Candi_invite_to_apply.objects.filter(client_id=admin_id).count()
    shortlisted = applicants_status.objects.filter(
        client_id=admin_id, status_id__in=[2, 3]
    ).count()
    try:
        jobs_last_update = JD_form.objects.filter(user_id=admin_id).last().created_on
    except AttributeError:
        jobs_last_update = None
    try:
        applicants_last_update = (
            applicants_status.objects.filter(
                client_id=admin_id, status_id__in=[1, 2, 3, 4, 7]
            )
            .last()
            .created_on
        )
    except AttributeError:
        applicants_last_update = None
    try:
        viewed_last_update = (
            employer_pool.objects.filter(client_id=admin_id, can_source_id=2)
            .last()
            .created_at
        )
    except AttributeError:
        viewed_last_update = None
    try:
        rejected_last_update = (
            applicants_status.objects.filter(client_id=admin_id, status_id=7)
            .last()
            .created_on
        )
    except AttributeError:
        rejected_last_update = None
    try:
        invite_to_apply_last_update = (
            Candi_invite_to_apply.objects.filter(client_id=admin_id).last().created_at
        )
    except AttributeError:
        invite_to_apply_last_update = None
    try:
        shortlisted_last_update = (
            applicants_status.objects.filter(client_id=admin_id, status_id__in=[2, 3])
            .last()
            .created_on
        )
    except AttributeError:
        shortlisted_last_update = None
    try:
        selected_last_update = (
            applicants_status.objects.filter(client_id=admin_id, status_id__in=[4])
            .last()
            .created_on
        )
    except AttributeError:
        selected_last_update = None
    jd_metrics = list(
        JD_form.objects.filter(user_id=admin_id, jd_status_id__in=[1, 4])
        .order_by("-job_posted_on")
        .values("id", "job_id", "job_title")
    )
    logo = company_details.objects.get(recruiter_id=admin_id).logo
    plan = subscriptions.objects.filter(client_id=admin_id).last()
    job_count = client_features_balance.objects.get(
        client_id=admin_id, feature_id_id=10
    ).available_count
    contact_count = client_features_balance.objects.get(
        client_id=admin_id, feature_id_id=11
    ).available_count
    candidate_count = client_features_balance.objects.get(
        client_id=admin_id, feature_id_id=12
    ).available_count
    total_count = Recommended_Role.objects.all().distinct().count()
    try:
        google = google_return_details.objects.get(client_id=request.user)
    except:
        google = None
    try:
        outlook = outlook_return_details.objects.get(client_id=request.user)
    except:
        outlook = None
    context = {
        "user_info": user_info,
        "total_jobs": len(total_jobs),
        "jobs_last_update": jobs_last_update,
        "applicants_last_update": applicants_last_update,
        "viewed_last_update": viewed_last_update,
        "permission": permission,
        "outlook": outlook,
        "google": google,
        "logo": logo,
        "job_count": job_count,
        "contact_count": contact_count,
        "candidate_count": candidate_count,
        "rejected_last_update": rejected_last_update,
        "invite_to_apply_last_update": invite_to_apply_last_update,
        "shortlisted_last_update": shortlisted_last_update,
        "selected_last_update": selected_last_update,
        "applicants": applicants,
        "shortlisted": shortlisted,
        "selected": selected,
        "viewed": viewed,
        "plan": plan,
        "rejected": rejected,
        "invite_to_apply": invite_to_apply,
        "jd_metrics": json.dumps(jd_metrics, cls=DjangoJSONEncoder),
    }
    return render(request, "jobs/dashboard.html", context)


class YearWeek(Func):
    function = "YEARWEEK"
    template = "%(function)s(%(expressions)s)"
    output_field = IntegerField()


def dashboard_message(request):
    admin_id, updated_by = admin_account(request)
    message = Message.objects.filter(receiver=admin_id, is_read=False)

    message = message.values_list("sender", "jd_id").distinct()
    message = message.annotate(
        first_name=Subquery(
            User.objects.filter(id=OuterRef("sender")).values("first_name")[:1]
        ),
        last_name=Subquery(
            User.objects.filter(id=OuterRef("sender")).values("last_name")[:1]
        ),
        jd=Subquery(JD_form.objects.filter(id=OuterRef("jd_id")).values("id")[:1]),
        message=Subquery(
            Message.objects.filter(sender=OuterRef("sender"), jd_id=OuterRef("jd_id"))
            .values("text")
            .order_by("-date_created")[:1]
        ),
        is_read=Subquery(
            Message.objects.filter(sender=OuterRef("sender"), jd_id=OuterRef("jd_id"))
            .values("is_read")
            .order_by("-date_created")[:1]
        ),
        time=Subquery(
            Message.objects.filter(sender=OuterRef("sender"), jd_id=OuterRef("jd_id"))
            .values("date_created")
            .order_by("-date_created")[:1]
        ),
        profile_pic=Subquery(
            Profile.objects.filter(user=OuterRef("sender"))[:1].values("image")
        ),
        can_id=Subquery(
            employer_pool.objects.filter(candidate_id__user_id=OuterRef("sender"))[
                :1
            ].values("id")
        ),
    )

    message_count = Message.objects.filter(receiver=admin_id, is_read=False).count()
    context = {
        "message": message,
        "message_count": message_count,
    }
    return render(request, "jobs/dash_message.html", context)


from itertools import chain, groupby


class YearWeek(Func):
    function = "YEARWEEK"
    template = "%(function)s(%(expressions)s)"
    output_field = IntegerField()


def dashboard_job_metrics(request):
    pk = request.GET["jd_id"]
    # pk=101
    job_count = (
        job_view_count.objects.filter(jd_id_id=pk)
        .values("source")
        .annotate(count=Sum("count"))
        .order_by("-count")
    )
    total_count = job_count.aggregate(Sum("count"))
    role_base1 = []
    role_base2 = []
    posted_channel = external_jobpostings_by_client.objects.filter(jd_id_id=pk).count()
    dates = list(
        sorted(
            set(
                [
                    i["created_at"]
                    for i in job_view_count.objects.filter(jd_id_id=pk).values(
                        "created_at"
                    )
                ]
            )
        )
    )
    date_list1 = list(
        job_view_count.objects.filter(jd_id_id=pk)
        .annotate(label=YearWeek("created_at"))
        .values("label")
        .annotate(y=Sum("count"))
    )
    date_list2 = list(
        applicants_status.objects.filter(jd_id_id=pk, status_id_id__in=[1, 2, 3, 4, 7])
        .annotate(label=YearWeek("created_on"))
        .values("label")
        .annotate(y=Count("id"))
    )
    posted_date = JD_form.objects.get(id=pk).job_posted_on
    posted_date = posted_date.strftime("%b-%d")
    date_list1.insert(0, {"label": posted_date, "y": 0})
    date_list2.insert(0, {"label": posted_date, "y": 0})
    role_base = [date_list1, date_list2]
    pipeline = []
    pipeline.append({"Views": total_count["count__sum"]})
    pipeline.append(
        {
            "Applicants": applicants_status.objects.filter(
                jd_id_id=pk, status_id_id__in=[1, 2, 3, 4, 7]
            ).count()
        }
    )
    pipeline.append(
        {
            "Shortlisted": applicants_status.objects.filter(
                jd_id_id=pk, status_id_id__in=[2]
            ).count()
        }
    )
    pipeline.append(
        {
            "Qualified": applicants_status.objects.filter(
                jd_id_id=pk, status_id_id__in=[4]
            ).count()
        }
    )
    pipeline.append(
        {
            "Disqualified": applicants_status.objects.filter(
                jd_id_id=pk, status_id_id__in=[7]
            ).count()
        }
    )

    total_invite = list(
        Candi_invite_to_apply.objects.filter(jd_id_id=pk)
        .values_list("candidate_id", flat=True)
        .distinct()
    )
    my_database = []
    job_details = JD_form.objects.filter(id=pk).annotate(
        country=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                "country_id__name"
            )[:1]
        ),
        state=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values("state_id__name")[
                :1
            ]
        ),
        city=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values("city_id__name")[
                :1
            ]
        ),
    )
    zita_match = zita_match_candidates.objects.filter(jd_id_id=pk).count()
    my_database.append(
        {"Zita Match": zita_match_candidates.objects.filter(jd_id_id=pk).count()}
    )
    my_database.append(
        {"Invited to Apply": Candi_invite_to_apply.objects.filter(jd_id_id=pk).count()}
    )
    my_database.append(
        {
            "Applicant Conversion": applicants_status.objects.filter(
                jd_id_id=pk,
                candidate_id__in=total_invite,
                status_id_id__in=[1, 2, 3, 4, 7],
            ).count()
        }
    )
    applicant_count = (
        applicants_status.objects.filter(jd_id_id=pk, status_id__in=[1, 2, 3, 4, 7])
        .exclude(source__isnull=True)
        .values("source")
        .annotate(count=Count("candidate_id"))
    )
    total_count = applicant_count.aggregate(Sum("count"))

    perc_dict = []
    for i in applicant_count:

        perc = (int(i["count"]) / total_count["count__sum"]) * 100
        perc_dict.append({i["source"]: "{:.2f}".format(perc)})

    context = {
        "object1": json.dumps(list(role_base), cls=DjangoJSONEncoder),
        "posted_date": json.dumps(posted_date, cls=DjangoJSONEncoder),
        "dates_length": dates,
        "zita_match": zita_match,
        "posted_channel": posted_channel,
        "total_count": total_count,
        "job_details": job_details[0],
        "perc_dict": json.dumps(perc_dict, cls=DjangoJSONEncoder),
        "pipeline": json.dumps(pipeline, cls=DjangoJSONEncoder),
        "my_database": json.dumps(my_database, cls=DjangoJSONEncoder),
        "job_count": json.dumps(list(job_count), cls=DjangoJSONEncoder),
    }
    return render(request, "jobs/job_metrics_ajax.html", context)


# not used
def career_page_plan(request):
    plan = tmeta_career_page_plan.objects.all()
    context = {
        "plan": plan,
    }
    return render(request, "jobs/plan_page.html", context)


# not used
def job_posting_plan_page(request, uidb64):
    plan = tmeta_job_posting_plan.objects.all()
    pk = force_text(urlsafe_base64_decode(uidb64))
    if request.method == "POST":
        if "upgrade" in request.POST:
            exists_plan = recuriter_job_posting_plan.objects.get(
                recruiter_id=request.user, jd_id_id=pk, is_active=True
            )
            if "add-on" in request.POST:
                add_on_id = tmeta_job_posting_add_on.objects.get(
                    id=int(request.POST["add-on"])
                )
                if request.POST["add-on"] == "4":
                    applicant_count = None
                    add_on = applicant_add_on_plan.objects.create(
                        recruiter_id=request.user,
                        jd_id_id=pk,
                        add_on_id=add_on_id,
                        available_count=None,
                    )
                else:
                    add_on = applicant_add_on_plan.objects.create(
                        recruiter_id=request.user,
                        jd_id_id=pk,
                        add_on_id=add_on_id,
                        available_count=add_on_id.applicant_count,
                    )
                    applicant_count = (
                        exists_plan.available_applicants + add_on_id.applicant_count
                    )
            else:
                applicant_count = exists_plan.available_applicants
                add_on = None

            if "plan" in request.POST:
                plan_id = request.POST["plan"]
                job_posting_plan = tmeta_job_posting_plan.objects.get(id=plan_id)
                if exists_plan.plan_id.id == 1:
                    validity_days = job_posting_plan.validity_days
                else:
                    validity_days = (
                        exists_plan.available_days + job_posting_plan.validity_days
                    )

                featured_days = (
                    exists_plan.featured_days + job_posting_plan.featured_days
                )
                has_external_promotion = job_posting_plan.has_external_promotion
                view_contact_count = (
                    exists_plan.available_view_contacts
                    + job_posting_plan.view_contact_count
                )
                try:
                    invites_count = (
                        exists_plan.available_invites + job_posting_plan.invites_count
                    )
                except:
                    invites_count = job_posting_plan.invites_count
                try:
                    if applicant_count == None:
                        applicant_count = None
                    else:
                        applicant_count = (
                            applicant_count + job_posting_plan.applicant_count
                        )
                except:
                    applicant_count = job_posting_plan.applicant_count
                posting_plan = recuriter_job_posting_plan.objects.create(
                    recruiter_id=request.user,
                    jd_id_id=pk,
                    plan_id=job_posting_plan,
                    available_invites=invites_count,
                    available_applicants=applicant_count,
                    featured_days=featured_days,
                    available_days=validity_days,
                    has_external_promotion=has_external_promotion,
                    available_view_contacts=view_contact_count,
                    is_active=True,
                    expiry_date=timezone.now() + timedelta(days=validity_days),
                )
                exists_plan.is_active = False
                exists_plan.save()
                recuriter_payment_history.objects.create(
                    recruiter_id=request.user,
                    jd_id_id=pk,
                    add_on_id=add_on,
                    job_posting_plan_id=posting_plan,
                    is_paid=1,
                    price=add_on_id.price + job_posting_plan.price,
                    invoice_id="-",
                )
            else:
                exists_plan.available_applicants = applicant_count
                exists_plan.save()
                posting_plan = None
                recuriter_payment_history.objects.create(
                    recruiter_id=request.user,
                    jd_id_id=pk,
                    add_on_id=add_on,
                    job_posting_plan_id=posting_plan,
                    is_paid=1,
                    price=add_on_id.price,
                    invoice_id="-",
                )
            return redirect("jobs:jobs_main")
        jd = JD_form.objects.get(id=pk)
        jd.job_posted_on = timezone.now()
        jd.jd_status_id = int(1)
        jd.save()
        plan_id = request.POST["plan"]
        job_posting_plan = tmeta_job_posting_plan.objects.get(id=plan_id)
        if "add-on" in request.POST:
            add_on_id = tmeta_job_posting_add_on.objects.get(
                id=int(request.POST["add-on"])
            )
            if request.POST["add-on"] == "4":
                applicant_count = None
                add_on = applicant_add_on_plan.objects.create(
                    recruiter_id=request.user,
                    jd_id_id=jd.id,
                    add_on_id=add_on_id,
                    available_count=None,
                )
            else:
                add_on = applicant_add_on_plan.objects.create(
                    recruiter_id=request.user,
                    jd_id_id=jd.id,
                    add_on_id=add_on_id,
                    available_count=add_on_id.applicant_count,
                )
                applicant_count = (
                    job_posting_plan.applicant_count + add_on_id.applicant_count
                )
        else:
            applicant_count = job_posting_plan.applicant_count
            add_on = None
        posting_plan = recuriter_job_posting_plan.objects.create(
            recruiter_id=request.user,
            jd_id_id=jd.id,
            plan_id=job_posting_plan,
            available_invites=job_posting_plan.invites_count,
            available_applicants=applicant_count,
            featured_days=job_posting_plan.featured_days,
            available_days=job_posting_plan.validity_days,
            has_external_promotion=job_posting_plan.has_external_promotion,
            available_view_contacts=job_posting_plan.view_contact_count,
            is_active=True,
            expiry_date=timezone.now() + timedelta(days=job_posting_plan.validity_days),
        )
        if add_on == None:
            recuriter_payment_history.objects.create(
                recruiter_id=request.user,
                jd_id_id=jd.id,
                add_on_id=add_on,
                job_posting_plan_id=posting_plan,
                is_paid=1,
                price=job_posting_plan.price,
                invoice_id="-",
            )
        else:
            recuriter_payment_history.objects.create(
                recruiter_id=request.user,
                jd_id_id=jd.id,
                add_on_id=add_on,
                job_posting_plan_id=posting_plan,
                is_paid=1,
                price=add_on_id.price + job_posting_plan.price,
                invoice_id="-",
            )
        # user_id = User.objects.get(username = request.user).id
        # user = User.objects.get(username = request.user)
        # jd = JD_form.objects.filter(user_id = user_id).last()
        logger.info("Posting JD " + str(jd))
        chosen_role = JD_form.objects.get(id=jd.id).job_role.label_name
        # JD_list,candidate_list = get_JDlist_candlist(jd_id = jd.id)
        # result = candidate_matcher(JD_list,candidate_list,10,10,'n') 'http://192.168.3.170:9999/match/matchapplication-with-jd-id/' 'http://192.168.3.243/match/matchapplication-with-jd-id/',
        if chosen_role != "Others":
            data = {"jd_id": jd.id}
            # Staging-Matching-URL
            responses = requests.post(
                matching_api_url + matching_application_jd_endpoint,
                data=data,
                headers={"Authorization": matching_auth_token},
            )
            # DEV-matching-URL
            # responses = requests.post('http://192.168.3.170:9999/match/matchapplication-with-jd-id/',data=data,headers={'Authorization': 'Token 3f139bacc554c9c5befdd705fa297c95b7d89eba'})
            logger.debug("Matching API response: " + str(responses))
            result = Matched_candidates.objects.filter(
                jd_list_id_id__zita_jd_id_id=jd.id
            ).values("application_id_id", "profile_match", "skill_match")

            # recom_cand_ids = [i['candidate_id_id'] for i in Recommended_candidates.objects.filter(jd_id_id=jd.id).values('candidate_id_id')]
            for i in result:
                jd_candidate_analytics.objects.get_or_create(
                    jd_id_id=jd.id,
                    candidate_id_id=i["application_id_id"],
                    status_id_id=int(5),
                    recruiter_id=request.user,
                )

            count = jd_candidate_analytics.objects.filter(
                jd_id_id=jd.id, status_id_id=5
            ).count()
            Zita_match_count.objects.create(jd_id_id=jd.id, count=count)
            user = User.objects.get(username=request.user)
            current_site = get_current_site(request)
            mail_notification(
                user,
                "job_post_confirmation.html",
                "Congratulations!!! Your job has been successfully posted on your career page",
                jd_id=jd.id,
                count=count,
                domain=current_site,
            )

        else:
            logger.info("As 'Others' is chosen role, Not doing Matching")

        return redirect("jobs:jobs_main")

        # return redirect()
    try:
        exists_plan = recuriter_job_posting_plan.objects.get(
            recruiter_id=request.user, jd_id_id=pk, is_active=True
        )
    except:
        exists_plan = 0

    context = {
        "plan": plan,
        "exists_plan": exists_plan,
    }
    return render(request, "jobs/plan_page.html", context)


# This function is to list the candidate list (ziat_match and Applicant) for the JD
@never_cache
@login_required
@recruiter_required
def applicant(request, pk=None, *args):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    user_id, updated_by = admin_account(request)
    has_permission = user_permission(request, "applicants")
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    if not has_permission == True:
        return render(request, "jobs/no_permission.html", {"permission": permission})

    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")

    # result=matching_api_to_db(request,jd_id=pk,can_id=None)

    data = request.GET
    job_details = JD_form.objects.filter(id=pk).annotate(
        country=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                "country_id__name"
            )[:1]
        ),
        state=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values("state_id__name")[
                :1
            ]
        ),
        city=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values("city_id__name")[
                :1
            ]
        ),
    )

    context = {
        "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        "jd_id": pk,
        "job_details": job_details[0],
        "permission": permission,
    }
    return render(request, "jobs/applicant_zita_match.html", context)


from calendarapp.models import Event


@never_cache
@login_required
@recruiter_required
def applicant_ajax(request, pk=None, *args):
    user_id, updated_by = admin_account(request)
    if "update" in request.GET:
        status = 1
        jd_id = JD_form.objects.get(id=pk)
        applicant_update = applicants_status.objects.get(id=request.GET["update"])
        if request.GET["status"] == "yellow":
            status = 1
        elif request.GET["status"] == "blue":
            status = 2
            UserActivity.objects.create(
                user=request.user,
                action_id=6,
                action_detail='"'
                + str(applicant_update.candidate_id.first_name)
                + '" for the job id: '
                + str(jd_id.job_id),
            )
        elif request.GET["status"] == "green":
            status = 3
        elif request.GET["status"] == "purple":
            status = 4
            UserActivity.objects.create(
                user=request.user,
                action_id=7,
                action_detail='"'
                + str(applicant_update.candidate_id.first_name)
                + '" for the job id: '
                + str(jd_id.job_id),
            )
        elif request.GET["status"] == "red":
            status = 7
            UserActivity.objects.create(
                user=request.user,
                action_id=8,
                action_detail='"'
                + str(applicant_update.candidate_id.first_name)
                + '" for the job id: '
                + str(jd_id.job_id),
            )
        applicant_update.status_id_id = status
        applicant_update.updated_by = updated_by
        applicant_update.created_on = datetime.now()
        applicant_update.save()
        applicants_screening_status.objects.get_or_create(
            jd_id=jd_id,
            candidate_id=applicant_update.candidate_id,
            client_id=user_id,
            status_id_id=status,
            updated_by=updated_by,
        )
        return HttpResponseNotModified()
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")
    today = timezone.now().date
    applicants = applicants_status.objects.filter(jd_id_id=pk)
    jd_list = get_object_or_404(JD_form, id=pk)
    fav = jd_list.favourite.all()
    applicants = applicants.annotate(
        fav=Subquery(fav.filter(id=OuterRef("candidate_id"))[:1].values("id")),
        name=Subquery(
            applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                "candidate_id__candidate_id__firstname"
            )
        ),
        email=Subquery(
            applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                "candidate_id__email"
            )
        ),
        qualification=Subquery(
            applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                "candidate_id__qualification"
            )
        ),
        skills=Subquery(
            applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                "candidate_id__skills"
            )
        ),
        event=Subquery(
            Event.objects.filter(
                attendees__in=OuterRef("candidate_id__email"), user=request.user
            )[:1].values("id")
        ),
        location=Subquery(
            applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                "candidate_id__location"
            )
        ),
        viewed=Subquery(
            applicants_status.objects.filter(
                candidate_id=OuterRef("candidate_id"), client_id=user_id, status_id_id=6
            )[:1].values("candidate_id__location")
        ),
        work_exp=Subquery(
            Additional_Details.objects.filter(
                application_id=OuterRef("candidate_id__candidate_id")
            )[:1].values("total_exp_year")
        ),
        match=Subquery(
            Matched_candidates.objects.filter(
                jd_id_id=pk, candidate_id=OuterRef("candidate_id")
            )[:1].values("profile_match")
        ),
        image=Subquery(
            Profile.objects.filter(
                user_id=OuterRef("candidate_id__candidate_id__user_id")
            )[:1].values("image")
        ),
        file=Subquery(
            Myfiles.objects.filter(
                upload_id=OuterRef("candidate_id__candidate_id__user_id")
            )
            .order_by("-id")[:1]
            .values("resume_file")
        ),
    ).order_by("-created_on")

    if "profile_match" in request.GET and len(request.GET["profile_match"]) > 0:
        try:
            if len(request.GET["profile_match"]) > 0:
                data_profile = request.GET["profile_match"].split("-")
                request.GET._mutable = True
                request.GET["match_min"] = data_profile[0]
                request.GET["match_max"] = data_profile[1]
                if data_profile[1] == "60":
                    applicants = applicants.filter(
                        Q(
                            match__range=(
                                request.GET["match_min"],
                                request.GET["match_max"],
                            )
                        )
                        | Q(match__isnull=True)
                    )
                else:
                    applicants = applicants.filter(
                        match__range=(
                            request.GET["match_min"],
                            request.GET["match_max"],
                        )
                    )
        except:
            request.GET._mutable = True
            request.GET["profile_match"] = ""
    fav_id = 0
    if "fav" in request.GET and len(request.GET["fav"]) > 0:
        if request.GET["fav"] == "add":
            fav_id = 1
            applicants = applicants.exclude(fav__isnull=True)
    if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
        if "@" in request.GET["candidate"]:
            applicants = applicants.filter(email__icontains=request.GET["candidate"])
        else:
            applicants = applicants.filter(name__icontains=request.GET["candidate"])
    if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
        data_profile = request.GET["work_experience"].split("-")
        request.GET._mutable = True
        request.GET["work_min"] = data_profile[0]
        request.GET["work_max"] = data_profile[1]
        applicants = applicants.filter(
            work_exp__range=(int(request.GET["work_min"]), int(request.GET["work_max"]))
        )
    if "profile_view" in request.GET and len(request.GET["profile_view"]) > 0:
        if request.GET["profile_view"] == "1":
            applicants = applicants.exclude(viewed__isnull=True)
        elif request.GET["profile_view"] == "0":
            applicants = applicants.exclude(viewed__isnull=False)
    if "education_level" in request.GET and len(request.GET["education_level"]) > 0:
        applicants = applicants.filter(
            reduce(
                operator.or_,
                (
                    Q(qualification__icontains=qual)
                    for qual in request.GET.getlist("education_level")
                ),
            )
        )
    if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
        skill_match_list = request.GET.getlist("skill_match")
        applicants = applicants.filter(
            reduce(
                operator.or_, (Q(skills__icontains=item) for item in skill_match_list)
            )
        )
    request.GET._mutable = True
    if "sort_applicant" in request.GET:
        if len(request.GET.getlist("sort_applicant")) > 1:
            request.GET["sort_applicant"] = request.GET.getlist("sort_applicant")[0]
        if request.GET["sort_applicant"] == "date":
            applicant = applicants.filter(status_id_id=1).order_by("-created_on")
        elif request.GET["sort_applicant"] == "name":
            applicant = applicants.filter(status_id_id=1).order_by("name")
        else:
            applicant = applicants.filter(status_id_id=1)
    else:
        applicant = applicants.filter(status_id_id=1)
    if "sort_shortlisted" in request.GET:
        if len(request.GET.getlist("sort_shortlisted")) > 1:
            request.GET["sort_shortlisted"] = request.GET.getlist("sort_shortlisted")[0]
        if request.GET["sort_shortlisted"] == "date":
            shortlisted = applicants.filter(status_id_id=2).order_by("-created_on")
        elif request.GET["sort_shortlisted"] == "name":
            shortlisted = applicants.filter(status_id_id=2).order_by("name")
        else:
            shortlisted = applicants.filter(status_id_id=2)
    else:
        shortlisted = applicants.filter(status_id_id=2)
    if "sort_interviewed" in request.GET:
        if len(request.GET.getlist("sort_interviewed")) > 1:
            request.GET["sort_interviewed"] = request.GET.getlist("sort_interviewed")[0]
        if request.GET["sort_interviewed"] == "date":
            interviewed = applicants.filter(status_id_id=3).order_by("-created_on")
        elif request.GET["sort_interviewed"] == "name":
            interviewed = applicants.filter(status_id_id=3).order_by("name")
        else:
            interviewed = applicants.filter(status_id_id=3)
    else:
        interviewed = applicants.filter(status_id_id=3)
    if "sort_selected" in request.GET:
        if len(request.GET.getlist("sort_selected")) > 1:
            request.GET["sort_selected"] = request.GET.getlist("sort_selected")[0]
        if request.GET["sort_selected"] == "date":
            selected = applicants.filter(status_id_id=4).order_by("-created_on")
        elif request.GET["sort_selected"] == "name":
            selected = applicants.filter(status_id_id=4).order_by("name")
        else:
            selected = applicants.filter(status_id_id=4)
    else:
        selected = applicants.filter(status_id_id=4)
    if "sort_rejected" in request.GET:
        if len(request.GET.getlist("sort_rejected")) > 1:
            request.GET["sort_rejected"] = request.GET.getlist("sort_rejected")[0]
        if request.GET["sort_rejected"] == "date":
            rejected = applicants.filter(status_id_id=7).order_by("-created_on")
        elif request.GET["sort_rejected"] == "name":
            rejected = applicants.filter(status_id_id=7).order_by("name")
        else:
            rejected = applicants.filter(status_id_id=7)
    else:
        rejected = applicants.filter(status_id_id=7)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.urlencode()
    try:
        google = google_return_details.objects.get(client_id=request.user)
    except:
        google = None
    try:
        outlook = outlook_return_details.objects.get(client_id=request.user)
    except:
        outlook = None
    context = {
        "jd_id": pk,
        "applicant": applicant,
        "shortlisted": shortlisted,
        "interviewed": interviewed,
        "selected": selected,
        "rejected": rejected,
        "params": params,
        "today": today,
        "fav_id": fav_id,
        "google": google,
        "outlook": outlook,
        "total_applicants": applicants.filter(status_id__in=[1, 2, 3, 4, 7]).count(),
        "applicants": json.dumps(list(applicants.values()), cls=DjangoJSONEncoder),
    }
    return render(request, "jobs/applicant_zita_match_ajax.html", context)


@never_cache
@login_required
@recruiter_required
def zita_match(request, pk=None, *args):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass

    has_permission = user_permission(request, "zita_match_candidate")
    if not has_permission == True:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")
    user = User.objects.get(username=request.user).id
    logger.info("In function shorlist_candidates - User ID: " + str(user))
    jd_state = JD_locations.objects.filter(jd_id_id=pk).values_list(
        "state_id", flat=True
    )
    job_details = JD_form.objects.filter(id=pk).annotate(
        profile=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("id")).values(
                "recommended_role_id__label_name"
            )[:1]
        ),
        country=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                "country_id__name"
            )[:1]
        ),
        state=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values("state_id__name")[
                :1
            ]
        ),
        city=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id")).values("city_id__name")[
                :1
            ]
        ),
    )[0]
    location = JD_locations.objects.filter(jd_id_id=pk).values_list("state_id__name")
    data = request.GET
    matching_api_to_db(request, jd_id=pk, can_id=None)
    candidate_details = Personal_Info.objects.none()
    filters = Zita_Match_Filter(data, queryset=candidate_details)

    context = {
        "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        "jd_id": pk,
        "job_details": job_details,
        "filters": filters,
        "permission": permission,
        "location": list(sum(location, ())),
    }
    return render(request, "jobs/zita_match.html", context)


@never_cache
@login_required
@recruiter_required
def zita_match_ajax(request, pk=None, *args):
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")
    user_id, updated_by = admin_account(request)
    user = User.objects.get(username=request.user).id
    logger.info("In function shorlist_candidates - User ID: " + str(user))
    # rr = Personal_Info.objects.filter(Q(relocate=True)|Q(current_state__in=jd_state)).values_list('application_id',flat=True)
    data = request.GET
    get_dict_copy = request.GET.copy()
    fav_id = 0
    zita_match = zita_match_candidates.objects.filter(
        jd_id_id=pk,
        candidate_id__first_name__isnull=False,
        candidate_id__email__isnull=False,
    ).values_list("candidate_id", flat=True)
    data = employer_pool.objects.filter(id__in=zita_match)
    jd_list = get_object_or_404(JD_form, id=pk)
    fav = jd_list.favourite.all()
    # data=data.annotate(

    # 	)
    data = data.annotate(
        fav=Subquery(fav.filter(id=OuterRef("id"))[:1].values("id")),
        applicant=Subquery(
            applicants_status.objects.filter(
                jd_id_id=pk, candidate_id=OuterRef("id"), status_id__in=[1, 2, 3, 4, 7]
            )[:1].values("jd_id__job_title")
        ),
        match=Subquery(
            Matched_candidates.objects.filter(jd_id_id=pk, candidate_id=OuterRef("id"))[
                :1
            ].values("profile_match")
        ),
        image=Subquery(
            Profile.objects.filter(user_id=OuterRef("candidate_id__user_id"))[
                :1
            ].values("image")
        ),
        invite=Subquery(
            Candi_invite_to_apply.objects.filter(
                jd_id_id=pk, candidate_id=OuterRef("id")
            )[:1].values("created_at")
        ),
        applicant_view=Subquery(
            applicants_status.objects.filter(
                client_id=user_id, candidate_id=OuterRef("id"), status_id_id=6
            )[:1].values("created_on")
        ),
        interested=Subquery(
            Candi_invite_to_apply.objects.filter(
                jd_id_id=pk, candidate_id=OuterRef("id")
            )
            .order_by("-created_at")[:1]
            .values("is_interested")
        ),
    ).order_by("-match")
    if "profile_match" in request.GET and len(request.GET["profile_match"]) > 0:
        try:
            if len(request.GET["profile_match"]) > 0:
                data_profile = request.GET["profile_match"].split("-")
                request.GET._mutable = True
                request.GET["match_min"] = data_profile[0]
                request.GET["match_max"] = data_profile[1]
                data = data.filter(
                    match__range=(request.GET["match_min"], request.GET["match_max"])
                )
        except:
            request.GET._mutable = True
            request.GET["profile_match"] = ""

    if "fav" in request.GET and len(request.GET["fav"]) > 0:

        if request.GET["fav"] == "add":
            fav_id = 1
            # jd_list = get_object_or_404(JD_form, id=pk)
            # fav=jd_list.favourite.all()
            data = data.exclude(fav__isnull=True)

    if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
        if "@" in request.GET["candidate"]:
            data = data.filter(email__icontains=request.GET["candidate"])
        else:
            data = data.filter(first_name__icontains=request.GET["candidate"])
    # if 'work_experience' in request.GET and len(request.GET['work_experience'])>0:
    # 	data=data.filter(work_exp__icontains=request.GET['work_experience'])
    if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
        if request.GET["work_experience"] == "0-1":
            data = data.filter(work_exp__in=["0-1", "0", "Less than 1 year"])
        elif request.GET["work_experience"] == "10+":
            data = data.filter(
                work_exp__in=["More than 10 years", "10", "11", "12", "13", "14", "15"]
            )
        else:
            data = data.filter(work_exp__icontains=request.GET["work_experience"])
    if "relocate" in request.GET and len(request.GET["relocate"]) > 0:
        data = data.filter(relocate=True)
    if "invite" in request.GET and len(request.GET["invite"]) > 0:
        if request.GET["invite"] == "1":
            data = data.exclude(invite__isnull=True)
        elif request.GET["invite"] == "0":
            data = data.exclude(invite__isnull=False)
    if "profile_view" in request.GET and len(request.GET["profile_view"]) > 0:
        if request.GET["profile_view"] == "1":
            data = data.exclude(applicant_view__isnull=True)
        elif request.GET["profile_view"] == "0":
            data = data.exclude(applicant_view__isnull=False)
    if "education_level" in request.GET and len(request.GET["education_level"]) > 0:
        data = data.filter(
            reduce(
                operator.or_,
                (
                    Q(qualification__icontains=qual)
                    for qual in request.GET.getlist("education_level")
                ),
            )
        )
    if "type_of_job" in request.GET and len(request.GET["type_of_job"]) > 0:
        data = data.filter(job_type_id=request.GET["type_of_job"])
    if (
        "preferred_location" in request.GET
        and len(request.GET["preferred_location"]) > 0
    ):
        location = JD_locations.objects.filter(jd_id_id=pk).values("state_id__name")
        data = data.filter(
            location__icontains=location.values("state_id__name")[0]["state_id__name"]
        )
    if "user_type" in request.GET and len(request.GET["user_type"]) > 0:
        data = data.filter(can_source_id=request.GET["user_type"])
        user_type = request.GET["user_type"]
    else:
        user_type = ""
    if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
        skill_match_list = request.GET.getlist("skill_match")
        data = data.filter(
            reduce(
                operator.or_, (Q(skills__icontains=item) for item in skill_match_list)
            )
        )
    if "interested" in request.GET and len(request.GET["interested"]) > 0:
        if request.GET["interested"] == "interested":
            data = data.order_by("-interested")
        elif request.GET["interested"] == "not_interested":
            data = data.order_by("interested")

    page = request.GET.get("page", 1)
    paginator = Paginator(data, 20)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)

    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
    context = {
        "data": data,
        "jd_id": pk,
        "fav_id": fav_id,
        "user_type": user_type,
        "params": params,
    }
    return render(request, "jobs/zita_match_ajax.html", context)


# This function is for shortlist the candidate in the shortlisting page


def sorting(request, pk=None, id=None, status_id=None, *args, **kwargs):
    jd_id = pk
    candidate_id = id
    status_id = 13 if status_id == 13 else 7
    interested = 1 if status_id == 13 else 0
    user_id, updated_by = admin_account(request)

    if "invite" in request.GET:
        if Candi_invite_to_apply.objects.filter(
            jd_id_id=jd_id,
            candidate_id_id=candidate_id,
            client_id=user_id,
        ).exists():
            Candi_invite_to_apply.objects.filter(
                jd_id_id=jd_id,
                candidate_id_id=candidate_id,
                client_id=user_id,
            ).update(created_at=timezone.now())
        else:
            Candi_invite_to_apply.objects.create(
                jd_id_id=jd_id,
                candidate_id_id=candidate_id,
                client_id=user_id,
            )
        candidate_details = employer_pool.objects.get(id=candidate_id)
        jd_id = JD_form.objects.get(id=jd_id)
        loc = JD_locations.objects.filter(jd_id=jd_id)
        qual = JD_qualification.objects.filter(jd_id=jd_id)
        detail = company_details.objects.filter(recruiter_id=user_id)
        try:
            match = Matched_candidates.objects.get(
                candidate_id=candidate_details, jd_id=jd_id
            ).profile_match
        except:
            match = None
        company_detail = company_details.objects.get(recruiter_id=user_id).company_name
        url = career_page_setting.objects.get(recruiter_id=user_id).career_page_url
        htmly = get_template("email_templates/invite_to_apply.html")
        current_site = get_current_site(request)
        subject, from_email, to = (
            "Job Notification: An employer invitation to Apply for a Job",
            email_main,
            "support@zita.ai",
        )
        html_content = htmly.render(
            {
                "jd_id": jd_id,
                "url": url,
                "loc": loc,
                "match": match,
                "qual": qual,
                "detail": detail,
                "current_site": current_site,
                "company_detail": company_detail,
                "candidate_details": candidate_details,
                "job_pool": jd_id,
            }
        )
        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = "related"
        image_data = [
            "twitter.png",
            "linkedin.png",
            "youtube.png",
            "new_zita_white.png",
        ]
        for i in image_data:
            msg.attach(logo_data(i))
        msg.send()
        UserActivity.objects.create(
            user=request.user,
            action_id=5,
            action_detail='"'
            + str(candidate_details.first_name)
            + '" for the job id: '
            + str(jd_id.job_id),
        )

        data = {"success": 1, "date": datetime.now().date().strftime("%b %d,  %Y")}
        return JsonResponse(data)


def contact_zita(request, pk=None):
    user = User.objects.get(username=request.user)

    if int(pk) != 0:
        jd_id = pk
        candidate_details = jd_candidate_analytics.objects.filter(
            status_id_id=5, recruiter_id_id=user.id, jd_id_id=jd_id, interested=1
        ).exclude(contacted=1)
        if candidate_details.count() > 0:
            jd = JD_form.objects.get(id=jd_id)
            htmly = get_template("email_templates/contact_zita.html")
            subject, from_email, to = (
                "Applicants and Zita Match Candidates",
                email_main,
                EMAIL_TO,
            )
            html_content = htmly.render(
                {"user": user, "candidate_details": candidate_details, "jd": jd}
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "facebook.png",
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()
            htmly = get_template("email_templates/contact_zita_user.html")
            subject, from_email, to = "Zita Contacted Details", email_main, user.email
            html_content = htmly.render(
                {
                    "user": user,
                    "candidate_details": candidate_details,
                    "jd": jd,
                    "company_name": jd.company_name,
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "facebook.png",
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()
            candidate_details.update(contacted=1)

        data = {"success": True}
    else:
        candidate_details = jd_candidate_analytics.objects.filter(
            status_id_id=15, recruiter_id_id=user.id, interested=1
        ).exclude(contacted=1)
        company_name = Signup_Form.objects.get(user_id_id=user.id).company_name
        if candidate_details.count() > 0:
            jd = 0
            htmly = get_template("email_templates/contact_zita.html")
            subject, from_email, to = "Interested Candidates", email_main, EMAIL_TO
            html_content = htmly.render(
                {
                    "user": user,
                    "candidate_details": candidate_details,
                    "jd": jd,
                    "company_name": company_name,
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "facebook.png",
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()
            htmly = get_template("email_templates/contact_zita_user.html")
            subject, from_email, to = "Zita Contacted Details", email_main, user.email
            html_content = htmly.render(
                {
                    "user": user,
                    "candidate_details": candidate_details,
                    "jd": jd,
                    "company_name": company_name,
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "facebook.png",
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()
            candidate_details.update(status_id_id=13, contacted=1)
        data = {"success": True}

    return JsonResponse(data)


# def func(pct, allvals):
#     absolute = int(pct/100.*np.sum(allvals))
#     return "{:.1f}%\n({:d} g)".format(pct, absolute)


class Render:

    @staticmethod
    def render(path: str, params: dict, filename: str):
        template = get_template(path)
        html = template.render(params)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type="application/pdf")
            # response['Content-Disposition'] = 'attachment; filename="'+str(filename)+'.pdf"'
            return response

        else:
            return HttpResponse("Error Rendering PDF", status=400)


class download_interested_1(View):

    def get(self, request, pk, *args, **kwargs):
        jd_id = pk
        user = User.objects.get(username=request.user).id
        candidate_details = jd_candidate_analytics.objects.filter(
            status_id_id=16, recruiter_id_id=user, jd_id_id=jd_id
        )
        candidate_details = candidate_details.annotate(
            profile_match=Subquery(
                Matched_candidates.objects.filter(
                    application_id=OuterRef("candidate_id"),
                    jd_list_id_id__zita_jd_id_id=jd_id,
                )[:1].values("profile_match")
            ),
        )
        today = timezone.now()
        params = {
            "candidate_details": candidate_details,
            "today": today,
            "request": request,
        }
        file = Render.render("pdf/test.html", params, filename="interested")

        return file


def venn_diagram(request, match, filename):
    match = match
    non_match = 100 - match
    size_of_groups = [non_match, match]

    # Create a pie plot
    plt.pie(
        size_of_groups,
        colors=["gray", "orange"],
        startangle=90,
    )
    # plt.show()

    # add a white circle at the center
    my_circle = plt.Circle((0, 0), 0.7, color="white")
    # plt.pie(size_of_groups,colors=['eee','ff9f00'])
    p = plt.gcf()
    p.gca().add_artist(my_circle)

    # show the graph
    name_file = "role_match_" + str(filename) + ".png"
    plt.savefig(base_dir + "/media/charts/" + name_file)
    plt.close()
    # v=venn2(subsets = (50,50,int(match)),set_labels = ('', ''),alpha=0.7,set_colors=('#7cb5ec', '#434348'),subset_label_formatter=None)

    # labels = ['JD', 'Candidate']
    # for label,ID in zip(labels, ["10", "01"]):
    # 	v.get_label_by_id(ID).get_text()
    # 	v.get_label_by_id(ID).set_text(label)
    # 	v.get_label_by_id(ID).set_fontsize(14)
    # 	v.get_label_by_id('11').set_text(str(match)+'%')
    # 	v.get_label_by_id('11').set_fontsize(16)
    # 	v.get_patch_by_id('11').set_color('#90ED7D')

    # name_file = 'role_match_'+str(filename)+'.png'
    # plt.savefig(base_dir+'/media/charts/'+name_file)
    # plt.close()

    return


def radar_factory(num_vars, frame="circle"):

    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = "radar"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location("N")

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == "circle":
                return Circle((0.5, 0.5), 0.5)
            elif frame == "polygon":
                return RegularPolygon((0.5, 0.5), num_vars, radius=0.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def draw(self, renderer):
            """Draw. If frame is polygon, make gridlines polygon-shaped"""
            if frame == "polygon":
                gridlines = self.yaxis.get_gridlines()
                for gl in gridlines:
                    gl.get_path()._interpolation_steps = num_vars
            super().draw(renderer)

        def _gen_axes_spines(self):
            if frame == "circle":
                return super()._gen_axes_spines()
            elif frame == "polygon":
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(
                    axes=self,
                    spine_type="circle",
                    path=Path.unit_regular_polygon(num_vars),
                )
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(
                    Affine2D().scale(0.5).translate(0.5, 0.5) + self.transAxes
                )

                return {"polar": spine}
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def redar_chart(request, evaluation, avg_score, filename):

    metric_dict = {
        "problem_understanding_analysis": "Approach (Problem Understanding & Analysis)",
        "design_a_solution": "Design a Solution",
        "develop_solution": "Develop Solution",
        "result_output": "Output (Presentation / Visualisation)",
        "time_management": "Time Management",
        "utilization_of_resources": "Utilization of Resources",
    }

    # Set data
    evaluation_dict = {"group": ["A", "B"]}

    for eva in evaluation:
        metric_value = eva["metric_value"]
        score = eva["score"]
        evaluation_dict[metric_value] = [score]
    for k, v in metric_dict.items():
        evaluation_dict[v].append(avg_score[0][k])

    df = pd.DataFrame(evaluation_dict)

    if avg_score[0]["role_id_id"] == 1:
        avg_score_lable = "Average DA Score"
    elif avg_score[0]["role_id_id"] == 2:
        avg_score_lable = "Average MLE Score"
    elif avg_score[0]["role_id_id"] == 3:
        avg_score_lable = "Average DE Score"
    elif avg_score[0]["role_id_id"] == 4:
        avg_score_lable = "Average BI Score"
    elif avg_score[0]["role_id_id"] == 5:
        avg_score_lable = "Average DO Score"

    # ------- PART 1: Create background

    # number of variable
    categories = list(df)[1:]
    N = len(categories)

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    N = 6
    theta = radar_factory(N, frame="polygon")

    fig, ax = plt.subplots(subplot_kw=dict(projection="radar"))

    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    est_list = categories[-1:] + categories[:-1]
    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], est_list, size=14)
    for label, i in zip(ax.get_xticklabels(), range(0, len(angles))):

        angle_rad = angles[i]
        if angle_rad <= 1:
            ha = "center"
            va = "bottom"
        elif 1 < angle_rad <= 2:
            ha = "left"
            va = "bottom"
        elif 2 < angle_rad <= 3:
            ha = "left"
            va = "bottom"
        elif 3 < angle_rad <= 4:
            ha = "center"
            va = "bottom"
        elif pi < angle_rad <= (3 * pi / 2):
            ha = "right"
            va = "top"
        else:
            ha = "right"
            va = "bottom"
        label.set_verticalalignment(va)
        label.set_horizontalalignment(ha)

    ax.set_rlabel_position(0)

    plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], color="grey", size=7)
    plt.ylim(0, 5)

    # ------- PART 2: Add plots

    # Plot each individual = each line of the data
    # I don't do a loop, because plotting more than 3 groups makes the chart unreadable

    # Ind1
    values = df.loc[0].drop("group").values.flatten().tolist()

    values = values[-1:] + values[:-1]
    values += values[:1]

    ax.plot(angles, values, linewidth=1, linestyle="solid", label="Your Score")
    ax.fill(angles, values, "b", color="skyblue", alpha=0.9)

    # Ind2
    values = df.loc[1].drop("group").values.flatten().tolist()
    values = values[-1:] + values[:-1]
    values += values[:1]

    ax.plot(angles, values, linewidth=1, linestyle="solid", label=avg_score_lable)
    ax.fill(angles, values, "r", color="orange", alpha=0.5)

    # Add legend
    plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize="large")
    # plt.legend(loc='best', bbox_to_anchor=(0.1, 0.1))

    plt.savefig(
        base_dir + "/media/charts/radar_" + str(filename) + ".png", bbox_inches="tight"
    )
    plt.close()

    return


# import seaborn as set_transform


def area_chart(request, main_prof, filename):
    main_prof = {
        key: value
        for key, value in main_prof.items()
        if key not in ("dset_date", "usecase_date")
    }
    z = len(list((main_prof.values())))
    x = range(1, z + 1)
    y = list((main_prof.values()))
    fig, ax = plt.subplots()
    x_new = np.linspace(min(x), max(x), 500)
    f = interp1d(x, y, kind="quadratic")
    y_smooth = f(x_new)
    # Change the color and its transparency
    plt.fill_between(x_new, y_smooth, color="orange", alpha=0.8, lw=0.2)
    plt.plot(
        x_new,
        y_smooth,
        color="orange",
        alpha=0.8,
        lw=1,
        marker="o",
    )
    # plt.scatter (x, y)
    plt.yticks(
        [0, 1, 2, 3, 4],
        ["Not Eligible", "Fresher", "Beginner", "Intermediate", "Advanced"],
        size=14,
    )
    plt.xticks(x, list(main_prof.keys()), rotation=20, size=14)

    ax.set(xlim=(1, len(x)), ylim=(0, None))
    ax.grid()
    plt.savefig(
        base_dir + "/media/charts/area_" + str(filename) + ".png", bbox_inches="tight"
    )
    plt.close()
    return


def pie_chart(request, prof, filename):
    prof = prof[0]
    r = dict(prof)
    for k, v in prof.items():
        if v == "0.0" or v == "0":
            del r[k]
        else:
            r[k] = str(round(int(float(v))))

    label = list(r.keys())
    data = list(r.values())

    role_inverse_dict = {
        "data_analysis": "Data Analyst",
        "business_intelligence": "Business Intelligence",
        "machine_learning": "Machine Learning\nEngineer",
        "devops": "Devops Engineer",
        "data_engineering": "Big Data\nEngineer",
        "others": "Others",
    }
    textprops = {"fontsize": 15}
    fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=dict(aspect="equal"))
    # slices = sorted(data)
    # small = slices[len(int(slices)) / 2:]
    # large = slices[:len(int(slices)) / 2]
    # reordered = large[::2] + small[::2] + large[1::2] + small[1::2]
    # angle = 180 + float(sum(small[::2])) / sum(reordered) * 360
    colors = [
        "#ff63849c",
        "#4bc0c09c",
        "#ffcd569c",
        "#ff9f409c",
        "#36a2eb9c",
        "#73eb369c",
    ]
    wedges, texts = ax.pie(
        data,
        labeldistance=1.05,
        wedgeprops={"alpha": 0.7},
        colors=colors,
        startangle=70,
    )

    # import math
    # for labels, t in zip(label, texts):
    #     x, y = t.get_position()
    #     angle = int(math.degrees(math.atan2(y, x)))
    #     ha = "left"

    #     if x<0:
    #         angle -= 180
    #         ha = "right"

    #     plt.annotate(labels, xy=(x,y), rotation=angle, ha=ha, va="center", rotation_mode="anchor", size=6)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), zorder=0, va="center")
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(
            role_inverse_dict[label[i]] + "-" + data[i] + "%",
            rotation_mode="anchor",
            xy=(x, y),
            xytext=(1.35 * np.sign(x), 1.4 * y),
            horizontalalignment=horizontalalignment,
            **kw,
        )

    plt.savefig(
        base_dir + "/media/charts/pie_" + str(filename) + ".png", bbox_inches="tight"
    )
    plt.close()
    return


def assessment_data(request, id):
    user = User_Info.objects.get(application_id_id=id)
    recom_role = Recommended_Role.objects.filter(application_id_id=id)
    user_id = user.user_id_id
    main_prof_dict = {}
    main_claimed_prof = {}
    evaluation = {}
    avg_score = {}
    usecase_success = []
    recommended_role_list = []
    dset_status = 0
    for r in recom_role:
        ds_main_roles = r.recommended_role.id
        recommended_role_list.append(r.recommended_role.label_name)
        if Test_Assign.objects.filter(
            user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
        ).exists():
            dset_status = 1
            dset_status = Test_Assign.objects.get(
                user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
            ).dset_status.id
            claimed_prof_status = (
                1
                if Tech_proficiency.objects.filter(
                    application_id_id__user_id_id=user_id,
                    role_id_id=ds_main_roles,
                    active_test=1,
                ).exists()
                else 0
            )
            # selected_role=r
            # claimed_prof = {i['Skill'].lower():i['level'] for i in Tech_proficiency.objects.filter(application_id_id__user_id_id=user_id, role_id_id=ds_main_roles,active_test=1).values('Skill','level')}
            if dset_status == 5:
                distinct_secs = (
                    Responses.objects.filter(
                        user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                    )
                    .values("section__label_name")
                    .distinct()
                )
                test_obj = Test_Assign.objects.get(
                    user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                )
                parameters = Create_test.objects.get(test_id=test_obj.test_id_id)

                ### for table summary
                summary_results = (
                    Responses.objects.filter(
                        user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                    )
                    .values(
                        "section__label_name",
                        "question_id_id__difficulty_level__label_name",
                    )
                    .order_by("section__label_name")
                    .annotate(
                        total=Count("marks"),
                        correct=Sum("marks"),
                        percent=Sum("marks") / Count("marks") * 100,
                    )
                )

                order = []
                order = [
                    i[0]
                    for i in tmeta_difficulty_level.objects.values_list(
                        "label_name", flat=0
                    )
                ]
                order = {key: i for i, key in enumerate(order)}
                ordered_sections = sorted(
                    summary_results,
                    key=lambda i: (
                        i["section__label_name"],
                        order.get(i["question_id_id__difficulty_level__label_name"], 0),
                    ),
                )
                section_arr_table = [list(os.values()) for os in summary_results]

                ### for prof_ex
                prof_res = (
                    Responses.objects.filter(
                        user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                    )
                    .values("section__label_name")
                    .order_by("section__label_name")
                    .exclude(question_id_id__question_type=2)
                    .annotate(
                        easy_percent=Sum(
                            "marks", filter=Q(question_id_id__difficulty_level=1)
                        )
                        / Count("marks", filter=Q(question_id_id__difficulty_level=1))
                        * 100,
                        med_percent=Sum(
                            "marks", filter=Q(question_id_id__difficulty_level=2)
                        )
                        / Count("marks", filter=Q(question_id_id__difficulty_level=2))
                        * 100,
                        hard_percent=Sum(
                            "marks", filter=Q(question_id_id__difficulty_level=3)
                        )
                        / Count("marks", filter=Q(question_id_id__difficulty_level=3))
                        * 100,
                    )
                )

                prof_dict = {}
                for section_dict in prof_res:
                    sec_name = section_dict["section__label_name"]
                    prof_level = 1
                    if section_dict["easy_percent"]:
                        if section_dict["easy_percent"] > 60:
                            prof_level = 2
                    if section_dict["med_percent"]:
                        if section_dict["med_percent"] > 60:
                            prof_level = 3
                    if section_dict["hard_percent"]:
                        if section_dict["hard_percent"] > 60:
                            prof_level = 4

                    prof_dict[sec_name.capitalize()] = prof_level
                if parameters.is_coding:
                    for i in range(len(section_arr_table)):
                        if section_arr_table[i][0] == "coding":
                            code_prof = section_arr_table[i][4]
                        else:
                            code_prof = 1

                    if code_prof == 0:
                        code_level = 1
                    elif code_prof == 50:
                        code_level = 3
                    elif code_prof == 100:
                        code_level = 4
                    else:
                        code_level = 1

                    prof_dict.update({"Coding": code_level})
                created_on = Test_Assign.objects.get(
                    user_id_id=user_id, role_id_id=ds_main_roles, active_test=1
                ).created_on.strftime(" %b %d, %Y")
                prof_dict.update({"dset_date": created_on})

                if Sloved_Usecase.objects.filter(
                    upload_id_id__user_id_id=user_id,
                    role_id_id=ds_main_roles,
                    active_test=1,
                ).exists():
                    usecase_date = Sloved_Usecase.objects.get(
                        upload_id_id__user_id_id=user_id,
                        role_id_id=ds_main_roles,
                        active_test=1,
                    ).updated_at.strftime(" %b %d, %Y")

                    prof_dict.update({"usecase_date": usecase_date})
                else:
                    prof_dict.update({"usecase_date": 0})
            else:
                prof_dict = 0

        else:

            prof_dict = 0

        main_prof_dict.update({r.recommended_role.label_name: prof_dict})

        try:
            usecase = Usecase.objects.get(
                application_id_id__user_id_id=user_id,
                role_id_id=ds_main_roles,
                active_test=1,
            )
        except:
            usecase = None

        if Usecase_evaluation.objects.filter(usecase_id=usecase).exists():
            usecase_status = 1
            evaluation_list = Usecase_evaluation.objects.filter(
                usecase_id=usecase
            ).values()
            evaluation_list = evaluation_list.annotate(
                metric_value=Subquery(
                    tmeta_metric_score.objects.filter(id=OuterRef("metric_id"))[
                        :1
                    ].values("value")
                ),
            ).order_by("-metric_id")
            avg_score_list = list(
                avg_metrics_score.objects.filter(
                    role_id_id=r.recommended_role.id
                ).values()
            )
            evaluation.update(
                {r.recommended_role.label_name: list(evaluation_list.values())}
            )
            avg_score.update({r.recommended_role.label_name: list(avg_score_list)})

        else:
            usecase_status = 0

    return main_prof_dict, evaluation, avg_score, dset_status, recommended_role_list


# def xml(request):
# #Getting all of the items in the Database
# products = Product.objects.all()
# #Putting all of it in to Context to pass to template
# context = {
#    'products': products
# }
# #calling template with all  of the information
# content = render_to_string('catalog/xml_template.xml', context)
# #Saving template tp a static folder so it can be accessible without     calling view
# with open (os.path.join(BASE_DIR, 'static/test.xml'), 'w') as xmlfile:
# xmlfile.write(content.encode('utf8'))
# #Not Sure if i actually need to call the return but i did not let me run it without content
# return render(request, 'catalog/xml_template.xml', context)
def download_jd(request, pk):

    jd_form = JD_form.objects.get(id=pk)
    skill = JD_skills_experience.objects.filter(jd_id_id=pk)
    location = JD_locations.objects.filter(jd_id_id=pk)
    location = [
        (
            City.objects.filter(id=i["city"]).values("name")[0]["name"],
            State.objects.filter(id=i["state"]).values("name")[0]["name"],
            Country.objects.filter(id=i["country"]).values("name")[0]["name"],
        )
        for i in JD_locations.objects.filter(jd_id_id=pk).values(
            "country", "state", "city"
        )
    ]

    education = [
        (i["qualification"], i["specialization"])
        for i in JD_qualification.objects.filter(jd_id_id=pk).values(
            "qualification", "specialization"
        )
    ]

    prof = list(
        JD_profile.objects.filter(jd_id_id=pk).values(
            "business_intelligence",
            "data_analysis",
            "data_engineering",
            "devops",
            "machine_learning",
            "others",
        )
    )
    if len(prof) > 0:
        try:
            pie_chart(request, prof, filename="jd_" + str(pk))
            is_profiled = 1
        except IndexError:
            is_profiled = 0
    else:
        is_profiled = 0
    params = {
        "jd_form": jd_form,
        "skill": skill,
        "location": location,
        "education": education,
        "is_profiled": is_profiled,
    }

    html_template = (
        get_template("pdf/jd_download.html").render(params).encode(encoding="UTF-8")
    )
    pdf_file = HTML(string=html_template, base_url=settings.profile_pdf_url).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        "attachment; filename=jd_" + str(jd_form.job_id) + ".pdf"
    )

    return response
    # return render(request, 'pdf/jd_download.html',params)


# plt.show()
def test(request, pk, jd=None):
    try:

        if "page" in request.GET:
            if request.GET["page"] == "cpf":
                pass
            else:
                roles = [
                    i["label_name"]
                    for i in list(
                        tmeta_ds_main_roles.objects.filter(is_active=True).values(
                            "label_name"
                        )
                    )
                ]
                page_id = request.GET.getlist("page")[0]
                page_id = page_id if page_id in roles else int(page_id)
                if type(page_id) == str:
                    jd = None
                else:
                    jd = page_id
    except Exception as e:
        logger.error(str(e))
    view_contact = False
    user_id = Personal_Info.objects.get(application_id=pk).user_id_id
    if jd != None:
        # Skill match
        # jd = page_id
        jd_obj = JD_form.objects.get(id=jd)
        is_applicant = jd_candidate_analytics.objects.filter(
            candidate_id_id=pk, status_id_id=int(1), jd_id_id=jd
        ).exists()
        jd_skills = [
            i[0]
            for i in JD_skills_experience.objects.filter(jd_id_id=jd).values_list(
                "skill"
            )
        ]
        skill_list = list(set(flatten(jd_skills)))
        skill_match = JD_form.objects.filter(id=jd).values("id")
        matched_cand = Matched_candidates.objects.filter(
            application_id=pk, jd_list_id_id__zita_jd_id_id=jd
        )
        skill_match = skill_match.annotate(
            skill_match=Subquery(
                matched_cand.filter(jd_list_id_id__zita_jd_id_id=jd)[:1].values(
                    "skill_match"
                )
            ),
            profile_match=Subquery(
                matched_cand.filter(jd_list_id_id__zita_jd_id_id=jd)[:1].values(
                    "profile_match"
                )
            ),
        )
        user, resume_details, prof = get_app_prof_details(
            u_id=user_id, for_exp=True, jd_id=jd, epf=True
        )
        view_contact = jd_candidate_analytics.objects.filter(
            candidate_id_id=pk,
            status_id_id=int(17),
            jd_id_id=jd,
            recruiter_id=request.user,
        ).exists()

    else:
        skill_match = 0
        role_match = 0
        skill_list = 0
        jd_obj = 0
        is_applicant = 1
        # if request.user.is_staff:
        # else:
        # 	view_contact = False
        # function(request)
        if "page" in request.GET:
            if request.GET["page"] == "cpf":
                user, resume_details, prof = get_app_prof_details(
                    u_id=user_id, for_exp=True, jd_id=None, epf=False
                )
                is_applicant = 1
            else:
                user, resume_details, prof = get_app_prof_details(
                    u_id=user_id,
                    for_exp=True,
                    jd_id=None,
                    epf=True,
                    user_id=request.user,
                )
        else:
            user, resume_details, prof = get_app_prof_details(
                u_id=user_id, for_exp=True, jd_id=None, epf=False
            )
    current_site = get_current_site(request)
    personal = Personal_Info.objects.get(user_id=user_id)

    try:
        pie_chart(request, prof, filename=str(user_id))
        is_profiled = 1
    except IndexError:
        is_profiled = 0

    role_match = 0
    if skill_match != 0:
        if skill_match[0]["profile_match"] != None:
            role_match = skill_match[0]["profile_match"]
            name_file = str(user_id) + str(jd)
            venn_diagram(
                request, match=skill_match[0]["profile_match"], filename=name_file
            )

    main_prof_dict, evaluation, avg_score, dset_status, recommended_role_list = (
        assessment_data(request, user.application_id)
    )
    for r in main_prof_dict:
        if main_prof_dict[r] != 0:
            area_chart(
                request, main_prof_dict[r], filename="chart_" + str(r) + str(user_id)
            )
    for eva in evaluation:
        if evaluation[eva] != 0:
            redar_chart(
                request,
                evaluation[eva],
                avg_score[eva],
                filename="chart_" + eva + str(user_id),
            )
    if skill_match != 0:
        if skill_match[0]["profile_match"] != None:
            your_match = skill_match[0]["skill_match"].split(",")
            non_match = [e for e in skill_list if e not in your_match]
        else:
            your_match = None
            non_match = None
    else:
        your_match = None
        non_match = None
    params = {
        "object": resume_details,
        "is_profiled": is_profiled,
        "recommended_role_list": (" / ").join(recommended_role_list),
        "user": user,
        "domain": current_site.domain,
        "request": request,
        "personal": personal,
        "role_match": role_match,
        "main_prof_dict": main_prof_dict,
        "skill_list": skill_list,
        "your_match": your_match,
        "non_match": non_match,
        "evaluation": evaluation,
        "jd_obj": jd_obj,
        "is_applicant": is_applicant,
        "view_contact": view_contact,
        "dset_status": dset_status,
    }

    return render(request, "pdf/candidate_profile.html", params)


def generate_pdf(request, pk, jd=None):
    try:

        if "page" in request.GET:
            if request.GET["page"] == "cpf":
                pass
            else:
                roles = [
                    i["label_name"]
                    for i in list(
                        tmeta_ds_main_roles.objects.filter(is_active=True).values(
                            "label_name"
                        )
                    )
                ]
                page_id = request.GET.getlist("page")[0]
                page_id = page_id if page_id in roles else int(page_id)
                if type(page_id) == str:
                    jd = None
                else:
                    jd = page_id
    except Exception as e:
        logger.error(str(e))
    user_id = Personal_Info.objects.get(application_id=pk).user_id_id
    view_contact = False
    if jd != None:
        # Skill match
        # jd = page_id
        jd_obj = JD_form.objects.get(id=jd)
        is_applicant = jd_candidate_analytics.objects.filter(
            candidate_id_id=pk, status_id_id=int(1), jd_id_id=jd
        ).exists()
        jd_skills = [
            i[0]
            for i in JD_skills_experience.objects.filter(jd_id_id=jd).values_list(
                "skill"
            )
        ]
        skill_list = list(set(flatten(jd_skills)))
        skill_match = JD_form.objects.filter(id=jd).values("id")
        matched_cand = Matched_candidates.objects.filter(
            application_id=pk, jd_list_id_id__zita_jd_id_id=jd
        )
        skill_match = skill_match.annotate(
            skill_match=Subquery(
                matched_cand.filter(jd_list_id_id__zita_jd_id_id=jd)[:1].values(
                    "skill_match"
                )
            ),
            profile_match=Subquery(
                matched_cand.filter(jd_list_id_id__zita_jd_id_id=jd)[:1].values(
                    "profile_match"
                )
            ),
        )
        # if request.user.is_staff:
        view_contact = jd_candidate_analytics.objects.filter(
            candidate_id_id=pk,
            status_id_id=int(17),
            jd_id_id=jd,
            recruiter_id=request.user,
        ).exists()
        # else:
        # 	view_contact = False
        user, resume_details, prof = get_app_prof_details(
            u_id=user_id, for_exp=True, jd_id=jd, epf=True
        )

    else:
        skill_match = 0
        role_match = 0
        skill_list = 0
        jd_obj = 0
        is_applicant = 0
        if "page" in request.GET:
            if request.GET["page"] == "cpf":
                user, resume_details, prof = get_app_prof_details(
                    u_id=user_id, for_exp=True, jd_id=None, epf=False
                )
                is_applicant = 1
            else:
                user, resume_details, prof = get_app_prof_details(
                    u_id=user_id,
                    for_exp=True,
                    jd_id=None,
                    epf=True,
                    user_id=request.user,
                )
        else:
            user, resume_details, prof = get_app_prof_details(
                u_id=user_id, for_exp=True, jd_id=None, epf=False
            )
    current_site = get_current_site(request)
    personal = Personal_Info.objects.get(user_id=user_id)

    try:
        is_profiled = 1
        pie_chart(request, prof, filename=str(user_id))
    except IndexError:
        is_profiled = 0

    role_match = 0
    if skill_match != 0:
        if skill_match[0]["profile_match"] != None:
            role_match = skill_match[0]["profile_match"]
            name_file = str(user_id) + str(jd)
            venn_diagram(
                request, match=skill_match[0]["profile_match"], filename=name_file
            )

    main_prof_dict, evaluation, avg_score, dset_status, recommended_role_list = (
        assessment_data(request, user.application_id)
    )
    for r in main_prof_dict:
        if main_prof_dict[r] != 0:
            area_chart(
                request, main_prof_dict[r], filename="chart_" + str(r) + str(user_id)
            )
    for eva in evaluation:
        if evaluation[eva] != 0:
            redar_chart(
                request,
                evaluation[eva],
                avg_score[eva],
                filename="chart_" + eva + str(user_id),
            )
    if skill_match != 0:
        if skill_match[0]["profile_match"] != None:
            your_match = skill_match[0]["skill_match"].split(",")
            non_match = [e for e in skill_list if e not in your_match]
        else:
            your_match = None
            non_match = None
    else:
        your_match = None
        non_match = None
    media = settings.MEDIA_ROOT
    params = {
        "object": resume_details,
        "is_profiled": is_profiled,
        "recommended_role_list": (" / ").join(recommended_role_list),
        "user": user,
        "domain": current_site.domain,
        "request": request,
        "personal": personal,
        "role_match": role_match,
        "main_prof_dict": main_prof_dict,
        "skill_list": skill_list,
        "your_match": your_match,
        "non_match": non_match,
        "evaluation": evaluation,
        "jd_obj": jd_obj,
        "is_applicant": is_applicant,
        "view_contact": view_contact,
        "dset_status": dset_status,
        "media": media,
    }

    html_template = (
        get_template("pdf/candidate_profile.html")
        .render(params)
        .encode(encoding="UTF-8")
    )
    # pdf_file = HTML(string=html_template,base_url=request.build_absolute_uri()).write_pdf()
    pdf_file = HTML(string=html_template, base_url=settings.profile_pdf_url).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=Profile.pdf"
    return response


class download_interested(View):

    def get(self, request, pk, *args, **kwargs):
        jd_id = pk
        user = User.objects.get(username=request.user).id
        candidate_details = jd_candidate_analytics.objects.filter(
            status_id_id=16, jd_id_id=jd_id
        )
        interested = JD_form.objects.get(id=jd_id).job_id

        with zipfile.ZipFile(
            base_dir + "/media/candidate_profile/" + str(interested) + ".zip", "w"
        ) as myzip:
            for i in candidate_details:
                try:
                    file = generate_pdf(request, i.candidate_id_id, i.jd_id_id)
                    file_name = file["Content-Disposition"].split("=")[1]
                    file_content = open(
                        base_dir + "/media/candidate_profile/" + file_name, "wb"
                    ).write(file.content)
                    file_name = os.path.basename(file_name)
                    myzip.write(
                        base_dir + "/media/candidate_profile/" + file_name, file_name
                    )
                except Exception as e:
                    logger.error("error in download_interested : " + str(e))
                    file_name = "error.txt"
                    file_content = open(
                        base_dir + "/media/candidate_profile/" + file_name, "w"
                    ).write(
                        str(
                            "Some details are not there for the candidate ID ---- Can_"
                            + str(i.candidate_id_id)
                        )
                    )
                    file_name = os.path.basename(file_name)
                    myzip.write(
                        base_dir + "/media/candidate_profile/" + file_name, file_name
                    )
        myzip.close()
        file = open(
            base_dir + "/media/candidate_profile/" + str(interested) + ".zip", "rb"
        )
        response = HttpResponse(file, content_type="application/zip")
        response["Content-Disposition"] = (
            "attachment; filename=" + str(interested) + ".zip"
        )

        return response


class download_interested_search(View):

    def get(self, request, *args, **kwargs):

        candidate_details = jd_candidate_analytics.objects.filter(
            jd_id=None, status_id_id=16, recruiter_id_id=request.user.id
        )
        interested = "interested"

        with zipfile.ZipFile(
            base_dir + "/media/candidate_profile/" + str(interested) + ".zip", "w"
        ) as myzip:
            for i in candidate_details:
                try:
                    file = generate_pdf(request, i.candidate_id_id)
                    file_name = file["Content-Disposition"].split("=")[1]
                    file_content = open(
                        base_dir + "/media/candidate_profile/" + file_name, "wb"
                    ).write(file.content)
                    file_name = os.path.basename(file_name)
                    myzip.write(
                        base_dir + "/media/candidate_profile/" + file_name, file_name
                    )
                except Exception as e:
                    logger.error("error in download_interested_search : " + str(e))
                    file_name = "error.txt"
                    file_content = open(
                        base_dir + "/media/candidate_profile/" + file_name, "w"
                    ).write(
                        str(
                            "Some details are not there for the candidate ID ---- Can_"
                            + str(i.candidate_id_id)
                        )
                    )
                    file_name = os.path.basename(file_name)
                    myzip.write(
                        base_dir + "/media/candidate_profile/" + file_name, file_name
                    )
        myzip.close()
        file = open(
            base_dir + "/media/candidate_profile/" + str(interested) + ".zip", "rb"
        )
        response = HttpResponse(file, content_type="application/zip")
        response["Content-Disposition"] = (
            "attachment; filename=" + str(interested) + ".zip"
        )

        return response


class download_shortlist(View):

    def get(self, request, pk, *args, **kwargs):
        jd_id = pk
        user = User.objects.get(username=request.user).id
        candidate_details = jd_candidate_analytics.objects.filter(
            status_id_id=16, jd_id_id=jd_id
        ).exclude(rejected=1)
        interested = JD_form.objects.get(id=jd_id).job_id
        with zipfile.ZipFile(
            base_dir + "/media/candidate_profile/" + str(interested) + ".zip", "w"
        ) as myzip:
            for i in candidate_details:
                try:
                    file = generate_pdf(request, i.candidate_id_id, i.jd_id_id)
                    file_name = file["Content-Disposition"].split("=")[1]
                    file_content = open(
                        base_dir + "/media/candidate_profile/" + file_name, "wb"
                    ).write(file.content)
                    file_name = os.path.basename(file_name)
                    myzip.write(
                        base_dir + "/media/candidate_profile/" + file_name, file_name
                    )
                except Exception as e:
                    logger.error("error in download shortlist page : " + str(e))
                    file_name = "error.txt"
                    file_content = open(
                        base_dir + "/media/candidate_profile/" + file_name, "w"
                    ).write(
                        str(
                            "Some details are not there for the candidate ID ---- Can_"
                            + str(i.candidate_id_id)
                        )
                    )
                    file_name = os.path.basename(file_name)
                    myzip.write(
                        base_dir + "/media/candidate_profile/" + file_name, file_name
                    )
        myzip.close()
        file = open(
            base_dir + "/media/candidate_profile/" + str(interested) + ".zip", "rb"
        )
        response = HttpResponse(file, content_type="application/zip")
        response["Content-Disposition"] = (
            "attachment; filename=" + str(interested) + ".zip"
        )
        return response


# This function is to list the shorlisted candidate in the hiring process page
@login_required
@recruiter_required
def hiring_process(request):
    user = User.objects.get(username=request.user).id
    logger.info("In function hiring_process - User ID: " + str(user))
    try:
        if len(request.GET["process_status"]) > 0:
            status_id = request.GET["process_status"]
        else:
            status_id = 7
    except:
        status_id = 7
    hiring_details = jd_candidate_analytics.objects.filter(
        recruiter_id=user, status_id=7
    )
    Jobs_List = 0
    if hiring_details.exists():
        Jobs_List = 1

    location = JD_locations.objects.filter(
        jd_id__in=hiring_details.values_list("jd_id", flat=True).distinct()
    )
    location = location.annotate(
        countries=Subquery(
            Country.objects.filter(id=OuterRef("country"))[:1].values("name")
        ),
        states=Subquery(State.objects.filter(id=OuterRef("state"))[:1].values("name")),
        cities=Subquery(City.objects.filter(id=OuterRef("city"))[:1].values("name")),
    )

    location = location.annotate(
        loc=Concat(
            "cities", V(", "), "states", V(", "), "countries", output_field=CharField()
        )
    )
    hiring_details = hiring_details.annotate(
        availability=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("available_to_start")
        ),
        job_title=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_title")
        ),
        job_id=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_id")
        ),
        recommended_role=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "recommended_role"
            )
        ),
        assessment=Subquery(
            jd_candidate_analytics.objects.filter(
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=9,
            )[:1].values("candidate_id")
        ),
        tele_interview=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id=OuterRef("jd_id"),
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=10,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("candidate_id")
        ),
        shortlisted_8=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id__isnull=True,
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=8,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("shortlisted_role_id")
        ),
        shortlisted_4=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id__isnull=True,
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=4,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("shortlisted_role_id")
        ),
        shortlisted_10=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id__isnull=True,
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=10,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("shortlisted_role_id")
        ),
        shortlisted_11=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id__isnull=True,
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=11,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("shortlisted_role_id")
        ),
        shortlisted_12=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id__isnull=True,
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=12,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("shortlisted_role_id")
        ),
        inperson_interview=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id=OuterRef("jd_id"),
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=11,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("candidate_id")
        ),
        telephone_screen=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id=OuterRef("jd_id"),
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=8,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("recruiter_id")
        ),
        process_status=Subquery(
            jd_candidate_analytics.objects.filter(
                Q(jd_id=OuterRef("jd_id")) | Q(jd_id__isnull=True)
            )
            .filter(
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
                status_id=status_id,
            )[:1]
            .values("status_id")
        ),
        candidate_name=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("firstname")
        ),
        candidate_email=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("email")
        ),
        onboard=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id=OuterRef("jd_id"),
                recruiter_id=OuterRef("recruiter_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=12,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("candidate_id")
        ),
        offer=Subquery(
            jd_candidate_analytics.objects.filter(
                jd_id=OuterRef("jd_id"),
                candidate_id_id=OuterRef("candidate_id"),
                status_id=4,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
            )[:1].values("candidate_id")
        ),
    ).order_by("-updated_on")
    filters = HiringFilter(request.GET, queryset=hiring_details)
    hiring_details = filters.qs
    shortlist_candidates = len(
        hiring_details.values_list("candidate_id", flat=True).distinct()
    )
    len_list = len(
        hiring_details.values_list("jd_id", flat=True)
        .exclude(jd_id__isnull=True)
        .order_by("-jd_id")
        .distinct()
    )

    location_list = list(
        location.order_by("loc").values_list("loc", flat=True).distinct()
    )
    page = request.GET.get("page", 1)
    paginator = Paginator(hiring_details, 10)

    try:
        hiring_details = paginator.page(page)
    except PageNotAnInteger:
        hiring_details = paginator.page(1)

    except EmptyPage:
        jd_details = paginator.page(paginator.num_pages)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()

    context = {
        "hiring_details": hiring_details,
        "shortlist_candidates": shortlist_candidates,
        "filters": filters,
        "Jobs_List": Jobs_List,
        "len_list": len_list,
        "params": params,
        "location_list": json.dumps(location_list, cls=DjangoJSONEncoder),
    }

    return render(request, "jobs/hiring_process.html", context)


# This function is for setting the status of the candidate for that JD in hiring process page
@login_required
@recruiter_required
def ajax_hiring_process(request, pk=None, string=None):
    user = User.objects.get(username=request.user).id
    logger.info("In function ajax_hiring_process - User ID: " + str(user))
    if pk == "0":
        job_id = None
    else:
        job_id = pk

    candidates_id = string

    role_id = request.GET["role"].split("_")[1]

    result = 0
    if request.GET["name"] == "telephone_screen":
        result = "tele_screen"
        if jd_candidate_analytics.objects.filter(
            jd_id_id=job_id,
            candidate_id_id=candidates_id,
            recruiter_id=user,
            status_id_id=8,
            shortlisted_role_id_id=role_id,
        ).exists():
            jd_candidate_analytics.objects.filter(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=8,
                shortlisted_role_id_id=role_id,
            ).delete()
        else:
            jd_candidate_analytics.objects.create(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=8,
                shortlisted_role_id_id=role_id,
            )
    if request.GET["name"] == "assessment":
        result = "assessment"
        if jd_candidate_analytics.objects.filter(
            jd_id_id=job_id,
            candidate_id_id=candidates_id,
            recruiter_id_id=user,
            status_id_id=9,
            shortlisted_role_id_id=role_id,
        ).exists():
            jd_candidate_analytics.objects.filter(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=9,
                shortlisted_role_id_id=role_id,
            ).delete()
        else:
            jd_candidate_analytics.objects.create(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=9,
                shortlisted_role_id_id=role_id,
            )
    if request.GET["name"] == "tele_interview":
        result = "tele_interview"
        if jd_candidate_analytics.objects.filter(
            jd_id_id=job_id,
            candidate_id_id=candidates_id,
            recruiter_id_id=user,
            status_id_id=10,
            shortlisted_role_id_id=role_id,
        ).exists():
            jd_candidate_analytics.objects.filter(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=10,
                shortlisted_role_id_id=role_id,
            ).delete()
        else:
            jd_candidate_analytics.objects.create(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=10,
                shortlisted_role_id_id=role_id,
            )
    if request.GET["name"] == "inperson_interview":
        result = "inperson_interview"
        if jd_candidate_analytics.objects.filter(
            jd_id_id=job_id,
            candidate_id_id=candidates_id,
            recruiter_id_id=user,
            status_id_id=11,
            shortlisted_role_id_id=role_id,
        ).exists():
            jd_candidate_analytics.objects.filter(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=11,
                shortlisted_role_id_id=role_id,
            ).delete()
        else:
            jd_candidate_analytics.objects.create(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=11,
                shortlisted_role_id_id=role_id,
            )
    if request.GET["name"] == "offer":
        result = "offer"
        if jd_candidate_analytics.objects.filter(
            jd_id_id=job_id,
            candidate_id_id=candidates_id,
            recruiter_id_id=user,
            status_id_id=4,
            shortlisted_role_id_id=role_id,
        ).exists():
            jd_candidate_analytics.objects.filter(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=4,
                shortlisted_role_id_id=role_id,
            ).delete()
        else:
            jd_candidate_analytics.objects.create(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=4,
                shortlisted_role_id_id=role_id,
            )
    if request.GET["name"] == "onboard":
        result = "onboard"
        if jd_candidate_analytics.objects.filter(
            jd_id_id=job_id,
            candidate_id_id=candidates_id,
            recruiter_id_id=user,
            status_id_id=12,
            shortlisted_role_id_id=role_id,
        ).exists():
            pass
        else:
            jd_candidate_analytics.objects.create(
                jd_id_id=job_id,
                candidate_id_id=candidates_id,
                recruiter_id_id=user,
                status_id_id=12,
                shortlisted_role_id_id=role_id,
            )

    data = {"result": result}

    return JsonResponse(data)


# This function is for recuriter can search the candidates using the search filters in the search candidate page
@login_required
@recruiter_required
def zita_talent_pool(request):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass

    has_permission = user_permission(request, "talent_sourcing")
    if not has_permission == True:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    user_id, updated_by = admin_account(request)
    if "session_id" in request.GET:
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id = request.GET["session_id"]
        checkout = stripe.checkout.Session.retrieve(
            session_id,
        )
        metadata = checkout.get("metadata")
        product_name = metadata["product_name"]
        quantity = metadata["quantity"]
        if product_name == "Source_Credit":
            try:
                available_count = client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=11
                ).available_count
            except client_features_balance.DoesNotExist:
                client_features_balance.objects.create(
                    client_id=user_id, feature_id_id=11, available_count=0
                )
                available_count = client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=11
                ).available_count
            total = int(quantity) + available_count
            client_features_balance.objects.filter(
                client_id=user_id, feature_id_id=11
            ).update(available_count=total)
            client_addons_purchase_history.objects.create(
                client_id=user_id,
                feature_id_id=11,
                purchased_count=int(quantity),
            )
    # try:

    # 	if not subscriptions.objects.get( client_id=request.user,is_active=True).plan_id.pk >1:
    # 		messages.success(request, 'Please upgrade your plan to get the contact credits and access talent sourcing')
    # 		return redirect('payment:manage_subscription')
    # except KeyError:
    # 	pass
    show_pop = 0
    if "session_id" in request.GET:
        show_pop = 1
    elif "cancelled" in request.GET:
        show_pop = 2
    else:
        show_pop = 0
    try:
        source_limit = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=11
        ).available_count
    except:
        source_limit = 0
    try:
        candi_limit = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=12
        ).available_count
    except:
        candi_limit = 0
    state_list = list(
        State.objects.filter(country_id=231).values_list("name", flat=True)
    )
    location_id = State.objects.filter(country_id=231).values_list("id", flat=True)
    city_list = list(
        City.objects.filter(state_id__in=location_id).values_list("name", flat=True)
    )
    location = state_list + city_list
    context = {
        "show_pop": json.dumps(show_pop, cls=DjangoJSONEncoder),
        "source_limit": json.dumps(source_limit, cls=DjangoJSONEncoder),
        "source_limit": json.dumps(source_limit, cls=DjangoJSONEncoder),
        "permission": permission,
        "location": json.dumps(location, cls=DjangoJSONEncoder),
    }

    return render(request, "jobs/zita_talent_pool.html", context)


candi_id = []


def candidate_list(request, pk=None):
    if pk in candi_id:
        candi_id.remove(pk)
    else:
        candi_id.append(pk)
    request.session["candi_list"] = candi_id
    data = {"success": True}
    return JsonResponse(data)


@login_required
@recruiter_required
def bulk_action(request):
    user_id, updated_by = admin_account(request)
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    if "download" in request.GET:
        t = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
        with zipfile.ZipFile(
            base_dir + "/media/Candidates_Profiles_" + str(t) + ".zip", "w"
        ) as myzip:
            for i in request.session["candi_list"]:
                try:
                    url = (
                        "https://api.resume-library.com/v1/candidate/backfill/view/pdf/"
                        + i
                        + "/all/zita-"
                        + str(user_id.id)
                    )

                    result = requests.get(
                        url, auth=(settings.rl_username, settings.rl_password)
                    )
                    result = json.loads(result.content)
                    try:
                        data = result["result"]["pages"][0]["content"]
                    except:
                        data = result["result"]["pages"]["content"]
                    byte = b64decode(data, validate=True)

                    if byte[0:4] != b"%PDF":
                        raise ValueError("Missing the PDF file signature")
                    f = open(
                        base_dir
                        + "/media/"
                        + result["first_name"]
                        + "_"
                        + result["id"]
                        + ".pdf",
                        "wb",
                    )
                    f.write(byte)
                    f.close()
                    myzip.write(
                        base_dir
                        + "/media/"
                        + result["first_name"]
                        + "_"
                        + result["id"]
                        + ".pdf",
                        result["first_name"] + "_" + result["id"] + ".pdf",
                    )
                except:
                    pass
        myzip.close()
        file = open(base_dir + "/media/Candidates_Profiles_" + str(t) + ".zip", "rb")
        response = HttpResponse(file, content_type="application/zip")
        response["Content-Disposition"] = (
            "attachment; filename=Candidates_Profiles_" + str(t) + ".zip"
        )
        return response
    elif "unlock" in request.GET:
        t = datetime.now()
        unlock_can_list = []
        if not "manage_account_settings" in permission:
            data = {"success": 3}
            return JsonResponse(data)
        try:

            source = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            )
        except:
            data = {"success": False}
            return JsonResponse(data)
        candi_limit = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=12
        )

        if candi_limit.available_count != None:
            if candi_limit.available_count == 0 or candi_limit.available_count < len(
                request.session["candi_list"]
            ):
                data = {"success": 2}
                return JsonResponse(data)
        if source.available_count < len(request.session["candi_list"]):
            data = {"success": False}
            return JsonResponse(data)
        else:
            source_limit = source.available_count
        if candi_limit.available_count != None:
            if candi_limit.available_count < len(request.session["candi_list"]):
                data = {"success": 2}
                return JsonResponse(data)
        count = 0
        for i in request.session["candi_list"]:
            try:
                url = (
                    "https://api.resume-library.com/v1/candidate/backfill/unlock/pdf/"
                    + i
                    + "/all/zita-"
                    + str(user_id.id)
                )

                result = requests.get(
                    url, auth=(settings.rl_username, settings.rl_password)
                )
                result = json.loads(result.content)
                t = datetime.now()
                try:
                    data = result["result"]["pages"][0]["content"]
                except:
                    data = result["result"]["pages"]["content"]
                byte = b64decode(data, validate=True)
                if byte[0:4] != b"%PDF":
                    raise ValueError("Missing the PDF file signature")
                file = open(
                    base_dir
                    + "/media/unlock/"
                    + result["first_name"]
                    + "_"
                    + result["id"]
                    + ".pdf",
                    "wb",
                )
                file.write(byte)
                file.close()
                try:
                    job_type = tmeta_job_type.objects.get(label_name=result["job_type"])
                except:
                    job_type = None

                relocate = None
                if result["willing_to_relocate"] == "Yes":
                    relocate = True
                elif result["willing_to_relocate"] == "No":
                    relocate = False
                state = result["town"].split(",")[1]
                city = result["town"].split(",")[0]
                try:
                    countries_states = pd.read_csv(
                        base_dir + "/" + "media/countries_states.csv"
                    )
                except:
                    countries_states = pd.read_csv(
                        os.getcwd() + "/" + "media/countries_states.csv"
                    )

                for i in range(len(countries_states["state_code"])):
                    if countries_states["state_code"][i] == state.strip().lower():
                        state = countries_states["state"][i]
                location = city + ", " + state.upper()
                if employer_pool.objects.filter(
                    email=result["email"], client_id=user_id
                ).exists():
                    employer_pool.objects.filter(email=result["email"]).update(
                        can_source_id=2,
                        client_id=user_id,
                        updated_by=updated_by,
                        candidate_id=None,
                        job_type=job_type,
                        first_name=result["first_name"],
                        last_name=result["last_name"],
                        email=result["email"],
                        candi_ref_id=result["id"],
                        work_exp=result["work_experience"],
                        relocate=relocate,
                        qualification=result["educational_level"],
                        exp_salary=str(result["min_expected_salary"])
                        + " - "
                        + str(result["max_expected_salary"]),
                        job_title=result["desired_job_title"],
                        skills=",".join(result["key_skills"]),
                        location=location,
                    )
                    emp_pool = employer_pool.objects.get(
                        email=result["email"], client_id=user_id
                    )
                else:
                    employer_pool.objects.create(
                        can_source_id=2,
                        client_id=user_id,
                        updated_by=updated_by,
                        candidate_id=None,
                        job_type=job_type,
                        candi_ref_id=result["id"],
                        first_name=result["first_name"],
                        last_name=result["last_name"],
                        email=result["email"],
                        work_exp=result["work_experience"],
                        relocate=relocate,
                        qualification=result["educational_level"],
                        exp_salary=str(result["min_expected_salary"])
                        + " - "
                        + str(result["max_expected_salary"]),
                        job_title=result["desired_job_title"],
                        skills=",".join(result["key_skills"]),
                        location=location,
                    )
                    emp_pool = employer_pool.objects.filter(
                        client_id=user_id,
                        email=result["email"],
                    ).last()
                unlock_can_list.append(
                    str(emp_pool.id) + "##" + result["first_name"] + "_" + result["id"]
                )
                count = count + 1

            except:
                pass
        source.available_count = source.available_count - count
        source.save()
        if candi_limit.available_count != None:
            candi_limit.available_count = candi_limit.available_count - count
            candi_limit.save()
            candi_limit = candi_limit.available_count
        else:
            candi_limit = "Unlimited"
        if count > 0:
            if count == 1:
                UserActivity.objects.create(
                    user=request.user,
                    action_id=4,
                    action_detail=str(count) + " candidate from Talent Sourcing",
                )
            else:
                UserActivity.objects.create(
                    user=request.user,
                    action_id=4,
                    action_detail=str(count) + " candidates from Talent Sourcing",
                )

        try:
            source = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            ).available_count
        except:
            source = 0

        data = {
            "success": True,
            "unlock_can_list": unlock_can_list,
            "source_limit": source,
            "candi_limit": candi_limit,
        }
        return JsonResponse(data)
    else:
        return HttpResponse("Please try again later")


@login_required
@recruiter_required
def unlock_candidates(request):
    user_id, updated_by = admin_account(request)
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    if not "manage_account_settings" in permission:
        data = {"success": 3}
        return JsonResponse(data)
    candi_limit = client_features_balance.objects.get(
        client_id=user_id, feature_id_id=12
    )
    if candi_limit.available_count == 0:
        data = {"success": 2}
        return JsonResponse(data)
    try:
        source_limit = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=11
        )
        if source_limit.available_count == 0:
            data = {"success": False}
            return JsonResponse(data)
    except:
        data = {"success": False}
        return JsonResponse(data)
    candidate_key = request.GET["key"]
    url = (
        "https://api.resume-library.com/v1/candidate/backfill/unlock/pdf/"
        + candidate_key
        + "/all/zita-"
        + str(user_id.id)
    )
    unlock_can_list = []

    # global data_rl
    # # data_rl=data_rl[data_rl['candidate_hash']== candidate_key]

    result = requests.get(url, auth=(settings.rl_username, settings.rl_password))
    result = json.loads(result.content)
    try:
        data = result["result"]["pages"][0]["content"]
    except:
        data = result["result"]["pages"]["content"]
    byte = b64decode(data, validate=True)
    if byte[0:4] != b"%PDF":
        raise ValueError("Missing the PDF file signature")
    file = open(
        base_dir
        + "/media/unlock/"
        + result["first_name"]
        + "_"
        + result["id"]
        + ".pdf",
        "wb",
    )
    file.write(byte)
    file.close()
    try:
        job_type = tmeta_job_type.objects.get(label_name=result["job_type"])
    except:
        job_type = None

    relocate = None
    if result["willing_to_relocate"] == "Yes":
        relocate = True
    elif result["willing_to_relocate"] == "No":
        relocate = False
    state = result["town"].split(",")[1]
    city = result["town"].split(",")[0]
    try:
        countries_states = pd.read_csv(base_dir + "/" + "media/countries_states.csv")
    except:
        countries_states = pd.read_csv(os.getcwd() + "/" + "media/countries_states.csv")

    for i in range(len(countries_states["state_code"])):
        if countries_states["state_code"][i] == state.strip().lower():
            state = countries_states["state"][i]
    location = city + ", " + state.upper()
    if employer_pool.objects.filter(email=result["email"], client_id=user_id).exists():
        employer_pool.objects.filter(email=result["email"]).update(
            can_source_id=2,
            client_id=user_id,
            updated_by=updated_by,
            candidate_id=None,
            job_type=job_type,
            first_name=result["first_name"],
            last_name=result["last_name"],
            email=result["email"],
            work_exp=result["work_experience"],
            relocate=relocate,
            candi_ref_id=result["id"],
            qualification=result["educational_level"],
            exp_salary=str(result["min_expected_salary"])
            + " - "
            + str(result["max_expected_salary"]),
            job_title=result["desired_job_title"],
            skills=",".join(result["key_skills"]),
            location=location,
        )
        emp_pool = employer_pool.objects.get(email=result["email"], client_id=user_id)
    else:
        employer_pool.objects.create(
            can_source_id=2,
            client_id=user_id,
            updated_by=updated_by,
            candidate_id=None,
            job_type=job_type,
            candi_ref_id=result["id"],
            first_name=result["first_name"],
            last_name=result["last_name"],
            email=result["email"],
            work_exp=result["work_experience"],
            relocate=relocate,
            qualification=result["educational_level"],
            exp_salary=str(result["min_expected_salary"])
            + " - "
            + str(result["max_expected_salary"]),
            job_title=result["desired_job_title"],
            skills=",".join(result["key_skills"]),
            location=location,
        )
        emp_pool = employer_pool.objects.filter(
            email=result["email"], client_id=user_id
        ).last()
    unlock_can_list.append(
        str(emp_pool.id) + "##" + result["first_name"] + "_" + result["id"]
    )
    # try:
    source_limit.available_count = source_limit.available_count - 1
    source_limit.save()
    source_limit = source_limit.available_count
    if candi_limit.available_count != None:
        candi_limit.available_count = candi_limit.available_count - 1
        candi_limit.save()
        candi_limit = candi_limit.available_count
    else:
        candi_limit = "Unlimited"

    UserActivity.objects.create(
        user=request.user,
        action_id=4,
        action_detail="1 candidate from Talent Sourcing",
    )

    data = {
        "success": True,
        "unlock_can_list": unlock_can_list,
        "source_limit": source_limit,
        "candi_limit": candi_limit,
    }
    return JsonResponse(data)


def parsed_text(request):
   
    for i in request.GET.getlist("unlock_can_list[]"):
        emp_pool_id = i.split("##")[0]
        user_id = None
        if employer_pool.objects.filter(id =emp_pool_id).exists():
            user_id = employer_pool.objects.get(id =emp_pool_id).user_id
        
        talent_pool_id = i.split("##")[1]
        parser_output = resume_parsing(str(talent_pool_id) + ".pdf",user_id=user_id)
        if candidate_parsed_details.objects.filter(
            candidate_id_id=int(emp_pool_id)
        ).exists():

            candidate_parsed_details.objects.filter(
                candidate_id_id=int(emp_pool_id)
            ).update(
                candidate_id_id=int(emp_pool_id),
                parsed_text=parser_output,
                resume_file_path="unlock/" + str(talent_pool_id) + ".pdf",
            )
        else:
            candidate_parsed_details.objects.create(
                candidate_id_id=int(emp_pool_id),
                parsed_text=parser_output,
                resume_file_path="unlock/" + str(talent_pool_id) + ".pdf",
            )
        result = generate_candidate_json(request, pk=int(emp_pool_id))
    data = {"success": True}
    return JsonResponse(data)


def parsing_rl(filename):
    tmp_path = os.getcwd()
    headers = {"Authorization": settings.rp_api_auth_token}

    url = settings.rp_api_url

    # files = {'resume_file': open('/home/server/zita/django/zita/media/resume/'+filename,'rb')}

    try:
        files = {
            "resume_file": open(os.getcwd() + "/" + "media/resume/" + filename, "rb")
        }
    except:

        files = {"resume_file": open(base_dir + "/" + "media/resume/" + filename, "rb")}

    result = requests.post(url, headers=headers, files=files)
    respone_json = json.loads(result.content)

    try:
        r_data = respone_json["file_data"]
    except:
        r_data = {}

    try:
        sample = respone_json["result_dict"]
    except:
        sample = {}
    try:
        sentence_list = respone_json["sentence_list"]
    except:
        sentence_list = "[]"
    # with open('/home/server/zita/django/zita/media/SOT_OUT/'+filename+'.json', 'w') as fp:
    try:
        with open(base_dir + "/" + "media/SOT_OUT/" + filename + ".json", "w") as fp:
            json.dump(sample, fp)
        with open(
            base_dir + "/" + "media/SOT_OUT/" + filename + "_data.json", "w"
        ) as fp:
            json.dump(r_data, fp)
    except:
        with open(os.getcwd() + "/" + "media/SOT_OUT/" + filename + ".json", "w") as fp:
            json.dump(sample, fp)
        with open(
            os.getcwd() + "/" + "media/SOT_OUT/" + filename + "_data.json", "w"
        ) as fp:
            json.dump(r_data, fp)

    os.chdir(tmp_path)

    return sentence_list


def resume_parsing(filename,user_id = None):
    # headers = {'Authorization': settings.rp_api_auth_token }
    # url = settings.rp_api_url

    # try:
    #     files = {'resume_file': open(os.getcwd()+'/'+'media/unlock/'+filename,'rb')}
    # except:

    #     files = {'resume_file': open(base_dir+'/'+'media/unlock/'+filename,'rb')}
    # result = requests.post(url, headers = headers, files=files)
    # respone_json = json.loads(result.content)

    # try:
    #     parser_output = respone_json['result_dict']
    # except:
    #     parser_output= {}

    # return parser_output
    try:
        files = {
            "resume_file": open(os.getcwd() + "/" + "media/unlock/" + filename, "rb")
        }
    except:

        files = {"resume_file": open(base_dir + "/" + "media/unlock/" + filename, "rb")}
    # result = requests.post(url, headers = headers, files=files)
    result, count_total, raw_text = resume_parser_AI(
        files["resume_file"].name, files["resume_file"].name,user_id=user_id
    )
    respone_json = json.loads(result)
    try:
        parser_output = respone_json
        raw_text = raw_text
    except Exception as e:
        logger.info("Exception" + str(e))
        parser_output = {}
        raw_text = None
    return parser_output, raw_text


def url_call(data):
    try:
        headers = {"Content-Type": "application/json"}
        result = requests.post(
            settings.rl_search_url,
            json=data,
            headers=headers,
            auth=(settings.rl_username, settings.rl_password),
        )
        result = json.loads(result.content)
        data_rl = result["candidates"]
    except:
        data_rl = None

    return data_rl


class zita_talent_pool_ajax(View):

    def get(self, request):
        user_id, updated_by = admin_account(request)
        global data_rl
        global candi_id
        select = 0
        no_search = 1
        if "filter" in self.request.GET:
            filter_data = pd.DataFrame(data_rl)
            if "relocate" in self.request.GET:
                filter_data = filter_data[filter_data["relocate"] == "1"]
            if "education_level" in self.request.GET:
                if len(self.request.GET["education_level"]) > 0:
                    filter_data = filter_data[
                        filter_data["education_level"].isin(
                            self.request.GET.getlist("education_level")
                        )
                    ]
            if len(self.request.GET["work_experience"]) > 0:
                filter_data = filter_data[
                    filter_data["work_experience"]
                    == self.request.GET["work_experience"]
                ]
            if "select" in self.request.GET:
                if self.request.GET["select"] == "add":
                    filter_data = filter_data[filter_data["unlock_status"] == "locked"]
                    request.session["candi_list"] = filter_data[
                        "candidate_hash"
                    ].tolist()
                    select = 1
                else:
                    select = 0
                    request.session["candi_list"] = []
            else:
                candi_id.clear()
                request.session["candi_list"] = candi_id
            filter_data = filter_data.to_dict("records")
            page = request.GET.get("page", 1)
            paginator = Paginator(filter_data, 10)
            no_search = 0

        elif "page" in self.request.GET:
            data_rl = data_rl
            page = request.GET.get("page", 1)

            paginator = Paginator(data_rl, 10)
            no_search = 0
        else:
            if len(self.request.GET["keywords"]) > 0:
                try:
                    countries_states = pd.read_csv(
                        base_dir + "/" + "media/countries_states.csv"
                    )
                except:
                    countries_states = pd.read_csv(
                        os.getcwd() + "/" + "media/countries_states.csv"
                    )
                if (
                    request.GET["location"].lower()
                    in countries_states["state"].to_list()
                ):
                    location = "state of " + self.request.GET["location"]
                else:
                    location = self.request.GET["location"]
                data = {
                    "keywords": self.request.GET["keywords"],
                    "partner_user_ref": "zita-" + str(user_id.id),
                    "location": location,
                    "radius": self.request.GET["radius"],
                    "active_within_days": self.request.GET["last_active"],
                    "limit": 100,
                }
                candi_id.clear()
                request.session["candi_list"] = candi_id
                data_rl = url_call(data)
                no_search = 0
            else:
                data_rl = User.objects.none()
            if data_rl == None:
                data_rl = User.objects.none()

            page = request.GET.get("page", 1)
            paginator = Paginator(data_rl, 10)
        try:
            request.session["candi_list"] = request.session["candi_list"]
        except:
            request.session["candi_list"] = []
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)

        except EmptyPage:
            data = paginator.page(paginator.num_pages)
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            ).available_count
        except:
            source_limit = 0
        try:
            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=12
            ).available_count
        except:
            candi_limit = 0
        candi_list = employer_pool.objects.filter(
            client_id=user_id, can_source_id=2
        ).values_list("candi_ref_id", flat=True)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        plan = subscriptions.objects.get(client_id=user_id, is_active=True)
        context = {
            "data": data,
            "params": params,
            "source_limit": source_limit,
            "select": select,
            "candi_limit": candi_limit,
            "no_search": no_search,
            "plan": plan,
            "permission": permission,
            "candi_list": json.dumps(list(candi_list), cls=DjangoJSONEncoder),
            "candi_id": request.session["candi_list"],
        }
        # return JsonResponse(context)
        return render(request, "jobs/zita_talent_pool_ajax.html", context)


from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.response import Response


class zita_talent_pool_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            if int(self.request.session["expire_in"]) <= 0:
                return redirect("payment:manage_subscription")
        except KeyError:
            pass

        has_permission = user_permission(self.request, "talent_sourcing")
        if not has_permission == True:
            permission = Permission.objects.filter(user=self.request.user).values_list(
                "codename", flat=True
            )
            return render(
                self.request, "jobs/no_permission.html", {"permission": permission}
            )
        permission = Permission.objects.filter(user=self.request.user).values_list(
            "codename", flat=True
        )
        user_id, updated_by = admin_account(self.request)
        if "session_id" in self.request.GET:
            import stripe

            stripe.api_key = settings.STRIPE_SECRET_KEY
            session_id = self.request.GET["session_id"]
            checkout = stripe.checkout.Session.retrieve(
                session_id,
            )
            metadata = checkout.get("metadata")
            product_name = metadata["product_name"]
            quantity = metadata["quantity"]
            if product_name == "Source_Credit":
                try:
                    available_count = client_features_balance.objects.get(
                        client_id=user_id, feature_id_id=11
                    ).available_count
                except client_features_balance.DoesNotExist:
                    client_features_balance.objects.create(
                        client_id=user_id, feature_id_id=11, available_count=0
                    )
                    available_count = client_features_balance.objects.get(
                        client_id=user_id, feature_id_id=11
                    ).available_count
                total = int(quantity) + available_count
                client_features_balance.objects.filter(
                    client_id=user_id, feature_id_id=11
                ).update(available_count=total)
                client_addons_purchase_history.objects.create(
                    client_id=user_id,
                    feature_id_id=11,
                    purchased_count=int(quantity),
                )
        show_pop = 0
        if "session_id" in self.request.GET:
            show_pop = 1
        elif "cancelled" in self.request.GET:
            show_pop = 2
        else:
            show_pop = 0
        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            ).available_count
        except:
            source_limit = 0
        try:
            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=12
            ).available_count
        except:
            candi_limit = 0
        state_list = list(
            State.objects.filter(country_id=231).values_list("name", flat=True)
        )
        location_id = State.objects.filter(country_id=231).values_list("id", flat=True)
        city_list = list(
            City.objects.filter(state_id__in=location_id).values_list("name", flat=True)
        )
        location = state_list + city_list
        context = {
            "show_pop": show_pop,
            "source_limit": source_limit,
            "source_limit": source_limit,
            "permission": list(permission),
            "location": location,
        }
        return Response(context)


class zita_talent_pool_search_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(request)
        if len(self.request.GET["keywords"]) > 0:
            try:
                countries_states = pd.read_csv(
                    base_dir + "/" + "media/countries_states.csv"
                )
            except:
                countries_states = pd.read_csv(
                    os.getcwd() + "/" + "media/countries_states.csv"
                )
            if request.GET["location"].lower() in countries_states["state"].to_list():
                location = "state of " + self.request.GET["location"]
            else:
                location = self.request.GET["location"]
            data = {
                "keywords": self.request.GET["keywords"],
                "partner_user_ref": "zita-" + str(user_id.id),
                "location": location,
                "radius": self.request.GET["radius"],
                "active_within_days": self.request.GET["last_active"],
                "limit": 100,
            }
            data_rl = url_call(data)
        else:
            data_rl = User.objects.none()

        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            ).available_count
        except:
            source_limit = 0
        try:
            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=12
            ).available_count
        except:
            candi_limit = 0
        candi_list = employer_pool.objects.filter(
            client_id=user_id, can_source_id=2
        ).values_list("candi_ref_id", flat=True)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        plan = subscriptions.objects.filter(client_id=user_id, is_active=True).values()
        context = {
            "data": data_rl,
            "source_limit": source_limit,
            "candi_limit": candi_limit,
            "plan": list(plan),
            "permission": list(permission),
            "candi_list": list(candi_list),
        }
        return Response(context)


# @api_view(['GET', 'POST'])
def candidate_view_api(request):
    unlock_can_list = []
    user_id, updated_by = admin_account(request)
    candidate_key = request.GET["key"]
    url = (
        "https://api.resume-library.com/v1/candidate/backfill/view/pdf/"
        + candidate_key
        + "/all/zita-"
        + str(user_id.id)
    )

    result = requests.get(url, auth=(settings.rl_username, settings.rl_password))
    result = json.loads(result.content)
    data = result["result"]["pages"][0]["content"]
    byte = b64decode(data, validate=True)

    if byte[0:4] != b"%PDF":
        raise ValueError("Missing the PDF file signature")
    # f = open('media/data.pdf', 'wb')
    try:
        f = open(base_dir + "/" + "media/data.pdf", "wb")
    except:
        f = open(os.getcwd() + "/" + "media/data.pdf", "wb")
    f.write(byte)
    f.close()
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    context = {
        "file": f,
        "permission": permission,
        "candidate_key": candidate_key,
        "unlock_status": result["unlock_status"],
        "unlock_can_list": json.dumps(unlock_can_list, cls=DjangoJSONEncoder),
    }

    return Response(context)


# import requests
# import json
# from requests.auth import HTTPBasicAuth

from base64 import b64decode


@login_required
@recruiter_required
def candidate_view(request):
    unlock_can_list = []
    user_id, updated_by = admin_account(request)
    if "unlock" in request.GET:
        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            )
        except:
            source_limit = 0
            messages.success(
                request,
                "Not enough sourcing candidates to unlock, please buy more & proceed",
            )
            return redirect("/jobs/candidate_view?key=" + request.GET["key"])
        if source_limit.available_count == 0:
            messages.success(
                request,
                "Not enough sourcing candidates to unlock, please buy more & proceed",
            )
            return redirect("/jobs/candidate_view?key=" + request.GET["key"])
        else:
            source_limit.available_count = source_limit.available_count - 1
            source_limit.save()
        candidate_key = request.GET["key"]
        url = (
            "https://api.resume-library.com/v1/candidate/backfill/unlock/pdf/"
            + candidate_key
            + "/all/zita-"
            + str(user_id.id)
        )
        result = requests.get(url, auth=(settings.rl_username, settings.rl_password))
        result = json.loads(result.content)
        try:
            data = result["result"]["pages"][0]["content"]
        except:
            data = result["result"]["pages"]["content"]
        byte = b64decode(data, validate=True)
        if byte[0:4] != b"%PDF":
            raise ValueError("Missing the PDF file signature")
        file = open(
            base_dir
            + "/media/unlock/zita-"
            + str(request.user.id)
            + "-"
            + result["id"]
            + ".pdf",
            "wb",
        )
        file.write(byte)
        file.close()
        try:
            job_type = tmeta_job_type.objects.get(label_name=result["job_type"])
        except:
            job_type = None
        relocate = False
        if result["willing_to_relocate"] == "Yes":
            relocate = True
        if employer_pool.objects.filter(email=result["email"]).exists():
            employer_pool.objects.filter(email=result["email"]).update(
                can_source_id=2,
                client_id=user_id,
                updated_by=updated_by,
                candidate_id=None,
                job_type=job_type,
                first_name=result["first_name"],
                last_name=result["last_name"],
                email=result["email"],
                candi_ref_id=result["id"],
                work_exp=result["work_experience"],
                relocate=relocate,
                qualification=result["educational_level"],
                exp_salary=str(result["min_expected_salary"])
                + " - "
                + str(result["max_expected_salary"]),
                job_title=result["desired_job_title"],
                skills=",".join(result["key_skills"]),
                location=result["town"],
            )
            emp_pool = employer_pool.objects.get(email=result["email"])
        else:
            employer_pool.objects.create(
                can_source_id=2,
                client_id=user_id,
                updated_by=updated_by,
                candidate_id=None,
                job_type=job_type,
                first_name=result["first_name"],
                last_name=result["last_name"],
                email=result["email"],
                candi_ref_id=result["id"],
                work_exp=result["work_experience"],
                relocate=relocate,
                qualification=result["educational_level"],
                exp_salary=str(result["min_expected_salary"])
                + " - "
                + str(result["max_expected_salary"]),
                job_title=result["desired_job_title"],
                skills=",".join(result["key_skills"]),
                location=result["town"],
            )
            emp_pool = employer_pool.objects.filter(client_id=user_id).last()
        unlock_can_list.append(str(emp_pool.id) + "-" + str(result["id"]))
        import time

        time.sleep(1)
    candidate_key = request.GET["key"]
    url = (
        "https://api.resume-library.com/v1/candidate/backfill/view/pdf/"
        + candidate_key
        + "/all/zita-"
        + str(user_id.id)
    )

    result = requests.get(url, auth=(settings.rl_username, settings.rl_password))
    result = json.loads(result.content)
    data = result["result"]["pages"][0]["content"]
    byte = b64decode(data, validate=True)

    if byte[0:4] != b"%PDF":
        raise ValueError("Missing the PDF file signature")
    # f = open('media/data.pdf', 'wb')
    try:
        f = open(base_dir + "/" + "media/data.pdf", "wb")
    except:
        f = open(os.getcwd() + "/" + "media/data.pdf", "wb")
    f.write(byte)
    f.close()
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    context = {
        "file": f,
        "permission": permission,
        "candidate_key": candidate_key,
        "unlock_status": result["unlock_status"],
        "unlock_can_list": json.dumps(unlock_can_list, cls=DjangoJSONEncoder),
    }

    return render(request, "jobs/candidate_view_rl.html", context)


# This function for the recruiter can filter the already shortlisted candidates from the search candidate page
@login_required
@recruiter_required
def interested_candidates(request):
    data = request.GET
    user = User.objects.get(username=request.user).id
    candidate_id = jd_candidate_analytics.objects.filter(
        jd_id=None, interested=1, recruiter_id_id=user
    )
    recommended_role = Recommended_Role.objects.filter(
        application_id__in=candidate_id.values_list(
            "candidate_id", flat=True
        ).distinct()
    )
    recommended_role = recommended_role.annotate(
        roles=Subquery(
            tmeta_ds_main_roles.objects.filter(id=OuterRef("recommended_role")).values(
                "label_name"
            )
        ),
    )
    candidate_details = candidate_id.annotate(
        exp_year=Subquery(
            Additional_Details.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("total_exp_year")
        ),
        exp_month=Subquery(
            Additional_Details.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("total_exp_month")
        ),
        edu_title=Subquery(
            Education.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("qual_title")
        ),
        validation=Subquery(
            User_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("val_status_2recruiter")
        ),
        edu_spec=Subquery(
            Education.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("qual_spec")
        ),
        tech_skill=Subquery(
            Skills.objects.filter(application_id=OuterRef("candidate_id"))[:1].values(
                "tech_skill"
            )
        ),
        role=Subquery(
            recommended_role.filter(application_id=OuterRef("candidate_id"))
            .values("application_id")
            .annotate(name=Concats("roles"))
            .values("name")[:1],
            output_field=CharField(),
        ),
        hiring_status=Subquery(
            jd_candidate_analytics.objects.filter(
                candidate_id=OuterRef("candidate_id"),
                recruiter_id=OuterRef("recruiter_id"),
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
                jd_id=None,
                status_id__in=[8, 9, 10, 11, 12, 4],
            )[:1].values("candidate_id")
        ),
        available_to_start=Subquery(
            Personal_Info.objects.filter(
                application_id=OuterRef("candidate_id")
            ).values("available_to_start__label_name")[:1]
        ),
        type_of_job=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("type_of_job")
        ),
        pre_country1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current_country")
        ),
        pre_state1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current_state")
        ),
        pre_city1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current_city")
        ),
    ).order_by("-updated_on")

    candidate_details = candidate_details.annotate(
        pre_country=Subquery(
            Country.objects.filter(id=OuterRef("pre_country1"))[:1].values("name")
        ),
        pre_state=Subquery(
            State.objects.filter(id=OuterRef("pre_state1"))[:1].values("name")
        ),
        pre_city=Subquery(
            City.objects.filter(id=OuterRef("pre_city1"))[:1].values("name")
        ),
    )
    candidate_details = candidate_details.annotate(
        location=Concat("pre_state", V(", "), "pre_country", output_field=CharField())
    )
    location_list = list(
        candidate_details.order_by("location")
        .values_list("location", flat=True)
        .distinct()
    )
    shortlist_list = jd_candidate_analytics.objects.filter(
        jd_id=None, status_id=7, recruiter_id_id=user
    )
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")

    filters = InterestedCandFilters(data, queryset=candidate_details)
    candidate_details = filters.qs
    len_list = candidate_details.count()

    page = request.GET.get("page", 1)
    paginator = Paginator(candidate_details, 10)

    try:
        candidate_details = paginator.page(page)
    except PageNotAnInteger:
        candidate_details = paginator.page(1)

    except EmptyPage:
        candidate_details = paginator.page(paginator.num_pages)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()

    skill_match_list = data.getlist("skill_match")
    context = {
        "candidate_details": candidate_details,
        "filters": filters,
        "len_list": len_list,
        "params": params,
        "shortlist_list": shortlist_list,
        "data_list": json.dumps(data, cls=DjangoJSONEncoder),
        "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        "skill_match_list": json.dumps(skill_match_list, cls=DjangoJSONEncoder),
        "location_list": json.dumps(location_list, cls=DjangoJSONEncoder),
    }

    return render(request, "jobs/interested_candidates.html", context)


def interested_candidates_ajax(request):
    data = request.GET
    user = User.objects.get(username=request.user).id
    contact_waiting_list = jd_candidate_analytics.objects.filter(
        status_id_id=15, interested=1, recruiter_id_id=user
    ).count()
    if "delete_id" in data:
        app_id = request.GET["delete_id"]
        role_id = request.GET["delete_role"]
        jd_candidate_analytics.objects.filter(
            candidate_id_id=app_id,
            shortlisted_role_id_id=role_id,
            status_id__in=[13, 15],
        ).delete()
        try:
            notes = Candidate_notes.objects.get(
                recruiter_id=request.user, candidate_id_id=app_id, jd_id=None
            ).notes
        except:
            Candidate_notes.objects.create(
                recruiter_id=request.user, candidate_id_id=app_id, jd_id=None
            )
            notes = ""
        time = datetime.date.today()
        notes = (
            notes
            + "\n"
            + str(time.strftime("%b %d, %Y"))
            + ": The Candidate has been removed from my interested page"
        )
        Candidate_notes.objects.filter(
            recruiter_id=request.user, candidate_id_id=app_id
        ).update(notes=notes)
        data = {"success": True}
        return JsonResponse(data)
    if "count" in data:
        return JsonResponse({"count": contact_waiting_list})
    jd_candidate_analytics.objects.filter(
        status_id_id=16, jd_id=None, recruiter_id=request.user
    ).delete()
    candidate_id = jd_candidate_analytics.objects.filter(
        jd_id=None, interested=1, recruiter_id_id=user
    )

    skill_match_list = data.getlist("skill_match")

    try:
        candidate_details = Personal_Info.objects.filter(
            reduce(
                operator.or_,
                (Q(skills__tech_skill__icontains=item) for item in skill_match_list),
            )
        )
        candidate_id = jd_candidate_analytics.objects.filter(
            jd_id=None,
            interested=1,
            recruiter_id_id=user,
            candidate_id__in=candidate_details,
        )
    except Exception as e:
        pass
    try:
        if len(data["total_exp_year"]) > 0:
            data_profile = data["total_exp_year"].split("-")
            data._mutable = True
            data["total_exp_year_min"] = data_profile[0]
            data["total_exp_year_max"] = data_profile[1]
    except:
        data._mutable = True
        data["total_exp_year"] = ""

    recommended_role = Recommended_Role.objects.filter(
        application_id__in=candidate_id.values_list(
            "candidate_id", flat=True
        ).distinct()
    )
    recommended_role = recommended_role.annotate(
        roles=Subquery(
            tmeta_ds_main_roles.objects.filter(id=OuterRef("recommended_role")).values(
                "label_name"
            )
        ),
    )

    candidate_details = candidate_id.annotate(
        availability=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("available_to_start")
        ),
        exp_year=Subquery(
            Additional_Details.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("total_exp_year")
        ),
        exp_month=Subquery(
            Additional_Details.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("total_exp_month")
        ),
        edu_title=Subquery(
            Education.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("qual_title")
        ),
        validation=Subquery(
            User_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("val_status_2recruiter")
        ),
        edu_spec=Subquery(
            Education.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("qual_spec")
        ),
        tech_skill=Subquery(
            Skills.objects.filter(application_id=OuterRef("candidate_id"))[:1].values(
                "tech_skill"
            )
        ),
        role=Subquery(
            recommended_role.filter(application_id=OuterRef("candidate_id"))
            .values("application_id")
            .annotate(name=Concats("roles"))
            .values("name")[:1],
            output_field=CharField(),
        ),
        relocate=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("relocate")
        ),
        is_contacted=Subquery(
            jd_candidate_analytics.objects.filter(
                candidate_id=OuterRef("candidate_id"),
                status_id__in=[13, 7],
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
                recruiter_id=OuterRef("recruiter_id"),
            )[:1].values("contacted")
        ),
        is_contact_waiting=Subquery(
            jd_candidate_analytics.objects.filter(
                candidate_id=OuterRef("candidate_id"),
                status_id=15,
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
                recruiter_id=OuterRef("recruiter_id"),
            )[:1].values("status_id")
        ),
        hiring_status=Subquery(
            jd_candidate_analytics.objects.filter(
                candidate_id=OuterRef("candidate_id"),
                recruiter_id=OuterRef("recruiter_id"),
                shortlisted_role_id=OuterRef("shortlisted_role_id"),
                jd_id=None,
                status_id__in=[8, 9, 10, 11, 12, 4],
            )[:1].values("candidate_id")
        ),
        shortlisted_role_name=Subquery(
            tmeta_ds_main_roles.objects.filter(
                id=OuterRef("shortlisted_role_id")
            ).values("label_name")
        ),
        available=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("available_to_start")
        ),
        type_of_job=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("type_of_job")
        ),
        profile_pic=Subquery(
            Profile.objects.filter(user=OuterRef("candidate_id__user_id"))[:1].values(
                "image"
            )
        ),
        pre_country1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current_country")
        ),
        current1_country1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current1_country")
        ),
        current2_country1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current2_country")
        ),
        current3_country1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current3_country")
        ),
        pre_state1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current_state")
        ),
        pre_city1=Subquery(
            Personal_Info.objects.filter(application_id=OuterRef("candidate_id"))[
                :1
            ].values("current_city")
        ),
    ).order_by("-updated_on")

    candidate_details = candidate_details.annotate(
        country_auth=Concat(
            "current1_country1",
            V(", "),
            "current2_country1",
            V(", "),
            "current3_country1",
            output_field=CharField(),
        )
    )

    candidate_details = candidate_details.annotate(
        total_exp=Concat("exp_year", V("."), "exp_month", output_field=FloatField())
    )
    candidate_details = candidate_details.annotate(
        pre_country=Subquery(
            Country.objects.filter(id=OuterRef("pre_country1"))[:1].values("name")
        ),
        pre_state=Subquery(
            State.objects.filter(id=OuterRef("pre_state1"))[:1].values("name")
        ),
        pre_city=Subquery(
            City.objects.filter(id=OuterRef("pre_city1"))[:1].values("name")
        ),
        available_to_start=Subquery(
            tmeta_notice_period.objects.filter(id=OuterRef("available"))[:1].values(
                "tag_name"
            )
        ),
    )
    candidate_details = candidate_details.annotate(
        location=Concat("pre_state", V(", "), "pre_country", output_field=CharField())
    )
    location_list = list(
        candidate_details.order_by("location")
        .values_list("location", flat=True)
        .distinct()
    )
    interested_list = jd_candidate_analytics.objects.filter(
        jd_id=None, status_id__in=[7, 13], interested=1, recruiter_id_id=user
    )
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()

    skill_list = skill_list.split("\n")
    if "type_of_job" in request.GET:
        if request.GET["type_of_job"] == "1":
            candidate_details = candidate_details.filter(type_of_job__in=[1, 5])
            data._mutable = True
            del data["type_of_job"]
        elif request.GET["type_of_job"] == "2":
            candidate_details = candidate_details.filter(type_of_job__in=[2, 5])
            data._mutable = True
            del data["type_of_job"]
        elif request.GET["type_of_job"] == "5":
            candidate_details = candidate_details.filter(type_of_job__in=[1, 2, 5])
            data._mutable = True
            del data["type_of_job"]
    filters = InterestedCandFilters(data, queryset=candidate_details)
    candidate_details = filters.qs
    len_list = candidate_details.count()

    page = request.GET.get("page", 1)
    paginator = Paginator(candidate_details, 10)

    try:
        candidate_details = paginator.page(page)
    except PageNotAnInteger:
        candidate_details = paginator.page(1)

    except EmptyPage:
        candidate_details = paginator.page(paginator.num_pages)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()

    # skill_match_list =data.getlist('skill_match')
    context = {
        "candidate_details": candidate_details,
        "filters": filters,
        "len_list": len_list,
        "params": params,
        "interested_list": interested_list,
        "data_list": json.dumps(data, cls=DjangoJSONEncoder),
        "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        "skill_match_list": json.dumps(skill_match_list, cls=DjangoJSONEncoder),
        "location_list": json.dumps(location_list, cls=DjangoJSONEncoder),
        "contact_waiting_list": contact_waiting_list,
    }

    return render(request, "jobs/interested_candidates_ajax.html", context)


def find_lat_long(company_name, location):
    import requests

    URL = "https://geocode.search.hereapi.com/v1/geocode"

    API_key = "s5DExdC_Sohkock53a1tlelgliI_Z-t-QMr7cuZgaGo"
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {"q": str(company_name) + "," + str(location), "apiKey": API_key}

    r = requests.get(url=URL, params=PARAMS)

    # extracting data in json format
    data = r.json()
    try:
        return data["items"][0]
    except:
        return {}


from django.utils import timezone


def jd_form_to_jd_list(pk=None, string=None):

    jd_detail = JD_locations.objects.filter(jd_id_id=pk)
    jd_detail = jd_detail.annotate(
        job_role=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_title")
        ),
        company_name=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("company_name")
        ),
        job_posted_date=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_posted_on")
        ),
        prof_role=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "recommended_role__tag_name"
            )
        ),
        is_active=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("jd_status")
        ),
        richtext_job_description=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values(
                "richtext_job_description"
            )
        ),
        business_intelligence=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "business_intelligence"
            )
        ),
        data_analysis=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "data_analysis"
            )
        ),
        data_engineering=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "data_engineering"
            )
        ),
        devops=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("jd_id"))[:1].values("devops")
        ),
        machine_learning=Subquery(
            JD_profile.objects.filter(jd_id=OuterRef("jd_id"))[:1].values(
                "machine_learning"
            )
        ),
        # tech_req=Subquery(JD_form.objects.filter(id=OuterRef('jd_id'))[:1].values('tech_req')),
        qual_spec=Subquery(
            JD_qualification.objects.filter(jd_id=OuterRef("jd_id"))
            .values("jd_id")
            .annotate(name=Concats("qualification"))[:1]
            .values("name"),
            output_field=CharField(),
        ),
        Minimum_Experience=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("min_exp")
        ),
        Maximum_Experience=Subquery(
            JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("max_exp")
        ),
        skill_match=Subquery(
            JD_skills_experience.objects.filter(jd_id=OuterRef("jd_id"))
            .values("jd_id")
            .annotate(name=Concats("skill"))[:1]
            .values("name"),
            output_field=CharField(),
        ),
        countries=Subquery(
            Country.objects.filter(id=OuterRef("country"))[:1].values("name")
        ),
        states=Subquery(State.objects.filter(id=OuterRef("state"))[:1].values("name")),
        cities=Subquery(City.objects.filter(id=OuterRef("city"))[:1].values("name")),
    )

    jd_detail = jd_detail.annotate(
        loc=Concat(
            "cities", V(", "), "states", V(", "), "countries", output_field=CharField()
        )
    )

    from job_pool.models import JD_list

    if string == 1:
        now = timezone.now()
        for i in jd_detail:
            lat_lng = find_lat_long(i.company_name, i.loc)
            try:
                lat = lat_lng["position"]["lat"]
                lng = lat_lng["position"]["lng"]
            except:
                lat = float(0)
                lng = float(0)
            matching_text = i._job_description
            JD_list.objects.create(
                job_role=i.job_role,
                company_name=i.company_name,
                lng=lng,
                lat=lat,
                prof_role=i.prof_role,
                is_active=i.is_active,
                mapped_skills=i.skill_match,
                job_posted_date=i.job_posted_date,
                state=i.loc,
                input_for_matching=matching_text,
                edu_qualification=i.qual_spec,
                Minimum_Experience=i.Minimum_Experience,
                Maximum_Experience=i.Maximum_Experience,
                business_intelligence=i.business_intelligence,
                data_analysis=i.data_analysis,
                data_engineering=i.data_engineering,
                devops=i.devops,
                is_keyword_match=1,
                machine_learning=i.machine_learning,
                zita_jd_id=i.jd_id,
                updated_at=now,
            )

    elif string == 2:
        now = timezone.now()
        for i in jd_detail:
            JD_list.objects.filter(
                state=i.loc,
                zita_jd_id=i.jd_id,
            ).update(job_posted_date=now, is_active=1)
    else:
        for i in jd_detail:
            JD_list.objects.filter(
                state=i.loc,
                zita_jd_id=i.jd_id,
            ).update(is_active=0)
    #
    return


# Function used to parse the uploaded JD by recruiter
def parsing(request, pk=None):

    if request.method == "POST":
        form_upload = Upload_jd(request.POST, request.FILES)
        if form_upload.is_valid():
            temp = form_upload.save(commit=False)
            temp.user_id = User.objects.get(username=request.user)
            temp.save()
            filepath = form_upload.instance.jd_file.path
            file_name = os.path.splitext(os.path.basename(filepath))
            filename = "".join(list(file_name))
            # parsing(filename)
            logger.info("Parsing the JD: " + str(filename))

    headers = {"Authorization": settings.jdp_api_auth_token}
    # url = "http://192.168.3.231:82/parse-jd/"
    url = settings.jdp_api_url

    try:
        files = {
            "jd_file": open(os.getcwd() + "/" + "media/uploaded_jds/" + filename, "rb")
        }
    except:
        files = {
            "jd_file": open(base_dir + "/" + "media/uploaded_jds/" + filename, "rb")
        }

    result = requests.post(url, headers=headers, files=files)
    logger.debug("JD Parser API response " + str(result))
    sample = result.json()
    try:
        with open(base_dir + "/" + "media/jd_output/" + filename + ".json", "w") as fp:
            json.dump(sample, fp)
    except:
        with open(
            os.getcwd() + "/" + "media/jd_output/" + filename + ".json", "w"
        ) as fp:
            json.dump(sample, fp)

    if "duplicate" in request.POST:
        return redirect(
            "/jobs/update/"
            + str(pk)
            + "/?"
            + request.POST["jd_role"]
            + "&parsing=&duplicate=1"
        )
    if pk == None:
        return redirect("/jobs/description?" + request.POST["jd_role"])
    else:
        return redirect(
            "/jobs/update/" + str(pk) + "/?" + request.POST["jd_role"] + "&parsing="
        )


def Save_JD(request, form, user_id, updated_by):
    logger.info("In function save_jd - Saving......")
    work_remote = False
    if form.get("work_remote") == "on":
        work_remote = True
    else:
        work_remote = False
    jd = JD_form()
    jd.job_title = form["job_title"] if len(form["job_title"]) != 0 else "NULL"
    jd.user_id = user_id
    jd.updated_by = updated_by
    jd.job_role = (
        tmeta_ds_main_roles.objects.get(id=form["job_role"])
        if len(form["job_role"]) != 0
        else "NULL"
    )
    jd.job_id = form["job_id"] if len(form["job_id"]) != 0 else "NULL"
    jd.industry_type_id = form["industry_type"]
    jd.min_exp = form["min_exp"] if len(form["min_exp"]) > 0 else None
    jd.max_exp = form["max_exp"] if len(form["max_exp"]) > 0 else None
    jd.work_remote = work_remote
    jd.richtext_job_description = (
        form["richtext_job_description"]
        if len(form["richtext_job_description"]) != 0
        else "NULL"
    )
    text_des = re.sub(r"<.*?>", "", form["richtext_job_description"])
    text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
    text_des = re.sub(r"Requirements:", "", text_des)
    jd.job_description = text_des
    jd.no_of_vacancies = (
        form["no_of_vacancies"] if len(form["no_of_vacancies"]) != 0 else 0
    )

    jd.salary_curr_type_id = int(form["salary_curr_type"])
    try:
        jd.show_sal_to_candidate = (
            True if form["show_sal_to_candidate"] == "on" else False
        )
    except:
        pass
    jd.salary_min = form["salary_min"] if len(form["salary_min"]) != 0 else 0
    jd.salary_max = form["salary_max"] if len(form["salary_max"]) != 0 else 0
    jd.job_type_id = int(form["job_type"])
    jd.jd_status_id = int(2)
    jd.save()
    UserActivity.objects.create(
        user=request.user,
        action_id=1,
        action_detail=str(form["job_title"]) + " (" + str(form["job_id"]) + ")",
    )
    jd_id = JD_form.objects.filter(user_id=user_id).last()
    qual_list = [value for key, value in form.items() if "qualification" in key.lower()]
    spec_list = [
        value for key, value in form.items() if "specialization" in key.lower()
    ]
    for q, s in zip(qual_list, spec_list):
        q = q if q != "" else "NULL"
        s = s if s != "" else "NULL"
        JD_qualification.objects.create(
            qualification=q, specialization=s, jd_id_id=jd_id.id
        )

    if form["job_role"] == "6" or form["job_role"] == 6:
        skills = form.getlist("mand_skill")
        skills.pop(0)
        skills = [i.strip().upper() for i in skills]
        skills = list(dict.fromkeys(skills))
        for s in skills:
            JD_skills_experience.objects.create(
                skill=s, experience=0, jd_id_id=jd_id.id, category_id=None
            )

    else:
        mand_skill_list = (
            form.getlist("mand_skill")[0].split("|")
            if form.getlist("mand_skill")[0] != ""
            else ["NULL"]
        )
        skill_exp_list = form.getlist("mand_skill_exp")[0].split(",")

        if len(skill_exp_list) > 1:
            skill_l = [
                skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 == 0
            ]
            exp_l = [
                skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 != 0
            ]
        else:
            skill_l = [i for i in mand_skill_list]
            exp_l = [0] * len(skill_l)
        database_skill = form.getlist("database_skill")[0].split(",")
        platform_skill = form.getlist("platform_skill")[0].split(",")
        programming_skill = form.getlist("programming_skill")[0].split(",")
        tool_skill = form.getlist("tool_skill")[0].split(",")
        misc_skill = form.getlist("misc_skill")[0].split(",")
        for s, e in zip(skill_l, exp_l):
            if s.lower() in database_skill:
                JD_skills_experience.objects.create(
                    skill=s, experience=e, jd_id_id=jd_id.id, category_id=1
                )
            if s.lower() in platform_skill:
                JD_skills_experience.objects.create(
                    skill=s, experience=e, jd_id_id=jd_id.id, category_id=2
                )
            if s.lower() in programming_skill:
                JD_skills_experience.objects.create(
                    skill=s, experience=e, jd_id_id=jd_id.id, category_id=3
                )
            if s.lower() in tool_skill:
                JD_skills_experience.objects.create(
                    skill=s, experience=e, jd_id_id=jd_id.id, category_id=4
                )
            if s.lower() in misc_skill:
                JD_skills_experience.objects.create(
                    skill=s, experience=e, jd_id_id=jd_id.id, category_id=5
                )
    # loc = jd_locations_form()
    country_list = [
        value for key, value in form.items() if "work_country" in key.lower()
    ]
    state_list = [value for key, value in form.items() if "work_state" in key.lower()]
    city_list = [value for key, value in form.items() if "work_city" in key.lower()]

    for c, s, ci in zip(country_list, state_list, city_list):
        JD_locations.objects.create(
            country_id=int(c), state_id=int(s), city_id=int(ci), jd_id_id=jd_id.id
        )
    logger.info("Saved JD successfully")

    return redirect("jobs:jobs_main")


# Function gets called when recriter clicked on 'Create JD' button in 'Job-postings page'
@login_required
@recruiter_required
def post_job(request):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass

    admin_id, updated_by = admin_account(request)
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    user_id = User.objects.get(username=request.user)
    logger.info("logged in User-ID: " + str(user_id))
    # try:
    if "non_ds" in request.GET:
        is_ds_role = 0
    else:
        is_ds_role = 1
    # 	permission = user_type.objects.get(user_id=request.user).admin_id

    # except:
    # 	permission = 0
    # if permission != 0 :
    # 	user_id = permission
    logger.info("In function post_job - Getting JD form")
    form_upload = Upload_jd()
    form_jd = jd_form()
    form_qual = jd_qualification_form()
    form_skill_exp = jd_skills_experience_form()
    form_loc = jd_locations_form()
    # t = datetime.datetime.now()
    countries_to_be_displayed = Country.objects.all().values_list("name", flat=True)
    country_list = [
        {
            i.id: list(State.objects.filter(country=i.id).values("id", "name"))
            for i in Country.objects.all()
            if i.name in countries_to_be_displayed
        }
    ]
    filtered_state = [i["name"] for i in sum(country_list[0].values(), [])]
    state_list = [
        {
            i.id: list(City.objects.filter(state=i.id).values("id", "name"))
            for i in State.objects.all()
            if i.name in filtered_state
        }
    ]
    country = Country.objects.all()
    # country_ids=[country.filter(name__iexact=i)[0].id for i in countries_to_be_displayed]
    # country=country.filter(id__in=country_ids)
    current_site = get_current_site(request).domain

    # if 'image_file' in request.FILES and request.method == 'POST':
    # 	i=request.FILES['image_file']
    # 	out_file = open(base_dir + '/media/company_logo/'+str(i), 'wb+')
    # 	out_file.write(i.read())

    if request.method == "POST" and "0" in request.POST:
        data = request.POST
        form = request.POST
        Save_JD(request, form, admin_id, updated_by)

    elif request.method == "POST":

        logger.info("Profiling the JD")
        form = request.POST
        work_remote = True
        if form.get("work_remote") == "on":
            work_remote = True
        else:
            work_remote = False

        jd = JD_form()
        jd.job_title = form["job_title"]
        jd.user_id = admin_id
        jd.job_role = tmeta_ds_main_roles.objects.get(id=int(form["job_role"]))
        jd.job_id = form["job_id"]
        # jd.company_name = form['company_name']
        # jd.company_website = form['company_website']
        jd.industry_type_id = form["industry_type"]
        # jd.org_info = form['org_info']
        jd.min_exp = form["min_exp"]
        if form["max_exp"] == "":
            jd.max_exp = None
        else:
            jd.max_exp = form["max_exp"]
        jd.no_of_vacancies = form["no_of_vacancies"]
        jd.work_remote = work_remote
        jd.richtext_job_description = form["richtext_job_description"]
        text_des = re.sub(r"<.*?>", "", form["richtext_job_description"])
        text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
        text_des = re.sub(r"Requirements:", "", text_des)
        jd.job_description = text_des

        jd.salary_curr_type_id = int(form["salary_curr_type"])
        try:
            jd.show_sal_to_candidate = 1 if form["show_sal_to_candidate"] == "on" else 0
        except:
            pass

        # jd.tech_req = form['tech_req']
        # jd.non_tech_req = form['non_tech_req']
        # jd.add_info = form['add_info']
        jd.salary_min = form["salary_min"]
        jd.salary_max = form["salary_max"]
        jd.job_type_id = form["job_type"]
        jd.jd_status_id = int(2)
        jd.save()
        UserActivity.objects.get_or_create(
            user=request.user,
            action_id=1,
            action_detail=str(form["job_title"]) + " (" + str(form["job_id"]) + ")",
        )
        jd_id = JD_form.objects.filter(user_id=admin_id).last()

        qual_list = [
            value for key, value in form.items() if "qualification" in key.lower()
        ]
        spec_list = [
            value for key, value in form.items() if "specialization" in key.lower()
        ]
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id.id
            )

        if form["job_role"] == "6" or form["job_role"] == 6:
            try:
                skills = form.getlist("mand_skill")
                skills.pop(0)
                for s in skills:
                    JD_skills_experience.objects.create(
                        skill=s, experience=0, jd_id_id=jd_id.id, category_id=None
                    )
            except:
                pass
        else:
            mand_skill_list = form.getlist("mand_skill")[0].split("|")
            skill_exp_list = form.getlist("mand_skill_exp")[0].split(",")

            if len(skill_exp_list) > 1:
                skill_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 == 0
                ]
                exp_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 != 0
                ]
            else:
                skill_l = [i for i in mand_skill_list]
                exp_l = [0] * len(skill_l)
            database_skill = form.getlist("database_skill")[0].split(",")
            platform_skill = form.getlist("platform_skill")[0].split(",")
            programming_skill = form.getlist("programming_skill")[0].split(",")
            tool_skill = form.getlist("tool_skill")[0].split(",")
            misc_skill = form.getlist("misc_skill")[0].split(",")
            for s, e in zip(skill_l, exp_l):
                if s.lower() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=1
                    )
                if s.lower() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=2
                    )
                if s.lower() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=3
                    )
                if s.lower() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=4
                    )
                if s.lower() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=5
                    )

        # loc = jd_locations_form()
        country_list = [
            value for key, value in form.items() if "work_country" in key.lower()
        ]
        state_list = [
            value for key, value in form.items() if "work_state" in key.lower()
        ]
        city_list = [value for key, value in form.items() if "work_city" in key.lower()]
        for c, s, ci in zip(country_list, state_list, city_list):
            JD_locations.objects.create(
                country_id=int(c), state_id=int(s), city_id=int(ci), jd_id_id=jd_id.id
            )
        if not "non_ds" in request.POST:
            text_des = re.sub(r"<.*?>", "", form["richtext_job_description"])
            text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
            text_des = re.sub(r"Requirements:", "", text_des)
            # text_des = re.sub(r'Non-Technical Requirements:', '', text_des)
            job_description = text_des
            profiler_input = [job_description]
            try:
                if profiler_input != []:
                    # s_time = datetime.datetime.now()
                    url = settings.profile_api_url
                    headers = {"Authorization": settings.profile_api_auth_token}
                    input_texts = profiler_input
                    texts_file = {"texts": "||".join(input_texts)}
                    result = requests.post(url, headers=headers, data=texts_file)
                    profiles = result.json()["profiles"]
                    profiles["bi_vis"] = profiles.pop("Business_Intelligence")
                    profiles["data_analysis"] = profiles.pop("Data_Analysis")
                    profiles["data_eng"] = profiles.pop("Data_Engineering")
                    profiles["devops"] = profiles.pop("Dev_Ops")
                    profiles["ml_model"] = profiles.pop("Machine_Learning")
                    sorted_profiles = sorted(
                        profiles.items(), key=lambda kv: (kv[1], kv[0]), reverse=True
                    )
                    recommended_roles = result.json()["recommended_roles"]
                    ds_profile = ""
                    if recommended_roles != []:
                        ds_profile = "DS Profile"
                    else:
                        ds_profile = "Others"
                        recommended_roles.append(ds_profile)
                    classification_url = settings.classification_url
                    cl_result = requests.post(
                        classification_url,
                        headers=headers,
                        data={"profiles": profiles.values()},
                    )

                    role_obj = tmeta_ds_main_roles.objects.get(
                        tag_name=recommended_roles[0].replace("_", " ")
                    )

                    Visualize_instance = JD_profile.objects.create(
                        jd_id=jd_id,
                        user_id=admin_id,
                        business_intelligence=profiles["bi_vis"],
                        data_analysis=profiles["data_analysis"],
                        data_engineering=profiles["data_eng"],
                        devops=profiles["devops"],
                        machine_learning=profiles["ml_model"],
                        others=profiles["others"],
                        recommended_role=role_obj,
                        dst_or_not=cl_result.json()["dst_or_not"],
                    )

                    Visualize_instance.save()
                    # logger.info('Time taken to profile and save in DB'+str(datetime.datetime.now()-s_time).total_seconds())
            except Exception as e:
                logger.error("Profiling failed----" + str(e))

            # return redirect('jobs:profile')

            return HttpResponseNotModified()
        else:
            data = {"id": jd_id.pk}
            return JsonResponse(data)
            # return redirect('jobs:questionnaire',pk=jd_id.pk)

    try:
        with open(base_dir + "/static/media/skills2.json", "r") as fp:
            data = json.load(fp)
    except:
        with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
            data = json.load(fp)
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")
    tool = []
    database = []
    platform = []
    misc = []
    programming = []
    context = {
        "form_jd": form_jd,
        "form_upload": form_upload,
        "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        "data": json.dumps(data, cls=DjangoJSONEncoder),
        "tool_skill": json.dumps(tool, cls=DjangoJSONEncoder),
        "database_skill": json.dumps(database, cls=DjangoJSONEncoder),
        "platform_skill": json.dumps(platform, cls=DjangoJSONEncoder),
        "misc_skill": json.dumps(misc, cls=DjangoJSONEncoder),
        "programming_skill": json.dumps(programming, cls=DjangoJSONEncoder),
        "country_list": json.dumps(country_list, cls=DjangoJSONEncoder),
        "state_list": json.dumps(state_list, cls=DjangoJSONEncoder),
        "country": country,
        "permission": permission,
        "jd_prev": [{"check": 1}],
        "current_site": current_site,
        "is_ds_role": is_ds_role,
    }
    return render(request, "jobs/post_job.html", context)


# Function gets called when JD Parsed to show the prepopulated values within JD-form
@login_required
@recruiter_required
def pre_jdView(request, pk=None):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    logger.info("Getting pre-populated data")
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    user_id, updated_by = admin_account(request)
    if "non_ds" in request.GET:
        is_ds_role = 0
    else:
        is_ds_role = 1
    countries_to_be_displayed = Country.objects.all().values_list("name", flat=True)
    country_list = [
        {
            i.id: list(State.objects.filter(country=i.id).values("id", "name"))
            for i in Country.objects.all()
            if i.name in countries_to_be_displayed
        }
    ]
    filtered_state = [i["name"] for i in sum(country_list[0].values(), [])]
    state_list = [
        {
            i.id: list(City.objects.filter(state=i.id).values("id", "name"))
            for i in State.objects.all()
            if i.name in filtered_state
        }
    ]
    country = Country.objects.all()
    if request.method == "GET":
        form_upload = JDfiles.objects.filter(user_id=request.user).last()
        filepath_str = form_upload.jd_file
        file_path = str(filepath_str)
        filepath = file_path.split("/")
        filename = filepath[1]
        try:
            json_data = open(base_dir + "/" + "media/jd_output/" + filename + ".json")
        except:
            json_data = open(
                os.getcwd() + "/" + "media/jd_output/" + filename + ".json"
            )
        data_jd = json.load(json_data)
        form_jd = jd_form()
        form_qual = jd_qualification_form()
        form_skill = jd_skills_experience_form()
        try:
            form_jd.fields["job_title"].initial = (", ").join(data_jd["job_title"])[:59]
        except KeyError:
            pass
        try:
            o_inf = data_jd["organisation_information"]

        except KeyError:
            pass
        try:
            form_jd.fields["min_exp"].initial = data_jd["Minimum Experience"][0]
        except KeyError:
            pass

        try:
            if data_jd["Maximum Experience"][0] != None:
                form_jd.fields["max_exp"].initial = data_jd["Maximum Experience"][0]
        except KeyError:
            try:
                if len(data_jd["Minimum Experience"]) > 1:
                    form_jd.fields["max_exp"].initial = data_jd["Minimum Experience"][1]
            except KeyError:
                pass

        qual_name = []
        try:
            qual = data_jd["edu_qualification"]
            import re

            qual_list = re.split(", |_|-|!|\+", qual[0])
            for i in qual_list:
                if i.lower().strip() in settings.ug:
                    qual_name.append("Bachelors")
                if i.lower().strip() in settings.pg:
                    qual_name.append("Masters")
                if i.lower().strip() in settings.phd:
                    qual_name.append("Doctorate")
        except KeyError:
            pass
        try:
            add_in = data_jd["Additional Information"]

        except:
            pass
        role_and_res = []
        try:
            roles = data_jd["roles_and_responsibilities"]
            role_and_res.append("<h4>Roles and Responsibilities</h4>")
            role_and_res.append("<br>".join(roles))
        except:
            pass
        try:
            tech_re = data_jd["Technical requirements"]
            role_and_res.append("<h4>Requirements</h4>")
            role_and_res.append("<br>".join(tech_re))
        except:
            pass
        try:
            non_tech = data_jd["Non_Technical requirements"]
            # role_and_res.append('<h4>Non Technical Responsibilities</h4>')
            role_and_res.append("<br>".join(non_tech))
        except:
            pass
        try:
            role_and_res.append("<h4>Organisation Information</h4>")
            role_and_res.append("<br>".join(o_inf))
        except:
            pass
        try:
            role_and_res.append("<h4>Additional Information</h4>")
            role_and_res.append("<br>".join(add_in))
        except:
            pass
        form_jd.fields["richtext_job_description"].initial = "".join(role_and_res)

        try:
            with open(base_dir + "/static/media/skills2.json", "r") as fp:
                data = json.load(fp)
        except:
            with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
                data = json.load(fp)

        # dummy = ['JDBC', 'UML', 'ACCESS-VBA', 'STATA','SQL']
        skills = data_jd["Skills"]["Mapped"]
        tool = []
        database = []
        platform = []
        misc = []
        programming = []
        # t = datetime.now()
        for prof in data:
            for i in data[prof]:
                for skill in skills:
                    if skill.upper() in data[prof][i]:
                        if i == "tool":
                            tool.append(skill + "*#fad7a0")
                        elif i == "database":
                            database.append(skill + "*#aed6f1")
                        elif i == "platform":
                            platform.append(skill + "*#a2d9ce")
                        elif i == "programming":
                            programming.append(skill + "*#f5b7b1")
                        else:
                            misc.append(skill + "*#e8daef")

        tool = list(dict.fromkeys(tool))
        database = list(dict.fromkeys(database))
        platform = list(dict.fromkeys(platform))
        misc = list(dict.fromkeys(misc))
        programming = list(dict.fromkeys(programming))
        mand_skills = [j + "*#d0d0d0" for j in skills]
        # form_skill.fields['skill'].initial = data_jd['Skills']['Mapped']
        # try:
        # 	tech_re = data_jd['Technical requirements']
        # 	tech_req = ''
        # 	for i in range(0,len(tech_re)):
        # 		if len(tech_re[i])==0:
        # 			continue
        # 		else:
        # 			if tech_re[i].endswith('.') == True:
        # 				tech_req = tech_req + tech_re[i] + '\n '
        # 			else:
        # 				tech_req = tech_req+tech_re[i] + '.\n '
        # 	form_jd.fields['tech_req'].initial = tech_req
        # except KeyError:
        # 	pass

        # try:
        # 	non_tech = data_jd['Non_Technical requirements']
        # 	non_tech_req = ''
        # 	for i in range(0,len(non_tech)):
        # 		if len(non_tech[i])==0:
        # 			continue
        # 		else:
        # 			non_tech_req+=non_tech[i] +'\n'
        # 	form_jd.fields['non_tech_req'].initial = non_tech_req
        # except KeyError:
        # 	pass
        try:
            form_jd.fields["salary_min"].initial = data_jd["SALARY_RANGE"]
        except KeyError:
            pass
    elif request.method == "POST" and "save" in request.POST:
        form = request.POST

        try:
            job_role = tmeta_ds_main_roles.objects.get(id=form["job_role"])
        except:
            pass
        work_remote = False
        if form.get("work_remote") == "on":
            work_remote = True
        else:
            work_remote = False
        jd = JD_form()
        jd.work_remote = work_remote
        jd.job_title = form["job_title"]
        try:
            jd.job_role = job_role
        except:
            pass
        if form["max_exp"] == "":
            jd_max = None
        else:
            jd_max = form["max_exp"]
        # jd.org_info = form['org_info']
        jd.user_id = user_id
        jd.updated_by = updated_by
        jd.min_exp = form["min_exp"]
        jd.job_id = form["job_id"]
        # jd.company_name = form['company_name']
        # jd.company_website = form['company_website']
        jd.industry_type_id = form["industry_type"]
        jd.max_exp = jd_max
        jd.richtext_job_description = form["richtext_job_description"]
        jd.no_of_vacancies = form["no_of_vacancies"]
        jd.salary_curr_type_id = int(form["salary_curr_type"])
        try:
            jd.show_sal_to_candidate = 1 if form["show_sal_to_candidate"] == "on" else 0
        except:
            pass
        # jd.tech_req = form['tech_req']
        # jd.add_info = form['add_info']
        # jd.non_tech_req = form['non_tech_req']
        jd.salary_min = form["salary_min"]
        jd.salary_max = form["salary_max"]
        # if 'company_logo' in request.FILES:
        # 	jd.company_logo = request.FILES['company_logo']
        # jd.company_logo = company_logo if ' ' not in company_logo else company_logo.replace(' ','_')

        jd.job_type_id = form["job_type"]
        jd.jd_status_id = int(2)
        jd.save()
        UserActivity.objects.create(
            user=request.user,
            action_id=1,
            action_detail=str(form["job_title"]) + " (" + str(form["job_id"]) + ")",
        )

        jd_id = JD_form.objects.filter(user_id=user_id).last()

        qual_list = [
            value for key, value in form.items() if "qualification" in key.lower()
        ]
        spec_list = [
            value for key, value in form.items() if "specialization" in key.lower()
        ]
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id.id
            )
        if form["job_role"] == "6" or form["job_role"] == 6:
            # try:
            skills = form.getlist("mand_skill")
            skills.pop(0)
            skills = [i.strip().upper() for i in skills]
            skills = list(dict.fromkeys(skills))
            for s in skills:
                JD_skills_experience.objects.create(
                    skill=s, experience=0, jd_id_id=jd_id.id, category_id=None
                )
        # except:
        # 	pass
        else:
            mand_skill_list = form.getlist("mand_skill")[0].split("|")
            skill_exp_list = form.getlist("mand_skill_exp")[0].split(",")

            if len(skill_exp_list) > 1:
                skill_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 == 0
                ]
                exp_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 != 0
                ]
            else:
                skill_l = [i for i in mand_skill_list]
                exp_l = [0] * len(skill_l)

            database_skill = form.getlist("database_skill")[0].split(",")
            platform_skill = form.getlist("platform_skill")[0].split(",")
            programming_skill = form.getlist("programming_skill")[0].split(",")
            tool_skill = form.getlist("tool_skill")[0].split(",")
            misc_skill = form.getlist("misc_skill")[0].split(",")
            for s, e in zip(skill_l, exp_l):
                if s.lower() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=1
                    )
                if s.lower() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=2
                    )
                if s.lower() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=3
                    )
                if s.lower() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=4
                    )
                if s.lower() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=5
                    )

        country_list = [
            value for key, value in form.items() if "work_country" in key.lower()
        ]
        state_list = [
            value for key, value in form.items() if "work_state" in key.lower()
        ]
        city_list = [value for key, value in form.items() if "work_city" in key.lower()]
        for c, s, ci in zip(country_list, state_list, city_list):
            JD_locations.objects.create(
                country_id=int(c), state_id=int(s), city_id=int(ci), jd_id_id=jd_id.id
            )

        return redirect("jobs:jobs_main")

    else:
        form = request.POST
        logger.info("Submitting JD for profiling")
        try:
            job_role = form["job_role"]
        except:
            pass
        work_remote = True
        if form.get("work_remote") == "on":
            work_remote = True
        else:
            work_remote = False
        jd = JD_form()
        jd.job_title = form["job_title"]
        try:
            jd.job_role_id = job_role
        except:
            pass
        # jd.org_info = form['org_info']
        jd.user_id = user_id
        jd.work_remote = work_remote
        jd.updated_by = updated_by
        jd.min_exp = form["min_exp"]
        jd.job_id = form["job_id"]
        if form["max_exp"] == "":
            jd_max = None
        else:
            jd_max = form["max_exp"]
        jd.industry_type_id = form["industry_type"]
        jd.max_exp = jd_max
        jd.richtext_job_description = form["richtext_job_description"]
        jd.no_of_vacancies = form["no_of_vacancies"]
        jd.salary_curr_type_id = int(form["salary_curr_type"])
        try:
            jd.show_sal_to_candidate = 1 if form["show_sal_to_candidate"] == "on" else 0
        except:
            pass
        # jd.tech_req = form['tech_req']
        # jd.add_info = form['add_info']
        # jd.non_tech_req = form['non_tech_req']
        jd.salary_min = form["salary_min"]
        jd.salary_max = form["salary_max"]
        # if 'company_logo' in request.FILES:
        # 	jd.company_logo = request.FILES['company_logo']
        # jd.company_logo =company_logo if ' ' not in company_logo else company_logo.replace(' ','_')

        jd.job_type_id = form["job_type"]
        jd.jd_status_id = int(2)
        jd.save()
        UserActivity.objects.create(
            user=request.user,
            action_id=1,
            action_detail=str(form["job_title"]) + " (" + str(form["job_id"]) + ")",
        )

        jd_id = JD_form.objects.filter(user_id=user_id).last()

        qual_list = [
            value for key, value in form.items() if "qualification" in key.lower()
        ]
        spec_list = [
            value for key, value in form.items() if "specialization" in key.lower()
        ]
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id.id
            )
        if form["job_role"] == "6" or form["job_role"] == 6:
            try:
                skills = form.getlist("mand_skill")
                skills.pop(0)
                for s in skills:
                    JD_skills_experience.objects.create(
                        skill=s, experience=0, jd_id_id=jd_id.id, category_id=None
                    )
            except:
                pass
        else:
            mand_skill_list = form.getlist("mand_skill")[0].split("|")
            skill_exp_list = form.getlist("mand_skill_exp")[0].split(",")

            if len(skill_exp_list) > 1:
                skill_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 == 0
                ]
                exp_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 != 0
                ]
            else:
                skill_l = [i for i in mand_skill_list]
                exp_l = [0] * len(skill_l)

            database_skill = form.getlist("database_skill")[0].split(",")
            platform_skill = form.getlist("platform_skill")[0].split(",")
            programming_skill = form.getlist("programming_skill")[0].split(",")
            tool_skill = form.getlist("tool_skill")[0].split(",")
            misc_skill = form.getlist("misc_skill")[0].split(",")
            for s, e in zip(skill_l, exp_l):
                if s.lower() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=1
                    )
                if s.lower() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=2
                    )
                if s.lower() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=3
                    )
                if s.lower() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=4
                    )
                if s.lower() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=5
                    )

        # loc = jd_locations_form()
        country_list = [
            value for key, value in form.items() if "work_country" in key.lower()
        ]
        state_list = [
            value for key, value in form.items() if "work_state" in key.lower()
        ]
        city_list = [value for key, value in form.items() if "work_city" in key.lower()]
        for c, s, ci in zip(country_list, state_list, city_list):
            JD_locations.objects.create(
                country_id=int(c), state_id=int(s), city_id=int(ci), jd_id_id=jd_id.id
            )

        if not "non_ds" in request.POST:
            # profiler_input = []
            import re

            # profiler_input.extend(form['job_description'].replace('\r',' ').replace('\t',' ').split('\n'))
            text_des = re.sub(r"<.*?>", "", form["richtext_job_description"])
            text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
            text_des = re.sub(r"Requirements:", "", text_des)
            profiler_input = text_des
            if profiler_input != []:
                # try:
                s_time = datetime.now()
                url = settings.profile_api_url
                headers = {"Authorization": settings.profile_api_auth_token}
                input_texts = [profiler_input]
                texts_file = {"texts": "||".join(input_texts)}
                result = requests.post(url, headers=headers, data=texts_file)
                # logger.debug("Profiling API response "+(result.json()))
                profiles = result.json()["profiles"]
                profiles["bi_vis"] = profiles.pop("Business_Intelligence")
                profiles["data_analysis"] = profiles.pop("Data_Analysis")
                profiles["data_eng"] = profiles.pop("Data_Engineering")
                profiles["devops"] = profiles.pop("Dev_Ops")
                profiles["ml_model"] = profiles.pop("Machine_Learning")
                sorted_profiles = sorted(
                    profiles.items(), key=lambda kv: (kv[1], kv[0]), reverse=True
                )
                recommended_roles = result.json()["recommended_roles"]
                ds_profile = ""
                if recommended_roles != []:
                    ds_profile = "DS Profile"
                else:
                    ds_profile = "Others"
                    recommended_roles.append(ds_profile)
                classification_url = settings.classification_url
                cl_result = requests.post(
                    classification_url,
                    headers=headers,
                    data={"profiles": profiles.values()},
                )
                role_obj = tmeta_ds_main_roles.objects.get(
                    tag_name=recommended_roles[0].replace("_", " ")
                )
                Visualize_instance = JD_profile.objects.create(
                    jd_id=jd_id,
                    user_id_id=user_id,
                    business_intelligence=profiles["bi_vis"],
                    data_analysis=profiles["data_analysis"],
                    data_engineering=profiles["data_eng"],
                    devops=profiles["devops"],
                    machine_learning=profiles["ml_model"],
                    others=profiles["others"],
                    recommended_role=role_obj,
                    dst_or_not=cl_result.json()["dst_or_not"],
                )

                Visualize_instance.save()
                # logger.info('Time taken to profile and save in DB '+str(datetime.datetime.now()-s_time).total_seconds())

                # except Exception as e:
                # 	logger.error("Profiling failed---"+str(e))
            return HttpResponseNotModified()
        return redirect("jobs:questionnaire", pk=jd_id.id)

    try:
        with open(base_dir + "/static/media/skills2.json", "r") as fp:
            data = json.load(fp)
    except:
        with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
            data = json.load(fp)
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")
    data_t = {}
    context = {
        "form_jd": form_jd,
        "form_upload": form_upload,
        "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        "data": json.dumps(data, cls=DjangoJSONEncoder),
        "tool_skill": json.dumps(tool, cls=DjangoJSONEncoder),
        "database_skill": json.dumps(database, cls=DjangoJSONEncoder),
        "platform_skill": json.dumps(platform, cls=DjangoJSONEncoder),
        "misc_skill": json.dumps(misc, cls=DjangoJSONEncoder),
        "qual_name": json.dumps(qual_name, cls=DjangoJSONEncoder),
        "programming_skill": json.dumps(programming, cls=DjangoJSONEncoder),
        # 'others_skill':json.dumps(others, cls=DjangoJSONEncoder),
        "skills": json.dumps(skills, cls=DjangoJSONEncoder),
        "country_list": json.dumps(country_list, cls=DjangoJSONEncoder),
        "state_list": json.dumps(state_list, cls=DjangoJSONEncoder),
        "country": country,
        "permission": permission,
        "is_ds_role": is_ds_role,
        # 'jd_prev':[{'check':0}]
    }
    return render(request, "jobs/post_job.html", context)


# Function gets called when recruiter clicks 'Profile' button in JD-form
@login_required
@recruiter_required
def profile(request, pk=""):
    time.sleep(2)
    user_id, updated_by = admin_account(request)

    # try:
    # 	permission = user_type.objects.get(user_id=request.user).admin_id
    # except:
    # 	permission=0
    # if permission != 0:
    # 	user_id = permission
    Roles = [
        [i["tag_name"], i["label_name"]]
        for i in list(
            tmeta_ds_main_roles.objects.filter(is_active=True).values(
                "label_name", "tag_name"
            )
        )
    ]
    if pk != "":
        jd_id = pk
    else:
        jd_id = JD_form.objects.filter(user_id=user_id).last().id
    logger.info(
        "In function profile - Getting profiling pop-up for the JD " + str(jd_id)
    )
    s = JD_form.objects.get(id=jd_id).job_role

    if request.method == "GET":
        jd_profile = JD_profile.objects.filter(jd_id=jd_id).values(
            "business_intelligence",
            "data_analysis",
            "data_engineering",
            "devops",
            "machine_learning",
            "others",
        )
        JD_profile.objects.filter(jd_id=jd_id).update(role_acceptence=0)
        recom_role = JD_profile.objects.get(jd_id=jd_id).recommended_role.id
        chosen_role = JD_form.objects.get(id=jd_id).job_role.id
        if chosen_role == recom_role:
            rr_match = 1
        else:
            rr_match = 0
        logger.info(
            "Chosen role for JD: "
            + str(chosen_role)
            + "\nRecommended role for JD: "
            + str(recom_role)
            + "\nRole match for both: "
            + str(rr_match)
        )
        recom_role = tmeta_ds_main_roles.objects.filter(id=recom_role).values(
            "label_name"
        )
        chosen_role = tmeta_ds_main_roles.objects.filter(id=chosen_role).values(
            "label_name"
        )
        context = {
            "profile_object": json.dumps(list(jd_profile), cls=DjangoJSONEncoder),
            "recom_role": json.dumps(list(recom_role), cls=DjangoJSONEncoder),
            "jd_id": jd_id,
            "rr_match": rr_match,
            "chosen_role": json.dumps(list(chosen_role), cls=DjangoJSONEncoder),
        }

    if request.method == "POST":
        if request.POST.get("post_recom_role") is not None:
            role = request.POST.get("post_recom_role")
            logger.info("Recruiter has chosen recommended role ")
            # for i in range(len(Roles)):
            # 	if role == Roles[i][1]:
            role_obj = tmeta_ds_main_roles.objects.get(label_name=role)
            JD_form.objects.filter(id=jd_id).update(job_role_id=role_obj)
            JD_profile.objects.filter(jd_id_id=jd_id).update(role_acceptence=1)
        context = {}
        return HttpResponseNotModified()

    return render(request, "jobs/role_recom.html", context)


def delete_profile(request):
    jd_id = request.GET["pk_id"]

    JD_profile.objects.filter(jd_id_id=jd_id).delete()

    return HttpResponseNotModified()

    # return render(request,'jobs/role_recom.html',context)


def Diff(li1, li2):
    return list(set(li1) - set(li2))


# Function gets called when Recruiter chosen a button(Accepts recommended role/constinue with chosen role) from role recommendation to show missing skills for the chole chosen.
@login_required
@recruiter_required
def missing_skills(request, pk):
    logger.info("Showing missing skills for the JD " + str(pk))
    user_id = admin_account(request)
    # try:
    # 	permission = user_type.objects.get(user_id=request.user).admin_id
    # except:
    # 	permission=0
    # if permission != 0:
    # 	user_id = permission
    try:
        jd_id = pk
        jd = JD_form.objects.get(id=pk)

    except:
        jd_id = JD_form.objects.filter(user_id_id=user_id).last().id
        jd = JD_form.objects.filter(user_id_id=user_id).last()
    time.sleep(2)
    inp1 = str(JD_form.objects.get(id=jd_id).job_role.id)
    logger.info("missing skills for: " + str(inp1))
    try:
        skill_n_exp1 = {}
        for i in JD_skills_experience.objects.filter(jd_id_id=jd_id).values(
            "skill", "experience"
        ):
            skill_n_exp1[i["skill"]] = i["experience"]
        skill_n_exp = [skill_n_exp1]
    except:
        skill_n_exp = []
    mand_skill = [
        i["skill"].upper().strip()
        for i in JD_skills_experience.objects.filter(jd_id_id=jd_id).values("skill")
    ]
    # mand_skill = [i.strip() for i in mand_skill1]
    mand_skill_exp1 = [
        i["experience"].upper().strip()
        for i in JD_skills_experience.objects.filter(jd_id_id=jd_id).values(
            "experience"
        )
    ]

    if len(mand_skill_exp1) == 0:
        mand_skill_expi = []
        for i in range(len(mand_skill)):
            mand_skill_expi.append(0)
    else:
        mand_skill_expi = [i.strip() for i in mand_skill_exp1]
    # pref_skill1=JD_form.objects.filter(id=jd_id).values('pre_skill')[0]['pre_skill'].upper().split('|')
    # pref_skill = [i.strip() for i in pref_skill1]

    allskill = mand_skill
    # for i in range(len(allskill)):
    # 	allskill[i]=allskill[i].upper()
    # allskill=[x.upper() for x in allskill]
    try:
        with open(base_dir + "/static/media/skills2.json", "r") as fp:
            a = json.load(fp)
    except:
        with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
            a = json.load(fp)

    unique = [*a[inp1]["database"]]
    missing_db = Diff(unique, allskill)
    missing_db.sort()
    for i in range(len(missing_db)):
        missing_db[i] = missing_db[i] + "*#aed6f1"

    missing_db = str(missing_db)
    missing_db = (
        missing_db.replace("'", "", len(missing_db)).replace("[", "").replace("]", "")
    )

    unique = [*a[inp1]["tool"]]
    missing_tl = Diff(unique, allskill)
    missing_tl.sort()

    for i in range(len(missing_tl)):
        missing_tl[i] = missing_tl[i] + "*#fad7a0"

    missing_tl = str(missing_tl)
    missing_tl = (
        missing_tl.replace("'", "", len(missing_tl)).replace("[", "").replace("]", "")
    )

    unique = [*a[inp1]["programming"]]
    missing_pl = Diff(unique, allskill)
    missing_pl.sort()
    for i in range(len(missing_pl)):
        missing_pl[i] = missing_pl[i] + "*#f5b7b1"

    missing_pl = str(missing_pl)
    missing_pl = (
        missing_pl.replace("'", "", len(missing_pl)).replace("[", "").replace("]", "")
    )

    unique = [*a[inp1]["platform"]]
    missing_pf = Diff(unique, allskill)
    missing_pf.sort()
    for i in range(len(missing_pf)):
        missing_pf[i] = missing_pf[i] + "*#a2d9ce"

    missing_pf = str(missing_pf)
    missing_pf = (
        missing_pf.replace("'", "", len(missing_pf)).replace("[", "").replace("]", "")
    )

    unique = [*a[inp1]["misc"]]
    missing_ot = Diff(unique, allskill)
    missing_ot.sort()
    for i in range(len(missing_ot)):
        missing_ot[i] = missing_ot[i] + "*#e8daef"
    missing_ot = str(missing_ot)
    missing_ot = (
        missing_ot.replace("'", "", len(missing_ot)).replace("[", "").replace("]", "")
    )
    for i in range(len(mand_skill)):
        mand_skill[i] = mand_skill[i] + "*#d0d0d0"
    # for i in range(len(pref_skill)):
    # 	pref_skill[i]=pref_skill[i]+'*#d0d0d0'

    mand_skill = str(mand_skill)
    # pref_skill=str(pref_skill)
    tool = list(
        JD_skills_experience.objects.filter(jd_id_id=jd_id, category_id=4)
        .values_list("skill", flat=True)
        .distinct()
    )
    database = list(
        JD_skills_experience.objects.filter(jd_id_id=jd_id, category_id=1)
        .values_list("skill", flat=True)
        .distinct()
    )
    platform = list(
        JD_skills_experience.objects.filter(jd_id_id=jd_id, category_id=2)
        .values_list("skill", flat=True)
        .distinct()
    )
    misc = list(
        JD_skills_experience.objects.filter(category_id=5, jd_id_id=jd_id)
        .values_list("skill", flat=True)
        .distinct()
    )
    programming = list(
        JD_skills_experience.objects.filter(jd_id_id=jd_id, category_id=3)
        .values_list("skill", flat=True)
        .distinct()
    )
    for i in range(len(tool)):
        tool[i] = tool[i] + "*#fad7a0"
    for i in range(len(database)):
        database[i] = database[i] + "*#aed6f1"
    for i in range(len(platform)):
        platform[i] = platform[i] + "*#a2d9ce"
    for i in range(len(misc)):
        misc[i] = misc[i] + "*#e8daef"
    for i in range(len(programming)):
        programming[i] = programming[i] + "*#f5b7b1"

    mand_skill = (
        mand_skill.replace("'", "", len(mand_skill)).replace("[", "").replace("]", "")
    )
    # pref_skill=pref_skill.replace("'",'',len(pref_skill)).replace("[","").replace("]","")

    # user_id = User.objects.get(username = request.user).id
    missing_skill_instance = Missing_Skills_Table.objects.create(
        jd_id_id=jd_id,
        missingskill_mand=mand_skill,
        missingskill_pl=missing_pl,
        missingskill_db=missing_db,
        missingskill_tl=missing_tl,
        missingskill_pf=missing_pf,
        missingskill_ot=missing_ot,
    )
    missing_skill_instance.save()
    # user_id = User.objects.get(username = request.user).id
    if request.method == "POST":
        # jd = JD_form.objects.filter(user_id = user_id).last()
        jd = JD_form.objects.filter(id=pk).last()
        skill_exp = request.POST.getlist("mand_skill_exp")[0].split(",")
        skills = request.POST.getlist("mand_skills")[0].split("|")
        skill_l = [skill_exp[i] for i in range(len(skill_exp)) if i % 2 == 0]
        exp_l = [skill_exp[i] for i in range(len(skill_exp)) if i % 2 != 0]
        JD_skills_experience.objects.filter(jd_id_id=jd.id).delete()
        skill_temp = []
        database_skill = request.POST.getlist("database_skill")[0].split(",")
        platform_skill = request.POST.getlist("platform_skill")[0].split(",")
        programming_skill = request.POST.getlist("programming_skill")[0].split(",")
        tool_skill = request.POST.getlist("tool_skill")[0].split(",")
        misc_skill = request.POST.getlist("misc_skill")[0].split(",")

        for s, e in zip(skill_l, exp_l):
            if s.lower() in skills and s.lower() not in skill_temp:
                skill_temp.append(s.lower())
                if s.lower() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=1
                    )
                if s.lower() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=2
                    )
                if s.lower() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=3
                    )
                if s.lower() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=4
                    )
                if s.lower() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=5
                    )

        return redirect("jobs:questionnaire", pk=jd.id)

    else:
        jd_profile = JD_profile.objects.get(jd_id=jd)
        missing_skills_id = (
            Missing_Skills_Table.objects.filter(jd_id=jd_id).last().miss_skill_id
        )
        temp = list(
            Missing_Skills_Table.objects.filter(
                miss_skill_id=missing_skills_id
            ).values()
        )
        context = {
            "object": json.dumps(temp, cls=DjangoJSONEncoder),
            "pk_id": jd,
            "jd_profile": jd_profile,
            "object1": json.dumps(mand_skill_expi, cls=DjangoJSONEncoder),
            "skill_e": json.dumps(skill_n_exp, cls=DjangoJSONEncoder),
            "tool_skill": json.dumps(tool, cls=DjangoJSONEncoder),
            "database_skill": json.dumps(database, cls=DjangoJSONEncoder),
            "platform_skill": json.dumps(platform, cls=DjangoJSONEncoder),
            "misc_skill": json.dumps(misc, cls=DjangoJSONEncoder),
            "programming_skill": json.dumps(programming, cls=DjangoJSONEncoder),
        }
    return render(request, "jobs/missing_skills.html", context)


# Function gets called when recruiter submits the missing skills& their experience details
@login_required
@recruiter_required
def Preview(request, pk=""):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    username = request.user
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    current_site = str(get_current_site(request))
    JD_form.objects.filter(id=pk).update(jd_status_id=6)
    # countries_to_be_displayed =Country.objects.all().values_list('name',flat=True)
    # country_list=[{i.id:list(State.objects.filter(country=i.id).values('id','name')) for i in Country.objects.all() if i.name in countries_to_be_displayed}]
    # filtered_state = [i['name'] for i in sum(country_list[0].values(),[])]
    # state_list=[{i.id:list(City.objects.filter(state=i.id).values('id','name')) for i in State.objects.all() if i.name in filtered_state}]
    # country=Country.objects.all()
    # country_ids=[country.filter(name__iexact=i)[0].id for i in countries_to_be_displayed]
    # country=country.filter(id__in=country_ids)

    user_id, updated_by = admin_account(request)
    # try:
    # 	permission = user_type.objects.get(user_id=request.user).admin_id
    # except:
    # 	permission=0
    # if permission != 0:
    # 	user_id = permission
    try:
        jd = JD_form.objects.filter(id=pk).last()
    except:
        jd = JD_form.objects.filter(user_id=user_id).last()
    logger.info("Getting into preview page of JD " + str(jd))
    # company_logo = str(jd.company_logo)
    # company_logo = company_logo if ' ' not in company_logo else company_logo.replace(' ','_')
    job_type = tmeta_job_type.objects.get(id=jd.job_type.id).value

    job_role = tmeta_ds_main_roles.objects.get(id=jd.job_role.id).label_name
    sal_curr_type = (
        tmeta_currency_type.objects.filter(id=jd.salary_curr_type_id)
        .values("value")[0]["value"]
        .split(" ")[0]
    )

    location = JD_locations.objects.get(jd_id_id=jd.id)

    education = [
        (i["qualification"], i["specialization"])
        for i in JD_qualification.objects.filter(jd_id_id=jd.id).values(
            "qualification", "specialization"
        )
    ]

    mand_skills = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(jd_id_id=jd.id).values("skill")
    ]
    mand_skill_exp = [
        i["experience"]
        for i in JD_skills_experience.objects.filter(jd_id_id=jd.id).values(
            "experience"
        )
    ]

    for i in range(len(mand_skills)):
        mand_skills[i] = mand_skills[i] + "*#d0d0d0"
    try:
        original_jd_profile = JD_profile.objects.get(jd_id=jd.id).recommended_role
        o_recommended_role = tmeta_ds_main_roles.objects.get(
            id=original_jd_profile.id
        ).label_name
        jd_profile = JD_profile.objects.filter(jd_id=jd).values(
            "business_intelligence",
            "data_analysis",
            "data_engineering",
            "devops",
            "machine_learning",
            "others",
        )
        recom_role = JD_profile.objects.filter(jd_id=jd).values("recommended_role")
        role_acceptence = JD_profile.objects.get(jd_id=jd).role_acceptence
        role_acceptence = 1 if job_role == o_recommended_role else o_recommended_role

    except:
        role_acceptence = 0
        o_recommended_role = None
        jd_profile = ""
        recom_role = ""
    if "non_ds" in request.GET:
        is_ds_role = 0
    else:
        is_ds_role = 1
    if request.method == "POST" and "FinalSave" in request.POST:
        # result=generate_jd_json(request,pk=jd.id)
        jd_count = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=10
        )
        if jd_count.available_count != None:
            if jd_count.available_count > 0:
                jd.job_posted_on = datetime.now()
                jd_count.available_count = jd_count.available_count - 1
                jd.jd_status_id = int(1)
                jd.save()
                UserActivity.objects.create(
                    user=request.user,
                    action_id=2,
                    action_detail=str(jd.job_title) + " (" + str(jd.job_id) + ")",
                )
                jd_count.save()
            else:
                jd_count.available_count = 0
                jd_count.save()
                return redirect("jobs:jobs_main")
        else:
            jd.job_posted_on = datetime.now()
            jd.jd_status_id = int(1)
            UserActivity.objects.create(
                user=request.user,
                action_id=2,
                action_detail=str(jd.job_title) + " (" + str(jd.job_id) + ")",
            )
            jd.save()

        jd = JD_form.objects.filter(user_id=user_id).last()
        logger.info("Posting JD " + str(jd))
        chosen_role = JD_form.objects.get(id=jd.id).job_role.label_name

        mail_notification(
            request.user,
            "job_post_confirmation.html",
            "Congratulations!!! Your job has been successfully posted on your career page",
            jd_id=jd.id,
            count=0,
            domain=current_site,
        )

        # else:
        # 	logger.info("As 'Others' is chosen role, Not doing Matching")
        data = {"success": True}
        return JsonResponse(data)

    elif request.method == "POST" and "preview_save" in request.POST:
        jd.jd_status_id = int(6)
        jd.save()
        logger.info("Saved JD from preview page successfully")
        return redirect("jobs:jobs_main")

    elif request.method == "POST" and "Edit" in request.POST:
        val = request.POST["Edit"]
        if val == "0":
            return redirect("/jobs/update/" + str(jd.id) + "?non_ds")
        else:
            return redirect("/jobs/update/" + str(jd.id) + "?ds")
    try:
        plan_id = subscriptions.objects.get(is_active=True, client_id=user_id).plan_id
        has_external_posting = plan_features.objects.filter(
            plan_id=plan_id, feature_id_id=13
        ).exists()
    except:
        has_external_posting = False
    try:
        available_jobs = client_features_balance.objects.get(
            feature_id_id=10, client_id=user_id
        ).available_count
    except:
        available_jobs = 0
    setting = company_details.objects.get(recruiter_id=user_id)
    try:
        career_page_url = career_page_setting.objects.get(
            recruiter_id=user_id
        ).career_page_url
    except:
        career_page_url = None
    return render(
        request,
        "jobs/preview.html",
        {
            "jd": jd,
            "sal_curr_type": sal_curr_type,
            "job_type": job_type,
            "job_role1": o_recommended_role,
            "location": location,
            "education": education,
            "profile_object": json.dumps(list(jd_profile), cls=DjangoJSONEncoder),
            "recom_role": json.dumps(list(recom_role), cls=DjangoJSONEncoder),
            "mand_skills": json.dumps(mand_skills, cls=DjangoJSONEncoder),
            "mand_skill_exp": json.dumps(mand_skill_exp, cls=DjangoJSONEncoder),
            "o_recommended_role": o_recommended_role,
            "is_ds_role": is_ds_role,
            "career_page_url": career_page_url,
            "setting": setting,
            "permission": permission,
            "has_external_posting": has_external_posting,
            "available_jobs": available_jobs,
            "richtext_job_description": json.dumps(
                jd.richtext_job_description, cls=DjangoJSONEncoder
            ),
            # 'tech_req': json.dumps(jd.tech_req, cls=DjangoJSONEncoder),
            # 'non_tech_req': json.dumps(jd.non_tech_req, cls=DjangoJSONEncoder),
            "add_info": json.dumps(jd.add_info, cls=DjangoJSONEncoder),
            "org_info": json.dumps(jd.org_info, cls=DjangoJSONEncoder),
            "work_remote": json.dumps(jd.work_remote, cls=DjangoJSONEncoder),
            "job_role": json.dumps(jd.job_role.tag_name, cls=DjangoJSONEncoder),
            "role_acceptence": role_acceptence,
        },
    )


@login_required
@recruiter_required
def get_JDlist_candlist(jd_id=None):
    if jd_id != None:
        profile_dict = {}
        for p in JD_profile.objects.filter(jd_id=jd_id).values(
            "business_intelligence",
            "data_analysis",
            "data_engineering",
            "devops",
            "machine_learning",
            "others",
        ):
            profile_dict["mle"] = float(p["machine_learning"])
            profile_dict["bi"] = float(p["business_intelligence"])
            profile_dict["dw/a"] = float(p["data_analysis"])
            profile_dict["devops"] = float(p["devops"])
            profile_dict["bde"] = float(p["data_engineering"])
            profile_dict["others"] = float(p["others"])

        min_exp = JD_form.objects.filter(id=jd_id).values("min_exp")[0]["min_exp"]
        max_exp = JD_form.objects.filter(id=jd_id).values("max_exp")[0]["max_exp"]
        # pref_skill = JD_form.objects.filter(id = jd_id).values('pre_skill')[0]['pre_skill'].split('|')
        mand_skill = (
            JD_form.objects.filter(id=jd_id)
            .values("tech_skills")[0]["tech_skills"]
            .split("|")
        )
        JD_tech_skills1 = mand_skill
        JD_tech_skills = []
        for i in JD_tech_skills1:
            JD_tech_skills.append(i.strip())

        jd_loc = (
            JD_form.objects.filter(id=jd_id)
            .values("work_city")[0]["work_city"]
            .split("|")
        )
        JD_list = {
            "profile": profile_dict,
            "min_exp": min_exp,
            "max_exp": max_exp,
            "tech_skills": JD_tech_skills,
            "location": jd_loc,
        }
    else:
        JD_list = []
    candidate_list = []
    for i in Personal_Info.objects.all():
        app_id = i.application_id
        if i.current_city != None:
            loc = [i.current_city]
        else:
            loc = []

        S = Skills.objects.filter(application_id=app_id).values("tech_skill")
        if len(S) == 0:
            skill = ""
        else:
            skill1 = S[0]["tech_skill"].split(",")
            skill = [i.strip() for i in skill1]
        profile = {}
        prof_list = Visualize.objects.filter(application_id=app_id).values(
            "business_intelligence",
            "data_analysis",
            "data_engineering",
            "devops",
            "machine_learning",
            "others",
        )
        if len(prof_list) == 1:
            for p in prof_list:
                profile["mle"] = float(p["machine_learning"])
                profile["bi"] = float(p["business_intelligence"])
                profile["dw/a"] = float(p["data_analysis"])
                profile["devops"] = float(p["devops"])
                profile["bde"] = float(p["data_engineering"])
                profile["others"] = float(p["others"])
        else:
            profile["mle"] = 0
            profile["bi"] = 0
            profile["dw/a"] = 0
            profile["devops"] = 0
            profile["bde"] = 0
            profile["others"] = 0

        try:
            exp_y = Additional_Details.objects.filter(application_id=app_id).values(
                "total_exp_year"
            )[0]["total_exp_year"]
        except IndexError:
            exp_y = 0
        try:
            exp_m = Additional_Details.objects.filter(application_id=app_id).values(
                "total_exp_month"
            )[0]["total_exp_month"]
        except IndexError:
            exp_m = 0
        exp = round(exp_y + exp_m / 12)
        candidate_list.append(
            (
                app_id,
                {
                    "profile": profile,
                    "n_exp": exp,
                    "tech_skills": skill,
                    "location": loc,
                },
            )
        )
    return JD_list, candidate_list


def generate_candidate_load_all(request):
    emp_list = employer_pool.objects.all()
    for i in emp_list:
        pk = i.id
        try:
            parsed_text = candidate_parsed_details.objects.get(
                candidate_id_id=pk
            ).parsed_text
            emp_pool = employer_pool.objects.get(id=pk)
            parsed_text = ast.literal_eval(parsed_text)
            try:
                parsed_text["Personal"].update({"location": [emp_pool.location]})
            except:
                pass
            try:
                exp = parsed_text["Experience"]
                exp_list = []
                for e in exp:
                    exp_list.append({"work ex": exp[e]})
                try:
                    exp_list[0]["work ex"]["Skills"] = exp_list[0]["work ex"][
                        "Skills"
                    ] + emp_pool.skills.split(",")
                except:
                    exp_list[0]["work ex"]["Skills"] = emp_pool.skills.split(",")
                parsed_text["Experience"] = exp_list
            except:
                pass
            try:
                qual = parsed_text["Qualification"]
                qual_list = []
                for q in qual:
                    qual_list.append({"Qual": qual[q]})
                qual_list.append(
                    {
                        "Qual": {
                            "Institute": "",
                            "Year": "",
                            "Qualification": emp_pool.qualification,
                            "Specialization": "",
                            "Percentage": "",
                        }
                    }
                )
                parsed_text["Qualification"] = qual_list
            except:
                pass
            json_object = json.dumps(parsed_text)
            json_object = base64.b64encode(json_object.encode("utf-8"))
            encodedcandi = str(json_object, "utf-8")
            body = (
                """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/index">
            <soapenv:Body> <xmp:addOrUpdateCaseWithData><action><index><caseType>candidate</caseType><indexId>"""
                + emp_pool.client_id.username
                + """</indexId></index><cases><id>"""
                + str(pk)
                + """</id>
            <content>"""
                + str(encodedcandi)
                + """</content></cases><refresh>false</refresh><executionMode>SYNC</executionMode></action></xmp:addOrUpdateCaseWithData></soapenv:Body>
            </soapenv:Envelope>
            """
            )
            index_url = settings.index_url
            index_headers = settings.xmp_headers
            response = requests.post(index_url, data=body, headers=index_headers)
            # result=matching_api_to_db(request,jd_id=None,can_id=pk)
        except Exception as e:
            logger.error("Error in candidate indexing" + str(e))
    return JsonResponse({"Data": "true"}, safe=False)


def generate_jd_json_all(request):

    jd_list = JD_form.objects.filter(jd_status_id=1)
    for i in jd_list:
        pk = i.id
        jd = JD_form.objects.get(id=pk)
        loc = JD_locations.objects.get(jd_id_id=pk)
        edu = JD_qualification.objects.filter(jd_id_id=pk)
        skill = JD_skills_experience.objects.filter(jd_id_id=pk)
        education = []
        for e in edu:
            education.append(e.qualification + "  " + e.specialization)
        skills = []
        for s in skill:
            skills.append(s.skill)
        data = {
            "job_title": [jd.job_title],
            "Technical requirements": [jd.job_description],
            "Minimum Experience": [str(jd.min_exp)],
            "Maximum Experience": [str(jd.max_exp)],
            "salary_range": [str("") + "-" + str("")],
            "Others": [],
            "organisation_information": [],
            "roles_and_responsibilities": [jd.job_description],
            "Additional Information": [],
            "location": [
                loc.country.name + ", " + loc.state.name + ", " + loc.city.name
            ],
            "skills_based_experience": [],
            "Non_Technical requirements": [],
            "edu_qualification": education,
            "MISCELLANEOUS": [],
            "Skills": {"Mapped": skills, "Unmapped": []},
        }
        json_object = json.dumps(data)
        json_object = base64.b64encode(json_object.encode("utf-8"))
        encodedjob = str(json_object, "utf-8")
        body = (
            """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/index">
        <soapenv:Body> <xmp:addOrUpdateCaseWithData><action><index><caseType>job</caseType><indexId>"""
            + jd.user_id.username
            + """</indexId></index><cases><id>"""
            + str(pk)
            + """</id>
        <content>"""
            + str(encodedjob)
            + """</content></cases><refresh>false</refresh><executionMode>SYNC</executionMode></action></xmp:addOrUpdateCaseWithData></soapenv:Body>
        </soapenv:Envelope>
        """
        )
        index_url = settings.index_url
        index_headers = settings.xmp_headers
        response = requests.post(index_url, data=body, headers=index_headers)
        # time.sleep(2)
        # result=matching_api_to_db(request,jd_id=pk,can_id=None)
    result = {"success": True}
    return JsonResponse(result, safe=False)


def generate_candidate_json(request, pk=None):
    matching_api_to_db(request, can_id=pk, jd_id=None)


def generate_jd_json(request, pk=None):
    user_id, updated_by = admin_account(request)
    jd_list = JD_form.objects.filter(user_id=user_id, jd_status_id=1)
    # for i in jd_list:
    # 	pk = i.id
    jd = JD_form.objects.get(id=pk)
    loc = JD_locations.objects.get(jd_id_id=pk)
    edu = JD_qualification.objects.filter(jd_id_id=pk)
    skill = JD_skills_experience.objects.filter(jd_id_id=pk)
    education = []
    for e in edu:
        education.append(e.qualification + "  " + e.specialization)
    skills = []
    for s in skill:
        skills.append(s.skill)
    data = {
        "job_title": [jd.job_title],
        "Technical requirements": [jd.job_description],
        "Minimum Experience": [str(jd.min_exp)],
        "Maximum Experience": [str(jd.max_exp)],
        "salary_range": [str("") + "-" + str("")],
        "Others": [],
        "organisation_information": [],
        "roles_and_responsibilities": [jd.job_description],
        "Additional Information": [],
        "location": [loc.country.name + ", " + loc.state.name + ", " + loc.city.name],
        "skills_based_experience": [],
        "Non_Technical requirements": [],
        "edu_qualification": education,
        "MISCELLANEOUS": [],
        "Skills": {"Mapped": skills, "Unmapped": []},
    }
    json_object = json.dumps(data)
    json_object = base64.b64encode(json_object.encode("utf-8"))
    encodedjob = str(json_object, "utf-8")
    body = (
        """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/index">
    <soapenv:Body> <xmp:addOrUpdateCaseWithData><action><index><caseType>job</caseType><indexId>"""
        + user_id.username
        + """</indexId></index><cases><id>"""
        + str(pk)
        + """</id>
    <content>"""
        + str(encodedjob)
        + """</content></cases><refresh>false</refresh><executionMode>SYNC</executionMode></action></xmp:addOrUpdateCaseWithData></soapenv:Body>
    </soapenv:Envelope>
    """
    )
    index_url = settings.index_url
    index_headers = settings.xmp_headers
    response = requests.post(index_url, data=body, headers=index_headers)
    time.sleep(2)
    result = matching_api_to_db(request, jd_id=pk, can_id=None)
    result = {"success": True}
    return JsonResponse(result, safe=False)


def applicant_genarate_json(request, pk=None):
    try:
        emp_pool = employer_pool.objects.get(id=pk)
        projects = Projects.objects.filter(application_id_id=emp_pool.candidate_id_id)
        education = Education.objects.filter(application_id_id=emp_pool.candidate_id_id)
        experiences = Experiences.objects.filter(
            application_id_id=emp_pool.candidate_id_id
        )
        skills = Skills.objects.filter(application_id_id=emp_pool.candidate_id_id)
        personal = Personal_Info.objects.get(application_id=emp_pool.candidate_id_id)
        exp_list = []
        edu_list = []
        for exp in experiences:
            ex = {
                "work ex": {
                    "Organisation": exp.organisations,
                    "Skills": exp.work_tools.split(","),
                    "Location": exp.work_location,
                    "Start Date": str(exp.from_exp),
                    "End Date": str(exp.to_exp),
                    "Designation": exp.designation,
                    "Role&Res": [exp.work_role],
                }
            }
            exp_list.append(ex)
        for pro in projects:
            ex = {
                "work ex": {
                    "Organisation": pro.work_proj_client,
                    "Skills": pro.work_proj_skills.split(","),
                    "Location": pro.work_proj_location,
                    "Designation": pro.work_proj_desig,
                    "Role&Res": [pro.work_proj_role],
                }
            }
            exp_list.append(ex)
        for edu in education:
            ed = {
                "Qual": {
                    "Qualification": edu.qual_title,
                    "Specialization": edu.qual_spec,
                    "Institute": edu.institute_name,
                    "Year": edu.year_completed,
                }
            }
            edu_list.append(ed)
        data = {
            "File Name": personal.firstname + ".docx",
            "Experience": exp_list,
            "Technical Skills": emp_pool.skills.split(","),
            "Qualification": edu_list,
            "Personal": {
                "LinkedIn": personal.linkedin_url,
                "Code Repo": personal.code_repo,
                "Date of Birth": str(personal.Date_of_birth),
                "Phone": [personal.contact_no],
                "Name": personal.firstname,
                "Email": personal.email,
                "location": [""],
            },
        }
        json_object = json.dumps(data)
        json_object = base64.b64encode(json_object.encode("utf-8"))
        encodedcandi = str(json_object, "utf-8")
        body = (
            """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/index">
        <soapenv:Body> <xmp:addOrUpdateCaseWithData><action><index><caseType>candidate</caseType><indexId>"""
            + emp_pool.client_id.username
            + """</indexId></index><cases><id>"""
            + str(pk)
            + """</id>
        <content>"""
            + str(encodedcandi)
            + """</content></cases><refresh>false</refresh><executionMode>SYNC</executionMode></action></xmp:addOrUpdateCaseWithData></soapenv:Body>
        </soapenv:Envelope>
        """
        )
        index_url = settings.index_url
        index_headers = settings.xmp_headers
        response = requests.post(index_url, data=body, headers=index_headers)
        # time.sleep(2)
        # result=matching_api_to_db(request,jd_id=None,can_id=pk)
    except Exception as e:
        logger.error("Error in candidate indexing" + str(e))
    data = {"success": True}
    return JsonResponse(data)


# canddate and job need to pass with function parms
def remove_case_id(request=None, can_id=None, jd_id=None):
    user_id, updated_by = admin_account(request)
    if jd_id == None:
        remove_data = (
            """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/index">
                <soapenv:Body>
                    <xmp:removeCase>
                        <action>
                            <index>
                                <caseType>candidate</caseType>
                                <indexId>"""
            + user_id.username
            + """</indexId>
                            </index>
                             <ids>"""
            + str(can_id)
            + """</ids>
                                
                            <refresh>false</refresh>
                            <executionMode>ASYNC</executionMode>
                        </action>
                    </xmp:removeCase>
                </soapenv:Body>
            </soapenv:Envelope>"""
        )
    else:
        remove_data = (
            """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/index">
                <soapenv:Body>
                    <xmp:removeCase>
                        <action>
                            <index>
                                <caseType>job</caseType>
                                <indexId>"""
            + user_id.username
            + """</indexId>
                            </index>
                             <ids>"""
            + str(jd_id)
            + """</ids>
                                
                            <refresh>false</refresh>
                            <executionMode>ASYNC</executionMode>
                        </action>
                    </xmp:removeCase>
                </soapenv:Body>
            </soapenv:Envelope>"""
        )

    index_url = settings.index_url
    index_headers = settings.xmp_headers
    response = requests.post(index_url, data=remove_data, headers=index_headers)
    return True


# def matching_api_to_db(request,can_id=None,jd_id=None):
# 	if request.user.is_staff == True:
# 		user_id,updated_by = admin_account(request)
# 	else:
# 		user_id = User_Info.objects.get(user_id=request.user).employer_id
# 		user_id = User.objects.get(id=user_id)
# 	match_url =settings.match_url
# 	index_headers =settings.xmp_headers
# 	if jd_id != None:
# 		match_data = """
# 		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/match">
# 		<soapenv:Body><xmp:match><action><index><caseType>candidate</caseType><indexId>"""+user_id.username+"""</indexId>
# 		</index><conditions><xmp:profileCaseCondition><occur>SHOULD</occur><weight>1</weight><sourceIndex>
# 		<caseType>job</caseType><indexId>"""+user_id.username+"""</indexId></sourceIndex><sourceCaseId>"""+str(jd_id)+"""</sourceCaseId>
# 		</xmp:profileCaseCondition></conditions></action></xmp:match></soapenv:Body></soapenv:Envelope>
# 		"""
# 	else:
# 		match_data = """
# 		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/match">
# 		<soapenv:Body><xmp:match><action><index><caseType>job</caseType><indexId>"""+user_id.username+"""</indexId>
# 		</index><conditions><xmp:profileCaseCondition><occur>SHOULD</occur><weight>1</weight><sourceIndex>
# 		<caseType>candidate</caseType><indexId>"""+user_id.username+"""</indexId></sourceIndex><sourceCaseId>"""+str(can_id)+"""</sourceCaseId>
# 		</xmp:profileCaseCondition></conditions></action></xmp:match></soapenv:Body></soapenv:Envelope>
# 		"""
# 	response = requests.post(match_url, data = match_data, headers = index_headers)
# 	data_dict = xmltodict.parse(response.content)
# 	json_data = json.dumps(data_dict)
# 	user_id,updated_by = admin_account(request)
# 	try:
# 		with open(base_dir+"/media/data.json", "w") as json_file:
# 			json_file.write(json_data)
# 	except:
# 		with open(os.getcwd()+"/media/data.json", "w") as json_file:
# 			json_file.write(json_data)
# 	json_file.close()
# 	f = open(base_dir+'/media/data.json',)
# 	matching_data = json.load(f)
# 	try:
# 		matching_data=matching_data['soap:Envelope']['soap:Body']['ns2:matchResponse']['return']['matches']
# 		if type(matching_data) == list :
# 			for i in matching_data:
# 				try:
# 					score =round(float(i['score'])*100)

# 					if jd_id != None:
# 						if not 'can'in  i['id']:
# 							if employer_pool.objects.filter(id=int(i['id']),client_id=user_id).exists():
# 								if not  Matched_candidates.objects.filter(candidate_id_id=int(i['id']),jd_id_id=jd_id).exists():
# 									Matched_candidates.objects.create(candidate_id_id=int(i['id']),
# 											jd_id_id=jd_id,
# 											profile_match=score,
# 															)
# 									zita_match_candidates.objects.create(
# 										jd_id_id=jd_id,
# 										candidate_id_id=int(i['id']),
# 										client_id=user_id,
# 										status_id_id=5,
# 										updated_by=user_id.username,)
# 								else:
# 									Matched_candidates.objects.filter(candidate_id_id=int(i['id']),
# 											jd_id_id=jd_id,).update(
# 											profile_match=score,
# 															)
# 				except Exception as e:
# 		else:
# 			try:
# 				score =round(float(matching_data['score'])*100)

# 				if jd_id != None:
# 					if not 'can'in  matching_data['id']:
# 						if employer_pool.objects.filter(id=int(matching_data['id']),client_id=user_id).exists():
# 							if not  Matched_candidates.objects.filter(candidate_id_id=int(matching_data['id']),jd_id_id=jd_id).exists():

# 								Matched_candidates.objects.create(candidate_id_id=int(matching_data['id']),
# 										jd_id_id=jd_id,
# 										profile_match=score,
# 														)
# 								zita_match_candidates.objects.create(
# 									jd_id_id=jd_id,
# 									candidate_id_id=int(matching_data['id']),
# 									client_id=user_id,
# 									status_id_id=5,
# 									updated_by=user_id.username,)


# 							else:
# 								Matched_candidates.objects.filter(candidate_id_id=int(matching_data['id']),
# 										jd_id_id=jd_id,).update(
# 										profile_match=score,
# 														)
# 			except Exception as e:
# 	except Exception as e:
# 		logger.error("error in Matching API , and the Error is "+str(e))
# 	return True
def new_parse_func(filename):
    data = ResumeParser(settings.BASE_DIR + "/media/" + filename).get_extracted_data()
    return data


def total_res_parse_func(filename, can_id):
    headers = {"Authorization": settings.rp_api_auth_token}
    url = settings.rp_api_url
    try:
        files = {"resume_file": open(os.getcwd() + "/" + "media/" + filename, "rb")}
    except:
        files = {"resume_file": open(base_dir + "/" + "media/" + filename, "rb")}
    result = requests.post(url, headers=headers, files=files)
    response_json = json.loads(result.content)
    # data = new_parse_func(filename)
    response_json["file_data"]["mapped skills"] = list(
        set(response_json["file_data"]["mapped skills"])
    )
    res_qual = list(
        chain.from_iterable(response_json["file_data"]["LR Output"]["qualification"])
    )
    res_qual = " ".join(res_qual)
    res_qual = res_qual.split()
    qual_name = []
    qual = ""
    qualifi = []
    for i in res_qual:
        if i.lower().strip() in settings.dip:
            qual_name.append("Diploma")
        if i.lower().strip() in settings.ug:
            qual_name.append("Bachelors")
        if i.lower().strip() in settings.pg:
            qual_name.append("Masters")
        if i.lower().strip() in settings.phd:
            qual_name.append("Doctorate")
    if "Diploma" in qual_name:
        qual = "Diploma"
    if "Bachelors" in qual_name:
        qual = "Bachelors"
    if "Masters" in qual_name:
        qual = "Masters"
    if "Doctorate" in qual_name:
        qual = "Doctorate"
    sublist = response_json["file_data"]["mapped skills"]
    sot_skills = [re.split("(\d\).\s)", a) for a in sublist]
    total_skill = [item.strip().upper() for sublist in sot_skills for item in sublist]
    total_skill = [t for t in total_skill if not re.match(r"\d\).", t)]
    total_skill = [t for t in total_skill if len(t) > 0]
    total_skill = [i.split(",") for i in total_skill]
    total_skill = [item for sublist in total_skill for item in sublist]
    total_skill = [i.strip() for i in total_skill]
    total_skill = list(dict.fromkeys(total_skill))
    skill_list = ", ".join(total_skill)
    employer_pool.objects.filter(id=can_id).update(skills=skill_list)
    employer_pool.objects.filter(id=can_id).update(qualification=qual)


from datetime import datetime
import time

# def save_time_to_file(time_taken, can_id,jd_id,total_tokens):
#     file_name = "timetaken.txt"
#     with open(file_name, 'a+') as file:
#         file.write(f"jd_id :{jd_id} Can ID: {can_id}, Time taken: {time_taken} seconds  token consumed {total_tokens}\n")


def matching_api_to_db(request, can_id=None, jd_id=None):
    try:
        user, updated_by = admin_account(request)
    except:
        if request.user.is_staff:
            user = request.user
        else:
            user = employer_pool.objects.get(id=can_id).client_id
    sub_user = request.user
    plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
    if can_id != None and jd_id != None:
        basic_matching_plan = [6, 7, 10, 11]
        if plan_id in basic_matching_plan:
            # if not client_features_balance.objects.filter(Q(client_id=user, feature_id=62)).exists():
            if applicants_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).exists():
                adv_match = AdvancedAIMatching(jd_id, can_id, user, "applicants",sub_user = sub_user)
                content = zita_matched_candidates(user, jd_id, can_id, "ai")
                return Response(content)
            else:
                basic_score = basic_matching(can_id, jd_id, user, request)
                if basic_score["skills_percent"] > 0:
                    content = zita_matched_candidates(user, jd_id, can_id, "basic")
                return Response(basic_score)

        else:
            if not applicants_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).exists():
                basic_score = basic_matching(can_id, jd_id, user, request)
                if basic_score["skills_percent"] > 0:
                    content = zita_matched_candidates(user, jd_id, can_id, "basic")
                # adv_match = AdvancedAIMatching(jd_id,can_id,user,'candidates')
                # content = zita_matched_candidates(user,jd_id,can_id,'ai')
            else:
                descriptive = client_features_balance.objects.get(
                    client_id=user, feature_id=6
                ).available_count
                if descriptive > 0:
                    adv_match = AdvancedAIMatching(jd_id, can_id, user, "applicants",sub_user = sub_user)
                else:
                    descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                    adv_match = AdvancedAIMatching(jd_id, can_id, user, "applicants",sub_user = sub_user)
                content = zita_matched_candidates(user, jd_id, can_id, "ai")
            return Response(content)

    elif can_id == None and jd_id != None:
        try:
            candidate = employer_pool.objects.filter(
                client_id=user, first_name__isnull=False, email__isnull=False
            ).values("id")
            for i in candidate:
                can_id = i["id"]
                basic_matching_plan = [6, 7, 10, 11]
                if plan_id in basic_matching_plan:
                    # if not client_features_balance.objects.filter(Q(client_id=user, feature_id=55)).exists():
                    if applicants_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id
                    ).exists():
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "applicants",sub_user = sub_user
                        )
                        content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        # return Response(content)
                    else:
                        basic_score = basic_matching(can_id, jd_id, user, request)
                        if basic_score["skills_percent"] > 0:
                            content = zita_matched_candidates(
                                user, jd_id, can_id, "basic"
                            )
                else:
                    if not applicants_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id
                    ).exists():
                        # adv_match = AdvancedAIMatching(jd_id,can_id,user,'candidates')
                        # content = zita_matched_candidates(user,jd_id,can_id,'ai')
                        basic_score = basic_matching(can_id, jd_id, user, request)
                        if basic_score["skills_percent"] > 0:
                            content = zita_matched_candidates(
                                user, jd_id, can_id, "basic"
                            )
                    else:
                        descriptive = client_features_balance.objects.get(
                            client_id=user, feature_id=6
                        ).available_count
                        if descriptive > 0:
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user=sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        else:
                            descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user=sub_user
                            )
            return Response({"suceess": True})
        except Exception as e:
            return Response({"suceess": False, "Error": str(e)})
    elif can_id != None and jd_id == None:
        jobs = JD_form.objects.filter(user_id=user.id, jd_status_id=1).values("id")
        try:
            for i in jobs:
                jd_id = i["id"]
                basic_matching_plan = [6, 7, 10, 11]
                if plan_id in basic_matching_plan:
                    # if not client_features_balance.objects.filter(Q(client_id=user, feature_id=62)).exists():
                    if applicants_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id
                    ).exists():
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "applicants",sub_user=sub_user
                        )
                        content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        # return Response(content)
                    else:
                        basic_score = basic_matching(can_id, jd_id, user, request)
                        if basic_score["skills_percent"] > 0:
                            content = zita_matched_candidates(
                                user, jd_id, can_id, "basic"
                            )
                else:
                    if not applicants_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id
                    ).exists():
                        # adv_match = AdvancedAIMatching(jd_id,can_id,user,'candidates')
                        # content = zita_matched_candidates(user,jd_id,can_id,'ai')
                        basic_score = basic_matching(can_id, jd_id, user, request)
                        if basic_score["skills_percent"] > 0:
                            content = zita_matched_candidates(
                                user, jd_id, can_id, "basic"
                            )
                    else:
                        descriptive = client_features_balance.objects.get(
                            client_id=user, feature_id=6
                        ).available_count
                        if descriptive > 0:
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user=sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        else:
                            descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user=sub_user
                            )

            return Response({"suceess": True})
        except Exception as e:
            return Response({"suceess": False, "Error": str(e)})


@login_required
@recruiter_required
def get_candlist_info(db_data, jd_id=None):
    if jd_id != None:
        jd_profile1 = JD_profile.objects.filter(jd_id=jd_id).values(
            "business_intelligence",
            "data_analysis",
            "data_engineering",
            "devops",
            "machine_learning",
            "others",
        )
        jd_profile = [
            float(jd_profile1[0]["business_intelligence"]),
            float(jd_profile1[0]["data_analysis"]),
            float(jd_profile1[0]["data_engineering"]),
            float(jd_profile1[0]["devops"]),
            float(jd_profile1[0]["machine_learning"]),
            float(jd_profile1[0]["others"]),
        ]
        rador = []
        for r in db_data:
            cand_profile1 = Visualize.objects.filter(application_id_id=r).values(
                "business_intelligence",
                "data_analysis",
                "data_engineering",
                "devops",
                "machine_learning",
                "others",
            )
            rador.append(
                [
                    r,
                    jd_profile,
                    [
                        float(cand_profile1[0]["business_intelligence"]),
                        float(cand_profile1[0]["data_analysis"]),
                        float(cand_profile1[0]["data_engineering"]),
                        float(cand_profile1[0]["devops"]),
                        float(cand_profile1[0]["machine_learning"]),
                        float(cand_profile1[0]["others"]),
                    ],
                ]
            )
    else:
        rador = []
    recom_cand_list = []
    for app_id in db_data:
        user_user_id = [
            i["user_id_id"]
            for i in User_Info.objects.filter(application_status=100).values(
                "user_id_id"
            )
        ]
        app_user_id = Personal_Info.objects.filter(application_id=app_id).values(
            "user_id_id"
        )[0]["user_id_id"]
        if app_user_id in user_user_id:
            role1 = User_Info.objects.filter(user_id_id=app_user_id).values(
                "recommended_role"
            )[0]["recommended_role"]
            if role1 != "":
                role = role1
            else:
                role = "Fresher"
        else:
            role = "Fresher"
        personal = Personal_Info.objects.filter(application_id=app_id).values(
            "firstname",
            "lastname",
            "current_city",
            "current_state",
            "current_country",
            "exp_gross",
        )
        name = personal[0]["firstname"] + " " + personal[0]["lastname"]
        loc = ",".join(
            [
                personal[0]["current_city"],
                personal[0]["current1_state"],
                personal[0]["current1_country"],
            ]
        )
        ctc = personal[0]["exp_gross"]
        edu = Education.objects.filter(application_id=app_id).values(
            "qual_spec", "qual_title", "year_completed"
        )
        try:
            if len(edu) > 1:
                try:
                    year = max(
                        [
                            int(edu[i]["year_completed"])
                            for i in range(len(edu))
                            if edu[i]["year_completed"] != ""
                        ]
                    )
                    for i in range(len(edu)):
                        try:
                            if int(edu[i]["year_completed"]) == year:
                                qual = edu[i]["qual_title"] + "," + edu[i]["qual_spec"]
                        except ValueError:
                            pass
                except ValueError:
                    qual = edu[0]["qual_title"] + "," + edu[0]["qual_spec"]

            else:
                qual = edu[0]["qual_title"] + "," + edu[0]["qual_spec"]
        except IndexError:
            qual = ""

        qual = re.sub(r"[^a-zA-Z0-9,]+", " ", qual)

        try:
            exp_y = Additional_Details.objects.filter(application_id=app_id).values(
                "total_exp_year"
            )[0]["total_exp_year"]
        except IndexError:
            exp_y = 0
        try:
            exp_m = Additional_Details.objects.filter(application_id=app_id).values(
                "total_exp_month"
            )[0]["total_exp_month"]
        except IndexError:
            exp_m = 0
        exp = round(exp_y + exp_m / 12)
        np = (
            Personal_Info.objects.filter(application_id=app_id)
            .values("available_to_start")[0]["available_to_start"]
            .lower()
        )
        S = Skills.objects.filter(application_id=app_id).values("tech_skill")
        if len(S) == 0:
            skill = []
        else:
            skill1 = S[0]["tech_skill"].split(",")
            skill = [i.strip() for i in skill1]
            skill = re.sub(r"[^a-zA-Z0-9,+#./]+", " ", str(skill))
        try:
            match = Recommended_candidates.objects.filter(
                candidate_id_id=app_id
            ).values("percentage_profile_match", "percentage_skill_match")
            p_match = round(float(match[0]["percentage_profile_match"]))
            s_match = round(float(match[0]["percentage_skill_match"]))
        except IndexError:
            s_match = 0
            p_match = 0

        recom_cand_list.append(
            [
                app_id,
                {
                    "name": name,
                    "location": loc,
                    "exp_CTC": ctc,
                    "qual": qual,
                    "n_exp": exp,
                    "role": role,
                    "tech_skills": skill,
                    "profile_match": p_match,
                    "skill_match": s_match,
                    "notice_period": np,
                },
                rador,
            ]
        )
    return recom_cand_list


@login_required
@recruiter_required
def recom_cand(request, pk=None):
    jd_id = int(pk)
    db_data1 = Recommended_candidates.objects.filter(jd_id=jd_id).values(
        "candidate_id_id"
    )
    db_data = [i["candidate_id_id"] for i in db_data1]
    recom_cand_list = get_candlist_info(db_data, jd_id)

    db_data2 = Applicants.objects.filter(jd_id=jd_id, status__gte=3).values(
        "candidate_id_id"
    )
    db_data_s1 = [i["candidate_id_id"] for i in db_data2]
    db_data3 = Recommended_candidates.objects.filter(jd_id=jd_id, status__gte=3).values(
        "candidate_id_id"
    )
    db_data_s2 = [i["candidate_id_id"] for i in db_data3]
    db_data_s = db_data_s1 + db_data_s2

    context = {
        "cand_object": recom_cand_list,
        "pk": jd_id,
        "db_data_s": db_data_s,
        "match_len": db_data,
    }

    if "shortlisted" in request.GET:
        j = request.GET.get("shortlisted")
        jd_id = int(pk)
        Recommended_candidates.objects.filter(jd_id=jd_id, candidate_id_id=j).update(
            status=3
        )

    return render(request, "jobs/recommended_cand.html", context)


@login_required
@recruiter_required
def applicants_lists(request, pk=None):
    jd_id = int(pk)
    db_data1 = Applicants.objects.filter(jd_id=jd_id, status__gte=2).values(
        "candidate_id_id"
    )
    db_data = [i["candidate_id_id"] for i in db_data1]
    recom_cand_list = get_candlist_info(db_data, jd_id)

    db_data2 = Applicants.objects.filter(jd_id=jd_id, status__gte=3).values(
        "candidate_id_id"
    )
    db_data_s1 = [i["candidate_id_id"] for i in db_data2]
    db_data3 = Recommended_candidates.objects.filter(jd_id=jd_id, status__gte=3).values(
        "candidate_id_id"
    )
    db_data_s2 = [i["candidate_id_id"] for i in db_data3]
    db_data_s = db_data_s1 + db_data_s2

    tech_s = Skills.objects.values("tech_skill")
    skill5 = [i["tech_skill"].split(",") for i in tech_s]
    all_skill = []
    for i in skill5:
        for j in i:
            if j != "" and j.lower() not in all_skill:
                all_skill.append((j.strip()).lower())

    skill_list = [
        re.sub(r"[^a-zA-Z0-9,+()./]+", " ", i).strip() for i in list(set(all_skill))
    ]

    context = {
        "pk": jd_id,
        "cand_object": recom_cand_list,
        "match_len": db_data,
        "db_data_s": db_data_s,
        "skill_list": list(set(skill_list)),
    }

    if "shortlisted" in request.GET:
        j = request.GET.get("shortlisted")
        jd_id = int(pk)
        Applicants.objects.filter(jd_id=jd_id, candidate_id_id=j).update(status=3)

    return render(request, "jobs/applicants.html", context)


@login_required
@recruiter_required
def shortlist_cand(request, pk=None):
    jd_id = int(pk)
    db_data2 = Applicants.objects.filter(jd_id=jd_id, status__gte=3).values(
        "candidate_id_id"
    )
    db_data_s1 = [i["candidate_id_id"] for i in db_data2]
    db_data3 = Recommended_candidates.objects.filter(jd_id=jd_id, status__gte=3).values(
        "candidate_id_id"
    )
    db_data_s2 = [i["candidate_id_id"] for i in db_data3]
    db_data = db_data_s1 + db_data_s2
    recom_cand_list = get_candlist_info(db_data, jd_id)

    context = {"cand_object": recom_cand_list, "pk": jd_id, "match_len": db_data}

    if "unshortlisted" in request.GET:
        jd_id = int(pk)
        j = request.GET.get("unshortlisted")
        Applicants.objects.filter(jd_id=jd_id, candidate_id_id=j).update(status=2)
        Recommended_candidates.objects.filter(jd_id=jd_id, candidate_id_id=j).update(
            status=0
        )

    return render(request, "jobs/shortlist_cand.html", context)


@login_required
@recruiter_required
def search_cand(request):
    user = [
        i["user_id_id"]
        for i in User_Info.objects.filter(application_status=100).values("user_id_id")
    ]
    db_data = []
    for i in user:
        for j in Personal_Info.objects.filter(user_id_id=i).values("application_id"):
            db_data.append(j["application_id"])
    recom_cand_list = get_candlist_info(sorted(db_data))

    tech_s = Skills.objects.values("tech_skill")
    skill5 = [i["tech_skill"].split(",") for i in tech_s]
    all_skill = []
    for i in skill5:
        for j in i:
            if j != "" and j.lower() not in all_skill:
                all_skill.append((j.strip()).lower())

    skill_list = [
        re.sub(r"[^a-zA-Z0-9,+()./]+", " ", i).strip() for i in list(set(all_skill))
    ]
    context = {
        "cand_object": recom_cand_list,
        "match_len": db_data,
        "skill_list": list(set(skill_list)),
    }

    return render(request, "jobs/search_cand.html", context)


@login_required
@recruiter_required
def analytics(request):
    user = User.objects.get(username=request.user).id
    jd_ids = JD_form.objects.filter(user_id=user).values("id")
    int_list = {
        "jd_id_pk": [],
        "jd_titles": [],
        "posted_at": [],
        "jd_status": [],
        "cities": [],
        "views": [],
        "recommended_candidates": [],
        "applicants": [],
        "shortlisted": [],
        "interviewed": [],
        "hired": [],
    }
    final_list = []
    for a in jd_ids:
        int_list["jd_id_pk"].append(a["id"])
        int_list["jd_titles"].append(JD_form.objects.get(id=a["id"]).job_title)
        int_list["posted_at"].append(JD_form.objects.get(id=a["id"]).job_posted_on)
        int_list["jd_status"].append(JD_form.objects.get(id=a["id"]).jd_status)
        int_list["cities"].append(JD_form.objects.get(id=a["id"]).work_city)
        int_list["applicants"].append(
            Applicants.objects.filter(jd_id=a["id"], status__gte=2).count()
        )
        int_list["recommended_candidates"].append(
            Recommended_candidates.objects.filter(jd_id=a["id"]).count()
        )
        int_list["shortlisted"].append(
            Applicants.objects.filter(jd_id=a["id"], status=3).count()
            + Recommended_candidates.objects.filter(jd_id=a["id"], status=3).count()
        )
        int_list["views"].append(
            Applicants.objects.filter(jd_id=a["id"], status__gte=1).count()
        )
        int_list["interviewed"].append(
            Applicants.objects.filter(jd_id=a["id"], status__gte=4).count()
            + Recommended_candidates.objects.filter(
                jd_id=a["id"], status__gte=4
            ).count()
        )
        int_list["hired"].append(
            Applicants.objects.filter(jd_id=a["id"], status=6).count()
            + Recommended_candidates.objects.filter(jd_id=a["id"], status=6).count()
        )

    for i in range(0, len(int_list["jd_titles"])):
        final_list.append(
            {
                "jd_titles": int_list["jd_titles"][i],
                "jd_id_pk": int_list["jd_id_pk"][i],
                "jd_status": int_list["jd_status"][i],
                "applicants": int_list["applicants"][i],
                "shortlisted": int_list["shortlisted"][i],
                "recommended_candidates": int_list["recommended_candidates"][i],
                "views": int_list["views"][i],
                "cities": int_list["cities"][i],
                "interviewed": int_list["interviewed"][i],
                "hired": int_list["hired"][i],
            }
        )
    return render(request, "jobs/analytics.html", {"final_list": final_list})


@login_required
@recruiter_required
def update_or_duplicate_jd(request, pk):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    has_permission = user_permission(request, "create_post")
    if not has_permission == True:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    user_id, updated_by = admin_account(request)
    from_duplicate = (
        request.GET.get("duplicate") if request.GET.get("duplicate") is not None else 0
    )
    logger.info("Is request for duplicate JD " + str(from_duplicate))
    form_jd = jd_form()
    jd = JD_form.objects.filter(id=pk).last()
    try:
        profile_copy = JD_profile.objects.get(jd_id_id=pk)
    except:
        profile_copy = ""
    # user_id = User.objects.get(username = request.user).id
    if "non_ds" in request.GET:
        is_ds_role = 0
    else:
        is_ds_role = 1
    if "duplicate" in request.GET:
        duplicate = 0
    else:
        duplicate = 1
    country_list = [
        {
            i.id: list(State.objects.filter(country=i.id).values("id", "name"))
            for i in Country.objects.all()
            if i.name in countries_to_be_displayed
        }
    ]
    filtered_state = [i["name"] for i in sum(country_list[0].values(), [])]
    state_list = [
        {
            i.id: list(City.objects.filter(state=i.id).values("id", "name"))
            for i in State.objects.all()
            if i.name in filtered_state
        }
    ]

    country = Country.objects.all()
    # country_ids=[country.filter(name__iexact=i)[0].id for i in countries_to_be_displayed]
    # country=country.filter(id__in=country_ids)
    show_sal_to_candidate = jd.show_sal_to_candidate

    profile_confirmation = 1 if JD_profile.objects.filter(jd_id_id=pk).exists() else 0

    job_type = tmeta_job_type.objects.filter(id=jd.job_type.id).values("value")[0][
        "value"
    ]

    location = [
        (
            Country.objects.filter(id=i["country"]).values("name")[0]["name"],
            State.objects.filter(id=i["state"]).values("name")[0]["name"],
            City.objects.filter(id=i["city"]).values("name")[0]["name"],
        )
        for i in JD_locations.objects.filter(jd_id_id=jd.id).values(
            "country", "state", "city"
        )
    ]
    education = [
        (i["qualification"], i["specialization"])
        for i in JD_qualification.objects.filter(jd_id_id=jd.id).values(
            "qualification", "specialization"
        )
    ]
    non_ds_skill = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(
            jd_id_id=jd.id, category_id=5
        ).values("skill")
        if i["skill"] != "NULL"
    ]
    tool = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(
            jd_id_id=jd.id, category_id=4
        ).values("skill")
        if i["skill"] != "NULL"
    ]
    database = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(
            jd_id_id=jd.id, category_id=1
        ).values("skill")
        if i["skill"] != "NULL"
    ]
    platform = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(
            jd_id_id=jd.id, category_id=2
        ).values("skill")
        if i["skill"] != "NULL"
    ]
    misc = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(
            Q(category_id=5) | Q(category_id__isnull=True), jd_id_id=jd.id
        ).values("skill")
        if i["skill"] != "NULL"
    ]
    programming = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(
            jd_id_id=jd.id, category_id=3
        ).values("skill")
        if i["skill"] != "NULL"
    ]
    mand_skills = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(jd_id_id=jd.id).values("skill")
        if i["skill"] != "NULL"
    ]
    mand_skill_exp = [
        i["experience"]
        for i in JD_skills_experience.objects.filter(jd_id_id=jd.id).values(
            "experience"
        )
    ]
    for i in range(len(tool)):
        tool[i] = tool[i] + "*#fad7a0"
    for i in range(len(database)):
        database[i] = database[i] + "*#aed6f1"
    for i in range(len(platform)):
        platform[i] = platform[i] + "*#a2d9ce"
    for i in range(len(misc)):
        misc[i] = misc[i] + "*#e8daef"
    for i in range(len(programming)):
        programming[i] = programming[i] + "*#f5b7b1"

    try:
        skill_n_exp1 = {}
        for i in JD_skills_experience.objects.filter(jd_id_id=pk).values(
            "skill", "experience"
        ):
            skill_n_exp1[i["skill"]] = i["experience"]
        skill_n_exp = [skill_n_exp1]
    except:
        skill_n_exp = []
    profile = 0
    if "parsing" in request.GET:
        profile = 1
        form_upload = JDfiles.objects.filter(user_id=request.user.id).last()
        filepath_str = form_upload.jd_file
        file_path = str(filepath_str)
        filepath = file_path.split("/")
        filename = filepath[1]
        try:
            json_data = open(base_dir + "/" + "media/jd_output/" + filename + ".json")
        except:
            json_data = open(
                os.getcwd() + "/" + "media/jd_output/" + filename + ".json"
            )
        data_jd = json.load(json_data)
        form_jd = jd_form()
        form_qual = jd_qualification_form()
        form_skill = jd_skills_experience_form()
        try:
            form_jd.fields["job_title"].initial = (", ").join(data_jd["job_title"])[:59]
        except KeyError:
            pass
        try:
            o_inf = data_jd["organisation_information"]

        except KeyError:
            pass
        try:
            form_jd.fields["min_exp"].initial = data_jd["Minimum Experience"][0]
        except KeyError:
            pass

        try:
            if data_jd["Maximum Experience"][0] != None:
                form_jd.fields["max_exp"].initial = data_jd["Maximum Experience"][0]
        except KeyError:
            try:
                if len(data_jd["Minimum Experience"]) > 1:
                    form_jd.fields["max_exp"].initial = data_jd["Minimum Experience"][1]
            except KeyError:
                pass
        try:
            if jd.job_id != "NULL":
                form_jd.fields["job_id"].initial = jd.job_id
        except KeyError:
            pass
        qual1 = []
        try:
            qual = data_jd["edu_qualification"]
            import re

            qual_list = re.split(", |_|-|!|\+", qual[0])
            for i in qual_list:
                if i.lower().strip() in settings.ug:
                    qual1.append("Bachelors")
                if i.lower().strip() in settings.pg:
                    qual1.append("Masters")
                if i.lower().strip() in settings.phd:
                    qual1.append("Doctorate")
        except KeyError:
            pass
        try:
            add_in = data_jd["Additional Information"]

        except KeyError:
            pass
        role_and_res = []
        try:
            roles = data_jd["roles_and_responsibilities"]
            role_and_res.append("<h4>Roles and Responsibilities</h4>")
            role_and_res.append("<br>".join(roles))
        except KeyError:
            pass
        try:
            tech_re = data_jd["Technical requirements"]
            role_and_res.append("<h4>Requirements</h4>")
            role_and_res.append("<br>".join(tech_re))
        except KeyError:
            pass
        try:
            non_tech = data_jd["Non_Technical requirements"]
            # role_and_res.append('<h4>Non Technical Responsibilities</h4>')
            role_and_res.append("<br>".join(non_tech))
        except KeyError:
            pass
        try:
            role_and_res.append("<h4>Organisation Information</h4>")
            role_and_res.append("<br>".join(o_inf))
        except:
            pass
        try:
            role_and_res.append("<h4>Additional Information</h4>")
            role_and_res.append("<br>".join(add_in))
        except:
            pass

        form_jd.fields["richtext_job_description"].initial = "".join(role_and_res)
        try:
            with open(base_dir + "/static/media/skills2.json", "r") as fp:
                data = json.load(fp)
        except:
            with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
                data = json.load(fp)

        # dummy = ['JDBC', 'UML', 'ACCESS-VBA', 'STATA','SQL']

        mand_skills = data_jd["Skills"]["Mapped"]
        tool = []
        database = []
        platform = []
        misc = []
        programming = []
        # t = datetime.now()
        for prof in data:
            for i in data[prof]:
                for skill in mand_skills:
                    if skill.upper() in data[prof][i]:
                        if i == "tool":
                            tool.append(skill + "*#fad7a0")
                        elif i == "database":
                            database.append(skill + "*#aed6f1")
                        elif i == "platform":
                            platform.append(skill + "*#a2d9ce")
                        elif i == "programming":
                            programming.append(skill + "*#f5b7b1")
                        else:
                            misc.append(skill + "*#e8daef")

        tool = list(dict.fromkeys(tool))
        database = list(dict.fromkeys(database))
        platform = list(dict.fromkeys(platform))
        misc = list(dict.fromkeys(misc))
        programming = list(dict.fromkeys(programming))
        # company_logo_path = None
        # mand_skills=[ j+'*#d0d0d0' for j in mand_skills]
        form_skill.fields["skill"].initial = data_jd["Skills"]["Mapped"]

        try:
            form_jd.fields["salary_min"].initial = data_jd["SALARY_RANGE"]
        except KeyError:
            pass
        work_country1 = ""
        work_state1 = ""
        work_city1 = ""
        state = ""
        city = ""
        spec1 = [
            i["specialization"] if i["specialization"] != "NULL" else ""
            for i in JD_qualification.objects.filter(jd_id_id=pk).values(
                "specialization"
            )
        ]
    else:
        work_country1 = [
            Country.objects.filter(id=i["country"]).values("id", "name")[0]
            for i in JD_locations.objects.filter(jd_id_id=pk).values("country")
        ]
        work_state1 = [
            State.objects.filter(id=i["state"]).values("id", "name")[0]
            for i in JD_locations.objects.filter(jd_id_id=pk).values("state")
        ]
        work_city1 = [
            City.objects.filter(id=i["city"]).values("id", "name")[0]
            for i in JD_locations.objects.filter(jd_id_id=pk).values("city")
        ]
        state = list(
            State.objects.filter(
                country_id=JD_locations.objects.get(jd_id_id=pk).country.id
            ).values("id", "name")
        )
        city = list(
            City.objects.filter(
                state_id=JD_locations.objects.get(jd_id_id=pk).state.id
            ).values("id", "name")
        )
        qual1 = [
            i["qualification"] if i["qualification"] != "NULL" else ""
            for i in JD_qualification.objects.filter(jd_id_id=pk).values(
                "qualification"
            )
        ]
        spec1 = [
            i["specialization"] if i["specialization"] != "NULL" else ""
            for i in JD_qualification.objects.filter(jd_id_id=pk).values(
                "specialization"
            )
        ]
        try:
            if jd.job_title != "NULL":
                form_jd.fields["job_title"].initial = jd.job_title
        except KeyError:
            pass
        # try:
        # 	form_jd.fields['org_info'].initial = jd.org_info
        # except KeyError:
        # 	pass
        try:
            form_jd.fields["job_type"].initial = jd.job_type_id
        except KeyError:
            pass
        try:
            form_jd.fields["job_role"].initial = jd.job_role
        except KeyError:
            pass
        try:
            if int(jd.min_exp) >= 0:
                form_jd.fields["min_exp"].initial = int(jd.min_exp)
        except KeyError:
            pass
        try:
            if int(jd.max_exp) >= 0:
                form_jd.fields["max_exp"].initial = jd.max_exp
        except:
            pass
        try:
            if jd.job_id != "NULL":
                form_jd.fields["job_id"].initial = jd.job_id
        except KeyError:
            pass
        try:
            form_jd.fields["industry_type"].initial = jd.industry_type_id
        except KeyError:
            pass
        # try:
        # 	if jd.company_name!='NULL':form_jd.fields['company_name'].initial = jd.company_name
        # except KeyError:
        # 	pass
        # try:
        # 	if jd.company_website!='NULL':form_jd.fields['company_website'].initial = jd.company_website
        # except KeyError:
        # 	pass

        try:
            if int(jd.no_of_vacancies) != 0:
                form_jd.fields["no_of_vacancies"].initial = int(jd.no_of_vacancies)
        except KeyError:
            pass
        try:
            if jd.richtext_job_description != "NULL":
                form_jd.fields["richtext_job_description"].initial = (
                    jd.richtext_job_description
                )
        except KeyError:
            pass
        # try:
        # 	if jd.tech_req!='NULL':form_jd.fields['tech_req'].initial = jd.tech_req
        # except KeyError:
        # 	pass
        # try:
        # 	form_jd.fields['add_info'].initial = jd.add_info
        # except KeyError:
        # 	pass
        # try:
        # 	if jd.non_tech_req!='NULL':form_jd.fields['non_tech_req'].initial = jd.non_tech_req
        # except KeyError:
        # 	pass
        try:
            if int(jd.salary_min) != 0:
                form_jd.fields["salary_min"].initial = int(jd.salary_min)
        except KeyError:
            pass
        try:
            if int(jd.salary_max) != 0:
                form_jd.fields["salary_max"].initial = int(jd.salary_max)
        except KeyError:
            pass
        try:
            form_jd.fields["salary_curr_type"].initial = jd.salary_curr_type_id
        except KeyError:
            pass
        # company_logo_path = str(jd.company_logo)

        # company_logo_path = company_logo_path.replace('company_logo/','') if company_logo_path!='0' else company_logo_path

    try:
        with open(base_dir + "/static/media/skills2.json", "r") as fp:
            data = json.load(fp)
    except:
        with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
            data = json.load(fp)

    if request.method == "POST" and "submit_duplicateJD" in request.POST:
        d_jd = request.POST
        logger.info("submitting duplicate JD ")
        # Enable this for bug ZPI-378
        # JD_form.objects.filter(id=pk_id).update(job_reposted_on=datetime.datetime.now())
        # user_id = User.objects.get(username = request.user).id
        # try:
        # 	permission = user_type.objects.get(user_id=request.user).admin_id
        # except:
        # 	permission=0
        # if permission != 0:
        # 	user_id = permission
        work_remote = True if d_jd.get("work_remote") == "on" else False
        # try:
        # 	company_logo = request.FILES['company_logo'] if 'company_logo' in request.FILES else d_jd.get('company_logo')
        # 	company_logo =company_logo if ' ' not in company_logo else company_logo.replace(' ','_')
        # except:
        # if d_jd.get('logo_hidden')!='company_logo/':
        # 	company_logo = d_jd['logo_hidden']
        # if ' ' not in d_jd['logo_hidden'] else d_jd['logo_hidden'].replace(' ','_')
        # else:
        # 	company_logo='0'
        show_sal_to_candidate = (
            True if d_jd.get("show_sal_to_candidate") == "on" else False
        )
        import re

        text_des = re.sub(r"<.*?>", "", d_jd["richtext_job_description"])
        text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
        text_des = re.sub(r"Requirements:", "", text_des)
        job_description = text_des

        if (
            not int(d_jd["job_role"]) == 6
            and (int(d_jd["job_role"]) != int(jd.job_role.id))
            or (job_description != jd.job_description)
        ):
            logger.info("Changes made in profiling relevant fields")
            profiler_input = [job_description]
            if profiler_input != []:
                s_time = datetime.now()
                url = settings.profile_api_url
                headers = {"Authorization": settings.profile_api_auth_token}
                input_texts = profiler_input
                texts_file = {"texts": "||".join(input_texts)}
                result = requests.post(url, headers=headers, data=texts_file)
                logger.debug("Profiling API response: " + str(result))
                try:
                    profiles = result.json()["profiles"]
                    profiles["bi_vis"] = profiles.pop("Business_Intelligence")
                    profiles["data_analysis"] = profiles.pop("Data_Analysis")
                    profiles["data_eng"] = profiles.pop("Data_Engineering")
                    profiles["devops"] = profiles.pop("Dev_Ops")
                    profiles["ml_model"] = profiles.pop("Machine_Learning")
                    sorted_profiles = sorted(
                        profiles.items(), key=lambda kv: (kv[1], kv[0]), reverse=True
                    )
                    recommended_roles = result.json()["recommended_roles"]
                except:
                    profiles = {}
                    profiles["bi_vis"] = 0
                    profiles["data_analysis"] = 0
                    profiles["data_eng"] = 0
                    profiles["devops"] = 0
                    profiles["ml_model"] = 0
                    profiles["others"] = 100
                    sorted_profiles = sorted(
                        profiles.items(), key=lambda kv: (kv[1], kv[0]), reverse=True
                    )
                    recommended_roles = ["others"]
                ds_profile = ""
                if recommended_roles != []:
                    ds_profile = "DS Profile"
                else:
                    ds_profile = "Others"
                    recommended_roles.append(ds_profile)

                classification_url = settings.classification_url
                cl_result = requests.post(
                    classification_url,
                    headers=headers,
                    data={"profiles": profiles.values()},
                )
                job_role_obj = tmeta_ds_main_roles.objects.get(id=d_jd.get("job_role"))
                JD_form.objects.create(
                    user_id=user_id,
                    updated_by=updated_by,
                    job_title=d_jd.get("job_title"),
                    job_role=job_role_obj,
                    job_id=d_jd.get("job_id"),
                    min_exp=d_jd.get("min_exp"),
                    max_exp=d_jd.get("max_exp"),
                    richtext_job_description=d_jd.get("richtext_job_description"),
                    job_description=job_description,
                    job_type_id=int(d_jd.get("job_type")),
                    jd_status_id=int(2),
                    salary_min=d_jd.get("salary_min"),
                    salary_max=d_jd.get("salary_max"),
                    salary_curr_type_id=d_jd.get("salary_curr_type"),
                    show_sal_to_candidate=show_sal_to_candidate,
                    no_of_vacancies=d_jd.get("no_of_vacancies"),
                    work_remote=work_remote,
                    industry_type_id=int(d_jd.get("industry_type")),
                )
                UserActivity.objects.create(
                    user=request.user,
                    action_id=1,
                    action_detail=str(d_jd.get("job_title"))
                    + " ("
                    + str(d_jd.get("job_id"))
                    + ")",
                )

                jd_id = JD_form.objects.filter(user_id=user_id).last()
                qual_list = [
                    value
                    for key, value in d_jd.items()
                    if "qualification" in key.lower()
                ]
                spec_list = [
                    value
                    for key, value in d_jd.items()
                    if "specialization" in key.lower()
                ]
                for q, s in zip(qual_list, spec_list):
                    JD_qualification.objects.create(
                        qualification=q, specialization=s, jd_id_id=jd_id.id
                    )
                if d_jd["job_role"] == "6" or d_jd["job_role"] == 6:

                    skills = d_jd.getlist("mand_skill_non_ds")
                    skills = [i.strip().upper() for i in skills]
                    skills = list(dict.fromkeys(skills))
                    JD_skills_experience.objects.filter(jd_id_id=jd_id.id).delete()
                    for s in skills:
                        JD_skills_experience.objects.create(
                            skill=s, experience=0, jd_id_id=jd_id.id, category_id=5
                        )
                else:
                    mand_skill_list = d_jd.getlist("mand_skill")[0].split("|")
                    skill_exp_list = d_jd.getlist("mand_skill_exp")[0].split(",")

                    if len(skill_exp_list) > 1:
                        skill_l = [
                            skill_exp_list[i]
                            for i in range(len(skill_exp_list))
                            if i % 2 == 0
                        ]
                        exp_l = [
                            skill_exp_list[i]
                            for i in range(len(skill_exp_list))
                            if i % 2 != 0
                        ]
                    else:
                        skill_l = [i for i in mand_skill_list]
                        exp_l = [0] * len(skill_l)

                    database_skill = d_jd.getlist("database_skill")[0].split(",")
                    platform_skill = d_jd.getlist("platform_skill")[0].split(",")
                    programming_skill = d_jd.getlist("programming_skill")[0].split(",")
                    tool_skill = d_jd.getlist("tool_skill")[0].split(",")
                    misc_skill = d_jd.getlist("misc_skill")[0].split(",")
                    for s, e in zip(skill_l, exp_l):
                        if s.lower() in database_skill:
                            JD_skills_experience.objects.create(
                                skill=s, experience=e, jd_id_id=jd_id.id, category_id=1
                            )
                        if s.lower() in platform_skill:
                            JD_skills_experience.objects.create(
                                skill=s, experience=e, jd_id_id=jd_id.id, category_id=2
                            )
                        if s.lower() in programming_skill:
                            JD_skills_experience.objects.create(
                                skill=s, experience=e, jd_id_id=jd_id.id, category_id=3
                            )
                        if s.lower() in tool_skill:
                            JD_skills_experience.objects.create(
                                skill=s, experience=e, jd_id_id=jd_id.id, category_id=4
                            )
                        if s.lower() in misc_skill:
                            JD_skills_experience.objects.create(
                                skill=s, experience=e, jd_id_id=jd_id.id, category_id=5
                            )

                country_list = [
                    value
                    for key, value in d_jd.items()
                    if "work_country" in key.lower()
                ]
                state_list = [
                    value for key, value in d_jd.items() if "work_state" in key.lower()
                ]
                city_list = [
                    value for key, value in d_jd.items() if "work_city" in key.lower()
                ]
                for c, s, ci in zip(country_list, state_list, city_list):
                    JD_locations.objects.create(
                        country_id=int(c),
                        state_id=int(s),
                        city_id=int(ci),
                        jd_id_id=jd_id.id,
                    )
                role_obj = tmeta_ds_main_roles.objects.get(
                    tag_name=recommended_roles[0].replace("_", " ")
                )
                JD_profile.objects.create(
                    jd_id_id=jd_id.id,
                    business_intelligence=profiles["bi_vis"],
                    data_analysis=profiles["data_analysis"],
                    data_engineering=profiles["data_eng"],
                    devops=profiles["devops"],
                    machine_learning=profiles["ml_model"],
                    others=profiles["others"],
                    user_id=user_id,
                    recommended_role=role_obj,
                    dst_or_not=cl_result.json()["dst_or_not"],
                )
                if request.POST["submit_duplicateJD"] == "NEXT":
                    return redirect("jobs:questionnaire", pk=jd_id.id)
                else:
                    return HttpResponseNotModified()
            if int(d_jd["job_role"]) == 6:
                return redirect("jobs:questionnaire", pk=jd_id.id)
            else:
                return redirect("jobs:questionnaire", pk=jd_id.id)

        if d_jd.get("max_exp") == "":
            max_exp = None
        else:
            max_exp = d_jd.get("max_exp")
        job_role_obj = tmeta_ds_main_roles.objects.get(id=d_jd.get("job_role"))
        JD_form.objects.create(
            user_id=user_id,
            updated_by=updated_by,
            job_title=d_jd.get("job_title"),
            job_role=job_role_obj,
            job_id=d_jd.get("job_id"),
            min_exp=d_jd.get("min_exp"),
            max_exp=max_exp,
            richtext_job_description=d_jd.get("richtext_job_description"),
            job_description=job_description,
            job_type_id=int(d_jd.get("job_type")),
            jd_status_id=int(2),
            salary_min=d_jd.get("salary_min"),
            salary_max=d_jd.get("salary_max"),
            salary_curr_type_id=d_jd.get("salary_curr_type"),
            show_sal_to_candidate=show_sal_to_candidate,
            no_of_vacancies=d_jd.get("no_of_vacancies"),
            work_remote=work_remote,
            industry_type_id=int(d_jd.get("industry_type")),
        )
        UserActivity.objects.create(
            user=request.user,
            action_id=1,
            action_detail=str(d_jd.get("job_title"))
            + " ("
            + str(d_jd.get("job_id"))
            + ")",
        )

        jd_id = JD_form.objects.filter(user_id=user_id).last()

        try:
            profile_copy.pk = None
            profile_copy.jd_id_id = jd_id.id
            profile_copy.save()
        except Exception as e:
            logger.error("Falied to save profiling data: " + str(e))

        qual_list = [
            value for key, value in d_jd.items() if "qualification" in key.lower()
        ]
        spec_list = [
            value for key, value in d_jd.items() if "specialization" in key.lower()
        ]
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id.id
            )
        if d_jd["job_role"] == "6" or d_jd["job_role"] == 6:
            try:
                skills = d_jd.getlist("mand_skill")
                skills = [i.strip().upper() for i in skills]
                skills = list(dict.fromkeys(skills))
                JD_skills_experience.objects.filter(jd_id_id=jd_id).delete()
                for s in skills:
                    JD_skills_experience.objects.create(
                        skill=s, experience=0, jd_id=jd_id, category_id=5
                    )
            except:
                pass
        else:
            mand_skill_list = d_jd.getlist("mand_skill")[0].split("|")
            skill_exp_list = d_jd.getlist("mand_skill_exp")[0].split(",")

            if len(skill_exp_list) > 1:
                skill_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 == 0
                ]
                exp_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 != 0
                ]
            else:
                skill_l = [i for i in mand_skill_list]
                exp_l = [0] * len(skill_l)

            database_skill = d_jd.getlist("database_skill")[0].split(",")
            platform_skill = d_jd.getlist("platform_skill")[0].split(",")
            programming_skill = d_jd.getlist("programming_skill")[0].split(",")
            tool_skill = d_jd.getlist("tool_skill")[0].split(",")
            misc_skill = d_jd.getlist("misc_skill")[0].split(",")
            for s, e in zip(skill_l, exp_l):
                if s.lower() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=1
                    )
                if s.lower() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=2
                    )
                if s.lower() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=3
                    )
                if s.lower() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=4
                    )
                if s.lower() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id.id, category_id=5
                    )

        country_list = [
            value for key, value in d_jd.items() if "work_country" in key.lower()
        ]
        state_list = [
            value for key, value in d_jd.items() if "work_state" in key.lower()
        ]
        city_list = [value for key, value in d_jd.items() if "work_city" in key.lower()]
        for c, s, ci in zip(country_list, state_list, city_list):
            JD_locations.objects.create(
                country_id=int(c), state_id=int(s), city_id=int(ci), jd_id_id=jd_id.id
            )

        logger.info("Redirecting to preview from duplicated JD")
        return redirect("jobs:questionnaire", pk=jd_id.id)

    elif request.method == "POST" and "submit_editJD" in request.POST:
        import re

        editedimage_form = jd_form()
        jd_id = pk
        logger.info("Submitting edited JD: " + str(jd_id))
        edited_jd = request.POST
        # o_richtext_job_descriptionp = re.sub('\s\s+', ' ',jd.richtext_job_description)
        # e_richtext_job_descriptionp = re.sub('\s\s+', ' ',edited_jd['richtext_job_description'])
        try:
            if edited_jd["work_remote"] == "on":
                work_remote = True
        except:
            work_remote = False

        show_sal_to_candidate = (
            True if edited_jd.get("show_sal_to_candidate") == "on" else False
        )

        # if 'company_logo' in request.FILES:
        # 	company_logo = request.FILES['company_logo']
        # 	# company_logo = company_logo
        # 	 # if ' ' not in company_logo else company_logo.replace(' ','_')
        # 	temp = JD_form(company_logo=company_logo)
        # 	temp.id = jd_id
        # 	temp.save(update_fields=["company_logo"])

        # else:
        # 	company_logo = edited_jd['logo_hidden']
        # if ' ' not in edited_jd['logo_hidden'] else edited_jd['logo_hidden'].replace(' ','_')

        qual_list = [
            value for key, value in edited_jd.items() if "qualification" in key.lower()
        ]
        spec_list = [
            value for key, value in edited_jd.items() if "specialization" in key.lower()
        ]
        JD_qualification.objects.filter(jd_id_id=jd_id).delete()
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id
            )
        if edited_jd["job_role"] == "6" or edited_jd["job_role"] == 6:

            skills = edited_jd.getlist("mand_skill_non_ds")
            skills = [i.strip().upper() for i in skills]
            skills = list(dict.fromkeys(skills))
            JD_skills_experience.objects.filter(jd_id_id=jd_id).delete()
            for s in skills:
                JD_skills_experience.objects.create(
                    skill=s, experience=0, jd_id_id=jd_id, category_id=5
                )
        else:
            mand_skill_list = edited_jd.getlist("mand_skill")[0].split("|")
            skill_exp_list = edited_jd.getlist("mand_skill_exp")[0].split(",")

            if len(skill_exp_list) > 1:
                skill_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 == 0
                ]
                exp_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 != 0
                ]
            else:
                skill_l = [i for i in mand_skill_list]
                exp_l = [0] * len(skill_l)
            JD_skills_experience.objects.filter(jd_id_id=jd_id).delete()
            database_skill = edited_jd.getlist("database_skill")[0].split(",")
            platform_skill = edited_jd.getlist("platform_skill")[0].split(",")
            programming_skill = edited_jd.getlist("programming_skill")[0].split(",")
            tool_skill = edited_jd.getlist("tool_skill")[0].split(",")
            misc_skill = edited_jd.getlist("misc_skill")[0].split(",")
            for s, e in zip(skill_l, exp_l):
                if s.lower() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=1
                    )
                if s.lower() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=2
                    )
                if s.lower() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=3
                    )
                if s.lower() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=4
                    )
                if s.lower() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=5
                    )

        country_list = [
            value for key, value in edited_jd.items() if "work_country" in key.lower()
        ]
        state_list = [
            value for key, value in edited_jd.items() if "work_state" in key.lower()
        ]
        city_list = [
            value for key, value in edited_jd.items() if "work_city" in key.lower()
        ]
        JD_locations.objects.filter(jd_id=jd_id).delete()
        for c, s, ci in zip(country_list, state_list, city_list):
            JD_locations.objects.create(
                country_id=int(c), state_id=int(s), city_id=int(ci), jd_id_id=jd_id
            )

        jd = JD_form.objects.filter(id=jd_id).last()
        text_des = re.sub(r"<.*?>", "", edited_jd["richtext_job_description"])
        text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
        text_des = re.sub(r"Requirements:", "", text_des)
        # text_des = re.sub(r'Non Technical Responsibilities:', '', text_des)
        job_description = text_des
        if (
            JD_profile.objects.filter(jd_id_id=jd_id).exists() == False
            or int(edited_jd["job_role"]) != int(jd.job_role.id)
        ) or (
            edited_jd["richtext_job_description"].strip()
            != jd.richtext_job_description.strip()
        ):

            logger.info("Changes made in profiling relevant fields")
            job_role_obj = tmeta_ds_main_roles.objects.get(id=edited_jd["job_role"])
            JD_form.objects.filter(id=jd_id).update(
                job_role=job_role_obj,
                richtext_job_description=edited_jd["richtext_job_description"],
            )

            profiler_input = [job_description]

            if profiler_input != []:
                url = settings.profile_api_url
                headers = {"Authorization": settings.profile_api_auth_token}
                input_texts = profiler_input
                texts_file = {"texts": "||".join(input_texts)}
                result = requests.post(url, headers=headers, data=texts_file)
                logger.debug("Profiling API response: " + str(result))
                try:
                    profiles = result.json()["profiles"]
                    profiles["bi_vis"] = profiles.pop("Business_Intelligence")
                    profiles["data_analysis"] = profiles.pop("Data_Analysis")
                    profiles["data_eng"] = profiles.pop("Data_Engineering")
                    profiles["devops"] = profiles.pop("Dev_Ops")
                    profiles["ml_model"] = profiles.pop("Machine_Learning")
                    sorted_profiles = sorted(
                        profiles.items(), key=lambda kv: (kv[1], kv[0]), reverse=True
                    )
                    recommended_roles = result.json()["recommended_roles"]
                except:
                    profiles = {}
                    profiles["bi_vis"] = 0
                    profiles["data_analysis"] = 0
                    profiles["data_eng"] = 0
                    profiles["devops"] = 0
                    profiles["ml_model"] = 0
                    profiles["others"] = 100
                    sorted_profiles = sorted(
                        profiles.items(), key=lambda kv: (kv[1], kv[0]), reverse=True
                    )
                    recommended_roles = ["others"]
                ds_profile = ""
                if recommended_roles != []:
                    ds_profile = "DS Profile"
                else:
                    ds_profile = "Others"
                    recommended_roles.append(ds_profile)

                classification_url = settings.classification_url
                cl_result = requests.post(
                    classification_url,
                    headers=headers,
                    data={"profiles": profiles.values()},
                )
                role_obj = tmeta_ds_main_roles.objects.get(
                    tag_name=recommended_roles[0].replace("_", " ")
                )
                if JD_profile.objects.filter(jd_id=jd).exists():
                    logger.info(
                        "Updating existing record in jd_profile table for JD: "
                        + str(jd)
                    )
                    JD_profile.objects.filter(jd_id=jd).update(
                        business_intelligence=profiles["bi_vis"],
                        data_analysis=profiles["data_analysis"],
                        data_engineering=profiles["data_eng"],
                        devops=profiles["devops"],
                        machine_learning=profiles["ml_model"],
                        others=profiles["others"],
                        recommended_role=role_obj,
                        dst_or_not=cl_result.json()["dst_or_not"],
                    )
                else:
                    logger.info(
                        "creating new record in jd_profile table for JD: " + str(jd)
                    )
                    JD_profile.objects.create(
                        jd_id_id=jd.id,
                        business_intelligence=profiles["bi_vis"],
                        data_analysis=profiles["data_analysis"],
                        data_engineering=profiles["data_eng"],
                        devops=profiles["devops"],
                        machine_learning=profiles["ml_model"],
                        others=profiles["others"],
                        user_id=user_id,
                        recommended_role=role_obj,
                        dst_or_not=cl_result.json()["dst_or_not"],
                    )
                if edited_jd["max_exp"] == "":
                    max_exp = None
                else:
                    max_exp = edited_jd["max_exp"]
                JD_form.objects.filter(id=jd_id).update(
                    job_title=edited_jd["job_title"],
                    job_id=edited_jd["job_id"],
                    no_of_vacancies=edited_jd["no_of_vacancies"],
                    # company_name = edited_jd['company_name'],
                    # company_website = edited_jd['company_website'],
                    industry_type_id=edited_jd["industry_type"],
                    # tech_req = edited_jd['tech_req'],
                    job_role=edited_jd["job_role"],
                    # org_info = edited_jd['org_info'],
                    min_exp=edited_jd["min_exp"],
                    max_exp=max_exp,
                    work_remote=work_remote,
                    job_description=job_description,
                    richtext_job_description=edited_jd["richtext_job_description"],
                    # non_tech_req = edited_jd['non_tech_req'],
                    # add_info = edited_jd['add_info'],
                    salary_curr_type_id=edited_jd["salary_curr_type"],
                    salary_min=edited_jd["salary_min"],
                    salary_max=edited_jd["salary_max"],
                    show_sal_to_candidate=show_sal_to_candidate,
                    job_type=edited_jd["job_type"],
                    updated_by=updated_by,
                    # company_logo = company_logo,
                )
            # return redirect('jobs:profile')
            return HttpResponseNotModified()

        else:
            if edited_jd["max_exp"] == "":
                max_exp = None
            else:
                max_exp = edited_jd["max_exp"]
            JD_form.objects.filter(id=jd_id).update(
                job_title=edited_jd["job_title"],
                job_id=edited_jd["job_id"],
                updated_by=updated_by,
                no_of_vacancies=edited_jd["no_of_vacancies"],
                # company_name = edited_jd['company_name'],
                # company_website = edited_jd['company_website'],
                industry_type_id=edited_jd["industry_type"],
                # tech_req = edited_jd['tech_req'],
                job_role=edited_jd["job_role"],
                # org_info = edited_jd['org_info'],
                min_exp=edited_jd["min_exp"],
                max_exp=max_exp,
                work_remote=work_remote,
                job_description=job_description,
                richtext_job_description=edited_jd["richtext_job_description"],
                # non_tech_req = edited_jd['non_tech_req'],
                # add_info = edited_jd['add_info'],
                salary_curr_type_id=edited_jd["salary_curr_type"],
                salary_min=edited_jd["salary_min"],
                salary_max=edited_jd["salary_max"],
                show_sal_to_candidate=show_sal_to_candidate,
                job_type=edited_jd["job_type"],
                # company_logo = company_logo,
            )
            return redirect("jobs:questionnaire", pk=pk)
    elif (
        request.method == "POST"
        and "0" in request.POST
        and "1" not in request.POST
        or "non_ds" in request.POST
    ):

        import re

        jd_id = pk
        logger.info("Saving...... edited JD: " + str(jd_id))
        edited_jd = request.POST

        # o_richtext_job_descriptionp = re.sub('\s\s+', ' ',jd.richtext_job_description)
        # try:
        # 	e_richtext_job_descriptionp = re.sub('\s\s+', ' ',edited_jd['richtext_job_description'])
        # except:
        # 	e_richtext_job_descriptionp = 'NULL'

        try:
            if edited_jd["work_remote"] == "on":
                work_remote = True
        except:
            work_remote = False

        # company_logo = edited_jd['logo_hidden']

        # if ' ' not in company_logo else company_logo.replace(' ','_')

        qual_list = [
            value for key, value in edited_jd.items() if "qualification" in key.lower()
        ]
        spec_list = [
            value for key, value in edited_jd.items() if "specialization" in key.lower()
        ]
        JD_qualification.objects.filter(jd_id_id=jd_id).delete()
        for q, s in zip(qual_list, spec_list):
            q = q if q != "" else "NULL"
            s = s if s != "" else "NULL"
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id
            )

        if edited_jd["job_role"] == "6" or edited_jd["job_role"] == 6:

            skills = edited_jd.getlist("mand_skill_non_ds")
            skills = [i.strip().upper() for i in skills]
            skills = list(dict.fromkeys(skills))
            JD_skills_experience.objects.filter(jd_id_id=jd_id).delete()
            for s in skills:
                JD_skills_experience.objects.create(
                    skill=s, experience=0, jd_id_id=jd_id, category_id=5
                )
        else:
            mand_skill_list = (
                edited_jd.getlist("mand_skill")[0].split("|")
                if (
                    len(edited_jd.getlist("mand_skill")) == 1
                    and edited_jd.getlist("mand_skill")[0] != ""
                )
                else ["NULL"]
            )
            skill_exp_list = (
                edited_jd.getlist("mand_skill_exp")[0].split(",")
                if len(edited_jd.getlist("mand_skill_exp")) == 1
                else ["0"]
            )

            if len(skill_exp_list) > 1:
                skill_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 == 0
                ]
                exp_l = [
                    skill_exp_list[i] for i in range(len(skill_exp_list)) if i % 2 != 0
                ]
            else:
                skill_l = [i for i in mand_skill_list]
                exp_l = [0] * len(skill_l)
            JD_skills_experience.objects.filter(jd_id_id=jd_id).delete()
            database_skill = edited_jd.getlist("database_skill")[0].split(",")
            platform_skill = edited_jd.getlist("platform_skill")[0].split(",")
            programming_skill = edited_jd.getlist("programming_skill")[0].split(",")
            tool_skill = edited_jd.getlist("tool_skill")[0].split(",")
            misc_skill = edited_jd.getlist("misc_skill")[0].split(",")
            for s, e in zip(skill_l, exp_l):
                if s.lower() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=1
                    )
                if s.lower() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=2
                    )
                if s.lower() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=3
                    )
                if s.lower() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=4
                    )
                if s.lower() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd_id, category_id=5
                    )

        country_list = [
            value for key, value in edited_jd.items() if "work_country" in key.lower()
        ]
        state_list = [
            value for key, value in edited_jd.items() if "work_state" in key.lower()
        ]
        city_list = [
            value for key, value in edited_jd.items() if "work_city" in key.lower()
        ]

        JD_locations.objects.filter(jd_id_id=jd_id).delete()
        for c, s, ci in zip(country_list, state_list, city_list):
            JD_locations.objects.create(
                country_id=int(c), state_id=int(s), city_id=int(ci), jd_id_id=jd_id
            )

        jd = JD_form.objects.filter(id=jd_id).last()

        jd.job_title = (
            edited_jd["job_title"] if len(edited_jd["job_title"]) != 0 else "NULL"
        )
        jd.job_role = (
            tmeta_ds_main_roles.objects.get(id=edited_jd["job_role"])
            if len(edited_jd["job_role"]) != 0
            else "NULL"
        )
        jd.job_id = edited_jd["job_id"] if len(edited_jd["job_id"]) != 0 else "NULL"
        # jd.company_name = edited_jd['company_name'] if len(edited_jd['company_name'])!=0 else 'NULL'
        # jd.company_website = edited_jd['company_website'] if len(edited_jd['company_website'])!=0 else 'NULL'
        jd.industry_type_id = edited_jd["industry_type"]
        # jd.org_info = edited_jd['org_info']
        jd.min_exp = edited_jd["min_exp"] if len(edited_jd["min_exp"]) != 0 else None
        jd.max_exp = edited_jd["max_exp"] if len(edited_jd["max_exp"]) != 0 else None
        jd.work_remote = work_remote
        jd.richtext_job_description = (
            edited_jd["richtext_job_description"]
            if len(edited_jd["richtext_job_description"]) != 0
            else "NULL"
        )
        text_des = re.sub(r"<.*?>", "", edited_jd["richtext_job_description"])
        text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
        text_des = re.sub(r"Requirements", "", text_des)
        # text_des = re.sub(r'Non Technical Responsibilities:', '', text_des)
        jd.job_description = text_des
        jd.no_of_vacancies = (
            edited_jd["no_of_vacancies"]
            if len(edited_jd["no_of_vacancies"]) != 0
            else 0
        )
        # jd.tech_req = edited_jd['tech_req'] if len(edited_jd['tech_req'])!=0 else 'NULL'
        # jd.company_logo = company_logo
        # jd.company_logo = company_logo
        # if ' ' not in company_logo else company_logo.replace(' ','_')
        jd.salary_curr_type_id = int(edited_jd["salary_curr_type"])
        jd.show_sal_to_candidate = (
            True if edited_jd.get("show_sal_to_candidate") == "on" else False
        )
        # jd.non_tech_req = edited_jd['non_tech_req'] if len(edited_jd['non_tech_req'])!=0 else 'NULL'
        # jd.add_info = edited_jd['add_info']
        jd.salary_min = (
            edited_jd["salary_min"] if len(edited_jd["salary_min"]) != 0 else 0
        )
        jd.salary_max = (
            edited_jd["salary_max"] if len(edited_jd["salary_max"]) != 0 else 0
        )
        jd.job_type_id = int(edited_jd["job_type"])
        jd.jd_status_id = int(2)
        jd.updated_by = updated_by
        jd.save()
        logger.info("saved edited JD successfully!!")
        try:
            if request.POST["non_ds"] == "non_ds_submit":
                return redirect("jobs:questionnaire", pk=jd_id)
        except:
            pass
        return redirect("jobs:jobs_main")

    elif request.method == "POST" and "1" in request.POST:
        d_jd = request.POST
        logger.info("Saving....duplicated JD")
        # user_id = User.objects.get(username = request.user)
        # try:
        # 	permission = user_type.objects.get(user_id=request.user).admin_id
        # except:
        # 	permission=0
        # if permission != 0:
        # 	user_id = permission
        # if 'company_logo' in request.FILES:
        # 	company_logo = request.FILES['company_logo']
        # 	# company_logo = company_logo if ' ' not in company_logo else company_logo.replace(' ','_')
        # else:
        # 	company_logo = d_jd['logo_hidden']
        # if ' ' not in d_jd['logo_hidden'] else d_jd['logo_hidden'].replace(' ','_')

        Save_JD(request, d_jd, user_id, updated_by)

        return redirect("jobs:jobs_main")
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")
    context = {
        "form_jd": form_jd,
        "jd_id": pk,
        "profile": profile,
        "data_for_profile": json.dumps(
            [
                jd.job_role.tag_name,
                jd.job_description,
            ],
            cls=DjangoJSONEncoder,
        ),
        "data": json.dumps(data, cls=DjangoJSONEncoder),
        # 'bi_data':json.dumps(data_t['4'], cls=DjangoJSONEncoder),
        # 'da_data':json.dumps(data_t['1'], cls=DjangoJSONEncoder),
        # 'de_data':json.dumps(data_t['3'], cls=DjangoJSONEncoder),
        # 'do_data':json.dumps(data_t['5'], cls=DjangoJSONEncoder),
        # 'ml_data':json.dumps(data_t['2'], cls=DjangoJSONEncoder),
        "tool_skills": json.dumps(tool, cls=DjangoJSONEncoder),
        "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        "mand_skills": json.dumps(mand_skills, cls=DjangoJSONEncoder),
        "non_ds_skill": json.dumps(non_ds_skill, cls=DjangoJSONEncoder),
        "database_skills": json.dumps(database, cls=DjangoJSONEncoder),
        "platform_skills": json.dumps(platform, cls=DjangoJSONEncoder),
        "misc_skills": json.dumps(misc, cls=DjangoJSONEncoder),
        "programming_skills": json.dumps(programming, cls=DjangoJSONEncoder),
        "mand_skill_exp": json.dumps(mand_skill_exp, cls=DjangoJSONEncoder),
        "work_country": json.dumps(work_country1, cls=DjangoJSONEncoder),
        "work_state": json.dumps(work_state1, cls=DjangoJSONEncoder),
        "work_city": json.dumps(work_city1, cls=DjangoJSONEncoder),
        "qual_spec": json.dumps(spec1, cls=DjangoJSONEncoder),
        "qual_name": json.dumps(qual1, cls=DjangoJSONEncoder),
        "state": json.dumps(state, cls=DjangoJSONEncoder),
        "city": json.dumps(city, cls=DjangoJSONEncoder),
        # 'company_logo': company_logo_path,
        "selected_role": json.dumps(jd.job_role.id, cls=DjangoJSONEncoder),
        "country_list": json.dumps(country_list, cls=DjangoJSONEncoder),
        "state_list": json.dumps(state_list, cls=DjangoJSONEncoder),
        "country": country,
        "duplicate": duplicate,
        "permission": permission,
        "is_ds_role": is_ds_role,
        "profile_confirmation": profile_confirmation,
        "work_remote": jd.work_remote,
        "show_sal_to_candidate": jd.show_sal_to_candidate,
        "show_sal_to_cand": json.dumps(jd.show_sal_to_candidate, cls=DjangoJSONEncoder),
        "skill_e": json.dumps(skill_n_exp, cls=DjangoJSONEncoder),
        "request_from_jd_view": from_duplicate,
    }
    return render(request, "jobs/edit_jd.html", context)


@login_required
@recruiter_required
def select_ds_or_non_ds(request):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    has_permission = user_permission(request, "create_post")
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    if not has_permission == True:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})
    user, updated_by = admin_account(request)
    feature = client_features_balance.objects.get(
        client_id=user, feature_id_id=10
    ).available_count
    if not company_details.objects.filter(recruiter_id=user).exists():
        return redirect("jobs:company_detail")
    if not career_page_setting.objects.filter(recruiter_id=user).exists():
        return redirect("jobs:setting_page")

    setting = career_page_setting.objects.get(recruiter_id=user)
    return render(
        request,
        "jobs/select_ds_or_non_ds.html",
        {"feature": feature, "permission": permission},
    )


def url_varification(request):
    url = request.GET["url"]
    data = {}
    data["success"] = 0
    if career_page_setting.objects.filter(career_page_url=url).exists():
        data["success"] = 1
    return JsonResponse(data)


def career_page(request, url=None):
    try:
        user = career_page_setting.objects.get(career_page_url=url).recruiter_id
    except:
        user, updated_by = admin_account(request)
    jd_form = JD_form.objects.filter(user_id=user, jd_status_id=1)
    jd_form = jd_form.annotate(
        country=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                "country__name"
            )
        ),
        state=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values("state__name")
        ),
        city=Subquery(
            JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values("city__name")
        ),
    ).order_by("-job_posted_on")
    jd_form = jd_form.annotate(
        job_location=Concat(
            "city",
            V(", "),
            "state",
            V(", "),
            "country",
            V("."),
            output_field=CharField(),
        )
    )
    filters = Career_filter(request.GET, queryset=jd_form)
    jd_form = filters.qs
    try:
        company_detail = company_details.objects.get(recruiter_id=user)
    except:
        company_detail = None
    try:

        setting = career_page_setting.objects.get(recruiter_id=user)
    except:
        setting = None
    page = request.GET.get("page", 1)
    paginator = Paginator(jd_form, 10)

    try:
        jd_form = paginator.page(page)
    except PageNotAnInteger:
        jd_form = paginator.page(1)

    except EmptyPage:
        jd_form = paginator.page(paginator.num_pages)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
    context = {
        "jd_form": jd_form,
        "params": params,
        "filters": filters,
        "setting": setting,
        "company_detail": company_detail,
    }
    return render(request, "jobs/career_page.html", context)


def career_job_view(request, pk=None, url=None):
    # try:

    jd_form = JD_form.objects.get(id=pk)
    logo = company_details.objects.get(recruiter_id=jd_form.user_id).logo
    company = company_details.objects.get(recruiter_id=jd_form.user_id).company_name
    career_page_url = career_page_setting.objects.get(
        recruiter_id=jd_form.user_id
    ).career_page_url
    context = {
        "jd_form": jd_form,
        "logo": logo,
        "career_page_url": career_page_url,
        "company": company,
    }
    response = render(request, "jobs/job_view.html", context)
    return response
    # except:
    # 	jd_form = JD_form.objects.get(id=pk).user_id
    # 	url=career_page_setting.objects.get(recruiter_id=jd_form).career_page_url
    # 	# return redirect('jobs:career_page', url=url)
    # 	return HttpResponseRedirect('/'+url+"/career#%s" % 'not_aval')


def job_view_count_fun(request, pk=None):
    try:
        viewed_site = request.COOKIES["__atssc"].split("%")
    except:
        viewed_site = ""

    try:
        source = request.COOKIES["source"]
    except:
        source = 1
    # try:

    if source == 1:
        if "whatsapp" in viewed_site:
            source = "Whatsapp"
        elif "facebook" in viewed_site:
            source = "Facebook"
        elif "linkedin" in viewed_site:
            source = "Linkedin"
        elif "twitter" in viewed_site:
            source = "Twitter"
        elif "gmail" in viewed_site:
            source = "Gmail"
        elif "whatjobs" in viewed_site:
            source = "whatjobs"
        elif source != 1:
            source = source
        else:
            source = "Career Page"
        if "rl_token" in request.GET:
            source = "Resume Library"
            return JsonResponse({"data": source})

        if job_view_count.objects.filter(
            jd_id_id=pk, source=source, created_at=timezone.now().date()
        ).exists():
            job_view = job_view_count.objects.get(
                jd_id_id=pk, source=source, created_at=timezone.now().date()
            )
            job_view.count = job_view.count + 1
            job_view.save()
        else:
            job_view_count.objects.create(
                jd_id_id=pk, count=1, source=source, created_at=timezone.now().date()
            )

    return JsonResponse({"data": source})


def applicant_inflow(request, pk=None):
    if "rl_token" in request.GET:
        url = "https://api.resume-library.com/v1/apply/" + request.GET["rl_token"]
        result = requests.get(url, auth=(settings.rl_username, settings.rl_password))
        result = json.loads(result.content)
        if job_view_count.objects.filter(
            jd_id_id=pk, source="Resume Library", created_at=timezone.now().date()
        ).exists():
            job_view = job_view_count.objects.get(
                jd_id_id=pk, source="Resume Library", created_at=timezone.now().date()
            )
            job_view.count = job_view.count + 1
            job_view.save()
        else:
            job_view_count.objects.create(
                jd_id_id=pk,
                count=1,
                source="Resume Library",
            )
        emp_id = request.COOKIES["emp-id"]
        username = generate_random_username()
        password = generate_random_username(split=8)
        if User_Info.objects.filter(email=result["email"], employer_id=emp_id).exists():
            user = User_Info.objects.get(
                email=result["email"], employer_id=emp_id
            ).user_id
            username = user.username
            password = User_Info.objects.get(
                email=result["email"], employer_id=emp_id
            ).password
            user = authenticate(username=username, password=password)
        else:
            user = User.objects.create(
                username=username,
                date_joined=datetime.now(),
                first_name=result["first_name"],
                last_name=result["last_name"],
            )
            user.set_password(password)
            user.save()
            user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        try:
            data = result["result"]["pages"][0]["content"]
            byte = b64decode(data, validate=True)
            if byte[0:4] != b"%PDF":
                file = open(base_dir + "/media/resume/" + result["id"] + ".docx", "wb")
                file.write(byte)
                file.close()
                data = Myfiles.objects.create(
                    upload_id=user, resume_file="resume/" + result["id"] + ".docx"
                )
                sentences_list = parsing_rl(result["id"] + ".docx")
            else:
                file = open(base_dir + "/media/resume/" + result["id"] + ".doc", "wb")
                file.write(byte)
                file.close()
                data = Myfiles.objects.create(
                    upload_id=user, resume_file="resume/" + result["id"] + ".pdf"
                )
                sentences_list = parsing_rl(result["id"] + ".pdf")
            if not User_Info.objects.filter(
                email=result["email"], employer_id=emp_id
            ).exists():
                User_Info.objects.create(
                    user_id=request.user,
                    username=request.user.username,
                    password=password,
                    first_name=result["first_name"],
                    last_name=result["last_name"],
                    email=result["email"],
                )
                personal = Personal_Info.objects.create(
                    user_id=request.user,
                    firstname=result["first_name"],
                    lastname=result["last_name"],
                    email=result["email"],
                )
                Additional_Details.objects.create(
                    application_id=personal,
                    total_exp_year=0,
                    total_exp_month=0,
                )
        except:
            return JsonResponse({"data": 0, "source": "Resume Library"})
        return JsonResponse({"data": 1, "source": "Resume Library"})


@login_required
@recruiter_required
def questionnaire(request, pk):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    if "delete" in request.GET:
        applicant_questionnaire.objects.filter(id=int(request.GET["delete"])).delete()
        return HttpResponse("1")
    if "temp" in request.GET:
        temp_list = request.GET.getlist("temp")
        for i in temp_list:
            row_id = i.split("***")[0]
            row_req = i.split("***")[1]
            is_required = False
            if row_req == "true":
                is_required = True
            template = applicant_questionnaire_template.objects.get(id=int(row_id))
            applicant_questionnaire.objects.create(
                jd_id_id=pk,
                field_type_id=template.field_type_id,
                question=template.question,
                description=template.description,
                is_required=is_required,
                option1=template.option1,
                option2=template.option2,
                option3=template.option3,
                option4=template.option4,
            )
        return HttpResponse("1")
    if request.method == "POST":
        if "required" in request.POST:
            is_required = True
        else:
            is_required = False
        if (
            request.POST["field-type"] == "5"
            or request.POST["field-type"] == "6"
            or request.POST["field-type"] == "7"
        ):
            update_questionnaire = applicant_questionnaire.objects.create(
                jd_id_id=pk,
                field_type_id=int(request.POST["field-type"]),
                question=request.POST["question"],
                description=request.POST["description"],
                is_required=is_required,
            )
            option = request.POST.getlist("option")
            for i in range(len(option)):
                if i == 0:
                    update_questionnaire.option1 = option[i]
                elif i == 1:
                    update_questionnaire.option2 = option[i]
                elif i == 2:
                    update_questionnaire.option3 = option[i]
                elif i == 3:
                    update_questionnaire.option4 = option[i]
            update_questionnaire.save()

        else:
            applicant_questionnaire.objects.create(
                jd_id_id=pk,
                field_type_id=int(request.POST["field-type"]),
                question=request.POST["question"],
                description=request.POST["description"],
                is_required=is_required,
            )
        return redirect("jobs:questionnaire", pk=pk)

    applicant_qus = applicant_questionnaire.objects.filter(jd_id_id=pk)
    JD_form.objects.filter(id=pk).update(jd_status_id=5)
    applicant_qus_list = applicant_questionnaire.objects.filter(
        jd_id_id=pk
    ).values_list("question", flat=True)
    applicant_qus_template = applicant_questionnaire_template.objects.all()
    is_ds_role = 0
    if not JD_form.objects.filter(id=pk, job_role_id=6).exists():
        is_ds_role = 1
    context = {
        "pk": pk,
        "is_ds_role": is_ds_role,
        "applicant_qus": applicant_qus,
        "permission": permission,
        "applicant_qus_list": applicant_qus_list,
        "applicant_qus_template": applicant_qus_template,
    }
    return render(request, "jobs/questionnaire.html", context)


def applicant_qus(request, pk):
    # pk= request.GET['pk']
    applicant_qus = applicant_questionnaire.objects.filter(jd_id_id=pk)
    return render(
        request,
        "jobs/applicant_qus.html",
        {
            "applicant_qus": applicant_qus,
        },
    )


# JD-view page when clicks on job-title of jobpostings page
@login_required
@recruiter_required
def jd_view(request, pk):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    has_permission = user_permission(request, "zita_match_candidate")
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    if not has_permission == True:
        return render(request, "jobs/no_permission.html", {"permission": permission})
    if "non_ds" in request.GET:
        is_ds_role = 0
    else:
        is_ds_role = 1
    from_analytics = request.GET.get("a")
    # logger.info("Is the request for JD Analytics page?? "+str(from_analytics))
    username = request.user
    current_site = get_current_site(request)
    user_id, updated_by = admin_account(request)
    # try:
    # 	permission = user_type.objects.get(user_id=request.user).admin_id
    # except:
    # 	permission=0
    # if permission != 0:
    # 	user_id = permission
    user = User.objects.get(username=request.user)
    if pk:
        jd = JD_form.objects.filter(id=pk).last()
    else:
        jd = JD_form.objects.filter(user_id=user_id).last()
    jd_state = JD_locations.objects.filter(jd_id_id=jd.id).values_list(
        "state_id", flat=True
    )
    job_type = tmeta_job_type.objects.filter(id=jd.job_type.id).values("value")[0][
        "value"
    ]
    location = [
        (
            Country.objects.filter(id=i["country"]).values("name")[0]["name"],
            State.objects.filter(id=i["state"]).values("name")[0]["name"],
            City.objects.filter(id=i["city"]).values("name")[0]["name"],
        )
        for i in JD_locations.objects.filter(jd_id_id=jd.id).values(
            "country", "state", "city"
        )
    ]
    sal_curr_type = (
        tmeta_currency_type.objects.filter(id=jd.salary_curr_type_id)
        .values("value")[0]["value"]
        .split(" ")[0]
    )
    job_role = tmeta_ds_main_roles.objects.get(id=jd.job_role.id).label_name
    location = JD_locations.objects.get(jd_id_id=jd.id)
    education = [
        (i["qualification"], i["specialization"])
        for i in JD_qualification.objects.filter(jd_id_id=jd.id).values(
            "qualification", "specialization"
        )
    ]

    mand_skills = [
        i["skill"]
        for i in JD_skills_experience.objects.filter(jd_id_id=jd.id).values("skill")
    ]
    mand_skill_exp = [
        i["experience"]
        for i in JD_skills_experience.objects.filter(jd_id_id=jd.id).values(
            "experience"
        )
    ]

    for i in range(len(mand_skills)):
        mand_skills[i] = mand_skills[i] + "*#d0d0d0"
    try:

        original_jd_profile = JD_profile.objects.get(jd_id=jd.id).recommended_role
        o_recommended_role = tmeta_ds_main_roles.objects.get(
            id=original_jd_profile.id
        ).label_name
        jd_profile = JD_profile.objects.filter(jd_id=jd).values(
            "business_intelligence",
            "data_analysis",
            "data_engineering",
            "devops",
            "machine_learning",
            "others",
        )
        recom_role = JD_profile.objects.filter(jd_id=jd).values("recommended_role")
        role_acceptence = JD_profile.objects.filter(jd_id=jd).values("role_acceptence")
    except:
        jd_profile = ""
        recom_role = ""
        o_recommended_role = ""
        role_acceptence = "0"
    int_list = {
        "posted_at": "",
        "reposted_on": "",
        "jd_status": "",
        "active_for": "",
        "zita_match": 0,
        "applicants": 0,
        "views": 0,
        "interviewed": 0,
        "screened": 0,
        "offered": 0,
    }
    final_list = []
    int_list["posted_at"] = JD_form.objects.get(id=jd.id).job_posted_on.date()
    try:
        active_for = (
            timezone.now().date() - JD_form.objects.get(id=jd.id).job_posted_on.date()
        )
        int_list["active_for"] = active_for.days
    except:
        int_list["active_for"] = "NA"

    status_id = JD_form.objects.filter(id=jd.id).values("jd_status_id")[0][
        "jd_status_id"
    ]
    int_list["jd_status"] = tmeta_jd_status.objects.filter(id=status_id).values(
        "value"
    )[0]["value"]

    int_list["zita_match"] = (
        zita_match_candidates.objects.filter(jd_id_id=jd.id, status_id_id=5)
        .values("candidate_id")
        .distinct()
        .count()
    )

    int_list["applicants"] = applicants_status.objects.filter(
        jd_id_id=jd.id, status_id_id__in=[1, 2, 3, 4, 7]
    ).count()
    int_list["shortlisted"] = (
        applicants_status.objects.filter(jd_id_id=jd.id, status_id_id__in=[2])
        .distinct()
        .count()
    )
    int_list["onboard"] = (
        applicants_status.objects.filter(jd_id_id=jd.id, status_id_id=4)
        .distinct()
        .count()
    )
    int_list["invite"] = (
        Candi_invite_to_apply.objects.filter(jd_id_id=jd.id).distinct().count()
    )
    int_list["rejected"] = applicants_status.objects.filter(
        jd_id_id=jd.id, status_id_id=7
    ).count()
    job_count = (
        job_view_count.objects.filter(jd_id_id=jd.id)
        .values("source")
        .annotate(counts=Sum("count"))
        .aggregate(Sum("counts"))
    )

    int_list["views"] = job_count["counts__sum"]
    role_base1 = []
    role_base2 = []
    data_dict = ["Applicants", "Views"]
    data_dict_ids = [1, 6]
    dates = list(
        sorted(
            set(
                [
                    i["created_at"]
                    for i in job_view_count.objects.filter(jd_id_id=jd.id).values(
                        "created_at"
                    )
                ]
            )
        )
    )
    date_list1 = list(
        job_view_count.objects.filter(jd_id_id=jd.id)
        .annotate(label=YearWeek("created_at"))
        .values("label")
        .annotate(y=Sum("count"))
    )
    date_list2 = list(
        applicants_status.objects.filter(
            jd_id_id=jd.id, status_id_id__in=[1, 2, 3, 4, 7]
        )
        .annotate(label=YearWeek("created_on"))
        .values("label")
        .annotate(y=Count("id"))
    )
    posted_date = JD_form.objects.get(id=jd.id).job_posted_on
    posted_date = posted_date.strftime("%b-%d")
    date_list1.insert(0, {"label": posted_date, "y": 0})
    date_list2.insert(0, {"label": posted_date, "y": 0})
    role_base = [date_list1, date_list2]
    if request.method == "POST":
        if "repost_jd_id" in request.POST:
            pk_id = request.POST.get("repost_jd_id")
            JD_form.objects.filter(id=pk_id).update(job_reposted_on=datetime.now())
            JD_form.objects.filter(id=pk_id).update(jd_status_id=int(1))
            logger.info("Reposted JD successfully!!")
            # jd_form_to_jd_list(pk=pk_id, string=2)
            count = jd_candidate_analytics.objects.filter(
                jd_id_id=jd.id, status_id_id=5
            ).count()
            mail_notification(
                user,
                "jd_repost.html",
                "Congrats from Zita.ai. Your Job is here. Check now.",
                jd_id=jd.id,
                count=count,
                domain=current_site,
            )
            return redirect("jobs:jobs_main")
        if "inactive_jd_id" in request.POST:
            pk_id = request.POST.get("inactive_jd_id")
            JD_form.objects.filter(id=pk_id).update(jd_status_id=int(4))
            logger.info("In-activated JD successfully!!")
            jd_count = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=10
            )
            if jd_count.available_count != None:
                jd_count.available_count = jd_count.available_count + 1
                jd_count.save()
            recuriter_job_posting_plan.objects.filter(jd_id_id=pk_id).update(
                is_active=False
            )
            mail_notification(
                user,
                "jd_inactive.html",
                "Job Inactivated Successfully.",
                jd_id=jd.id,
                domain=current_site,
            )
            results = remove_case_id(request, can_id=None, jd_id=pk_id)
            return redirect("jobs:jobs_main")

    # try:
    ext_jobs = external_jobpostings_by_client.objects.filter(
        jd_id_id=pk, is_active=True
    )
    try:
        career_page_url = career_page_setting.objects.get(
            recruiter_id=user_id
        ).career_page_url
    except:
        career_page_url = None
    return render(
        request,
        "jobs/jd_view.html",
        {
            "object1": json.dumps(list(role_base), cls=DjangoJSONEncoder),
            "dates_length": dates,
            "jd": jd,
            "job_type": job_type,
            "location": location,
            "education": education,
            "ext_jobs": ext_jobs,
            "sal_curr_type": sal_curr_type,
            "job_role1": o_recommended_role,
            "profile_object": json.dumps(list(jd_profile), cls=DjangoJSONEncoder),
            "recom_role": json.dumps(list(recom_role), cls=DjangoJSONEncoder),
            "mand_skills": json.dumps(mand_skills, cls=DjangoJSONEncoder),
            "mand_skill_exp": json.dumps(mand_skill_exp, cls=DjangoJSONEncoder),
            "o_recommended_role": o_recommended_role,
            "is_ds_role": is_ds_role,
            "permission": permission,
            "career_page_url": career_page_url,
            "int_list": int_list,
            "richtext_job_description": json.dumps(
                jd.richtext_job_description, cls=DjangoJSONEncoder
            ),
            "posted_date": json.dumps(posted_date, cls=DjangoJSONEncoder),
            # 'tech_req': json.dumps(jd.tech_req, cls=DjangoJSONEncoder),
            # 'non_tech_req': json.dumps(jd.non_tech_req, cls=DjangoJSONEncoder),
            # 'add_info': json.dumps(jd.add_info, cls=DjangoJSONEncoder),
            # 'org_info': json.dumps(jd.org_info, cls=DjangoJSONEncoder),
            "work_remote": json.dumps(jd.work_remote, cls=DjangoJSONEncoder),
            "job_role": json.dumps(jd.job_role.id, cls=DjangoJSONEncoder),
            "role_acceptence": json.dumps(list(role_acceptence), cls=DjangoJSONEncoder),
            "from_analytics": json.dumps(from_analytics, cls=DjangoJSONEncoder),
        },
    )


@login_required
@recruiter_required
def applicant_profile(request, jd_id=None, can_id=None):
    user_id, updated_by = admin_account(request)
    if "shortlist" in request.GET:
        applicants_status.objects.filter(
            jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=1
        ).update(status_id_id=2)
        applicants_screening_status.objects.get_or_create(
            jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=2
        )
        time = timezone.now().strftime("%b %d,  %Y")
        return JsonResponse({"data": time})

    if "comments" in request.GET:
        if "rating" in request.GET:
            rating = request.GET["rating"]
        else:
            rating = 0
        if interview_scorecard.objects.filter(
            jd_id_id=jd_id,
            candidate_id_id=can_id,
        ).exists():
            interview_scorecard.objects.filter(
                jd_id_id=jd_id,
                candidate_id_id=can_id,
            ).update(rating=rating, comments=request.GET["comments"])
        else:
            interview_scorecard.objects.create(
                jd_id_id=jd_id,
                candidate_id_id=can_id,
                rating=rating,
                comments=request.GET["comments"],
            )
    current_site = get_current_site(request)
    if request.method == "POST":
        notes = Candidate_notes.objects.get(
            client_id=user_id, candidate_id_id=can_id
        ).notes
        notes = request.POST["notes"]
        Candidate_notes.objects.filter(
            client_id=user_id, candidate_id_id=can_id
        ).update(notes=notes)
        return JsonResponse({"data": 1})
    if Candidate_notes.objects.filter(
        client_id=user_id, candidate_id_id=can_id
    ).exists():
        notes = Candidate_notes.objects.get(client_id=user_id, candidate_id_id=can_id)
    else:
        notes = Candidate_notes.objects.create(
            client_id=user_id, candidate_id_id=can_id, notes=""
        )
    form = Candidates_notes_form(instance=notes)
    candidate_details = employer_pool.objects.filter(id=can_id)
    if "message" in request.GET:
        Message.objects.filter(
            receiver=user_id,
            sender_id=candidate_details[0].candidate_id.user_id,
            jd_id_id=jd_id,
        ).update(is_read=True)
        return JsonResponse({"data": "1"})
    candidate_details = candidate_details.annotate(
        image=Subquery(
            Profile.objects.filter(user_id=OuterRef("candidate_id__user_id"))[
                :1
            ].values("image")
        ),
        file=Subquery(
            Myfiles.objects.filter(upload_id=OuterRef("candidate_id__user_id"))
            .order_by("-id")[:1]
            .values("resume_file")
        ),
    )
    try:
        scorecard = interview_scorecard.objects.get(
            jd_id_id=jd_id,
            candidate_id_id=can_id,
        )
        score = scorecard.rating
    except:
        score = 0
    try:
        text_des = interview_scorecard_form(instance=scorecard)
    except:
        text_des = interview_scorecard_form()
    total_exp = Additional_Details.objects.get(
        application_id=candidate_details[0].candidate_id
    )
    experience = Experiences.objects.filter(
        application_id=candidate_details[0].candidate_id
    )
    education = Education.objects.filter(
        application_id=candidate_details[0].candidate_id
    )
    project = Projects.objects.filter(
        application_id=candidate_details[0].candidate_id, work_proj_type=False
    )
    ac_project = Projects.objects.filter(
        application_id=candidate_details[0].candidate_id, work_proj_type=True
    )
    skills = Skills.objects.get(application_id=candidate_details[0].candidate_id)
    fresher = Fresher.objects.filter(application_id=candidate_details[0].candidate_id)
    course = Certification_Course.objects.filter(
        application_id=candidate_details[0].candidate_id
    )
    contrib = Contributions.objects.filter(
        application_id=candidate_details[0].candidate_id
    )
    applicants_status.objects.get_or_create(
        jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=6, client_id=user_id
    )
    try:
        google = google_return_details.objects.get(client_id=request.user)
    except:
        google = None
    try:
        outlook = outlook_return_details.objects.get(client_id=request.user)
    except:
        outlook = None
    if jd_id == None:
        chatname = (
            str(candidate_details[0].client_id.id)
            + "-"
            + str(candidate_details[0].candidate_id.user_id.id)
        )
        context = {
            "candidate_details": candidate_details[0],
            "jd_id": 0,
            "can_id": can_id,
            "total_exp": total_exp,
            "experience": experience,
            "course": course,
            "form": form,
            "user_id": user_id,
            "google": google,
            "outlook": outlook,
            "contrib": contrib,
            "score": score,
            "current_site": current_site,
            "skills": skills,
            "education": education,
            "project": project,
            "ac_project": ac_project,
            "fresher": fresher,
            "chatname": chatname,
        }
        return render(request, "jobs/applicant_profile.html", context)
    applied = applicants_screening_status.objects.filter(
        jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=1
    ).last()
    shortlisted = applicants_screening_status.objects.filter(
        jd_id_id=jd_id, candidate_id_id=can_id, status_id__in=[2]
    ).last()
    selected = applicants_screening_status.objects.filter(
        jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=4
    ).last()
    interviewed = applicants_screening_status.objects.filter(
        jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=3
    ).last()
    rejected = applicants_screening_status.objects.filter(
        jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=7
    ).last()
    invite = Candi_invite_to_apply.objects.filter(
        jd_id_id=jd_id, candidate_id_id=can_id
    ).last()

    event = Event.objects.filter(
        user=request.user, attendees__icontains=candidate_details[0].email
    )

    try:
        status_id = applicants_status.objects.get(
            jd_id_id=jd_id, candidate_id_id=can_id, status_id__in=[1, 2, 3, 4, 7]
        ).status_id
    except:
        status_id = 0
    try:
        source = (
            applicants_status.objects.filter(jd_id_id=jd_id, candidate_id_id=can_id)
            .exclude(status_id_id=6)
            .last()
            .source
        )
    except:
        source = "Career Page"
    jd = JD_form.objects.get(id=jd_id)
    questionnaire = applicant_questionnaire.objects.filter(jd_id_id=jd_id)
    cover_letter = applicant_cover_letter.objects.filter(
        candidate_id=candidate_details[0].candidate_id,
        jd_id_id=jd_id,
    ).last()
    questionnaire = questionnaire.annotate(
        answer=Subquery(
            applicant_answers.objects.filter(
                qus_id=OuterRef("id"), candidate_id=candidate_details[0].candidate_id
            )[:1].values("answer")
        ),
    )
    url = "http://192.168.3.251:8080/v5_8/GapService?WSDL"
    headers = {"content-type": "application/soap+xml"}
    try:
        match = Matched_candidates.objects.get(jd_id_id=jd_id, candidate_id_id=can_id)
    except:
        match = None
    body = (
        """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/gap">
        <soapenv:Header/><soapenv:Body><xmp:analyse><action><left><index><index><caseType>job</caseType>
        <indexId>"""
        + user_id.username
        + """</indexId></index><caseId>"""
        + str(jd_id)
        + """</caseId></index></left><right>
        <index><index><caseType>candidate</caseType><indexId>"""
        + user_id.username
        + """</indexId></index><caseId>"""
        + str(can_id)
        + """</caseId>
        </index></right></action></xmp:analyse></soapenv:Body>
    </soapenv:Envelope>
    """
    )
    try:
        response = requests.post(url, data=body, headers=headers)
        data_dict = xmltodict.parse(response.content.decode("iso-8859-1"))
        json_data = json.dumps(data_dict)
        with open(base_dir + "/media/data-1.json", "w") as json_file:
            json_file.write(json_data)
            json_file.close()
        f = open(
            base_dir + "/media/data-1.json",
        )
        data = json.load(f)
        data = data["soap:Envelope"]["soap:Body"]["ns2:analyseResponse"]["return"]
        match.profile_match = round(float(data["score"]) * 100)
        match.save()
    except:
        data = {}
    chatname = (
        str(candidate_details[0].client_id.id)
        + "-"
        + str(candidate_details[0].candidate_id.user_id.id)
    )
    context = {
        "candidate_details": candidate_details[0],
        "jd_id": jd_id,
        "can_id": can_id,
        "total_exp": total_exp,
        "experience": experience,
        "status_id": status_id,
        "jd": jd,
        "course": course,
        "cover_letter": cover_letter,
        "applied": applied,
        "shortlisted": shortlisted,
        "interviewed": interviewed,
        "selected": selected,
        "rejected": rejected,
        "google": google,
        "outlook": outlook,
        "invite": invite,
        "event": event,
        "source": source,
        "user_id": user_id,
        "current_site": current_site,
        "contrib": contrib,
        "text_des": text_des,
        "score": score,
        "skills": skills,
        "education": education,
        "questionnaire": questionnaire,
        "form": form,
        "data": data,
        "project": project,
        "ac_project": ac_project,
        "fresher": fresher,
        "chatname": chatname,
        "match": match,
        "data_1": json.dumps(data, cls=DjangoJSONEncoder),
    }
    return render(request, "jobs/applicant_profile.html", context)


def cal_event(request, can_id):
    candidate_details = employer_pool.objects.get(id=can_id)
    event = Event.objects.filter(
        user=request.user, attendees__icontains=candidate_details.email
    )
    context = {"event": event}
    return render(request, "jobs/cal_event.html", context)


@never_cache
@login_required
@recruiter_required
def candidate_profile(request, jd_id=None, can_id=None):
    user_id, updated_by = admin_account(request)
    candidate_details = employer_pool.objects.filter(id=can_id, client_id=user_id)

    if "message" in request.GET:
        Message_non_applicants.objects.create(
            sender=user_id,
            receiver_id=can_id,
            jd_id_id=jd_id,
            text=request.GET["message"],
        )
        Candi_invite_to_apply.objects.get_or_create(
            jd_id_id=jd_id, candidate_id_id=can_id, client_id=user_id
        )
        candidate = employer_pool.objects.get(id=can_id).email
        htmly = get_template("jobs/Message_non_applicants.html")
        domain = get_current_site(request)
        company_name = company_details.objects.get(recruiter_id=user_id).company_name
        subject, from_email, to = (
            "You got a message from " + company_name,
            "no-reply@zita.ai",
            "support@zita.ai",
        )
        html_content = htmly.render(
            {
                "sender": user_id,
                "receiver": candidate_details[0],
                "company_name": company_name,
                "message": request.GET["message"],
                "domain": domain,
                "date": timezone.now(),
            }
        )
        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = "related"
        image_data = [
            "twitter.png",
            "linkedin.png",
            "youtube.png",
            "new_zita_white.png",
        ]
        for i in image_data:
            msg.attach(logo_data(i))
        msg.send()
        result = (
            Message_non_applicants.objects.filter(
                sender_id=user_id.id, receiver_id=can_id, jd_id_id=jd_id
            )
            .annotate(
                username=F("sender__first_name"),
                message=F("text"),
            )
            .order_by("date_created")
            .values("username", "message", "sender", "date_created")
        )
        return JsonResponse(list(result), safe=False)
        # return JsonResponse({'data':1})
    if request.method == "POST":
        notes = Candidate_notes.objects.get(
            client_id=user_id, candidate_id_id=can_id
        ).notes
        notes = request.POST["notes"]
        Candidate_notes.objects.filter(
            client_id=user_id, candidate_id_id=can_id
        ).update(notes=notes)
        return JsonResponse({"data": 1})
    if Candidate_notes.objects.filter(
        client_id=user_id, candidate_id_id=can_id
    ).exists():
        notes = Candidate_notes.objects.get(client_id=user_id, candidate_id_id=can_id)
    else:
        notes = Candidate_notes.objects.create(
            client_id=user_id, candidate_id_id=can_id, notes=""
        )
    form = Candidates_notes_form(instance=notes)
    result = (
        Message_non_applicants.objects.filter(sender_id=user_id.id, receiver_id=can_id)
        .annotate(
            username=F("sender__first_name"),
            message=F("text"),
        )
        .order_by("date_created")
        .values("username", "message", "sender", "date_created")
    )
    candidate_details = candidate_details.annotate(
        file=Subquery(
            candidate_parsed_details.objects.filter(candidate_id=OuterRef("id"))
            .order_by("id")[:1]
            .values("resume_file_path")
        ),
    )
    applicants_status.objects.get_or_create(
        jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=6, client_id=user_id
    )
    current_site = get_current_site(request)
    if jd_id == None:
        context = {
            "candidate_details": candidate_details[0],
            "jd_id": 0,
            "can_id": can_id,
            "current_site": current_site,
            "result": json.dumps(list(result), cls=DjangoJSONEncoder),
            "candidate_profile": candidate_profile,
            "form": form,
        }

        return render(request, "jobs/candidate_profile.html", context)

    url = "http://192.168.3.251:8080/v5_8/GapService?WSDL"
    headers = {"content-type": "application/soap+xml"}
    invite = Candi_invite_to_apply.objects.filter(
        jd_id_id=jd_id, candidate_id_id=can_id
    ).last()
    jd = JD_form.objects.get(id=jd_id)
    try:
        match = Matched_candidates.objects.get(jd_id_id=jd_id, candidate_id_id=can_id)
    except:
        match = None
    body = (
        """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xmp="http://xmp.actonomy.com/gap">
        <soapenv:Header/><soapenv:Body><xmp:analyse><action><left><index><index><caseType>job</caseType>
        <indexId>"""
        + user_id.username
        + """</indexId></index><caseId>"""
        + str(jd_id)
        + """</caseId></index></left><right>
        <index><index><caseType>candidate</caseType><indexId>"""
        + user_id.username
        + """</indexId></index><caseId>"""
        + str(can_id)
        + """</caseId>
        </index></right></action></xmp:analyse></soapenv:Body>
    </soapenv:Envelope>
    """
    )
    try:
        response = requests.post(url, data=body, headers=headers)
        data_dict = xmltodict.parse(response.content.decode("iso-8859-1"))
        json_data = json.dumps(data_dict)
        with open(base_dir + "/media/data-1.json", "w") as json_file:
            json_file.write(json_data)
            json_file.close()
        f = open(
            base_dir + "/media/data-1.json",
        )
        data = json.load(f)
        data = data["soap:Envelope"]["soap:Body"]["ns2:analyseResponse"]["return"]
        match.profile_match = round(float(data["score"]) * 100)
        match.save()
    except Exception as e:
        data = {}
    context = {
        "data_1": json.dumps(data, cls=DjangoJSONEncoder),
        "result": json.dumps(list(result), cls=DjangoJSONEncoder),
        "candidate_details": candidate_details[0],
        "jd_id": jd_id,
        "can_id": can_id,
        "match": match,
        "invite": invite,
        "current_site": current_site,
        "candidate_profile": candidate_profile,
        "form": form,
        "data": data,
        "jd": jd,
    }

    return render(request, "jobs/candidate_profile.html", context)


def messages_data(request, chatname, jd_id):

    # text_data_json = json.loads(text_data)
    username = request.GET["username"]
    message = request.GET["message"]
    # Store message.
    users = chatname.split("-")
    jd_id = jd_id
    if request.user.is_staff:

        if company_details.objects.filter(recruiter_id=request.user).exists():
            sender = request.user
        else:
            sender = UserHasComapny.objects.get(user=request.user).company
            sender = sender.recruiter_id
        users.remove(str(sender.id))
        company_name = company_details.objects.get(recruiter_id=sender).company_name
    else:
        users.remove(str(request.user.id))
        sender = request.user
        company_name = sender.first_name

    receiver = User.objects.get(id=int(users[0]))
    Message(sender=sender, receiver=receiver, text=message, jd_id_id=jd_id).save()
    # self.receiver=receiver
    domain = get_current_site(request)
    if request.user.is_staff:
        try:
            emp_can = employer_pool.objects.get(
                client_id=request.user, email=receiver.email
            )
        except:
            emp_can = None
        if (
            applicants_status.objects.filter(
                client_id=request.user, candidate_id=emp_can, jd_id_id=jd_id
            ).exists()
            == False
            or Candi_invite_to_apply.objects.filter(
                client_id=request.user, candidate_id=emp_can, jd_id_id=jd_id
            ).exists()
            == False
        ):
            Candi_invite_to_apply.objects.create(
                client_id=request.user, candidate_id=emp_can, jd_id_id=jd_id
            )
        htmly = get_template("jobs/message.html")

        subject, from_email, to = (
            "You got a message from " + company_name,
            "no-reply@zita.ai",
            "support@zita.ai",
        )
        html_content = htmly.render(
            {
                "sender": sender,
                "receiver": receiver,
                "jd_id": jd_id,
                "company_name": company_name,
                "message": message,
                "domain": domain,
                "date": timezone.now(),
            }
        )
        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = "related"
        image_data = [
            "twitter.png",
            "linkedin.png",
            "youtube.png",
            "new_zita_white.png",
        ]
        for i in image_data:
            msg.attach(logo_data(i))
        msg.send()
    else:
        htmly = get_template("jobs/message_staff.html")

        subject, from_email, to = (
            "You got a message from " + company_name,
            "no-reply@zita.ai",
            receiver.email,
        )
        html_content = htmly.render(
            {
                "sender": sender,
                "receiver": receiver,
                "jd_id": jd_id,
                "company_name": company_name,
                "message": message,
                "domain": domain,
                "date": timezone.now(),
            }
        )
        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = "related"
        msg.send()
    return JsonResponse({"data": 1})


class MessagesAPIView(View):

    def get(self, request, chatname, jd_id):

        # Grab two users based on the chat name.
        users = User.objects.filter(id__in=chatname.split("-"))
        result = (
            Message.objects.filter(jd_id_id=jd_id)
            .filter(
                Q(sender=users[0], receiver=users[1])
                | Q(sender=users[1], receiver=users[0])
            )
            .annotate(
                username=F("sender__first_name"),
                message=F("text"),
            )
            .order_by("date_created")
            .values("username", "message", "sender", "date_created")
        )

        return JsonResponse(list(result), safe=False)


class download_invoices(View):

    def post(self, request):
        download = request.POST.getlist("download")
        invoice = recuriter_payment_history.objects.filter(id__in=download)

        with zipfile.ZipFile(
            base_dir + "/media/candidate_profile/invoice.zip", "w"
        ) as myzip:
            for i in invoice:
                try:
                    file = generate_invoice(request, i.id)
                    file_name = file["Content-Disposition"].split("=")[1]
                    file_content = open(
                        base_dir + "/media/candidate_profile/" + file_name, "wb"
                    ).write(file.content)
                    file_name = os.path.basename(file_name)
                    myzip.write(
                        base_dir + "/media/candidate_profile/" + file_name, file_name
                    )
                except Exception as e:
                    logger.error("error in download_interested : " + str(e))
                    file_name = "error.txt"
                    file_content = open(
                        base_dir + "/media/candidate_profile/" + file_name, "w"
                    ).write(str("Some details are not there for the candidate ID"))
                    file_name = os.path.basename(file_name)
                    myzip.write(
                        base_dir + "/media/candidate_profile/" + file_name, file_name
                    )
        myzip.close()
        file = open(base_dir + "/media/candidate_profile/invoice.zip", "rb")
        response = HttpResponse(file, content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=invoice.zip"
        return response


def generate_invoice(request, pk=None):

    invoice = recuriter_payment_history.objects.get(id=pk)
    context = {"invoice": invoice, "request": request}
    html_template = (
        get_template("pdf/invoice.html").render(context).encode(encoding="UTF-8")
    )
    # pdf_file = HTML(string=html_template,base_url=request.build_absolute_uri()).write_pdf()
    pdf_file = HTML(string=html_template, base_url=settings.profile_pdf_url).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        "attachment; filename=Invoice-" + invoice.invoice_id + ".pdf"
    )
    return response


def generate_invoice_test(request, pk=None):

    invoice = recuriter_payment_history.objects.get(id=pk)
    context = {"invoice": invoice, "request": request}
    return render(request, "pdf/invoice.html", context)


@login_required
@recruiter_required
def invoice(request):

    form = recuriter_payment_history.objects.filter(recruiter_id=request.user).order_by(
        "-jd_id", "-created_on"
    )
    page = request.GET.get("page", 1)
    paginator = Paginator(form, 10)

    try:
        form = paginator.page(page)
    except PageNotAnInteger:
        form = paginator.page(1)

    except EmptyPage:
        form = paginator.page(paginator.num_pages)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
    context = {"form": form, "params": params}
    return render(request, "jobs/invoice_history.html", context)


def candidate_notes(request, pk):
    user_id, updated_by = admin_account(request)
    if request.method == "POST":
        notes = Candidate_notes.objects.get(client_id=user_id, candidate_id_id=pk).notes
        notes = request.POST["notes"]
        Candidate_notes.objects.filter(client_id=user_id, candidate_id_id=pk).update(
            notes=notes
        )
        return JsonResponse({"data": 1})
    if Candidate_notes.objects.filter(client_id=user_id, candidate_id_id=pk).exists():
        notes = Candidate_notes.objects.get(client_id=user_id, candidate_id_id=pk)
    else:
        notes = Candidate_notes.objects.create(
            client_id=user_id, candidate_id_id=pk, notes=""
        )
    form = Candidates_notes_form(instance=notes)
    context = {"form": form}
    return render(request, "jobs/candidate_notes.html", context)


@never_cache
@login_required
@recruiter_required
def company_detail(request):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass

    has_permission = user_permission(request, "manage_account_settings")
    if not has_permission == True:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    user_id, updated_by = admin_account(request)
    try:
        recruiter = company_details.objects.get(recruiter_id=user_id)
        company_detail = company_details_form(instance=recruiter)
    except:
        company_detail = company_details_form()
        basic_details = Signup_Form.objects.get(user_id=user_id)
        company_detail.fields["company_name"].initial = basic_details.company_name
        company_detail.fields["email"].initial = request.user.email
        company_detail.fields["contact"].initial = basic_details.contact_no
        recruiter = None
    if request.method == "POST":
        if "company_details" in request.POST:
            if recruiter == None:
                company_detail = company_details_form(request.POST, request.FILES)
            else:
                company_detail = company_details_form(
                    request.POST, request.FILES, instance=recruiter
                )
            if company_detail.is_valid():
                temp = company_detail.save(commit=False)
                temp.recruiter_id = user_id
                temp.updated_by = updated_by
                main = temp.save()
                recruiter = company_details.objects.get(recruiter_id=user_id)
                UserDetail.objects.filter(user=user_id).update(
                    contact=request.POST["contact"]
                )
                if "without_career" in request.POST:
                    data = {"success": False}
                    return JsonResponse(data)
                data = {"success": True}
                return JsonResponse(data)
    try:
        setting = career_page_setting.objects.get(recruiter_id=user_id)
    except:
        setting = None
    context = {
        "company_detail": company_detail,
        "setting": setting,
        "permission": permission,
        "recruiter": recruiter,
    }
    return render(request, "jobs/company_details.html", context)


def company_detail_signup(request):
    user = request.user
    if request.method == "POST":
        if "company_details" in request.POST:
            company_detail = company_details_form(request.POST, request.FILES)
            if company_detail.is_valid():
                temp = company_detail.save(commit=False)
                temp.recruiter_id_id = request.user.id
                main = temp.save()
                return redirect("jobs:company_detail_signup")
    basic_details = Signup_Form.objects.get(user_id=request.user)
    basic_details = Signup_Form.objects.get(user_id=request.user)
    company_detail = company_details_form()
    company_detail.fields["company_name"].initial = basic_details.company_name
    company_detail.fields["email"].initial = request.user.email
    company_detail.fields["contact"].initial = basic_details.contact_no

    context = {
        "company_detail": company_detail,
    }
    return render(request, "jobs/company_detail_signup.html", context)


@never_cache
@login_required
@recruiter_required
def setting_page(request):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass

    has_permission = user_permission(request, "manage_account_settings")
    if not has_permission == True:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    user_id, updated_by = admin_account(request)
    try:
        setting = career_page_setting.objects.get(recruiter_id=user_id)
    except:
        setting = None
    if request.is_ajax():
        if request.method == "POST":
            if "setting_page" in request.POST:
                if setting == None:
                    setting_pages = career_page_setting_form(
                        request.POST, request.FILES
                    )
                else:
                    setting_pages = career_page_setting_form(
                        request.POST, request.FILES, instance=setting
                    )
                if setting_pages.is_valid():
                    temp = setting_pages.save(commit=False)
                    temp.recruiter_id = user_id
                    temp.updated_by = updated_by
                    temp.save()
                    data = {"url": request.POST["career_page_url"], "success": 1}
                    return JsonResponse(data)
    if setting != None:
        setting_page = career_page_setting_form(instance=setting)
    else:
        setting_page = career_page_setting_form()

        setting_page.fields["page_font"].initial = "proxima nova alt rg"
        setting_page.fields["header_font_size"].initial = 16
        setting_page.fields["header_color"].initial = "#ffffff"
        setting_page.fields["page_font_size"].initial = 15
        setting_page.fields["banner_font_size"].initial = 16
        setting_page.fields["menu_1"].initial = "Home"
        setting_page.fields["button_color"].initial = "#f26522"
        setting_page.fields["footer_color"].initial = "#ffffff"

    domain = get_current_site(request)
    context = {
        "setting_page": setting_page,
        "setting": setting,
        "domain": domain,
        "permission": permission,
    }
    return render(request, "jobs/setting_page.html", context)


def setting_page_signup(request):
    user = request.user
    try:
        setting = career_page_setting.objects.get(recruiter_id=user)
    except:
        setting = None

    if request.method == "POST":
        if "setting_page" in request.POST:
            if setting == None:
                setting_pages = career_page_setting_form(request.POST, request.FILES)
            else:
                setting_pages = career_page_setting_form(
                    request.POST, request.FILES, instance=setting
                )
            if setting_pages.is_valid():
                setting = setting_pages.save(commit=False)
                setting.recruiter_id_id = request.user.id
                setting.save()
    if setting != None:
        setting_page = career_page_setting_form(instance=setting)
    else:
        setting_page = career_page_setting_form()

        setting_page.fields["page_font"].initial = "proxima nova alt rg"
        setting_page.fields["header_font_size"].initial = 16
        setting_page.fields["header_color"].initial = "#ffffff"
        setting_page.fields["page_font_size"].initial = 15
        setting_page.fields["banner_font_size"].initial = 16
        setting_page.fields["button_color"].initial = "#f26522"
        setting_page.fields["footer_color"].initial = "#ffffff"
    context = {
        "setting_page": setting_page,
        "setting": setting,
    }
    return render(request, "jobs/setting.html", context)


@never_cache
@login_required
@recruiter_required
def user_profile_setting(request):

    password = PasswordChangeForm(request.user)
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )

    if request.method == "POST":
        if "password" in request.POST:
            password = PasswordChangeForm(request.user, request.POST)
            if password.is_valid():
                user = password.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully")
                return redirect("jobs:user_profile_setting")

        form = user_profile_form(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()

    form = user_profile_form(instance=request.user)
    context = {"form": form, "password": password, "permission": permission}
    return render(request, "jobs/user_profile_setting.html", context)


def external_job_posting(request, pk=None):
    if request.method == "POST" and "ext_job_post" in request.POST:
        jd_details = JD_form.objects.get(id=pk)
        location = JD_locations.objects.get(jd_id_id=pk)
        user_id, updated_by = admin_account(request)
        company_name = company_details.objects.get(recruiter_id=user_id).company_name
        career_page_url = career_page_setting.objects.get(
            recruiter_id=user_id
        ).career_page_url
        main_url = get_current_site(request).domain
        data = {}
        data["title"] = jd_details.job_title
        if jd_details.job_type.id in [1, 4, 5]:
            data["job_type"] = "Permanent"
        else:
            data["job_type"] = jd_details.job_type.label_name
        data["description"] = jd_details.richtext_job_description
        if jd_details.show_sal_to_candidate == False:
            data["salary_hidden"] = "yes"
        data["currency"] = "USD"
        data["salary_min"] = jd_details.salary_min
        data["salary_max"] = jd_details.salary_max
        data["salary_max"] = jd_details.salary_max
        data["location_city"] = location.city.name
        data["location_state"] = location.state.name
        data["country"] = "US"
        data["apply_url"] = (
            "https://"
            + main_url
            + "/"
            + career_page_url
            + "/job-view/"
            + str(jd_details.id)
            + "/"
            + str(jd_details.job_title)
        )
        data["apply_email"] = request.user.email
        data["quick_apply"] = "false"
        data["posted_by"] = company_name
        data["reference"] = jd_details.job_id
        if jd_details.job_type.id != 3:
            data["salary_time_period"] = "annum"
        else:
            data["salary_time_period"] = "hour"

        url = settings.rl_job_posting_url
        headers = {
            "Content-Type": "application/json",
            "AccountId": "13478",
            "AccountKey": "44DDDB92BBEC24E",
        }
        result = requests.post(
            url,
            json=data,
            headers=headers,
            auth=(settings.rl_username, settings.rl_password),
        )
        try:
            result = json.loads(result.content)
            external_jobpostings_by_client.objects.get_or_create(
                client_id=request.user,
                ext_jp_site_id_id=1,
                jd_id_id=pk,
                posted_by=request.user.username,
                jobposting_url=result["job_url"],
                job_posting_ref_id=result["job_id"],
            )
        except Exception as e:
            logger.error(
                "Error in resume-library job posting, Error -- "
                + str(e)
                + "JD-ID -- "
                + str(pk)
            )
    result = {"success": True}
    return JsonResponse(result)


def remove_external_job_posting(request, pk=None):
    try:
        external_jobs = external_jobpostings_by_client.objects.get(
            jd_id_id=pk, is_active=True, ext_jp_site_id_id=1
        )
    except:
        external_jobs = None
    if external_jobs != None:
        try:
            url = settings.rl_job_removing_url + external_jobs.job_posting_ref_id
            headers = {"Content-Type": "application/json"}
            result = requests.delete(
                url, headers=headers, auth=(settings.rl_username, settings.rl_password)
            )
        except Exception as e:
            logger.error(
                "Error in resume-library job remove, Error -- "
                + str(e)
                + "JD-ID -- "
                + str(pk)
            )
        external_jobs.is_active = False
        external_jobs.job_inactivated_on = datetime.now()
        external_jobs.job_inactivated_by = request.user.username
        external_jobs.save()
        result = {"success": True}
    else:
        result = {"success": False}
    return JsonResponse(result)


def xml_test(request):
    return HttpResponse(
        open(base_dir + "/templates/test.xml").read(), content_type="application/xml"
    )
    # return render(request,'test.xml',content_type='application/xml')


def my_database_bulk(request):
    user_id, updated_by = admin_account(request)
    if "invite" in request.GET:
        jd = request.GET["jd"]

        for i in request.GET.getlist("candi_id"):
            Candi_invite_to_apply.objects.create(
                jd_id_id=jd,
                candidate_id_id=i,
                client_id=user_id,
            )
            candidate_details = employer_pool.objects.get(id=i)
            jd_id = JD_form.objects.get(id=jd)
            loc = JD_locations.objects.filter(jd_id=jd_id)
            qual = JD_qualification.objects.filter(jd_id=jd_id)
            match = Matched_candidates.objects.filter(
                candidate_id=candidate_details, jd_id=jd_id
            ).last()
            company_detail = company_details.objects.get(
                recruiter_id=user_id
            ).company_name
            url = career_page_setting.objects.get(recruiter_id=user_id).career_page_url
            htmly = get_template("email_templates/invite_to_apply.html")
            current_site = get_current_site(request)
            subject, from_email, to = (
                "Job Notification: An employer invitation to Apply for a Job",
                email_main,
                "support@zita.ai",
            )
            html_content = htmly.render(
                {
                    "jd_id": jd_id,
                    "loc": loc,
                    "match": match,
                    "qual": qual,
                    "company_detail": company_detail,
                    "current_site": current_site,
                    "candidate_details": candidate_details,
                    "job_pool": jd_id,
                    "url": url,
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()
            UserActivity.objects.create(
                user=request.user,
                action_id=5,
                action_detail='"'
                + str(candidate_details.first_name)
                + '" for the job id: '
                + str(jd_id.job_id),
            )

    elif "download" in request.GET:
        t = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
        with zipfile.ZipFile(
            base_dir + "/media/candidate_profile/candidates_profile_" + str(t) + ".zip",
            "w",
        ) as myzip:
            for i in request.GET.getlist("candi_id"):
                resume_file = candidate_parsed_details.objects.get(
                    candidate_id_id=i
                ).resume_file_path
                myzip.write(
                    base_dir + "/media/" + str(resume_file),
                    str(resume_file).split("/")[1],
                )
        myzip.close()
        file = open(
            base_dir + "/media/candidate_profile/candidates_profile_" + str(t) + ".zip",
            "rb",
        )
        response = HttpResponse(file, content_type="application/zip")
        response["Content-Disposition"] = (
            "attachment; filename=candidates_profile_" + str(t) + ".zip"
        )
        return response
    data = {
        "success": 1,
    }
    return JsonResponse(data)

    result = {"success": False}
    return JsonResponse(result)


@never_cache
@login_required
@recruiter_required
def my_database(request):
    try:
        if int(request.session["expire_in"]) <= 0:
            return redirect("payment:manage_subscription")
    except KeyError:
        pass
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    has_permission = user_permission(request, "my_database")
    if not has_permission == True:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})
    user_id, updated_by = admin_account(request)
    try:
        skill_list = open(base_dir + "/" + "media/skills.csv", "r")
    except:
        skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
    skill_list = skill_list.read()
    skill_list = skill_list.split("\n")
    job_title = JD_form.objects.filter(user_id=user_id, jd_status_id=1).values(
        "job_title", "id"
    )
    # for i in job_title:
    # data = employer_pool.objects.filter(client_id=user_id).count()
    # 	result=matching_api_to_db(request,jd_id=i['id'],can_id=None)
    try:
        candidate_available = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=12
        ).available_count
    except:
        candidate_available = 0
    context = {
        "job_title": job_title,
        "permission": permission,
        "skill_list": json.dumps(skill_list, cls=DjangoJSONEncoder),
        "candidate_available": candidate_available,
    }
    return render(request, "jobs/my_database.html", context)


def my_database_ajax(request):
    fav_id = 0
    user_id, updated_by = admin_account(request)
    data = (
        employer_pool.objects.filter(client_id=user_id)
        .order_by("-created_at")
        .exclude(email__isnull=True)
        .exclude(first_name__isnull=True)
    )
    # for i in data:
    # 	generate_candidate_json(request,pk=i.pk)
    # applicant = applicants_status.objects.filter(client_id=admin)
    data = data.annotate(
        applicant_view=Subquery(
            applicants_status.objects.filter(
                client_id=user_id, candidate_id=OuterRef("id"), status_id_id=6
            )[:1].values("created_on")
        ),
    )

    if "job_title" in request.GET and len(request.GET["job_title"]) > 0:
        jd = request.GET["job_title"]
        data = data.annotate(
            applicant=Subquery(
                applicants_status.objects.filter(
                    jd_id_id=jd, candidate_id=OuterRef("id")
                )
                .exclude(status_id_id=6)[:1]
                .values("created_on")
            ),
            match=Subquery(
                Matched_candidates.objects.filter(
                    jd_id_id=jd, candidate_id=OuterRef("id")
                )[:1].values("profile_match")
            ),
            invite=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id_id=jd, candidate_id=OuterRef("id")
                )
                .order_by("-created_at")[:1]
                .values("created_at")
            ),
            image=Subquery(
                Profile.objects.filter(user_id=OuterRef("candidate_id__user_id"))[
                    :1
                ].values("image")
            ),
            interested=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id_id=jd, candidate_id=OuterRef("id")
                )
                .order_by("-created_at")[:1]
                .values("is_interested")
            ),
            responded_date=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id_id=jd, candidate_id=OuterRef("id")
                )[:1].values("responded_date")
            ),
        ).order_by("-match")
        if "fav" in request.GET and len(request.GET["fav"]) > 0:

            if request.GET["fav"] == "add":
                fav_id = 1
                jd_list = get_object_or_404(JD_form, id=jd)
                fav = jd_list.favourite.all()
                data = data.annotate(
                    fav=Subquery(fav.filter(id=OuterRef("id"))[:1].values("id"))
                ).exclude(fav__isnull=True)
    else:
        jd = 0
        data = data.order_by("-id")
    if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
        if "@" in request.GET["candidate"]:
            data = data.filter(email__icontains=request.GET["candidate"])
        else:
            data = data.filter(first_name__icontains=request.GET["candidate"])

    if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
        if request.GET["work_experience"] == "0-1":
            data = data.filter(work_exp__in=["0-1", "0", "Less than 1 year"])
        elif request.GET["work_experience"] == "10+":
            data = data.filter(
                work_exp__in=["More than 10 years", "10", "11", "12", "13", "14", "15"]
            )
        else:
            data = data.filter(work_exp__icontains=request.GET["work_experience"])
    if "relocate" in request.GET and len(request.GET["relocate"]) > 0:
        data = data.filter(relocate=True)
    if "education_level" in request.GET and len(request.GET["education_level"]) > 0:
        data = data.filter(
            reduce(
                operator.or_,
                (
                    Q(qualification__icontains=qual)
                    for qual in request.GET.getlist("education_level")
                ),
            )
        )
    if "type_of_job" in request.GET and len(request.GET["type_of_job"]) > 0:
        data = data.filter(job_type_id=request.GET["type_of_job"])
    if "location" in request.GET and len(request.GET["location"]) > 0:
        data = data.filter(location__icontains=request.GET["location"])
    if "user_type" in request.GET and len(request.GET["user_type"]) > 0:
        data = data.filter(can_source_id=request.GET["user_type"])
        user_type = request.GET["user_type"]
    else:
        user_type = ""
    if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
        skill_match_list = request.GET.getlist("skill_match")
        data = data.filter(
            reduce(
                operator.or_, (Q(skills__icontains=item) for item in skill_match_list)
            )
        )
    if "interested" in request.GET and len(request.GET["interested"]) > 0:
        if request.GET["interested"] == "interested":
            data = data.order_by("-interested", "-match")
        elif request.GET["interested"] == "not_interested":
            data = data.order_by("-responded_date", "interested", "-match")
    search = 1
    try:
        if request.GET["search"] == "1":
            search = 0
    except:
        pass
    page = request.GET.get("page", 1)
    paginator = Paginator(data, 20)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)

    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
    context = {
        "data": data,
        "jd": jd,
        "fav_id": fav_id,
        "user_type": user_type,
        "params": params,
        "search": search,
    }
    return render(request, "jobs/my_database_ajax.html", context)


def show_all_match(request, jd, pk):
    user_id, updated_by = admin_account(request)
    jd_list = JD_form.objects.filter(user_id=user_id, jd_status_id__in=[1]).values_list(
        "id", flat=True
    )
    match = Matched_candidates.objects.filter(candidate_id_id=pk, jd_id__in=jd_list)
    applicant = applicants_status.objects.filter(
        candidate_id_id=pk, jd_id__in=jd_list, status_id__in=[1, 2, 3, 4, 7]
    )
    candidate_id = get_object_or_404(employer_pool, id=pk)
    fav = candidate_id.favourite.all()
    match = match.annotate(
        applicant=Subquery(
            applicant.filter(
                candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
            )[:1].values("id")
        ),
        fav=Subquery(fav.filter(id=OuterRef("jd_id"))[:1].values("id")),
    )
    applicant = applicant.annotate(
        match=Subquery(
            match.filter(
                candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
            )[:1].values("profile_match")
        ),
        fav=Subquery(fav.filter(id=OuterRef("jd_id"))[:1].values("id")),
    ).exclude(match__isnull=False)
    context = {
        "match": match,
        "applicant": applicant,
    }
    return render(request, "jobs/show_all_match.html", context)


def favourite_post(request, jd, pk):
    jd_id = get_object_or_404(JD_form, id=jd)
    candidate_id = get_object_or_404(employer_pool, id=pk)

    data = {"success": False}
    if candidate_id.favourite.filter(id=jd_id.pk).exists():
        candidate_id.favourite.remove(jd_id)

    else:
        # jd_list.favourite.add(request.user)
        candidate_id.favourite.add(jd_id)
        data["success"] = True
    return JsonResponse(data)


def qualification_matching(jd_qualification, qualifications):
    jd_qualification = [item for sublist in jd_qualification for item in sublist]
    qual = []
    qualifications = get_qualification(qualifications)
    if qualifications:
        try:
            if "Diploma" in qualifications:
                qual = ["Diploma"]
            if "Bachelors" in qualifications:
                qual = ["Diploma", "Bachelors"]
            if "Masters" in qualifications:
                qual = ["Diploma", "Bachelors", "Masters"]
            if "Doctorate" in qualifications:
                qual = ["Diploma", "Bachelors", "Masters", "Doctorate"]
            len_jd_qual = len(jd_qualification)
            qual = set(qual)
            jd_education = set(word.lower() for word in jd_qualification)
            qual = set(word.lower() for word in qual)
            matched_qualification = jd_education.intersection(qual)
            len_mat_qual = len(matched_qualification)
            qualification_percent = round((len_mat_qual / len_jd_qual) * 20)
            not_matched_qualification = jd_education - qual
            if "Any Qualification" in jd_qualification and len(qual) >= 1:
                qualification_percent = 20
                matched_qualification = qualifications
                not_matched_qualification = []
            elif "Any Qualification" in jd_qualification and len(qual) == 0:
                qualification_percent = 20
                matched_qualification = []
                not_matched_qualification = jd_qualification
        except Exception as e:
            qualification_percent = 0
            matched_qualification = []
            not_matched_qualification = jd_qualification
    else:
        qualification_percent = 0
        matched_qualification = []
        not_matched_qualification = jd_qualification
    return qualification_percent, matched_qualification, not_matched_qualification


def skills_matching(resume_skills, jd_skills):
    # the name is changed jd_skills is converted into resume_skills and resume_skills ins converted into jd_skills
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    jd_skills_lower = [skill.lower() for skill in jd_skills]
    matched_skills = []
    not_matched_skills = []
    for resume_skill in resume_skills_lower:
        is_matched = False
        for jd_skill in jd_skills_lower:
            # if all(part in jd_skill for part in re.findall(r'\w+', resume_skill)):
            if jd_skill.strip() == resume_skill.strip():
                matched_skills.append(resume_skill)
                is_matched = True
                break
        if not is_matched:
            not_matched_skills.append(resume_skill)
    if len(resume_skills_lower) != 0:
        percentage_matched = round(
            (len(matched_skills) / len(resume_skills_lower)) * 100, 2
        )
    else:
        percentage_matched = 0
    percentage_matched = percentage_matched * 0.8
    return round(percentage_matched), matched_skills, not_matched_skills


from jobs.utils import *


def basic_matching(cand_id, jd_id, user, request):
    can_id = employer_pool.objects.get(id=cand_id)
    if Resume_overview.objects.filter(application_id=can_id.candidate_id).exists():
        resume_input = Resume_overview.objects.get(
            application_id=can_id.candidate_id
        ).parsed_resume
    elif candidate_parsed_details.objects.filter(candidate_id=can_id).exists():
        resume_input = candidate_parsed_details.objects.get(
            candidate_id=can_id
        ).parsed_text
    else:
        resume_input = None
    resume_input = json.loads(json.dumps(resume_input))
    resume_input = json.loads(str(resume_input))
    if (
        resume_input["Technical skills"] == None
        or resume_input["Technical skills"] == []
    ):
        resume_input["Technical skills"] = ""
    else:
        total_skills = resume_input["Technical skills"]

    s_skills = resume_input.get("Soft Skills", None)
    s_skills1 = resume_input.get("Soft skills", None)
    if s_skills and len(s_skills) > 0:
        if "Soft Skills" in resume_input:
            if resume_input["Soft Skills"] == None or resume_input["Soft Skills"] == []:
                pass
            else:
                if isinstance(resume_input, str):
                    tech_skill = resume_input["Technical skills"].split()

                    resume_input["Technical skills"] = tech_skill
                elif isinstance(resume_input["Technical skills"], list):
                    resume_input["Technical skills"].extend(resume_input["Soft Skills"])
    if s_skills1 and len(s_skills1) > 0:
        try:
            if "Soft skills" in resume_input:
                if (
                    resume_input["Soft skills"] == None
                    or resume_input["Soft skills"] == []
                ):
                    resume_input["Soft skills"] = ""
                else:
                    resume_input["Technical skills"].extend(resume_input["Soft skills"])
        except:
            if "Soft skills" in resume_input:
                if (
                    resume_input["Soft skills"] is None
                    or not resume_input["Soft skills"]
                ):
                    resume_input["Soft skills"] = []
                if not isinstance(resume_input["Technical skills"], list):
                    resume_input["Technical skills"] = []

                resume_input["Technical skills"].extend(resume_input["Soft skills"])

    total_skills = resume_input["Technical skills"]
    skills = total_skills
    qualifications = resume_input.get("Highest Qualifications", None)
    jd_skills = JD_skills_experience.objects.filter(jd_id=jd_id).values("skill")
    jd_skills = [item["skill"] for item in jd_skills]
    jd_qualification = JD_qualification.objects.filter(jd_id=jd_id).values_list(
        "qualification"
    )
    skills_percent, matched_skills, not_matched_skills = skills_matching(
        jd_skills, skills
    )
    qualification_percent, matched_qualification, not_matched_qualification = (
        qualification_matching(jd_qualification, qualifications)
    )

    if qualification_percent == 20 and skills_percent == 0:
        qualification_percent = 0
    overall_percentage = qualification_percent + skills_percent
    result = None
    if Matched_candidates.objects.filter(candidate_id=can_id, jd_id=jd_id).exists():
        if not Matched_percentage.objects.filter(
            jd_id=jd_id, candidate_id=can_id
        ).exists():
            Matched_candidates.objects.filter(candidate_id=can_id, jd_id=jd_id).update(
                profile_match=overall_percentage
            )
            remove_zmatch = removing_zita_match(can_id, jd_id)
            result = None
        else:
            overall_percentage = (
                Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id)
                .values_list("overall_percentage")
                .last()[0]
            )
            result = adv_match_calculation(jd_id, can_id, user, request)
    else:
        Matched_candidates.objects.create(
            profile_match=overall_percentage,
            candidate_id=employer_pool.objects.get(id=cand_id),
            jd_id=JD_form.objects.get(id=jd_id),
        )

    if skills_percent > 0:
        content = zita_matched_candidates(user, jd_id, cand_id, "basic")
    plan = subscriptions.objects.filter(client_id=user).last().plan_id.pk
    length_check = len(subscriptions.objects.filter(client_id=user))
    degrade_ai_match = False
    if length_check > 2:
        previous_plan = (
            subscriptions.objects.filter(client_id=user)
            .order_by("-subscription_id")
            .values("plan_id_id")[1]
        )
        if previous_plan["plan_id_id"] > plan:
            if Matched_percentage.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).exists():
                degrade_ai_match = True

    ai_matching = client_features_balance.objects.filter(
        client_id=user, feature_id=62
    ).exists()
    ai_matching_plan = list(
        tmeta_plan.objects.filter(plan_id__in=[6, 7, 10, 11]).values_list(
            "plan_id", flat=True
        )
    )
    apply_match = applicants_status.objects.filter(
        jd_id=jd_id, candidate_id=cand_id
    ).exists()
    # if candidates_ai_matching.objects.filter(jd_id=jd_id,candidate_id = cand_id).exists():
    #     apply_match = True
    features, plans = plan_checking(user, "resume")
    active_resume = list(
        employer_pool.objects.filter(
            client_id=user, first_name__isnull=False, email__isnull=False
        ).values_list("id", flat=True)[: int(features)]
    )
    total_length = employer_pool.objects.filter(
        client_id=user, first_name__isnull=False, email__isnull=False
    ).values_list("id", flat=True)
    active_resume = employer_pool.objects.filter(
        client_id=user, first_name__isnull=False, email__isnull=False
    ).values_list("id", flat=True)[: int(features)]
    blocked_resume = blocked_resume = (
        employer_pool.objects.filter(
            client_id=user, first_name__isnull=False, email__isnull=False
        )
        .order_by("id")
        .values_list("id", flat=True)
    )
    if len(total_length) > int(features):
        blocked_resume = (
            employer_pool.objects.filter(
                client_id=user, first_name__isnull=False, email__isnull=False
            )
            .order_by("-id")
            .values_list("id", flat=True)[: len(total_length) - int(features)]
        )
    candidates_ai = candidates_ai_matching.objects.filter(
        jd_id=jd_id, candidate_id=cand_id
    ).exists()
    block_descriptive = applicant_descriptive.objects.filter(
        jd_id=jd_id, candidate_id=cand_id, is_active=True
    ).exists()
    technical = []
    non_technical = []
    nontech = 0
    if result:
        technical = result["technical"]
        non_technical = result["non_technical"]
        nontech = result["nontech"]
        overall_percentage = result["overall"]
    status = (
        jd_nice_to_have.objects.filter(jd_id_id=jd_id, nice_to_have__isnull=False)
        .exclude(nice_to_have="")
        .exists()
    )

    overall_output = {
        "source": {"jd_skills": jd_skills, "qualification": list(jd_qualification)},
        "matched_data": {
            "matched_skills": matched_skills,
            "matched_qualification": matched_qualification,
        },
        "not_matched_data": {
            "not_matched_skills": not_matched_skills,
            "not_matched_qualification": not_matched_qualification,
        },
        "skills_percent": skills_percent,
        "qualification_percent": qualification_percent,
        "overall_percentage": round(overall_percentage),
        "candidate_id": cand_id,
        "non_tech_percentage": nontech if non_technical != 0 else 0,
        "ai_matching": ai_matching,
        "plan": plan,
        "non_technical": non_technical if non_technical != [] else [],
        "technical": technical if technical != [] else [],
        "ai_matching_plan": ai_matching_plan,
        "active_resume": active_resume,
        "apply_match": apply_match,
        "blocked_resume": blocked_resume,
        "candidates_ai": candidates_ai,
        "block_descriptive": block_descriptive,
        "degrade_ai_match": degrade_ai_match,
        "status": status,
    }
    return overall_output


def zita_matched_candidates(user, jd_id, can_id, matching):
    if matching == "ai":
        if Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id).exists():
            overall_percentage = (
                Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id)
                .values_list("overall_percentage")
                .last()[0]
            )
        else:
            overall_percentage = 0
        if overall_percentage > 0:
            jd_zita = list(
                applicants_status.objects.filter(jd_id=jd_id)
                .values_list("candidate_id", flat=True)
                .distinct()
            )
            if int(can_id) not in jd_zita:
                if (
                    client_features_balance.objects.get(
                        client_id=user, feature_id=27
                    ).available_count
                    > 0
                ):
                    if not zita_match_candidates.objects.filter(
                        client_id=user, jd_id_id=jd_id, candidate_id_id=can_id
                    ).exists():
                        if employer_pool.objects.filter(
                            id=can_id, first_name__isnull=False, email__isnull=False
                        ).exists():
                            zita_match_candidates.objects.create(
                                jd_id_id=jd_id,
                                candidate_id_id=can_id,
                                client_id=user,
                                status_id_id=5,
                                updated_by=user.username,
                            )
    elif matching == "basic":
        jd_zita = (
            applicants_status.objects.filter(jd_id=jd_id)
            .values_list("candidate_id", flat=True)
            .distinct()
        )
        if int(can_id) not in jd_zita:
            # if client_features_balance.objects.get(client_id=user,feature_id=27).available_count > 0:
            if not zita_match_candidates.objects.filter(
                client_id=user, jd_id=jd_id, candidate_id_id=can_id
            ).exists():
                if employer_pool.objects.filter(
                    id=can_id, first_name__isnull=False, email__isnull=False
                ).exists():
                    data = zita_match_candidates.objects.create(
                        jd_id_id=JD_form.objects.get(id=jd_id).id,
                        candidate_id_id=employer_pool.objects.get(id=can_id).id,
                        client_id=User.objects.get(username=user),
                        status_id_id="5",
                        updated_by=user,
                    )

    context = {"success": True, "matching": matching}
    return context


def string_checking(name):
    if name != None:
        word = name.strip()
        if word == "":
            return None
        elif word == None or word == "None":
            return None
        elif word == "Resume Parser Pro":
            return None
        else:
            return word
    else:
        return name


def candidate_bulk_matching(can_id, jd_id, user_id):
    success = True
    if candidates_ai_matching.objects.filter(candidate_id=can_id, jd_id=jd_id).exists():
        success = candidates_ai_matching.objects.filter(
            candidate_id=can_id, jd_id=jd_id
        ).update(is_active=True)
    else:
        candidates = employer_pool.objects.get(id=can_id)
        jd_ids = JD_form.objects.get(id=jd_id)
        if not applicants_status.objects.filter(
            candidate_id=can_id,
            jd_id=jd_id,
            candidate_id__first_name__isnull=False,
            candidate_id__email__isnull=False,
        ).exists():
            success = candidates_ai_matching.objects.create(
                candidate_id=candidates, jd_id=jd_ids, user_id=user_id
            )
    return success


def user_credits(user_id):
    job_credits = client_features_balance.objects.get(
        client_id=user_id, feature_id=10
    ).available_count
    resume_credits = client_features_balance.objects.get(
        client_id=user_id, feature_id=27
    ).available_count
    resume_unlock_credits = client_features_balance.objects.get(
        client_id=user_id, feature_id=53
    ).available_count
    ai_match_count = client_features_balance.objects.get(
        client_id=user_id, feature_id=6
    ).available_count
    context = {
        "job_credits": job_credits,
        "resume_credits": resume_credits,
        "resume_unlock_credits": resume_unlock_credits,
        "ai_match_count": ai_match_count,
    }
    return context


def unlimited_addons(user_id):
    interview = client_features_balance.objects.filter(
        client_id=user_id, feature_id=59
    ).exists()
    comparative = client_features_balance.objects.filter(
        client_id=user_id, feature_id=60
    ).exists()
    resume_multiple_job = client_features_balance.objects.filter(
        client_id=user_id, feature_id=62
    ).exists()
    priority = client_features_balance.objects.filter(
        client_id=user_id, feature_id=61
    ).exists()
    context = {
        "interview": interview,
        "comparative": comparative,
        "resume_multiple_job": resume_multiple_job,
        "priority": priority,
    }
    return context


def expire_details(user_id):
    plan = subscriptions.objects.filter(client_id=user_id).last()
    end_date = None
    end_date = plan.subscription_valid_till
    start_date = plan.subscription_start_ts
    plan_exp = remaining_days(end_date)
    addons_feature = addons_remainder(user_id, start_date, end_date)
    if plan_exp["days"] > 0:
        alert_remainder = f'Plan will expire in {plan_exp["days"]} days'
    elif plan_exp["days"] == 0:
        alert_remainder = f"Plan expires today."
    else:
        alert_remainder = f"Plan has already expired."
    context = {
        "plan_id": plan.plan_id.pk,
        "end_subscription": end_date,
        "remainder": alert_remainder,
        "plan_exp": plan_exp,
        "addons_feature": addons_feature,
    }
    return context


def remaining_days(target):
    target = datetime.fromisoformat(str(target))
    current = datetime.now(target.tzinfo)
    target += timedelta(days=1)
    remaining = target - current
    # if remaining.total_seconds() <= 0:
    #     return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}
    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    context = {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}
    return context


def addons_remainder(user_id, start_date, end_date):
    carry_in = (
        client_features_balance.objects.filter(
            client_id=user_id, add_ons_id__is_carry=True
        )
        .values("add_ons_id", "add_ons_id__name", "available_count")
        .exclude(feature_id__in=[6, 10, 27, 53])
    )
    carry_out = (
        client_features_balance.objects.filter(
            client_id=user_id, add_ons_id__is_carry=False
        )
        .values("add_ons_id", "add_ons_id__name", "available_count")
        .exclude(feature_id__in=[6, 10, 27, 53])
    )
    carry_forward = []
    carry_outward = []
    result = remaining_days(end_date)
    add_on_remaining = None
    for i in carry_in:
        alerts = f'Your Addons{i["add_ons_id__name"]} count is {i["available_count"]} to use this addons untill 0'
        carry_forward.append(alerts)
    for x in carry_out:
        end_addon = one_month_checking(start_date, 1)
        date_only = datetime.fromisoformat(str(end_addon))
        date_only = date_only.strftime("%b %dth")
        add_on_remaining = remaining_days(end_addon)
        add_on_remaining = add_on_remaining["days"]
        if result["days"] < 30:
            alerts = f'Your Have Unlimited {x["add_ons_id__name"]} will use untill {date_only}'
        else:
            alerts = f'Your Have Unlimited {x["add_ons_id__name"]} will use untill {date_only}'
        carry_outward.append(alerts)
    context = {
        "carry": carry_forward,
        "notcarry": carry_outward,
        "remaining_days": add_on_remaining,
    }
    return context


def reducematchcount(user_id, feature):  # need to work on Add-ons
    if feature == "ai_match":
        feature, add_on = 6, 56
    elif feature == "job":
        feature, add_on = 10, 51
    elif feature == "resume":
        feature, add_on = 27, 52
    elif feature == "talent_sourcing":
        feature, add_on = 53, 4
    else:
        feature, add_on = 0, 0
    if client_features_balance.objects.filter(
        client_id=user_id, feature_id=feature
    ).exists():
        reduce = client_features_balance.objects.get(
            client_id=user_id, feature_id=feature
        )
        if reduce.available_count > 0:
            reduce.available_count = int(reduce.available_count) - 1
            reduce.save()
        if reduce.plan_count and reduce.plan_count > 0:
            reduce.plan_count = int(reduce.plan_count) - 1
            reduce.save()
        elif reduce.plan_count == 0:
            if client_features_balance.objects.filter(
                client_id=user_id, feature_id=add_on
            ).exists():
                addon_reduce = client_features_balance.objects.get(
                    client_id=user_id, feature_id=add_on
                )
                addon_reduce.plan_count = int(reduce.plan_count) - 1
                addon_reduce.save()
        success = True
    else:
        success = False
    return success


def AdvancedAIMatching(jd_id, can_id, user, source,sub_user = None):

    matched_data = Matching_AI(jd_id, can_id, user,sub_user=sub_user)
    if matched_data != None:
        if source == "applicants":
            count = reducematchcount(user, "ai_match")
        elif source == "candidates":
            count = candidate_bulk_matching(can_id, jd_id, user)
        else:
            pass
        context = {"success": True, "message": "Matching Completed"}
        return context
    elif matched_data == None:
        context = {
            "error": True,
            "message": "Sorry, there was a problem connecting to the API. Please try again later.",
        }
        return context
    elif matched_data == []:
        context = {
            "error": True,
            "message": "Sorry, there was a problem connecting to the API. Please try again later.",
        }
        return context
    else:
        context = {"success": True, "message": "Matching Completed"}
        return context


def Descriptive_Analaysis(jd_id, can_id, user):
    success = True
    if applicant_descriptive.objects.filter(jd_id=jd_id, candidate_id=can_id).exists():
        applicant_descriptive.objects.filter(jd_id=jd_id, candidate_id=can_id).update(
            is_active=True
        )
    else:
        candidate = employer_pool.objects.get(id=can_id)
        if applicants_status.objects.filter(jd_id=jd_id, candidate_id=can_id).exists():
            applicant_descriptive.objects.create(
                jd_id=JD_form.objects.get(id=jd_id),
                candidate_id=candidate,
                user_id=user,
                is_active=True,
            )
    return success


def update_addons(num):
    if num == "51" or num == 51:
        return 10
    elif num == "52" or num == 52:
        return 27
    elif num == "58" or num == 58:
        return 53
    elif num == "56" or num == 56:
        return 6
    else:
        return 0


from jobs.parsing import weightage_calculation, percentage_matching


def adv_match_calculation(jd_id, can_id, user, request):
    if Weightage_Matching.objects.filter(jd_id=jd_id, user_id=request.user).exists():
        user = request.user
    data = Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id).values(
        "title", "percentage", "description", "jd_id"
    )
    ai_matching = client_features_balance.objects.filter(
        client_id=user, feature_id=62
    ).exists()
    non_tech = [
        "Industry-Specific Experience",
        "Domain-Specific Experience",
        "Certifications",
        "Location Alignment",
        "Cultural Fit",
        "Nice to Have",
    ]
    tech = [
        "Skills",
        "Roles and Responsibilities",
        "Experience",
        "Technical Tools and Languages",
        "Educational Qualifications",
        "Soft Skills",
    ]
    non_technical = []
    technical = []
    try:
        custom_order = [
            "skills",
            "roles",
            "exp",
            "qualification",
            "industry_exp",
            "domain_exp",
            "certification",
            "tech_tools",
            "soft_skills",
            "location",
            "cultural_fit",
            "Nice to Have",
        ]
        score = (
            Weightage_Matching.objects.filter(jd_id=jd_id, user_id=user)
            .values("criteria__title", "score")
            .order_by(
                Case(
                    *[
                        When(criteria__title=title, then=position)
                        for position, title in enumerate(custom_order)
                    ],
                    default=len(custom_order),
                    output_field=IntegerField(),
                )
            )
        )

        # score = Weightage_Matching.objects.filter(jd_id=jd_id,user_id=self.request.user).values("criteria__title","score")
    except Exception as e:
        pass
    nontech = 0
    overall = 0

    for i in data:
        validate = [
            "Industry-Specific Experience",
            "Technical Tools and Languages",
            "Soft Skills",
        ]
        if i["title"] in tech:
            if weightage_calculation(i["title"]) != 12:
                if Weightage_Matching.objects.filter(
                    jd_id=jd_id,
                    user_id=user,
                    criteria=weightage_calculation(i["title"]),
                ).exists():
                    score = Weightage_Matching.objects.get(
                        jd_id=jd_id,
                        user_id=user,
                        criteria=weightage_calculation(i["title"]),
                    ).score
                    i["percentage"] = percentage_matching(i["percentage"], score)
                    i["skill_percentage"] = score
                    overall += i["percentage"]
                    technical.append(i)
        elif i["title"] in non_tech:
            if weightage_calculation(i["title"]) != 12:
                if Weightage_Matching.objects.filter(
                    jd_id=jd_id,
                    user_id=user,
                    criteria=weightage_calculation(i["title"]),
                ).exists():
                    score = Weightage_Matching.objects.get(
                        jd_id=jd_id,
                        user_id=user,
                        criteria=weightage_calculation(i["title"]),
                    ).score
                    i["percentage"] = percentage_matching(i["percentage"], score)
                    i["skill_percentage"] = score
                    nontech += i["percentage"]
                    non_technical.append(i)
    non_technical_order = [
        "Industry-Specific Experience",
        "Domain-Specific Experience",
        "Certifications",
        "Cultural Fit",
        "References and Recommendations",
        "Location Alignment",
        "Nice to Have",
    ]
    technical_order = [
        "Skills",
        "Roles and Responsibilities",
        "Experience",
        "Technical Tools and Languages",
        "Soft Skills",
        "Educational Qualifications",
    ]
    # Matched_percentage.objects.filter(jd_id= jd_id,candidate_id = can_id).update(overall_percentage = overall)
    # Matched_candidates.objects.filter(jd_id=jd_id,candidate_id=can_id).update(profile_match=overall)
    non_technical = sorted(
        non_technical, key=lambda item: non_technical_order.index(item["title"])
    )
    technical = sorted(technical, key=lambda item: technical_order.index(item["title"]))
    context = {
        "technical": technical,
        "non_technical": non_technical,
        "nontech": nontech,
        "overall": overall,
    }
    return context


def addon_interview_question(user_id):
    success = False
    date = datetime.now()
    plan = subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
    plans_checks = [6, 7, 10, 11]
    if plan in plans_checks:
        if client_features_balance.objects.filter(
            client_id=user_id, feature_id=59
        ).exists():
            purchase_date = client_features_balance.objects.get(
                client_id=user_id, feature_id=59
            ).created_at
            # validating = one_month_checking(purchase_date,1)
            date = purchase_date
            success = True
    else:
        success = True
    return success, date


from jobs.models import applicants_list


def resume_exceed(can_id, user_id, jd_id, target):
    if isinstance(user_id, str):
        user_id = User.objects.get(id=user_id)
    if client_features_balance.objects.filter(
        client_id=user_id, feature_id=27
    ).exists():
        count = client_features_balance.objects.get(
            client_id=user_id, feature_id=27
        ).available_count

        if count == 0:
            if jd_id:
                if target == 1:
                    if applicants_list.objects.filter(
                        candidate_id=can_id, jd_id__isnull=True, user_id=user_id
                    ).exists():
                        applicants_list.objects.filter(
                            candidate_id=can_id, jd_id__isnull=True, user_id=user_id
                        ).update(jd_id=JD_form.objects.get(id=jd_id))
                    # elif not applicants_list.objects.filter(candidate_id=can_id,jd_id = jd_id,user_id=user_id).exists():
                    #     applicants_list.objects.create(candidate_id=employer_pool.objects.get(id=can_id),user_id=user_id,jd_id=JD_form.objects.get(id=jd_id))
                # else:
                #     if applicants_list.objects.filter(candidate_id=can_id,user_id=user_id).exists():
                #         applicants_list.objects.filter(candidate_id=can_id).update(jd_id=JD_form.objects.get(id=jd_id))
                #     else:
            if target == 0:
                applicants_list.objects.create(
                    candidate_id=employer_pool.objects.get(id=can_id), user_id=user_id
                )


def remove_duplicate_skills(data):
    try:
        for i in data.keys():
            if isinstance(data[i], list):
                data[i] = [
                    skill
                    for skill in data[i]
                    if skill not in (data["mandatory_skills"] + data["nice_to_have"])
                ]
        return data
    except:
        return data


def utc_to_timezone(time, time_zone):
    if time_zone != "UTC":
        original_time_str = str(time)
        original_time_format = "%Y-%m-%dT%H:%M:%S"
        original_time = datetime.strptime(original_time_str, original_time_format)
        local_tz = pytz.timezone("Asia/Kolkata")
        localized_time = local_tz.localize(original_time)
        utc_tz = pytz.utc
        formatted_time = localized_time.astimezone(utc_tz)
    else:
        formatted_time = time
    return formatted_time


def last_login(utc_timestamp, timezone):
    utc_datetime = datetime.strptime(str(utc_timestamp), "%Y-%m-%d %H:%M:%S.%f%z")
    target_time_zone = pytz.timezone(timezone)
    target_datetime = utc_datetime.astimezone(target_time_zone)
    result_format = "%Y-%m-%dT%H:%M:%S.%f"
    return target_datetime.strftime(result_format)


def event_timings_data(applicants_data, time_zone):
    for can_id in applicants_data:
        candidate_id = can_id["candidate_id_id"]
        events = list(CalEvents.objects.filter(cand_id=candidate_id).values())
        current_time = (
            convert_to_another_timnezone(time_zone, "UTC")
            if time_zone != "UTC"
            else cuurent_tz_format_change()
        )
        max = current_time
        if events != None and events != []:
            timings = []
            for event in events:
                if format_time_change(event["s_time"]) > current_time:
                    s_time = event["s_time"]
                    event_tz = event["timezone"]
                    event["s_time"] = change_timezone_time(s_time, time_zone, event_tz)
                    # if max<event["s_time"]:
                    #     max = event["s_time"]
                    timings.append(event["s_time"])
            current_time = (
                convert_to_another_timnezone(time_zone, "UTC")
                if time_zone != "UTC"
                else cuurent_tz_format_change()
            )
            can_id["event_timings"] = min(timings) if timings else None
        can_id.setdefault("event_timings", None)
    return applicants_data


def coresigna_qualification(highest_qualification):
    education = []
    for x in highest_qualification:
        qual = qualifi_function(x["subtitle"])
        if qual not in education:
            if qual:
                education.append(qual)
    return education


# def qualifi_function(highest_qualification):
#     if highest_qualification:
#         # TODO check this in other places.
#         sentence_split=re.split(r"[',\s_!+]+", highest_qualification)
#         for i  in sentence_split:
#             if i.lower().strip in settings.dip:
#                 return "Diploma"
#             elif i.lower().strip() in settings.ug:
#                 return "Bachelors"
#             elif i.lower().strip() in settings.ug:
#                 return "Bachelor's"
#             elif i.lower().strip() in settings.pg:
#                 return "Masters"
#             elif i.lower().strip() in settings.phd:
#                 return "Doctorate"
#             elif i.lower().strip() in settings.phd:
#                 return "Doctorate"
#             else:
#                 return "Others"
#     return None
def qualifi_function(highest_qualification):
    if highest_qualification:
        # Improved splitting to handle a wider range of delimiters more cleanly
        sentence_split = re.split(r"[',\s_!+]+", highest_qualification)
        for word in sentence_split:
            word = word.lower().strip()
            if word in settings.dip:
                return "Diploma"
            elif word in settings.ug:
                return "Bachelors"
            elif word in settings.pg:
                return "Masters"
            elif word in settings.phd:
                return "Doctorate"

        # Return "Others" only after all words have been checked and no match was found
        return ""


def removing_zita_match(can_id, jd_id):
    if Matched_candidates.objects.filter(jd_id=jd_id, candidate_id=can_id).exists():
        match = Matched_candidates.objects.get(
            jd_id=jd_id, candidate_id=can_id
        ).profile_match
        if round(match) == 0:
            if zita_match_candidates.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).exists():
                zita_match_candidates.objects.filter(
                    jd_id=jd_id, candidate_id=can_id
                ).delete()
    return True


def calculate_weightage(jd_id):
    count = 0
    if Weightage_Matching.objects.filter(jd_id=jd_id).exists():
        values = Weightage_Matching.objects.filter(
            jd_id=jd_id, criteria__in=[7, 8, 9, 10, 11, 13]
        ).values_list("score", flat=True)
        for i in values:
            count += int(i)
    return count


def candidate_filter_location(pk, name):
    if name == "pipeline":
        candidatelocation = (
            applicants_status.objects.filter(jd_id_id=pk)
            .values_list("candidate_id_id", flat=True)
            .distinct()
        )
    elif name == "zitamatch":
        candidatelocation = (
            zita_match_candidates.objects.filter(jd_id_id=pk)
            .values_list("candidate_id_id", flat=True)
            .distinct()
        )
    elif name == "database":
        candidatelocation = (
            employer_pool.objects.filter(client_id_id=pk)
            .values_list("id", flat=True)
            .distinct()
        )
    candidate_location = []
    for data in candidatelocation:
        if employer_pool.objects.filter(
            id=data, candidate_id__isnull=False, location__isnull=False
        ).exists():
            loc = employer_pool.objects.get(id=data).location
        elif employer_pool.objects.filter(id=data, location__isnull=False).exists():
            loc = employer_pool.objects.get(id=data).location
        else:
            loc = None
        if loc not in candidate_location and loc:
            candidate_location.append(loc)
    return candidate_location


def candidate_name_email(pk, name):
    candidatename_mail = []
    if name == "database":
        candidatename = (
            employer_pool.objects.filter(
                client_id_id=pk, email__isnull=False, first_name__isnull=False
            )
            .values_list("id", flat=True)
            .distinct()
        )
    if name == "applicantpipeline":
        candidatename = (
            applicants_status.objects.filter(jd_id_id=pk)
            .values_list("candidate_id_id", flat=True)
            .distinct()
        )
    for data in candidatename:
        if employer_pool.objects.filter(id=data, last_name__isnull=False).exists():
            first_name = employer_pool.objects.get(id=data).first_name
            last_name = employer_pool.objects.get(id=data).last_name
            email = employer_pool.objects.get(id=data).email
            candidateName = first_name + "" + last_name
        elif employer_pool.objects.filter(id=data, last_name__isnull=True).exists():
            email = employer_pool.objects.get(id=data).email
            first_name = employer_pool.objects.get(id=data).first_name
            candidateName = first_name
        else:
            email = None
            candidateName = None
        if candidateName not in candidatename_mail and candidateName:
            candidatename_mail.append(candidateName)
        if email not in candidatename_mail and email:
            candidatename_mail.append(email)
    return candidatename_mail


def postjob_location(pk, name):
    candidate_location = []
    job_id = (
        JD_form.objects.filter(user_id_id=pk, jd_status_id=1)
        .values_list("id", flat=True)
        .distinct()
    )
    for data in job_id:
        if name == "jobtitle":
            job_title = JD_form.objects.get(id=data).job_title
            loc = job_title
        elif name == "joblocation":
            if not JD_locations.objects.filter(jd_id_id=data).exists():
                loc = "Remote"
            else:
                location = JD_locations.objects.get(jd_id_id=data)
                loc = (
                    location.city.name
                    + ", "
                    + location.state.name
                    + ", "
                    + location.country.name
                )
        if loc not in candidate_location and loc:
            candidate_location.append(loc)
    return candidate_location


def string_replace(string):
    if string:
        if "/" in string:
            string = string.replace("/", "")
            return string
        else:
            return string
    else:
        return string


def date_time_format(format):
    event = format[:-1]
    # Parse the corrected datetime string into a datetime object
    datetime_obj = datetime.strptime(event, "%Y-%m-%dT%H:%M:%S.%f")
    # Convert the datetime object to the desired format
    format_time = datetime_obj.strftime("%b %d %Y from %I:%M %p")
    return format_time


def mail_cancelevent_applicant(eventid, comapany_name, full_name):
    can_id = CalEvents.objects.get(eventId=eventid).cand_id
    date_s_time = CalEvents.objects.get(eventId=eventid).s_time
    date_e_time = CalEvents.objects.get(eventId=eventid).e_time
    event_type = CalEvents.objects.get(eventId=eventid).event_type
    summary = formating_summary(date_s_time, date_e_time, event_type)
    date_time = date_time_format(date_s_time)
    mail = employer_pool.objects.get(id=can_id).email
    first_name = employer_pool.objects.get(id=can_id).first_name
    last_name = None
    if not employer_pool.objects.filter(id=can_id).values("last_name"):
        last_name = employer_pool.objects.get(id=can_id).last_name
    htmly = get_template("email_templates/interview_canceled_applicants.html")
    d = {
        "comapany_name": comapany_name,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "date_time": date_time,
    }
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(summary, html_content, "support@zita.ai", [mail])
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = "related"
    image_data = ["twitter.png", "linkedin.png", "youtube.png", "new_zita_white.png"]
    for i in image_data:
        msg.attach(logo_data(i))
    try:
        msg.send()
    except Exception as e:
        pass
    return HttpResponse("Email sent successfully")
    # return None


def mail_cancelevent_interviewer(eventid, comapany_name, full_name):
    can_id = CalEvents.objects.get(eventId=eventid).cand_id
    date_s_time = CalEvents.objects.get(eventId=eventid).s_time
    date_e_time = CalEvents.objects.get(eventId=eventid).e_time
    event_type = CalEvents.objects.get(eventId=eventid).event_type
    summary = formating_summary(date_s_time, date_e_time, event_type)
    date_time = date_time_format(date_s_time)
    mail = CalEvents.objects.get(eventId=eventid).email
    first_name = employer_pool.objects.get(id=can_id).first_name
    last_name = None
    if not employer_pool.objects.filter(id=can_id).values("last_name"):
        last_name = employer_pool.objects.get(id=can_id).last_name
    htmly = get_template("email_templates/interview_canceled_employee.html")

    d = {
        "Comapany_name": comapany_name,
        "first_name": first_name,
        "last_name": last_name,
        "date_time": date_time,
    }
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(summary, html_content, "support@zita.ai", [mail])
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = "related"
    image_data = ["twitter.png", "linkedin.png", "youtube.png", "new_zita_white.png"]
    for i in image_data:
        msg.attach(logo_data(i))
    try:
        msg.send()
    except Exception as e:
        pass
    return HttpResponse("Email sent successfully")


from notifications.signals import notify


def interview_cancel(users, eventId):
    if CalEvents.objects.filter(eventId=eventId).exists():
        event = CalEvents.objects.get(eventId=eventId)  # event_id
        jd_id = event.jd_id  # 3129
        from calendarapp.api import get_date_and_time

        date = event.s_time.split(".")[0].replace("T", " ")
        date1 = get_date_and_time(date, "date")
        job_name = JD_form.objects.get(id=jd_id).job_title
        candi_id = event.cand_id
        if employer_pool.objects.filter(
            id=candi_id, candidate_id__isnull=False
        ).exists():
            emp = employer_pool.objects.get(id=candi_id).candidate_id
            appli_id = emp.application_id
            target = Personal_Info.objects.get(application_id=appli_id)
            data = f"Notice: Your interview for {job_name} on {date1} has been cancelled. Please check your registered email's calendar."
            notify.send(
                users,
                recipient=target.user_id,
                description="Cancellation",
                verb=data,
                action_object=event,
            )
            return Response({"success": True})
    return Response({"success": False})


def formating_summary(start_time, end_time, interview_type):
    # Parse the start and end times
    start_time_obj = format_datetime(start_time)
    end_time_obj = format_datetime(end_time)

    # Format the date and times
    formatted_date = start_time_obj.strftime("%b %d %Y")
    formatted_start_time = start_time_obj.strftime("%I:%M %p")
    formatted_end_time = end_time_obj.strftime("%I:%M %p")

    # Create the message
    message = f"Event Cancelled: {interview_type} on {formatted_date} from {formatted_start_time} to {formatted_end_time}"

    return message


# Function to parse and format datetime
def format_datetime(datetime_str):
    # Ensure the microseconds part has exactly 6 digits
    date_part, microseconds_part = datetime_str.split(".")
    microseconds_part = microseconds_part.ljust(6, "0")[:6]
    corrected_datetime_str = f"{date_part}.{microseconds_part}"

    # Parse the corrected datetime string into a datetime object
    datetime_obj = datetime.strptime(corrected_datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
    return datetime_obj


def automated_notify(jd_id, candidate, user):
    jd_id = JD_form.objects.get(id=jd_id)
    for can in candidate:
        if employer_pool.objects.filter(id=can, candidate_id__isnull=False).exists():
            emp = employer_pool.objects.get(id=can).candidate_id
            appli_id = emp.application_id
            target = Personal_Info.objects.get(application_id=appli_id)
            data = f"You got a new email regarding the {jd_id.job_title}.Please check your registered email inbox."
            notify.send(
                sender=user,
                recipient=target.user_id,
                description="Automated",
                verb=data,
                action_object=jd_id,
            )
    return Response({"success": True})




def get_admin_account(userid):
    if User.objects.filter(id = userid.id).exists():
        admin_user = UserHasComapny.objects.get(user_id=userid.id).company.recruiter_id
        if userid == admin_user:
            return admin_user
        else:
            return admin_user
    else:
        return None
