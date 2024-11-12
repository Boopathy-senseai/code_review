from rest_framework.response import Response
from bulk_upload.views import candidate_notification_upload
from jobs.parsing import *
from jobs.utils import data_conversion, downloaded_analysis_csv, is_category_valid
from schedule_event.views import *
from .forms import *
from login.forms import ProfileUpdateForm
from calendarapp.api.outlook import *
from calendarapp.auth_helper import *
from calendarapp.graph_helper import *
from jobs.models import *
from main.models import *
from payment.models import *
from application.models import *
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseNotModified, HttpResponseRedirect
import json
from calendarapp.utils import get_fullname
from django.contrib.auth import login, authenticate, logout
import os, re, time
from django.shortcuts import render, get_object_or_404, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
import datetime
from login.decorators import *
import requests
from django.db.models import *
from jobs.filters import *
from jobs.views import (
    basic_matching,
    generate_candidate_json,
    generate_jd_json,
    matching_api_to_db,
    remove_case_id,
    applicant_genarate_json,
)
from login.models import *
from users.models import *


from users.serializers import CompanySerializer
from calendarapp.models import *

# global countries_to_be_displayed
countries_to_be_displayed = [
    "USA"
]  # if we need to add more countries, the text should be same as the meta of country table in application
from datetime import timedelta, datetime
from zita import settings

base_dir = settings.BASE_DIR
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Aggregate, CharField, Value
from django.core.exceptions import FieldError
from django.db.models.expressions import Subquery
from django.utils import timezone
import pytz
from collections import Counter
import clamd
import logging
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from collections.abc import Iterable
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import View
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

email_main = settings.EMAIL_HOST_USER
EMAIL_TO = settings.EMAIL_TO
from django.views.decorators.cache import never_cache
import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

# from matplotlib_venn import venn2
import numpy as np
import pandas as pd
import csv
from .utils import *

# from pyresparser import ResumeParser
from django.http import HttpResponse
from django.template.loader import render_to_string
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
logger = logging.getLogger("jobs_api")
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
from base64 import b64decode
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from jobs.views import admin_account, user_permission
from calendarapp.models import Event
from email.mime.image import MIMEImage

candi_id = []
from notifications.signals import notify
from notifications.models import Notification
from django.contrib.staticfiles import finders
from django.http import FileResponse
from itertools import chain, groupby
from jobspipeline.models import *
import csv
from googleapiclient.discovery import build
from striprtf.striprtf import rtf_to_text

from jobs.parsing import *
from jobs.models import *
from application.models import *
from jobs.views import *
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from payment.views import *
from jobs.views import *
from payment.views import *
from jobs.function import *
from .finetune import FT
from .utils import plan_checking

try:
    from weasyprint import HTML
except:
    pass

from zita.settings import *
class YearWeek(Func):
    function = "YEARWEEK"
    template = "%(function)s(%(expressions)s)"
    output_field = IntegerField()


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
    logo=None,
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
    if logo == True:
        image_data = [
            "twitter.png",
            "linkedin.png",
            "youtube.png",
            "new_zita_white.png",
        ]
        for i in image_data:
            msg.attach(logo_data(i))
    msg.mixed_subtype = "related"

    try:
        msg.send()
    except:
        pass


# Initial page load api with basic data


class country(generics.GenericAPIView):
    def get(self, request):
        country_list = []
        country = tmeta_currency_type.objects.all()
        for i in country:
            country_list.append({"value": i.id, "label": i.value})

        return Response(country_list)


class job_post_confirmation(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        user_id, updated_by = admin_account(request)
        jd = JD_form.objects.filter(id=pk)
        import time

        time.sleep(120)
        if email_preference.objects.filter(
            user_id=user_id, stage_id_id=5, is_active=True
        ).exists():
            # try:
            #     result=matching_api_to_db(request,jd_id=pk,can_id=None)
            # except Exception as e:
            #     logger.error("Error in the matching : "+str(e))
            jd = jd.annotate(
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
            zita_match_candidate = zita_match_candidates.objects.filter(
                status_id_id=5,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
                jd_id=jd[0],
            )[:3]
            domain = settings.CLIENT_URL
            zita_match_candidate = zita_match_candidate.annotate(
                image=Subquery(
                    Profile.objects.filter(
                        user_id=OuterRef("candidate_id__candidate_id__user_id")
                    )[:1].values("image")
                ),
                match=Subquery(
                    Matched_candidates.objects.filter(
                        jd_id=OuterRef("jd_id"), candidate_id=OuterRef("candidate_id")
                    )[:1].values("profile_match")
                ),
            )
            career_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
            context = {
                "jd_form": jd[0],
                "zita_match": zita_match_candidate,
                "career_url": career_url,
                "domain": domain,
            }
            email = get_template("email_templates/job_post_confirmation.html")
            email = email.render(context)
            msg = EmailMultiAlternatives(
                "Congratulations!!! Your job has been successfully posted on your career page",
                email,
                settings.EMAIL_HOST_USER,
                ["rajas@zita.ai"],
            )
            msg.attach_alternative(email, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
                "default.jpg",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            for p in zita_match_candidate:
                if p.image != None and p.image != "default.jpg":
                    msg.attach(profile(p.image))
            msg.mixed_subtype = "related"
            msg.send()
        return Response({"success": True})


def logo_data(img):
    with open(finders.find("images/" + img), "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", img)
    return logo


def profile(prof):
    with open(settings.BASE_DIR + "/media/" + prof, "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", prof)
    return logo


class notification(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from datetime import timedelta
        from django.utils import timezone
        from datetime import date

        if self.request.user.is_staff:
            user, updated_by = admin_account(self.request)
        else:
            user = User.objects.get(username=self.request.user).id
        unread = self.request.user.notifications.filter(deleted=0)
        has_permission = user_permission(self.request, "bulkImport_candidates")
        if not has_permission == True:
            unread = unread.exclude(description="bulkimport")
        today_time = date.today()
        end_time = date.today() + timezone.timedelta(days=1)
        end_time = end_time
        yesterday_time = date.today() - timezone.timedelta(days=1)
        yesterday_time_last = yesterday_time + timezone.timedelta(days=1)
        total = self.request.user.notifications.filter(unread=1).count()
        today = unread.filter(timestamp__range=(today_time, end_time))
        yesterday = unread.filter(
            timestamp__range=(yesterday_time, yesterday_time_last)
        )
        others = unread.filter(timestamp__lte=yesterday_time)
        # need to be changed as greaterthan equalto
        evaluation = Questions_Generation.objects.filter(
            attendees=self.request.user.id,
            interview_id__e_time__lte=datetime.now(),
            scorecard__isnull=True,
        ).distinct()
        evaluation = evaluation.values(
            "interview_id",
            "interview_id__event_type",
            "interview_id__e_time",
            "interview_id__s_time",
            "interview_id__applicant",
            "interview_id__cand_id",
            "interview__jd_id",
        ).annotate(count=Count("interview_id"))
        data = {
            "success": True,
            "today": today.values(),
            "yesterday": yesterday.values(),
            "others": others.values(),
            "total_unread": total,
            "total": unread.count(),
            "evaluation": evaluation,
        }
        return Response(data)

    def post(self, request):
        request = self.request
        user = request.user
        pk = request.POST["id"]
        Notification.objects.filter(id=pk).update(unread=0)
        data = {
            "success": True,
        }
        return Response(data)

    def delete(self, request):
        request = self.request
        user = request.user
        user.notifications.all().update(deleted=1, unread=0)
        data = {
            "success": True,
        }
        return Response(data)


class zita_talent_pool_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(self.request)
        has_permission = user_permission(self.request, "talent_sourcing")

        # page permisson check
        if not has_permission == True:
            permission = Permission.objects.filter(user=self.request.user).values_list(
                "codename", flat=True
            )
            return Response({"success": False, "Permission": False})

        permission = Permission.objects.filter(user=self.request.user).values_list(
            "codename", flat=True
        )

        # stripe checkout responce and updating the data
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

        # retrieve data form DB for initial page load
        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=27
            ).available_count
        except:
            source_limit = 0
        try:
            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=53
            ).available_count
        except:
            candi_limit = 0
        location_id = State.objects.filter(country_id=231).values_list("id", flat=True)
        state_list = list(
            State.objects.filter(country_id=231)
            .values_list("name", flat=True)
            .distinct()
        )
        city_list = list(
            City.objects.filter(state_id__in=location_id)
            .values_list("name", flat=True)
            .distinct()
        )
        location = list(set(state_list + city_list))
        context = {
            "show_pop": show_pop,
            "source_limit": source_limit,
            "source_limit": source_limit,
            "permission": list(permission),
            "location": location,
        }
        return Response(context)


# talent pool search data


class zita_talent_pool_search_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(self.request)

        # Search query for RL API
        if len(self.request.GET["keywords"]) > 0:
            print("Pddd--->",pd)
            try:
                countries_states = pd.read_csv(
                    base_dir + "/" + "media/countries_states.csv"
                )
            except:
                countries_states = pd.read_csv(
                    os.getcwd() + "/" + "media/countries_states.csv"
                )
            if (
                self.request.GET["location"].lower()
                in countries_states["state"].to_list()
            ):
                location = "state of " + self.request.GET["location"]
            else:
                location = self.request.GET["location"]

            data = {
                "keywords": self.request.GET["keywords"],
                "partner_user_ref": "zita-" + str(user_id.id),
                "location": location,
                "radius": int(self.request.GET["radius"]),
                "active_within_days": int(self.request.GET["last_active"]),
                "limit": 500,
            }

            data_rl = RL_search_api(data)
            if data_rl:
                for item in data_rl:
                    item["first_name"] = base64.b64encode(
                        item["first_name"].encode()
                    ).decode()
        else:
            data_rl = User.objects.none()

        # retrieve data form DB for access the cards
        try:
            source_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=27
            ).available_count
        except:
            source_limit = 0
        try:
            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=53
            ).available_count
        except:
            candi_limit = 0
        candi_list = employer_pool.objects.filter(
            client_id=user_id, can_source_id=2
        ).values_list("candi_ref_id", flat=True)
        plan = subscriptions.objects.filter(client_id=user_id, is_active=True).values()
        page_count = request.GET.get("pagecount")
        if pagination.objects.filter(user_id=request.user, page_id=6).exists():
            if page_count:
                pagination.objects.filter(user_id=request.user, page_id=6).update(
                    pages=page_count
                )
            page_count = pagination.objects.get(user_id=request.user, page_id=6).pages
        elif not pagination.objects.filter(user_id=request.user, page_id=6).exists():
            page_count = tmete_pages.objects.get(id=6).default_value
        context = {
            "data": data_rl,
            "source_limit": source_limit,
            "pagecount": page_count,
            "candi_limit": candi_limit,
            "plan": list(plan),
            "candi_list": list(candi_list),
        }
        return Response(context)


# bulk unlock and download api for talent pool


class bulk_action_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        sub_user = self.request.user
        user_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        candi_list = request.GET["candi_list"].split(",")

        # bulk download function
        if "download" in request.GET:
            t = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
            with zipfile.ZipFile(
                base_dir + "/media/Candidates_Profiles_" + str(t) + ".zip", "w"
            ) as myzip:
                for i in candi_list:
                    if not i == "false":
                        try:
                            # unlock API call
                            url = (
                                "https://api.resume-library.com/v1/candidate/backfill/view/pdf/"
                                + i
                                + "/all/zita-"
                                + str(user_id.id)
                            )
                            from zita.settings import rl_username,rl_password
                            result = requests.get(
                                url, auth=(rl_username, rl_password)
                            )
                            result = json.loads(result.content)
                            try:
                                data = result["result"]["pages"][0]["content"]
                            except:
                                data = result["result"]["pages"]["content"]
                            byte = b64decode(data, validate=True)

                            # processing the encoded data to file

                            # if byte[0:4] != b"%PDF":
                            #     raise ValueError("Missing the PDF file signature")
                            if employer_pool.objects.filter(
                                candi_ref_id=result["id"]
                            ).exists():
                                name = result["first_name"] + "_" + result["id"]
                            else:
                                name = result["id"]
                            f = open(base_dir + "/media/" + name + ".pdf", "wb")
                            f.write(byte)
                            f.close()
                            myzip.write(
                                base_dir + "/media/" + name + ".pdf", name + ".pdf"
                            )

                        except Exception as e:
                            logger.error("Bulk download file error ---- " + str(e))

            # converting zip file
            myzip.close()
            file = open(
                base_dir + "/media/Candidates_Profiles_" + str(t) + ".zip", "rb"
            )
            response = HttpResponse(file, content_type="application/zip")
            response["Content-Disposition"] = (
                "attachment; filename=Candidates_Profiles_" + str(t) + ".zip"
            )
            domain = get_current_site(request)
            return JsonResponse(
                {
                    "file_path": str(domain)
                    + "/media/Candidates_Profiles_"
                    + str(t)
                    + ".zip"
                }
            )

        # bulk unlock function
        elif "unlock" in request.GET:
            t = datetime.now()
            unlock_can_list = []

            # unlock access validation
            # if not 'manage_account_settings' in permission:
            #     data={'success':'no_permission'}
            #     return JsonResponse(data)
            try:

                source = client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=53
                )
            except:
                data = {"success": "no_count"}
                return JsonResponse(data)

            candi_limit = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=53
            )

            if candi_limit.available_count != None:
                if (
                    candi_limit.available_count == 0
                    or candi_limit.available_count < len(candi_list)
                ):
                    data = {"success": "no_count"}
                    return JsonResponse(data)
            if source.available_count < len(candi_list):
                data = {"success": "no_limit"}
                return JsonResponse(data)
            else:
                source_limit = source.available_count
            if candi_limit.available_count != None:
                if candi_limit.available_count < len(candi_list):
                    data = {"success": "no_limit"}
                    return JsonResponse(data)
            count = 0
            for i in candi_list:
                if not i == "false":

                    try:

                        # unlock API call
                        url = (
                            "https://api.resume-library.com/v1/candidate/backfill/unlock/pdf/"
                            + i
                            + "/all/zita-"
                            + str(user_id.id)
                        )
                        from zita.settings import rl_username,rl_password
                        result = requests.get(
                            url, auth=(rl_username, rl_password)
                        )
                        result = json.loads(result.content)
                        t = datetime.now()
                        try:
                            data = result["result"]["pages"][0]["content"]
                        except:
                            data = result["result"]["pages"]["content"]

                        # processing the encoded data to file
                        byte = b64decode(data, validate=True)
                        # if byte[0:4] != b"%PDF":
                        #     raise ValueError("Missing the PDF file signature")
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
                            job_type = tmeta_job_type.objects.get(
                                label_name=result["job_type"]
                            )
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
                            if (
                                countries_states["state_code"][i]
                                == state.strip().lower()
                            ):
                                state = countries_states["state"][i]
                        location = city + ", " + state.upper()

                        # store data to DB
                        if employer_pool.objects.filter(
                            email=result["email"], client_id=user_id
                        ).exists():
                            employer_pool.objects.filter(email=result["email"]).update(
                                can_source_id=2,
                                client_id=user_id,
                                user_id = sub_user,
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
                                user_id = sub_user,
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
                            str(emp_pool.id)
                            + "@@"
                            + result["first_name"]
                            + "_"
                            + result["id"]
                        )
                        count = count + 1

                    except Exception as e:
                        logger.error("Unlock file Error ---- " + str(e))

            # updating the details in DB
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
                    client_id=user_id, feature_id_id=53
                ).available_count
            except:
                source = 0
            candi_list = employer_pool.objects.filter(
                client_id=user_id, can_source_id=2
            ).values_list("candi_ref_id", flat=True)
            data = {
                "success": True,
                "unlock_can_list": unlock_can_list,
                "candi_list": list(candi_list),
                "source_limit": source,
                "candi_limit": candi_limit,
            }
            return Response(data)
        else:
            return Response(
                {
                    "success": False,
                }
            )


# single unlock candidates


class unlock_candidates_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            request = self.request
            sub_user = self.request.user
            user_id, updated_by = admin_account(request)

            # unlock  validation
            permission = Permission.objects.filter(user=request.user).values_list(
                "codename", flat=True
            )
            # if not 'manage_account_settings' in permission:
            #     data={'success':'no_permission'}
            #     return JsonResponse(data)

            # candi_limit = client_features_balance.objects.get(client_id=user_id,feature_id_id=27)
            # if candi_limit.available_count == 0:
            #     data={'success':'no_count'}
            #     return JsonResponse(data)
            try:
                source_limit = client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=53
                )
            except:
                source_limit = 0
            if source_limit.available_count == 0:
                data = {"success": "no_count"}
                return JsonResponse(data)
            # except:
            #     data={'success':False}
            #     return JsonResponse(data)

            # API call
            candidate_key = request.GET["key"]
            url = (
                "https://api.resume-library.com/v1/candidate/backfill/unlock/pdf/"
                + candidate_key
                + "/all/zita-"
                + str(user_id.id)
            )
            unlock_can_list = []
            from zita.settings import rl_username,rl_password
            result = requests.get(
                url, auth=(rl_username, rl_password)
            )
            result = json.loads(result.content)

            # res=result["result"]["pages"]
            # page_keys =  [i.keys() for i in res]
            if 'pages' not in result["result"]:
                return Response({"success":False,"message":"Resume has no content"})
            
            if 'pages' in result["result"]:
                res=result["result"]["pages"]
                page_keys =  [i.keys() for i in res]
                if not all('content' in keys for keys in page_keys):
                    return Response({"success": False, "message": "Resume has no content"})

            # Data processing
            try:
                data = result["result"]["pages"][0]["content"]
            except:
                data = result["result"]["pages"]["content"]
            byte = b64decode(data, validate=True)
            # if byte[0:4] != b"%PDF":
            #     raise ValueError("Missing the PDF file signature")
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
            # Stroing DB
            if employer_pool.objects.filter(
                email=result["email"], client_id=user_id
            ).exists():
                employer_pool.objects.filter(email=result["email"]).update(
                    can_source_id=2,
                    client_id=user_id,
                    user_id = sub_user,
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
                    skills=", ".join(result["key_skills"]),
                    location=location,
                )
                emp_pool = employer_pool.objects.get(
                    email=result["email"], client_id=user_id
                )
            else:
                employer_pool.objects.create(
                    can_source_id=2,
                    client_id=user_id,
                    user_id = sub_user,
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
                    skills=", ".join(result["key_skills"]),
                    location=location,
                )
                emp_pool = employer_pool.objects.filter(
                    email=result["email"], client_id=user_id
                ).last()
            # update the count in DB
            unlock_can_list.append(
                str(emp_pool.id) + "@@" + result["first_name"] + "_" + result["id"]
            )
            source_limit.available_count = source_limit.available_count - 1
            source_limit.plan_count = source_limit.plan_count - 1
            source_limit.save()
            source_limit = source_limit.available_count
            # if candi_limit.available_count != None:
            #     candi_limit.available_count = candi_limit.available_count -1
            #     candi_limit.save()
            #     candi_limit = candi_limit.available_count
            # else:
            #     candi_limit = "Unlimited"

            UserActivity.objects.create(
                user=request.user,
                action_id=4,
                action_detail="1 candidate from Talent Sourcing",
            )
            candi_list = employer_pool.objects.filter(
                client_id=user_id, can_source_id=2
            ).values_list("candi_ref_id", flat=True)
            data = {
                "success": True,
                "unlock_can_list": unlock_can_list,
                "source_limit": source_limit,
                "candi_list": list(candi_list),
                "candi_limit": 0,
            }
            return Response(data)
        except Exception as e:
            print("Exception",e)
            return Response(
                {"success": False, "message": "Resume Doesnot parsed Correctly"}
            )


# Background parsing API
@api_view(["GET", "POST"])
def parsed_text_api(request):
    try:
        unlock_can_list = request.GET["unlock_can_list"].split(",")
        for i in unlock_can_list:
            emp_pool_id = i.split("@@")[0]
            talent_pool_id = i.split("@@")[1]
            user_id = None
            if employer_pool.objects.filter(id =emp_pool_id).exists():
                user_id = employer_pool.objects.get(id =emp_pool_id).user_id
          
            # Parsing function
            skills = None
            parser_output, raw_text = resume_parsing(str(talent_pool_id) + ".pdf",user_id = user_id)
            
            if isinstance(parser_output.get("Technical skills",None),str):
                t_skills = [parser_output["Technical skills"]]
            else:
                t_skills=parser_output.get("Technical skills",[])

            soft_s = parser_output.get("Soft skills", None)
            if isinstance(soft_s,str):
                soft_s = [soft_s]

            try:
                contact = parser_output.get("Phone number", None)
                if (
                    contact != None
                    and contact != "None"
                    and contact != "NULL"
                    and contact != "null"
                ):
                    contact = parser_output["Phone number"]
                    if isinstance(contact, list):
                        if len(contact) >= 1:
                            contact = contact[0]
                        else:
                            contact = None
                    if "/" in contact:
                        contact = contact.split("/")
                        contact = contact[0]
                    if "," in contact:
                        contact = contact.split(",")
                        contact = contact[0]
                else:
                    contact = (",  ").join(parser_output["Personal"]["Phone"])
            except:
                contact = None
            try:
                LinkedIn = parser_output.get("LinkedIn URL", None)
                if (
                    LinkedIn != None
                    and LinkedIn != "None"
                    and LinkedIn != "NULL"
                    and LinkedIn != "null"
                ):
                    LinkedIn = parser_output["LinkedIn URL"]
                else:
                    LinkedIn = parser_output["Personal"]["LinkedIn"]
            except:
                LinkedIn = None
            #'''<----------------Job Type-------------------->'''
            # jobtype = parser_output.get('Job Type',None)
            # if jobtype and jobtype != "None" and jobtype != '':
            #     try:
            #         if tmeta_job_type.objects.filter(value__exact=jobtype).exists():
            #             jobtype = tmeta_job_type.objects.get(value=jobtype)
            #         else:
            #             jobtype = None
            #     except:
            #         jobtype = None
            # else:
            #     jobtype = None
            try:
                location = parser_output.get("Preferred Location", None)
                if (
                    location != None
                    and location != "None"
                    and location != "NULL"
                    and location != "null"
                ):
                    location = parser_output["Preferred Location"]
            except:
                location = None
            # '''<---------------------Location-------------->'''
            if "Preferred Location" in parser_output:
                location = parser_output["Preferred Location"]
                location = string_checking(parser_output["Preferred Location"])
            else:
                location = parser_output.get("Preferred Location")
                location = string_checking(parser_output.get("Preferred Location"))
            # '''<---------------------Experience-------------->'''
            try:
                exp = parser_output["Total years of Experience"]
                if exp != None:
                    if exp["Years"] != None and exp["Months"] != None:
                        if exp["Years"] != 0 and exp["Months"] != 0:
                            exp = (
                                str(exp["Years"])
                                + " Years"
                                + " "
                                + str(exp["Months"])
                                + " Months"
                            )
                        elif exp["Years"] != 0:
                            exp = str(exp["Years"]) + " Years"
                        elif exp["Years"] == 0:
                            if exp["Months"] != 0:
                                exp = str(exp["Months"]) + " Months"
                            else:
                                exp = None
                        else:
                            exp = None
                    elif (
                        exp["Years"] != None
                        and exp["Months"] == None
                        and exp["Months"] != 0
                    ):
                        exp = str(exp["Years"]) + " Years"
                    elif (
                        exp["Years"] == None
                        and exp["Months"] != 0
                        and exp["Months"] != None
                    ):
                        exp = str(exp["Months"]) + " Months"
                    else:
                        exp = None
                else:
                    exp = None
            except Exception as e:
                exp = None
            # '''<---------------------Qualifications-------------->'''
            qualifi = parser_output.get("Highest Qualification", None)
            qualifi1 = parser_output.get("Highest Qualifications", None)
            qual = None
            if qualifi:
                if "Highest Qualification" in parser_output:
                    qual = get_qualification(parser_output["Highest Qualification"])
            if qualifi1:
                if "Highest Qualifications" in parser_output:
                    qual = get_qualification(parser_output["Highest Qualifications"])

            # if soft_s:
            #     if "Soft skills" in parser_output:
            #         if parser_output.get("Technical skills", None):
            #             parser_output["Technical skills"].extend(
            #                 parser_output["Soft skills"]
            #             )
            if soft_s:
                if "Soft skills" in parser_output:
                    if parser_output.get("Technical skills", None):
                      
                        tech_skills = parser_output["Technical skills"]
                        soft_skills = parser_output["Soft skills"]

                        if isinstance(tech_skills, str):
                            tech_skills = [tech_skills]
                        if isinstance(soft_skills, str):
                            soft_skills = [soft_skills]

                        tech_skills.extend(soft_skills)
                        parser_output["Technical skills"] = tech_skills

            else:
                soft_s = parser_output.get("Soft Skills", None)
                if soft_s:
                    if parser_output.get("Technical skills", None):
                        t_skills = list(t_skills)
                        t_skills.extend(parser_output["Soft Skills"])
            t_skills = list(filter(lambda x: x is not None, set(t_skills)))
            if t_skills:
                skills = ", ".join(t_skills)
            if employer_pool.objects.filter(id=emp_pool_id).exists():
                employer_pool.objects.filter(id=emp_pool_id).update(
                    skills=skills,
                    contact=contact,
                    linkedin_url=LinkedIn,
                    location=location,
                    qualification=qual,
                    work_exp=exp,
                )
            # storing parsed data to DB
            if candidate_parsed_details.objects.filter(
                candidate_id_id=int(emp_pool_id)
            ).exists():
                candidate_parsed_details.objects.filter(
                    candidate_id_id=int(emp_pool_id)
                ).update(
                    candidate_id_id=int(emp_pool_id),
                    parsed_text=json.dumps(parser_output),
                    resume_file_path="unlock/" + str(talent_pool_id) + ".pdf",
                    resume_description=raw_text,
                )
            else:
                candidate_parsed_details.objects.create(
                    candidate_id_id=int(emp_pool_id),
                    parsed_text=json.dumps(parser_output),
                    resume_file_path="unlock/" + str(talent_pool_id) + ".pdf",
                    resume_description=raw_text,
                )
            result = generate_candidate_json(request, pk=int(emp_pool_id))
        data = {"success": True}
    except Exception as e:
        print("Exception While Parsing Unlock Candiate",str(e)  )
        data = {"success": False, ":Error": str(e)}
    return JsonResponse(data)


# Parsing function
def resume_parsing(filename,user_id = None):
    from zita.settings import rp_api_auth_token,rp_api_url
    headers = {"Authorization": rp_api_auth_token}
    url = rp_api_url
    # TODO - checking on Resume_parser_AI
    try:
        files = {
            "resume_file": open(os.getcwd() + "/" + "media/unlock/" + filename, "rb")
        }
    except:
        print('exception')
        files = {"resume_file": open(base_dir + "/" + "media/unlock/" + filename, "rb")}
    # result = requests.post(url, headers = headers, files=files)
    result, count_total, raw_text = resume_parser_AI(
        files["resume_file"].name, files["resume_file"].name,user_id = user_id
    )
    if isinstance(result,str):
        respone_json = json.loads(result)
    else:
        respone_json = result
    try:
        parser_output = respone_json
        raw_text = raw_text
    except Exception as e:
        print('exception for resume parser',e)
        logger.info("Exception" + str(e))
        parser_output = {}
        raw_text = None
    return parser_output, raw_text


# searching api call in RL
def RL_search_api(data):
    print("data@@@@",data)
    try:
        from zita.settings import rl_search_url,rl_username,rl_password
        headers = {"Content-Type": "application/json"}
        result = requests.post(
            rl_search_url,
            json=data,
            headers=headers,
            auth=(rl_username, rl_password),
        )
        result = json.loads(result.content)
        data_rl = result["candidates"]
    except Exception as e:
        print("Except",e)
        data_rl = None
    return data_rl


def parsing_rl(filename):
    from zita.settings import rp_api_auth_token,rp_api_url
    headers = {"Authorization": rp_api_auth_token}

    url = rp_api_url
    try:
        files = {
            "resume_file": open(os.getcwd() + "/" + "media/resume/" + filename, "rb")
        }
    except:

        files = {"resume_file": open(base_dir + "/" + "media/resume/" + filename, "rb")}
    result = requests.post(url, headers=headers, files=files)
    respone_json = json.loads(result.content)

    # AI PARSER
    respone_json, token, raw_text = resume_parser_AI(filename=files["resume_file"].name)

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

    return sentence_list


class url_verification(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        url = request.GET["url"]
        data = {}
        data["success"] = 0
        if career_page_setting.objects.filter(career_page_url=url).exclude(
            recruiter_id=request.user
        ):
            data["success"] = 1
        return Response(data)


# candidate view api for talent pool
@api_view(["GET", "POST"])
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

    result = requests.get(url, auth=("975486", "a4afe1a58d53"))
    result = json.loads(result.content)
    data = result["result"]["pages"][0]["content"]
    byte = b64decode(data, validate=True)
    main_url = request.build_absolute_uri("/")

    # if byte[0:4] != b"%PDF":
    #     raise ValueError("Missing the PDF file signature")
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
        "file": str(main_url) + "media/data.pdf",
        "permission": permission,
        "candidate_key": candidate_key,
        "unlock_status": result["unlock_status"],
    }

    return Response(context)


# from oauth2client.service_account import ServiceAccountCredentials
import httplib2


@api_view(["GET", "POST"])
def google_job_posting(request):

    if request.method == "POST":
        SCOPES = ["https://www.googleapis.com/auth/indexing"]
        ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

        # service_account_file.json is the private key that you created for your service account.
        JSON_KEY_FILE = base_dir + "/job-posting.json"

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            JSON_KEY_FILE, scopes=SCOPES
        )
        http = credentials.authorize(httplib2.Http())

        # Define contents here as a JSON string.
        # This example shows a simple update request.
        # Other types of requests are described in the next step.

        content = """{
          \"url\": \"https://www.app.zita.ai/zitaj_obs/career_job_view/71/AWS%20Engineer\",
          \"type\": \"URL_UPDATED\"
        }"""

        response, content = http.request(ENDPOINT, method="POST", body=content)
        return Response(response)


@api_view(["GET", "POST"])
def what_jobs_posting(request):
    if request.method == "POST":
        pk = request.POST["jd_id"]
        jd_details = JD_form.objects.get(id=pk)
        location = None
        if JD_locations.objects.filter(jd_id_id=pk).exists():
            location = JD_locations.objects.get(jd_id_id=pk)
        user_id, updated_by = admin_account(request)
        company_name = company_details.objects.get(recruiter_id=user_id).company_name
        career_page_url = career_page_setting.objects.get(
            recruiter_id=user_id
        ).career_page_url
        main_url = settings.CLIENT_URL
        data = {}
        data["command"] = "add"
        data["title"] = jd_details.job_title
        data["title"] = jd_details.job_title
        if jd_details.job_type.id in [1, 2, 5, 6]:
            data["job_type"] = "Permanent"
            data["job_status"] = "Full-Time"
        elif jd_details.job_type.id in [3, 4]:
            data["job_type"] = "Contract"
            data["job_status"] = "Part-Time"
        else:
            data["job_type"] = "temporary"
            data["job_status"] = "Part-Time"
        # if jd_details.job_type.id in [1,4,5] :
        # 	data['job_type'] = "Permanent"
        # 	data['job_status'] = "full-time"
        # elif jd_details.job_type.id in [2,3,6,7]:
        # 	# data['job_type'] = jd_details.job_type.label_name
        # 	data['job_type'] = "Any"
        # 	data['job_status'] = "full-time"
        # else:
        # 	data['job_type'] = "Contract"

        # 	data['job_status'] = "full-time"
        # else:
        # 	data['job_type'] = jd_details.job_type.label_name
        # 	data['job_status'] = "full-time"
        a = jd_details.richtext_job_description
        b = str(jd_details.job_id)
        des = (
            '<p style="box-sizing: border-box; margin-bottom: 1rem; padding: 0px; font-family: "Noto Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; color: #000000; background-color: #ffffff;">'
            + "This job_id is :"
            + b
            + "</p>"
            + "\n"
            + a
        )
        # des = "<h4>"+"The job_id is : "+"avita_avita_avita_avita"+"</h4>"+"\r\n"+a
        data["description"] = des
        # data['description'] = jd_details.job_id
        if jd_details.show_sal_to_candidate == True:
            data["salary_from"] = jd_details.salary_min
            data["salary_to"] = jd_details.salary_max
        if location:
            data["location"] = (
                location.country.name
                + ", "
                + location.state.name
                + ", "
                + location.city.name
            )
        data["application_url"] = (
            main_url
            + "/"
            + career_page_url
            + "/career_job_view/"
            + str(jd_details.id)
            + "/"
            + str(jd_details.job_title).replace(" ", "_")
            + "#whatjobs"
        )
        data["company_email"] = request.user.email
        data["company_name"] = company_name
        data["company_name"] = company_name
        data["reference"] = jd_details.job_id
        if jd_details.job_type.id != 3:
            data["salary_type"] = "annum"
        else:
            data["salary_type"] = "hour"
        url = settings.what_jobs_posting_url
        headers = {"x-api-token": settings.what_jobs_token}
        result = requests.post(
            url, headers=headers, files={"data": (None, json.dumps([data]))}
        )
        # try:
        result = json.loads(result.content)
        result = result[0]["response"]

        try:
            external_jobpostings_by_client.objects.get_or_create(
                client_id=user_id,
                ext_jp_site_id_id=2,
                jd_id_id=pk,
                posted_by=request.user.username,
                jobposting_url=result["job_url"],
                job_posting_ref_id=result["job_id"],
            )
        except:
            final_result = {
                "success": True,
                "message": "You are trying to reposted the job. The job already exist in whatjobs",
            }
            return Response(final_result)
        result = {"success": True, "out_data": result}
        # except  Exception as e:
        # 	logger.error("Error in resume-library job posting, Error -- "+str(e)+'JD-ID -- '+str(pk))
        # 	result = {'success':False,"out_data":False}
        return Response(result)


@api_view(["GET", "POST"])
def remove_what_jobs_posting(request):
    pk = request.GET["jd_id"]
    try:
        external_jobs = external_jobpostings_by_client.objects.get(
            jd_id_id=pk, is_active=True, ext_jp_site_id_id=2
        )
    except:
        external_jobs = None
    if external_jobs != None:
        try:
            data = [
                {
                    "job_id": str(external_jobs.job_posting_ref_id),
                    "command": "delete",
                }
            ]
            url = settings.what_jobs_posting_url
            headers = {"x-api-token": settings.what_jobs_token}
            result = requests.post(
                url, headers=headers, files={"data": (None, json.dumps(data))}
            )
            result = json.loads(result.content)
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
        result = {"success": True, "out_data": result}
    else:
        result = {"success": False, "out_data": False}
    return Response(result)


# @api_view(['GET', 'POST'])
# def what_jobs_posting(request):
#     if request.method == 'POST':
#         pk = 95
#         # pk=request.POST['pk']
#         jd_details = JD_form.objects.get(id=pk)
#         location = JD_locations.objects.get(jd_id_id=pk)
#         user_id,updated_by = admin_account(request)
#         company_name=company_details.objects.get(recruiter_id=user_id).company_name
#         career_page_url = career_page_setting.objects.get(recruiter_id=user_id).career_page_url
#         main_url= settings.CLIENT_URL
#         data={}
#         data['command'] = 'add'
#         data['title'] = jd_details.job_title
#         data['title'] = jd_details.job_title
#         if jd_details.job_type.id in [1,4,5] :
#             data['job_type'] = "Permanent"
#             data['job_status'] = "full-time"
#         else:
#             data['job_type'] = jd_details.job_type.label_name
#             data['job_status'] = "full-time"
#         data['description'] = jd_details.richtext_job_description
#         if  jd_details.show_sal_to_candidate == True :
#             data['salary_from'] = jd_details.salary_min
#             data['salary_to'] = jd_details.salary_max

#         data['location'] = location.country.name+', '+location.state.name+', '+location.city.name
#         data['application_url'] = main_url+'/'+career_page_url+'/career_job_view/'+str(jd_details.id)+'/'+str(jd_details.job_title).replace(' ', '_')
#         data['company_email'] = request.user.email
#         data['company_name'] = company_name
#         data['company_name'] = company_name
#         data['reference'] = jd_details.job_id
#         if jd_details.job_type.id != 3:
#             data['salary_type'] = 'annum'
#         else:
#             data['salary_type'] = 'hour'
#         url=settings.what_jobs_posting_url
#         headers = {'x-api-token': settings.what_jobs_token }
#         result=requests.post(url,headers=headers,files={'data':(None, json.dumps([data]))})
#         # try:
#         result=json.loads(result.content)
#         result=result[0]['response']

#         external_jobpostings_by_client.objects.get_or_create(client_id=user_id,
#                     ext_jp_site_id_id=2,
#                     jd_id_id=pk,
#                     posted_by=request.user.username,
#                     jobposting_url=result['job_url'],
#                     job_posting_ref_id=result['job_id']
#                     )
#         result = {'success':True,"out_data":result}
#         # except  Exception as e:
#         # 	logger.error("Error in resume-library job posting, Error -- "+str(e)+'JD-ID -- '+str(pk))
#             # result = {'success':False,"out_data":False}
#     return Response (result)


# @api_view(['GET', 'POST'])
# def remove_what_jobs_posting(request):
#     pk=request.GET['pk']
#     try:
#         external_jobs = external_jobpostings_by_client.objects.get(jd_id_id=pk,is_active=True,ext_jp_site_id_id=2)
#     except:
#         external_jobs=None
#     if external_jobs != None:
#         try:
#             data= [
#             {
#               "job_id": str(external_jobs.job_posting_ref_id),
#               "command": "delete",
#             }
#             ]
#             url=settings.what_jobs_posting_url
#             headers = {'x-api-token': settings.what_jobs_token }
#             result=requests.post(url,headers=headers,files={'data':(None, json.dumps(data))})
#             result=json.loads(result.content)
#         except:
#             logger.error("Error in resume-library job remove, Error -- "+str(e)+'JD-ID -- '+str(pk))
#         external_jobs.is_active=False
#         external_jobs.job_inactivated_on=datetime.now()
#         external_jobs.job_inactivated_by=request.user.username
#         external_jobs.save()
#         result = {'success':True,"out_data":result}
#     else:
#         result = {'success':False,"out_data":False}
#     return Response (result)


class applicants_profile_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        has_permission = user_permission(self.request, "applicants")
        if not has_permission == True:
            permission = Permission.objects.filter(user=self.request.user).values_list(
                "codename", flat=True
            )
            return Response({"success": False, "Permission": False})
        user_id, updated_by = admin_account(self.request)
        can_id = self.request.GET["can_id"]
        if int(self.request.GET["jd_id"]) != 0:
            jd_id = self.request.GET["jd_id"]
        else:
            jd_id = None
        candidate_details = employer_pool.objects.filter(id=can_id)
        jd = JD_form.objects.filter(id=jd_id)
        status_id = None
        # if applicants_status.objects.filter(jd_id_id=jd_id,candidate_id_id=can_id):
        #     status_id=applicants_status.objects.filter(jd_id_id=jd_id,candidate_id_id=can_id).values("stage_id")
        status = tmeta_jd_candidate_status.objects.get(id=1)
        try:
            chatname = (
                str(candidate_details[0].client_id.id)
                + "-"
                + str(candidate_details[0].candidate_id.user_id.id)
            )
        except:
            chatname = ""
        applicants_status.objects.get_or_create(
            candidate_id_id=can_id, client_id=user_id, status_id_id=6
        )
        if jd_id == None:
            jd = None
        else:
            jd = JD_form.objects.filter(id=jd_id).values()[0]
        source = "Career Page"

        if candidate_details[0].candidate_id != None:
            try:
                if jd_id != None:
                    source = applicants_status.objects.get(
                        jd_id_id=jd_id, candidate_id_id=can_id
                    ).source
                else:
                    source = applicants_status.objects.filter(candidate_id_id=can_id)[
                        0
                    ].source
            except:
                source = "Career Page"
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
                created_on=Subquery(
                    applicants_status.objects.filter(
                        candidate_id=can_id, jd_id=jd_id
                    ).values("created_on")
                ),
                interested=Subquery(
                    Candi_invite_to_apply.objects.filter(
                        candidate_id=can_id, jd_id=jd_id
                    )
                    .order_by("-id")[:1]
                    .values("is_interested")
                ),
            )
            if Additional_Details.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).exists():
                total_exp = Additional_Details.objects.filter(
                    application_id=candidate_details[0].candidate_id
                ).values()
            else:
                total_exp = None
            experience = Experiences.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            education = Education.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()

            personalInfo = Personal_Info.objects.filter(
                application_id=candidate_details[0].candidate_id.pk
            ).values(
                "firstname",
                "lastname",
                "email",
                "contact_no",
                "country__name",
                "state__name",
                "city__name",
                "zipcode",
                "Date_of_birth",
                "linkedin_url",
                "career_summary",
                "gender",
                "updated_at",
                "code_repo",
                "visa_sponsorship",
                "remote_work",
                "type_of_job__label_name",
                "available_to_start__label_name",
                "industry_type__label_name",
                "desired_shift__label_name",
                "curr_gross",
                "current_currency",
                "exp_gross",
                "salary_negotiable",
                "current_country__name",
                "current_state__name",
                "current_city__name",
                "current1_country",
                "current2_country",
                "current3_country",
                "relocate",
            )

            project = Projects.objects.filter(
                application_id=candidate_details[0].candidate_id, work_proj_type=False
            ).values()
            ac_project = Projects.objects.filter(
                application_id=candidate_details[0].candidate_id, work_proj_type=True
            ).values()
            skills = Skills.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            fresher = Fresher.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            course = Certification_Course.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values()
            contrib = Contributions.objects.filter(
                application_id=candidate_details[0].candidate_id
            ).values(
                "application_id",
                "contrib_text",
                "contrib_type__label_name",
            )
            questionnaire = applicant_questionnaire.objects.filter(jd_id_id=jd_id)
            questionnaire = questionnaire.annotate(
                answer=Subquery(
                    applicant_answers.objects.filter(
                        qus_id=OuterRef("id"),
                        candidate_id=candidate_details[0].candidate_id,
                    )[:1].values("answer")
                ),
            ).values()
            cover_letter = applicant_cover_letter.objects.filter(
                candidate_id=candidate_details[0].candidate_id,
                jd_id_id=jd_id,
            ).values()
            interested = Candi_invite_to_apply.objects.filter(
                candidate_id=can_id, jd_id=jd_id
            )[:1].values("is_interested")
            context = {
                "applicant": True,
                "success": True,
                "candidate_details": candidate_details.values(),
                "jd_id": jd_id,
                "can_id": can_id,
                "course": course,
                "contrib": contrib,
                "chatname": chatname,
                "source": source,
                "skills": skills,
                "education": education,
                "project": project,
                "questionnaire": questionnaire,
                "ac_project": ac_project,
                "fresher": fresher,
                "cover_letter": cover_letter,
                "total_exp": total_exp,
                "experience": experience,
                "jd": jd,
                "status_id": status_id,
                "personalInfo": personalInfo,
            }
        else:
            candidate_details = candidate_details.annotate(
                file=Subquery(
                    candidate_parsed_details.objects.filter(candidate_id=OuterRef("id"))
                    .order_by("id")[:1]
                    .values("resume_file_path")
                ),
                interested=Subquery(
                    Candi_invite_to_apply.objects.filter(
                        candidate_id=OuterRef("id"), jd_id=jd_id
                    )
                    .order_by("-id")[:1]
                    .values("is_interested")
                ),
                job_type_name=F("job_type__value"),
            )
            context = {
                "success": True,
                "applicant": False,
                "candidate_details": candidate_details.values(),
                "jd_id": jd_id,
                "can_id": can_id,
                "chatname": chatname,
                "source": source,
                "status_id": status_id,
                "jd": jd,
            }
        return Response(context)


class matching_algorithm(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user, updated_by = admin_account(request)
        jd_id = request.GET["pk"]
        matching_api_to_db(request, can_id=None, jd_id=jd_id)
        return Response("True")


class match_alg_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        can_id = request.GET["can_id"]
        jd_id = request.GET["jd_id"]
        overall_output = matching_api_to_db(request, can_id=can_id, jd_id=jd_id)
        return Response(overall_output)


class job_matching_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        can_id = request.GET["can_id"]
        matching_api_to_db(request, can_id=can_id, jd_id=None)
        return Response("True")


class email_label(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user = request.user
        email_id = employer_pool.objects.filter(user_id=user).values("id", "email")
        email_id = email_id.annotate(
            candidate=Exists(employer_pool.objects.filter(id=OuterRef("id")))
        )
        company = UserHasComapny.objects.get(user_id=user).company
        all_users = (
            UserHasComapny.objects.filter(company=company, user__is_active=True)
            .exclude(user=user)
            .values("user")
        )
        users_mail = User.objects.filter(id__in=all_users).values(
            "id", "email", "is_staff"
        )
        if "can_id" in self.request.GET:
            email_id = users_mail.exclude(username=user)
        else:
            email_id = list(chain(email_id, users_mail))

        email_list = [
            {
                "value": i["email"],
                "label": i["email"],
                "id": i["id"],
                "candidate": i.get("candidate"),
            }
            for i in email_id
            if i["email"] is not None
        ]
        if outlook_user_details.objects.filter(client_id=user.id).exists:
            if os.path.exists(
                base_dir
                + "/media/user_bin/outlook_mail/"
                + str(request.user)
                + "_token_outlook.json"
            ):
                try:
                    Outlook.get_token_from_refresh_token_outlook(request)
                    file_path = open(
                        base_dir
                        + "/media/user_bin/outlook_mail/"
                        + str(request.user)
                        + "_token_outlook.json",
                        "r",
                    )
                    temp2 = json.load(file_path)
                    email = (
                        outlook_user_details.objects.filter(client_id=request.user.id)
                        .values_list("email", flat=True)
                        .first()
                    )
                    context = {
                        "data": email_list,
                        "access_token": temp2["access_token"],
                        "email": email,
                        "account": "outlook",
                    }
                    return Response(context)
                except KeyError:
                    pass
                except Exception as e:
                    pass

        if google_user_details.objects.filter(client_id=user.id).exists:
            if os.path.exists(
                base_dir
                + "/media/user_bin/google_mail/"
                + str(request.user)
                + "_token_google.json"
            ):
                authcreds = None
            if Google.auth_token_google_exists(request):
                authcreds = Credentials.from_authorized_user_file(
                    Google.auth_token_google_path(request),
                    Google.SCOPES,
                )
                if not authcreds or not authcreds.valid:
                    if authcreds and authcreds.expired and authcreds.refresh_token:
                        authcreds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            "client_secret.json", Google.SCOPES
                        )
                        authcreds = flow.run_local_server(port=0)
                    with open(
                        Google.auth_token_google_path(request),
                        "w",
                    ) as token:
                        token.write(authcreds.to_json())
                try:
                    service = build("calendar", "v3", credentials=authcreds)
                    file_path = open(
                        base_dir
                        + "/media/user_bin/google_mail/"
                        + str(request.user)
                        + "_token_google.json",
                        "r",
                    )
                    temp2 = json.load(file_path)

                    if google_user_details.objects.filter(client_id=request.user.id):
                        email = google_user_details.objects.filter(
                            client_id=request.user.id
                        ).values("email")
                        email = email[0]
                        email = email["email"]
                    context = {
                        "data": email_list,
                        "access_token": temp2["token"],
                        "email": email,
                        "account": "google",
                    }
                    return Response(context)
                except Exception as e:
                    pass
            context = {
                "data": email_list,
                "access_token": None,
                "email": None,
                "account": None,
            }
            return Response(context)


class applicants_data(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jd_id):
        request = self.request
        pk = jd_id
        user_id, updated_by = admin_account(request)
        todo_stage = Todo_Stages_creation(pk)
        try:
            skill_list = open(base_dir + "/" + "media/skills.csv", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skills.csv", "r")
        skill_list = skill_list.read()
        skill_list = skill_list.split("\n")
        from django.utils import timezone

        today = timezone.now().date
        applicants = applicants_status.objects.filter(jd_id_id=pk)
        jd_list = get_object_or_404(JD_form, id=pk)
        fav = jd_list.favourite.all()
        applicants = (
            applicants.annotate(
                fav=Subquery(fav.filter(id=OuterRef("candidate_id"))[:1].values("id")),
                name=Subquery(
                    applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                        "candidate_id__first_name"
                    )
                ),
                first_name=Subquery(
                    applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                        "candidate_id__first_name"
                    )
                ),
                last_name=Subquery(
                    applicants.filter(candidate_id=OuterRef("candidate_id"))[:1].values(
                        "candidate_id__last_name"
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
                # viewed =Subquery(applicants_status.objects.filter(candidate_id=OuterRef('candidate_id'),client_id=user_id,status_id_id=6)[:1].values('candidate_id__location')),
                total_exp=Subquery(
                    employer_pool.objects.filter(id=OuterRef("candidate_id"))[
                        :1
                    ].values("work_exp")
                ),
                work_exp=Subquery(
                    Additional_Details.objects.filter(
                        application_id=OuterRef("candidate_id__candidate_id")
                    )[:1].values("total_exp_year")
                ),
                work_exp_mon=Subquery(
                    Additional_Details.objects.filter(
                        application_id=OuterRef("candidate_id__candidate_id")
                    )[:1].values("total_exp_month")
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
                viewed=Subquery(
                    applicants_status.objects.filter(
                        candidate_id=OuterRef("candidate_id"), status_id_id=6
                    )[:1].values("status_id__label_name")
                ),
                block_descriptive=Exists(
                    applicant_descriptive.objects.filter(
                        jd_id_id=pk,
                        candidate_id=OuterRef("candidate_id"),
                        is_active=True,
                    )
                ),
                interview_scheduled=Exists(
                    CalEvents.objects.filter(cand_id=OuterRef("candidate_id"))
                ),
                last_stage=Subquery(
                    stages_customization.objects.filter(
                        user_id=user_id, is_compelted=True
                    )[:1].values("stage_id")
                ),
                current_stage=Subquery(
                    pipeline_status.objects.filter(
                        jd_id=OuterRef("jd_id"),
                        candidate_id=OuterRef("candidate_id"),
                        pipeline_id=OuterRef("stage_id"),
                    )
                    .order_by("-id")[:1]
                    .values("stage_id__stage")
                ),
                stage_checking=Subquery(
                    pipeline_status.objects.filter(
                        jd_id=OuterRef("jd_id"),
                        candidate_id=OuterRef("candidate_id"),
                        pipeline_id=OuterRef("stage_id"),
                    )
                    .order_by("-id")[:1]
                    .values("is_active")
                ),
                is_move=Case(
                    When(stage_checking=None, then=True),
                    default=F("stage_checking"),
                    output_field=BooleanField(),
                ),
            )
            .exclude(name__isnull=True)
            .exclude(email__isnull=True)
            .order_by("-created_on")
        )
        # work_exp =employer_pool.objects.filter(candidate_id=OuterRef('candidate_id+'))[:1].values('work_exp'),
        # is_move =  Exists(pipeline_status.objects.filter(jd_id = OuterRef('jd_id'),candidate_id = OuterRef('candidate_id'),pipeline_id = OuterRef('stage_id'),stage_id = F('last_stage')))

        # shortlisted = []
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
        fav_id = False
        if "fav" in request.GET and len(request.GET["fav"]) > 0:
            if request.GET["fav"] == "add":
                fav_id = True
                applicants = applicants.exclude(fav__isnull=True)
        if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
            if "@" in request.GET["candidate"]:
                applicants = applicants.filter(
                    email__icontains=request.GET["candidate"]
                )
            else:
                applicants = applicants.filter(name__icontains=request.GET["candidate"])
        if "location" in request.GET and len(request.GET["location"]) > 0:
            location = request.GET["location"]
            applicants = applicants.filter(location__icontains=location)
        if "StageStatus" in request.GET and len(request.GET["StageStatus"]) > 0:
            StageStatus = request.GET["StageStatus"]
            applicants = applicants.filter(current_stage__icontains=StageStatus)
        if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
            # data_profile = request.GET['work_experience'].split('-')
            # request.GET._mutable = True
            # request.GET['work_min']=data_profile[0]
            # request.GET['work_max']=data_profile[1]
            # applicants=applicants.filter(work_exp__range=(int(request.GET['work_min']), int(request.GET['work_max'])))

            # Updating Work_exp filter
            if request.GET["work_experience"] == "0-1":
                applicants = applicants.filter(
                    Q(candidate_id__work_exp__startswith="0 Years")
                    | Q(candidate_id__work_exp__startswith="0")
                    | Q(candidate_id__work_exp="0-1")
                    | Q(candidate_id__work_exp="1 Year")
                    | Q(candidate_id__work_exp="1 Years")
                )
            elif request.GET["work_experience"] == "10+":
                # data=data.filter(work_exp__in=['More than 10 years','11','12','13','14','15','16','17','18','10+'])
                applicants = applicants.filter(
                    Q(candidate_id__work_exp="10+")
                    | Q(candidate_id__work_exp__startswith="11 Years")
                    | Q(candidate_id__work_exp__startswith="12 Years")
                    | Q(candidate_id__work_exp__startswith="13 Years")
                    | Q(candidate_id__work_exp__startswith="14 Years")
                    | Q(candidate_id__work_exp__startswith="15 Years")
                    | Q(candidate_id__work_exp__startswith="16 Years")
                    | Q(candidate_id__work_exp__startswith="17 Years")
                    | Q(candidate_id__work_exp__startswith="18 Years")
                    | Q(candidate_id__work_exp__startswith="19 Years")
                    | Q(candidate_id__work_exp__startswith="20 Years")
                    | Q(candidate_id__work_exp__startswith="21 Years")
                    | Q(candidate_id__work_exp__startswith="22 Years")
                    | Q(candidate_id__work_exp__startswith="23 Years")
                    | Q(candidate_id__work_exp__startswith="24 Years")
                    | Q(candidate_id__work_exp__startswith="25 Years")
                    | Q(candidate_id__work_exp__startswith="26 Years")
                    | Q(candidate_id__work_exp__startswith="27 Years")
                    | Q(candidate_id__work_exp__startswith="28 Years")
                    | Q(candidate_id__work_exp__startswith="29 Years")
                    | Q(candidate_id__work_exp__startswith="30 Years")

                )
            elif request.GET["work_experience"] == "10-30":
                # data=data.filter(work_exp__in=['More than 10 years','11','12','13','14','15','16','17','18','10+'])
                applicants = applicants.filter(
                    Q(candidate_id__work_exp="10+")
                    | Q(candidate_id__work_exp__startswith="11 Years")
                    | Q(candidate_id__work_exp__startswith="12 Years")
                    | Q(candidate_id__work_exp__startswith="13 Years")
                    | Q(candidate_id__work_exp__startswith="14 Years")
                    | Q(candidate_id__work_exp__startswith="15 Years")
                    | Q(candidate_id__work_exp__startswith="16 Years")
                    | Q(candidate_id__work_exp__startswith="17 Years")
                    | Q(candidate_id__work_exp__startswith="18 Years")
                    | Q(candidate_id__work_exp__startswith="19 Years")
                    | Q(candidate_id__work_exp__startswith="20 Years")
                    | Q(candidate_id__work_exp__startswith="21 Years")
                    | Q(candidate_id__work_exp__startswith="22 Years")
                    | Q(candidate_id__work_exp__startswith="23 Years")
                    | Q(candidate_id__work_exp__startswith="24 Years")
                    | Q(candidate_id__work_exp__startswith="25 Years")
                    | Q(candidate_id__work_exp__startswith="26 Years")
                    | Q(candidate_id__work_exp__startswith="27 Years")
                    | Q(candidate_id__work_exp__startswith="28 Years")
                    | Q(candidate_id__work_exp__startswith="29 Years")
                    | Q(candidate_id__work_exp__startswith="30 Years")
                )
            elif request.GET["work_experience"] == "3-5":
                applicants = applicants.filter(
                    Q(candidate_id__work_exp__startswith="3 Years")
                    | Q(candidate_id__work_exp__startswith="4 Years")
                    | Q(candidate_id__work_exp__startswith="5 Years")
                    | Q(candidate_id__work_exp="3-5")
                )
            elif request.GET["work_experience"] == "1-2":
                # data=data.filter(work_exp__in=['1-2','1','2','1-2 years'])
                applicants = applicants.filter(
                    Q(candidate_id__work_exp__startswith="1 Years ")
                    | Q(candidate_id__work_exp="1-2")
                    | Q(candidate_id__work_exp__startswith="2 Years")
                )
            elif request.GET["work_experience"] == "6-10":
                applicants = applicants.filter(
                    Q(candidate_id__work_exp__startswith="6 Years")
                    | Q(candidate_id__work_exp__startswith="7 Years")
                    | Q(candidate_id__work_exp__startswith="8 Years")
                    | Q(candidate_id__work_exp__startswith="9 Years")
                    | Q(candidate_id__work_exp__startswith="10 Years")
                    | Q(candidate_id__work_exp="6-10")
                )
            else:
                applicants = applicants.filter(
                    candidate_id__work_exp__icontains=request.GET["work_experience"]
                )
        if "profile_view" in request.GET and len(request.GET["profile_view"]) > 0:
            if request.GET["profile_view"] == "1":
                applicants = applicants.exclude(viewed__isnull=True)
            elif request.GET["profile_view"] == "0":
                applicants = applicants.exclude(viewed__isnull=False)
        if "education_level" in request.GET and len(request.GET["education_level"]) > 0:
            education_level = request.GET["education_level"].split(",")
            if "others" in education_level:
                education_level = education_level + [
                    "Professional",
                    "HighSchool",
                    "College",
                    "Vocational",
                    "Certification",
                    "Associates",
                ]
            applicants = applicants.filter(
                reduce(
                    operator.or_,
                    (Q(qualification__icontains=qual) for qual in education_level),
                )
            )
        if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
            skill_match_list = request.GET["skill_match"].split(",")
            applicants = applicants.filter(
                reduce(
                    operator.or_,
                    (Q(skills__icontains=item) for item in skill_match_list),
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
                applicant = applicants.filter(status_id_id=1).order_by("-match")
        else:
            applicant = applicants.filter(status_id_id=1)

        if "sort_shortlisted" in request.GET:
            if len(request.GET.getlist("sort_shortlisted")) > 1:
                request.GET["sort_shortlisted"] = request.GET.getlist(
                    "sort_shortlisted"
                )[0]
            if request.GET["sort_shortlisted"] == "date":
                shortlisted = applicants.filter(status_id_id=2).order_by("-created_on")

            elif request.GET["sort_shortlisted"] == "name":
                shortlisted = applicants.filter(status_id_id=2).order_by("name")

            else:
                shortlisted = applicants.filter(status_id_id=2).order_by("-match")

        else:
            shortlisted = applicants.filter(status_id_id=2)
        if "sort_interviewed" in request.GET:
            if len(request.GET.getlist("sort_interviewed")) > 1:
                request.GET["sort_interviewed"] = request.GET.getlist(
                    "sort_interviewed"
                )[0]
            if request.GET["sort_interviewed"] == "date":
                interviewed = applicants.filter(status_id_id=3).order_by("-created_on")
            elif request.GET["sort_interviewed"] == "name":
                interviewed = applicants.filter(status_id_id=3).order_by("name")
            else:
                interviewed = applicants.filter(status_id_id=3).order_by("-match")
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
                selected = applicants.filter(status_id_id=4).order_by("-match")
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
                rejected = applicants.filter(status_id_id=7).order_by("-match")
        else:
            rejected = applicants.filter(status_id_id=7)
        time_zone = "Asia/Calcutta"
        if "time_zone" in request.GET:
            time_zone = request.GET["time_zone"]
        applicants_data = applicants.values()
        applicants_data = event_timings_data(applicants_data, time_zone)
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.urlencode()
        if os.path.exists(
            base_dir + "/media/user_bin/" + str(request.user.id) + "_token_google.json"
        ):
            f = open(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_google.json",
                "r",
            )
            google = json.load(f)
        else:
            google = None
        if not email_preference.objects.filter(user_id=request.user).exists():
            meta_email = tmeta_email_preference.objects.all()
            for i in meta_email:
                email_preference.objects.create(
                    user_id=request.user, stage_id_id=i.id, is_active=i.is_active
                )
        if os.path.exists(
            base_dir + "/media/user_bin/" + str(request.user.id) + "_token_outlook.json"
        ):
            f = open(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_outlook.json",
                "r",
            )
            outlook = json.load(f)
        else:
            outlook = None
        features, plan = plan_checking(user_id, "resume")
        active_count = client_features_balance.objects.get(
            client_id=user_id, feature_id=27
        ).available_count
        total_resume = employer_pool.objects.filter(
            client_id=user_id, first_name__isnull=False, email__isnull=False
        ).values_list("id", flat=True)
        blocked_resume = (
            applicants_list.objects.filter(user_id=user_id, is_active=True)
            .exclude(jd_id=None)
            .values_list("candidate_id", flat=True)
            .distinct()
        )
        active_resume = (
            employer_pool.objects.filter(
                client_id=user_id, first_name__isnull=False, email__isnull=False
            )
            .values_list("id", flat=True)
            .exclude(id__in=list(blocked_resume))
        )
        disable_resume = len(total_resume) - len(active_resume)
        matching = bulk_matching_user(user_id, pk)
        new_cloumn = applicants_status.objects.filter(
            jd_id=jd_id,
            candidate_id__first_name__isnull=False,
            candidate_id__email__isnull=False,
            stage_id_id=None,
        ).values_list("candidate_id", flat=True)
        ai_matched_count = None
        if client_features_balance.objects.filter(
            client_id=user_id, feature_id=6
        ).exists():
            ai_matched_count = client_features_balance.objects.get(
                client_id=user_id, feature_id=6
            ).available_count
        comparative = client_features_balance.objects.filter(
            client_id=user_id, feature_id=60
        ).exists()
        plan_details = tmeta_plan.objects.filter(
            is_active=True, plan_id__in=[7, 11]
        ).values_list("plan_id", flat=True)
        current_plan = subscriptions.objects.filter(client_id=user_id).last().plan_id.pk

        candidate_location = candidate_filter_location(pk, "pipeline")
        candidate_name_mail = candidate_name_email(pk, "applicantpipeline")
        context = {
            "jd_id": pk,
            "params": params,
            "applicants_list": applicants_data,
            "total_applicant": len(applicants),
            "fav_id": fav_id,
            "google": google,
            "outlook": outlook,
            "active_count": active_count,
            "active_resume": active_resume,
            "matching": matching,
            "disabled_resume": disable_resume,
            "new_apply_count": new_cloumn,
            "plan_details": plan_details,
            "current_plan": current_plan,
            "comparative": comparative,
            "ai_matched_count": ai_matched_count,
            "candidate_location": candidate_location,
            "candidate_name_mail": candidate_name_mail,
        }
        return Response(context)


class matching_analysis(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(self.request)
        can_id = self.request.GET["can_id"]
        jd_id = self.request.GET["jd_id"]
        url = settings.gap_url
        headers = settings.xmp_headers
        try:
            match = Matched_candidates.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id
            ).values()
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
            Matched_candidates.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id
            ).update(profile_match=round(float(data["score"]) * 100))
        except Exception as e:
            logger.error("Error in matching analysis, Error -- " + str(e))
            data = {}
        return Response({"success": True, "data": data, "match": match})


class MessagesAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chatname = self.request.GET["chatname"]
        jd_id = self.request.GET["jd_id"]
        users = User.objects.filter(id__in=chatname.split("-"))
        numbers = chatname.split("-")
        user_id = self.request.user.id
        if User.objects.get(id=user_id).is_staff == 1:
            Message.objects.filter(
                jd_id_id=jd_id, receiver=numbers[0], sender=numbers[1]
            ).exclude(sender=self.request.user).update(is_read=True)
        else:
            Message.objects.filter(
                jd_id_id=jd_id, receiver=numbers[1], sender=numbers[0]
            ).exclude(sender=self.request.user).update(is_read=True)
        result = (
            Message.objects.filter(jd_id_id=jd_id)
            .filter(
                Q(sender=users[0], receiver=users[1])
                | Q(sender=users[1], receiver=users[0])
            )
            .annotate(
                username=F("sender__first_name"),
                last_name=F("sender__last_name"),
                message=F("text"),
                sender_image=Subquery(
                    Profile.objects.filter(user_id=OuterRef("sender"))[:1].values(
                        "image"
                    )
                ),
                receiver_image=Subquery(
                    Profile.objects.filter(user_id=OuterRef("receiver"))[:1].values(
                        "image"
                    )
                ),
            )
            .order_by("date_created")
            .values(
                "username",
                "last_name",
                "message",
                "sender",
                "receiver_image",
                "sender_image",
                "date_created",
            )
        )

        return JsonResponse(list(result), safe=False)


from django.utils import timezone


class candidate_notes(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = self.request.user
        pk = self.request.GET["pk"]
        result = Candidate_notes.objects.filter(candidate_id_id=pk)
        result = result.annotate(
            can_image=Subquery(
                Profile.objects.filter(
                    user_id=OuterRef("candidate_id__candidate_id__user_id")
                )[:1].values("image")
            ),
            emp_image=Subquery(
                Profile.objects.filter(user_id=OuterRef("client_id"))[:1].values(
                    "image"
                )
            ),
            user=Subquery(
                Candidate_notes.objects.filter(client_id=user).values("client_id")[:1]
            ),
        )

        return Response(result.values())

    def post(self, request):
        if "update" in request.POST:
            notes = self.request.POST["notes"]
            pk = self.request.POST["pk"]
            from django.utils import timezone

            Candidate_notes.objects.filter(
                id=pk,
            ).update(notes=self.request.POST["notes"], created_at=timezone.now())
            result = Candidate_notes.objects.filter(candidate_id_id=pk).values()
            return JsonResponse(list(result), safe=False)
        pk = self.request.GET["pk"]
        Candidate_notes.objects.create(
            client_id=self.request.user,
            candidate_id_id=pk,
            notes=self.request.POST["notes"],
            updated_by=str(self.request.user.first_name)
            + " "
            + str(self.request.user.last_name),
        )
        result = Candidate_notes.objects.filter(candidate_id_id=pk).values()
        return JsonResponse(list(result), safe=False)

    def delete(self, request):
        pk = self.request.GET["pk"]
        Candidate_notes.objects.filter(id=pk).delete()
        return JsonResponse({"success": True})


def MailShare(user, candi_id, other_user, company, cand_name, d):
    success = False
    recipient_email = other_user[0]["email"]
    htmly = get_template("notes.html")
    if other_user[0]["last_name"] != None:
        username = other_user[0]["first_name"] + " " + other_user[0]["last_name"]
    else:
        username = other_user[0]["first_name"]
    full_name = user.first_name + " " + user.last_name
    if d.get("update") == 1:
        subject, from_email, to = (
            full_name + " has updated a notes to " + cand_name,
            email_main,
            recipient_email,
        )
    else:
         subject, from_email, to = (
            full_name + " has added a notes to " + cand_name,
            email_main,
            recipient_email,
        )
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    success = True
    msg.mixed_subtype = "related"
    image_data = ["twitter.png", "linkedin.png", "youtube.png", "new_zita_white.png"]
    for i in image_data:
        msg.attach(logo_data(i))
    try:
        msg.send()
    except:
        pass
    return success


class mention_notification_candidate_notes(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user = request.user
        com_name = UserHasComapny.objects.get(user_id=user).company
        name = (
            UserHasComapny.objects.filter(user__is_active=1, company_id=com_name)
            .values(
                "user", "user__first_name", "user__last_name", "company__company_name"
            )
            .exclude(user=user)
        )
        name = name.annotate(
            value=Concat(
                "user__first_name", V(" "), "user__last_name", output_field=CharField()
            )
        )
        context = {"data": name}
        return Response(context)

    def post(self, request):
        user_id, updated_by = admin_account(request)
        request = self.request
        user = request.user
        otheruserid = self.request.POST["otheruserid"]
        otheruserid = [int(x) for x in otheruserid.split(",")]
        notif = self.request.POST["notes"]
        body = self.request.POST["body"]
        first_last_name = User.objects.filter(username=user).values(
            "first_name", "last_name"
        )
        first_last_name = first_last_name.annotate(
            value=Concat("first_name", V(" "), "last_name", output_field=CharField())
        )
        first_last_name = first_last_name[0]["value"]
        if self.request.POST["jd_id"] != "null":
            jd = self.request.POST["jd_id"]
        else:
            jd = 0
        notif = first_last_name.title() + " " + notif
        cand_id = self.request.POST["candidate_id"]
        can_full_name = employer_pool.objects.filter(id=cand_id).values(
            "first_name", "last_name"
        )[0]
        summary = (
            first_last_name + " has added a notes to " + get_fullname(can_full_name)
        )
    
        can_obj = employer_pool.objects.get(id=int(cand_id))
        company = company_details.objects.get(recruiter_id=user_id).company_name
        name = UserHasComapny.objects.filter(company__recruiter_id_id=user_id).exclude(
            user=user
        )
        fullname = user.first_name + " " + user.last_name
        domain = settings.CLIENT_URL
        if -1 in otheruserid:
            for i in name:
                notify.send(
                    user_id,
                    recipient=i.user,
                    description="candidateNotes",
                    verb=notif,
                    target=can_obj,
                )
                e_ml = User.objects.filter(username=i.user).values()
                other_user1 = User.objects.get(username=i.user).first_name
                other_user2 = User.objects.get(username=i.user).last_name
                other_user = other_user1 + " " + other_user2
                if "update" in request.POST:
                    update = 1
                    d = {
                        "user": fullname,
                        "jd_id": jd,
                        "candidate": get_fullname(can_full_name),
                        "notes": body,
                        "company": company,
                        "members": other_user,
                        "candidate_id": cand_id,
                        "domain": domain,
                        "update":update
                    }
                else:
                    d = {
                        "user": fullname,
                        "jd_id": jd,
                        "candidate": get_fullname(can_full_name),
                        "notes": body,
                        "company": company,
                        "members": other_user,
                        "candidate_id": cand_id,
                        "domain": domain,
                        }
                MailShare(user, cand_id, e_ml, company, get_fullname(can_full_name), d)
        elif -2 not in otheruserid and -1 not in otheruserid:
            for i in otheruserid:
                notify.send(
                    user_id,
                    recipient=User.objects.get(id=int(i)),
                    description="candidateNotes",
                    verb=notif,
                    target=can_obj,
                )
                e_ml = User.objects.filter(id=i).values()
                # i = User.objects.get(id=i)
                other_user1 = User.objects.get(id=int(i)).first_name
                other_user2 = User.objects.get(id=int(i)).last_name
                other_user = other_user1 + " " + other_user2
                if "update" in request.POST:
                    update = 1
                    d = {
                        "user": fullname,
                        "jd_id": jd,
                        "candidate": get_fullname(can_full_name),
                        "notes": body,
                        "company": company,
                        "members": other_user,
                        "candidate_id": cand_id,
                        "domain": domain,
                        "update":update
                    }
                else:
                    d = {
                        "user": fullname,
                        "jd_id": jd,
                        "candidate": get_fullname(can_full_name),
                        "notes": body,
                        "company": company,
                        "members": other_user,
                        "candidate_id": cand_id,
                        "domain": domain,
                    }
                MailShare(user, cand_id, e_ml, company, get_fullname(can_full_name), d)
        data = []
        return Response(data)


class Messages_templates(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = self.request.user
        company = UserHasComapny.objects.get(user_id=user).company
        result = UserHasComapny.objects.filter(company=company.id).values_list(
            "user", flat=True
        )
        role = UserHasComapny.objects.get(user_id=user).department.name
        letters = request.GET.get("user")
        tags = tmeta_email_tags.objects.values("name", "tag")
        tags = [{"%s" % item["name"]: "%s" % item["tag"]} for item in tags]
        if letters == "1":
            # Default_template [1,2,3,4]
            default_user = "Zita"
            result1 = tmeta_message_templates.objects.filter(
                user__isnull=True, is_active=1, id__in=[1, 2, 3, 4, 5, 6, 7, 8]
            ).values()

            result1 = result1.annotate(
                jd_id_id=Value(None, output_field=IntegerField()),
                is_edit=Value(False, output_field=BooleanField()),
                full_name=Value(default_user, output_field=CharField()),
            )
            # User Based
            result2 = (
                tmeta_message_templates.objects.filter(user=user)
                .exclude(is_active=0)
                .values()
            )
            result2 = result2.annotate(
                jd_id_id=Value(None, output_field=IntegerField()),
                full_name=Concat(
                    "user__first_name",
                    V(" "),
                    "user__last_name",
                    output_field=CharField(),
                ),
            )
            result = list(chain(result1, result2))
            # result = tmeta_message_templates.objects.filter(user__in=result,jd_id  = None).values()
            # title1=tmeta_message_templates.objects.filter(user__isnull=True,jd_id  = None).values_list('name',flat=True)
            title1 = tmeta_message_templates.objects.filter(
                user__isnull=True
            ).values_list("name", flat=True)
            title2 = tmeta_message_templates.objects.filter(user=user.id).values_list(
                "name", flat=True
            )
            title = list(set(chain(title1, title2)))

        else:
            default_user = "Zita"
            result1 = tmeta_message_templates.objects.filter(
                user__isnull=True, is_active=1, id__in=[1, 2, 3, 4, 5, 6, 7, 8]
            ).values()

            result1 = result1.annotate(
                jd_id_id=Value(None, output_field=IntegerField()),
                is_edit=Value(False, output_field=BooleanField()),
                full_name=Value(default_user, output_field=CharField()),
            )
            result2 = (
                tmeta_message_templates.objects.filter(user=user)
                .exclude(is_active=0)
                .values()
            )
            result2 = result2.annotate(
                jd_id_id=Value(None, output_field=IntegerField()),
                full_name=Concat(
                    "user__first_name",
                    V(" "),
                    "user__last_name",
                    output_field=CharField(),
                ),
            )
            result = list(chain(result1, result2))

            title1 = tmeta_message_templates.objects.filter(
                user__isnull=True
            ).values_list("name", flat=True)
            title2 = tmeta_message_templates.objects.filter(user=user.id).values_list(
                "name", flat=True
            )
            title = list(set(chain(title1, title2)))
            # result = tmeta_message_templates.objects.filter( Q(user__isnull=True) | Q(user__in=result)).values()
            # title=tmeta_message_templates.objects.all().values_list('name',flat=True)
        return Response({"data": result, "role": role, "title": title, "tags": tags})

    def post(self, request):
        user = self.request.user
        id = self.request.POST.get("id", None)
        title = self.request.POST.get("title", None)
        subject = self.request.POST.get("subject", None).strip()
        description = self.request.POST.get("rich_text", None)
        text = self.request.POST.get("text", None)
        IsActive = self.request.POST.get("isactive", None)
        if title and description:
            if tmeta_message_templates.objects.filter(
                user=user, id=id
            ).exists():  # update
                tmeta_message_templates.objects.filter(id=id, jd_id=None).update(
                    templates=description,
                    name=title,
                    templates_text=text,
                    subject=subject,
                    is_active=IsActive,
                )
                name = tmeta_message_templates.objects.get(id=id).name
                # jd_message_templates.objects.filter(message_id=id).update(name=name,templates=description,templates_text =text,subject = subject)

                message = "Email Templates Updated Successfully"

            else:
                if tmeta_message_templates.objects.filter(user=user).count() < 150:
                    if not tmeta_message_templates.objects.filter(name=title).exists():
                        tmeta_message_templates.objects.create(
                            templates=description,
                            name=title.strip(),
                            user=user,
                            templates_text=text,
                            subject=subject,
                            is_active=1,
                        )
                        message = "Email Templates Created Successfully"
                    elif tmeta_message_templates.objects.filter(name=title).exists():
                        message = "Email Templates already exists"
                else:
                    message = "Limits is Exceed"
            if id:
                templateid = id
            elif title:
                templateid = tmeta_message_templates.objects.get(
                    name=title.strip(), user=user
                ).id
            return Response(
                {"success": True, "message": message, "templateid": templateid}
            )
        else:
            return Response({"success": False, "message": "KeyError"})

    def delete(self, request):
        user = self.request.user
        id = self.request.GET.get("id", None)
        admin, updated_by = admin_account(request)
        ids = [1, 2, 3, 4, 5, 6, 7, 8]
        if tmeta_message_templates.objects.filter(id=id).exclude(id__in=ids).exists():
            if user == admin:
                tmeta_message_templates.objects.filter(id=id).delete()
                jd_message_templates.objects.filter(message=id).update(message=None)
                return Response({"success": True, "message": "Deleted Successfully"})
            else:
                if tmeta_message_templates.objects.filter(id=id).exists():
                    tmeta_message_templates.objects.filter(id=id).delete()
                    jd_message_templates.objects.filter(message=id).update(message=None)
                    return Response({"success": True, "message": "Deleted Successfully"})    
                return Response({"success": False, "message": "Admin Can Delete Access"})
        else:
            return Response({"success": False})


class messages_data(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from django.utils import timezone

        chatname = self.request.POST["chatname"]
        jd_id = self.request.POST["jd_id"]
        username = self.request.POST["username"]
        message = self.request.POST["message"]
        users = chatname.split("-")
        if self.request.user.is_staff:

            if company_details.objects.filter(recruiter_id=self.request.user).exists():
                sender = self.request.user
            else:
                sender = UserHasComapny.objects.get(user=self.request.user).company
                sender = sender.recruiter_id
            users.remove(str(sender.id))
            company_name = company_details.objects.get(recruiter_id=sender).company_name
        else:
            users.remove(str(self.request.user.id))
            sender = self.request.user
            company_name = sender.first_name

        receiver = User.objects.get(id=int(users[0]))
        Message(sender=sender, receiver=receiver, text=message, jd_id_id=jd_id).save()
        domain = settings.CLIENT_URL
        if self.request.user.is_staff:
            target_id = User_Info.objects.get(username=receiver).application_id
            if target_id == None:
                if Personal_Info.objects.filter(user_id__username=receiver).exists():
                    target_id = Personal_Info.objects.get(user_id__username=receiver)
            target_id = Personal_Info.objects.get(
                application_id=target_id.application_id
            )
            data = f"You got a new message for the {JD_form.objects.get(id=jd_id).job_title}."
            notify.send(
                self.request.user,
                recipient=target_id.user_id,
                description="CandidateMessage",
                verb=data,
                action_object=JD_form.objects.get(id=jd_id),
            )
        if self.request.user.is_staff:
            try:
                emp_can = employer_pool.objects.get(
                    client_id=self.request.user, candidate_id__user_id=receiver
                )
            except:
                emp_can = None
            user = User_Info.objects.get(user_id=receiver)

            if (
                applicants_status.objects.filter(candidate_id=emp_can, jd_id_id=jd_id)
                .exclude(status_id_id=6)
                .exists()
                == False
            ):
                Candi_invite_to_apply.objects.get_or_create(
                    client_id=self.request.user, candidate_id=emp_can, jd_id_id=jd_id
                )
            htmly = get_template("jobs/message.html")

            # subject, from_email, to = 'You got a message from '+company_name ,settings.EMAIL_HOST_USER, settings.EMAIL_HOST_USER
            subject, from_email, to = (
                "You got a message from " + company_name,
                settings.EMAIL_HOST_USER,
                receiver.email,
            )
            html_content = htmly.render(
                {
                    "sender": sender,
                    "receiver": receiver,
                    "jd_id": jd_id,
                    "user": user,
                    "emp_can": emp_can,
                    "company_name": company_name,
                    "message": message,
                    "domain": domain + "/login_candidate",
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
            try:
                emp_can = employer_pool.objects.get(
                    client_id=receiver, email=sender.email
                )
            except:
                emp_can = None
            subject, from_email, to = (
                "You got a message from " + company_name,
                settings.EMAIL_HOST_USER,
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
            image_data = [
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            msg.send()
            data = "You got a message from " + str(sender.first_name.title())
            jd = JD_form.objects.get(id=jd_id)
            notify.send(
                receiver,
                recipient=receiver,
                description="messages",
                verb=data,
                target=emp_can,
                action_object=jd,
            )
        return Response(
            {
                "success": True,
            }
        )


class show_all_match(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pk = self.request.GET["pk"]
        user_id, updated_by = admin_account(self.request)
        jd_list = JD_form.objects.filter(
            user_id=user_id, jd_status_id__in=[1]
        ).values_list("id", flat=True)
        match = Matched_candidates.objects.filter(candidate_id_id=pk, jd_id__in=jd_list)
        applicant = applicants_status.objects.filter(
            candidate_id_id=pk, jd_id__in=jd_list
        )
        candidate_id = get_object_or_404(employer_pool, id=pk)
        fav = candidate_id.favourite.all()
        match = match.annotate(
            applicant=Subquery(
                applicant.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )[:1].values("id")
            ),
            invited=Subquery(
                Candi_invite_to_apply.objects.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )[:1].values("created_at")
            ),
            jd_title=Subquery(
                JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_title")
            ),
            job_id=Subquery(
                JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_id")
            ),
            fav=Subquery(fav.filter(id=OuterRef("jd_id"))[:1].values("id")),
            interested=Subquery(
                Candi_invite_to_apply.objects.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )
                .order_by("-id")[:1]
                .values("is_interested")
            ),
        )
        applicant = applicant.annotate(
            invited=Subquery(
                Candi_invite_to_apply.objects.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )[:1].values("created_at")
            ),
            match=Subquery(
                match.filter(
                    candidate_id=OuterRef("candidate_id"), jd_id=OuterRef("jd_id")
                )[:1].values("profile_match")
            ),
            jd_title=Subquery(
                JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_title")
            ),
            job_id=Subquery(
                JD_form.objects.filter(id=OuterRef("jd_id"))[:1].values("job_id")
            ),
            fav=Subquery(fav.filter(id=OuterRef("jd_id"))[:1].values("id")),
        ).exclude(match__isnull=False)
        context = {
            "match": match.values(),
            "applicant": applicant.values(),
        }
        return Response(context)


class invite_to_apply(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        jd_id = self.request.POST["jd_id"]
        candidate_id = self.request.POST["candi_id"]
        user_id, updated_by = admin_account(self.request)
        from django.utils import timezone

        target_id = employer_pool.objects.get(id=candidate_id)
        if target_id.candidate_id != None:
            jd_details = JD_form.objects.get(id=jd_id)
            try:
                target_data = User_Info.objects.get(
                    application_id=target_id.candidate_id
                )
            except:
                target_data = Personal_Info.objects.get(
                    application_id=target_id.candidate_id.application_id
                )
            data = f"You've been invited to apply for the {JD_form.objects.get(id=jd_id).job_title } position!"
            notify.send(
                user_id,
                recipient=target_data.user_id,
                description="InviteToApply",
                verb=data,
                action_object=jd_details,
            )
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
        if candidate_details.candidate_id != None:
            user = User_Info.objects.get(user_id=candidate_details.candidate_id.user_id)
        else:
            user = None

        company_detail = company_details.objects.get(recruiter_id=user_id).company_name
        url = career_page_setting.objects.get(recruiter_id=user_id).career_page_url
        htmly = get_template("email_templates/invite_to_apply.html")
        current_site = settings.CLIENT_URL
        # subject, from_email, to = 'Job Notification: An employer invitation to ‘Apply for a Job’',email_main, email_main
        subject, from_email, to = (
            "Job Notification: An employer invitation to ‘Apply for a Job’",
            email_main,
            candidate_details.email,
        )
        jobtitle = jd_id.job_title.replace(" ", "-")
        html_content = htmly.render(
            {
                "jd_id": jd_id,
                "url": url,
                "loc": loc,
                "user": user,
                "match": match,
                "qual": qual,
                "detail": detail,
                "current_site": current_site,
                "company_detail": company_detail,
                "candidate_details": candidate_details,
                "job_pool": jd_id,
                "jobtitle": jobtitle,
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
            user=self.request.user,
            action_id=5,
            action_detail='"'
            + str(candidate_details.first_name)
            + '" for the job id: '
            + str(jd_id.job_id),
        )
        from django.utils import timezone

        data = {"success": True, "date": timezone.now().date().strftime("%b %d,  %Y")}
        return Response(data)


class applicant_status(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        try:
            user_id, updated_by = admin_account(request)
            jd_id = int(self.request.GET["jd_id"])
            can_id = int(self.request.GET["candi_id"])
            can_id = employer_pool.objects.get(id=can_id)
            invite = Candi_invite_to_apply.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id
            ).values()
            stage_data = applicants_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).values(
                "id",
                "jd_id",
                "stage_id",
                "stage_id__stage_name",
                "stage_id__stage_color",
                "candidate_id",
                "client_id",
                "id",
                "created_on",
                "updated_by",
            )[
                :1
            ]
            stage_list = (
                applicants_screening_status.objects.filter(
                    jd_id=jd_id, candidate_id=can_id
                )
                .values(
                    "id",
                    "jd_id",
                    "stage_id",
                    "stage_id__stage_name",
                    "stage_id__stage_color",
                    "candidate_id",
                    "client_id",
                    "id",
                    "created_on",
                    "updated_by",
                )
                .exclude(stage_id=None)
                .distinct()
            )
            stage_list = stage_list.annotate(
                last_stage=Subquery(
                    stages_customization.objects.filter(
                        user_id=user_id, is_compelted=True
                    )[:1].values("stage_id")
                ),
                current_stage=Subquery(
                    pipeline_status.objects.filter(
                        jd_id=OuterRef("jd_id"),
                        candidate_id=OuterRef("candidate_id"),
                        pipeline_id=OuterRef("stage_id"),
                    )
                    .order_by("-id")[:1]
                    .values("stage_id__stage")
                ),
                stage_checking=Subquery(
                    pipeline_status.objects.filter(
                        jd_id=OuterRef("jd_id"),
                        candidate_id=OuterRef("candidate_id"),
                        pipeline_id=OuterRef("stage_id"),
                    )
                    .order_by("-id")[:1]
                    .values("is_active")
                ),
                is_completed=Case(
                    When(stage_checking=None, then=True),
                    default=F("stage_checking"),
                    output_field=BooleanField(),
                ),
            )
            updated_stage_data = []

            for data in stage_data:
                data["stage_id__stage_name"] = "Applied"
                data["stage_id__stage_color"] = "#581845"
                updated_stage_data.append(data)
            merged_values = updated_stage_data + list(stage_list)
            # if len(stage_list) > 0:
            #     stage_list = stage_list
            # else:
            #     applied_date = applicants_status.objects.get(candidate_id= can_id).created_on
            #     stage_list= [
            #                     {
            #                         "id": 1046,
            #                         "jd_id": 1337,
            #                         "stage_id": 536,
            #                         "stage_id__stage_name": "applicant",
            #                         "stage_id__stage_color": "#80C0D0",
            #                         "candidate_id": str(can_id.id),
            #                         "client_id": 325,
            #                         "created_on": applied_date,
            #                         "updated_by": "Reshma K"
            #                     }
            #                 ]
            data = {
                "data": merged_values,
                "invite": invite,
            }
            return Response(data)
        except Exception as e:
            logger.error("Error in applicant_status retrieve , Error -- " + str(e))
            return Response({"success": False})

    def post(self, request):
        try:
            jd_id = self.request.POST["jd_id"]
            can_id = self.request.POST["candi_id"]
            user_id, updated_by = admin_account(self.request)
            applicants_status.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=1
            ).update(status_id_id=2)
            applicants_screening_status.objects.get_or_create(
                jd_id_id=jd_id, candidate_id_id=can_id, status_id_id=2
            )
            time = timezone.now().strftime("%b %d,  %Y")
            return Response({"data": time, "success": True})
        except Exception as e:
            logger.error("Error in applicant_status update , Error -- " + str(e))
            return Response({"success": False})


class scorecard(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        try:
            user = self.request.user
            jd_id = self.request.POST["jd_id"]
            can_id = self.request.POST["can_id"]
            rating = self.request.POST["rating"]
            interview_id = self.request.POST.get("interview_id", None)
            if interview_id:
                interview = CalEvents.objects.get(id=interview_id)
            comments = None
            if "comments" in self.request.POST:
                comments = self.request.POST["comments"]
            id = 0
            if "id" in self.request.POST:
                id = self.request.POST["id"]
            if "edit" in request.POST:
                edit = True
            else:
                edit = None
            if "rating" in self.request.POST:
                rating = rating
            else:
                rating = 0
            rating1 = self.request.POST.get("rating1", 0)
            rating2 = self.request.POST.get("rating2", 0)
            rating3 = self.request.POST.get("rating3", 0)
            rating4 = self.request.POST.get("rating4", 0)
            rating5 = self.request.POST.get("rating5", 0)
            overall_percentage = self.request.POST.get("roundedValues", 0)
            if interview_scorecard.objects.filter(
                jd_id_id=jd_id,
                candidate_id_id=can_id,
                user=user,
                interview_id=interview_id,
            ).exists():
                interview_scorecard.objects.filter(
                    jd_id_id=jd_id,
                    candidate_id_id=can_id,
                    user=user,
                    interview_id=interview_id,
                ).update(rating=rating, comments=comments)
                score_categories.objects.filter(
                    jd_id_id=jd_id,
                    candidate_id_id=can_id,
                    user=user,
                    interview_id=interview_id,
                ).update(
                    rating1=rating1,
                    rating2=rating2,
                    rating3=rating3,
                    rating4=rating4,
                    rating5=rating5,
                    overall_percentage=overall_percentage,
                )
            else:
                interview_scorecard.objects.create(
                    jd_id_id=jd_id,
                    candidate_id_id=can_id,
                    rating=rating,
                    comments=comments,
                    user=user,
                    interview_id=interview,
                )
                score_categories.objects.create(
                    jd_id_id=jd_id,
                    candidate_id_id=can_id,
                    user=user,
                    rating1=rating1,
                    rating2=rating2,
                    rating3=rating3,
                    rating4=rating4,
                    rating5=rating5,
                    overall_percentage=overall_percentage,
                    interview_id=interview,
                )
            interview = (
                interview_scorecard.objects.filter(
                    jd_id_id=jd_id, candidate_id_id=can_id
                )
                .values()
                .distinct()
            )
            return Response({"success": True, "interview": interview})
        except Exception as e:
            logger.error("Error in scorecard update , Error -- " + str(e))
            return Response({"success": False})

    def get(self, request):
        try:
            user = self.request.user
            jd_id = self.request.GET["jd_id"]
            can_id = self.request.GET["can_id"]
            interview = interview_scorecard.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id
            )
            interview = interview.annotate(
                img_name=Subquery(
                    Profile.objects.filter(user=OuterRef("user"))[:1].values("image")
                ),
                first_name=Subquery(
                    interview_scorecard.objects.filter(user=OuterRef("user"))[
                        :1
                    ].values("user__first_name")
                ),
                last_name=Subquery(
                    interview_scorecard.objects.filter(user=OuterRef("user"))[
                        :1
                    ].values("user__last_name")
                ),
                rating1=Subquery(
                    score_categories.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, user=OuterRef("user")
                    )[:1].values("rating1")
                ),
                rating2=Subquery(
                    score_categories.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, user=OuterRef("user")
                    )[:1].values("rating2")
                ),
                rating3=Subquery(
                    score_categories.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, user=OuterRef("user")
                    )[:1].values("rating3")
                ),
                rating4=Subquery(
                    score_categories.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, user=OuterRef("user")
                    )[:1].values("rating4")
                ),
                rating5=Subquery(
                    score_categories.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, user=OuterRef("user")
                    )[:1].values("rating5")
                ),
                overall_percentage=Subquery(
                    score_categories.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, user=OuterRef("user")
                    ).values("overall_percentage")[:1]
                ),
            )
            rating = score_categories.objects.filter(
                jd_id_id=jd_id, candidate_id_id=can_id
            ).aggregate(overall=Sum(F("overall_percentage")))
            overall = None
            if (
                interview_scorecard.objects.filter(candidate_id_id=can_id, jd_id=jd_id)
                .values("user")
                .count()
                > 0
                and rating["overall"] != None
            ):
                user_count = (
                    interview_scorecard.objects.filter(candidate_id_id=can_id)
                    .values("user")
                    .exclude(user=None)
                    .count()
                )
                overall = rating["overall"] / user_count

            cumulative = score_categories.objects.filter(
                candidate_id_id=can_id, jd_id=jd_id
            ).values(
                "candidate_id_id",
                "jd_id_id",
                "user_id",
                "rating1",
                "rating2",
                "rating3",
                "rating4",
                "rating5",
                "overall_percentage",
                "created_at",
                "interview_id",
                "interview_id__event_type",
                "interview_id__s_time",
                "interview_id__e_time",
                "interview_id__org_id",
                "interview_id__addon",
            )
            cumulative = cumulative.annotate(
                commands=Subquery(
                    interview_scorecard.objects.filter(
                        jd_id=jd_id,
                        candidate_id=can_id,
                        user=OuterRef("user_id"),
                        interview_id=OuterRef("interview_id"),
                    ).values("comments")[:1]
                ),
                first_name=Subquery(
                    User.objects.filter(id=OuterRef("user_id")).values("first_name")[:1]
                ),
                last_name=Subquery(
                    User.objects.filter(id=OuterRef("user_id")).values("last_name")[:1]
                ),
                full_name=ExpressionWrapper(
                    Case(
                        When(
                            last_name__isnull=False,
                            then=Concat(F("first_name"), Value(" "), F("last_name")),
                        ),
                        default=F("first_name"),
                        output_field=CharField(),
                    ),
                    output_field=CharField(),
                ),
            )
            result = cumulative.aggregate(
                total_avg=ExpressionWrapper(
                    Sum(F("overall_percentage") / Value(cumulative.count())),
                    output_field=FloatField(),
                )
            )

            return Response(
                {
                    "interview": interview.values(),
                    "overall": overall,
                    "user": user.id,
                    "cumulative": cumulative,
                    "result": result,
                }
            )
        except Exception as e:
            logger.error("Error in scorecard retrieve , Error --" + str(e))
            return Response({"Success": False})


class message_non_applicants(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        try:
            user_id, updated_by = admin_account(self.request)
            jd_id = self.request.POST["jd_id"]
            can_id = self.request.POST["can_id"]
            candidate_details = employer_pool.objects.filter(
                id=can_id, client_id=user_id
            )
            Message_non_applicants.objects.create(
                sender=user_id,
                receiver_id=can_id,
                jd_id_id=jd_id,
                text=self.request.POST["message"],
            )
            Candi_invite_to_apply.objects.get_or_create(
                jd_id_id=jd_id, candidate_id_id=can_id, client_id=user_id
            )
            candidate = employer_pool.objects.get(id=can_id).email
            htmly = get_template("jobs/Message_non_applicants.html")
            domain = settings.CLIENT_URL
            company_name = company_details.objects.get(
                recruiter_id=user_id
            ).company_name
            subject, from_email, to = (
                "You got a message from " + company_name,
                settings.EMAIL_HOST_USER,
                candidate,
            )
            html_content = htmly.render(
                {
                    "sender": user_id,
                    "receiver": candidate_details[0],
                    "company_name": company_name,
                    "message": self.request.POST["message"],
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
        except Exception as e:
            logger.error("Error in message non applicants update , Error -- " + str(e))
            return Response({"success": False})

    def get(
        self,
        request,
    ):
        try:
            user_id, updated_by = admin_account(self.request)
            jd_id = self.request.GET["jd_id"]
            can_id = self.request.GET["can_id"]
            result = (
                Message_non_applicants.objects.filter(
                    sender_id=user_id.id, receiver_id=can_id, jd_id_id=jd_id
                )
                .annotate(
                    username=F("sender__first_name"),
                    last_name=F("sender__last_name"),
                    message=F("text"),
                )
                .order_by("date_created")
                .values("username", "last_name", "message", "sender", "date_created")
            )
            return JsonResponse(list(result), safe=False)
        except Exception as e:
            logger.error(
                "Error in message non applicants retrieve , Error -- " + str(e)
            )
            return Response({"success": False})


class calender_event(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        try:
            can_id = self.request.GET["can_id"]
            candidate_details = employer_pool.objects.get(id=can_id)
            # google=google_return_details.objects.filter(client_id=self.request.user).values()
            # outlook = outlook_return_details.objects.filter(client_id=self.request.user).values()
            event = Event.objects.filter(
                user=self.request.user, attendees__icontains=candidate_details.email
            ).values()
            if os.path.exists(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_google.json"
            ):
                f = open(
                    base_dir
                    + "/media/user_bin/"
                    + str(request.user.id)
                    + "_token_google.json",
                    "r",
                )
                google = json.load(f)
            else:
                google = []

            if os.path.exists(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_outlook.json"
            ):
                f = open(
                    base_dir
                    + "/media/user_bin/"
                    + str(request.user.id)
                    + "_token_outlook.json",
                    "r",
                )
                outlook = json.load(f)
            else:
                outlook = []

            context = {
                "google": google,
                "event": event,
                "outlook": outlook,
            }

            return Response(context)
        except Exception as e:
            logger.error("Error in calender event retrieve , Error -- " + str(e))
            return Response({"success": False})


class applicants_pipline(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jd_id):
        try:

            has_permission = user_permission(self.request, "applicants")
            if not has_permission == True:
                permission = Permission.objects.filter(
                    user=self.request.user
                ).values_list("codename", flat=True)
                return Response({"success": True, "Permission": False})
            request = self.request
            pk = jd_id
            user_id, updated_by = admin_account(request)
            permission = Permission.objects.filter(user=request.user).values_list(
                "codename", flat=True
            )
            try:
                skill_list = open(base_dir + "/" + "media/skill_dict.json", "r")
            except:
                skill_list = open(os.getcwd() + "/" + "media/skill_dict.json", "r")
            skill_list = json.load(skill_list)

            # result=matching_api_to_db(request,jd_id=pk,can_id=None)
            zita_match_count = zita_match_candidates.objects.filter(
                jd_id_id=pk,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
            ).count()
            job_details = JD_form.objects.filter(id=pk).annotate(
                country=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "country_id__name"
                    )[:1]
                ),
                state=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "state_id__name"
                    )[:1]
                ),
                city=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "city_id__name"
                    )[:1]
                ),
            )
            context = {
                "success": True,
                "skill_list": skill_list,
                "zita_match_count": zita_match_count,
                "jd_id": pk,
                "job_details": job_details.values(
                    "country",
                    "job_title",
                    "job_role__label_name",
                    "job_id",
                    "state",
                    "city",
                    "work_space_type",
                )[0],
                "permission": permission,
            }
            return Response(context)
        except Exception as e:
            logger.error("Error in applicants pipline retrieve , Error -- " + str(e))
            return Response({"success": False})


class update_status(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, jd_id):
        try:
            request = self.request
            pk = jd_id

            user_id, updated_by = admin_account(request)

            status = 1
            jd_id = JD_form.objects.get(id=pk)
            applicant_update = applicants_status.objects.get(
                id=request.GET["update_id"]
            )
            if request.GET["status"] == "new_applicants":
                status = 1
            elif request.GET["status"] == "shortlisted":
                status = 2
                UserActivity.objects.create(
                    user=request.user,
                    action_id=6,
                    action_detail='"'
                    + str(applicant_update.candidate_id.first_name)
                    + '" for the job id: '
                    + str(jd_id.job_id),
                )
            elif request.GET["status"] == "interviewed":
                status = 3
            elif request.GET["status"] == "offered":
                status = 4
                UserActivity.objects.create(
                    user=request.user,
                    action_id=7,
                    action_detail='"'
                    + str(applicant_update.candidate_id.first_name)
                    + '" for the job id: '
                    + str(jd_id.job_id),
                )
            elif request.GET["status"] == "rejected":
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
            return Response({"success": True})
        except Exception as e:
            logger.error(
                "Error in applicants update status api update , Error -- " + str(e)
            )
            return Response({"success": False})


class favourite(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        jd = self.request.GET["jd_id"]
        pk = self.request.GET["can_id"]
        jd_id = get_object_or_404(JD_form, id=jd)
        candidate_id = get_object_or_404(employer_pool, id=pk)

        data = {"success": False}
        if candidate_id.favourite.filter(id=jd_id.pk).exists():
            candidate_id.favourite.remove(jd_id)

        else:
            candidate_id.favourite.add(jd_id)
            data["success"] = True
        return JsonResponse(data)


from .models import *


class zita_match(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        has_permission = user_permission(self.request, "zita_match_candidate")
        if not has_permission == True:
            permission = Permission.objects.filter(user=self.request.user).values_list(
                "codename", flat=True
            )
            return Response({"success": False, "Permission": False})
        request = self.request
        pk = self.request.GET["jd_id"]
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        try:
            skill_list = open(base_dir + "/" + "media/skill_dict.json", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skill_dict.json", "r")
        skill_list = json.load(skill_list)
        user = User.objects.get(username=request.user).id
        logger.info("In function shorlist_candidates - User ID: " + str(user))
        jd_state = JD_locations.objects.filter(jd_id_id=pk).values_list(
            "state_id", flat=True
        )
        job_details = (
            JD_form.objects.filter(id=pk)
            .annotate(
                profile=Subquery(
                    JD_profile.objects.filter(jd_id=OuterRef("id")).values(
                        "recommended_role_id__label_name"
                    )[:1]
                ),
                country=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "country__name"
                    )[:1]
                ),
                state=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "state_id__name"
                    )[:1]
                ),
                city=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "city_id__name"
                    )[:1]
                ),
            )
            .values(
                "country",
                "job_title",
                "work_space_type",
                "job_id",
                "profile",
                "state",
                "city",
            )[0]
        )
        location = JD_locations.objects.filter(jd_id_id=pk).values_list(
            "state_id__name"
        )
        data = request.GET
        # matching_api_to_db(request, jd_id=pk,can_id=None)
        applicants_count = applicants_status.objects.filter(jd_id_id=pk).count()
        admin_id, updated_by = admin_account(request)
        matching = bulk_matching_user(admin_id, pk)
        context = {
            "success": True,
            # 'skill_list':skill_list,
            "applicants_count": applicants_count,
            "jd_id": pk,
            "job_details": job_details,
            "bulk_matching": matching,
        }
        return Response(context)


class matching_process(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        status = False
        if "jd_id" in request.GET:
            jd_id = request.GET["jd_id"]
            loader_object = matching_loader.objects.filter(jd_id=jd_id).first()
            if loader_object:
                if loader_object.initial_count == loader_object.reduce_count:
                    loader_object.delete()
            status = matching_loader.objects.filter(jd_id=jd_id).exists()
        data = matching_loader.objects.filter(user_id=user_id).exists()
        return Response({"status": status, "data": data})


class zita_match_data(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        pk = self.request.GET["jd_id"]
        loader_object = matching_loader.objects.filter(jd_id=pk).first()
        if loader_object:
            if loader_object.initial_count == loader_object.reduce_count:
                loader_object.delete()
        user_id, updated_by = admin_account(request)
        user = User.objects.get(username=request.user).id
        logger.info("In function shorlist_candidates - User ID: " + str(user))
        data = request.GET
        get_dict_copy = request.GET.copy()
        fav_id = False
        change_location = employer_pool.objects.filter(location="None" or None).update(
            location="Not Specified"
        )
        if employer_pool.objects.filter(user_id=user_id, can_source_id=5).exists():
            zita_match = zita_match_candidates.objects.filter(
                jd_id_id=pk, candidate_id__first_name__isnull=False
            ).values_list("candidate_id", flat=True)
        else:
            zita_match = zita_match_candidates.objects.filter(
                jd_id_id=pk,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
            ).values_list("candidate_id", flat=True)
        if "invite_candidate" in request.GET:
            can_invite = json.loads(request.GET["invite_candidate"])
            if can_invite:
                data_invite = (
                    Candi_invite_to_apply.objects.filter(jd_id=pk)
                    .values_list("candidate_id", flat=True)
                    .distinct()
                    .exclude(id__in=zita_match)
                )
                zita_match = chain(zita_match, data_invite)
        data = employer_pool.objects.filter(id__in=zita_match)
        jd_list = get_object_or_404(JD_form, id=pk)
        fav = jd_list.favourite.all()
        data = data.annotate(
            fav=Subquery(fav.filter(id=OuterRef("id"))[:1].values("id")),
            applicant=Subquery(
                applicants_status.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("id")
                )[:1].values("jd_id__job_title")
            ),
            match=Subquery(
                Matched_candidates.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("id")
                )[:1].values("profile_match")
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
                    jd_id_id=pk, candidate_id=OuterRef("id"), is_interested=True
                )
                .order_by("-id")[:1]
                .values("is_interested")
            ),
            not_interested=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("id"), is_interested=False
                )
                .order_by("-id")[:1]
                .values("is_interested")
            ),
            city_name=Subquery(
                Personal_Info.objects.filter(application_id=OuterRef("id"))[:1].values(
                    "city__name"
                )
            ),
            state_name=Subquery(
                Personal_Info.objects.filter(application_id=OuterRef("id"))[:1].values(
                    "state__name"
                )
            ),
            country_name=Subquery(
                Personal_Info.objects.filter(application_id=OuterRef("id"))[:1].values(
                    "country__name"
                )
            ),
            source=Subquery(
                applicants_status.objects.filter(id=OuterRef("id"))[:1].values("source")
            ),
            responded_date=Subquery(
                Candi_invite_to_apply.objects.filter(jd_id_id=OuterRef("id"))[
                    :1
                ].values("responded_date")
            ),
            candidate_ai=Exists(
                candidates_ai_matching.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("id")
                )
            ),
            adv_match=Exists(
                Matched_percentage.objects.filter(
                    jd_id_id=pk, candidate_id=OuterRef("id")
                )
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
                        match__range=(
                            request.GET["match_min"],
                            request.GET["match_max"],
                        )
                    )
            except:
                request.GET._mutable = True
                request.GET["profile_match"] = ""
        if "location" in request.GET and len(request.GET["location"]) > 0:
            data = data.filter(location__icontains=request.GET["location"])
        if "fav" in request.GET and len(request.GET["fav"]) > 0:

            if request.GET["fav"] == "add":
                fav_id = True
                data = data.exclude(fav__isnull=True)

        if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
            if "@" in request.GET["candidate"]:
                data = data.filter(email__icontains=request.GET["candidate"])
            else:
                data = data.filter(first_name__icontains=request.GET["candidate"])
        if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
            if request.GET["work_experience"] == "0-1":
                data = data.filter(
                    Q(work_exp__startswith="0 Years")
                    | Q(work_exp__startswith="0")
                    | Q(work_exp="0-1")
                    | Q(work_exp="1 Year")
                    | Q(work_exp="1 Years")
                )
            elif request.GET["work_experience"] == "10-30":
                data = data.filter(
                    Q(work_exp="10+")
                    | Q(work_exp__startswith="11 Years")
                    | Q(work_exp__startswith="12 Years")
                    | Q(work_exp__startswith="13 Years")
                    | Q(work_exp__startswith="14 Years")
                    | Q(work_exp__startswith="15 Years")
                    | Q(work_exp__startswith="16 Years")
                    | Q(work_exp__startswith="17 Years")
                    | Q(work_exp__startswith="18 Years")
                    | Q(work_exp__startswith="19 Years")
                    | Q(work_exp__startswith="20 Years")
                    | Q(work_exp__startswith="21 Years")
                    | Q(work_exp__startswith="22 Years")
                    | Q(work_exp__startswith="23 Years")
                    | Q(work_exp__startswith="24 Years")
                    | Q(work_exp__startswith="25 Years")
                    | Q(work_exp__startswith="26 Years")
                    | Q(work_exp__startswith="27 Years")
                    | Q(work_exp__startswith="28 Years")
                    | Q(work_exp__startswith="29 Years")
                    | Q(work_exp__startswith="30 Years")
                )
            elif request.GET["work_experience"] == "10+":
                data = data.filter(
                    Q(work_exp="10+")
                    | Q(work_exp__startswith="11 Years")
                    | Q(work_exp__startswith="12 Years")
                    | Q(work_exp__startswith="13 Years")
                    | Q(work_exp__startswith="14 Years")
                    | Q(work_exp__startswith="15 Years")
                    | Q(work_exp__startswith="16 Years")
                    | Q(work_exp__startswith="17 Years")
                    | Q(work_exp__startswith="18 Years")
                    | Q(work_exp__startswith="19 Years")
                    | Q(work_exp__startswith="20 Years")
                    | Q(work_exp__startswith="21 Years")
                    | Q(work_exp__startswith="22 Years")
                    | Q(work_exp__startswith="23 Years")
                    | Q(work_exp__startswith="24 Years")
                    | Q(work_exp__startswith="25 Years")
                    | Q(work_exp__startswith="26 Years")
                    | Q(work_exp__startswith="27 Years")
                    | Q(work_exp__startswith="28 Years")
                    | Q(work_exp__startswith="29 Years")
                    | Q(work_exp__startswith="30 Years")
                )
            elif request.GET["work_experience"] == "3-5":
                data = data.filter(
                    Q(work_exp__startswith="3 Years")
                    | Q(work_exp__startswith="4 Years")
                    | Q(work_exp__startswith="5 Years")
                    | Q(work_exp="3-5")
                )
            elif request.GET["work_experience"] == "1-2":
                data = data.filter(
                    Q(work_exp__startswith="1 Years ") 
                    | Q(work_exp="1-2")
                    | Q(work_exp__startswith="2 Years")
                )
            elif request.GET["work_experience"] == "6-10":
                data = data.filter(
                    Q(work_exp__startswith="6 Years")
                    | Q(work_exp__startswith="7 Years")
                    | Q(work_exp__startswith="8 Years")
                    | Q(work_exp__startswith="9 Years")
                    | Q(work_exp__startswith="10 Years")
                    | Q(work_exp="6-10")
                )
            else:
                data = data.filter(
                    work_exp__icontains=request.GET["work_experience"])
        if "relocate" in request.GET and len(request.GET["relocate"]) > 0:
            if request.GET["relocate"] == "1":
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
            education_level = request.GET["education_level"].split(",")
            if "others" in education_level:
                education_level = education_level + [
                    "Professional",
                    "HighSchool",
                    "College",
                    "Vocational",
                    "Certification",
                    "Associates",
                ]
            data = data.filter(
                reduce(
                    operator.or_,
                    (Q(qualification__icontains=qual) for qual in education_level),
                )
            )
        if "type_of_job" in request.GET and len(request.GET["type_of_job"]) > 0:
            data = data.filter(job_type_id=request.GET["type_of_job"])
        if (
            "preferred_location" in request.GET
            and len(request.GET["preferred_location"]) > 0
        ):
            if request.GET["preferred_location"] == "1":
                location = JD_locations.objects.filter(jd_id_id=pk).values(
                    "state_id__name"
                )
                if len(location) > 0:
                    data = data.filter(
                        location__icontains=location.values("state_id__name")[0][
                            "state_id__name"
                        ]
                    )
        if "user_type" in request.GET and len(request.GET["user_type"]) > 0:
            data = data.filter(can_source_id=request.GET["user_type"])
            user_type = request.GET["user_type"]
        else:
            user_type = ""
        if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
            skill_match_list = request.GET["skill_match"].split(",")
            data = data.filter(
                reduce(
                    operator.or_,
                    (Q(skills__icontains=item) for item in skill_match_list),
                )
            )
        if "interested" in request.GET and len(request.GET["interested"]) > 0:
            if request.GET["interested"] == "interested":
                data = data.order_by("-interested")
            elif request.GET["interested"] == "not_interested":
                data = data.order_by("interested")
        if "sort" in request.GET and len(request.GET["sort"]) > 0:
            if request.GET["sort"] == "interested":
                data = data.order_by("-interested", "-match")
            elif request.GET["sort"] == "not_interested":
                data = data.order_by("-not_interested", "-responded_date", "-match")
            elif request.GET["sort"] == "name":
                data = data.order_by("first_name")
            elif request.GET["sort"] == "invited":
                data = data.order_by("-invite")
            elif request.GET["sort"] == "not_invited":
                data = data.order_by("invite")
        if "matching" in request.GET and len(request.GET["sort"]) > 0:
            if self.request.GET["matching"] != "":
                matching = json.loads(self.request.GET["matching"])
                if matching == True:
                    data = data.filter(adv_match=True)
                else:
                    data = data.filter(adv_match=False)

        total_count = data.count()
        page = request.GET.get("page", 1)
        page_count = request.GET.get("pagecount", None)
        if pagination.objects.filter(user_id=request.user, page_id=2).exists():
            if page_count:
                pagination.objects.filter(user_id=request.user, page_id=2).update(
                    pages=page_count
                )
            page_count = pagination.objects.get(user_id=request.user, page_id=2).pages
        elif not pagination.objects.filter(user_id=request.user, page_id=2).exists():
            page_count = tmete_pages.objects.get(id=2).default_value
        paginator = Paginator(data, page_count)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)
        get_dict_copy = request.GET.copy()
        del get_dict_copy["jd_id"]
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        matching = candidates_ai_matching.objects.filter(jd_id=pk).values_list(
            "candidate_id", flat=True
        )
        resume_credits = client_features_balance.objects.get(
            client_id=user_id, feature_id=27
        ).available_count
        plan_details = tmeta_plan.objects.filter(
            is_active=True, plan_id__in=[7, 11]
        ).values_list("plan_id", flat=True)
        ai_credits = client_features_balance.objects.filter(
            client_id=user_id, feature_id=62
        ).exists()
        current_plan = subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
        status = matching_loader.objects.filter(jd_id=pk).exists()
        user = self.request.user
        try:
            if not Weightage_Matching.objects.filter(
                jd_id_id=pk, user_id=user
            ).exists():
                default_scores = {
                    "skills": 20,
                    "roles": 20,
                    "exp": 20,
                    "qualification": 10,
                    "tech_tools": 20,
                    "soft_skills": 10,
                    "industry_exp": 20,
                    "domain_exp": 20,
                    "certification": 20,
                    "location": 10,
                    "cultural_fit": 20,
                    "nice": 10,  # 'ref': 10,
                }
                criteria = tmeta_Weightage_Criteria.objects.all()
                for i in criteria:
                    criteria_name = i.title
                    default_score = default_scores.get(criteria_name, 0)
                    Weightage_Matching.objects.get_or_create(
                        jd_id_id=pk, user_id=user, criteria=i, score=default_score
                    )
        except:
            pass
        candidate_location = candidate_filter_location(pk, "zitamatch")
        context = {
            "data": data.object_list.values(),
            "jd_id": pk,
            "total_count": int(total_count),
            "fav_id": fav_id,
            "user_type": user_type,
            "params": params,
            "bulk_matching": matching,
            "resume_credits": resume_credits,
            "plan_details": plan_details,
            "ai_credits": ai_credits,
            "current_plan": current_plan,
            "status": status,
            "candidate_location": candidate_location,
        }
        return Response(context)


class bulk_download(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        jd = request.POST["jd"]
        if "invite" in request.POST:
            for i in request.POST["candi_id"].split(","):
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
                url = career_page_setting.objects.get(
                    recruiter_id=user_id
                ).career_page_url
                htmly = get_template("email_templates/invite_to_apply.html")
                current_site = get_current_site(request)
                subject, from_email, to = (
                    "Job Notification: An employer invitation to ‘Apply for a Job’",
                    email_main,
                    candidate_details.email,
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
            data = {
                "success": True,
            }
        elif "download" in request.POST:
            domain = get_current_site(request)
            t = datetime.now().strftime("%b_%d_%Y_%H_%M_%S")
            with zipfile.ZipFile(
                base_dir
                + "/media/candidate_profile/candidates_profile_"
                + str(t)
                + ".zip",
                "w",
            ) as myzip:
                for i in request.POST["candi_id"].split(","):
                    try:
                        resume_file = (
                            candidate_parsed_details.objects.filter(candidate_id_id=i)
                            .first()
                            .resume_file_path
                        )
                        myzip.write(
                            base_dir + "/media/" + str(resume_file),
                            str(resume_file).split("/")[1],
                        )
                    except Exception as e:
                        pass
            myzip.close()
            file = open(
                base_dir
                + "/media/candidate_profile/candidates_profile_"
                + str(t)
                + ".zip",
                "rb",
            )
            response = HttpResponse(file, content_type="application/zip")
            response["Content-Disposition"] = (
                "attachment; filename=candidates_profile_" + str(t) + ".zip"
            )
            data = {
                "success": True,
                "file_path": str(domain)
                + "/media/candidate_profile/candidates_profile_"
                + str(t)
                + ".zip",
            }

        return Response(data)


class my_database(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        has_permission = user_permission(request, "my_database")
        if not has_permission == True:
            return Response({"success": True, "Permission": False})
        try:
            skill_list = open(base_dir + "/" + "media/skill_dict.json", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skill_dict.json", "r")
        skill_list = json.load(skill_list)
        # job_title = JD_form.objects.filter(user_id=user_id,jd_status_id = 1).values('job_title','id').order_by('-job_posted_on')
        job_title = (
            JD_form.objects.filter(user_id=user_id, jd_status_id=1)
            .values("job_title", "id")
            .order_by("-job_posted_on")
        )

        try:
            candidate_available = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=27
            ).available_count
        except:
            candidate_available = 0
        job_details = (
            JD_form.objects.filter(user_id=user_id, jd_status_id__in=[1, 4])
            .annotate(
                applicants=Exists(employer_pool.objects.filter(jd_id=OuterRef("pk")))
            )
            .values("job_title", "id", "applicants")
            .order_by("-job_posted_on")
        )
        context = {
            "success": True,
            "job_title": job_title,
            "permission": permission,
            "skill_list": skill_list,
            "candidate_available": candidate_available,
            "job_details": job_details,
        }
        return Response(context)


from django.db.models.functions import Coalesce


class my_database_data(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        fav_id = False
        user_id, updated_by = admin_account(request)
        if employer_pool.objects.filter(client_id=user_id, can_source_id=5).exists():
            data = (
                employer_pool.objects.filter(client_id=user_id)
                .order_by("-created_at")
                .exclude(first_name__isnull=True)
            )
        else:
            data = (
                employer_pool.objects.filter(client_id=user_id)
                .order_by("-created_at")
                .exclude(email__isnull=True)
                .exclude(first_name__isnull=True)
            )
        data = data.annotate(
            applicant_view=Subquery(
                applicants_status.objects.filter(
                    client_id=user_id, status_id_id=6, candidate_id=OuterRef("id")
                )[:1].values("created_on")
            ),
            image=Subquery(
                Profile.objects.filter(user_id=OuterRef("candidate_id__user_id"))[
                    :1
                ].values("image")
            ),
            interested=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id_id=OuterRef("id"), is_interested=True
                )
                .order_by("-id")[:1]
                .values("is_interested")
            ),
            not_interested=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id_id=OuterRef("id"), is_interested=False
                )
                .order_by("-id")[:1]
                .values("is_interested")
            ),
            match=Subquery(
                Matched_candidates.objects.filter(jd_id_id=OuterRef("id"))[:1].values(
                    "profile_match"
                )
            ),
            responded_date=Subquery(
                Candi_invite_to_apply.objects.filter(jd_id_id=OuterRef("id"))[
                    :1
                ].values("responded_date")
            ),
            invite=Subquery(
                Candi_invite_to_apply.objects.filter(jd_id_id=OuterRef("id"))
                .order_by("-created_at")[:1]
                .values("created_at")
            ),
        ).order_by("-id")
        if "job_title" in request.GET and len(request.GET["job_title"]) > 0:
            jd = request.GET["job_title"]
            jd_list = get_object_or_404(JD_form, id=jd)
            fav = jd_list.favourite.all()
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
                interested=Subquery(
                    Candi_invite_to_apply.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id"), is_interested=True
                    )
                    .order_by("-id")[:1]
                    .values("is_interested")
                ),
                not_interested=Subquery(
                    Candi_invite_to_apply.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id"), is_interested=False
                    )
                    .order_by("-id")[:1]
                    .values("is_interested")
                ),
                responded_date=Subquery(
                    Candi_invite_to_apply.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id")
                    )[:1].values("responded_date")
                ),
                # fav=Subquery(fav.filter(id=OuterRef('id'))[:1].values('id'))
                fav=Coalesce(
                    Subquery(
                        fav.filter(id=OuterRef("id"))[:1].values("id"),
                        output_field=IntegerField(),
                    ),
                    Value(None),
                ),
                candidate_ai=Exists(
                    Matched_percentage.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id")
                    )
                ),
                adv_match=Exists(
                    Matched_percentage.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id")
                    )
                ),
                block_descriptive=Exists(
                    applicant_descriptive.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id"), is_active=True
                    )
                ),
                zita_match_candidate=Exists(
                    zita_match_candidates.objects.filter(
                        jd_id_id=jd, candidate_id=OuterRef("id"))
                ),
            ).order_by("-match")
            fav_id = True
            if "fav" in request.GET and request.GET["fav"] == "add":
                data = data.exclude(fav__isnull=True)
            if "zitamatchfilter" in request.GET and request.GET["zitamatchfilter"] == "1":
                data = data.filter(zita_match_candidate=True)

        else:
            jd = False
            data = data.order_by("-id")
        if "candidate" in request.GET and len(request.GET["candidate"]) > 0:
            if "@" in request.GET["candidate"]:
                data = data.filter(email__icontains=request.GET["candidate"])
            else:
                try:
                    data = data.annotate(combined_name=Concat('first_name', Value(''), 'last_name'))
                    data = data.filter(combined_name__icontains=request.GET["candidate"])
                except:
                    data = data.filter(first_name__icontains=request.GET["candidate"])
        if "work_experience" in request.GET and len(request.GET["work_experience"]) > 0:
            if request.GET["work_experience"] == "0-1":
                data = data.filter(
                    Q(work_exp__startswith="0 Years")
                    | Q(work_exp__startswith="0")
                    | Q(work_exp="0-1")
                    | Q(work_exp="1 Year")
                    | Q(work_exp="1 Years")
                )
            elif request.GET["work_experience"] == "10+":
                # data=data.filter(work_exp__in=['More than 10 years','11','12','13','14','15','16','17','18','10+'])
                data = data.filter(
                    Q(work_exp="10+")
                    | Q(work_exp__startswith="11 Years")
                    | Q(work_exp__startswith="12 Years")
                    | Q(work_exp__startswith="13 Years")
                    | Q(work_exp__startswith="14 Years")
                    | Q(work_exp__startswith="15 Years")
                    | Q(work_exp__startswith="16 Years")
                    | Q(work_exp__startswith="17 Years")
                    | Q(work_exp__startswith="18 Years")
                    | Q(work_exp__startswith="19 Years")
                    | Q(work_exp__startswith="20 Years")
                    | Q(work_exp__startswith="21 Years")
                    | Q(work_exp__startswith="22 Years")
                    | Q(work_exp__startswith="23 Years")
                    | Q(work_exp__startswith="24 Years")
                    | Q(work_exp__startswith="25 Years")
                    | Q(work_exp__startswith="26 Years")
                    | Q(work_exp__startswith="27 Years")
                    | Q(work_exp__startswith="28 Years")
                    | Q(work_exp__startswith="29 Years")
                    | Q(work_exp__startswith="30 Years")
                )
            elif request.GET["work_experience"] == "10-30":
                # data=data.filter(work_exp__in=['More than 10 years','11','12','13','14','15','16','17','18','10+'])
                data = data.filter(
                    Q(work_exp="10+")
                    | Q(work_exp__startswith="11 Years")
                    | Q(work_exp__startswith="12 Years")
                    | Q(work_exp__startswith="13 Years")
                    | Q(work_exp__startswith="14 Years")
                    | Q(work_exp__startswith="15 Years")
                    | Q(work_exp__startswith="16 Years")
                    | Q(work_exp__startswith="17 Years")
                    | Q(work_exp__startswith="18 Years")
                    | Q(work_exp__startswith="19 Years")
                    | Q(work_exp__startswith="20 Years")
                    | Q(work_exp__startswith="21 Years")
                    | Q(work_exp__startswith="22 Years")
                    | Q(work_exp__startswith="23 Years")
                    | Q(work_exp__startswith="24 Years")
                    | Q(work_exp__startswith="25 Years")
                    | Q(work_exp__startswith="26 Years")
                    | Q(work_exp__startswith="27 Years")
                    | Q(work_exp__startswith="28 Years")
                    | Q(work_exp__startswith="29 Years")
                    | Q(work_exp__startswith="30 Years")
                )
            elif request.GET["work_experience"] == "3-5":
                data = data.filter(
                    Q(work_exp__startswith="3 Years")
                    | Q(work_exp__startswith="4 Years")
                    | Q(work_exp__startswith="5 Years")
                    | Q(work_exp="3-5")
                )
            elif request.GET["work_experience"] == "1-2":
                # data=data.filter(work_exp__in=['1-2','1','2','1-2 years'])
                data = data.filter(
                    Q(work_exp__startswith="1 Years ") 
                    | Q(work_exp="1-2")
                    | Q(work_exp__startswith="2 Years")
                )
            elif request.GET["work_experience"] == "6-10":
                data = data.filter(
                    Q(work_exp__startswith="6 Years")
                    | Q(work_exp__startswith="7 Years")
                    | Q(work_exp__startswith="8 Years")
                    | Q(work_exp__startswith="9 Years")
                    | Q(work_exp__startswith="10 Years")
                    | Q(work_exp="6-10")
                )
                # data=data.filter(work_exp__in=['6-10 years','6-10','6','7','8','9','10'])
            else:
                data = data.filter(work_exp__icontains=request.GET["work_experience"])
        if "relocate" in request.GET and len(request.GET["relocate"]) > 0:
            if request.GET["relocate"] == "1":
                data = data.filter(relocate=True)
        if "education_level" in request.GET and len(request.GET["education_level"]) > 0:
            education_level = request.GET["education_level"].split(",")
            if "others" in education_level:
                education_level = education_level + [
                    "Professional",
                    "HighSchool",
                    "College",
                    "Vocational",
                    "Certification",
                    "Associates",
                ]
            data = data.filter(
                reduce(
                    operator.or_,
                    (Q(qualification__icontains=qual) for qual in education_level),
                )
            )
        if "type_of_job" in request.GET and len(request.GET["type_of_job"]) > 0:
            data = data.filter(job_type_id=request.GET["type_of_job"])
        if "location" in request.GET and len(request.GET["location"]) > 0:
            data = data.filter(location__icontains=request.GET["location"])
        if "user_type" in request.GET and len(request.GET["user_type"]) > 0:
            if (
                int(request.GET["user_type"]) == 3
                and request.GET["applicant_only"] == "1"
            ):
                data = data.filter(can_source_id=request.GET["user_type"]).exclude(
                    applicant__isnull=True
                )
            elif (
                int(request.GET["user_type"]) == 3
                and request.GET["applicant_only"] == "0"
            ):
                data = data.filter(candidate_id_id__isnull=False).exclude(
                    can_source_id=4
                )
            elif (
                int(request.GET["user_type"]) == 1
                and request.GET["applicant_only"] == "0"
            ):
                data = data.filter(
                    candidate_id_id__isnull=True, can_source_id=request.GET["user_type"]
                )
            elif (
                int(request.GET["user_type"]) == 4
                and request.GET["applicant_only"] == "0"
            ):  # Others
                data = data.filter(can_source_id=request.GET["user_type"])
            else:  # change for linkedin sourcing
                data = data.filter(can_source_id__in=[2, 5])
            user_type = request.GET["user_type"]
        else:
            user_type = ""
        if "skill_match" in request.GET and len(request.GET["skill_match"]) > 0:
            skill_match_list = request.GET["skill_match"].split(",")
            data = data.filter(
                reduce(
                    operator.or_,
                    (Q(skills__icontains=item) for item in skill_match_list),
                )
            )
        if "sort" in request.GET and len(request.GET["sort"]) > 0:
            if request.GET["sort"] == "interested":
                data = data.order_by("-interested", "-match")
            elif request.GET["sort"] == "not_interested":
                data = data.order_by("-not_interested", "-responded_date", "-match")
            elif request.GET["sort"] == "name":
                data = data.order_by("first_name")
            elif request.GET["sort"] == "invited":
                data = data.order_by("-invite")
            elif request.GET["sort"] == "not_invited":
                data = data.order_by("invite")
        if "job_title" in request.GET and len(request.GET["job_title"]) > 0:
            if "matching" in request.GET and len(request.GET["relocate"]) > 0:
                matching = self.request.GET["matching"]
                if matching != "":
                    matching = json.loads(matching)
                    if matching == True:
                        data = data.filter(adv_match=True)
                    else:
                        data = data.filter(adv_match=False)
        if "job_title" in request.GET and len(request.GET["job_title"]) > 0:
            jd_data = request.GET["job_title"]
            if "user_type" in request.GET and len(request.GET["user_type"]) > 0:
                if (
                    int(request.GET["user_type"]) == 3
                    and request.GET["applicant_only"] == "1"
                ):
                    data = data.filter(
                        can_source_id=request.GET["user_type"], jd_id=jd_data
                    ).exclude(applicant__isnull=True)
                elif (
                    int(request.GET["user_type"]) == 3
                    and request.GET["applicant_only"] == "0"
                ):
                    applicant_id = applicants_status.objects.filter(
                        jd_id=jd_data,
                        candidate_id__first_name__isnull=False,
                        candidate_id__email__isnull=False,
                    ).values_list("candidate_id", flat=True)
                    data = data.filter(id__in=applicant_id)
                elif (
                    int(request.GET["user_type"]) == 1
                    and request.GET["applicant_only"] == "0"
                ):
                    data = data.filter(
                        candidate_id_id__isnull=True,
                        can_source_id=request.GET["user_type"],
                        jd_id=jd_data,
                    )
                elif (
                    int(request.GET["user_type"]) == 4
                    and request.GET["applicant_only"] == "0"
                ):  # others
                    data = data.filter(
                        can_source_id=request.GET["user_type"], jd_id=jd_data
                    )
                else:
                    data = data.filter(
                        can_source_id__in=[request.GET["user_type"], 5], jd_id=jd_data
                    )
                user_type = request.GET["user_type"]
            else:
                user_type = ""
      
        search = False
        total_count = data.count()
        try:
            if request.GET["search"] == "1":
                search = True
        except:
            pass
        page = request.GET.get("page", 1)
        page_count = request.GET.get("pagecount", None)
        if pagination.objects.filter(user_id=request.user, page_id=5).exists():
            if page_count:
                pagination.objects.filter(user_id=request.user, page_id=5).update(
                    pages=page_count
                )
            page_count = pagination.objects.get(user_id=request.user, page_id=5).pages
        elif not pagination.objects.filter(user_id=request.user, page_id=5).exists():
            page_count = tmete_pages.objects.get(id=5).default_value
        paginator = Paginator(data, page_count)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)
        data = data.object_list.values()
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        matching = bulk_matching_user(user_id, jd)
        features, plan = plan_checking(user_id, "resume")
        total_length = employer_pool.objects.filter(
            client_id=user_id, first_name__isnull=False, email__isnull=False
        ).values_list("id", flat=True)
        # blocked_resume = []
        # if len(total_length) > int(features):
        #     blocked_resume = employer_pool.objects.filter(client_id=user_id,first_name__isnull= False,email__isnull = False).order_by('-id').values_list('id',flat= True)[:len(total_length)-int(features)]
        blocked_resume = (
            applicants_list.objects.filter(user_id=user_id, is_active=True)
            .exclude(jd_id=None)
            .values_list("candidate_id", flat=True)
            .distinct()
        )
        plan_details = tmeta_plan.objects.filter(
            is_active=True, plan_id__in=[7, 11]
        ).values_list("plan_id", flat=True)
        ai_credits = client_features_balance.objects.filter(
            client_id=user_id, feature_id=62
        ).exists()
        current_plan = subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
        user = self.request.user
        try:
            if not Weightage_Matching.objects.filter(
                jd_id_id=jd, user_id=user
            ).exists():
                default_scores = {
                    "skills": 20,
                    "roles": 20,
                    "exp": 20,
                    "qualification": 10,
                    "tech_tools": 20,
                    "soft_skills": 10,
                    "industry_exp": 20,
                    "domain_exp": 20,
                    "certification": 20,
                    "location": 10,
                    "cultural_fit": 20,
                    "nice": 10,  # 'ref': 10,
                }
                criteria = tmeta_Weightage_Criteria.objects.all()
                for i in criteria:
                    criteria_name = i.title
                    default_score = default_scores.get(criteria_name, 0)
                    Weightage_Matching.objects.get_or_create(
                        jd_id_id=jd, user_id=user, criteria=i, score=default_score
                    )
        except:
            pass

        candidate_location = candidate_filter_location(user_id, "database")
        candidate_name = candidate_name_email(user_id, "database")
        context = {
            "data": data,
            "jd": jd,
            "fav_id": fav_id,
            "total_count": total_count,
            "user_type": user_type,
            "plan_details": plan_details,
            "ai_credits": ai_credits,
            "current_plan": current_plan,
            "params": params,
            "search": search,
            "matching": matching,
            "blocked_resume": blocked_resume,
            "candidate_location": candidate_location,
            "candidate_name": candidate_name,
        }
        return Response(context)


class company_detail(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        has_permission = user_permission(request, "manage_account_settings")
        build_career_page = career_page_setting.objects.filter(
            recruiter_id=user_id
        ).exists()
        company_detail = company_details.objects.filter(recruiter_id=user_id).values(
            "id",
            "recruiter_id_id",
            "company_name",
            "company_website",
            "email",
            "contact",
            "industry_type_id",
            "industry_type_id__value",
            "no_of_emp",
            "address",
            "country_id",
            "state_id",
            "city_id",
            "zipcode",
            "updated_by",
            "logo",
            "created_at",
        )
        country = Country.objects.filter(name__in=countries_to_be_displayed)
        state = State.objects.filter(country_id__in=country)
        city = City.objects.filter(state_id__in=state)
        com = company_detail[0]
        context = {
            "success": True,
            "build_career_page": build_career_page,
            "permission": permission,
            "country": country.values(),
            "state": state.values(),
            "city": city.values(),
            "company_detail": company_detail[0],
        }
        return Response(context)

    def post(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        # if 'image_null' in request.POST:
        recruiter = company_details.objects.get(recruiter_id=user_id)
        new_request = request.POST.copy()
        industry = new_request["industry_type"]
        # try:
        if tmeta_industry_type.objects.filter(value=industry).exists():
            new_request["industry_type"] = tmeta_industry_type.objects.get(
                value=industry
            ).id
        else:
            industry_type = tmeta_industry_type.objects.create(
                label_name=industry,
                description=industry,
                value=industry,
                is_active=True,
                client_id=user_id,
            )
            new_request["industry_type"] = tmeta_industry_type.objects.get(
                id=industry_type.id
            ).id
        # except Exception as e:
        #     industry_type = tmeta_industry_type.objects.create(label_name =industry,description=industry,value=industry,is_active = True)
        #     new_request["industry_type"] = tmeta_industry_type.objects.get(id = industry_type.id).id

        company_detail = company_details_form(
            new_request, request.FILES, instance=recruiter
        )
        logo = request.FILES.get("logo", None)
        if logo:
            logo = "company_logo/" + str(request.FILES["logo"])

        company_details.objects.filter(recruiter_id=user_id).update(logo=logo)
        if company_detail.is_valid():
            temp = company_detail.save(commit=False)
            temp.recruiter_id = user_id
            temp.updated_by = updated_by
            main = temp.save()
            # if not tmeta_industry_type.objects.filter(value=company_detail['industry_type']).exists():
            #     tmeta_industry_type.objects.create(label_name =company_detail['industry_type'],description=company_detail['industry_type'],value=company_detail['industry_type'],is_active = True)
            recruiter = company_details.objects.get(recruiter_id=user_id)
            UserDetail.objects.filter(user=user_id).update(
                contact=request.POST["contact"]
            )
            data = {"success": True}
            return Response(data)
        if logo == None:
            company_details.objects.filter(recruiter_id=user_id).update(logo=logo)

        data = {"success": True}
        return Response(data)


class LogoUpdateAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_id, updated_by = admin_account(request)
        recruiter = company_details.objects.get(recruiter_id=user_id)
        logo = request.FILES.get("logo")
        if logo:
            logo_name = f"{logo.name}"
            recruiter.logo.save(logo_name, logo, save=True)
            data = {"success": True, "message": "Logo updated successfully"}
            return Response(data)
        if logo == None:
            logo = ""
            company_details.objects.filter(recruiter_id=user_id).update(logo=logo)
            data = {"success": True, "message": "Logo updated successfully"}
            return Response(data)

        else:
            data = {"success": False, "message": "No logo file provided"}
            return Response(data)


class Password_Change(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request = self.request

        password = PasswordChangeForm(request.user, request.POST)
        if request.user.is_staff == False:
            User_Info.objects.filter(user_id=request.user).update(
                password=request.POST["new_password1"]
            )
        if password.is_valid():
            try:
                user = password.save()
            except:
                user = request.user
            update_session_auth_hash(request, user)
            subject = "Your Zita Password has been Reset"
            email_template_name = get_template(
                "email_templates/password_reset_conformation.html"
            )
            user_obj = User.objects.get(id=request.user.id)
            c = {"user": user_obj}
            try:
                email = email_template_name.render(c)
                msg = EmailMultiAlternatives(
                    subject, email, settings.EMAIL_HOST_USER, [user.email]
                )
                msg.attach_alternative(email, "text/html")
                msg.mixed_subtype = "related"
                image_data = [
                    "twitter.png",
                    "linkedin.png",
                    "youtube.png",
                    "new_zita_white.png",
                ]
                for i in image_data:
                    msg.attach(logo_data(i))
                msg.mixed_subtype = "related"
                msg.send()
            except BadHeaderError as e:
                return Response({"success": False})
            data = {"success": True}
            return Response(data)
        else:
            data = {"success": False, "msg": "Enter correct current password"}
        return Response(data)


class user_profile(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request.user
        user = User.objects.filter(id=self.request.user.id).values()
        profile = ""
        if Profile.objects.filter(user=request.user, image__isnull=False).exists():
            profile = request.user.profile.image
        data = {"success": True, "user": user[0], "profile": str(profile)}
        return Response(data)

    def post(self, request, *args, **kwargs):
        request = self.request
        if "image_null" in request.POST:
            Profile.objects.filter(user=request.user).update(image="")
            User.objects.filter(id=request.user.id).update(
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
            )
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )  # check this code
        data = {
            "success": True,
        }
        if "image" in request.FILES:
            if p_form.is_valid():
                p_form.save()
                data = {"success": True}
        form = user_profile_form(instance=request.user, data=request.POST)
        if form.is_valid():
            # form.save()
            User.objects.filter(id=request.user.id).update(
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
            )
            data = {
                "success": True,
            }
        return Response(data)


class build_career_page(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        has_permission = user_permission(request, "manage_account_settings")
        if not has_permission == True:
            return Response({"success": True, "Permission": False})
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        user_id, updated_by = admin_account(request)

        career_page_exists = career_page_setting.objects.filter(
            recruiter_id=user_id
        ).exists()
        company_detail = company_details.objects.filter(recruiter_id=user_id).values()
        if career_page_exists:
            career_page = career_page_setting.objects.filter(
                recruiter_id=user_id
            ).values()[0]
        else:
            career_page = None

        domain = settings.CLIENT_URL
        context = {
            "success": True,
            "career_page": career_page,
            "company_detail": company_detail[0],
            "career_page_exists": career_page_exists,
            "domain": str(domain),
            "permission": permission,
        }
        return Response(context)

    def post(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        career_page_exists = career_page_setting.objects.filter(
            recruiter_id=user_id
        ).exists()
        if not career_page_exists:
            setting_pages = career_page_setting_form(request.POST, request.FILES)
        else:
            setting_pages = career_page_setting_form(
                request.POST,
                request.FILES,
                instance=career_page_setting.objects.get(recruiter_id=user_id),
            )
        if setting_pages.is_valid():
            temp = setting_pages.save(commit=False)
            temp.recruiter_id = user_id
            temp.updated_by = updated_by
            temp.save()
            data = {"url": request.POST["career_page_url"], "success": True}
            return Response(data)
        data = {"success": False}
        return Response(data)


class career_page(generics.GenericAPIView):

    def get(self, request, url=None):
        request = self.request
        if request.GET["user_id"] != "0":
            login_user = True
        else:
            login_user = False
        try:
            user = career_page_setting.objects.get(career_page_url=url).recruiter_id
        except:
            user, updated_by = admin_account(request)
        if request.GET["user_id"] != "0":
            client_id = User.objects.get(id=request.GET["user_id"])
        else:
            client_id = user
        jd_active = False

        if login_user:
            image = str(Profile.objects.get(user_id=int(request.GET["user_id"])).image)
            user_detail = User.objects.filter(id=int(request.GET["user_id"])).values()[
                0
            ]
        else:
            image = None
            user_detail = None

        jd_form = JD_form.objects.filter(user_id=user, jd_status_id=1)
        count = len(jd_form)
        if jd_form.count() > 0:
            jd_active = True
        jd_form = jd_form.annotate(
            country=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "country__name"
                )
            ),
            state=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "state__name"
                )
            ),
            city=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "city__name"
                )
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
        total = jd_form.count()
        try:
            company_detail = company_details.objects.filter(recruiter_id=user).values(
                "company_name",
                "company_website",
                "email",
                "address",
                "country__name",
                "state__name",
                "city__name",
                "zipcode",
                "logo",
                "contact",
            )
        except:
            company_detail = None
        # try:

        career_page_settings = career_page_setting.objects.filter(
            recruiter_id=user
        ).values()
        # except:
        # career_page_setting= None
        page = request.GET.get("page", 1)
        page_count = request.GET.get("pagecount", None)
        if page_count:
            if pagination.objects.filter(user_id=user, page_id=7).exists():
                if page_count and page_count != "0":
                    pagination.objects.filter(user_id=user, page_id=7).update(
                        pages=page_count
                    )
                page_count = pagination.objects.get(user_id=user, page_id=7).pages
            elif not pagination.objects.filter(user_id=user, page_id=7).exists():
                page_count = tmete_pages.objects.get(id=7).default_value
        else:
            if pagination.objects.filter(user_id=user, page_id_id=7).exists():
                page_count = pagination.objects.get(user_id=user, page_id_id=7).pages
            else:
                page_count = tmete_pages.objects.get(id=7).default_value
        paginator = Paginator(jd_form, page_count)

        try:
            jd_form = paginator.page(page)
        except PageNotAnInteger:
            jd_form = paginator.page(1)
        except ZeroDivisionError:
            jd_form = paginator.page(1)

        except EmptyPage:
            jd_form = paginator.page(paginator.num_pages)
        jd_form = jd_form.object_list.values(
            "job_posted_on",
            "job_title",
            "job_id",
            "no_of_vacancies",
            "id",
            "job_role__label_name",
            "work_remote",
            "is_ds_role",
            "work_remote",
            "is_eeo_comp",
            "industry_type__label_name",
            "salary_min",
            "salary_max",
            "salary_curr_type__value",
            "show_sal_to_candidate",
            "job_type__label_name",
            "jd_status__label_name",
            "job_location",
            "min_exp",
            "max_exp",
            "work_space_type",
        )
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        job_location = postjob_location(user, "joblocation")
        job_title = postjob_location(user, "jobtitle")
        if pagination.objects.filter(user_id=user, page_id_id=7).exists():
            careers_page = pagination.objects.get(user_id=user, page_id_id=7).pages
        else:
            careers_page = tmete_pages.objects.get(id=7).default_value
        context = {
            "jd_form": jd_form,
            "filter_count": total,
            "count": count,
            "user_detail": user_detail,
            "params": params,
            "image": image,
            "total": total,
            "jd_active": jd_active,
            "login_user": login_user,
            "career_page_setting": career_page_settings[0],
            "company_detail": company_detail[0],
            "job_location": job_location,
            "job_title": job_title,
            "careers_page": careers_page,
        }
        return Response(context)


class create_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        try:
            with open(base_dir + "/static/media/skills2.json", "r") as fp:
                data = json.load(fp)
        except:
            with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
                data = json.load(fp)

        try:
            skill_list = open(base_dir + "/" + "media/skill_dict.json", "r")
        except:
            skill_list = open(os.getcwd() + "/" + "media/skill_dict.json", "r")
        try:
            soft_skills = open(base_dir + "/" + "media/soft_skills.json", "r")
        except:
            soft_skills = open(os.getcwd() + "/" + "media/soft_skills.json", "r")
        skill_list = json.load(skill_list)
        soft_skills = json.load(soft_skills)
        skill_list.extend(soft_skills)
        return Response({"data": data, "skill_list": skill_list, "success": True})

        # return Response({'data':data,})

    def post(
        self,
        request,
    ):
        request = self.request
        form = request.POST
        work_remote = True
        if form.get("work_remote") == "1":
            work_remote = True
        else:
            work_remote = False

        admin_id, updated_by = admin_account(self.request)
        jd = JD_form()
        jd.job_title = form["job_title"]
        jd.user_id = admin_id
        jd.job_role = tmeta_ds_main_roles.objects.get(id=int(form["job_role"]))
        jd.job_id = form["job_id"]
        if tmeta_industry_type.objects.filter(value=form["industry_type"]).exists():
            jd.industry_type_id = tmeta_industry_type.objects.get(
                value=form["industry_type"]
            ).id
        else:
            if form["industry_type"] != "" and form["industry_type"] != None:
                industry_type = tmeta_industry_type.objects.create(
                    label_name=form["industry_type"],
                    description=form["industry_type"],
                    value=form["industry_type"],
                    is_active=True,
                    client_id=admin_id,
                )
                jd.industry_type = tmeta_industry_type.objects.get(
                    id=industry_type.id
                )  # Access the ID
            else:
                industry_type, created = tmeta_industry_type.objects.get_or_create(
                    label_name=form["industry_type"],
                    description=form["industry_type"],
                    value=form["industry_type"],
                    is_active=True,
                    client_id=admin_id,
                )
                jd.industry_type = industry_type
        jd.min_exp = form["min_exp"]
        jd.work_space_type = form["work_space_type"]
        if form["max_exp"] == "":
            jd.max_exp = None
        else:
            jd.max_exp = form["max_exp"]
        if form["no_of_vacancies"] == "":
            no_of_vacancies = None
        else:
            no_of_vacancies = form["no_of_vacancies"]
        jd.no_of_vacancies = no_of_vacancies
        jd.work_remote = work_remote
        jd.richtext_job_description = form["richtext_job_description"]
        text_des = re.sub(r"<.*?>", "", form["richtext_job_description"])
        text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
        text_des = re.sub(r"Requirements:", "", text_des)
        jd.job_description = text_des
        if "salary_curr_type" in form:
            if form["salary_curr_type"]:
                jd.salary_curr_type_id = int(form["salary_curr_type"])
        try:
            jd.show_sal_to_candidate = 1 if form["show_sal_to_candidate"] == "1" else 0
        except:
            pass
        if form["salary_min"] == "":
            jd.salary_min = None
        else:
            jd.salary_min = form["salary_min"]

        if form["salary_max"] == "":
            jd.salary_max = None
        else:
            jd.salary_max = form["salary_max"]
        jd.job_type_id = form["job_type"]
        jd.jd_status_id = int(2)
        # jd.success =  False
        jd.save()
        count = reducematchcount(admin_id, "job")
        if "generate_ai" in self.request.POST:
            reparsing = reparsing_count.objects.get_or_create(
                jd_id=jd, count=request.POST.get("generate_ai", 0), is_active=True
            )
        UserActivity.objects.get_or_create(
            user=request.user,
            action_id=1,
            action_detail=str(form["job_title"]) + " (" + str(form["job_id"]) + ")",
        )

        jd_id = JD_form.objects.filter(user_id=admin_id).last()

        qual_list = form["qualification"].split(",")
        spec_list = form["specialization"].split(",")
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id.id
            )
        if "Nice_to_Have" in form:
            if form["Nice_to_Have"] != None or form["Nice_to_Have"] != "":
                nice_to_have = form["Nice_to_Have"]
                jd_nice_to_have.objects.create(
                    jd_id=jd_id,
                    user_id=admin_id,
                    nice_to_have=string_checking(nice_to_have),
                )

        if form["job_role"] == "6" or form["job_role"] == 6:
            try:
                skills = form["skills"].split(",")
                for s in skills:
                    JD_skills_experience.objects.create(
                        skill=s, experience=0, jd_id_id=jd_id.id, category_id=None
                    )
            except:
                pass

        try:
            JD_locations.objects.create(
                country_id=int(form["work_country"]),
                state_id=int(form["work_state"]),
                city_id=int(form["work_city"]),
                jd_id_id=jd_id.id,
            )
        except:
            pass
        if "duplicate" in form and form["job_role"] != "6":
            profiler_input = [text_des]
            try:
                if profiler_input != []:
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
                    JD_profile.objects.create(
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
            except Exception as e:
                logger.error("Profiling failed----" + str(e))
        context = {
            "success": True,
            "jd_id": jd_id.id,
        }
        return Response(context)


class edit_jd(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        request = self.request
        jd_id = pk
        user_id, updated_by = admin_account(request)
        edited_jd = request.POST
        text_des = re.sub(r"<.*?>", "", edited_jd["richtext_job_description"])
        text_des = re.sub(r"Roles and Responsibilities:", "", text_des)
        text_des = re.sub(r"Requirements:", "", text_des)
        job_description = text_des
        if edited_jd["work_remote"] == "1":
            work_remote = True
        else:
            work_remote = False

        show_sal_to_candidate = (
            True if edited_jd.get("show_sal_to_candidate") == "1" else False
        )

        if edited_jd["max_exp"] == "":
            max_exp = None
        else:
            max_exp = edited_jd["max_exp"]
        if edited_jd["salary_min"] == "":
            salary_min = None
        else:
            salary_min = edited_jd["salary_min"]

        if edited_jd["salary_max"] == "":
            salary_max = None
        else:
            salary_max = edited_jd["salary_max"]
        if edited_jd["no_of_vacancies"] == "":
            no_of_vacancies = None
        else:
            no_of_vacancies = edited_jd["no_of_vacancies"]
        JD_locations.objects.filter(jd_id=jd_id).delete()
        try:
            JD_locations.objects.create(
                country_id=int(edited_jd["work_country"]),
                state_id=int(edited_jd["work_state"]),
                city_id=int(edited_jd["work_city"]),
                jd_id_id=jd_id,
            )
        except:
            pass
        qual_list = edited_jd["qualification"].split(",")
        spec_list = edited_jd["specialization"].split(",")
        JD_qualification.objects.filter(jd_id_id=jd_id).delete()
        for q, s in zip(qual_list, spec_list):
            JD_qualification.objects.create(
                qualification=q, specialization=s, jd_id_id=jd_id
            )

        if edited_jd["job_role"] == "6" or edited_jd["job_role"] == 6:

            skills = edited_jd["skills"].split(",")

            JD_skills_experience.objects.filter(jd_id_id=jd_id).delete()
            for s in skills:
                JD_skills_experience.objects.create(
                    skill=s, experience=0, jd_id_id=jd_id, category_id=5
                )

        if "Nice_to_Have" in edited_jd:
            nice_to_have = edited_jd.get("Nice_to_Have", None)
            if jd_nice_to_have.objects.filter(jd_id=jd_id).exists():
                jd_nice_to_have.objects.filter(jd_id=jd_id).update(
                    nice_to_have=string_checking(nice_to_have)
                )
            else:
                jd_nice_to_have.objects.create(
                    jd_id=JD_form.objects.get(id=jd_id),
                    nice_to_have=string_checking(nice_to_have),
                    user_id=user_id,
                )
            update_score = calculate_weightage(jd_id)
            if Weightage_Matching.objects.filter(jd_id=jd_id, criteria=13).exists():
                if update_score != 100:
                    update_score = 100 - update_score
                    Weightage_Matching.objects.filter(jd_id=jd_id, criteria=13).update(
                        score=update_score
                    )
            if not Weightage_Matching.objects.filter(jd_id=jd_id, criteria=13).exists():
                if update_score != 100:
                    update_score = 100 - update_score
                    criteria_13 = None
                    if tmeta_Weightage_Criteria.objects.filter(id=13).exists():
                        criteria_13 = tmeta_Weightage_Criteria.objects.get(id=13)
                    Weightage_Matching.objects.create(
                        jd_id=JD_form.objects.get(id=jd_id),
                        criteria=criteria_13,
                        score=update_score,
                    )
        if tmeta_industry_type.objects.filter(
            value=edited_jd["industry_type"]
        ).exists():
            industry_type_id = tmeta_industry_type.objects.get(
                value=edited_jd["industry_type"]
            )
        else:
            if edited_jd["industry_type"] != "":
                industry_type_id = tmeta_industry_type.objects.create(
                    value=edited_jd["industry_type"],
                    label_name=edited_jd["industry_type"],
                    description=edited_jd["industry_type"],
                    client_id=user_id,
                )
            else:
                industry_type, created = tmeta_industry_type.objects.get_or_create(
                    label_name=edited_jd["industry_type"],
                    description=edited_jd["industry_type"],
                    value=edited_jd["industry_type"],
                    is_active=True,
                    client_id=user_id,
                )
                industry_type_id = industry_type
        JD_form.objects.filter(id=jd_id).update(
            job_title=edited_jd["job_title"],
            job_id=edited_jd["job_id"],
            no_of_vacancies=no_of_vacancies,
            industry_type_id=industry_type_id,
            job_role=edited_jd["job_role"],
            min_exp=edited_jd["min_exp"],
            max_exp=max_exp,
            work_remote=work_remote,
            job_description=job_description,
            richtext_job_description=edited_jd["richtext_job_description"],
            salary_curr_type_id=edited_jd["salary_curr_type"],
            salary_min=salary_min,
            salary_max=salary_max,
            show_sal_to_candidate=show_sal_to_candidate,
            job_type=edited_jd["job_type"],
            updated_by=updated_by,
            work_space_type=edited_jd["work_space_type"],
        )
        if "generate_ai" in request.POST:
            reparsing = reparsing_count.objects.filter(jd_id=jd_id).update(
                count=request.POST.get("generate_ai", 0)
            )
        context = {"success": True, "jd_id": jd_id}
        return Response(context)


class dst_or_not(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        jd_id = pk
        request = self.request

        ds_role = JD_form.objects.get(id=jd_id).is_ds_role
        context = {
            "success": True,
            "ds_role": ds_role,
        }
        return Response(context)

    def post(self, request, pk):
        request = self.request
        jd_id = pk
        if request.POST["is_ds_role"] == "1":
            ds_role = True
        else:
            ds_role = False

        JD_form.objects.filter(id=jd_id).update(is_ds_role=ds_role)
        context = {
            "success": True,
            "ds_role": ds_role,
        }
        return Response(context)


# def validate_job_id(request):
class validate_job_id(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        job_id = request.GET.get("job_id", None)
        jd_id = request.GET.get("jd_id", None)
        if "isEdit" in request.GET:
            isEdit = request.GET["isEdit"]
            if isEdit == "true":
                data = {
                    "is_taken": JD_form.objects.filter(
                        user_id=user_id, job_id=job_id
                    ).exists()
                }
            else:
                data = {
                    "is_taken": JD_form.objects.filter(user_id=user_id, job_id=job_id)
                    .exclude(id=jd_id)
                    .exists()
                }
        else:
            data = {
                "is_taken": JD_form.objects.filter(
                    user_id=user_id, job_id=job_id
                ).exists()
            }

        return Response(data)


class jd_profile(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # if request.method=='POST':
        request = self.request

        jd_id = pk
        if request.POST.get("post_recom_role") is not None:
            role = request.POST.get("post_recom_role")
            logger.info("Recruiter has chosen recommended role ")
            role_obj = tmeta_ds_main_roles.objects.get(label_name=role)
            JD_form.objects.filter(id=jd_id).update(job_role_id=role_obj)
            JD_profile.objects.filter(jd_id_id=jd_id).update(role_acceptence=1)
            context = {
                "success": True,
                "new_role": role,
            }
            return Response(context)
        return Response(
            {
                "success": False,
                "old_role": request.POST["do_not_change"],
            }
        )

    def get(self, request, pk):
        request = self.request
        jd_id = pk
        admin_id, updated_by = admin_account(request)
        jd = JD_form.objects.get(id=jd_id)
        job_description = jd.job_description
        profiler_input = [job_description]
        try:
            if profiler_input != []:

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
                JD_profile.objects.filter(
                    jd_id_id=jd_id,
                ).delete()
                JD_profile.objects.create(
                    jd_id_id=jd_id,
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

                profile_value = JD_profile.objects.filter(
                    jd_id_id=jd_id,
                ).values(
                    "business_intelligence",
                    "data_analysis",
                    "data_engineering",
                    "devops",
                    "machine_learning",
                    "others",
                    "recommended_role_id__label_name",
                )
            context = {
                "success": True,
                "profile_value": profile_value[0],
                "selected_role": jd.job_role.label_name,
            }
            return Response(context)
        except Exception as e:
            logger.error("Profiling failed----" + str(e))

        context = {
            "success": False,
        }
        return Response(context)


class jd_parser(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        request = self.request
        try:
            cd = clamd.ClamdUnixSocket()
            file = request.FILES["jd_file"]
            scan_results = cd.instream(file)
        except:
            scan_results = {"stream": ("OK", None)}
        try:
            if scan_results["stream"][0] == "OK":
                form_upload = Upload_jd(request.POST, request.FILES)
                if form_upload.is_valid():
                    temp = form_upload.save(commit=False)
                    temp.user_id = User.objects.get(username=request.user)
                    temp.save()
                    filepath = form_upload.instance.jd_file.path
                    file_name = os.path.splitext(os.path.basename(filepath))
                    filename = "".join(list(file_name))
                    logger.info("Parsing the JD: " + str(filename))
                from zita.settings import jdp_api_auth_token,jdp_api_url
                headers = {"Authorization": jdp_api_auth_token}
                url = jdp_api_url
                try:
                    files = {
                        "jd_file": open(
                            os.getcwd() + "/" + "media/uploaded_jds/" + filename, "rb"
                        )
                    }
                except:
                    files = {
                        "jd_file": open(
                            base_dir + "/" + "media/uploaded_jds/" + filename, "rb"
                        )
                    }
                user_id = request.user
                parser_output = Jd_Parser_AI(files, files["jd_file"].name,user_id = user_id)
                if isinstance(parser_output,dict):
                    zita_service = parser_output.get('error')
                    if zita_service:
                        return Response({"success": False,"standalone":True,"message": zita_service})
                print("parser_output@@@@@",parser_output)
                job_description = convert_dict_to_html(parser_output)
                if parser_output == None:
                    return Response(
                        {
                            "success": False,
                            "message": "The JD Could Not Parsed Correctly. Please try again",
                        }
                    )
                try:
                    with open(
                        base_dir + "/" + "media/jd_output/" + filename + ".json", "w"
                    ) as fp:
                        json.dump(parser_output, fp)
                except:
                    with open(
                        os.getcwd() + "/" + "media/jd_output/" + filename + ".json", "w"
                    ) as fp:
                        json.dump(parser_output, fp)
                qual_name = []
                role_and_res = []
                try:
                    job_title = ", ".join(parser_output["job_title"])
                except:
                    job_title = ""
                try:
                    qual = parser_output["edu_qualification"]
                    import re

                    qual_list = re.split(", |_|-|!|\+", qual[0])
                    for i in qual_list:
                        if i.lower().strip() in settings.ug:
                            qual_name.append({"qual": "Bachelors"})
                        if i.lower().strip() in settings.pg:
                            qual_name.append({"qual": "Masters"})
                        if i.lower().strip() in settings.phd:
                            qual_name.append({"qual": "Doctorate"})
                except KeyError:
                    pass
                except:
                    pass

                try:
                    add_in = parser_output["Additional Information"]
                except:
                    pass

                try:
                    roles = parser_output["roles_and_responsibilities"]
                    role_and_res.append(
                        '<h6 style="font-weight:600">Roles and Responsibilities</h6>'
                    )
                    role_and_res.append("<br>".join(roles))
                except:
                    pass

                try:
                    tech_re = parser_output["Technical requirements"]
                    role_and_res.append(
                        '<h6 style="font-weight:600;margin-top:1rem">Requirements</h6>'
                    )
                    role_and_res.append("<br>".join(tech_re))
                except:
                    pass

                try:
                    non_tech = parser_output["Non_Technical requirements"]
                    role_and_res.append("<br>".join(non_tech))
                except:
                    pass

                try:
                    o_inf = parser_output["organisation_information"]
                    if len(o_inf) > 0:
                        role_and_res.append(
                            '<h6 style="font-weight:600;margin-top:1rem">Organisation Information</h6>'
                        )
                        role_and_res.append("<br>".join(o_inf))
                except:
                    pass

                try:
                    add_in = parser_output["Additional Information"]
                    if len(add_in) > 0:
                        role_and_res.append(
                            '<h6 style="font-weight:600;margin-top:1rem">Additional Information</h6>'
                        )
                        role_and_res.append("<br>".join(add_in))
                except:
                    pass
                # job_description = ''.join(role_and_res)
                try:
                    with open(base_dir + "/static/media/skills2.json", "r") as fp:
                        data = json.load(fp)
                except:
                    with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
                        data = json.load(fp)

                if isinstance(parser_output, list):
                    job_title = parser_output[0]["job_title"]
                elif isinstance(parser_output, dict):
                    titles = ["Job Title", "job_title"]
                    for i in titles:
                        if i in parser_output:
                            job_title = parser_output[i]
                            break
                else:
                    job_title = ""

                # for mapping job type in the jd parsing page, if u use this you will get the job type
                if isinstance(parser_output, list):
                    job_type = parser_output[0]["job_type"]
                elif isinstance(parser_output, dict):
                    types = ["Job Type", "job_type","JobType"]
                    job_type = ""
                    for i in types:
                        if i in parser_output:
                            job_type = parser_output[i]
                            break

                else:
                    job_type = ""

                # skills=parser_output['Skills']['Mapped']

                # job_title = re.search(r'<h1>(.*?)</h1>',parser_output,re.DOTALL)
                # job_title = job_title.group(1)
                # html_snippet = re.sub(r'<ul>.*?<li>(.*?)</li>.*?</ul>', r'<p>\1</p>', flags=re.DOTALL)
                skills_match = []
                if isinstance(parser_output, list):
                    skills_match = parser_output[0]["skills"]
                elif isinstance(parser_output, dict):
                    skillswords = ["Skills", "skills"]
                    for key in skillswords:
                        if key in parser_output:
                            if parser_output[key] != ["None"]:
                                skills_match = parser_output[key]
                                break
                    techincal = ["Technical Skills", "Technical skills"]
                    if (
                        skills_match == None
                        or skills_match == "null"
                        or skills_match == "None"
                    ):
                        skills_match = []
                    for i in techincal:
                        if i in parser_output:
                            if (
                                parser_output[i] != ["None"]
                                and parser_output[i] != []
                                and parser_output[i] != "null"
                                and parser_output[i] != None
                                and parser_output[i] != "None"
                            ):
                                if skills_match == []:
                                    skills_match = parser_output[i]
                                else:
                                    flat_list = parser_output[i]
                                    if contains_nested_list(flat_list):
                                        flat_list = [
                                            skill
                                            for sublist in flat_list
                                            for skill in sublist
                                        ]
                                    skills_match.extend(flat_list)
                # try:
                #     try:
                #         skills_match = re.search(r"<h6>Skills:<\/h6>\s*<p>(.*?)<\/p>", html_snippet, re.DOTALL)
                #         skills_match = skills_match.group(1)
                #         if skills_match:
                #             skills_match = skills_match.strip()
                #             skills_match = re.findall(r'\S+', skills_match)
                #     except:
                #         skills_match = re.search(r"<h6>Skills<\/h6>\s*<p>(.*?)<\/p>", html_snippet, re.DOTALL)
                #         skills_match = skills_match.group(1)
                #         skills_match = [skill.strip() for skill in skills_match.split(',')]
                # except:
                #     try:
                #         # if len(skills_match) <= 100:
                #         skills_match = skills_text.strip().split('\n')[1:]
                #         skills_match = [line.split('.', 1)[1].strip() for line in skills_match]
                #     except:
                #         pattern = r"[-–—]\s"
                #         skills_list = re.split(pattern, skills_text)[1:]
                #         skills_match = [skill.strip() for skill in skills_list if skill.strip()]
                skills_list = []
                if skills_match:
                    for idx, skill in enumerate(skills_match):
                        skills_list.append({"id": idx, "skill": skill})
                if "non_ds" in request.POST:
                    print('---------------------')
                    skills_dic = []
                    i = 1
                    for skill in skills_match:
                        skills_dic.append({"skill": skill, "id": i, "exp": 0})
                        i = i + 1

                    context = {
                        "success": True,
                        "qual_name": qual_name,
                        "skills": skills_dic,
                        "job_title": job_title,
                        "job_type": job_type,
                        "job_description": job_description,
                    }
                    print(context,'///////////////////')
                    return Response(context)

                tool = []
                database = []
                platform = []
                misc = []
                programming = []
                d = 1
                if skills_match:
                    if len(skills_match) > 0:
                        for prof in data:
                            for i in data[prof]:
                                for skill in skills_match:
                                    if isinstance(skill, str):
                                        if skill.upper() in data[prof][i]:
                                            if i == "tool":
                                                tool.append(
                                                    {"skill": skill, "id": d, "exp": 0}
                                                )
                                            elif i == "database":
                                                database.append(
                                                    {"skill": skill, "id": d, "exp": 0}
                                                )
                                            elif i == "platform":
                                                platform.append(
                                                    {"skill": skill, "id": d, "exp": 0}
                                                )
                                            elif i == "programming":
                                                programming.append(
                                                    {"skill": skill, "id": d, "exp": 0}
                                                )
                                            else:
                                                misc.append(
                                                    {"skill": skill, "id": d, "exp": 0}
                                                )
                                            d = d + 1
                tool = [
                    dict(tupleized)
                    for tupleized in set(tuple(item.items()) for item in tool)
                ]
                database = [
                    dict(tupleized)
                    for tupleized in set(tuple(item.items()) for item in database)
                ]
                platform = [
                    dict(tupleized)
                    for tupleized in set(tuple(item.items()) for item in platform)
                ]
                programming = [
                    dict(tupleized)
                    for tupleized in set(tuple(item.items()) for item in programming)
                ]
                misc = [
                    dict(tupleized)
                    for tupleized in set(tuple(item.items()) for item in misc)
                ]
                context = {
                    "success": True,
                    "qual_name": qual_name,
                    "tool_skills": tool,
                    "database_skills": database,
                    "platform_skills": platform,
                    "misc_skills": misc,
                    "job_title": job_title,
                    "job_type": job_type,
                    "programming_skills": skills_list,
                    "job_description": job_description,
                }
            elif scan_results["stream"][0] == "FOUND":
                context = {"success": False, "error": "Virus found in submitted file"}
            return Response(context)
        except Exception as e:
            print('exception for jd parser',e)
            return Response(
                {
                    "success": False,
                    "message": "The JD Could Not Parsed Correctly. Please try again",
                    "qual_name": [],
                    "tool_skills": [],
                    "database_skills": [],
                    "platform_skills": [],
                    "misc_skills": [],
                    "job_title": "",
                    "programming_skills": [],
                    "job_description": "",
                }
            )


class duplicate(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request

        jd_id = pk
        jd = (
            JD_form.objects.filter(id=jd_id)
            .annotate(industry_type_name=F("industry_type__value"))
            .values()
        )
        skills = JD_skills_experience.objects.filter(jd_id_id=jd_id).values()
        try:
            location = JD_locations.objects.filter(jd_id_id=jd_id).values()[0]
        except:
            location = {
                "id": 0,
                "jd_id_id": 0,
                "country_id": 0,
                "state_id": 0,
                "city_id": 0,
                "lat": None,
                "lng": None,
                "location": None,
            }
        qualification = JD_qualification.objects.filter(jd_id_id=jd_id).values()
        jd_profile = JD_profile.objects.filter(jd_id_id=jd_id).exists()
        nice_to_have = None
        if jd_nice_to_have.objects.filter(jd_id=jd_id).exists():
            nice_to_have = jd_nice_to_have.objects.get(jd_id=jd_id).nice_to_have
        reparse = 0
        if reparsing_count.objects.filter(jd_id=jd_id).exists():
            reparse = reparsing_count.objects.get(jd_id=jd_id).count
        context = {
            "success": True,
            "jd_output": jd[0],
            "skills": skills,
            "location": location,
            "qualification": qualification,
            "jd_profile": jd_profile,
            "reparse": reparse,
            "nice_to_have": nice_to_have,
        }
        return Response(context)


from django.db import transaction


class inactive_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def get(self, request, pk):
        user_id, updated_by = admin_account(request)
        jd_id = pk

        JD_form.objects.filter(id=jd_id).update(jd_status_id=4)
        logger.info("Inactivated JD successfully!!")
        emp_can = (
            employer_pool.objects.filter(client_id_id=user_id)
            .exclude(candidate_id_id=None)
            .values("candidate_id_id")
        )
        for item in emp_can:
            jd_details = JD_form.objects.get(id=jd_id)
            target_id = Personal_Info.objects.get(
                application_id=item.get("candidate_id_id")
            )
            if applicants_status.objects.filter(
                candidate_id_id__candidate_id_id=item.get("candidate_id_id"),
                jd_id_id=jd_id,
            ).exists():
                data = f"Update: The {JD_form.objects.get(id=jd_id).job_title} you applied for is no longer active."
                notify.send(
                    user_id,
                    recipient=target_id.user_id,
                    description="Inactive",
                    verb=data,
                    action_object=JD_form.objects.get(id=jd_id),
                )
            else:
                data = f"{JD_form.objects.get(id=jd_id).job_title} has been inactivated and is no longer accepting applications."
                notify.send(
                    user_id,
                    recipient=target_id.user_id,
                    description="Inactive",
                    verb=data,
                    action_object=JD_form.objects.get(id=jd_id),
                )
        if email_preference.objects.filter(
            user_id=user_id, stage_id_id=6, is_active=True
        ).exists():
            current_site = settings.CLIENT_URL
            mail_notification(
                user_id,
                "jd_inactive.html",
                "Job Inactivated successfully",
                jd_id=jd_id,
                domain=current_site,
                logo=True,
            )

        try:
            response = requests.get(
                url="http://192.168.3.251:8080/your_endpoint", timeout=1
            )
        except requests.Timeout:
            logger.warning("The remove_case_id request timed out.")
        except requests.RequestException as e:
            logger.error(f"An error occurred while executing remove_case_id: {e}")

        return Response({"success": True})

    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]
    # def get(self, request,pk):
    #     request = self.request
    #     user_id ,updated_by=admin_account(request)
    #     jd_id = pk
    #     JD_form.objects.filter(id=jd_id).update(jd_status_id=int(4))
    #     logger.info("In-activated JD successfully!!")
    #     jd_count=client_features_balance.objects.get(client_id=user_id,feature_id_id=10)
    #     if jd_count.available_count != None :
    #         jd_count.available_count = jd_count.available_count + 1
    #         jd_count.save()
    #     if email_preference.objects.filter(user_id=user_id,stage_id_id=6,is_active=True).exists():
    #         current_site = settings.CLIENT_URL
    #         mail_notification(user_id,'jd_inactive.html','Job inactivated successfully ', jd_id=jd_id,domain=current_site,logo=True)
    #     try:
    #         results =remove_case_id(request=request, can_id=None,jd_id=jd_id)
    #     except:
    #         pass
    #     return Response({'success':True,})


class post_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        jd_id = pk
        user_id, updated_by = admin_account(request)
        jd = JD_form.objects.get(id=jd_id)
        jd_count = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=10
        )
        if jd_count.available_count != None:
            # if jd_count.available_count > 0:
            jd.job_posted_on = datetime.now()
            # jd_count.available_count = jd_count.available_count - 1
            jd.jd_status_id = int(1)
            jd.save()
            UserActivity.objects.create(
                user=request.user,
                action_id=2,
                action_detail=str(jd.job_title) + " (" + str(jd.job_id) + ")",
            )
            # jd_count.save()
            # else:
            #     jd_count.available_count = 0
            #     # jd_count.save()
            #     data={'success':False,'msg':'limit exists'}
            #     return Response(data)
        else:
            jd.job_posted_on = datetime.now()
            jd.jd_status_id = int(1)
            UserActivity.objects.create(
                user=request.user,
                action_id=2,
                action_detail=str(jd.job_title) + " (" + str(jd.job_id) + ")",
            )
            jd.save()
        # result=generate_jd_json(request, pk=jd.id)
        if reparsing_count.objects.filter(jd_id=jd_id).exists():
            reparsing = reparsing_count.objects.filter(jd_id=jd_id).update(
                is_active=True, count=0
            )
        plan_id = subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
        if client_features_balance.objects.filter(
            client_id=user_id, feature_id=57
        ).exists():
            if plan_id == 7 or plan_id == "7":
                if not bulk_matching.objects.filter(jd_id=jd_id).exists():
                    bulk_matching.objects.get_or_create(
                        user_id=user_id, jd_id=jd, is_active=True
                    )
        logger.info("Posting JD " + str(jd))
        current_site = settings.CLIENT_URL
        import time

        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
        except:
            career_page_url = None
        time.sleep(2)
        if email_preference.objects.filter(
            user_id=user_id, stage_id_id=5, is_active=True
        ).exists():
            # hired=Subquery(applicants_status.objects.filter(jd_id=OuterRef('id'),stage_id__stage_name='Hired').values('jd_id').annotate(count=Count('id')).values('count'),output_field=CharField()),
            # try:
            #     result=matching_api_to_db(request,jd_id=pk,can_id=None)
            # except Exception as e:
            #     logger.error("Error in the matching : "+str(e))
            jd_list = JD_form.objects.filter(id=pk)
            jd_list = jd_list.annotate(
                candid=Subquery(
                    employer_pool.objects.filter(
                        client_id=OuterRef("user_id"),
                        first_name__isnull=False,
                        email__isnull=False,
                    )
                    .values("client_id")
                    .annotate(candi_count=Count("id"))
                    .values("candi_count"),
                    output_field=IntegerField(),
                ),
                zmatch=Subquery(
                    zita_match_candidates.objects.filter(
                        status_id=5,
                        candidate_id__first_name__isnull=False,
                        candidate_id__email__isnull=False,
                        jd_id=OuterRef("id"),
                    )
                    .values("jd_id")
                    .annotate(zita_match_count=Count("id"))
                    .values("zita_match_count"),
                    output_field=IntegerField(),
                ),
                zita_match=Case(
                    When(candid=0, then=Value(0)),
                    When(
                        Q(candid__gt=0) & Q(zmatch__isnull=True),
                        then=Value("In Progress"),
                    ),
                    default=Subquery(
                        zita_match_candidates.objects.filter(
                            status_id=5,
                            candidate_id__first_name__isnull=False,
                            candidate_id__email__isnull=False,
                            jd_id=OuterRef("id"),
                        )
                        .values("jd_id")
                        .annotate(zita_match_count=Count("id"))
                        .values("zita_match_count")[:1],
                        output_field=CharField(),
                    ),
                ),
            )

            zita_match_candidate = zita_match_candidates.objects.filter(
                status_id_id=5,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
                jd_id=jd_list[0],
            )[:3]
            domain = settings.CLIENT_URL
            zita_match_candidate = zita_match_candidate.annotate(
                image=Subquery(
                    Profile.objects.filter(
                        user_id=OuterRef("candidate_id__candidate_id__user_id")
                    )[:1].values("image")
                ),
                match=Subquery(
                    Matched_candidates.objects.filter(
                        jd_id=OuterRef("jd_id"), candidate_id=OuterRef("candidate_id")
                    )[:1].values("profile_match")
                ),
            )
            career_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
            context = {
                "user": user_id,
                "jd_form": jd_list[0],
                "zita_match": zita_match_candidate,
                "career_url": career_url,
                "domain": domain,
            }
            email = get_template("email_templates/job_post_confirmation.html")
            email = email.render(context)
            header = "Congratulations!!! Your job has been successfully posted on your career page"
            msg = EmailMultiAlternatives(
                header, email, settings.EMAIL_HOST_USER, [user_id.email]
            )
            msg.attach_alternative(email, "text/html")
            msg.mixed_subtype = "related"
            image_data = [
                "facebook.png",
                "twitter.png",
                "linkedin.png",
                "youtube.png",
                "new_zita_white.png",
                "default.jpg",
            ]
            for i in image_data:
                msg.attach(logo_data(i))
            for p in zita_match_candidate:
                if p.image != None and p.image != "default.jpg":
                    msg.attach(profile(p.image))
            msg.mixed_subtype = "related"
            msg.send()
        emp_can = (
            employer_pool.objects.filter(client_id_id=user_id)
            .exclude(candidate_id_id=None)
            .values("candidate_id_id")
        )
        for item in emp_can:
            if Personal_Info.objects.filter(
                application_id=item.get("candidate_id_id")
            ).exists():
                target_id = Personal_Info.objects.get(
                    application_id=item.get("candidate_id_id")
                )
                data = f"New job alert: {JD_form.objects.get(id=jd_id).job_title} now open for applications."
                notify.send(
                    user_id,
                    recipient=target_id.user_id,
                    description="Newjob",
                    verb=data,
                    action_object=JD_form.objects.get(id=jd_id),
                )

            # ur job has been successfully posted on your career page', jd_id=jd.id,count=0,domain=current_site)

        data = {
            "success": True,
            "url": str(current_site)
            + "/"
            + str(career_page_url)
            + "/career_job_view/"
            + str(jd.id)
            + "/"
            + str(jd.job_title),
        }
        return Response(data)


# class job_post_confirmation(generics.GenericAPIView):
# 	permission_classes = [
# 		permissions.IsAuthenticated
# 	]
# 	def get(self, request,pk):
# 		user_id,updated_by=admin_account(request)
# 		jd = JD_form.objects.get(id=pk)


class questionnaire_save(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        if "is_eeo_comp" in request.GET:
            if request.GET["is_eeo_comp"] == "1":
                eeo = True
            else:
                eeo = False
            JD_form.objects.filter(id=pk).update(is_eeo_comp=eeo)
            return Response({"success": True})

        JD_form.objects.filter(id=pk).update(jd_status_id=5)
        is_ds_role = False
        if not JD_form.objects.filter(id=pk, job_role_id=6).exists():
            is_ds_role = True
        context = {
            "pk": pk,
            "is_ds_role": is_ds_role,
            "applicant_qus": applicant_qus,
        }
        return Response(context)

    def post(self, request, pk):
        request = self.request
        if "temp" in request.POST:
            temp_list = request.POST["temp"].split(",")
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
            context = {"success": True}
            return Response(context)
        if request.POST["required"] == "1":
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
            option = request.POST.getlist("option")[0].split(",")
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
        context = {"success": True}
        return Response(context)

    def delete(self, request):
        applicant_questionnaire.objects.filter(
            id=int(self.request.GET["delete"])
        ).delete()
        context = {"success": True}
        return Response(context)


class questionnaire_templates(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        template = applicant_questionnaire_template.objects.all().values()
        context = {
            "template": template,
        }
        return Response(context)


class questionnaire_for_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request
        user_id, updated_by = admin_account(request)
        if JD_form.objects.get(id=pk).jd_status.id != 6:
            JD_form.objects.filter(id=pk).update(jd_status_id=5)
        applicant_qus = applicant_questionnaire.objects.filter(jd_id_id=pk).values()
        company_name = company_details.objects.get(recruiter_id=user_id).company_name
        try:
            country = JD_locations.objects.get(jd_id_id=pk).country.name
        except:
            country = ""
        is_eeo_comp = JD_form.objects.get(id=pk).is_eeo_comp

        context = {
            "company_name": company_name,
            "questionnaire_for_jd": applicant_qus,
            "is_eeo_comp": is_eeo_comp,
            "country": country,
        }
        return Response(context)

    def delete(self, request, pk):
        applicant_questionnaire.objects.filter(id=pk).delete()
        context = {"success": True}
        return Response(context)


class jd_preview(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):

        request = self.request

        status = JD_form.objects.get(id=pk)
        status.jd_status_id = 6
        status.save()
        user_id, updated_by = admin_account(request)
        jd = JD_form.objects.filter(id=pk).values(
            "job_posted_on",
            "job_title",
            "job_id",
            "no_of_vacancies",
            "job_role__label_name",
            "work_remote",
            "is_ds_role",
            "work_remote",
            "is_eeo_comp",
            "richtext_job_description",
            "industry_type__label_name",
            "salary_min",
            "salary_max",
            "salary_curr_type__value",
            "show_sal_to_candidate",
            "job_type__label_name",
            "jd_status__label_name",
            "min_exp",
            "max_exp",
            "work_space_type",
        )
        try:
            location = JD_locations.objects.filter(jd_id_id=pk).values(
                "country__name",
                "state__name",
                "city__name",
            )[0]
        except:
            location = {
                "id": 0,
                "jd_id_id": 0,
                "country_id": 0,
                "state_id": 0,
                "city_id": 0,
                "lat": None,
                "lng": None,
                "location": None,
            }
        skills = JD_skills_experience.objects.filter(jd_id_id=pk).values()
        qualification = JD_qualification.objects.filter(jd_id_id=pk).values()
        applicant_qus = applicant_questionnaire.objects.filter(jd_id_id=pk).values()

        # profile = JD_profile.objects.filter(jd_id_id=pk).values()[0]
        try:
            profile = JD_profile.objects.filter(jd_id_id=pk).values()[0]
            recommended_role = JD_profile.objects.get(
                jd_id_id=pk
            ).recommended_role.label_name
        except:
            recommended_role = None
            profile = None
        try:
            plan_id = subscriptions.objects.get(
                is_active=True, client_id=user_id
            ).plan_id
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
        company_detail = company_details.objects.filter(recruiter_id=user_id).values()
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
        except:
            career_page_url = None

        reparse = 0
        if reparsing_count.objects.filter(jd_id=pk).exists():
            reparse = reparsing_count.objects.get(jd_id=pk).count
        if "Nice_to_Have" in request.GET:
            nice_to_have = request.GET["Nice_to_Have"]
            if nice_to_have:
                if jd_nice_to_have.objects.filter(jd_id=pk).exists():
                    jd_nice_to_have.objects.filter(jd_id=pk).update(
                        nice_to_have=string_checking(nice_to_have)
                    )
                else:
                    jd_nice_to_have.objects.create(
                        jd_id=pk,
                        user_id=user_id,
                        nice_to_have=string_checking(nice_to_have),
                    )
        else:
            nice_to_have = None

        #    nice_to_have = jd_nice_to_have.objects.get(jd_id=pk).nice_to_have

        context = {
            "jd": jd[0],
            "has_external_posting": has_external_posting,
            "available_jobs": available_jobs,
            "location": location,
            "skills": skills,
            "career_page_url": career_page_url,
            "qualification": qualification,
            "recommended_role": recommended_role,
            "profile": profile,
            "company_detail": company_detail[0],
            "questionnaire": applicant_qus,
            "reparse": reparse,
            "nice_to_have": nice_to_have,
        }
        return Response(context)


class jd_view(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):

        request = self.request

        user_id, updated_by = admin_account(request)
        jd = JD_form.objects.filter(id=pk).values(
            "job_posted_on",
            "job_title",
            "job_id",
            "no_of_vacancies",
            "id",
            "job_role__label_name",
            "work_remote",
            "is_ds_role",
            "work_remote",
            "is_eeo_comp",
            "richtext_job_description",
            "industry_type__label_name",
            "salary_min",
            "salary_max",
            "salary_curr_type__value",
            "show_sal_to_candidate",
            "job_type__label_name",
            "jd_status__label_name",
            "min_exp",
            "max_exp",
            "work_space_type",
        )
        try:
            location = JD_locations.objects.filter(jd_id_id=pk).values(
                "country__name",
                "state__name",
                "city__name",
            )[0]
        except:
            location = {"country__name": "", "state__name": "", "city__name": ""}
        skills = JD_skills_experience.objects.filter(jd_id_id=pk).values()
        qualification = JD_qualification.objects.filter(jd_id_id=pk).values()
        applicant_qus = applicant_questionnaire.objects.filter(jd_id_id=pk).values()

        try:
            profile = JD_profile.objects.filter(jd_id_id=pk).values()[0]
            recommended_role = JD_profile.objects.get(
                jd_id_id=pk
            ).recommended_role.label_name
        except:
            recommended_role = None
            profile = None
        try:
            plan_id = subscriptions.objects.get(
                is_active=True, client_id=user_id
            ).plan_id
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
        company_detail = company_details.objects.filter(recruiter_id=user_id).values()
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=user_id
            ).career_page_url
        except:
            career_page_url = None
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
        int_list["posted_at"] = JD_form.objects.get(id=pk).job_posted_on.date()
        try:
            from django.utils import timezone

            active_for = (
                timezone.now().date() - JD_form.objects.get(id=pk).job_posted_on.date()
            )
            if active_for.days < 2:
                int_list["active_for"] = (
                    str(active_for.days)
                    + " day (Since "
                    + str(
                        JD_form.objects.get(id=pk)
                        .job_posted_on.date()
                        .strftime("%b %d, %Y")
                    )
                    + ")"
                )
            else:
                int_list["active_for"] = (
                    str(active_for.days)
                    + " days (Since "
                    + str(
                        JD_form.objects.get(id=pk)
                        .job_posted_on.date()
                        .strftime("%b %d, %Y")
                    )
                    + ")"
                )
        except:
            int_list["active_for"] = "NA"

        status_id = JD_form.objects.filter(id=pk).values("jd_status_id")[0][
            "jd_status_id"
        ]
        int_list["jd_status"] = tmeta_jd_status.objects.filter(id=status_id).values(
            "value"
        )[0]["value"]
        if employer_pool.objects.filter(user_id=user_id, can_source_id=5).exists():
            int_list["zita_match"] = zita_match_candidates.objects.filter(
                jd_id_id=pk, status_id_id=5, candidate_id__first_name__isnull=False
            ).count()
        else:
            int_list["zita_match"] = zita_match_candidates.objects.filter(
                jd_id_id=pk,
                status_id_id=5,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
            ).count()
        # int_list['applicants'] = applicants_status.objects.filter(jd_id_id=pk,stage_id=None).count()
        int_list["applicants"] = applicants_status.objects.filter(
            jd_id_id=pk,
            candidate_id__first_name__isnull=False,
            candidate_id__email__isnull=False,
        ).count()

        int_list["shortlisted"] = (
            applicants_status.objects.filter(
                jd_id_id=pk, stage_id__stage_name="Shortlisted"
            )
            .distinct()
            .count()
        )
        int_list["offered"] = (
            applicants_status.objects.filter(jd_id_id=pk, stage_id__stage_name="Hired")
            .distinct()
            .count()
        )
        int_list["invite"] = (
            Candi_invite_to_apply.objects.filter(jd_id_id=pk).distinct().count()
        )
        int_list["rejected"] = applicants_status.objects.filter(
            jd_id_id=pk, stage_id__stage_name="Rejected"
        ).count()
        job_count = (
            job_view_count.objects.filter(jd_id_id=pk)
            .values("source")
            .annotate(counts=Sum("count"))
            .aggregate(Sum("counts"))
        )

        if job_count["counts__sum"] == None:
            int_list["views"] = 0
        else:
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
            applicants_status.objects.filter(
                jd_id_id=pk, status_id_id__in=[1, 2, 3, 4, 7]
            )
            .annotate(label=YearWeek("created_on"))
            .values("label")
            .annotate(y=Count("id"))
        )

        posted_date = JD_form.objects.get(id=pk).job_posted_on
        posted_date = posted_date.strftime("%b-%d")
        date_list1.insert(0, {"label": posted_date, "y": 0})
        date_list2.insert(0, {"label": posted_date, "y": 0})
        role_base = [date_list1, date_list2]
        ext_jobs = external_jobpostings_by_client.objects.filter(
            jd_id_id=pk, is_active=True
        ).values()
        dates = 1
        if len(date_list1) == 1 and len(date_list2) == 1:
            dates = 0
        if jd_nice_to_have.objects.filter(jd_id=pk).exists():
            nice_to_have = jd_nice_to_have.objects.get(jd_id=pk).nice_to_have
        else:
            nice_to_have = None

        context = {
            "jd": jd[0],
            "has_external_posting": has_external_posting,
            "available_jobs": available_jobs,
            "location": location,
            "skills": skills,
            "dates": dates,
            "ext_jobs": ext_jobs,
            "career_page_url": career_page_url,
            "qualification": qualification,
            "recommended_role": recommended_role,
            "profile": profile,
            "job_view_line": date_list1,
            "applicants_line": date_list2,
            "int_list": int_list,
            "company_detail": company_detail[0],
            "questionnaire": applicant_qus,
            "nice_to_have": nice_to_have,
        }
        return Response(context)


class job_view_count_fun(generics.GenericAPIView):

    def get(self, request, pk):
        source = request.GET["source"]
        from django.utils import timezone

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

        return Response({"data": source})


class my_job_posting(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        request = self.request

        admin_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        user = User.objects.get(username=request.user).id
        logger.info("In create_job_listing function - User ID: " + str(user))
        jd_list = JD_form.objects.filter(user_id=admin_id)
        jd_ids = jd_list.filter(jd_status_id=1).values_list("id", flat=True).distinct()
        # for i in jd_ids:
        #     try:
        #         result=matching_api_to_db(request,jd_id=i,can_id=None)
        #     except Exception as e:
        #         logger.error("Error in the matching : "+str(e))
        title = list(jd_list.values_list("job_title", flat=True).distinct())
        job_ids = list(jd_list.values_list("job_id", flat=True).distinct())
        location = JD_locations.objects.filter(
            jd_id__in=jd_list.values_list("id", flat=True).distinct()
        )
        location = location.annotate(
            countries=Subquery(
                Country.objects.filter(id=OuterRef("country"))[:1].values("name")
            ),
            states=Subquery(
                State.objects.filter(id=OuterRef("state"))[:1].values("name")
            ),
            cities=Subquery(
                City.objects.filter(id=OuterRef("city"))[:1].values("name")
            ),
        )
        location = location.annotate(
            loc=Concat(
                "cities",
                V(", "),
                "states",
                V(", "),
                "countries",
                output_field=CharField(),
            )
        )

        Jobs_List = 0
        if jd_list.exists():
            Jobs_List = 1

        location_list = list(
            location.values_list("loc", flat=True).exclude(loc__isnull=True).distinct()
        )
        job_title = list(jd_list.values_list("job_title", flat=True).distinct())

        context = {
            "location_list": location_list,
            "job_ids": job_ids,
            "job_title": job_title,
        }

        return Response(context)


class my_job_posting_data(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        request = self.request
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
            states=Subquery(
                State.objects.filter(id=OuterRef("state"))[:1].values("name")
            ),
            cities=Subquery(
                City.objects.filter(id=OuterRef("city"))[:1].values("name")
            ),
        )
        location = location.annotate(
            loc=Concat(
                "cities",
                V(", "),
                "states",
                V(", "),
                "countries",
                output_field=CharField(),
            )
        ).values()
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=admin_id
            ).career_page_url
        except:
            career_page_url = None

        candidate = 0
        applicants_total_count = 0
        from django.db.models import Count, Q

        total_jobs = (
            applicants_status.objects.filter(jd_id__in=jd_list)
            .exclude(stage_id__stage_name__isnull=True)
            .values("jd_id", "stage_id__stage_name")
            .annotate(
                count=Count("stage_id__stage_name")
                + Count("stage_id", filter=Q(stage_id__stage_name=None))
            )
            .order_by("jd_id")
        )

        total_jobs_list = list(total_jobs)
        count_values = [item["count"] for item in total_jobs_list]
        applicants_total_count = sum(count_values)
        candidate = total_jobs.filter(count=0).count()

        Jobs_List = 1
        if jd_list.exists():
            Jobs_List = 2
        candidate_count = 0
        features, plans = plan_checking(admin_id, "resume")
        candidate_count = jd_list.aggregate(
            applicants=Sum(
                Case(
                    When(applicants_status__stage_id=None, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            shortlisted=Sum(
                Case(
                    When(applicants_status__stage_id__stage_name="Shortlisted", then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            Offered=Sum(
                Case(
                    When(applicants_status__stage_id__stage_name="Hired", then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            rejected=Sum(
                Case(
                    When(applicants_status__stage_id__stage_name="Rejected", then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        jd_list = jd_list.annotate(
            applicants=Subquery(
                applicants_status.objects.filter(
                    jd_id=OuterRef("id"),
                    candidate_id__first_name__isnull=False,
                    candidate_id__email__isnull=False,
                )
                .values("jd_id")
                .annotate(count=Count("id"))
                .values("count"),
                output_field=CharField(),
            ),
            shortlisted=Subquery(
                applicants_status.objects.filter(
                    jd_id=OuterRef("id"), stage_id__stage_name="Shortlisted"
                )
                .values("jd_id")
                .annotate(count=Count("id"))
                .values("count"),
                output_field=CharField(),
            ),
            hired=Subquery(
                applicants_status.objects.filter(
                    jd_id=OuterRef("id"), stage_id__stage_name="Hired"
                )
                .values("jd_id")
                .annotate(count=Count("id"))
                .values("count"),
                output_field=CharField(),
            ),
            rejected=Subquery(
                applicants_status.objects.filter(
                    jd_id=OuterRef("id"), stage_id__stage_name="Rejected"
                )
                .values("jd_id")
                .annotate(count=Count("id"))
                .values("count"),
                output_field=CharField(),
            ),
            location_jd=Subquery(
                location.filter(jd_id=OuterRef("id"))
                .values("jd_id")
                .annotate(name=Count("state"))
                .values("name")[:1]
            ),
            invite_to_apply=Subquery(
                Candi_invite_to_apply.objects.filter(
                    jd_id=OuterRef("id"), is_interested=None
                )
                .values("jd_id")
                .annotate(count=Count("candidate_id"))
                .values("count"),
                output_field=CharField(),
            ),
            interested=Subquery(
                jd_candidate_analytics.objects.filter(
                    jd_id=OuterRef("id"), status_id=5
                ).values("interested")[:1]
            ),
            job_posted_on_date=Case(
                When(job_reposted_on__isnull=False, then="job_reposted_on"),
                default=F("job_posted_on"),
            ),
            location=Subquery(
                location.filter(jd_id=OuterRef("id"))
                .values("jd_id")
                .annotate(name=Concats("loc"))[:1]
                .values("name"),
                output_field=CharField(),
            ),
            whatjobs=Subquery(
                whatjob_activity.objects.filter(jd_id=OuterRef("id")).values("whatjob"),
                output_field=CharField(),
            ),
        ).order_by("-job_posted_on_date")
        if employer_pool.objects.filter(user_id=admin_id, can_source_id=5).exists():
            jd_list = jd_list.annotate(
                zita_match=Subquery(
                    zita_match_candidates.objects.filter(
                        status_id_id=5,
                        candidate_id__first_name__isnull=False,
                        jd_id=OuterRef("id"),
                    )
                    .values("status_id")
                    .annotate(cout=Count("candidate_id"))
                    .values("cout"),
                    output_field=CharField(),
                ),
            )
            zita_count = (
                zita_match_candidates.objects.filter(
                    status_id=5, candidate_id__first_name__isnull=False
                )
                .values("jd_id")
                .annotate(candidate_count=Count("candidate_id", distinct=True))
                .values_list("jd_id", "candidate_count")
            )
        else:
            jd_list = jd_list.annotate(
                zita_match=Subquery(
                    zita_match_candidates.objects.filter(
                        status_id_id=5,
                        candidate_id__first_name__isnull=False,
                        candidate_id__email__isnull=False,
                        jd_id=OuterRef("id"),
                    )
                    .values("status_id")
                    .annotate(cout=Count("candidate_id"))
                    .values("cout"),
                    output_field=CharField(),
                ),
            )
            zita_count = (
                zita_match_candidates.objects.filter(
                    status_id=5,
                    candidate_id__first_name__isnull=False,
                    candidate_id__email__isnull=False,
                )
                .values("jd_id")
                .annotate(candidate_count=Count("candidate_id", distinct=True))
                .values_list("jd_id", "candidate_count")
            )

        filters = JobFilter(request.GET, queryset=jd_list)
        final_list = filters.qs
        if "posted_on" in request.GET and request.GET["posted_on"] != "":
            date_posted = request.GET["posted_on"]
            timezone = pytz.timezone("UTC")
            today = datetime.now(timezone)
            date = today - timedelta(days=int(date_posted))

            final_list = final_list.filter(job_posted_on__range=(date, today))

            # date = today - timezone.timedelta(days=int(date_posted))
        if "jd_status" in request.GET and request.GET["jd_status"] != "":
            status = request.GET["jd_status"].split(",")
            final_list = final_list.filter(jd_status_id__in=status)
        if "remote" in request.GET and request.GET["remote"] != "":
            if request.GET["remote"].lower() == "true":
                final_list = final_list.filter(work_space_type=int(3))
        len_list = final_list.count()
        page = request.GET.get("page", 1)
        page_count = request.GET.get("pagecount", None)
        if pagination.objects.filter(user_id=request.user, page_id=1).exists():
            if page_count:
                pagination.objects.filter(user_id=request.user, page_id=1).update(
                    pages=page_count
                )
            page_count = pagination.objects.get(user_id=request.user, page_id=1).pages
        elif not pagination.objects.filter(user_id=request.user, page_id=1).exists():
            page_count = tmete_pages.objects.get(id=1).default_value
        paginator = Paginator(final_list, page_count)
        try:
            final_list = paginator.page(page)
        except PageNotAnInteger:
            final_list = paginator.page(1)
        except EmptyPage:
            final_list = paginator.page(paginator.num_pages)
        final_list = final_list.object_list.values(
            "applicants",
            "hired",
            "rejected",
            "id",
            "shortlisted",
            "invite_to_apply",
            "interested",
            "job_posted_on_date",
            "location",
            "job_title",
            "job_id",
            "is_ds_role",
            "job_type",
            "zita_match",
            "jd_status__label_name",
            "work_space_type",
        )
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop("page", True) and get_dict_copy.urlencode()
        domain = settings.CLIENT_URL
        availble_jobs = client_features_balance.objects.get(
            client_id=admin_id, feature_id=10
        ).available_count
        feature_value, plan = plan_checking(admin_id, "job")
        add_jdcredits = client_features_balance.objects.filter(
            client_id=admin_id, feature_id=51
        ).exists()
        active_jobs = JD_form.objects.filter(user_id=admin_id).values_list(
            "id", flat=True
        )[: int(feature_value)]
        context = {
            "Candidate_Count": candidate_count,
            "final_list": final_list,
            "career_page_url": career_page_url,
            "len_list": len_list,
            "Jobs_List": Jobs_List,
            "params": params,
            "availble_count": availble_jobs,
            "active_jobs": active_jobs,
            "add_jdcredits": add_jdcredits,
            "location": location,
            "zita_count": zita_count,
            "domain": domain,
        }
        return Response(context)


class dashboard(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user = request.user
        admin_id, updated_by = admin_account(self.request)
        try:
            company_name = Signup_Form.objects.get(user_id=admin_id).company_name
        except:
            company_name = "-"
        total_jobs = (
            JD_form.objects.filter(user_id=admin_id, jd_status_id__in=[1, 4])
            .values_list("id", flat=True)
            .distinct()
        )
        applicants = (
            applicants_status.objects.filter(
                client_id=admin_id,
                stage_id__isnull=True,
                candidate_id__first_name__isnull=False,
                candidate_id__email__isnull=False,
                candidate_id__candidate_id__isnull=False,
            )
            .exclude(jd_id=None)
            .exclude(jd_id=2389)
            .count()
        )
        offered = applicants_status.objects.filter(
            client_id=admin_id, stage_id__stage_name="Hired"
        ).count()
        job_count = (
            job_view_count.objects.filter(jd_id_id__in=total_jobs)
            .values("source")
            .annotate(count=Sum("count"))
            .order_by("-count")
        )
        viewed = employer_pool.objects.filter(
            client_id=admin_id, can_source_id__in=[2, 5]
        ).count()
        rejected = applicants_status.objects.filter(
            client_id=admin_id, stage_id__stage_name="Rejected"
        ).count()
        invite_to_apply = Candi_invite_to_apply.objects.filter(
            client_id=admin_id
        ).count()
        shortlisted = applicants_status.objects.filter(
            client_id=admin_id, stage_id__stage_name="Shortlisted"
        ).count()
        try:
            jobs_last_update = (
                JD_form.objects.filter(user_id=admin_id).last().created_on
            )
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
                Candi_invite_to_apply.objects.filter(client_id=admin_id)
                .last()
                .created_at
            )
        except AttributeError:
            invite_to_apply_last_update = None
        try:
            shortlisted_last_update = (
                applicants_status.objects.filter(
                    client_id=admin_id, status_id__in=[2, 3]
                )
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
        try:
            plan = subscriptions.objects.filter(client_id=admin_id).last()
            plan = subscriptions.objects.filter(subscription_id=plan.pk).values()
            plan = plan.annotate(
                plan_name=Subquery(
                    tmeta_plan.objects.filter(plan_id=OuterRef("plan_id")).values(
                        "plan_name"
                    )[:1]
                ),
                validate=Length(
                    Subquery(
                        tmeta_plan.objects.filter(plan_id=OuterRef("plan_id")).values(
                            "subscription_value_days"
                        )[:1]
                    )
                ),
                is_month=Case(
                    When(validate__exact=2, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
                plan_status=Case(
                    When(is_month=True, then=Value("Monthly")),
                    default=Value("Annual"),
                    output_field=CharField(),
                ),
            )[0]
        except:
            plan = None
        try:
            job_count = client_features_balance.objects.get(
                client_id=admin_id, feature_id_id=10
            ).available_count
        except:
            job_count = None
        try:
            contact_count = client_features_balance.objects.get(
                client_id=admin_id, feature_id_id=53
            ).available_count
        except:
            contact_count = None
        try:
            candidate_count = client_features_balance.objects.get(
                client_id=admin_id, feature_id_id=27
            ).available_count
        except:
            candidate_count = None
        total_count = Recommended_Role.objects.all().distinct().count()
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=admin_id
            ).career_page_url
        except:
            career_page_url = ""
        if os.path.exists(
            base_dir + "/media/user_bin/" + str(request.user.id) + "_token_google.json"
        ):
            f = open(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_google.json",
                "r",
            )
            google = json.load(f)
        else:
            google = None
        if not email_preference.objects.filter(user_id=request.user).exists():
            meta_email = tmeta_email_preference.objects.all()
            for i in meta_email:
                email_preference.objects.create(
                    user_id=request.user, stage_id_id=i.id, is_active=i.is_active
                )
        if os.path.exists(
            base_dir + "/media/user_bin/" + str(request.user.id) + "_token_outlook.json"
        ):
            f = open(
                base_dir
                + "/media/user_bin/"
                + str(request.user.id)
                + "_token_outlook.json",
                "r",
            )
            outlook = json.load(f)
        else:
            outlook = None
        domain = settings.CLIENT_URL
        user_info = User.objects.filter(id=request.user.id).values()[0]
        if "time_zone" in request.GET:
            time_zone = request.GET["time_zone"]
            user_info["last_login"] = last_login(
                User.objects.get(id=request.user.id).last_login, time_zone
            )
        user_credit = user_credits(admin_id)
        unlimited = unlimited_addons(admin_id)
        expire_content = expire_details(admin_id)
        plan_id = subscriptions.objects.filter(client_id=admin_id).last()
        expire_status = plan_id.subscription_valid_till
        today_date = datetime.now()
        expire_status = comparative(today_date, expire_status)
        addon_details = (
            client_features_balance.objects.filter(client_id=admin_id)
            .values("id", "feature_id", "feature_id__feature_name", "available_count")
            .exclude(feature_id__in=[51, 52, 58, 56])
        )
        addon_details = addon_details.annotate(
            usage=Case(
                When(available_count__isnull=False, then=F("available_count")),
                default=Value("Unlimited"),
                output_field=CharField(),
            ),
            name=Case(
                When(feature_id=10, then=Value("Job Posting")),
                When(feature_id=27, then=Value("AI Resume Parsing")),
                When(
                    feature_id=60,
                    then=Value(
                        "AI Resume Comparitive Analysis & Recommendation to Hire"
                    ),
                ),
                When(feature_id=53, then=Value("Sourcing Contact Unlock")),
                When(feature_id=59, then=Value("AI Interview Questions Generation")),
                When(feature_id=61, then=Value("Priority Support")),
                When(feature_id=62, then=Value("AI Resume Matching for Multiple Jobs")),
                When(
                    feature_id=6, then=Value("AI Matching with Descriptive Analytics")
                ),
                When(feature_id=64, then=Value("External Job Posting")),
                default=Value(None),  # Default value if none of the conditions match
                output_field=CharField(),
            ),
        )
        addon_details = orderby_addons(addon_details)
        client_url = settings.CLIENT_URL
        context = {
            "company_name": company_name,
            "total_jobs": len(total_jobs),
            "jobs_last_update": jobs_last_update,
            "applicants_last_update": applicants_last_update,
            "viewed_last_update": viewed_last_update,
            "outlook": outlook,
            "domain": domain,
            "career_page_url": career_page_url,
            "google": google,
            "logo": str(logo),
            "job_count": job_count,
            "user_info": user_info,
            "contact_count": contact_count,
            "Resume_parsing_count": int(50),
            "candidate_count": candidate_count,
            "rejected_last_update": rejected_last_update,
            "invite_to_apply_last_update": invite_to_apply_last_update,
            "shortlisted_last_update": shortlisted_last_update,
            "selected_last_update": selected_last_update,
            "applicants": applicants,
            "shortlisted": shortlisted,
            "selected": offered,
            "viewed": viewed,
            "plan": plan,
            "rejected": rejected,
            "invite_to_apply": invite_to_apply,
            "jd_metrics": jd_metrics,
            "user_credits": user_credit,
            "expire_details": expire_content,
            "addon_details": addon_details,
            "expire_status": expire_status,
            "client_url": client_url,
            "unlimited_addons": unlimited,
        }
        return Response(context)


from dateutil import tz, parser


class dashboard_calender(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        req = request
        request = self.request
        user_id = request.user
        events = Event.objects.filter(user=request.user)
        date = request.GET["date"]
        if "time_zone" in request.GET:
            time_zone = request.GET["time_zone"]
        else:
            time_zone = "Asia/Calcutta"
        # time_zone = request.GET['time_zone']
        try:
            if google_return_details.objects.filter(client_id=user_id).exists():
                date = request.GET["date"]
                now = datetime.strptime(date, "%Y-%m-%d").replace(
                    tzinfo=pytz.timezone(time_zone)
                )
                timeMax = datetime(
                    year=now.year,
                    month=now.month,
                    day=now.day,
                    tzinfo=pytz.timezone(time_zone),
                ) + timedelta(days=1)
                timeMax = timeMax.isoformat()
                now = now.isoformat()
                authcreds = Google.get_auth_credentials(request)
                service = build("calendar", "v3", credentials=authcreds)
                eventsResult = (
                    service.events()
                    .list(
                        calendarId="primary",
                        timeMin=now,
                        timeMax=timeMax,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                events = eventsResult.get("items", [])
                for event in events:
                    try:
                        event["start"]["dateTime"] = datetime.strftime(
                            parser.parse(event["start"]["dateTime"]),
                            "%Y-%m-%d %H:%M:%S",
                        )
                        event["end"]["dateTime"] = datetime.strftime(
                            parser.parse(event["end"]["dateTime"]), "%Y-%m-%d %H:%M:%S"
                        )
                        event["start_time"] = event["start"]["dateTime"]
                        event["end_time"] = event["end"]["dateTime"]
                        event["title"] = event["summary"]
                        if "hangoutLink" in event:
                            event["web_url"] = event["hangoutLink"]
                        if "hangoutLink" not in event:
                            if "description" in event:
                                content = event["description"]
                                lines = content.split("\n")
                                try:
                                    join_index = lines.index("Join Teams Meeting")
                                    # Extract the URL by fetching the next line
                                    url = (
                                        lines[join_index + 2]
                                        if join_index + 2 < len(lines)
                                        else None
                                    )
                                    if url:
                                        event["hangoutLink"] = url
                                        event["eventId"] = CalEvents.objects.get(
                                            join_url=url
                                        ).eventId
                                        event["slotter"] = (
                                            Interview_slot.objects.filter(
                                                interview_id__eventId=event["eventId"],
                                                event_id__event_type__in=[
                                                    "Google Hangouts/Meet",
                                                    "Microsoft Teams",
                                                ],
                                            ).exists()
                                        )
                                except:
                                    pass
                    except Exception as e:
                        event["start"]["dateTime"] = datetime.strftime(
                            parser.parse(event["start"]["date"]), "%Y-%m-%d %H:%M:%S"
                        )
                        event["end"]["dateTime"] = datetime.strftime(
                            parser.parse(event["end"]["date"]), "%Y-%m-%d %H:%M:%S"
                        )
                account = "GOOGLE"
                context = {"events": events, "account": account}
            elif outlook_return_details.objects.filter(client_id=user_id).exists():
                date = request.GET["date"]
                date = datetime.strptime(date, "%Y-%m-%d")
                end = date + timedelta(days=1)
                with open(Outlook.token_path(request), "r") as f:
                    temp2 = json.load(f)
                token = temp2["access_token"]
                start = utc_to_timezone(date.isoformat(timespec="seconds"), time_zone)
                end = utc_to_timezone(end.isoformat(timespec="seconds"), time_zone)
                events = get_calendar_events(token, start, end, time_zone)
                if "error" in events:
                    refresh_token = Outlook.get_token_from_refresh_token(request)
                    with open(
                        Outlook.auth_token_path(request),
                        "r",
                    ) as f:
                        temp2 = json.load(f)
                    today = datetime.now().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    token = temp2["access_token"]
                    if today.weekday() != 6:
                        start = today - timedelta(days=today.isoweekday())
                    else:
                        start = today
                    end = start + timedelta(days=120)
                    events = get_calendar_events(
                        get_calendar_events(token, start, end, time_zone)
                    )
                if events:
                    for event in events["value"]:
                        event["start"]["dateTime"] = parser.parse(
                            str(event["start"]["dateTime"])
                        )
                        event["end"]["dateTime"] = parser.parse(
                            str(event["end"]["dateTime"])
                        )
                        event["title"] = event["subject"]
                        event["start_time"] = event["start"]["dateTime"]
                        event["end_time"] = event["end"]["dateTime"]
                        event["web_url"] = event["webLink"]
                        event["slotter"] = Interview_slot.objects.filter(
                            interview_id__eventId=event["id"],
                            event_id__event_type__in=[
                                "Google Hangouts/Meet",
                                "Microsoft Teams",
                            ],
                        ).exists()
                    # context['events'] = events['value']
                    context = {"events": events["value"], "account": "OUTLOOK"}
                else:
                    context = {"events": [], "account": "OUTLOOK"}
            else:
                context = {"events": [], "account": ""}
        except Exception as e:
            context = {"events": [], "Error": str(e), "account": ""}
        return Response(context)


class dashboard_message(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
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
                Message.objects.filter(
                    sender=OuterRef("sender"), jd_id=OuterRef("jd_id")
                )
                .values("text")
                .order_by("-date_created")[:1]
            ),
            is_read=Subquery(
                Message.objects.filter(
                    sender=OuterRef("sender"), jd_id=OuterRef("jd_id")
                )
                .values("is_read")
                .order_by("-date_created")[:1]
            ),
            time=Subquery(
                Message.objects.filter(
                    sender=OuterRef("sender"), jd_id=OuterRef("jd_id")
                )
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
            can_source=Subquery(
                employer_pool.objects.filter(candidate_id__user_id=OuterRef("sender"))[
                    :1
                ].values("can_source__value")
            ),
        ).values()

        message_count = len(message)
        context = {
            "message": message,
            "message_count": message_count,
        }
        return Response(context)


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


class download_jd(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        pk = request.GET["jd_id"]
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
        work_space_type = int(jd_form.work_space_type)
        if work_space_type == 1:
            work_space_type = "Onsite"
        elif work_space_type == 2:
            work_space_type = "Hybrid"
        elif work_space_type == 3:
            work_space_type = "Remote"
        else:
            work_space_type = ""
        params = {
            "jd_form": jd_form,
            "skill": skill,
            "location": location,
            "education": education,
            "is_profiled": is_profiled,
            "work_space_type": work_space_type,
        }
        import pdfkit

        html_template = (
            get_template("pdf/jd_download.html").render(params).encode(encoding="UTF-8")
        )
        pdf_file = HTML(
            string=html_template, base_url=settings.profile_pdf_url
        ).write_pdf()
        f = open(base_dir + "/media/jd_" + str(jd_form.job_id) + ".pdf", "wb")
        f.write(pdf_file)

        # config = pdfkit.configuration(wkhtmltopdf="C:\Program Files\wkhtmltopdf\wkhtmltopdf.exe")

        # html_template = get_template('pdf/jd_download.html').render(params).encode(encoding="UTF-8")
        # pdf_file = pdfkit.from_string(html_template, False, options={'base_url': settings.profile_pdf_url}, configuration=config)

        # with open(base_dir+'/media/jd_'+str(jd_form.job_id)+'.pdf', 'wb') as f:
        #     f.write(pdf_file)
        # import pdfkit

        # config = pdfkit.configuration(wkhtmltopdf="C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe")

        # html_template = get_template('pdf/jd_download.html').render(params)

        # pdf_file = pdfkit.from_string(html_template, False, options={'--base-url': settings.profile_pdf_url}, configuration=config)

        # with open(base_dir+'/media/jd_'+str(jd_form.job_id)+'.pdf', 'wb') as f:
        #     f.write(pdf_file)

        domain = get_current_site(request)
        return JsonResponse(
            {
                "file_path": "https://"
                + str(domain)
                + "/media/jd_"
                + str(jd_form.job_id)
                + ".pdf"
            }
        )


# class download_jd(generics.GenericAPIView):
#     permission_classes = [
#         permissions.IsAuthenticated
#     ]
#     def get(self,request):
#         request = self.request
#         pk=request.GET['jd_id']
#         jd_form = JD_form.objects.get(id=pk)
#         skill = JD_skills_experience.objects.filter(jd_id_id=pk)
#         location = JD_locations.objects.filter(jd_id_id=pk)
#         location = [(City.objects.filter(id=i['city']).values('name')[0]['name'],State.objects.filter(id=i['state']).values('name')[0]['name'],Country.objects.filter(id=i['country']).values('name')[0]['name']) for i in JD_locations.objects.filter(jd_id_id=pk).values('country','state','city')]

#         education = [(i['qualification'],i['specialization']) for i in JD_qualification.objects.filter(jd_id_id=pk).values('qualification','specialization')]

#         prof=list(JD_profile.objects.filter(jd_id_id=pk).values('business_intelligence','data_analysis','data_engineering','devops','machine_learning','others',))
#         if len(prof) > 0 :
#             try:
#                 pie_chart(request,prof,filename='jd_'+str(pk))
#                 is_profiled = 1
#             except IndexError:
#                 is_profiled = 0
#         else:
#             is_profiled = 0
#         params = {'jd_form':jd_form,'skill':skill,'location':location,'education':education,'is_profiled':is_profiled}


#         html_template = get_template('pdf/jd_download.html').render(params).encode(encoding="UTF-8")
#         pdf_file = HTML(string=html_template,base_url=settings.profile_pdf_url).write_pdf()
#         f = open(base_dir+'/media/jd_'+str(jd_form.job_id)+'.pdf', 'wb')
#         f.write(pdf_file)
#         domain =request.build_absolute_uri('/')
#         return JsonResponse({'file_path':str(domain)+'media/jd_'+str(jd_form.job_id)+'.pdf'})

from jobs.candidate_data import get_app_prof_details


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


class download_profile(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        jd = None
        request = self.request
        pk = request.GET["can_id"]

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
            is_applicant = 1
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
                        epf=False,
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
                    request,
                    main_prof_dict[r],
                    filename="chart_" + str(r) + str(user_id),
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
        pdf_file = HTML(
            string=html_template, base_url=settings.profile_pdf_url
        ).write_pdf()

        f = open(base_dir + "/media/Profile.pdf", "wb")
        f.write(pdf_file)
        domain = get_current_site(request)
        return JsonResponse({"file_path": str(domain) + "/media/Profile.pdf"})


class dashboard_job_metrics(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        pk = request.GET["jd_id"]
        # pk=101
        admin_id, updated_by = admin_account(request)
        job_count = (
            job_view_count.objects.filter(jd_id_id=pk)
            .values("source")
            .annotate(count=Sum("count"))
            .order_by("-count")
        )
        total_count = job_count.aggregate(Sum("count"))
        role_base1 = []
        role_base2 = []
        posted_channel = external_jobpostings_by_client.objects.filter(
            jd_id_id=pk
        ).count()
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
            applicants_status.objects.filter(
                jd_id_id=pk, status_id_id__in=[1, 2, 3, 4, 7]
            )
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
        Shortlisted = pipeline_view.objects.filter(
            jd_id=pk, stage_name="Shortlisted"
        ).values("id")
        Offered = pipeline_view.objects.filter(jd_id=pk, stage_name="Hired").values(
            "id"
        )
        Rejected = pipeline_view.objects.filter(jd_id=pk, stage_name="Rejected").values(
            "id"
        )
        if total_count["count__sum"] == None:
            total_count["count__sum"] = 0
        pipeline.append({"Views": total_count["count__sum"]})
        pipeline.append(
            {
                "Applicants": applicants_status.objects.filter(
                    jd_id_id=pk,
                    candidate_id__first_name__isnull=False,
                    candidate_id__email__isnull=False,
                ).count()
            }
        )
        pipeline.append(
            {
                "Shortlisted": applicants_status.objects.filter(
                    jd_id=pk, stage_id__in=Shortlisted
                ).count()
            }
        )
        pipeline.append(
            {
                "Hired": applicants_status.objects.filter(
                    jd_id_id=pk, stage_id__in=Offered
                ).count()
            }
        )
        pipeline.append(
            {
                "Rejected": applicants_status.objects.filter(
                    jd_id_id=pk, stage_id__in=Rejected
                ).count()
            }
        )

        total_invite = list(
            Candi_invite_to_apply.objects.filter(jd_id_id=pk)
            .values_list("candidate_id", flat=True)
            .distinct()
        )
        my_database = []
        job_details = (
            JD_form.objects.filter(id=pk)
            .annotate(
                country=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "country_id__name"
                    )[:1]
                ),
                state=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "state_id__name"
                    )[:1]
                ),
                city=Subquery(
                    JD_locations.objects.filter(jd_id=OuterRef("id")).values(
                        "city_id__name"
                    )[:1]
                ),
            )
            .values()
        )
        zita_match = 0
        # zita_match = zita_match_candidates.objects.filter(status_id_id=5,candidate_id__first_name__isnull=False,candidate_id__email__isnull=False,jd_id__in=pk).values('status_id')
        jd_list = JD_form.objects.filter(id=pk)
        if employer_pool.objects.filter(user_id=admin_id, can_source_id=5).exists():
            jd_list = jd_list.annotate(
                zita_match=Subquery(
                    zita_match_candidates.objects.filter(
                        status_id_id=5,
                        candidate_id__first_name__isnull=False,
                        jd_id=OuterRef("id"),
                    )
                    .values("status_id")
                    .annotate(cout=Count("candidate_id"))[:1]
                    .values("cout"),
                    output_field=CharField(),
                ),
            )
        else:
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
        for jd_instance in jd_list:
            zita_match = jd_instance.zita_match
        my_database.append({"Zita Match": zita_match})
        my_database.append(
            {
                "Invited to Apply": Candi_invite_to_apply.objects.filter(
                    jd_id_id=pk
                ).count()
            }
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
            applicants_status.objects.filter(jd_id_id=pk)
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
            "role_base": role_base,
            "posted_date": posted_date,
            "dates_length": dates,
            "zita_match": zita_match,
            "posted_channel": posted_channel,
            "total_count": total_count,
            "job_details": job_details[0],
            "perc_dict": perc_dict,
            "pipeline": pipeline,
            "my_database": my_database,
            "job_count": job_count,
        }
        return Response(context)


def Diff(li1, li2):
    return list(set(li1) - set(li2))


class missing_skills(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        request = self.request

        logger.info("Showing missing skills for the JD " + str(pk))
        user_id = admin_account(request)
        try:
            jd_id = pk
            jd_form = JD_form.objects.filter(id=pk)

        except:
            jd_id = JD_form.objects.filter(user_id_id=user_id).last().id
            jd_form = JD_form.objects.filter(user_id_id=user_id)
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

        allskill = mand_skill
        try:
            with open(base_dir + "/static/media/skills2.json", "r") as fp:
                a = json.load(fp)
        except:
            with open(os.getcwd() + "/static/media/skills2.json", "r") as fp:
                a = json.load(fp)

        unique = [*a[inp1]["database"]]
        missing_db = Diff(unique, allskill)
        missing_db.sort()
        missing_db = str(missing_db)
        missing_db = (
            missing_db.replace("'", "", len(missing_db))
            .replace("[", "")
            .replace("]", "")
        )

        unique = [*a[inp1]["tool"]]
        missing_tl = Diff(unique, allskill)
        missing_tl.sort()

        missing_tl = str(missing_tl)
        missing_tl = (
            missing_tl.replace("'", "", len(missing_tl))
            .replace("[", "")
            .replace("]", "")
        )

        unique = [*a[inp1]["programming"]]
        missing_pl = Diff(unique, allskill)
        missing_pl.sort()

        missing_pl = str(missing_pl)
        missing_pl = (
            missing_pl.replace("'", "", len(missing_pl))
            .replace("[", "")
            .replace("]", "")
        )

        unique = [*a[inp1]["platform"]]
        missing_pf = Diff(unique, allskill)
        missing_pf.sort()

        missing_pf = str(missing_pf)
        missing_pf = (
            missing_pf.replace("'", "", len(missing_pf))
            .replace("[", "")
            .replace("]", "")
        )

        unique = [*a[inp1]["misc"]]
        missing_ot = Diff(unique, allskill)
        missing_ot.sort()
        missing_ot = str(missing_ot)
        missing_ot = (
            missing_ot.replace("'", "", len(missing_ot))
            .replace("[", "")
            .replace("]", "")
        )

        mand_skill = str(mand_skill)
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

        mand_skill = (
            mand_skill.replace("'", "", len(mand_skill))
            .replace("[", "")
            .replace("]", "")
        )
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
        jd_profile = JD_profile.objects.filter(jd_id_id=jd_id)
        missing_skills_id = (
            Missing_Skills_Table.objects.filter(jd_id=jd_id).last().miss_skill_id
        )
        temp = list(
            Missing_Skills_Table.objects.filter(
                miss_skill_id=missing_skills_id
            ).values()
        )

        context = {
            "object": temp,
            "pk_id": jd_form.values(),
            "jd_profile": jd_profile.values(),
            "object1": mand_skill_expi,
            "skill_n_exp": skill_n_exp,
            "tool_skill": tool,
            "database_skill": database,
            "platform_skill": platform,
            "misc_skill": misc,
            "programming_skill": programming,
        }
        return Response(context)

    def post(self, request, pk):
        request = self.request
        jd = JD_form.objects.filter(id=pk).last()
        skill_exp = request.POST.getlist("skills_exp")[0].split(",")
        skills = request.POST.getlist("skills")[0].split("|")
        # skill_l = [skill_exp[i] for i in range(len(skill_exp)) if i%2 == 0]
        # exp_l = [skill_exp[i] for i in range(len(skill_exp)) if i%2 != 0]
        JD_skills_experience.objects.filter(jd_id_id=jd.id).delete()
        skill_temp = []
        database_skill = request.POST.getlist("database_skill")[0].upper().split(",")
        platform_skill = request.POST.getlist("platform_skill")[0].upper().split(",")
        programming_skill = (
            request.POST.getlist("programming_skill")[0].upper().split(",")
        )
        tool_skill = request.POST.getlist("tool_skill")[0].upper().split(",")
        misc_skill = request.POST.getlist("misc_skill")[0].upper().split(",")

        for s, e in zip(skills, skill_exp):
            # if s.upper() in skills and s.upper() not in skill_temp:
            # skill_temp.append(s.upper())
            if len(s) != 0:
                if s.upper() in database_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=1
                    )
                if s.upper() in platform_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=2
                    )
                if s.upper() in programming_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=3
                    )
                if s.upper() in tool_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=4
                    )
                if s.upper() in misc_skill:
                    JD_skills_experience.objects.create(
                        skill=s, experience=e, jd_id_id=jd.id, category_id=5
                    )

        return Response({"success": True})


class select_ds_or_non_ds(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user, updated_by = admin_account(request)
        feature = client_features_balance.objects.get(
            client_id=user, feature_id_id=10
        ).available_count
        if not company_details.objects.filter(recruiter_id=user).exists():
            return Response({"feature": feature, "url": "company_detail"})
        if not career_page_setting.objects.filter(recruiter_id=user).exists():
            return Response({"feature": feature, "url": "build_career_page"})

        return Response({"feature": feature})


class JD_templates(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user = self.request.user

        ds_role = request.GET.get("ds_role", None)
        users = request.GET.get("user", None)
        letters = request.GET.get("search", "")
        if ds_role == "1":
            result = tmeta_jd_templates.objects.filter(user=user).values()
            job_title = tmeta_jd_templates.objects.filter(user=user).values_list(
                "job_title", flat=True
            )
        elif ds_role == "2":
            result = tmeta_jd_templates.objects.filter(user=user).values()
            job_title = tmeta_jd_templates.objects.filter(user=user).values_list(
                "job_title", flat=True
            )
        elif ds_role == "3":  # "0" and user=='1':
            job_title = tmeta_jd_templates.objects.filter(
                Q(user__isnull=True) | Q(user=user)
            ).values_list("job_title", flat=True)
            if tmeta_jd_templates.objects.filter(user=user).exists():
                result = tmeta_jd_templates.objects.filter(user=user).values()
                # job_title = tmeta_jd_templates.objects.filter(user=user).values_list('job_title',flat=True)
            else:
                result = tmeta_jd_templates.objects.filter(user=user).values()
                # job_title=[]
                return Response(
                    {"jd_templates": result, "job_title": job_title, "status": "0"}
                )
        elif ds_role == "0" and users == "2":
            dataone = tmeta_jd_templates.objects.filter(user__isnull=True).values()
            datatwo = (
                tmeta_jd_templates.objects.filter(user=user).values().order_by("-id")
            )
            result = list(chain(datatwo, dataone))
            # result = tmeta_jd_templates.objects.filter(Q(user__isnull=True) | Q(user=user)).values()
            job_title = tmeta_jd_templates.objects.filter(
                Q(user__isnull=True) | Q(user=user)
            ).values_list("job_title", flat=True)
        # result = tmeta_jd_templates.objects.filter(user__isnull=True,user=user).values()
        # job_title = tmeta_jd_templates.objects.filter(user__isnull=True,user=user).values_list('job_title', flat=True)

        else:
            result = tmeta_jd_templates.objects.filter(is_ds_role=False).values()
            job_title = tmeta_jd_templates.objects.filter(is_ds_role=False).values_list(
                "job_title", flat=True
            )
        return Response({"jd_templates": result, "job_title": job_title, "status": "1"})

    def post(self, request):
        user = self.request.user
        id = self.request.POST.get("id", None)
        title = self.request.POST.get("title", None).strip()
        description = self.request.POST.get("description", None)
        ds_role = self.request.POST.get("ds_role", False)
        if title and description:
            if tmeta_jd_templates.objects.filter(
                id=id, user_id=user
            ).exists():  # update
                tmeta_jd_templates.objects.filter(id=id, user_id=user).update(
                    job_description=description, job_title=title
                )
                message = "Job Templates Updated Successfully"
            elif not tmeta_jd_templates.objects.filter(
                job_title=title.strip()
            ).exists():  # create
                tmeta_jd_templates.objects.create(
                    job_description=description,
                    job_title=title.strip(),
                    is_ds_role=ds_role,
                    user=user,
                )
                message = "Job Templates Created Successfully"
            else:
                return Response(
                    {"success": False, "message": "Titles is already exist!."}
                )
            if id:
                templateid = id
            elif title:
                templateid = tmeta_jd_templates.objects.get(
                    job_title=title.strip(), user_id=user
                ).id
            return Response(
                {"success": True, "message": message, "templateid": templateid}
            )
        else:
            return Response({"success": False, "message": "KeyError"})

    def delete(self, request):
        user = self.request.user
        id = self.request.GET.get("id", None)
        if tmeta_jd_templates.objects.filter(id=id, user_id=user).exists():
            tmeta_jd_templates.objects.filter(id=id).delete()
            return Response({"success": True, "message": "Deleted Successfully"})
        else:
            return Response({"success": False})


# class candi_invite_status(generics.GenericAPIView):
#     def get(self, request,pk):
#         request = self.request
#         user = self.request.user
#         if 'interested' in request.GET and 'can_id' in request.GET:
#             # invite=Candi_invite_to_apply.objects.filter(jd_id_id=pk,candidate_id=request.GET['can_id']).last()
#             can_id = employer_pool.objects.get(id=request.GET['can_id'])
#             if request.GET['interested'] == 'true':
#                 is_interested = 1
#             elif request.GET['interested'] == 'false':
#                 is_interested = 0
#             # invite.responded_date = timezone.now()
#             # invite.save()
#             invite=Candi_invite_to_apply.objects.get_or_create(jd_id_id=pk,candidate_id=can_id,client_id = user,is_interested = is_interested,responded_date = datetime.now())
#             invite=Candi_invite_to_apply.objects.filter(jd_id_id=pk,candidate_id=request.GET['can_id']).values()[0]
#             return Response({'invite':invite})


class candi_invite_status(generics.GenericAPIView):
    def get(self, request, pk):
        request = self.request
        # user_id ,updated_by = admin_account(self.request)
        # user = self.request.user
        if "interested" in request.GET and "can_id" in request.GET:
            invite = Candi_invite_to_apply.objects.filter(
                jd_id_id=pk, candidate_id=request.GET["can_id"]
            ).last()
            if request.GET["interested"] == "true":
                is_interested = 1
            elif request.GET["interested"] == "false":
                is_interested = 0
            data = Candi_invite_to_apply.objects.filter(
                jd_id_id=pk, candidate_id=request.GET["can_id"]
            ).update(is_interested=is_interested, responded_date=datetime.now())
            # invite.responded_date = timezone.now()
            # invite.is_interested = is_interested
            # invite.save()
            # can_id = employer_pool.objects.get(id=request.GET['can_id'])
            # user_id = can_id.client_id
            # if Candi_invite_to_apply.objects.filter(jd_id_id=pk,candidate_id=can_id,client_id = user_id,is_interested__in = [0,1]).exists():
            #     invite=Candi_invite_to_apply.objects.filter(jd_id_id=pk,candidate_id=can_id,client_id = user_id,is_interested__in = [0,1]).update(is_interested = is_interested,responded_date = datetime.now())
            # else:
            #     invite=Candi_invite_to_apply.objects.get_or_create(jd_id_id=pk,candidate_id=can_id,client_id = user_id,is_interested = is_interested,responded_date = datetime.now())
            invite = Candi_invite_to_apply.objects.filter(
                jd_id_id=pk, candidate_id=request.GET["can_id"]
            ).values()[0]
            return Response({"invite": invite})


class career_job_view_api(generics.GenericAPIView):

    def get(self, request, pk):
        request = self.request

        if request.GET["user_id"] != "0":
            login_user = True
        else:
            login_user = False
        if "apply" in request.GET:
            request.session["apply_user"] = 1
        client_id = JD_form.objects.get(id=pk).user_id
        if jd_nice_to_have.objects.filter(jd_id=pk).exists():
            nice_to_have = jd_nice_to_have.objects.get(jd_id=pk).nice_to_have
        else:
            nice_to_have = None
        company_detail = company_details.objects.filter(recruiter_id=client_id).values(
            "company_name",
            "company_website",
            "email",
            "address",
            "country__name",
            "state__name",
            "city__name",
            "zipcode",
            "logo",
            "recruiter_id_id",
            "contact",
        )
        try:

            setting = career_page_setting.objects.filter(
                recruiter_id=client_id
            ).values()
        except:
            setting = None
        if not JD_form.objects.filter(id=pk, jd_status_id=1).exists():
            return Response(
                {
                    "success": False,
                    "msg": "jd_inactive",
                    "company_detail": company_detail[0],
                    "setting": setting[0],
                }
            )
        jd_form = JD_form.objects.filter(id=pk, jd_status_id=1)

        jd_form = jd_form.annotate(
            country=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "country__name"
                )
            ),
            state=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "state__name"
                )
            ),
            city=Subquery(
                JD_locations.objects.filter(jd_id=OuterRef("id"))[:1].values(
                    "city__name"
                )
            ),
        )
        jd_form = jd_form.annotate(
            job_location=Concat(
                "city", V(", "), "state", V(", "), "country", output_field=CharField()
            )
        ).values(
            "job_posted_on",
            "job_title",
            "job_id",
            "no_of_vacancies",
            "id",
            "job_role__label_name",
            "work_remote",
            "is_ds_role",
            "work_remote",
            "is_eeo_comp",
            "richtext_job_description",
            "industry_type__label_name",
            "job_location",
            "salary_min",
            "salary_max",
            "salary_curr_type__value",
            "show_sal_to_candidate",
            "job_type__label_name",
            "jd_status__label_name",
            "min_exp",
            "max_exp",
            "work_space_type",
        )
        questionnaire = applicant_questionnaire.objects.filter(jd_id_id=pk).values()
        education = JD_qualification.objects.filter(jd_id_id=pk).values()
        skills = JD_skills_experience.objects.filter(jd_id_id=pk).values()
        if login_user == True:

            applicant_details = Personal_Info.objects.get(
                user_id_id=request.GET["user_id"]
            )
            applicant_detail = Personal_Info.objects.filter(
                user_id_id=request.GET["user_id"]
            )
            applicant_detail = applicant_detail.annotate(
                image=Subquery(
                    Profile.objects.filter(user_id=OuterRef("user_id"))[:1].values(
                        "image"
                    )
                ),
            ).values(
                "user_id",
                "firstname",
                "lastname",
                "email",
                "contact_no",
                "image",
                "country__name",
                "state__name",
                "city__name",
                "zipcode",
                "Date_of_birth",
                "linkedin_url",
                "career_summary",
                "gender__label_name",
                "updated_at",
                "code_repo",
                "visa_sponsorship",
                "remote_work",
                "type_of_job__label_name",
                "available_to_start__label_name",
                "industry_type__label_name",
                "desired_shift__label_name",
                "curr_gross",
                "current_currency",
                "exp_gross",
                "salary_negotiable",
                "current_country__name",
                "current_state__name",
                "current_city__name",
                "relocate",
            )[
                0
            ]
            if Additional_Details.objects.filter(
                application_id=applicant_details
            ).exists():
                additional_detail = Additional_Details.objects.filter(
                    application_id=applicant_details
                ).values()[0]
            else:
                if not Additional_Details.objects.filter(
                    application_id=applicant_details
                ).exists():
                    if employer_pool.objects.filter(
                        candidate_id=applicant_details, can_source_id=1
                    ).exists():
                        experience = employer_pool.objects.get(
                            candidate_id=applicant_details, can_source_id=1
                        ).work_exp
                        if experience:
                            numbers = re.findall(r"\d+", experience)
                            numbers = [int(num) for num in numbers]
                            if "-" in experience:
                                Additional_Details.objects.create(
                                    application_id=applicant_details,
                                    total_exp_year=numbers[0],
                                )
                            else:
                                if len(numbers) > 1:
                                    Additional_Details.objects.create(
                                        application_id=applicant_details,
                                        total_exp_year=numbers[0],
                                        total_exp_month=numbers[1],
                                    )
                                else:
                                    Additional_Details.objects.create(
                                        application_id=applicant_details,
                                        total_exp_year=numbers[0],
                                        total_exp_month=0,
                                    )
                        else:
                            Additional_Details.objects.create(
                                application_id=applicant_details,
                                total_exp_year=0,
                                total_exp_month=0,
                            )
                        additional_detail = Additional_Details.objects.filter(
                            application_id=applicant_details
                        ).values()[0]
        else:
            applicant_details = None
            applicant_detail = None
            # additional_details=None
            additional_detail = None
        try:
            emp_id = employer_pool.objects.get(
                candidate_id=applicant_details, client_id=client_id
            ).pk
        except Exception as e:
            emp_id = 0

        try:
            apply_user = request.session["apply_user"]
        except:
            apply_user = 0

        applied_status = 0
        if applicants_status.objects.filter(
            jd_id_id=pk, candidate_id_id=emp_id, status_id__in=[1, 2, 3, 4, 7]
        ).exists():
            applied_status = 1
        current_site = settings.CLIENT_URL
        incomplete = False
        if User_Info.objects.filter(
            user_id=request.GET["user_id"], application_id__isnull=True
        ).exists():
            incomplete = User_Info.objects.filter(
                user_id=request.GET["user_id"], application_id__isnull=True
            ).exists()

        context = {
            "success": True,
            "jd_form": jd_form[0],
            "education": education,
            "skills": skills,
            "login_user": login_user,
            "applicant_detail": applicant_detail,
            "questionnaire": questionnaire,
            "additional_detail": additional_detail,
            "company_detail": company_detail[0],
            "setting": setting[0],
            "emp_id": emp_id,
            "current_site": str(current_site),
            "applied_status": applied_status,
            "apply_user": apply_user,
            "nice_to_have": nice_to_have,
            "incomplete": incomplete,
        }
        response = Response(context)

        return response

    def post(self, request, pk):
        try:
            user_id, updated_by = admin_account(request)
        except:
            user_id = request.user
            if User_Info.objects.filter(username=user_id).exists():
                user_id = User_Info.objects.get(username=user_id).employer_id
                user_id = User.objects.get(id=user_id)
        request = self.request
        applicant_details = Personal_Info.objects.get(user_id=request.user)
        if employer_pool.objects.filter(
            candidate_id=applicant_details.application_id
        ).exists():
            candidate_id = (
                employer_pool.objects.filter(
                    candidate_id=applicant_details.application_id
                )
                .last()
                .id
            )
        else:
            if employer_pool.objects.filter(
                candidate_id=applicant_details.application_id
            ).exists():
                candidate_id = employer_pool.objects.get(
                    candidate_id=applicant_details.application_id
                ).id
            else:
                candidate_id = None
        if Resume_overview.objects.filter(application_id=applicant_details).exists():
            res_details = Resume_overview.objects.get(
                application_id=applicant_details
            ).parsed_resume
        elif candidate_parsed_details.objects.filter(
            candidate_id=candidate_id
        ).exists():
            res_details = candidate_parsed_details.objects.get(
                candidate_id=candidate_id
            ).parsed_text
        res_details = json.loads(res_details)
        qual = request.POST.get("Qualification")
        res_details["Highest Qualifications"] = qual
        res_details = json.dumps(res_details)
        Resume_overview.objects.filter(application_id=applicant_details).update(
            parsed_resume=res_details
        )
        ques_list = request.POST["questionnaire"].split(",")
        from django.utils import timezone

        try:
            for i in ques_list:
                id_ = i.split(":")[0]
                value = i.split(":")[1]
                applicant_answers.objects.create(
                    qus_id_id=id_, candidate_id=applicant_details, answer=value
                )
        except:
            pass
        cover_letter = applicant_cover_letter_form(request.POST)
        jobs_eeo = jobs_eeo_form(request.POST)
        if cover_letter.is_valid():
            cover_letter = cover_letter.save(commit=False)
            cover_letter.candidate_id = applicant_details
            cover_letter.jd_id_id = pk
            cover_letter.save()
        if jobs_eeo.is_valid():
            jobs_eeo = jobs_eeo.save(commit=False)
            jobs_eeo.jd_id_id = pk
            jobs_eeo.candidate_id = applicant_details
            jobs_eeo.save()

        jd_form = JD_form.objects.get(id=pk)
        client_id = JD_form.objects.get(id=pk).user_id
        skills = Skills.objects.get(application_id=applicant_details)
        try:
            skilld = skills.tech_skill + "," + skills.soft_skill
        except:
            skilld = skills.tech_skill
        try:
            skilld = skilld.replace(",", ", ")
        except:
            skilld = None
        try:
            location = str(
                applicant_details.city.name
                + ", "
                + applicant_details.state.name
                + ", "
                + applicant_details.country.name
            )
        except:
            location = None
        work_exp = None
        exp_year = Additional_Details.objects.get(
            application_id=applicant_details
        ).total_exp_year
        exp_month = Additional_Details.objects.get(
            application_id=applicant_details
        ).total_exp_month
        if exp_year != 0 and exp_month != 0:
            work_exp = str(exp_year) + " Years" + " " + str(exp_month) + " Months"
        elif exp_year == 0 and exp_month != 0:
            work_exp = str(exp_year) + " Years" + " " + str(exp_month) + " Months"
        elif exp_year != 0 and exp_month == 0:
            work_exp = str(exp_year) + " Years"
        if employer_pool.objects.filter(
            client_id=client_id,
            email=applicant_details.email,
            can_source_id__in=[1, 2, 3],
        ).exists():
            employer_pool.objects.filter(
                client_id=client_id, email=applicant_details.email
            ).update(
                candidate_id=applicant_details,
                job_type=applicant_details.type_of_job,
                first_name=applicant_details.firstname,
                last_name=applicant_details.lastname,
                contact=applicant_details.contact_no,
                linkedin_url=applicant_details.linkedin_url,
                work_exp=work_exp,
                relocate=applicant_details.relocate,
                qualification=request.POST["Qualification"],
                exp_salary=applicant_details.exp_gross,
                skills=skilld,
                location=location,
            )
        elif employer_pool.objects.filter(
            client_id=client_id, can_source_id=4, candidate_id=applicant_details
        ).exists():
            employer_pool.objects.filter(
                client_id=client_id, email=applicant_details.email
            ).update(
                candidate_id=applicant_details,
                job_type=applicant_details.type_of_job,
                first_name=applicant_details.firstname,
                can_source_id=3,
                last_name=applicant_details.lastname,
                contact=applicant_details.contact_no,
                linkedin_url=applicant_details.linkedin_url,
                work_exp=work_exp,
                relocate=applicant_details.relocate,
                qualification=request.POST["Qualification"],
                exp_salary=applicant_details.exp_gross,
                skills=skilld,
                location=location,
            )
        else:
            employer_pool.objects.create(
                client_id=client_id,
                email=applicant_details.email,
                candidate_id=applicant_details,
                can_source_id=3,
                job_type=applicant_details.type_of_job,
                first_name=applicant_details.firstname,
                last_name=applicant_details.lastname,
                contact=applicant_details.contact_no,
                linkedin_url=applicant_details.linkedin_url,
                work_exp=work_exp,
                relocate=applicant_details.relocate,
                qualification=request.POST["Qualification"],
                exp_salary=applicant_details.exp_gross,
                skills=skilld,
                location=location,
            )
            if client_features_balance.objects.filter(
                client_id=client_id, feature_id_id=12
            ).exists():
                avail = client_features_balance.objects.get(
                    client_id=client_id, feature_id_id=12
                )
                if not avail.available_count == None:
                    avail.available_count = avail.available_count - 1
                    avail.save()

        try:
            source = request.POST["source_count"]
        except:
            source = "Career Page"
        if employer_pool.objects.filter(
            candidate_id=applicant_details, client_id=client_id
        ).exists():
            emp_id = employer_pool.objects.filter(
                candidate_id=applicant_details, client_id=client_id
            ).last()
        else:
            emp_id = employer_pool.objects.get(
                candidate_id=applicant_details, client_id=client_id
            )
        candidate_id = employer_pool.objects.filter(
            candidate_id=applicant_details, client_id=client_id
        ).values("id")
        result = applicant_genarate_json(request, pk=emp_id.id)
        exceed_applicant = resume_exceed(emp_id.id, client_id, jd_form.id, 1)
        if applicants_status.objects.filter(
            jd_id_id=pk, candidate_id=emp_id, client_id=client_id
        ).exists():
            pass
        else:
            # user_id ,updated_by = admin_account(request)
            try:
                user_id, updated_by = admin_account(request)
            except:
                user_id = request.user
                if User_Info.objects.filter(username=user_id).exists():
                    user_id = User_Info.objects.get(username=user_id).employer_id
                    user_id = User.objects.get(id=user_id)
            applicants_status.objects.create(
                jd_id_id=pk,
                source=source,
                candidate_id=emp_id,
                status_id_id=1,
                client_id=client_id,
                created_on=timezone.now(),
            )
            candidate_notification_upload(emp_id.id, jd_form.id, user_id)
            email_automation(emp_id.id, jd_form.id, user_id)
        applicants_screening_status.objects.create(
            jd_id_id=pk, candidate_id=emp_id, client_id=client_id
        )
        request.session["apply_user"] = 2
        data = (
            applicant_details.firstname.title()
            + " has applied for "
            + jd_form.job_title.title()
            + " - "
            + str(jd_form.job_id)
        )
        try:
            notify.send(
                client_id,
                recipient=client_id,
                verb=data,
                description="applicant",
                target=emp_id,
                action_object=jd_form,
            )
        except:
            pass
        messages.success(request, "test")
        try:
            career_page_url = career_page_setting.objects.get(
                recruiter_id=client_id
            ).career_page_url
        except:
            career_page_url = ""
        count = applicants_status.objects.filter(jd_id_id=pk, status_id_id=1).count()
        user = request.user
        first_last_name = User.objects.filter(username=user).values(
            "first_name", "last_name"
        )
        first_last_name = first_last_name.annotate(
            value=Concat("first_name", V(" "), "last_name", output_field=CharField())
        )
        user = first_last_name[0]["value"]
        # emp_id = str(emp_id)
        candi = employer_pool.objects.get(id=emp_id.id)
        candidate = None
        if candi.first_name != None and candi.last_name != None:
            candidate = str(candi.first_name) + " " + str(candi.last_name)
        elif candi.first_name != None and candi.last_name == None:
            candidate = str(candi.first_name)
        count = applicants_status.objects.filter(jd_id_id=pk, status_id_id=1).count()
        jd = JD_form.objects.get(id=pk)
        dd = JD_form.objects.filter(id=pk).all()
        domain = settings.CLIENT_URL
        available_resume = 0
        if client_features_balance.objects.filter(
            feature_id_id=27, client_id=user_id
        ).exists():
            available_resume = client_features_balance.objects.get(
                feature_id_id=27, client_id=user_id
            ).available_count

        d = {
            "user": user,
            "can_id": candi.id,
            "candidate_name": candi.first_name,
            "count": count,
            "jd_id": jd,
            "domain": domain,
            "jd_form": jd_form,
            "valid": available_resume,
        }
        htmly = get_template("email_templates/applicants.html")
        html_content = htmly.render(d)
        subject = "Candidate Applied for a job " + str(jd.job_title)
        user = candi.client_id.email
        msg = EmailMultiAlternatives(subject, html_content, "support@zita.ai", [user])

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
        response = Response({"success": True, "candidate_id": candidate_id})
        return response


class email_preference_api(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        email_preferences = email_preference.objects.filter(
            user_id=request.user
        ).values(
            "user_id",
            "stage_id",
            "is_active",
            "created_at",
            "updated_by",
        )

        meta_email = tmeta_email_preference.objects.all().values()
        context = {
            "success": True,
            "email_preferences": email_preferences,
            "meta_email": meta_email,
        }
        response = Response(context)
        return response

    def post(self, request):
        request = self.request
        email_preference.objects.filter(
            user_id=request.user, stage_id_id=request.POST["stage_id"]
        ).update(is_active=request.POST["is_active"])
        context = {
            "success": True,
            # 'email_preferences':email_preferences,
        }
        response = Response(context)
        return response


def pipeline_data(stages, emp_id, jd_id, workflow_id):
    emp_id = get_admin_account(emp_id)
    valid = pipeline_view.objects.filter(workflow_id=workflow_id, jd_id=jd_id).values()
    if valid.exists():
        pass
    else:
        for i in stages:
            pipeline_view.objects.create(
                workflow_id_id=workflow_id.wk_id,
                jd_id=jd_id,
                emp_id=emp_id,
                stage_order=i["stage_order"],
                stage_name=i["stage_name"],
                stage_color=i["stage_color"],
                is_disabled=i["is_disabled"],
            )
        newdata = tmeta_message_templates.objects.filter(
            id__in=[1, 2, 3, 4, 5, 6, 7, 8]
        )
        for i in newdata:
            if pipeline_view.objects.filter(jd_id=jd_id, stage_name=i.name).exists():
                jd = JD_form.objects.get(id=jd_id.id)
                template_name = f"{jd.job_id} {i.name}"
                stage_id_id = pipeline_view.objects.get(
                    jd_id=jd_id.id, stage_name=i.name
                ).id
                stage_id_id = jd_message_templates.objects.filter(
                    jd_id=jd_id, name=i.name
                ).update(stage=stage_id_id)

                # stage_id_id = tmeta_message_templates.objects.filter(jd_id = jd_id,name = template_name).update(stage = stage_id_id)

        # TODO - Update Template Stages also
        if pipeline_view.objects.filter(jd_id=jd_id).exists():
            filter_data = jd_message_templates.objects.filter(user=emp_id, jd_id=jd_id)

            # filter_data = tmeta_message_templates.objects.filter(user = user_id,jd_id = jd_id)
            for i in filter_data:
                if (
                    not template_stage.objects.filter(
                        stages_id=i.stage, user_id=emp_id
                    ).exists()
                    and i.stage != 0
                ):
                    # template__name=tmeta_message_templates.objects.filter(jd_id=i.jd_id,name = template_name,user=user_id).values('id',flat=True)
                    template_stage.objects.create(
                        stages_id=pipeline_view.objects.get(id=i.stage).id,
                        templates_id=tmeta_message_templates.objects.get(
                            id=i.message.id
                        ).id,
                        user_id=User.objects.get(id=i.user_id),
                    )


def associate(workflow_id, jd_id):
    if workflow_id and jd_id:
        connection = Employee_workflow.objects.filter(wk_id=workflow_id).update(
            associate=True
        )
    else:
        pass


def set_as_default(set_as_default, workflow_id, user):
    default = Employee_workflow.objects.filter(emp_id=user, set_as_default=True)
    value = Employee_workflow.objects.filter(wk_id=workflow_id)
    for i in value:
        for obj in default:
            if obj.wk_id != i.wk_id:
                obj.set_as_default = not obj.set_as_default
                i.set_as_default = not i.set_as_default
                obj.save()
                i.save()
    return None


def default_all(workflow_id, jd_id, user):
    setas = Employee_workflow.objects.filter(emp_id=user, default_all=True)
    check = Employee_workflow.objects.filter(wk_id=workflow_id)

    if len(setas) != 0:
        for i in check:
            for obj in setas:
                if obj.emp_id == i.emp_id:
                    if obj.wk_id != i.wk_id:
                        obj.default_all = not obj.default_all
                        i.default_all = not i.default_all
                        obj.save()
                        i.save()
    else:
        setas = Employee_workflow.objects.filter(wk_id=workflow_id, emp_id=user).update(
            default_all=True
        )
    return None


class kanban_pipeline_view(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            emp_id = self.request.user
            emp_id,updated_by = admin_account(request)
            if "jd_id" in self.request.GET:
                jd_id = self.request.GET["jd_id"].strip()
                jd_id = JD_form.objects.get(id=jd_id)
                workflow_update = (
                    pipeline_view.objects.filter(jd_id=jd_id)
                    .exclude(workflow_id=None)
                    .last()
                )
                if workflow_update:
                    workflow_update = (
                        pipeline_view.objects.filter(jd_id=jd_id)
                        .exclude(workflow_id=None)
                        .last()
                        .workflow_id
                    )
                    pipeline_view.objects.filter(jd_id=jd_id, workflow_id=None).update(
                        workflow_id=workflow_update
                    )
                if "workflow_id" not in self.request.GET and jd_id:
                    data = Employee_workflow.objects.filter(
                        emp_id=emp_id, default_all=True
                    )
                    if data.exists():
                        value = pipeline_view.objects.filter(jd_id=jd_id).exists()
                        if pipeline_view.objects.filter(jd_id=jd_id).exists():
                            stages = pipeline_view.objects.filter(jd_id=jd_id).values()
                            stages = sorted(stages, key=lambda x: x["stage_order"])
                            default = ["Shortlisted", "Rejected", "Hired"]

                            default_stage = []
                            new_stages = []

                            for stage in stages:
                                if stage["stage_name"] in default:
                                    default_stage.append(stage)
                                else:
                                    new_stages.append(stage)

                            context = {
                                "select_pipeline": False,
                                "message": "doesn't show any popup",
                                "stages": stages,
                                "default_stage": default_stage,
                                "new_stages": new_stages,
                            }
                            return Response(context)
                        else:
                            first_object = data.first()
                            wk_id = first_object.wk_id
                            stages = Stages_Workflow.objects.filter(
                                workflow_id=wk_id
                            ).values()
                            stages = sorted(stages, key=lambda x: x["stage_order"])
                            default = ["Shortlisted", "Rejected", "Hired"]

                            default_stage = []
                            new_stages = []

                            for stage in stages:
                                if stage["stage_name"] in default:
                                    default_stage.append(stage)
                                else:
                                    new_stages.append(stage)

                            # showpopup = True
                            context = {
                                "select_pipeline": True,
                                "message": "its default or choose your another pipeline",
                                "stages": stages,
                                "default_stage": default_stage,
                                "new_stages": new_stages,
                            }
                            return Response(context)

                    elif pipeline_view.objects.filter(jd_id=jd_id).exists():
                        stages = pipeline_view.objects.filter(jd_id=jd_id).values()
                        stages = sorted(stages, key=lambda x: x["stage_order"])
                        default = ["Shortlisted", "Rejected", "Hired"]

                        default_stage = []
                        new_stages = []

                        for stage in stages:
                            if stage["stage_name"] in default:
                                default_stage.append(stage)
                            else:
                                new_stages.append(stage)

                        context = {
                            "select_pipeline": False,
                            "message": "doesn't show any popup",
                            "stages": stages,
                            "default_stage": default_stage,
                            "new_stages": new_stages,
                        }
                        return Response(context)

                    else:
                        stages = Employee_workflow.objects.get(
                            emp_id=emp_id, set_as_default=True
                        )
                        stages = Stages_Workflow.objects.filter(
                            workflow_id=stages.wk_id
                        ).values()
                        # stages =  [
                        #     {"id": "","jdd_id": "","emp_id_id": "","workflow_id_id": "","is_active": False,"created_on": "","updated_by": None,"stage_order": 2,"stage_name": "Shortlisted","stage_color": "#80C0D0","stage_length": 0,"is_disabled": True},
                        #     {"id": "","jdd_id": "","emp_id_id": "","workflow_id_id": "","is_active": False,"created_on": "","updated_by": None,"stage_order": 3,"stage_name": "Offered","stage_color": "#F29111","stage_length": 0,"is_disabled": True},
                        #     {"id": "","jdd_id": "","emp_id_id": "","workflow_id_id": "","is_active": False,"created_on": "","updated_by": None,"stage_order": 4,"stage_name": "Rejected","stage_color": "#ED4857","stage_length": 0,"is_disabled": True}]
                        stages = sorted(stages, key=lambda x: x["stage_order"])
                        default = ["Shortlisted", "Rejected", "Hired"]

                        default_stage = []
                        new_stages = []

                        for stage in stages:
                            if stage["stage_name"] in default:
                                default_stage.append(stage)
                            else:
                                new_stages.append(stage)

                        context = {
                            "select_pipeline": None,
                            "message": "show choose the pipeline",
                            "stages": stages,
                            "default_stage": default_stage,
                            "new_stages": new_stages,
                        }
                        return Response(context)
            else:
                return Response({"successs": False})

            if "workflow_id" in self.request.GET:
                workflow_id = self.request.GET["workflow_id"].strip()
                if workflow_id != None and jd_id != None:
                    if "default_all" in self.request.GET:
                        default = self.request.GET["default_all"].strip()
                        if default.lower() == "true":
                            default_all(workflow_id, jd_id, emp_id)
                            set_as_default(default, workflow_id, emp_id)
                        else:
                            pass
                    workflow_id = Employee_workflow.objects.get(wk_id=workflow_id)
                    stages = Stages_Workflow.objects.filter(
                        workflow_id=workflow_id
                    ).values()
                    if len(stages) != 0:
                        pipeline_data(stages, emp_id, jd_id, workflow_id)
                        associate(workflow_id.wk_id, jd_id)
                        stages = pipeline_view.objects.filter(
                            workflow_id=workflow_id, emp_id=emp_id, jd_id=jd_id
                        ).values()
                        stages = sorted(stages, key=lambda x: x["stage_order"])
                        default = ["Shortlisted", "Rejected", "Hired"]

                        default_stage = []
                        new_stages = []

                        for stage in stages:
                            if stage["stage_name"] in default:
                                default_stage.append(stage)
                            else:
                                new_stages.append(stage)

                        context = {
                            "message": "deosnot set any default",
                            "stages": stages,
                            "default_stage": default_stage,
                            "new_stages": new_stages,
                        }
                        return Response(context)
        except Exception as e:
            print("EXCEPTION_____",e)
            return Response({"success": False, "jd-id": None})

    def post(self, request):
        jd_id = self.request.POST["jd_id"].strip()
        jd_id = JD_form.objects.get(id=jd_id)
        emp_id = self.request.user
        stages = self.request.POST["stages"].strip()
        if pipeline_view.objects.filter(jd_id=jd_id).exists():
            for i in json.loads(stages):
                workflow_id = (
                    pipeline_view.objects.filter(jd_id=jd_id)
                    .exclude(workflow_id=None)
                    .last()
                    .workflow_id
                )
                if pipeline_view.objects.filter(jd_id=jd_id, id=i["id"]).exists():
                    pipeline_view.objects.filter(jd_id=jd_id, id=i["id"]).update(
                        jd_id=jd_id,
                        emp_id=emp_id,
                        stage_order=i["stage_order"],
                        stage_name=i["stage_name"],
                        stage_color=i["stage_color"],
                        workflow_id=workflow_id,
                    )
                else:
                    pipeline_view.objects.create(
                        jd_id=jd_id,
                        emp_id=emp_id,
                        stage_order=i["stage_order"],
                        stage_name=i["stage_name"],
                        stage_color=i["stage_color"],
                        workflow_id=workflow_id,
                    )
            delete_stage = [i["stage_name"] for i in json.loads(stages)]
            delete_stage = (
                pipeline_view.objects.filter(jd_id=jd_id)
                .exclude(stage_name__in=delete_stage)
                .delete()
            )
            message = "updated sucessfully"
        context = {"message": message, "success": True}
        return Response(context)

    def delete(self, request):
        if "jd_id" in self.request.GET:
            jd_id = self.request.GET["jd_id"].strip()
            if "stages" in self.request.GET:
                stages = self.request.GET["stages"].strip()
                for i in json.loads(stages):
                    if pipeline_view.objects.filter(jd_id=jd_id).exists():
                        if pipeline_view.objects.filter(
                            jd_id=jd_id, stage_name=i["stage_name"]
                        ).exists():
                            pipeline_view.objects.filter(
                                jd_id=jd_id, stage_name=i["stage_name"]
                            ).delete()
                            message = "deleted succuesfully"
                        else:
                            pass
            context = {"message": message}
            return Response(context)


class kanban_updation(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(request)

        if "jd_id" in self.request.GET:
            jd_id = self.request.GET["jd_id"]
            jd_id = JD_form.objects.get(id=jd_id)
        if "stages" in self.request.GET:
            stages = self.request.GET["stages"].strip()
        if "candidate_id" in self.request.GET:
            candidate_id = self.request.GET["candidate_id"].strip()
            stage_length = eval(candidate_id)
            stage_id = pipeline_view.objects.filter(
                jd_id=jd_id, stage_name=stages
            ).exists()
            popop = (
                applicants_status.objects.filter(jd_id=jd_id)
                .values("stage_id")
                .distinct()
            )
            if "status" in self.request.GET:
                candidate = employer_pool.objects.get(id=candidate_id)

                status = self.request.GET["status"]
                if status == True:
                    company_name = company_details.objects.get(
                        recruiter_id_id=user_id
                    ).company_name
                    template = tmeta_automation_template.objects.get(stages=stage_id)
                    email_automation_template.objects.get_or_create(
                        stages=stages,
                        candidate_id=candidate_id,
                        templates=template,
                        jd_id=jd_id,
                        user_id=user_id,
                    )
                    email_content = (
                        template.template_content.replace(
                            "[Applicant Name]",
                            f"{candidate.first_name} {candidate.last_name}",
                        )
                        .replace("[Job Title]", jd_id.job_title)
                        .replace("[Company Name]", company_name)
                    )
                send_mail(
                    subject=template.subject.replace(
                        "[Applicant Name]",
                        f"{candidate.first_name} {candidate.last_name}",
                    ),
                    message="",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=candidate.eamil,
                    html_message=email_content,
                    fail_silently=False,
                )
            target_id = employer_pool.objects.filter(id__in=json.loads(candidate_id))
            for notifi in target_id:
                if notifi.candidate_id != None:
                    target_id = Personal_Info.objects.get(
                        application_id=notifi.candidate_id.application_id
                    )
                    if stages == "Rejected":
                        data = "Application Status: Your application is no longer under consideration."
                        notify.send(
                            user_id,
                            recipient=target_id.user_id,
                            description="Stages",
                            verb=data,
                            target_id=notifi.candidate_id,
                            action_object=jd_id,
                        )
                    else:
                        data = f"Application Status: Moved to under review."
                        notify.send(
                            user_id,
                            recipient=target_id.user_id,
                            description="Stages",
                            verb=data,
                            target_id=notifi.candidate_id,
                            action_object=jd_id,
                        )
            # for x in popop if stage_id
            if stage_id and len(stage_length) > 0:
                stage_id = pipeline_view.objects.filter(jd_id=jd_id, stage_name=stages)[
                    0
                ]
                if len(candidate_id) > 1:
                    for candidate_id in json.loads(candidate_id):
                        candidate_id = employer_pool.objects.get(id=candidate_id)
                        applicant_update = applicants_status.objects.filter(
                            jd_id=jd_id, candidate_id=candidate_id
                        ).update(
                            stage_id=stage_id.id,
                            updated_by=updated_by,
                            # created_on = datetime.now(),
                        )

                        value = applicants_screening_status.objects.create(
                            jd_id=jd_id,
                            candidate_id=candidate_id,
                            client_id=user_id,
                            stage_id=stage_id,
                            updated_by=updated_by,
                        )
                        # stage_length = applicants_status.objects.filter(jd_id = jd_id,stage_id=stage_id)
                        data = pipeline_view.objects.filter(
                            jd_id=jd_id, stage_name=stages
                        ).update(
                            updated_by=updated_by,
                            created_on=datetime.now(),
                            # stage_length = len(stage_length)
                        )

                        pipeline_status.objects.create(
                            candidate_id=candidate_id,
                            jd_id=jd_id,
                            pipeline_id=stage_id.id,
                            stage=tmeta_stages.objects.get(id=1),
                            user_id=user_id,
                        )

                        if UserAction.objects.filter(action_description = stages).exists():
                            action_id = UserAction.objects.get(action_description = stages).id
                            UserActivity.objects.create(
                                user=request.user,
                                action_id=int(action_id),
                                action_detail='"'
                                + str(candidate_id.first_name)
                                + '" for the job id: '
                                + str(jd_id.job_id),
                            )
                        success = True
                        message = "Candidate Move into stage: " + stages
                    stage_length = (
                        applicants_status.objects.filter(jd_id=jd_id, stage_id=stage_id)
                        .values("stage_id")
                        .annotate(stage_count=Count("stage_id"))[0]
                    )
                    stage_id.stage_length = stage_length["stage_count"]
                    stage_id.save()
                    applicants = applicants_status.objects.filter(
                        stage_id=stage_id
                    ).values()
                    applicants = [
                        {
                            "stage_id": i["stage_id_id"],
                            "candidate_id_id": i["candidate_id_id"],
                            "stage_name": stage_id.stage_name,
                        }
                        for i in applicants
                    ]
                    context = {
                        "sucess": success,
                        "message": message,
                        "applicants": applicants,
                        "applicant_length": len(applicants),
                    }
                    return Response(context)
                else:
                    return Response(
                        {"success": False, "error": "candidate is Empty array!"}
                    )
            else:
                return Response(
                    {
                        "success": False,
                        "error": "stage_name doesnot exist! or candidate is Empty array!",
                    }
                )


from datetime import datetime


class download_bulk_export(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        try:
            jd_id = self.request.GET["jd_id"]
            jd_id = JD_form.objects.get(id=jd_id)
            if "download" in self.request.GET:  # zip
                if "candidate_id" in self.request.GET:
                    candidate_id = self.request.GET["candidate_id"]
                    candidate_id = eval(candidate_id)
                    t = datetime.now().strftime("%b_%d_%Y")
                    # filepath =base_dir+'/media/jd_download/'+str(jd_id.id)+'_'+jd_id.job_title+'_'+str(t)+'.zip'
                    jd_title = string_replace(jd_id.job_title)
                    filepath = (
                        base_dir
                        + "/media/jd_download/"
                        + str(jd_id.id)
                        + "_"
                        + jd_title
                        + "_"
                        + "Applicants_Resumes_"
                        + str(t)
                        + ".zip"
                    )
                    if len(candidate_id) > 1:
                        with zipfile.ZipFile(filepath, "w") as myzip:
                            for candi_id in candidate_id:
                                candi_id = employer_pool.objects.get(id=candi_id)
                                url = candidate_parsed_details.objects.filter(
                                    candidate_id_id=candi_id
                                ).values("resume_file_path")[0]
                                url = url["resume_file_path"]
                                if "media" in str(url):
                                    url = url
                                else:
                                    url = os.path.join(base_dir, "media", str(url))
                                stage_id = applicants_status.objects.filter(
                                    jd_id=jd_id, candidate_id=candi_id
                                ).values("stage_id")[0]
                                if stage_id["stage_id"] != None:
                                    stage_id = pipeline_view.objects.get(
                                        id=stage_id["stage_id"]
                                    )
                                    destination_path = (
                                        str(stage_id.stage_name)
                                        + "/"
                                        + os.path.basename(url)
                                    )
                                    myzip.write(url, arcname=destination_path)
                                else:
                                    destination_path = (
                                        str("New Applicant")
                                        + "/"
                                        + os.path.basename(url)
                                    )
                                    myzip.write(url, arcname=destination_path)
                            myzip.close()
                            filepath = filepath.split("media/")[1]
                            file_name = filepath.split("jd_download/")[1]
                            return Response(
                                {
                                    "file_path": filepath,
                                    "success": True,
                                    "message": "Zip file Downloaded Successfully!",
                                    "file_name": file_name,
                                }
                            )
                    elif len(candidate_id) == 1:
                        for candi_id in candidate_id:
                            candi_id = employer_pool.objects.get(id=candi_id)
                            url = candidate_parsed_details.objects.get(
                                candidate_id_id=candi_id
                            ).resume_file_path
                            # url = '/Users/pugazh/Documents/clone_rep/zita-recruit/media/resume/data.pdf'
                            # base_dir=base_dir+'/media/'
                            if "media" in str(url):
                                url = url
                            else:
                                url = os.path.join(base_dir, "media", str(url))
                            # url = url.split("media/")[1]
                            if os.path.exists(str(url)):
                                destination = str(url)
                                destination = destination.split("media/")[1]
                                file_name = destination.split("resume/")[1]
                                return Response(
                                    {
                                        "file_type": "single",
                                        "file_path": destination,
                                        "file_name": file_name,
                                    }
                                )
                            else:
                                return Response({"message": "file_path doesnot exist"})
                    else:
                        return Response({"success": False})
                else:
                    return Response(
                        {"error": "Must Give candidate id to download File"}
                    )
            elif "csvdownload" in self.request.GET:  # csv
                # if "candidate_id" in self.request.GET:
                #     candidate_id = self.request.GET['candidate_id']
                #     candidate_id = eval(candidate_id)
                # else:
                candidate_id = applicants_status.objects.filter(
                    client_id=user_id, jd_id=jd_id
                ).values("candidate_id")

                try:
                    value = applicants_status.objects.filter(
                        client_id=user_id, jd_id=jd_id
                    ).values("stage_id__stage_name", "source", "created_on")
                    match_score = Matched_candidates.objects.filter(
                        jd_id=jd_id, candidate_id__in=candidate_id
                    ).values("profile_match")
                    if match_score:
                        match_score = match_score
                    else:
                        match_score = [{"profile_match": "0"}] * len(candidate_id)
                    data = employer_pool.objects.filter(id__in=candidate_id).values(
                        "id",
                        "first_name",
                        "location",
                        "contact",
                        "email",
                        "linkedin_url",
                        "skills",
                        "qualification",
                        "work_exp",
                    )
                    skills = employer_pool.objects.filter(id__in=candidate_id).values(
                        "candidate_id"
                    )
                    skills = [
                        i["candidate_id"] for i in skills if i["candidate_id"] != None
                    ]
                    skills = Skills.objects.filter(application_id__in=skills).values(
                        "soft_skill", "tech_skill"
                    )
                    job_preference = employer_pool.objects.filter(
                        id__in=candidate_id
                    ).values(
                        "candidate_id__type_of_job__label_name",
                        "candidate_id__available_to_start__label_name",
                        "candidate_id__industry_type__label_name",
                        "candidate_id__curr_gross",
                        "candidate_id__exp_gross",
                        "candidate_id__relocate",
                        "candidate_id__location",
                        "candidate_id__code_repo",
                    )
                    job_preference = [
                        {
                            **v,
                            "candidate_id__relocate": (
                                "Yes" if v["candidate_id__relocate"] else "No"
                            ),
                        }
                        for v in job_preference
                    ]
                    if len(job_preference[0]) > 0:
                        t = datetime.now().strftime("%b_%d_%Y")
                        jd_title = string_replace(jd_id.job_title)
                        filepath = (
                            base_dir
                            + "/media/csv_download/"
                            + str(jd_id.id)
                            + "_"
                            + jd_title
                            + "_"
                            + "Applicants_"
                            + str(t)
                            + ".csv"
                        )
                        with open(filepath, "w", newline="") as csvfile:
                            writer = csv.writer(csvfile)
                            # headers = ["Total Applicants:"+str(len(data))]
                            serial_number = 1
                            # writer.writerow(headers)
                            table_heading = [
                                "S.NO",
                                "Name",
                                "Candidate_id",
                                "Stages",
                                "Match Score",
                                "Qualification",
                                "Experience",
                                "Applied Date",
                                "Location",
                                "Contact",
                                "Email",
                                "Professional Skills",
                                "Soft Skills",
                                "Linked In",
                                "Github",
                                "Source",
                                "Job Type",
                                "Industry Type",
                                "Current Gross Salary",
                                "Expected Gross Salary",
                                "Availbility",
                                "Prefered Work Location",
                                "Willing to Relocate",
                            ]
                            writer.writerow(table_heading)

                            for i, x, z, y, m in zip(
                                value, data, job_preference, match_score, skills
                            ):
                                if i["stage_id__stage_name"] == None:
                                    i["stage_id__stage_name"] = "New Applicant"
                                # y = ["Not Specified" if value is None else value for value in y]
                                row = [
                                    serial_number,
                                    x.get(
                                        "first_name", "Not specified"
                                    ),  # Replace None with an empty string if the value is None
                                    x.get("id", "None"),
                                    i.get("stage_id__stage_name", ""),
                                    y.get("profile_match", ""),
                                    x.get("qualification", ""),
                                    x.get("work_exp", ""),
                                    i.get("created_on", ""),
                                    x.get("location", ""),
                                    x.get("contact", ""),
                                    x.get("email", ""),
                                    m.get("tech_skill", ""),
                                    m.get("soft_skill", ""),
                                    x.get("linkedin_url", ""),
                                    z.get("candidate_id__code_repo", ""),
                                    i.get("source", "Not specified"),
                                    z.get("candidate_id__type_of_job__label_name", ""),
                                    z.get(
                                        "candidate_id__industry_type__label_name", ""
                                    ),
                                    z.get("candidate_id__curr_gross", ""),
                                    z.get("candidate_id__exp_gross", ""),
                                    z.get(
                                        "candidate_id__available_to_start__label_name",
                                        "",
                                    ),
                                    z.get("candidate_id__location", "Not specified"),
                                    z.get("candidate_id__relocate", "Not specified"),
                                ]
                                row = [
                                    "Not Specified" if value is None else value
                                    for value in row
                                ]
                                writer.writerow(row)
                                serial_number += 1
                                # writer.writerow([serial_number] +[x["first_name"]]+[x["id"]]+[i["stage_id__stage_name"]]+[y["profile_match"]]+[x["qualification"]]+[x["work_exp"]]+[i["created_on"]]+
                                #                 [x["location"]]+[x["contact"]]+[x["email"]]+[m["tech_skill"]]+[m["soft_skill"]]+[x["linkedin_url"]]+[z["candidate_id__code_repo"]]+[i["source"]]+[z["candidate_id__type_of_job__label_name"]]+[z["candidate_id__industry_type__label_name"]]+
                                #                 [z["candidate_id__curr_gross"]]+[z["candidate_id__exp_gross"]]+[z["candidate_id__available_to_start__label_name"]]+[z["candidate_id__location"]]+[z["candidate_id__relocate"]])
                                #                 # [i["stage_id__stage_name"]]+list(y.values())+list(x.values())+list(z.values()))
                                # serial_number += 1
                            filepath = filepath.split("media/")[1]
                            file_name = filepath.split("csv_download/")[1]

                            return Response(
                                {
                                    "file_path": filepath,
                                    "success": True,
                                    "message": "csv file download successfully!",
                                    "file_name": file_name,
                                }
                            )
                    else:
                        pass
                        return Response({"message": "doesnot have any values"})
                except IndexError as e:
                    logger.info("IndexError :" + str(e))
                    return Response({"success": False})
            else:
                return Response({"success": False})
        except IndexError as e:
            logger.info("IndexErro :" + str(e))
            return Response({"success": False})
        except KeyError as e:
            logger.info("KeyError :" + str(e))
            return Response({"success": False})
        except Exception as e:
            filepath = filepath.split("media/")[1]
            if "jd_download/" in filepath:
                file_name = filepath.split("jd_download/")[1]
            elif "csv_download/" in filepath:
                file_name = filepath.split("csv_download/")[1]

            return Response(
                {
                    "success": False,
                    "message": "does not exist a Match_score for candidate",
                    "file_path": filepath,
                    "file_name": file_name,
                }
            )
            # qualification=list(JD_qualification.objects.filter(jd_id=job,jd_id__jd_status=1).values_list("qualification",flat=True))


from application.models import *
from jobs.views import adv_match_calculation


class match_canid_jdid(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user, updated_by = admin_account(request)
        except:
            user = request.user
        request = self.request
        sub_user = request.user
        can_id = request.GET["can_id"]
        jd_id = request.GET["jd_id"]
        plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
        basic_matching_plan = [6, 7, 10, 11]
        if plan_id in basic_matching_plan:
            if not applicants_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).exists():
                if "matching" in self.request.GET:
                    adv_match = AdvancedAIMatching(jd_id, can_id, user, "candidates",sub_user = sub_user)
                else:
                    basic_score = basic_matching(can_id, jd_id, user, request)
                    return Response(basic_score)

            else:
                descriptive = client_features_balance.objects.get(
                    client_id=user, feature_id=6
                ).available_count
                if descriptive > 0:
                    if "matching" in self.request.GET:
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "candidates",sub_user = sub_user
                        )
                else:
                    if "matching" in self.request.GET:
                        descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "candidates",sub_user = sub_user
                        )

        else:
            if not applicants_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).exists():
                if "matching" in self.request.GET:
                    adv_match = AdvancedAIMatching(jd_id, can_id, user, "candidates",sub_user = sub_user)
                else:
                    basic_score = basic_matching(can_id, jd_id, user, request)
                    # if basic_score["skills_percent"] > 0:
                    #     content = zita_matched_candidates(user,jd_id,can_id,'basic')
                    return Response(basic_score)
            else:
                descriptive = client_features_balance.objects.get(
                    client_id=user, feature_id=6
                ).available_count
                if descriptive > 0:
                    if "matching" in self.request.GET:
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "candidates",sub_user = sub_user
                        )
                else:
                    if "matching" in self.request.GET:
                        descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "candidates",sub_user = sub_user
                        )
            jd_skills = []
            matched_skills = []
            not_matched_skills = []
            skills_percent = 0
            qualification_percent = 0
            qualification = []
            matched_qualification = []
            not_matched_qualification = []
            location = []
            location_percent = 0
            not_matched_location = []
            matched_location = []

        if Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id).exists():
            overall_percentage = (
                Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id)
                .values_list("overall_percentage")
                .last()[0]
            )
        else:
            overall_percentage = 0
        if overall_percentage > 0:
            content = zita_matched_candidates(user, jd_id, can_id, "ai")
        ai_matching = client_features_balance.objects.filter(
            client_id=user, feature_id=55
        ).exists()
        result = adv_match_calculation(jd_id, can_id, user, request)
        # user=request.user.first_last_name
        # first_last_name = User.objects.filter(username=user).values("first_name","last_name")
        # first_last_name = first_last_name.annotate(value=Concat('first_name', V(' '), 'last_name',output_field=CharField()))
        # user = first_last_name[0]['value']
        # candi=employer_pool.objects.get(id=can_id)
        # # candidate = None
        # # if candi.first_name != None and candi.last_name != None:
        # #    candidate =  str(candi.first_name)+" "+str(candi.last_name)
        # # elif candi.first_name != None and candi.last_name == None:
        # #    candidate =  str(candi.first_name)
        # # d = {
        # #             'user' : user,
        # #
        # #             'can' : candidate,
        # #             'count' : count,
        # #             'job_id':pk

        # #         }

        # status = jd_nice_to_have.objects.filter(jd_id_id=jd_id,nice_to_have__isnull = False).exclude(nice_to_have='').exists()

        # if status==False:
        #     result['non_technical'] = [entry for entry in result['non_technical'] if entry['title'] != 'Nice to Have']

        # data = Matched_percentage.objects.filter(jd_id = jd_id,candidate_id = can_id).values("title","percentage","description","jd_id")
        # non_tech = ["Industry-Specific Experience","Domain-Specific Experience","Certifications","Location Alignment","Cultural Fit","References and Recommendations"]
        # tech= ["Skills","Roles and Responsibilities","Experience","Technical Tools and Languages","Educational Qualifications","Soft Skills"]
        # non_technical = []
        # technical = []
        # try:
        #     custom_order = ["skills","roles","exp","qualification","industry_exp","domain_exp","certification","tech_tools","soft_skills","location","cultural_fit","ref"]
        #     score = Weightage_Matching.objects.filter(
        #     jd_id=jd_id,user_id=self.request.user).values("criteria__title", "score").order_by(
        #     Case(*[When(criteria__title=title, then=position) for position, title in enumerate(custom_order)], default=len(custom_order), output_field=IntegerField()))

        #     # score = Weightage_Matching.objects.filter(jd_id=jd_id,user_id=self.request.user).values("criteria__title","score")
        # except:
        #     pass
        # nontech=0
        # overall = 0
        # for i,x in zip(data,score):
        #     validate = ["Industry-Specific Experience","Technical Tools and Languages","Soft Skills"]
        #     if i['title'] in tech:
        #         score = Weightage_Matching.objects.get(jd_id=jd_id,user_id=self.request.user,criteria=weightage_calculation(i['title'])).score
        #         i["percentage"] = percentage_matching(i["percentage"],score)
        #         i['skill_percentage'] = score
        #         overall +=i["percentage"]
        #         technical.append(i)
        #     elif i['title'] in non_tech:
        #         score = Weightage_Matching.objects.get(jd_id=jd_id,user_id=self.request.user,criteria=weightage_calculation(i['title'])).score
        #         i["percentage"] = percentage_matching(i["percentage"],score)
        #         i['skill_percentage'] = score
        #         nontech +=i["percentage"]
        #         non_technical.append(i)
        # non_technical_order = ["Industry-Specific Experience", "Domain-Specific Experience", "Certifications", "Cultural Fit", "References and Recommendations", "Location Alignment"]
        # technical_order = ["Skills", "Roles and Responsibilities", "Experience", "Technical Tools and Languages", "Soft Skills", "Educational Qualifications"]
        # # Matched_percentage.objects.filter(jd_id= jd_id,candidate_id = can_id).update(overall_percentage = overall)
        # # Matched_candidates.objects.filter(jd_id=jd_id,candidate_id=can_id).update(profile_match=overall)
        # non_technical = sorted(non_technical, key=lambda item: non_technical_order.index(item['title']))
        # technical = sorted(technical, key=lambda item: technical_order.index(item['title']))
        ai_matching_plan = tmeta_plan.objects.filter(
            plan_id__in=[6, 7, 10, 11]
        ).values_list("plan_id", flat=True)
        apply_match = applicants_status.objects.filter(
            jd_id=jd_id, candidate_id=can_id
        ).exists()
        features, plan = plan_checking(user, "resume")
        total_length = employer_pool.objects.filter(
            client_id=user, first_name__isnull=False, email__isnull=False
        ).values_list("id", flat=True)
        active_resume = employer_pool.objects.filter(
            client_id=user, first_name__isnull=False, email__isnull=False
        ).values_list("id", flat=True)[: int(features)]
        blocked_resume = []
        if len(total_length) > int(features):
            blocked_resume = applicant_descriptive.objects.filter(jd_id=jd_id, candidate_id=can_id, is_active=True).values_list('candidate_id',flat=True)
        candidates_ai = candidates_ai_matching.objects.filter(
            jd_id=jd_id, candidate_id=can_id
        ).exists()
        block_descriptive = applicant_descriptive.objects.filter(
            jd_id=jd_id, candidate_id=can_id, is_active=True
        ).exists()
        degrade_ai_match = False
        status = (
            jd_nice_to_have.objects.filter(jd_id_id=jd_id, nice_to_have__isnull=False)
            .exclude(nice_to_have="")
            .exists()
        )
        if status == False:
            result["non_technical"] = [
                entry
                for entry in result["non_technical"]
                if entry["title"] != "Nice to Have"
            ]

        overall_output = {
            "status": status,
            "source": {"jd_skills": [], "qualification": []},
            "matched_data": {"matched_skills": [], "matched_qualification": []},
            "not_matched_data": {
                "not_matched_skills": [],
                "not_matched_qualification": [],
            },
            "skills_percent": 0,
            "qualification_percent": 0,
            "overall_percentage": result["overall"],
            "non_tech_percentage": result["nontech"],
            "candidate_id": can_id,
            "ai_matching": ai_matching,
            "plan": plan_id,
            "non_technical": result["non_technical"],
            "technical": result["technical"],
            "ai_matching_plan": ai_matching_plan,
            "apply_match": apply_match,
            "active_resume": active_resume,
            "blocked_resume": blocked_resume,
            "candidates_ai": candidates_ai,
            "block_descriptive": block_descriptive,
            "degrade_ai_match": degrade_ai_match,
        }
        return Response(overall_output)

    def post(self, request):
        try:
            user, updated_by = admin_account(request)
        except:
            user = request.user
            
        request = self.request
        sub_user = request.user
        can_id = request.POST["can_id"]
        jd_id = request.POST["jd_id"]
        plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
        basic_matching_plan = [6, 7, 10, 11]
        if plan_id in basic_matching_plan:
            if not applicants_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).exists():
                if "matching" in self.request.POST:
                    adv_match = AdvancedAIMatching(jd_id, can_id, user, "candidates",sub_user = sub_user)
                else:
                    basic_score = basic_matching(can_id, jd_id, user, request)
                    return Response(basic_score)

            else:
                descriptive = client_features_balance.objects.get(
                    client_id=user, feature_id=6
                ).available_count
                if descriptive > 0:
                    if "matching" in self.request.POST:
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "candidates",sub_user = sub_user
                        )
                else:
                    if "matching" in self.request.POST:
                        descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "candidates",sub_user = sub_user
                        )

        else:
            if not applicants_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id
            ).exists():
                if "matching" in self.request.POST:
                    adv_match = AdvancedAIMatching(jd_id, can_id, user, "candidates",sub_user = sub_user)
                else:
                    basic_score = basic_matching(can_id, jd_id, user, request)
                    # if basic_score["skills_percent"] > 0:
                    #     content = zita_matched_candidates(user,jd_id,can_id,'basic')
                    return Response(basic_score)
            else:
                descriptive = client_features_balance.objects.get(
                    client_id=user, feature_id=6
                ).available_count
                if descriptive > 0:
                    if "matching" in self.request.POST:
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "candidates",sub_user = sub_user
                        )
                else:
                    if "matching" in self.request.POST:
                        descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                        adv_match = AdvancedAIMatching(
                            jd_id, can_id, user, "candidates",sub_user= sub_user
                        )
            jd_skills = []
            matched_skills = []
            not_matched_skills = []
            skills_percent = 0
            qualification_percent = 0
            qualification = []
            matched_qualification = []
            not_matched_qualification = []
            location = []
            location_percent = 0
            not_matched_location = []
            matched_location = []

        if Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id).exists():
            overall_percentage = (
                Matched_percentage.objects.filter(jd_id=jd_id, candidate_id=can_id)
                .values_list("overall_percentage")
                .last()[0]
            )
        else:
            overall_percentage = 0
        # if overall_percentage > 0:
        #      content = zita_matched_candidates(user,jd_id,can_id,'ai')
        ai_matching = client_features_balance.objects.filter(
            client_id=user, feature_id=55
        ).exists()
        result = adv_match_calculation(jd_id, can_id, user, request)
        # data = Matched_percentage.objects.filter(jd_id = jd_id,candidate_id = can_id).values("title","percentage","description","jd_id")
        # non_tech = ["Industry-Specific Experience","Domain-Specific Experience","Certifications","Location Alignment","Cultural Fit","References and Recommendations"]
        # tech= ["Skills","Roles and Responsibilities","Experience","Technical Tools and Languages","Educational Qualifications","Soft Skills"]
        # non_technical = []
        # technical = []
        # try:
        #     custom_order = ["skills","roles","exp","qualification","industry_exp","domain_exp","certification","tech_tools","soft_skills","location","cultural_fit","ref"]
        #     score = Weightage_Matching.objects.filter(
        #     jd_id=jd_id,user_id=self.request.user).values("criteria__title", "score").order_by(
        #     Case(*[When(criteria__title=title, then=position) for position, title in enumerate(custom_order)], default=len(custom_order), output_field=IntegerField()))

        #     # score = Weightage_Matching.objects.filter(jd_id=jd_id,user_id=self.request.user).values("criteria__title","score")
        # except:
        #     pass
        # nontech=0
        # overall = 0
        # for i,x in zip(data,score):
        #     validate = ["Industry-Specific Experience","Technical Tools and Languages","Soft Skills"]
        #     if i['title'] in tech:
        #         score = Weightage_Matching.objects.get(jd_id=jd_id,user_id=self.request.user,criteria=weightage_calculation(i['title'])).score
        #         i["percentage"] = percentage_matching(i["percentage"],score)
        #         i['skill_percentage'] = score
        #         overall +=i["percentage"]
        #         technical.append(i)
        #     elif i['title'] in non_tech:
        #         score = Weightage_Matching.objects.get(jd_id=jd_id,user_id=self.request.user,criteria=weightage_calculation(i['title'])).score
        #         i["percentage"] = percentage_matching(i["percentage"],score)
        #         i['skill_percentage'] = score
        #         nontech +=i["percentage"]
        #         non_technical.append(i)
        # non_technical_order = ["Industry-Specific Experience", "Domain-Specific Experience", "Certifications", "Cultural Fit", "References and Recommendations", "Location Alignment"]
        # technical_order = ["Skills", "Roles and Responsibilities", "Experience", "Technical Tools and Languages", "Soft Skills", "Educational Qualifications"]
        # # Matched_percentage.objects.filter(jd_id= jd_id,candidate_id = can_id).update(overall_percentage = overall)
        # # Matched_candidates.objects.filter(jd_id=jd_id,candidate_id=can_id).update(profile_match=overall)
        # non_technical = sorted(non_technical, key=lambda item: non_technical_order.index(item['title']))
        # technical = sorted(technical, key=lambda item: technical_order.index(item['title']))
        ai_matching_plan = tmeta_plan.objects.filter(
            plan_id__in=[6, 7, 10, 11]
        ).values_list("plan_id", flat=True)
        apply_match = applicants_status.objects.filter(
            jd_id=jd_id, candidate_id=can_id
        ).exists()
        features, plan = plan_checking(user, "resume")
        total_length = employer_pool.objects.filter(
            client_id=user, first_name__isnull=False, email__isnull=False
        ).values_list("id", flat=True)
        active_resume = employer_pool.objects.filter(
            client_id=user, first_name__isnull=False, email__isnull=False
        ).values_list("id", flat=True)[: int(features)]
        blocked_resume = []
        if len(total_length) > int(features):
            blocked_resume = applicant_descriptive.objects.filter(jd_id=jd_id, candidate_id=can_id, is_active=True).values_list('candidate_id',flat=True)
        candidates_ai = candidates_ai_matching.objects.filter(
            jd_id=jd_id, candidate_id=can_id
        ).exists()
        block_descriptive = applicant_descriptive.objects.filter(
            jd_id=jd_id, candidate_id=can_id, is_active=True
        ).exists()
        degrade_ai_match = False
        overall_output = {
            "source": {"jd_skills": [], "qualification": []},
            "matched_data": {"matched_skills": [], "matched_qualification": []},
            "not_matched_data": {
                "not_matched_skills": [],
                "not_matched_qualification": [],
            },
            "skills_percent": 0,
            "qualification_percent": 0,
            "overall_percentage": result["overall"],
            "non_tech_percentage": result["nontech"],
            "candidate_id": can_id,
            "ai_matching": ai_matching,
            "plan": plan_id,
            "non_technical": result["non_technical"],
            "technical": result["technical"],
            "ai_matching_plan": ai_matching_plan,
            "apply_match": apply_match,
            "active_resume": active_resume,
            "blocked_resume": blocked_resume,
            "candidates_ai": candidates_ai,
            "block_descriptive": block_descriptive,
            "degrade_ai_match": degrade_ai_match,
        }
        return Response(overall_output)


# def save_time_to_file(time_taken, can_id,total_tokens):
#     file_name = "timetaken_applicants.txt"
#     with open(file_name, 'a+') as file:
#         file.write(f"Can ID: {can_id}   Time taken: {time_taken} seconds    token consumed : {total_tokens}\n")


class match_jdid(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user, updated_by = admin_account(request)
        except:
            if request.user.is_staff:
                user = request.user
            else:
                user = employer_pool.objects.get(id=can_id).client_id
        request = self.request
        sub_user = request.user
        data = request.GET.get("location", None)
        jd_id = request.GET["jd_id"]
        if data:
            if data == "zita":
                data = "zitamatch"
            if data == "database":
                data = "database"
        if "candidates" in self.request.GET:
            candi_len = json.loads(self.request.GET["candidates"])
            # update_count = bulk_matching.objects.filter(jd_id= jd_id,user_id = user).update(count=0,is_active=False)
            candidate = (
                employer_pool.objects.filter(id__in=candi_len)
                .values("id")
                .order_by("-id")[: int(len(candi_len))]
            )
            matching_loader.objects.create(
                jd_id=JD_form.objects.get(id=jd_id), initial_count=len(candi_len)
            )
        elif "count" in self.request.GET:
            count = self.request.GET["count"]
            candidate = (
                employer_pool.objects.filter(
                    Q(client_id=user)
                    & Q(first_name__isnull=False)
                    & Q(email__isnull=False)
                    & ~Q(email=""),
                    jd_id=jd_id,
                )
                .values("id")
                .order_by("-id")[: int(count)]
            )
        else:
            candidate = (
                employer_pool.objects.filter(
                    Q(client_id=user)
                    & Q(first_name__isnull=False)
                    & Q(email__isnull=False)
                    & ~Q(email="")
                )
                .values("id")
                .order_by("-id")
            )
        plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
        count_matching = 0
        try:
            for i in candidate:
                can_id = i["id"]
                basic_matching_plan = [6, 7, 10, 11]
                if plan_id in basic_matching_plan:
                    if not applicants_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id
                    ).exists():
                        # if not client_features_balance.objects.filter(Q(client_id=user, feature_id=62)).exists():
                        #     basic_score = basic_matching(can_id,jd_id,user,request)
                        #     if basic_score["skills_percent"] > 0:
                        #         content = zita_matched_candidates(user,jd_id,can_id,'basic')
                        # else:
                        if candidate_parsed_details.objects.filter(
                            candidate_id=can_id
                        ).exists():
                            file_content = candidate_parsed_details.objects.get(
                                candidate_id=can_id
                            ).resume_description
                        else:
                            file_content = None
                            if unlocked_candidate.objects.filter(
                                user_id=user, candidate_id=can_id
                            ).exists():
                                if unlocked_candidate.objects.filter(
                                    user_id=user, candidate_id=can_id
                                ).exists():
                                    file_content = (
                                        unlocked_candidate.objects.filter(
                                            user_id=user, candidate_id=can_id
                                        )
                                        .last()
                                        .unlocked_candidate.sourcing_data
                                    )
                                    if isinstance(file_content, str):
                                        file_content = json.loads(file_content)
                                    file_content = file_content.pop(
                                        "member_groups_collection", None
                                    )
                        if not candidate_profile_detail.objects.filter(
                            candidate_id=can_id
                        ).exists():
                            candidate_profile = profile_summary(file_content,can_id=can_id,sub_user=sub_user)
                            candidate_profile_detail.objects.create(
                                candidate_id=employer_pool.objects.get(id=can_id),
                                profile_summary=candidate_profile,
                            )
                        if "candidates" in self.request.GET:
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "candidates",sub_user = sub_user
                            )
                            count_matching = count_matching + 1
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        else:
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
                                jd_id, can_id, user, "applicants",sub_user = sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        else:
                            descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user = sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")

                else:
                    if not applicants_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id
                    ).exists():
                        if "candidates" in self.request.GET:
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "candidates",sub_user = sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
                            count_matching = count_matching + 1
                        else:
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
                                jd_id, can_id, user, "applicants",sub_user= sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        else:
                            descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user = sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
            if "candidates" in self.request.GET:
                if matching_loader.objects.filter(jd_id=jd_id).exists():
                    matching_loader.objects.filter(jd_id=jd_id).update(
                        reduce_count=count_matching
                    )
                jd_values = JD_form.objects.filter(id=jd_id).values("job_title")
                job_title_value = jd_values[0]["job_title"]
                jd = JD_form.objects.get(id=jd_id)
                notify.send(
                    request.user,
                    recipient=request.user,
                    action_object=jd,
                    description=data,
                    verb="AI Matching process completed for {}".format(
                        job_title_value.title()
                    ),
                )
            matching_loader.objects.filter(jd_id=jd_id).delete()
            return Response({"suceess": True})
        except Exception as e:
            print("Exception in Match Jdid-->",str(e))
            matching_loader.objects.filter(jd_id=jd_id).delete()
            return Response({"suceess": False, "Error": str(e)})


class match_canid(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        can_id = request.GET["can_id"]
        try:
            user, updated_by = admin_account(request)
        except:
            if request.user.is_staff:
                user = request.user
            else:
                user = employer_pool.objects.get(id=can_id).client_id
        request = self.request
        sub_user = request.user
        jobs = JD_form.objects.filter(user_id=user.id, jd_status_id=1).values("id")
        plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
        try:
            for i in jobs:
                jd_id = i["id"]
                basic_matching_plan = [6, 7, 10, 11]
                if plan_id in basic_matching_plan:
                    if not applicants_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id
                    ).exists():
                        # if not client_features_balance.objects.filter(Q(client_id=user, feature_id=62)).exists():
                        basic_score = basic_matching(can_id, jd_id, user, request)
                        if basic_score["skills_percent"] > 0:
                            content = zita_matched_candidates(
                                user, jd_id, can_id, "basic"
                            )
                        # else:
                        #     adv_match = AdvancedAIMatching(jd_id,can_id,user,'candidates')
                        #     content = zita_matched_candidates(user,jd_id,can_id,'basic')
                    else:
                        if candidate_parsed_details.objects.filter(
                            candidate_id=can_id
                        ).exists():
                            file_content = candidate_parsed_details.objects.get(
                                candidate_id=can_id
                            ).resume_description
                        else:
                            file_content = None
                            if unlocked_candidate.objects.filter(
                                user_id=user, candidate_id=can_id
                            ).exists():
                                if unlocked_candidate.objects.filter(
                                    user_id=user, candidate_id=can_id
                                ).exists():
                                    file_content = (
                                        unlocked_candidate.objects.filter(
                                            user_id=user, candidate_id=can_id
                                        )
                                        .last()
                                        .unlocked_candidate.sourcing_data
                                    )
                                    if isinstance(file_content, str):
                                        file_content = json.loads(file_content)
                                    file_content = file_content.pop(
                                        "member_groups_collection", None
                                    )
                                    if "member_experience_collection" in file_content:
                                        file_content[
                                            "member_experience_collection"
                                        ].sort(
                                            key=lambda x: x["last_updated"],
                                            reverse=True,
                                        )
                        if not candidate_profile_detail.objects.filter(
                            candidate_id=can_id
                        ).exists():
                            candidate_profile = profile_summary(file_content,can_id=can_id,sub_user=sub_user)
                            candidate_profile_detail.objects.create(
                                candidate_id=employer_pool.objects.get(id=can_id),
                                profile_summary=candidate_profile,
                            )

                        descriptive = client_features_balance.objects.get(
                            client_id=user, feature_id=6
                        ).available_count
                        if descriptive > 0:
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user = sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        else:
                            descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user = sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")

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
                                jd_id, can_id, user, "applicants",sub_user = sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
                        else:
                            descriptive = Descriptive_Analaysis(jd_id, can_id, user)
                            adv_match = AdvancedAIMatching(
                                jd_id, can_id, user, "applicants",sub_user = sub_user
                            )
                            content = zita_matched_candidates(user, jd_id, can_id, "ai")
            return Response({"suceess": True})
        except Exception as e:
            print("Exception in Match Can-id:------>",str(e))
            return Response({"suceess": False, "Error": str(e)})


class jd_industry_type(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user = request.user
        if not Personal_Info.objects.filter(user_id=user).exists():
            admin_id, updated_by = admin_account(request)
        else:
            candidate_id = Personal_Info.objects.get(user_id=user).application_id
            if employer_pool.objects.filter(candidate_id=candidate_id).exists():
                admin_id = (
                    employer_pool.objects.filter(candidate_id=candidate_id)
                    .last()
                    .client_id
                )
            else:
                if employer_pool.objects.filter(candidate_id=candidate_id).exists():
                    admin_id = employer_pool.objects.get(
                        candidate_id=candidate_id
                    ).client_id
                else:
                    admin_id = None
        industry_id = request.GET.get("industry_id", None)
        if industry_id != None:
            if not tmeta_industry_type.objects.filter(value=industry_id).exists():
                industry_id = tmeta_industry_type.objects.create(
                    value=industry_id,
                    description=industry_id,
                    label_name=industry_id,
                    client_id=admin_id,
                )
        data = tmeta_industry_type.objects.filter(client_id=None).values_list(
            "value", flat=True
        )
        data1 = tmeta_industry_type.objects.filter(client_id=admin_id).values_list(
            "value", flat=True
        )
        data = chain(data, data1)
        sorted_industry_list = sorted(data, key=lambda x: x.lower())
        return Response(sorted_industry_list)


class external_job_post(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pk = request.GET.get("pk")
        try:
            whatjob = request.GET.get("whatjob")
            if whatjob is not None:
                whatjob_activity.objects.get_or_create(jd_id=pk)
                if whatjob_activity.objects.filter(jd_id=pk).exists():
                    whatjob = whatjob_activity.objects.filter(jd_id=pk).update(
                        whatjob=whatjob
                    )
                    whatjob = whatjob_activity.objects.get(jd_id=pk).whatjob
            else:
                whatjob = whatjob_activity.objects.get(jd_id=pk).whatjob
        except Exception as e:
            pass
        response_data = {"whatjobs": bool(whatjob)}

        return Response(response_data)


class jd_creation_ai(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
        
            total_token = 0
            success = False
            company = UserHasComapny.objects.get(user=self.request.user).company.company_name
            request = self.request
            response = JD_creation_AI(request, company)
            print("+++++++++++++++",type(response))
            if isinstance(response,dict):
                zita_service = response.get('error')
                if zita_service:
                    return Response({"success": False,"standalone":True,"message": zita_service})
            admin_id, updated_by = admin_account(request)
            if isinstance(response, list):
                response = response[0]
            mandatory_skills, nice_to_have = JD_features(
                response,
                request.POST["mandatory_skills"],
                request.POST.get("Nice_to_Have"),
            )
            response = remove_duplicate_skills(response)
            html_data = JD_convert_to_html(response)
            html_data = removeScript(html_data)
            titles = ["Job Title", "jobTitle", "job_title"]
            if response:
                for i in titles:
                    job_title = response.get(i, None)
                    if job_title:
                        job_title = job_title
                        break
                if job_title == None:
                    job_title = self.request.POST.get("jobTitle", "")
                skills_list = []
                skills_match = []
                keyword = ["skills_keywords", "skills", "Skills"]
                for x in keyword:
                    skills_match = response.get(x, None)
                    if isinstance(skills_match, str):
                        skills_match = re.split(r", |,|\. ", skills_match)
                        break
                tools = ["Tools And Technologies", "Tools and Technologies"]
                for i in tools:
                    tools = response.get(i, None)
                    if tools:
                        if isinstance(tools, str):
                            tools = tools.split(",")
                        if skills_match:
                            skills_match += tools
                            break
                        elif skills_match == [] or skills_match == None:
                            skills_match = tools
                            break
                if skills_match:
                    skills_match = remove_pointers(skills_match)
                    for idx, skill in enumerate(skills_match):
                        skills_list.append({"id": idx, "skill": skill})

                request = self.request.POST
                exp = request.get("Overview_the_Role", None)
                if exp != None:
                    matches = re.findall(
                        r"(\d+)\s*(?:year|yr|years)", exp, re.IGNORECASE
                    )
                    if matches:
                        for match in matches:
                            exp = int(match)
                    elif matches == []:
                        exp = 0
                domain = self.request.POST.get("Industry_and_Domain", "")
                if not tmeta_industry_type.objects.filter(
                    Q(value=domain.capitalize()) | Q(value=domain)
                ).exists():
                    tmeta_industry_type.objects.create(
                        value=domain.capitalize(),
                        description=domain.capitalize(),
                        label_name=domain,
                        client_id=admin_id,
                    )
                mandatory_skills = list(
                    [
                        item.upper()
                        for item in set(
                            item.lower().strip() for item in mandatory_skills
                        )
                    ]
                )
                mandatory_skills = [
                    i for i in mandatory_skills if i not in nice_to_have
                ]
                context = {
                    "success": True,
                    "job_title": job_title,
                    "job_description": html_data,
                    "skills": mandatory_skills,
                    "min_exp": request.get("min_exp"),
                    "max_exp": request.get("max_exp", None),
                    "total_token": total_token,
                    "mandatory_skills": mandatory_skills,
                    "nice_to_have": nice_to_have,
                }
                return Response(context)
            else:
                return Response(
                    {
                        "success": False,
                        "message ": "The Create JD and doesnot Parsed Correctly. Please try Again",
                        "total_token": total_token,
                    }
                )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message ": "The Create JD and doesnot Parsed Correctly. Please try Again",
                    "total_token": total_token,
                    "error": e,
                }
            )

import time
class get_comparative_analysis(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        1) Need Job id for which we are comparing
        2) Categories in which we are comparing
        3) Minimum of 2 applicants has to be selected
        4) Show which candidate is best suitable for the job

        REQUIREMENTS
        1) Job_id is a required input
        2) Categories should we given as List
        3) Finalise the input format - How are we getting the resumes ? Are we taking their details from the DB or will the resumes be sent? What else are the places we will use this?
        4) Output format : Should we rank them from best to worst match or give scores?
        """
        sum = 0
        job_id: int = self.request.GET["job_id"]
        user_id = request.user.id
        resume_not_found = []
        # This is a list of candidate ids and we will use it to retrieve their details for comparision
        candidate_ids = request.GET.get("candidate_ids", None)
        candidate_ids: list = (
            [candidate_id.strip() for candidate_id in candidate_ids.split(",")]
            if candidate_ids
            else []
        )
        categories = request.GET.get("categories")
        categories: list = (
            [category.strip() for category in categories.split(",")]
            if request.GET.get("categories")
            else []
        )
        try:
            if job_id and categories and is_category_valid(categories):
                jd_details = JD_form.objects.filter(id=int(job_id)).first()
                if jd_details and len(candidate_ids) > 1 and len(candidate_ids) <= 5:
                    # job_description = jd_details.job_description
                    # can_ids = str(candidate_ids)
                    job_description = FT.jd_conversion(job_id)
                    # Converting richtext to string format
                    job_description = rtf_to_text(job_description)
                    candidate_analysis = []
                    resumes = []
                    if job_description:
                        candidate_ids.sort(key=lambda x: int(x))
                        for candidate in candidate_ids:
                            is_active = False
                            if is_active:
                                resume = Resume_overview.objects.filter(
                                    application_id=candidate
                                ).first()
                                candidate_id_string = f"Candidate id : {candidate}"
                                if resume:
                                    resumes.append(
                                        candidate_id_string + " " + resume.parsed_resume
                                    )
                                else:
                                    resume = (
                                        candidate_parsed_details.objects.filter(
                                            candidate_id=candidate
                                        )
                                        .first()
                                        .parsed_text
                                    )
                                    if resume and resume.strip() != "":
                                        resumes.append(
                                            candidate_id_string + " " + resume
                                        )
                                    else:
                                        resume_not_found.append(str(candidate))
                            else:
                                data = FT.resume_conversion(candidate)
                                resumes.append(data)
                        # For AI analysis
                        if resumes and len(resumes) <= 5:
                            print("^^^lenlenlenlen&",len(resumes))
                            if len(resumes) > 1:
                               
                                try:
                                    time.sleep(10)
                                    candidate_analysis,token = analysis_from_AI(resumes,request.GET.get("categories"),job_description,candidate_ids,user_id = user_id)
                                    print("candidate_analysis@@@@@@@@@",candidate_analysis)
                                    if isinstance(candidate_analysis,dict):
                                        zita_service = candidate_analysis.get('candidates')
                                        if zita_service:
                                            if isinstance(zita_service,dict):
                                                zita_service = zita_service.get('error')
                                                if zita_service:
                                                    return Response({"success": False,"standalone":True,"message":zita_service,"status": False})
                                except Exception as e:
                                    print("Comparative APISERVICE exceptions",e)
                                    candidate_analysis, token = (comparative_analysis_from_AI_4(resumes,request.GET.get("categories"),job_description,))
                            elif len(resumes) == 4:
                                print("#####################")
                                time.sleep(10)
                                candidate_analysis, token = (
                                    comparative_analysis_from_AI_4(
                                        resumes,
                                        request.GET.get("categories"),
                                        job_description,
                                    )
                                )
                            elif len(resumes) == 5:
                                print("$$$$$$$$$$$$$$$$$$")
                                candidate_analysis, token = (
                                    comparative_analysis_from_AI_5(
                                        resumes,
                                        request.GET.get("categories"),
                                        job_description,
                                    )
                                )
                            sum_token = 0
                            print("candidate_analysis!!!!!!!!!!",candidate_analysis)
                            try:
                                if isinstance(candidate_analysis, str):
                                    candidate_analysis = json.loads(candidate_analysis)
                            except Exception as e:
                                pass
                            # Getting candidiate info for UI
                            if isinstance(candidate_analysis, tuple):
                                candidate_analysis = candidate_analysis[0]
                            if "candidates" in candidate_analysis:
                                for candidate in candidate_analysis["candidates"]:
                                    candidate = data_conversion(candidate, categories)
                                    candidate_id = candidate.get("candidate_id", None)
                                    if candidate_id == None:
                                        listof_candidates = ["candidateid", "Candidat id"]
                                        for i in listof_candidates:
                                            if candidate.get(i):
                                                candidate_id = candidate.get(i)
                                                break
                                        # candidate_id = candidate.get("candidateid",None)
                                    candidate["jobid"] = job_id
                                    # getting info from DB
                                    stage_details = applicants_status.objects.filter(
                                        jd_id_id=job_id,
                                        candidate_id_id=candidate_id,
                                        status_id__in=[1, 2, 3, 4, 7],
                                    ).values(
                                        "stage_id__stage_name",
                                        "stage_id__stage_color",
                                        "candidate_id__first_name",
                                        "candidate_id__last_name",
                                    )
                                    sum = 0
                                    # candidates = candidate["categories"]
                                    for category in categories:
                                        # try:
                                        if "%" in str(candidate[category]):
                                            # If it is percentage then it will be out of 100 and not out of 10
                                            candidate[category] = (
                                                int(
                                                    candidate[category].replace("%", "")
                                                )
                                                / 10
                                            )
                                        elif (
                                            candidate[category] == None
                                            or candidate[category] == "None"
                                        ):
                                            candidate[category] = 0
                                        sum += candidate[category]
                                    # It is out of 10 so multiply by 10 to get the percentage
                                    average_percentage = int(sum) / len(categories)
                                    candidate["Average_match_percentage"] = str(
                                        average_percentage
                                    )
                                    candidate["Total_matching_percentage"] = candidate[
                                        "Total matching percentage"
                                    ]
                                    try:
                                        stage_details = stage_details[0]
                                        candidate["first_name"] = (
                                            stage_details["candidate_id__first_name"]
                                            if stage_details["candidate_id__first_name"]
                                            is not None
                                            else ""
                                        )
                                        candidate["last_name"] = (
                                            stage_details["candidate_id__last_name"]
                                            if stage_details["candidate_id__last_name"]
                                            is not None
                                            else ""
                                        )
                                        candidate["stage_name"] = (
                                            stage_details["stage_id__stage_name"]
                                            if stage_details["stage_id__stage_name"]
                                            is not None
                                            else "New Applicant"
                                        )
                                        candidate["stage_color"] = (
                                            stage_details["stage_id__stage_color"]
                                            if stage_details["stage_id__stage_name"]
                                            is not None
                                            else "#581845"
                                        )
                                    except Exception as e:
                                        print("Exception on Comparative FirstName",e)
                                        candidate["first_name"] = None
                                        candidate["last_name"] = None
                                        candidate["stage_name"] = None
                                        candidate["stage_color"] = None
                                    try:
                                        image_id = employer_pool.objects.get(
                                            id=candidate_id
                                        ).candidate_id.user_id
                                        image = Profile.objects.filter(
                                            user=image_id
                                        ).values("image")
                                        candidate["image"] = image[0]["image"]
                                    except:
                                        candidate["image"] = None
                                    overall = score_categories.objects.filter(
                                        jd_id_id=job_id, candidate_id_id=candidate_id
                                    ).first()
                                    candidate["overall_scorecard"] = (
                                        overall.overall_percentage if overall else None
                                    )
                            candidate_analysis["candidates"] = sorted(
                                candidate_analysis["candidates"],
                                key=lambda x: float(x["Average_match_percentage"]),
                            )
                            return Response({ "success": True,"analysis": candidate_analysis["candidates"],"token": sum_token,})
                            # return Response({"success": True, "analysis": candidate_analysis["candidates"],})
                        return Response({"success": False,"analysis": "","error_msg": "Resumes not found for the candidates",})
                    return Response({"success": False,"analysis": "","error_msg": "Job description not found",})
                return Response({"success": False,"analysis": "","error_msg": "Job does not exists or no candidates selected",})
            return Response({"success": False,"analysis": "","error_msg": "Job ID/categories is required",})
        except Exception as e:
            print("Comparative Exceptions",str(e))
            return Response({"success": False, "Error": str(e), "token": sum})


from datetime import datetime


class subscription_scheduler_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        dates = datetime.now()
        data = client_features_balance.objects.filter(
            client_id=6904, feature_id=10
        ).values("client_id_id")
        for i in data:
            client_id = i["client_id_id"]
            last_plan = subscriptions.objects.filter(client_id=client_id).last()
            plan = last_plan.plan_id.pk
            if last_plan.subscription_valid_till != None:
                end_subscription = last_plan.subscription_valid_till.replace(
                    tzinfo=None
                )
                startdate = None
                if dates > end_subscription:
                    count_reset = client_features_balance.objects.filter(
                        client_id=client_id
                    ).values("add_ons_id", "feature_id", "client_id")
                    descriptive = applicant_descriptive.objects.filter(
                        is_active=False
                    ).delete()
                    if len(count_reset) > 0:
                        for i in count_reset:
                            client_id = i["client_id"]
                            if addons_plan_features.objects.filter(
                                plan_id=plan, addon_id=i["add_ons_id"]
                            ).exists():
                                add_ons = addons_plan_features.objects.get(
                                    plan_id=plan, addon_id=i["add_ons_id"]
                                ).carry_forward
                                if not add_ons:
                                    startdate = last_plan.subscription_start_ts.replace(
                                        tzinfo=None
                                    )
                                    checking = comparative(
                                        one_month_checking(startdate, 1), dates
                                    )
                                    if not checking:
                                        client_features_balance.objects.filter(
                                            client_id=client_id,
                                            add_ons_id__is_carry=False,
                                        ).delete()
                                else:
                                    client_features_balance.objects.filter(
                                        client_id=client_id,
                                        add_ons_id__is_carry=True,
                                        add_ons_id=i["add_ons_id"],
                                        available_count=0,
                                    ).delete()
                            else:
                                if client_features_balance.objects.filter(
                                    client_id=client_id,
                                    feature_id=expire_addons(i["feature_id"]),
                                ).exists():
                                    plans_count = client_features_balance.objects.get(
                                        client_id=client_id, feature_id=i["feature_id"]
                                    ).plan_count
                                    if plans_count == 0:
                                        client_features_balance.objects.filter(
                                            client_id=client_id,
                                            feature_id=i["feature_id"],
                                        ).update(
                                            available_count=client_features_balance.objects.get(
                                                client_id=client_id,
                                                feature_id=expire_addons(
                                                    i["feature_id"]
                                                ),
                                            ).available_count
                                        )
                                else:
                                    client_features_balance.objects.filter(
                                        client_id=client_id, feature_id=i["feature_id"]
                                    ).update(available_count=0)

                if plan == 12 or plan == 11:
                    monthy_renewal = last_plan.subscription_start_ts.replace(
                        tzinfo=None
                    )
                    monthy_renewal = one_month_checking(monthy_renewal, 1)
                    if dates > monthy_renewal:
                        features_balance = plan_features.objects.filter(
                            plan_id=plan, feature_id_id__in=[10, 27, 53, 6]
                        )
                        for i in features_balance:
                            feature_update = Plan_upgrade(client_id, i)

            # if Change_Validation(client_id) == False:
            #     preview_plan_date = subscriptions.objects.filter(client_id=client_id).order_by('-subscription_id'). values_list('subscription_start_ts',flat=True)[1]
            #     checking = comparative(one_month_checking(preview_plan_date,1),dates)
            #     if not checking:
            #         client_features_balance.objects.filter(client_id=client_id,feature_id__in=[10,6,53,27]).update(available_count=0)
        return Response({"successs": True, "data": dates})


class candidate_to_job(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pass


class candidate_searching_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user_id = request.user
        user_id, updated_by = admin_account(request)
        jd_id = request.GET["jd_id"]
        # data = employer_pool.objects.filter(client_id=user_id,jd_id=jd_id,first_name__isnull=False,email__isnull=False).values('id','first_name','last_name')
        data = applicants_status.objects.filter(
            jd_id=jd_id,
            client_id=user_id,
            candidate_id__first_name__isnull=False,
            candidate_id__email__isnull=False,
        ).values(
            "candidate_id",
            "candidate_id__first_name",
            "candidate_id__last_name",
            "candidate_id__email",
        )
        data = data.annotate(
            stage_name=Case(
                When(stage_id__isnull=True, then=Value("New Applicant")),
                default=F("stage_id__stage_name"),
                output_field=CharField(),
            ),
            stage_color=Case(
                When(stage_id__isnull=True, then=Value("#581845")),
                default=F("stage_id__stage_color"),
                output_field=CharField(),
            ),
        )
        data = (
            data.annotate(
                image=Subquery(
                    Profile.objects.filter(
                        user_id=OuterRef("candidate_id__candidate_id__user_id")
                    )[:1].values("image")
                )
            ),
        )
        data = data[0]
        for i in data:
            i["first_name"] = i.pop("candidate_id__first_name")
            i["last_name"] = i.pop("candidate_id__last_name")
            i["email"] = i.pop("candidate_id__email")
            i["profile_image"] = i.pop("image")
        data = {"data": data}
        return Response(data)


import json


class download_analysis_csv(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        jd_id = request.GET["jd_id"]
        response_json = request.GET["response_json"]
        response_json = json.loads(str(response_json))
        try:
            csv_file_name, csv_file_path = downloaded_analysis_csv(response_json, jd_id)
            return Response(
                {"success": True, "FilePath": csv_file_path, "FileName": csv_file_name}
            )
        except Exception as e:
            return Response({"success": False, "Error": str(e)})


class roles(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = request.GET.get("role", None)
        admin_id, updated_by = admin_account(request)
        if role:
            role = role.strip()
            try:
                interview_role.objects.get(value=role)
            except:
                pass
        data = (
            interview_role.objects.filter(client_id=None)
            .values_list("value", flat=True)
            .distinct()
        )
        data1 = (
            attendees_role.objects.filter(user_id=admin_id)
            .values_list("role", flat=True)
            .distinct()
        )
        combined_data = set(chain(data, data1))
        unique_values = list(combined_data)
        return Response(unique_values)


"""
class weightage_matching(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    def get(self,request):
        pk = request.GET.get('pk')
        user=self.request.user
        users,updated_by = admin_account(request)
        users=users.id
        if jd_tech_matching.objects.filter(jd_id_id=pk,user_id=user).exists():
            pass
        else:
            if users != user:
                if jd_tech_matching.objects.filter(jd_id_id=pk,user_id=users).exists():
                    source_data = jd_tech_matching.objects.filter(jd_id_id=pk,user_id=users).values()
                    for i in source_data:
                        jd_tech_matching.objects.create(jd_id_id=pk,user_id=user,
                        skills=i["skills"],
                        roles=i["roles"],
                        exp=i["exp"],
                        qualification=i["qualification"],
                        tech_tools=i["tech_tools"],
                        soft_skills=i["soft_skills"],
                        industry_exp=i["industry_exp"],
                        domain_exp=i["domain_exp"],
                        certification=i["certification"],
                        location=i["location"],
                        cultural_fit=i["cultural_fit"],
                        ref=i["ref"]
                        )            
                else:
                    jd_tech_matching.objects.get_or_create(jd_id=JD_form.objects.get(id =pk),user_id = self.request.user,skills=20,roles=20,exp=20,qualification=10,tech_tools=20,soft_skills=10,industry_exp = 20,domain_exp=20,certification=20,location = 10,cultural_fit = 20,ref = 10)
        jd=jd_tech_matching.objects.filter(jd_id_id=pk,user_id=user).all() 
        tech_skills=jd.values('skills','roles','exp','qualification','tech_tools','soft_skills')[0]
        non_tech=jd.values('industry_exp','domain_exp','certification','location','cultural_fit','ref')[0] 
        context={
            'tech_skills':tech_skills,
            'non_tech':non_tech,
            'success':True
        }

    
        return Response(context)
       
    def post(self, request):
        try:
            data = request.data
            user = self.request.user
            jd_id = self.request.POST.get('jd_id',None)
            tech = self.request.POST.get('tech',None) 
            import json
            if tech:
                tech = json.loads(tech) 

                for i in tech:
                    if jd_tech_matching.objects.filter(jd_id=jd_id).exists():
                        data=jd_tech_matching.objects.filter(jd_id=jd_id,user_id=user).update(
                        skills=i['skills'],
                        roles=i['roles'],
                        exp=i['exp'],
                        qualification=i['qualification'],
                        tech_tools=i['tech_tools'],
                        soft_skills=i['soft_skills'],
                        industry_exp=i['industry_exp'],
                        domain_exp=i['domain_exp'],
                        certification=i['certification'],
                        location=i['location'],
                        cultural_fit=i['cultural_fit'],
                        ref=i['ref'] 
                        )
                        if not JD_form.objects.filter(id=jd_id,jd_status_id=1):
                            JD_form.objects.filter(id=jd_id).update(jd_status_id=7)

                        return Response({'message': 'JD skill Matching updated successfully'})

                    else:
                        jd_tech_matching.objects.create(jd_id=JD_form.objects.get(id=jd_id),
                            user_id=user,
                            skills=i['skills'],
                            exp=i['exp'],
                            roles=i['roles'],       
                            industry_exp=i['industry_exp'],             
                            cultural_fit=i['cultural_fit'],
                            location=i['location'],
                            qualification=i['qualification'],
                            certification=i['certification'],
                            tech_tools=i['tech_tools'],
                            soft_skills=i['soft_skills'],
                            domain_exp=i['domain_exp'],
                            ref=i['ref'],
                            )
                        if not JD_form.objects.filter(id=jd_id,jd_status_id=1):
                            JD_form.objects.filter(id=jd_id).update(jd_status_id=7)
                        return Response({'message': 'JD skill Matching created successfully'})


        except Exception as e: 
            return Response({"success":False,'error': str(e)})

"""


class weightage_matching(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        results = jd_message_templates.objects.filter(
            message_id__in=[1995, 2398], user_id=7917
        )

        pk = request.GET.get("pk")
        if not JD_form.objects.filter(id=pk, jd_status_id__in=[1, 3, 4]).exists():
            JD_form.objects.filter(id=pk).update(jd_status_id=7)

        can_id = request.GET.get("can_id", None)
        user = self.request.user
        users, updated_by = admin_account(request)
        users = users.id
        # tech_skills_criteria = ['Skills', 'Roles and Responsibilities', 'Experience', 'Educational Qualifications', 'Technical Tools and Languages', 'Soft Skills']
        tech_skills_criteria = [
            "skills",
            "roles",
            "exp",
            "qualification",
            "tech_tools",
            "soft_skills",
        ]
        # result=adv_match_calculation(pk,can_id,user,request)
        # status = jd_nice_to_have.objects.filter(jd_id_id=pk,nice_to_have__isnull = False).exclude(nice_to_have='').exists()
        # if jd_nice_to_have.objects.filter(jd_id_id=pk,nice_to_have__isnull = False).exclude(nice_to_have='').exists():
        # status = jd_nice_to_have.objects.filter(jd_id_id=pk,nice_to_have__isnull = False).exists()

        status = (
            jd_nice_to_have.objects.filter(jd_id_id=pk, nice_to_have__isnull=False)
            .exclude(nice_to_have="")
            .exists()
        )
        if status == False:
            default_scores = {
                "skills": 20,
                "roles": 20,
                "exp": 20,
                "qualification": 10,
                "tech_tools": 20,
                "soft_skills": 10,
                "industry_exp": 20,
                "domain_exp": 20,
                "certification": 20,
                "location": 10,
                "cultural_fit": 20,  # 'ref': 10,
            }
            if (
                status == False
                and Weightage_Matching.objects.filter(
                    jd_id_id=pk, criteria=13, score__gt=0
                ).exists()
            ):
                new_weightage = Weightage_Matching.objects.filter(
                    jd_id_id=pk, criteria__in=[7, 8, 9, 10, 11, 13]
                )
                for y in new_weightage:
                    y.score = default_scores.get(y.criteria.title, 0)
                    y.save()
        else:
            default_scores = {
                "skills": 20,
                "roles": 20,
                "exp": 20,
                "qualification": 10,
                "tech_tools": 20,
                "soft_skills": 10,
                "industry_exp": 20,
                "domain_exp": 20,
                "certification": 20,
                "location": 10,
                "cultural_fit": 20,
                "nice": 10,  # 'ref': 10,
            }
        if not Weightage_Matching.objects.filter(jd_id_id=pk, user_id=user).exists():
            if users != user:
                if Weightage_Matching.objects.filter(
                    jd_id_id=pk, user_id=users
                ).exists():
                    source_data = Weightage_Matching.objects.filter(
                        jd_id_id=pk, user_id=users
                    )
                    for i in source_data:
                        Weightage_Matching.objects.create(
                            jd_id_id=pk,
                            user_id=user,
                            criteria=i.criteria,
                            score=i.score,
                        )
                else:
                    criteria = tmeta_Weightage_Criteria.objects.all()
                    for i in criteria:
                        criteria_name = i.title
                        default_score = default_scores.get(criteria_name, 0)
                        Weightage_Matching.objects.get_or_create(
                            jd_id_id=pk, user_id=user, criteria=i, score=default_score
                        )

        tech_skills = {}
        non_tech = {}
        weightage_records = Weightage_Matching.objects.filter(
            jd_id_id=pk, user_id=user
        ).exclude(criteria=12)
        for i in weightage_records:
            criteria_name = i.criteria.title
            if criteria_name in tech_skills_criteria:
                tech_skills[criteria_name] = i.score
            else:
                non_tech[criteria_name] = i.score
        if status == False:
            sumdata = (
                non_tech["location"]
                + non_tech["certification"]
                + non_tech["industry_exp"]
                + non_tech["domain_exp"]
                + non_tech["cultural_fit"]
            )
            if sumdata != 100:
                nodata = 100 - sumdata
                non_tech["location"] = nodata + non_tech["location"]
                if "nice" in non_tech:
                    # if non_tech.get("nice",None) != None:
                    del non_tech["nice"]
        # if status and not Weightage_Matching.objects.filter(jd_id_id=pk,criteria = 13).exists():
        #     non_tech['nice']=0
        # elif status == False and not Weightage_Matching.objects.filter(jd_id_id=pk,criteria = 13).exists():
        #     non_tech['nice']=0
        # x=subscriptions.objects.filter(client_id=self.request.user.id).values("plan_id")
        context = {
            "tech_skills": tech_skills,
            "non_tech": non_tech,
            "success": True,
            "status": status,
        }
        return Response(context)

    def post(self, request):
        try:
            data = request.data
            user = self.request.user
            jd_id = self.request.POST.get("jd_id", None)
            tech = self.request.POST.get("tech", None)
            import json

            tech = json.loads(tech)

            tech1 = tech[0]
            keys_list = list(tech1.keys())
            values_list = list(tech1.values())

            for index, x in enumerate(keys_list):
                if Weightage_Matching.objects.filter(
                    jd_id_id=jd_id, user_id=user, criteria__title=x
                ).exists():
                    Weightage_Matching.objects.filter(
                        jd_id_id=jd_id, user_id=user, criteria__title=x
                    ).update(score=values_list[index])
                else:
                    Weightage_Matching.objects.create(
                        jd_id_id=jd_id,
                        user_id=user,
                        criteria_id=index + 1,
                        score=values_list[index],
                    )

            return Response({"message": "JD skill Matching updated successfully"})

        except Exception as e:
            return Response({"success": False, "error": str(e)})


class weightage_score(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        jd_id = request.GET.get("jd_id", None)
        can_id = request.GET.get("can_id", None)
        user = self.request.user
        users = user.id
        if jd_id and can_id:
            data = weightage_mathching(jd_id, can_id, users)
        if jd_id:
            can_ids = applicants_status.objects.filter(jd_id=jd_id).values_list(
                "candidate_id", flat=True
            )

            success = True
            for i in can_ids:
                data = weightage_mathching(jd_id, i, users)
                if data == None:
                    return Response({"success": False})
            return Response({"success": success})

        return Response({"success": data})


class subs_details_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            request = self.request
            user_id = request.user
            try:
                admin, updated_by = admin_account(request)
            except:
                if User_Info.objects.filter(username=user_id).exists():
                    admin = User_Info.objects.get(username=user_id).employer_id
                    admin = User.objects.get(id=admin)
            from django.db.models.functions import Length

            total_plan = tmeta_plan.objects.filter(is_active=True).values()
            total_plan = total_plan.annotate(
                days_length=Length(F("subscription_value_days")),
                is_month=Case(
                    When(days_length__exact=2, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
                jd_count=Subquery(
                    plan_features.objects.filter(
                        plan_id=OuterRef("plan_id"), feature_id=10
                    ).values("feature_value")[:1]
                ),
                resume_count=Subquery(
                    plan_features.objects.filter(
                        plan_id=OuterRef("plan_id"), feature_id=27
                    ).values("feature_value")[:1]
                ),
                ai_matched_count=Subquery(
                    plan_features.objects.filter(
                        plan_id=OuterRef("plan_id"), feature_id=6
                    ).values("feature_value")[:1]
                ),
            )
            current_plan = subscriptions.objects.filter(client_id=admin).last()
            if client_features_balance.objects.filter(
                client_id=admin, feature_id=10
            ).exists():
                current_jd_count = client_features_balance.objects.get(
                    client_id=admin, feature_id=10
                ).available_count
            else:
                current_jd_count = 0
            if client_features_balance.objects.filter(
                client_id=admin, feature_id=27
            ).exists():
                current_resume_count = client_features_balance.objects.get(
                    client_id=admin, feature_id=27
                ).available_count
            else:
                current_resume_count = 0
            from django.utils import timezone

            timezone = timezone.now()
            formatted_string = timezone.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            plan_expire = (
                subscriptions.objects.filter(
                    client_id=admin, subscription_end_ts__gte=formatted_string
                )
                .order_by("-subscription_id")[:1]
                .values("subscription_id", "subscription_end_ts")
            )
            try:
                plan_id = current_plan.plan_id.pk
            except:
                plan_id = 1
            add_on_plans = (
                addons_plan_features.objects.filter(plan_id=plan_id)
                .annotate(
                    usage=Coalesce(
                        "value", Value("unlimited"), output_field=CharField()
                    )
                )
                .values(
                    "addon_id__id",
                    "addon_id__name",
                    "addon_id__currency",
                    "usage",
                    "price",
                    "carry_forward",
                    "plan_id",
                    "stripe_id",
                    "addon_id__display_name",
                )
            )
            add_on_plans = add_on_plans.annotate(
                name=Case(
                    When(addon_id__id=1, then=Value("Job")),
                    When(addon_id__id=2, then=Value("Resume")),
                    When(addon_id__id=3, then=Value("Comparative")),
                    When(addon_id__id=4, then=Value("Unlock")),
                    When(addon_id__id=6, then=Value("Interviews")),
                    When(addon_id__id=7, then=Value("AI-interview Question")),
                    When(addon_id__id=9, then=Value("Priority")),
                    When(addon_id__id=10, then=Value("Resume to Multiple Jobs")),
                    When(addon_id__id=11, then=Value("Descriptive AI matching")),
                    default=Value(
                        None
                    ),  # Default value if none of the conditions match
                    output_field=CharField(),
                )
            )
            user_permission = plan_features.objects.filter(plan_id=plan_id).values_list(
                "feature_id__feature_name", flat=True
            )
            add_features = (
                client_features_balance.objects.filter(client_id=admin)
                .values_list("feature_id__feature_name", flat=True)
                .exclude(feature_id__in=[10, 11, 12, 27])
            )
            user_permission = list(chain(user_permission, add_features))
            plan_diff = plan_id
            plan_diff1 = plan_id + 1
            if plan_diff == 1:
                plan_diff1 = 6
            try:
                features, plan = plan_checking(admin, "resume")
            except:
                features = 0
            differences = subscription_content.objects.filter(plan_id=1).values_list(
                "is_difference", flat=True
            )
            active_count = client_features_balance.objects.get(
                client_id=admin, feature_id=27
            ).available_count
            total_resume = employer_pool.objects.filter(client_id=admin).values_list(
                "id", flat=True
            )
            active_resume = employer_pool.objects.filter(client_id=admin).values_list(
                "id", flat=True
            )[: int(features)]
            disable_resume = len(
                applicants_list.objects.filter(user_id=user_id, is_active=True)
                .exclude(jd_id=None)
                .values_list("candidate_id", flat=True)
                .distinct()
            )
            Last_plan = [8, 12]
            user_credit = user_credits(admin)
            expire_content = expire_details(admin)
            standard = [7, 11]
            priority = client_features_balance.objects.filter(
                client_id=admin, feature_id=61
            ).exists()
            client_url = settings.CLIENT_URL
            unlimited = unlimited_addons(admin)
            integration = {
                "google": google_return_details.objects.filter(
                    client_id=user_id
                ).exists(),
                "outlook": outlook_return_details.objects.filter(
                    client_id=user_id
                ).exists(),
            }
            if pagination.objects.filter(user_id=user_id, page_id_id=1).exists():
                job_post = pagination.objects.get(user_id=user_id, page_id_id=1).pages
            else:
                job_post = tmete_pages.objects.get(id=1).default_value

            if pagination.objects.filter(user_id=user_id, page_id_id=2).exists():
                zita_match = pagination.objects.get(user_id=user_id, page_id_id=2).pages
            else:
                zita_match = tmete_pages.objects.get(id=2).default_value

            if pagination.objects.filter(user_id=user_id, page_id_id=3).exists():
                import_candidates = pagination.objects.get(
                    user_id=user_id, page_id_id=3
                ).pages
            else:
                import_candidates = tmete_pages.objects.get(id=3).default_value

            if pagination.objects.filter(user_id=user_id, page_id_id=4).exists():
                import_applicants = pagination.objects.get(
                    user_id=user_id, page_id_id=4
                ).pages
            else:
                import_applicants = tmete_pages.objects.get(id=4).default_value

            if pagination.objects.filter(user_id=user_id, page_id_id=5).exists():
                database = pagination.objects.get(user_id=user_id, page_id_id=5).pages
            else:
                database = tmete_pages.objects.get(id=5).default_value

            if pagination.objects.filter(user_id=user_id, page_id_id=6).exists():
                talent_sourcing = pagination.objects.get(
                    user_id=user_id, page_id_id=6
                ).pages
            else:
                talent_sourcing = tmete_pages.objects.get(id=6).default_value

            if pagination.objects.filter(user_id=user_id, page_id_id=7).exists():
                careers_page = pagination.objects.get(
                    user_id=user_id, page_id_id=7
                ).pages
            else:
                careers_page = tmete_pages.objects.get(id=7).default_value
            context = {
                "success": True,
                "current_plan": plan_id,
                "plan_name": current_plan.plan_id.plan_name,
                "start_date": current_plan.subscription_start_ts,
                "end_date": current_plan.subscription_end_ts,
                "current_jd_count": current_jd_count,
                "current_resume_count": current_resume_count,
                "total_plan": total_plan,
                "plan_expire": plan_expire,
                "add_on_plans": add_on_plans,
                "user_permission": user_permission,
                "add_features": add_features,
                "differences": differences,
                "active_count": active_count,
                "total_resume": total_resume,
                "active_resume": active_resume,
                "disable_count": disable_resume,
                "Last_plan": Last_plan,
                "user_credits": user_credit,
                "expire_details": expire_content,
                "standard": standard,
                "priority": priority,
                "client_url": client_url,
                "unlimited_addons": unlimited,
                "integration": integration,
                "job_post": job_post,
                "zita_match": zita_match,
                "import_candidates": import_candidates,
                "import_applicants": import_applicants,
                "database": database,
                "talent_sourcing": talent_sourcing,
                "careers_page": careers_page,
            }
            return Response(context)
        except Exception as e:
            return Response({"success": False})


from django.db.models.functions import Length


def format_array(plans):
    formatted_data = []
    # Define categories and corresponding titles
    categories = [
        "No. of Jobs",
        "JD Templates Library",
        "Create JD Templates Database",
        "AI JD Parsing",
    ]
    titles = ["Job", "Product 2"]  # Add more titles as needed

    for plan_type in plans:

        product = {"title": plan_type, "pricing": []}
        for category in categories:

            for plan in plans:
                pricing_info = {
                    "title": category,
                    plan_type["plan_name"].lower(): (
                        "Yes" if plan.get(category.lower(), False) else "No"
                    ),
                }
                product["pricing"].append(pricing_info)
        formatted_data.append(product)

    return formatted_data


class plan_details(generics.GenericAPIView):
    def get(self, request):
        # .exclude(plan_id__in=[6,9,10,13])
        plans = tmeta_plan.objects.filter(is_active=True).values()
        plans = plans.annotate(
            job_credits=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=10
                ).values("feature_value")[:1]
            ),
            resume_credits=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=27
                ).values("feature_value")[:1]
            ),
            career_page=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=1)
            ),
            weightage=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=22)
            ),
            comparative=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=28)
            ),
            interview=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=37)
            ),
            interview_question=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=39)
            ),
            pipeline=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=31)
            ),
            external_job_posting=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=13)
            ),
            application_customization=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=28)
            ),
            basic_match=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=54)
            ),
            ai_match=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=28)
            ),
            ai_descriptive_analysis=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=26)
            ),
            priority_support=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=47)
            ),
            candidate_message_platform=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=36)
            ),
            online_doc=Exists(
                plan_features.objects.filter(plan_id=OuterRef("plan_id"), feature_id=46)
            ),
        )
        # plans = format_array(plans)
        context = {"data": plans}
        return Response(context)


from bulk_upload.api import email_automation


class job_changes_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Bulk Import Candidates Has Only changed
        try:
            can_id = self.request.GET.get("can_id", None)
            if can_id:
                can_id = json.loads(can_id)
            jd_id = self.request.GET.get("jd_id", None)
            change_jd = self.request.GET.get("change_jd", None)
            user_id, updated_by = admin_account(request)
            sub_user = request.user
            from django.utils import timezone

            # can_id = employer_pool.objects.filter(client_id = user_id,jd_id=25).values_list('id',flat=True)[0:5]
            for i in can_id:
                can_id = i
                # <---- APPLICANT MOVE TO THE ANOTHER JOB ----->
                if can_id and jd_id and change_jd:
                    new_jd = JD_form.objects.get(id=change_jd)
                    if applicants_screening_status.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, stage_id__isnull=True
                    ).exists():  # 3
                        applicants_screening_status.objects.filter(
                            candidate_id=can_id, jd_id=jd_id
                        ).update(
                            jd_id=new_jd,
                            created_on=timezone.now(),
                            updated_by=updated_by,
                        )
                        if employer_pool.objects.filter(
                            id=can_id, jd_id=jd_id
                        ).exists():  # 1
                            employer_pool.objects.filter(id=can_id, jd_id=jd_id).update(
                                jd_id=new_jd
                            )
                        if applicants_status.objects.filter(
                            candidate_id=can_id, jd_id=jd_id, stage_id__isnull=True
                        ).exists():  # 2
                            applicants_status.objects.filter(
                                candidate_id=can_id, jd_id=jd_id
                            ).update(
                                jd_id=new_jd,
                                created_on=timezone.now(),
                                updated_by=updated_by,
                            )
                        if candidate_resume.objects.filter(
                            client_id=user_id, jd_id=jd_id
                        ).exists():  # 4
                            candidate_resume.objects.filter(
                                client_id=user_id, jd_id=jd_id
                            ).update(
                                jd_id=new_jd,
                                updated_at=timezone.now(),
                                updated_by=updated_by,
                            )
                        if Matched_candidates.objects.filter(
                            candidate_id=can_id, jd_id=jd_id
                        ).exists():  # 5
                            Matched_candidates.objects.filter(
                                candidate_id=can_id, jd_id=jd_id
                            ).delete()
                        if zita_match_candidates.objects.filter(
                            candidate_id=can_id, jd_id=change_jd
                        ).exists():  # 7
                            zita_match_candidates.objects.filter(
                                candidate_id=can_id, jd_id=change_jd
                            ).delete()
                        if Matched_percentage.objects.filter(
                            candidate_id=can_id, jd_id=jd_id
                        ).exists():  # 6
                            Matched_percentage.objects.filter(
                                candidate_id=can_id, jd_id=jd_id
                            ).delete()
                            matched_data = Matching_AI(change_jd, can_id, user_id,sub_user = sub_user)
                            basic_match = basic_matching(
                                can_id, jd_id, user_id, request
                            )
                            if matched_data != None:
                                count = reducematchcount(user_id, "ai_match")

                # <---- CANDIDATE CAN MOVE TO THE JOBS APPLICANT ----->
                if can_id and change_jd and jd_id == None:
                    candidate = employer_pool.objects.get(id=can_id)
                    new_jd = JD_form.objects.get(id=change_jd)
                    if employer_pool.objects.filter(id=can_id).exists():  # 1
                        employer_pool.objects.filter(id=can_id).update(jd_id=new_jd)
                        applicant_convert = Applicant_convertion(
                            can_id, change_jd, self.request.user.id
                        )
                    if not applicants_status.objects.filter(
                        candidate_id=can_id, jd_id=change_jd
                    ).exists():  # 2
                        status_id = tmeta_jd_candidate_status.objects.get(id=1)
                        applicants_status.objects.create(
                            candidate_id=candidate,
                            jd_id=new_jd,
                            created_on=timezone.now(),
                            updated_by=updated_by,
                            status_id=status_id,
                            source="Imported Applicants",
                            client_id=user_id,
                        )
                        email_automation(can_id, jd_id, user_id)

                    if not applicants_screening_status.objects.filter(
                        candidate_id=can_id, jd_id=change_jd
                    ).exists():  # 3
                        applicants_screening_status.objects.create(
                            candidate_id=candidate,
                            jd_id=new_jd,
                            created_on=timezone.now(),
                            updated_by=updated_by,
                        )
                    if not candidate_resume.objects.filter(
                        client_id=user_id, jd_id=change_jd
                    ).exists():  # 4
                        resume_file = candidate_parsed_details.objects.get(
                            candidate_id=can_id
                        ).resume_file_path
                        candidate_resume.objects.create(
                            client_id=user_id,
                            jd_id=new_jd,
                            updated_at=timezone.now(),
                            updated_by=updated_by,
                            file=resume_file,
                        )
                    if zita_match_candidates.objects.filter(
                        candidate_id=can_id, jd_id=change_jd
                    ).exists():  # 7
                        zita_match_candidates.objects.filter(
                            candidate_id=can_id, jd_id=change_jd
                        ).delete()
                    if Matched_candidates.objects.filter(
                        candidate_id=can_id, jd_id=change_jd
                    ).exists():  # 5
                        Matched_candidates.objects.filter(
                            candidate_id=can_id, jd_id=change_jd
                        ).delete()
                    if not Matched_percentage.objects.filter(
                        candidate_id=can_id, jd_id=change_jd
                    ).exists():  # 6
                        matched_data = Matching_AI(change_jd, can_id, user_id,sub_user = sub_user)
                        if matched_data != None:
                            count = reducematchcount(user_id, "ai_match")

                # <---- CANDIDATE OR APPLICANT REMOVE OPTION ----->
                if can_id and jd_id and change_jd == None:
                    if applicants_screening_status.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, stage_id__isnull=True
                    ).exists():  # 3
                        applicants_screening_status.objects.filter(
                            candidate_id=can_id, jd_id=jd_id
                        ).delete()
                    if applicants_status.objects.filter(
                        candidate_id=can_id, jd_id=jd_id, stage_id__isnull=True
                    ).exists():  # 2
                        applicants_status.objects.filter(
                            candidate_id=can_id, jd_id=jd_id
                        ).delete()
                    if Matched_candidates.objects.filter(
                        candidate_id=can_id, jd_id=jd_id
                    ).exists():  # 5
                        Matched_candidates.objects.filter(
                            candidate_id=can_id, jd_id=jd_id
                        ).delete()
                    if Matched_percentage.objects.filter(
                        candidate_id=can_id, jd_id=jd_id
                    ).exists():  # 6
                        Matched_percentage.objects.filter(
                            candidate_id=can_id, jd_id=jd_id
                        ).delete()
                    length = applicants_status.objects.filter(jd_id=jd_id)
                    if length == 0:
                        if pipeline_view.objects.filter(jd_id=jd_id).exists():
                            pipeline_view.objects.filter(jd_id=jd_id).delete()

            return Response(
                {"success": True, "message": "Candidated moved Successfully"}
            )
        except Exception as e:
            return Response({"success": False, "message": str(e)})


class pipeline_status_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        admin_id, updated_by = admin_account(request)
        request = self.request
        can_id = request.GET.get("can_id", None)
        jd_id = request.GET.get("jd_id", None)
        pipeline_id = request.GET.get("pipeline_id", None)

        if can_id and jd_id and pipeline_id:
            data = pipeline_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id, pipeline_id=pipeline_id
            ).values()
            data = data.annotate(
                stage_name=Subquery(
                    tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                        "stage"
                    )
                )
            )
            last_stage = None
            final_stage = stages_customization.objects.filter(
                user_id=admin_id, is_compelted=True
            ).values()
            final_stage = final_stage.annotate(
                stage_name=Subquery(
                    tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                        "stage"
                    )
                )
            )
            if stages_customization.objects.filter(
                user_id=admin_id, is_compelted=True
            ).exists():
                last_stage = stages_customization.objects.get(
                    user_id=admin_id, is_compelted=True
                )
            is_move = pipeline_status.objects.filter(
                jd_id=jd_id,
                candidate_id=can_id,
                pipeline=pipeline_id,
                stage_id=last_stage.stage,
                is_active=True,
            ).exists()
            if stages_customization.objects.filter(user_id=admin_id).exists():
                stages = (
                    stages_customization.objects.filter(user_id=admin_id)
                    .exclude(stage_id__description=None)
                    .values()
                )
                stages = stages.annotate(
                    stage_name=Subquery(
                        tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                            "stage"
                        )
                    ),
                    stage_description=Subquery(
                        tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                            "description"
                        )
                    ),
                    stage_userbased=Subquery(
                        tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                            "user_based"
                        )
                    ),
                    stage_used=Exists(
                        pipeline_status.objects.filter(
                            user_id=admin_id, status_on=OuterRef("stage_id")
                        )
                    ),
                )
                final_stage = stages_customization.objects.filter(
                    user_id=admin_id, stage_id__description__isnull=True
                ).values()
                final_stage = final_stage.annotate(
                    stage_name=Subquery(
                        tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                            "stage"
                        )
                    ),
                    stage_description=Subquery(
                        tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                            "description"
                        )
                    ),
                    stage_userbased=Subquery(
                        tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                            "user_based"
                        )
                    ),
                    stage_used=Exists(
                        pipeline_status.objects.filter(
                            user_id=admin_id, status_on=OuterRef("stage_id")
                        )
                    ),
                )
                stages = list(chain(stages, final_stage[::-1]))
            current_stage = None
            if pipeline_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id, pipeline_id=pipeline_id
            ).exists():
                current_stage = (
                    pipeline_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id, pipeline_id=pipeline_id
                    )
                    .last()
                    .stage.id
                )
            return Response(
                {
                    "success": True,
                    "data": data[::-1],
                    "is_move": is_move,
                    "stages": stages,
                    "final_stage": final_stage,
                    "current_stage": current_stage,
                }
            )

        if stages_customization.objects.filter(user_id=admin_id).exists():
            stages = (
                stages_customization.objects.filter(user_id=admin_id)
                .exclude(stage_id__description=None)
                .values()
            )
            stages = stages.annotate(
                stage_name=Subquery(
                    tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                        "stage"
                    )
                ),
                stage_description=Subquery(
                    tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                        "description"
                    )
                ),
                stage_userbased=Subquery(
                    tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                        "user_based"
                    )
                ),
                stage_used=Exists(
                    pipeline_status.objects.filter(
                        user_id=admin_id, status_on=OuterRef("stage_id")
                    )
                ),
            )
            final_stage = stages_customization.objects.filter(
                user_id=admin_id, stage_id__description__isnull=True
            ).values()
            final_stage = final_stage.annotate(
                stage_name=Subquery(
                    tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                        "stage"
                    )
                ),
                stage_description=Subquery(
                    tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                        "description"
                    )
                ),
                stage_userbased=Subquery(
                    tmeta_stages.objects.filter(id=OuterRef("stage_id"))[:1].values(
                        "user_based"
                    )
                ),
                stage_used=Exists(
                    pipeline_status.objects.filter(
                        user_id=admin_id, status_on=OuterRef("stage_id")
                    )
                ),
            )
            stages = list(chain(stages, final_stage[::-1]))
            return Response({"success": True, "stages": stages})
        return Response({"success": False})

    def post(self, request):
        admin_id, updated_by = admin_account(request)
        request = self.request
        can_id = self.request.POST.get("can_id", None)
        jd_id = request.POST.get("jd_id", None)
        pipeline_id = request.POST.get("pipeline_id", None)
        update = request.POST.get("update", None)
        customization = request.POST.get("customization", None)
        from django.utils import timezone

        if can_id and jd_id and pipeline_id and not customization:
            jd = JD_form.objects.get(id=jd_id)
            candidate = employer_pool.objects.get(id=can_id)
            pipeline = pipeline_view.objects.get(id=pipeline_id)
            update_stage = tmeta_stages.objects.get(id=update)
            if update:  # Update the Status
                value = pipeline_status.objects.filter(
                    jd_id=jd_id, candidate_id=can_id, pipeline_id=pipeline_id
                ).last()
                if int(value.stage.id):
                    val = pipeline_status.objects.filter(
                        jd_id=jd_id, candidate_id=can_id, pipeline_id=pipeline_id
                    ).last()
                    val.status_on = None
                    val.save()
                    moving_last = stages_customization.objects.get(
                        user_id=jd.user_id, is_compelted=True
                    ).stage.id
                    moving_last_stage = False
                    if int(moving_last) == int(update):
                        pipeline_status.objects.filter(
                            jd_id=jd_id, candidate_id=can_id, pipeline_id=pipeline_id
                        ).update(is_active=False)
                        moving_last_stage = True
                    pipeline_create = pipeline_status.objects.get_or_create(
                        jd_id=jd,
                        candidate_id=candidate,
                        pipeline_id=pipeline.id,
                        stage=update_stage,
                        user_id=admin_id,
                        is_active=moving_last_stage,
                        created_at=timezone.now(),
                        status_on=update,
                    )
                    return Response(
                        {"success": True, "message": "Stages Updates Successfully"}
                    )

        if customization:  # Update  User Customization
            stages = request.POST.get("stage_name", None)
            jd = JD_form.objects.get(id=jd_id)
            candidate = employer_pool.objects.get(id=can_id)
            pipeline = pipeline_view.objects.get(id=pipeline_id)
            if stages:
                new_stage = tmeta_stages.objects.create(stage=stages, user_based=True)
                stages_customization.objects.create(user_id=admin_id, stage=new_stage)
            value = pipeline_status.objects.filter(
                jd_id=jd_id, candidate_id=can_id, pipeline_id=pipeline_id
            ).last()
            if int(value.stage.id) != 4 and int(value.stage.id) != 1:
                moving_last_stage = False
                if stages_customization.objects.filter(
                    user_id=admin_id, stage=new_stage
                ).exists():
                    update_stage = stages_customization.objects.get(
                        user_id=admin_id, stage=new_stage
                    ).stage
                    pipeline_status.objects.get_or_create(
                        jd_id=jd,
                        candidate_id=candidate,
                        pipeline_id=pipeline.id,
                        stage=update_stage,
                        user_id=admin_id,
                        is_active=moving_last_stage,
                        created_at=timezone.now(),
                        status_on=update_stage.id,
                    )
            return Response(
                {"success": True, "message": "Customization Updated Successfully"}
            )
        return Response({"success": True})

    def delete(self, request):
        admin_id, updated_by = admin_account(request)
        DeleteStageId = self.request.GET.get("pk", None)
        val = stages_customization.objects.filter(
            user_id=admin_id, stage__id=DeleteStageId
        ).delete()
        vals = tmeta_stages.objects.filter(id=DeleteStageId).delete()
        return Response({"success": True})


from jobs import parsing


class profile_summary_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        can_id = request.GET.get("can_id")
        employer_pool.objects.get(id=can_id)
        sub_user = request.user
        try:
            file_content = None
            if candidate_parsed_details.objects.filter(candidate_id=can_id).exists():
                file_content = candidate_parsed_details.objects.get(
                    candidate_id=can_id
                ).resume_description
            profile_detail_exists = candidate_profile_detail.objects.filter(
                candidate_id=can_id
            ).exists()
            if profile_detail_exists:
                profile_details = candidate_profile_detail.objects.get(
                    candidate_id=can_id
                )
                status = True
            else:
                candidate_profile = profile_summary(file_content,can_id=can_id,sub_user=sub_user)
                if isinstance(candidate_profile,str):
                    candidate_profile = json.loads(candidate_profile)
                print("candidate_profile@------->",candidate_profile)
                if not candidate_profile_detail.objects.filter(
                    candidate_id=can_id
                ).exists():
                    profile_details = candidate_profile_detail.objects.create(
                        candidate_id=employer_pool.objects.get(id=can_id),
                        profile_summary=candidate_profile,
                    )
                    profile_details = candidate_profile_detail.objects.get(
                        candidate_id=can_id
                    )
                else:
                    profile_details = candidate_profile_detail.objects.get(
                        candidate_id=can_id
                    )
                    status = True
                status = False
            data = json.loads(profile_details.profile_summary)
            if isinstance(data,str):
                data  = json.loads(data)
            professional_profile_analysis = data.get(
                "Professional Profile Analysis", {}
            )
            if professional_profile_analysis == {}:
                professional_profile_analysis = data
            return_messgae = "No information available for this section"
            overall_output = {
                "success": True,
                "can_id": can_id,
                "status": status,
                "Career_Trajectory": professional_profile_analysis.get(
                    "Career Trajectory", return_messgae
                ),
                "Achievements": professional_profile_analysis.get(
                    "Achievements", return_messgae
                ),
                "Expertise_and_Skills": professional_profile_analysis.get(
                    "Expertise and Skills", return_messgae
                ),
                "Industry_Engagement": professional_profile_analysis.get(
                    "Industry Engagement", return_messgae
                ),
                "education": professional_profile_analysis.get(
                    "Education and Alignment with Career Goals", return_messgae
                ),
                "behaviour": professional_profile_analysis.get(
                    "Behavioral and Social Insights", return_messgae
                ),
                "Networking": professional_profile_analysis.get(
                    "Networking and Professional Development", return_messgae
                ),
                "summary": professional_profile_analysis.get(
                    "Summary and Recommendations", return_messgae
                ),
            }

            return Response(overall_output)
        except Exception as e:
            return Response({"success": False, "error": str(e), "can_id": can_id})


# Example usage
from django.template.loader import render_to_string


class Email_automation(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        user_id = self.request.user.id

        with transaction.atomic():
            retained_ids = (
                tmeta_message_templates.objects.filter(
                    name__in=[
                        "Application acknowledgement email",
                        "Keeping candidates warm email",
                        "Scheduling an interview",
                        "Test Sample Template",
                        "New Applicants",
                        "Shortlisted",
                        "Rejected",
                        "Hired",
                    ],
                    user_id=user_id,
                )
                .values("name")
                .annotate(retained_id=Min("id"))
                .values("retained_id", "name")
            )

            data_retained = {
                record["name"]: record["retained_id"] for record in retained_ids
            }

            for name, retained_id in data_retained.items():
                jd_message_templates.objects.filter(
                    message_id__in=tmeta_message_templates.objects.filter(
                        name=name, user_id=user_id
                    ).values("id")
                ).update(message_id=retained_id)
            tmeta_ids_to_keep = tmeta_message_templates.objects.filter(
                name__in=data_retained.keys(), user_id=user_id
            ).values_list("id", flat=True)
            tmeta_message_templates.objects.filter(id__in=tmeta_ids_to_keep).exclude(
                id__in=jd_message_templates.objects.values_list("message_id", flat=True)
            ).delete()
        user_id = self.request.user.id
        jd_id = self.request.GET.get("jd_id", None)
        tags = tmeta_email_tags.objects.values("name", "tag")
        # tags = {item['name']: item['tag'] for item in tags}
        tags = [{"%s" % item["name"]: "%s" % item["tag"]} for item in tags]
        if not jd_message_templates.objects.filter(user=user_id, jd_id=jd_id).exists():
            newdata = tmeta_message_templates.objects.filter(
                id__in=[1, 2, 3, 4, 5, 6, 7, 8]
            )
            for i in newdata:

                jd = JD_form.objects.get(id=jd_id)
                job_id = jd.job_id
                template_name = i.name  # f"{job_id} {i.name}"
                stage_name = template_name  # .split(' ')[1]

                message_id, updated_by = tmeta_message_templates.objects.get_or_create(
                    user_id=user_id,
                    name=i.name,
                    templates=i.templates,
                    templates_text=i.templates_text,
                    subject=i.subject,
                    is_active=0,
                )
                if jd:
                    if pipeline_view.objects.filter(
                        jd_id=jd_id, stage_name=i.name
                    ).exists():
                        stage_id_id = pipeline_view.objects.get(
                            jd_id=jd_id, stage_name=i.name
                        ).id
                    else:
                        if i.name in [
                            "Application acknowledgement email",
                            "Keeping candidates warm email",
                            "Scheduling an interview",
                            "Test Sample Template",
                        ]:

                            stage_id_id = 1
                        else:
                            stage_id_id = 0
                jd_message_templates.objects.get_or_create(
                    user_id=user_id,
                    name=i.name,
                    templates=i.templates,
                    templates_text=i.templates_text,
                    message=message_id,
                    subject=i.subject,
                    jd_id=jd,
                    stage=stage_id_id,
                    is_active=0,
                    status=1,
                )
                jd_message_templates.objects.filter(
                    user_id=user_id, jd_id=jd, name="New Applicants"
                ).update(stage=0)
        if not tmeta_message_templates.objects.filter(user=user_id).exists():
            newdata = tmeta_message_templates.objects.filter(
                id__in=[1, 2, 3, 4, 5, 6, 7, 8]
            )
            for i in newdata:
                if pipeline_view.objects.filter(
                    jd_id=jd_id, stage_name=i.name
                ).exists():
                    stage_id_id = pipeline_view.objects.get(
                        jd_id=jd_id, stage_name=i.name
                    ).id
                else:
                    if i.name in [
                        "Application acknowledgement email",
                        "Keeping candidates warm email",
                        "Scheduling an interview",
                        "Test Sample Template",
                    ]:

                        stage_id_id = 1
                    else:
                        stage_id_id = 0
                jd_message_templates.objects.get_or_create(
                    user_id=user_id,
                    name=i.name,
                    templates=i.templates,
                    templates_text=i.templates_text,
                    subject=i.subject,
                    jd_id=jd,
                    stage=stage_id_id,
                    is_active=0,
                )
                jd_message_templates.objects.filter(
                    user_id=user_id, jd_id=jd, name="New Applicants"
                ).update(stage=0)
                tmeta_message_templates.objects.get_or_create(
                    user_id=user_id,
                    name=i.name,
                    templates=i.templates,
                    templates_text=i.templates_text,
                    subject=i.subject,
                    is_active=0,
                )
        if jd_message_templates.objects.filter(
            user=user_id, jd_id=jd_id, stage__in=[0, 1], is_active=False
        ).exists():

            filter_data = jd_message_templates.objects.filter(
                user=user_id, jd_id=jd_id, stage__in=[0, 1], is_active=False
            )
            # existing
            # filter_data = tmeta_message_templates.objects.filter(user = user_id,jd_id = jd_id)
            for i in filter_data:
                jobid = i.jd_id.job_id
                template_name = f"{i.name}"
                # stage_id_id = 1
                if i.name == "New Applicants":
                    stage_id_id = 0
                    jd_message_templates.objects.filter(
                        jd_id=i.jd_id, name=i.name, is_active=False, stage=0
                    ).update(stage=stage_id_id)
                if pipeline_view.objects.filter(
                    jd_id=i.jd_id, stage_name=i.name
                ).exists():
                    stage_id_id = pipeline_view.objects.get(
                        jd_id=i.jd_id, stage_name=i.name
                    ).id
                if jd_message_templates.objects.filter(
                    jd_id=i.jd_id, name=i.name, is_active=False
                ).exists():
                    jd_message_templates.objects.filter(
                        jd_id=i.jd_id, name=i.name, is_active=False
                    ).update(name=template_name)
                # elif jd_message_templates.objects.filter(jd_id=i.jd_id,name = template_name).exists():
                #     jd_message_templates.objects.filter(jd_id=i.jd_id,name = template_name).update(stage = stage_id_id)

        data1 = tmeta_message_templates.objects.filter(user_id=user_id).values()
        data2 = jd_message_templates.objects.filter(jd_id=jd_id).values()
        data = list(chain(data1, data2))
        # data = data.annotate(
        #     jd_id_id=Value(None, output_field=IntegerField())  # You can choose the appropriate field type
        # )
        # if jd_id:
        #     jd_values = jd_message_templates.objects.filter(jd_id= jd_id,user_id = user_id).values()
        #     jd_values= jd_values.annotate(
        #         templates = Subquery(tmeta_message_templates.objects.filter(id =OuterRef('message_id'))[:1].values('templates')),
        #         templates_text = Subquery(tmeta_message_templates.objects.filter(id =OuterRef('message_id'))[:1].values('templates_text'))
        #     )
        #     data = list(chain(data,jd_values))
        title1 = tmeta_message_templates.objects.filter(user__isnull=True).values_list(
            "name", flat=True
        )
        title2 = tmeta_message_templates.objects.filter(user=user_id).values_list(
            "name", flat=True
        )
        title = list(set(chain(title1, title2)))
        return Response({"template": data, "title": title, "tags": tags})

    def post(self, request):

        user = request.user
        id = request.data.get("template_id")
        title = request.data.get("title")
        subject = request.data.get("subject", "").strip()
        new_stage_name = request.data.get("stageName", "")
        new_stage_id = request.data.get("stage_id", "")
        description = request.data.get("rich_text")
        text = request.data.get("text")
        user_id, updated_by = admin_account(request)
        jd_id = request.data.get("jd_id")
        isActive = request.data.get("isactive")
        # email_toggle= request.data['email_toggle']
        email_toggle = request.data.get("email_toggle", None)
        toggle = request.data.get("toggle", None)
        jd_id = JD_form.objects.get(id=jd_id)
        format_name = f"{jd_id.job_id} {new_stage_name}"
        if subject and description:
            if jd_message_templates.objects.filter(
                id=id, status=True, user_id=user_id, jd_id=jd_id
            ).exists():
                jd_message_templates.objects.filter(id=id, status=True).update(
                    name=title,
                    templates=description,
                    templates_text=text,
                    subject=subject,
                )

                if toggle == [True]:
                    toggle = 1
                    for i in new_stage_id:
                        pipeline_view.objects.filter(id=i, jd_id=jd_id).update(
                            email_toggle=toggle
                        )
                return Response({"template": "resultssss", "success": True})
            else:
                format_name = format_name.replace(" ", " ")
                jd_template = None
                if tmeta_message_templates.objects.filter(id=id).exists():
                    jd_template = tmeta_message_templates.objects.get(id=id)
                d = json.loads(new_stage_id)
                if toggle == "[true]":
                    toggle = 1

                    for i in d:
                        pipeline_view.objects.filter(id=i, jd_id=jd_id).update(
                            email_toggle=toggle
                        )
                for i in d:
                    if not jd_message_templates.objects.filter(stage=i).exists():
                        if toggle == "[true]":
                            toggle = 1
                        elif toggle == [True]:
                            toggle = 1

                            for i in d:
                                pipeline_view.objects.filter(id=i, jd_id=jd_id).update(
                                    email_toggle=toggle
                                )
                        if id == None:
                            # if tmeta_message_templates.objects.filter(user=user.id).exclude(id=None).exists():
                            tmeta_instance = tmeta_message_templates.objects.create(
                                name=title,
                                templates=description,
                                templates_text=text,
                                subject=subject,
                                user_id=request.user.id,
                                is_active=True,
                            )
                            for y in new_stage_id:
                                if not jd_message_templates.objects.filter(
                                    stage=d[0]
                                ).exists():
                                    jd_message_templates.objects.create(
                                        name=title,
                                        templates=description,
                                        templates_text=text,
                                        subject=subject,
                                        jd_id=jd_id,
                                        user_id=request.user.id,
                                        stage=d[0],
                                        is_active=1,
                                        message_id=tmeta_instance.id,
                                        status=1,
                                    )
                        else:
                            new_stage_id = json.loads(new_stage_id)
                            for y in new_stage_id:
                                if id == None:
                                    tmeta_instance = (
                                        tmeta_message_templates.objects.create(
                                            name=title,
                                            templates=description,
                                            templates_text=text,
                                            subject=subject,
                                            user_id=request.user.id,
                                            is_active=True,
                                        )
                                    )
                                    jd_message_templates.objects.create(
                                        name=title,
                                        templates=description,
                                        templates_text=text,
                                        subject=subject,
                                        jd_id=jd_id,
                                        user_id=request.user.id,
                                        stage=d[0],
                                        is_active=1,
                                        message_id=tmeta_instance.id,
                                        status=1,
                                    )
                                jd_message_templates.objects.create(
                                    name=title,
                                    templates=description,
                                    templates_text=text,
                                    subject=subject,
                                    jd_id=jd_id,
                                    user_id=request.user.id,
                                    stage=d[0],
                                    is_active=1,
                                    message_id=id,
                                    status=1,
                                )

                return Response({"template": "created", "success": True})

        elif email_toggle:
            try:
                stage_id = request.data["stage_id"]
                stages = pipeline_view.objects.get(id__in=json.loads(stage_id))
                if email_toggle == "[true]":
                    email_toggle = 1
                else:

                    email_toggle = 0
                pipeline_view.objects.filter(
                    id__in=json.loads(stage_id), jd_id=jd_id
                ).update(email_toggle=email_toggle)

                # if not template_stage.objects.filter(templates=temp.message).exists():
                #         template_stage.objects.create(
                #             stages=stage_id, user_id=user, templates=temp.
                #         )

                # templates = jd_message_templates.objects.filter(id__in=json.loads(id))
                # for temp in templates:
                # try:
                #     stage = pipeline_view.objects.get(jd_id = temp.jd_id,stage_name = temp.name)
                # except Exception as e:
                #     stage = None
                # if not template_stage.objects.filter(templates=temp.message).exists():
                #     template_stage.objects.create(
                #         stages=stage, user_id=user, templates=temp.message
                #     )
                #     # pipeline_view.objects.filter(id=stage_id, jd_id=jd_id).update(email_toggle=1)

                data = pipeline_view.objects.filter(jd_id=jd_id).values(
                    "id", "email_toggle"
                )

                return Response({"success": True, "template_id": id, "data": data})
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format"}, status=400)
        else:
            jd_id = request.data.get("jd_id")
            can = request.POST["candidate_id"]
            jd = JD_form.objects.get(id=jd_id)
            s_name = request.POST["stages"]
            stage_id = pipeline_view.objects.get(jd_id=jd_id, stage_name=s_name).id
            template_id = None

            u_id = self.request.user.id
            admin_id, updated_by = admin_account(request)
            admin = admin_id.id

            company = UserHasComapny.objects.get(user_id=admin).company

            comp_list = UserHasComapny.objects.filter(company_id=company).values()
            comp_list = comp_list.annotate(
                us_id=Exists(
                    jd_message_templates.objects.filter(
                        stage=stage_id, user_id=OuterRef("user_id")
                    )
                )
            )
            comp_user = (
                comp_list.filter(us_id=True).values_list("user_id", flat=True).first()
            )

            if jd_message_templates.objects.filter(
                stage=stage_id, user_id=u_id
            ).exists():
                template_id = jd_message_templates.objects.get(
                    stage=stage_id, user_id=u_id
                ).id
            elif jd_message_templates.objects.filter(
                stage=stage_id, user_id=admin
            ).exists():
                template_id = jd_message_templates.objects.get(
                    stage=stage_id, user_id=admin
                ).id
            elif comp_user:
                if jd_message_templates.objects.filter(
                    stage=stage_id, user_id=comp_user
                ).exists():
                    template_id = jd_message_templates.objects.get(
                        stage=stage_id, user_id=comp_user
                    ).id

            can = json.loads(can)
            if (
                pipeline_view.objects.filter(id=stage_id, email_toggle=1).exists()
                and template_id
            ):
                if jd_message_templates.objects.filter(id=template_id).exists():
                    template = jd_message_templates.objects.get(
                        id=template_id
                    )  # .message.templates
                elif not jd_message_templates.objects.filter(id=template_id).exists():
                    if tmeta_message_templates.objects.filter(id=template_id).exists():
                        template = None
                    # template = tmeta_message_templates.objects.get(id=template_id.id)
                if template:
                    admin_id, updated_by = admin_account(request)
                    company_detail = company_details.objects.get(
                        recruiter_id=admin_id
                    )  # change-1
                    for can_id in can:
                        candidate_instance = employer_pool.objects.get(id=can_id)
                        score = (
                            Matched_candidates.objects.filter(
                                candidate_id=can_id, jd_id=jd
                            )
                            .values_list("id", flat=True)
                            .first()
                        )
                        if score:
                            match_score = Matched_candidates.objects.get(
                                id=score
                            ).profile_match

                        else:
                            match_score = None

                        if candidate_instance.last_name == None:
                            last_name = " "
                        else:
                            last_name = candidate_instance.last_name
                        if candidate_instance.first_name == None:
                            first_name = ""
                        else:
                            first_name = candidate_instance.first_name

                        user_details = User.objects.get(id=request.user.id)
                        employee_name = (
                            user_details.first_name + " " + user_details.last_name
                        )
                        employee_first_name = user_details.first_name
                        employee_last_name = user_details.last_name
                        employee_email = user_details.email
                        company_detail = company_details.objects.get(
                            recruiter_id=admin_id
                        )

                        if JD_locations.objects.filter(jd_id=jd_id).exists():

                            job_location = JD_locations.objects.get(jd_id=jd_id)
                            job_location = (
                                str(job_location.city)
                                + ", "
                                + str(job_location.state)
                                + ", "
                                + str(job_location.country)
                            )
                        else:
                            job_location = "Remote"
                        if company_detail.city:
                            country_name = str(company_detail.country)
                            city_name = str(company_detail.city)
                            state_name = str(company_detail.state)
                            location = (
                                city_name + ", " + state_name + ", " + country_name
                            )
                        else:
                            location = "Remote"
                        if candidate_instance.location == None:
                            candidate_instance_location = ""
                        else:
                            candidate_instance_location = candidate_instance.location
                        if candidate_instance.email == None:
                            candidate_instance_email = ""
                        else:
                            candidate_instance_email = candidate_instance.email
                        if candidate_instance.last_name == None:
                            last_name = ""
                        if candidate_instance.first_name == None:
                            first_name = ""
                        if company_detail.company_website == None:
                            companywebsite = ""
                        else:
                            companywebsite = company_detail.company_website
                        if company_detail.email == None:
                            companyemail = ""
                        else:
                            companyemail = company_detail.email
                        if employee_name == None:
                            employeeName = ""
                        else:
                            employeeName = employee_name
                        if employee_first_name == None:
                            employeeFirstName = ""
                        else:
                            employeeFirstName = employee_first_name
                        if employee_last_name == None:
                            employeeLastName = ""
                        else:
                            employeeLastName = employee_last_name
                        if employee_email == None:
                            employeeEmail = ""
                        else:
                            employeeEmail = employee_email
                        if company_detail.contact == None:
                            companyContact = ""
                        else:
                            companyContact = convert_phonenumber(company_detail.contact)
                        email_content = (
                            template.templates.replace(
                                "[Applicant_Name]", f"{first_name} {last_name}"
                            )
                            .replace("{{Candidate Name}}", f"{first_name} {last_name}")
                            .replace("{{Applicant Name}}", f"{first_name} {last_name}")
                            .replace("{{Job Title}}", jd.job_title)
                            .replace("[Job_Title]", jd.job_title)
                            .replace("{{Job Location}}", job_location)
                            .replace("{{Company Name}}", company_detail.company_name)
                            .replace("[Company_Name]", company_detail.company_name)
                            .replace("{{Company Location}}", location)
                            .replace(
                                "{{Candidate Location}}", candidate_instance_location
                            )
                            .replace(
                                "{{Applicant Location}}", candidate_instance_location
                            )
                            .replace("{{Candidate Email ID}}", candidate_instance.email)
                            .replace("{{Applicant Email ID}}", candidate_instance.email)
                            .replace("{{Company Website URL}}", companywebsite)
                            .replace("{{Company Email ID}}", companyemail)
                            .replace("{{Employee Name}}", employeeName)
                            .replace("{{Employee Email ID}}", employeeEmail)
                            .replace("{{Employee Contact Number}}", companyContact)
                            .replace("{{Job ID}}", jd.job_id)
                            .replace("{{Candidate Match Score}}", str(match_score))
                            .replace("{{Applicant Match Score}}", str(match_score))
                        )  # email_content = template.templates.replace(
                    #             "[Applicant_Name]", f"{first_name} {last_name}"
                    #         ).replace('{Job Title}', jd.job_title).replace("{Company Name}", company_detail.company_name).replace('{Candidate Location}',candidate_instance.location).replace('{Candidate Email ID}',candidate_instance.email).replace('{Company URL}',company_detail.company_website).replace('{Company Email ID}',company_detail.email).replace('[company_location]', location).replace('{Employee Full Name}',employee_name).replace('{Employee First Name}',employee_first_name).replace('{Employee Last Name}',employee_last_name).replace('{Employee Email ID}',employee_email).replace('{Employee Contact Number}',company_detail.contact)

                    if candidate_instance.last_name == None:
                        last_name = ""
                    if candidate_instance.first_name == None:
                        first_name = ""

                    d = {"email_content": email_content}
                    htmly = get_template("email_templates/email_automation.html")

                    html_content = htmly.render(d)
                    # subject=template.subject.replace("[Applicant_Name]", f"{first_name} {last_name}").replace("{{Job Title}}", jd.job_title).replace("[Job_Title]", jd.job_title).replace("{{Company Name}}", company_detail.company_name).replace("[Company_Name]", company_detail.company_name)
                    subject = (
                        template.subject.replace(
                            "[Applicant_Name]", f"{first_name} {last_name}"
                        )
                        .replace("{{Applicant Name}}", f"{first_name} {last_name}")
                        .replace("{{Job Title}}", jd.job_title)
                        .replace("[Job_Title]", jd.job_title)
                        .replace("{{Company Name}}", company_detail.company_name)
                        .replace("[Company_Name]", company_detail.company_name)
                    )

                    msg = EmailMultiAlternatives(
                        subject,
                        html_content,
                        "support@zita.ai",
                        [candidate_instance.email],
                    )

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
                    automated_notify(jd_id, can, user)

                    return Response(
                        {"message": "Emails are being sent.", "success": True}
                    )
            return Response(
                {
                    "message": "Emails are Not being sent Exception : Email Toggle Cannot Set.",
                    "success": False,
                }
            )


base_dir = settings.BASE_DIR


class tour_data_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user, updated_by = admin_account(request)
        skip_id = self.request.GET.get("skip_id", None)
        feedback_rating = self.request.GET.get("rating", 0)
        feedback_notes = self.request.GET.get("notes", "")
        restart_status = self.request.GET.get("restart_status")
        explore = self.request.GET.get("explore")
        if restart_status:
            restart_status = json.loads(restart_status)
        if explore:
            explore = json.loads(explore)
        last_login = User.objects.get(id=request.user.id).last_login
        # if last_login:
        #     is_first_login = False
        # else:
        #     is_first_login=True
        is_first_login = False if last_login else True
        if not tour_data.objects.filter(user_id=self.request.user).exists():
            tour_data.objects.create(
                user_id=self.request.user,
                skip_id=skip_id,
                is_first_login=is_first_login,
            )
        else:
            if skip_id:
                tour_data.objects.filter(user_id=self.request.user).update(
                    skip_id=skip_id, is_first_login=explore, is_steps=restart_status
                )
            if feedback_rating != 0 or feedback_notes != "":
                tour_feedback.objects.create(
                    user_id=self.request.user,
                    feedback_rating=json.loads(feedback_rating),
                    feedback_notes=feedback_notes,
                )
        tour_user = tour_data.objects.filter(user_id=request.user.id).values()
        return Response(tour_user)


# from zita.settings import coresignal_token
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import JsonResponse
import json
import zipfile
from datetime import datetime
import os

# from django.conf import settings
from zita.settings import coresignal_token


def parse_duration(duration):
    years, months = 0, 0
    try:
        if "year" in duration:
            year_part = duration.split("year")[0].strip()
            if year_part.isdigit():
                years = int(year_part)
            elif "less than a" in year_part:

                years = 0
                months = 6
        if "month" in duration:
            months_section = duration.split("month")[0]
            if months_section.split()[-1].isdigit():
                months = int(months_section.split()[-1])
    except ValueError as e:
        pass
    return 12 * years + months


class Coresignalintegration(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        linkedin_id = request.GET.get("linkedin_id", None)
        pagecount = request.GET.get("pagecount", None)
        job_title = request.GET.get("job_title", None)
        location = request.GET.get("location", None)
        skill = request.GET.get("skill", None)
        education_program_name = request.GET.get("education", None)
        experience_company_employees_count_gte = request.GET.get("experience_gte", 1)
        experience_company_employees_count_lte = request.GET.get("experience_lte", 30)

        if skill == "" or skill == " ":
            skill = None

        if education_program_name and education_program_name != "[]":
            education_program_name = json.loads(education_program_name)

            education_program_name = " OR ".join(
                f"{program}" for program in education_program_name
            )

        if education_program_name == [] or education_program_name == "[]":

            education_program_name = None
        try:
            experience_company_employees_count_gte = int(
                experience_company_employees_count_gte
            )

        except ValueError:
            experience_company_employees_count_gte = 1

        try:
            experience_company_employees_count_lte = int(
                experience_company_employees_count_lte
            )
        except ValueError:
            experience_company_employees_count_lte = 100
        try:
            experience_company_employees_count_gte = int(
                experience_company_employees_count_gte
            )
        except ValueError:
            experience_company_employees_count_gte = (
                1  # Default to 1 if conversion fails
            )

        url = "https://api.coresignal.com/cdapi/v1/linkedin/member/search/filter"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {coresignal_token}",
        }

        if (
            education_program_name
            and skill == None
            and location
            and job_title
            and experience_company_employees_count_gte
            and experience_company_employees_count_lte
        ):

            payload = json.dumps(
                {
                    "location": location,
                    "title": job_title,
                    "education_program_name": education_program_name,
                    # "experience_company_employees_count_gte": experience_company_employees_count_gte,
                    # "experience_company_employees_count_lte": experience_company_employees_count_lte,
                    "active_experience": True,
                }
            )
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            candidate_list = response
            data = response[0:15]
            pagecount = len(data)
        elif (
            skill
            and education_program_name == None
            and job_title
            and location
            and experience_company_employees_count_gte
            and experience_company_employees_count_lte
        ):
            # All parameters combined.

            payload = json.dumps(
                {
                    "location": location,
                    "title": job_title,
                    "keyword": skill,
                    "experience_company_employees_count_gte": experience_company_employees_count_gte,
                    "experience_company_employees_count_lte": experience_company_employees_count_lte,
                    "active_experience": True,
                }
            )
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            candidate_list = response
            data = response[0:15]
            pagecount = len(data)
        elif (
            skill != None
            and education_program_name != None
            and job_title
            and location
            and experience_company_employees_count_gte
            and experience_company_employees_count_lte
        ):
            # All parameters combined.

            payload = json.dumps(
                {
                    "location": location,
                    "title": job_title,
                    "keyword": skill,
                    "education_program_name": education_program_name,
                    "experience_company_employees_count_gte": experience_company_employees_count_gte,
                    "experience_company_employees_count_lte": experience_company_employees_count_lte,
                    "active_experience": True,
                }
            )
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            candidate_list = response
            data = response[0:15]
            pagecount = len(data)
        elif (
            skill == None and job_title and location and job_title
        ):  # and experience_company_employees_count_gte and experience_company_employees_count_lte:
            # All parameters combined.

            payload = json.dumps(
                {
                    "location": location,
                    "title": job_title,
                    "keyword": skill,
                    "active_experience": True,
                }
            )
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            candidate_list = response
            data = response[0:10]
            pagecount = len(data)
        elif (
            job_title
            and location
            and skill == None
            and experience_company_employees_count_gte
            and experience_company_employees_count_lte
        ):
            # All parameters combined.

            payload = json.dumps(
                {
                    "location": location,
                    "title": job_title,
                    "keyword": skill,
                    "education_program_name": education_program_name,
                    "experience_company_employees_count_gte": experience_company_employees_count_gte,
                    "experience_company_employees_count_lte": experience_company_employees_count_lte,
                    "active_experience": True,
                }
            )
            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            candidate_list = response
            data = response[0:15]
            pagecount = len(data)
        else:
            search_results = json.loads(linkedin_id)
            pagecount = len(search_results)
            candidate_list = search_results

        if linkedin_id:
            response = json.loads(linkedin_id)
            pagecount = len(response)

        keys_to_remove = [
            "canonical_hash",
            "outdated",
            "member_volunteering_opportunities_collection",
            "member_websites_collection",
            "last_updated_ux",
            "experience_count",
            "connections_count",
            "deleted",
            "last_updated",
            "created",
            "last_response_code",
            "recommendations_count",
            "member_recommendations_collection",
            "member_also_viewed_collection",
            "member_similar_profiles_collection",
            "member_volunteering_supports_collection",
            "member_volunteering_positions_collection",
            "recommendations_count",
            "logo_url",
            "member_patents_collection" "member_groups_collection",
            "member_interests_collection",
            "member_languages_collection",
            "member_organizations_collection",
            "member_posts_see_more_urls_collection",
            "member_publications_collection",
            "member_test_scores_collection",
            "member_courses_suggestion_collection",
        ]

        candidate_ids = response
        candidates_processed = []
        count = 1
        for candidate_id in candidate_ids[0:15]:
            try:
                count += 1
                existing_candidate = linkedin_data.objects.get(
                    linkedin_id=candidate_id
                ).sourcing_data
                existing_candidate = json.loads(existing_candidate)

                candidate_profile = existing_candidate
                edu = candidate_profile["member_education_collection"]
                quall = coresigna_qualification(edu)[::-1]
                data = ", ".join(quall)
                print("&&&&&&&&&&&&&&&&&&444445458989898989&&&",candidate_profile["id"])
                if  linkedin_data.objects.filter(linkedin_id=candidate_profile["id"],is_active=0).exists():
                        print("^&^*(*(*(((*(*(***)))))))")
                        json_data = json.loads(linkedin_data.objects.get(linkedin_id=candidate_profile["id"] ).sourcing_data )
                        try:
                            print("&^*(((((($$$$$$$$$$$$$$$$$$$$$$$$$$))))))")
                            translated_json, was_translated = translate_selected_fields(json_data)
                            print("$$$$$$$$$$$$$$$$$$$$$$$",translated_json,was_translated)
                            linkedin_data.objects.filter(linkedin_id=candidate_profile["id"]).update(sourcing_data=json.dumps(translated_json), is_active=1 if was_translated else 0 )
                        except Exception as e:  
                            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",e)
                candidate_profile["Qualification"] = data

                if "member_experience_collection" in candidate_profile:
                    seen_titles_companies = set()
                    filtered_unique_experiences = []
                    total_experience_months = 0

                    for experience in candidate_profile["member_experience_collection"]:
                        dedup_key = (
                            experience.get("title", ""),
                            experience.get("company_name", ""),
                        )
                        if dedup_key not in seen_titles_companies:
                            seen_titles_companies.add(dedup_key)
                            filtered_experience = {
                                key: experience[key]
                                for key in [
                                    "id",
                                    "title",
                                    "company_name",
                                    "duration",
                                    "last_updated",
                                    "member_id",
                                    "date_to",
                                    "date_from",
                                ]
                                if key in experience
                            }
                            filtered_unique_experiences.append(filtered_experience)

                            duration = experience.get("duration", "") or ""
                            total_months = parse_duration(duration)

                            total_experience_months += total_months
                            if total_experience_months == 0:
                                candidate_profile["work_experience"] = 0
                            else:
                                if (
                                    total_experience_months > 1
                                    and total_experience_months <= 11
                                ):
                                    candidate_profile["work_experience"] = (
                                        f"{total_experience_months} Months"
                                    )
                                elif total_experience_months > 12:
                                    year = total_experience_months // 12
                                    month = total_experience_months % 12
                                    if month == 0:

                                        candidate_profile["work_experience"] = (
                                            f"{year} Years"
                                        )
                                    else:
                                        candidate_profile["work_experience"] = (
                                            f"{year} Years {month} Months"
                                        )

                    sorted_experiences = sorted(
                        filtered_unique_experiences,
                        key=lambda x: x.get("last_updated", ""),
                        reverse=True,
                    )
                    candidate_profile["member_experience_collection"] = (
                        sorted_experiences
                    )
                    if len(sorted_experiences) > 0:
                        candidate_profile["company_id"] = sorted_experiences[0].get(
                            "id"
                        )
                    else:
                        candidate_profile["company_id"] = []
                    if len(sorted_experiences) > 0:
                        most_recent_id = sorted_experiences[0].get("id")
                        member = sorted_experiences[0].get("member_id")
            except linkedin_data.DoesNotExist:
                count += 1
                if not linkedin_data.objects.filter(linkedin_id=candidate_id).exists():
                    profile_response = requests.get(
                        f"https://api.coresignal.com/cdapi/v1/linkedin/member/collect/{candidate_id}",
                        headers=headers,
                    )
                    linkedin_source_data = profile_response.json()
                    candidate_profile = profile_response.json()
                    if isinstance(candidate_profile, dict):
                        for key in keys_to_remove:
                            candidate_profile.pop(key, None)
                        if "member_education_collection" in candidate_profile:
                            unique_records = []
                            seen = set()
                            for education_record in candidate_profile[
                                "member_education_collection"
                            ]:
                                filtered_record = {
                                    k: v
                                    for k, v in education_record.items()
                                    if k in ["title", "subtitle"]
                                }
                                record_tuple = tuple(sorted(filtered_record.items()))
                                if record_tuple not in seen:
                                    seen.add(record_tuple)
                                    unique_records.append(filtered_record)

                            unique_records = sorted(
                                unique_records,
                                key=lambda x: x.get("subtitle", "") or "",
                                reverse=True,
                            )
                            candidate_profile["member_education_collection"] = (
                                unique_records
                            )
                            edu = candidate_profile["member_education_collection"]
                            quall = coresigna_qualification(edu)[::-1]
                            data = ", ".join(quall)
                            candidate_profile["Qualification"] = data
                        if "member_experience_collection" in candidate_profile:
                            seen_titles_companies = set()
                            filtered_unique_experiences = []
                            total_experience_months = 0

                            for experience in candidate_profile[
                                "member_experience_collection"
                            ]:
                                dedup_key = (
                                    experience.get("title", ""),
                                    experience.get("company_name", ""),
                                )
                                if dedup_key not in seen_titles_companies:
                                    seen_titles_companies.add(dedup_key)
                                    filtered_experience = {
                                        key: experience[key]
                                        for key in [
                                            "id",
                                            "title",
                                            "company_name",
                                            "duration",
                                            "last_updated",
                                            "member_id",
                                            "date_to",
                                            "date_from",
                                        ]
                                        if key in experience
                                    }
                                    filtered_unique_experiences.append(
                                        filtered_experience
                                    )

                                    duration = experience.get("duration", "") or ""
                                    total_months = parse_duration(duration)

                                    total_experience_months += total_months
                                    if total_experience_months == 0:
                                        candidate_profile["work_experience"] = 0
                                    else:
                                        if (
                                            total_experience_months > 1
                                            and total_experience_months <= 11
                                        ):
                                            candidate_profile["work_experience"] = (
                                                f"{total_experience_months} Months"
                                            )
                                        elif total_experience_months > 12:
                                            year = total_experience_months // 12
                                            month = total_experience_months % 12
                                            if month == 0:
                                                candidate_profile["work_experience"] = (
                                                    f"{year} Years"
                                                )
                                            else:
                                                candidate_profile["work_experience"] = (
                                                    f"{year} Years {month} Months"
                                                )

                            sorted_experiences = sorted(
                                filtered_unique_experiences,
                                key=lambda x: x.get("last_updated", ""),
                                reverse=True,
                            )
                            candidate_profile["member_experience_collection"] = (
                                sorted_experiences
                            )
                            if len(sorted_experiences) > 0:
                                candidate_profile["company_id"] = sorted_experiences[
                                    0
                                ].get("id")
                            else:
                                candidate_profile["company_id"] = []
                            if len(sorted_experiences) > 0:
                                most_recent_id = sorted_experiences[0].get("id")
                                member = sorted_experiences[0].get("member_id")

                        if "member_certifications_collection" in candidate_profile:
                            unique_certifications = []
                            seen_names = set()
                            for certification_record in candidate_profile[
                                "member_certifications_collection"
                            ]:
                                filtered_record = {
                                    k: certification_record[k]
                                    for k in ["name"]
                                    if k in certification_record
                                }
                                certification_name = filtered_record.get("name")
                                if certification_name not in seen_names:
                                    seen_names.add(certification_name)
                                    unique_certifications.append(filtered_record)
                            candidate_profile["member_certifications_collection"] = (
                                unique_certifications
                            )

                        if "member_projects_collection" in candidate_profile:
                            unique_records = []
                            seen = set()
                            for project_record in candidate_profile[
                                "member_projects_collection"
                            ]:
                                filtered_record = {
                                    k: v
                                    for k, v in project_record.items()
                                    if k in ["name", "description"]
                                }
                                record_tuple = tuple(sorted(filtered_record.items()))
                                if record_tuple not in seen:
                                    seen.add(record_tuple)
                                    unique_records.append(filtered_record)

                            unique_records = sorted(
                                unique_records,
                                key=lambda x: x.get("description", "") or "",
                            )
                            candidate_profile["member_projects_collection"] = (
                                unique_records
                            )
                        if "member_awards_collection" in candidate_profile:
                            for education_record in candidate_profile[
                                "member_awards_collection"
                            ]:
                                keys_to_keep = ["title", "issuer", "description"]
                                keys_in_record = list(education_record.keys())
                                for key in keys_in_record:
                                    if key not in keys_to_keep:
                                        education_record.pop(key)
                        if "member_skills_collection" in candidate_profile:
                            updated_skills_collection = []
                            for skill_record in candidate_profile[
                                "member_skills_collection"
                            ]:
                                if (
                                    "member_skill_list" in skill_record
                                    and "skill" in skill_record["member_skill_list"]
                                ):
                                    updated_skills_collection.append(
                                        skill_record["member_skill_list"]["skill"]
                                    )

                            candidate_profile["member_skills_collection"] = (
                                updated_skills_collection
                            )
                        if "member_volunteering_cares_collection" in candidate_profile:
                            updated_skills_collection = []
                            for skill_record in candidate_profile[
                                "member_volunteering_cares_collection"
                            ]:
                                if (
                                    "member_volunteering_care_list" in skill_record
                                    and "care"
                                    in skill_record["member_volunteering_care_list"]
                                ):
                                    updated_skills_collection.append(
                                        skill_record["member_volunteering_care_list"][
                                            "care"
                                        ]
                                    )

                            candidate_profile["member_volunteering_cares_collection"] = updated_skills_collection
                    linkedin_data.objects.create(
                        linkedin_id=candidate_profile["id"],
                        sourcing_data=json.dumps(candidate_profile),
                        linkedin_source_data=json.dumps(linkedin_source_data),
                    )
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&**",candidate_profile["id"])
                    if  linkedin_data.objects.filter(linkedin_id=candidate_profile["id"],is_active=0).exists():
                        print("^&^*(*(*(((*(*(***)))))))")
                        json_data = json.loads(linkedin_data.objects.get(linkedin_id=candidate_profile["id"] ).sourcing_data )
                        try:
                            print("&^*(((((($$$$$$$$$$$$$$$$$$$$$$$$$$))))))")
                            translated_json, was_translated = translate_selected_fields(json_data)
                            print("$$$$$$$$$$$$$$$$$$$$$$$",translated_json,was_translated)
                            linkedin_data.objects.filter(linkedin_id=candidate_profile["id"]).update(sourcing_data=json.dumps(translated_json), is_active=1 if was_translated else 0 )
                        except Exception as e:  
                            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",e)
                           
            except Exception as e:
                pass
            candidates_processed.append(candidate_profile)

        return Response(
            {"candidate_ids": candidate_list, "candidates": candidates_processed}
        )


    def post(self, request):
        request = self.request
        sub_user  = self.request.user
        user_id, updated_by = admin_account(request)
        unlock = request.POST["unlock"]
        candidates = json.loads(request.POST["linkedin_id"])

        if unlock == "True":
            unlock_count = 0
            for i in candidates:
                linkedin_unlock(user_id)
                if not unlocked_candidate.objects.filter(
                    user_id=user_id, unlocked_candidate__linkedin_id=i
                ).exists():
                    id = linkedin_data.objects.get(linkedin_id=i)
                    update_data = unlocked_candidate.objects.create(
                        user_id=user_id, unlocked_candidate=id
                    )
                if linkedin_data.objects.filter(linkedin_id=i).exists():
                    data = linkedin_data.objects.get(linkedin_id=i).sourcing_data
                    candidate_profile = json.loads(data)
                    try:
                        if candidate_profile["Qualification"]:
                            data = candidate_profile["Qualification"]
                            if "Doctorate" in data:
                                data = "Doctorate"
                            elif "Master" in data:
                                data = "Master"
                            elif "Bachelors" in data:
                                data = "Bachelors"
                            elif "Diplamo" in data:
                                data = "Diplamo"
                            else:
                                data = ""
                    except:
                        pass
                # if not unlocked_candidate.objects.get(unlocked_candidate__linkedin_id=i).email:
                if (
                    not unlocked_candidate.objects.filter(
                        unlocked_candidate__linkedin_id=i, email__isnull=True
                    ).last()
                    == None
                ):

                    url = f"https://enrichment.coresignal.com/v1/contacts?member_id={i}"
                    candidate_profile["email"] = None
                    try:
                        if candidate_profile["company_id"]:
                            company_id = candidate_profile["company_id"]
                            headers = {"x-api-key": settings.coresignal_email_token}
                            json_data = {
                                "query": {
                                    "bool": {
                                        "must": [
                                            {"term": {"id": company_id}},
                                            {"exists": {"field": "company_id"}},
                                        ]
                                    }
                                }
                            }

                            response = requests.get(
                                url, headers=headers, json=json_data
                            )

                            candidate_profile["email"] = None

                            if response.status_code == 200:
                                if "application/json" in response.headers.get(
                                    "Content-Type", ""
                                ):
                                    try:
                                        response_data = response.json()
                                        if response_data and response_data.get("data"):
                                            email = response_data["data"].get("email")
                                            if email:
                                                candidate_profile["email"] = email
                                                unlocked_candidate.objects.filter(
                                                    user_id=user_id,
                                                    unlocked_candidate=id,
                                                ).update(email=email)
                                            else:
                                                candidate_profile["email"] = email

                                    except Exception as e:
                                        pass
                        else:
                            email = unlocked_candidate.objects.get(
                                unlocked_candidate__linkedin_id=i
                            ).email
                    except:
                        candidate_profile["email"] = None
                    emp_id = employer_pool.objects.create(
                        can_source_id=5,
                        client_id=user_id,
                        updated_by=updated_by,
                        candidate_id=None,
                        job_type=None,
                        candi_ref_id=candidate_profile["id"],
                        first_name=candidate_profile.get("name"),
                        last_name=" ",
                        linkedin_url=candidate_profile.get("url"),
                        email=candidate_profile["email"],
                        work_exp=str(candidate_profile["work_experience"]),
                        relocate=None,
                        qualification=candidate_profile.get("Qualification"),
                        exp_salary=None,
                        user_id=sub_user,
                        job_title=candidate_profile["title"],
                        skills=", ".join(candidate_profile["member_skills_collection"]),
                        location=candidate_profile["location"],
                    )

                    # id.candidate_id = emp_id
                    # id.save()
                    if unlocked_candidate.objects.filter(
                        user_id=user_id, unlocked_candidate__linkedin_id=i
                    ).exists():
                        unlocked_candidate.objects.filter(id=update_data.id).update(
                            candidate_id=emp_id
                        )

                    file_content = json.loads(
                        linkedin_data.objects.get(linkedin_id=i).sourcing_data
                    )
                    file_content.pop("member_groups_collection", None)
                    # try:
                    #     if 'member_experience_collection' in file_content:

                    #         file_content['member_experience_collection'].sort(key=lambda x: x['last_updated'], reverse=True)
                    # except:
                    #     pass
                    candidate_profile = profile_summary(file_content,can_id=emp_id,sub_user=sub_user)
                    if not candidate_profile_detail.objects.filter(
                        candidate_id=emp_id
                    ).exists():
                        candidate_profile_detail.objects.create(
                            candidate_id=emp_id, profile_summary=candidate_profile
                        )
                        pdf_name = core_signal_pdf_generate(
                            i, candidate_profile, user_id
                        )

                        parsed_content = Json_convertion_Core(file_content)
                        if not candidate_parsed_details.objects.filter(
                            candidate_id=emp_id
                        ).exists():
                            # TODO need to be store resume_description
                            update_name = pdf_name.split("media", 1)
                            if len(update_name) > 1:
                                new_pdf_name = "media" + update_name[1]
                                new_pdf_name = new_pdf_name.replace("media/", "")
                            candidate_parsed_details.objects.create(
                                candidate_id=emp_id,
                                parsed_text=json.dumps(parsed_content),
                                resume_file_path=new_pdf_name,
                            )
                    jd_list = JD_form.objects.filter(
                        user_id=user_id, jd_status_id=1
                    ).values_list("id", flat=True)
                    for jd_id in jd_list:
                        basic_matching(emp_id.id, jd_id, user_id, request)
                unlock_count = unlock_count + 1
            if unlock_count > 0:
                if unlock_count == 1:
                    UserActivity.objects.create(
                        user=request.user,
                        action_id=4,
                        action_detail=str(unlock_count) + " candidate from LinkedIn Sourcing",
                    )
                else:
                    UserActivity.objects.create(
                        user=request.user,
                        action_id=4,
                        action_detail=str(unlock_count) + " candidates from LinkedIn Sourcing",
                    )
            return Response({"success": True, "status": True})

        if unlock == "False":
            t = datetime.now().strftime("%b_%d_%Y")
            zip_file_name = "candidate_profiles_" + str(t) + ".zip"
            zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_file_name)
            with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for candidate_id in candidates:
                    if linkedin_data.objects.filter(linkedin_id=candidate_id).exists():
                        name = json.loads(
                            linkedin_data.objects.get(
                                linkedin_id=candidate_id
                            ).sourcing_data
                        )
                        if unlocked_candidate.objects.filter(
                            unlocked_candidate__linkedin_id=candidate_id,
                            user_id=user_id,
                        ).exists():
                            if unlocked_candidate.objects.filter(
                                unlocked_candidate__linkedin_id=candidate_id,
                                user_id=user_id,
                                candidate_id__isnull=False,
                            ).exists():
                                emp_id = unlocked_candidate.objects.get(
                                    unlocked_candidate__linkedin_id=candidate_id,
                                    user_id=user_id,
                                ).candidate_id
                            else:
                                emp_id = linkedin_data.objects.get(
                                    linkedin_id=candidate_id
                                ).candidate_id
                            if candidate_parsed_details.objects.filter(
                                candidate_id=emp_id
                            ).exists():
                                pdf_name = candidate_parsed_details.objects.get(
                                    candidate_id=emp_id
                                ).resume_file_path
                                pdf_name = os.path.join(base_dir, str(pdf_name))
                            elif unlocked_candidate.objects.filter(
                                unlocked_candidate__linkedin_id=candidate_id,
                                user_id=user_id,
                                resume_file_path__isnull=False,
                            ).exists():
                                pdf_name = linkedin_data.objects.get(
                                    linkedin_id=candidate_id
                                ).resume_file_path
                            elif emp_id == None:
                                name.pop("member_groups_collection", None)
                                download_content = profile_summary(name,can_id=candidate_id,sub_user=sub_user)
                                pdf_name = core_signal_pdf_generate(
                                    candidate_id, download_content, user_id
                                )
                            # html_string = template.render({'data': data,"name": name['name']})
                        elif not unlocked_candidate.objects.filter(
                            unlocked_candidate=candidate_id, user_id=user_id
                        ).exists():
                            if linkedin_data.objects.filter(
                                linkedin_id=candidate_id, resume_file_path__isnull=False
                            ).exists():
                                pdf_name = linkedin_data.objects.get(
                                    linkedin_id=candidate_id
                                ).resume_file_path
                            elif linkedin_data.objects.filter(
                                linkedin_id=candidate_id, resume_file_path__isnull=True
                            ).exists():
                                # download_content = core_signal(name)
                                name.pop("member_groups_collection", None)
                                # if 'member_experience_collection' in data:
                                #     name['member_experience_collection'].sort(key=lambda x: x['last_updated'])

                                download_content = profile_summary(name,can_id=candidate_id,sub_user=sub_user)
                                pdf_name = core_signal_pdf_generate(
                                    candidate_id, download_content, user_id
                                )
                        destination_path = "souring_resumes/" + os.path.basename(
                            pdf_name
                        )
                        zf.write(pdf_name, arcname=destination_path)

                file_url = request.build_absolute_uri(
                    settings.MEDIA_URL + zip_file_name
                )
                parts = file_url.split("//", 1)
                return Response(
                    {"success": True, "file_path": parts[1], "status": "download"}
                )

from deep_translator import GoogleTranslator
translator = GoogleTranslator(source='auto', target='en')

# Function to check if any non-English characters are present


class linkedin_unlocked_candidate(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user_id = request.user
        current_site = request.build_absolute_uri(settings.MEDIA_URL)
        # admin,updated_by = admin_account(request)
        user, updated_by = admin_account(self.request)
        if request.GET.get("candidates_id", None):
            candidate_id = request.GET["candidates_id"]
            success = False
            filepath = None
            if linkedin_data.objects.filter(linkedin_id=candidate_id).exists():
                if linkedin_data.objects.filter(
                    linkedin_id=candidate_id, 
                ).exists():
                    json_data = json.loads(
                        linkedin_data.objects.get(
                            linkedin_id=candidate_id
                        ).sourcing_data
                    )
                    print("*(*(**()))",len(json_data))
                    # if contains_non_english(json.dumps(json_data)):
                    #     print("111111111")
                    #     json_data = translate_to_english(json_data)
                    json_data.pop("member_groups_collection", None)

                    pdf_name = core_signal_data_generate(candidate_id, user.id)
                
                filepath = linkedin_data.objects.get(
                    linkedin_id=candidate_id
                ).resume_file_path
                if unlocked_candidate.objects.filter(
                    user_id=user.id,
                    unlocked_candidate__linkedin_id=candidate_id,
                    resume_file_path__isnull=False,
                ).exists():
                    filepath = unlocked_candidate.objects.get(
                        user_id=user.id, unlocked_candidate__linkedin_id=candidate_id
                    ).resume_file_path
                filepath = filepath.split("media/", 1)
                if len(filepath) > 1:
                    filepath = current_site + filepath[1]
                    linkedin_ids = unlocked_candidate.objects.filter(
                        user_id=user.id
                   ).values_list("unlocked_candidate__linkedin_id", flat=True)

                return Response(
                    {
                      
                        "success": success,
                        "file_path": filepath,
                        "unlocked": "linkedin_ids",
                    }
                )  # ,"download_content1":download_content1,"download_content2":download_content2})
        if unlocked_candidate.objects.filter(user_id=user_id).exists():
            linkedin_ids = unlocked_candidate.objects.filter(
                user_id=user_id
            ).values_list("unlocked_candidate__linkedin_id", flat=True)
        else:
            linkedin_ids = []
        return Response({"unlocked": linkedin_ids})


class linkedin__candidate(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {coresignal_token}",
        }
        data = linkedin_data.objects.values("linkedin_id")
        linkedin_ids = [item["linkedin_id"] for item in data]

        for i in linkedin_ids:
            if linkedin_data.objects.filter(
                linkedin_id=i, linkedin_source_data=None
            ).exists():
                profile_response = requests.get(
                    f"https://api.coresignal.com/cdapi/v1/linkedin/member/collect/{i}",
                    headers=headers,
                )
                linkedin_source_data = profile_response.json()
                linkedin_data.objects.filter(linkedin_id=i).update(
                    linkedin_source_data=json.dumps(linkedin_source_data)
                )
        return Response({"data": linkedin_ids})


import os


class linkedin_integration(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        with open("jobs/.env", "r") as file:
            for line in file:
                if "STRIPE_PUBLISHABLE_KEY" in line:
                    stripe_publishable_key = line.split("=")[1].strip().strip("'")
                elif "STRIPE_SECRET_KEY" in line:
                    stripe_secret_key = line.split("=")[1].strip().strip("'")

            return Response(
                {
                    "create": True,
                    "account_id": stripe_publishable_key,
                    "stripe_": stripe_secret_key,
                }
            )

    def post(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        username = request.data.get("username")
        password = request.data.get("password")
        account_id = request.data.get("account_id")
        otp = request.data.get("otp")
        if username != None and password != None:
            url = "https://api1.unipile.com:13129/api/v1/accounts"

            payload = {
                "provider": "LINKEDIN",
                "username": username,
                "password": password,
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "X-API-KEY": "JwHqLUn2.MfrMscqMVXV6fHF1NZwWoo47qmn0WS3OcYqeoL5TOWA=",
            }

            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            account_id = result["account_id"]
            if result["object"] == "AccountCreated":
                return Response({"create": True, "account_id": account_id})
            elif result["object"] == "Checkpoint":
                data = result["checkpoint"]["type"]
                if data == "OTP":
                    return Response(
                        {"create": False, "account_id": account_id, "passcode": True}
                    )
                else:
                    return Response(
                        {"create": False, "account_id": account_id, "passcode": False}
                    )
        if otp != None and account_id != None:
            url = "https://api1.unipile.com:13129/api/v1/accounts/checkpoint"

            payload = {"provider": "LINKEDIN", "account_id": account_id, "code": otp}
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "X-API-KEY": "JwHqLUn2.MfrMscqMVXV6fHF1NZwWoo47qmn0WS3OcYqeoL5TOWA=",
            }

            response = requests.post(url, json=payload, headers=headers)
            if response["object"] == "AccountCreated":
                return Response({"created": True, "response": response})
            return Response({"created": False, "response": response})

    def delete(self, request):
        id = request.data.get("id")
        url = f"https://api1.unipile.com:13129/api/v1/accounts/{id}"

        headers = {
            "accept": "application/json",
            "X-API-KEY": "JwHqLUn2.MfrMscqMVXV6fHF1NZwWoo47qmn0WS3OcYqeoL5TOWA=",
        }

        response = requests.delete(url, headers=headers)
        data = response.json()
        data = data["object"]
        return Response({"success": True, "data": data})


class linkedin_message(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request = self.request
        user_id, updated_by = admin_account(request)
        #     account_id="jddG0hY-R8uIdIZYcsKafQ"
        #     provider="abineshnk"
        #     url = f"https://api1.unipile.com:13129/api/v1/users/{provider}?account_id={account_id}"

        #     headers = {
        # "accept": "application/json",
        # "X-API-KEY": "JwHqLUn2.MfrMscqMVXV6fHF1NZwWoo47qmn0WS3OcYqeoL5TOWA="
        #     }

        #     response = requests.get(url, headers=headers)
        url = "https://api1.unipile.com:13129/api/v1/users/invite"

        payload = {
            "provider_id": "ACoAADxhzroBUwMExgy_MeWGTTrxome7LCAvjeg",
            "account_id": "8xhBUJfOTl66W6qdRbsKmQ",
            "message": "hello.....",
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": "JwHqLUn2.MfrMscqMVXV6fHF1NZwWoo47qmn0WS3OcYqeoL5TOWA=",
        }

        response = requests.post(url, json=payload, headers=headers)

        return Response({"data": response.json()})


class JD_Conversion(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        jd_id_id = request.GET.get("jd_id")
        data = FT.jd_conversion(jd_id_id)
        context = {"data": data}
        return Response(context)


class RESUME_Conversion(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        can_id = request.GET.get("candidate_id_id")
        data = FT.resume_conversion(can_id)
        context = {"data": data}
        return Response(context)
from operator import or_
class sourced_candidates_api(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):
        user_id ,updated_by = admin_account(self.request)
        request=   self.request
        job = None
        questionnaire = None
        try:
            career_url = career_page_setting.objects.get(recruiter_id = user_id).career_page_url
        except:
            career_url = None
        if 'jd_id' in request.GET:
            jd_id = request.GET['jd_id']
            questionnaire=applicant_questionnaire.objects.filter(jd_id_id=jd_id).values()
            if jd_id == '':
                jd_id=None
                emp_pool = employer_pool.objects.none()
            elif jd_id == '0' or jd_id == 0:
                jd_id = None
                emp_pool = employer_pool.objects.none()
            else:
                emp_pool=employer_pool.objects.filter(client_id=user_id,can_source_id__in=[2,5],jd_id=jd_id).order_by('-created_at')
            if jd_id: 
                job = JD_form.objects.filter(id=jd_id).values()[0]
            emp_pool=emp_pool.annotate(
                resume_file =Subquery(candidate_parsed_details.objects.filter(candidate_id=OuterRef('id'))[:1].values('resume_file_path')),
                applicant =Subquery(applicants_status.objects.filter(candidate_id=OuterRef('id'),client_id=user_id,status_id_id__in=[1,2,3,4,7], candidate_id__email__isnull=False,candidate_id__first_name__isnull=False,).values('status_id').annotate(cout=Count('candidate_id'))[:1].values('cout'),output_field=CharField()),
                screen_status =Subquery(applicants_status.objects.filter(candidate_id=OuterRef('id'),jd_id_id=jd_id,status_id_id__in=[1,2,3,4,7]).values('status_id__label_name'),output_field=CharField()),
                match =Subquery(Matched_candidates.objects.filter(candidate_id=OuterRef('id'),jd_id_id=jd_id,candidate_id__first_name__isnull=False,candidate_id__email__isnull=False).values('profile_match')),
                current_ctc =Subquery(Personal_Info.objects.filter(application_id=OuterRef('candidate_id')).values('curr_gross')),
                currency =Subquery(Personal_Info.objects.filter(application_id=OuterRef('candidate_id')).values('current_currency')),
                exp_ctc =Subquery(Personal_Info.objects.filter(application_id=OuterRef('candidate_id')).values('exp_gross')),
                zita_match =Subquery(zita_match_candidates.objects.filter(candidate_id=OuterRef('id'),client_id=user_id,candidate_id__email__isnull=False,candidate_id__first_name__isnull=False,).values('status_id').annotate(cout=Count('candidate_id'))[:1].values('cout'),output_field=CharField()),
                adv_match = Exists(Matched_percentage.objects.filter(jd_id= jd_id,candidate_id=OuterRef('id'))),
                block_descriptive = Exists(applicant_descriptive.objects.filter(candidate_id=OuterRef('id'),jd_id= jd_id,is_active=True)),
                ).order_by('-id')

        else:
            emp_pool=employer_pool.objects.filter(client_id=user_id,can_source_id__in=[2,5],jd_id__isnull=True).order_by('-created_at')
            emp_pool=emp_pool.annotate(
                resume_file =Subquery(candidate_parsed_details.objects.filter(candidate_id=OuterRef('id'))[:1].values('resume_file_path')),
                applicant =Subquery(applicants_status.objects.filter(candidate_id=OuterRef('id'),client_id=user_id,status_id_id__in=[1,2,3,4,7], candidate_id__email__isnull=False,candidate_id__first_name__isnull=False,).values('status_id').annotate(cout=Count('candidate_id'))[:1].values('cout'),output_field=CharField()),
                zita_match =Subquery(zita_match_candidates.objects.filter(candidate_id=OuterRef('id'),client_id=user_id,candidate_id__email__isnull=False,candidate_id__first_name__isnull=False,).values('status_id').annotate(cout=Count('candidate_id'))[:1].values('cout'),output_field=CharField()),
                matched_percentage_exists=Exists(Matched_percentage.objects.filter(candidate_id=OuterRef('id'))),
                candidates_ai_matching_exists=Exists(candidates_ai_matching.objects.filter(candidate_id=OuterRef('id'))),
                adv_match=Case(When(Q(matched_percentage_exists=False, candidates_ai_matching_exists=False), then=Value(False)),default=Value(True),output_field=BooleanField()),
            ).order_by('-id')
            
        if 'work_experience' in request.GET and len(request.GET['work_experience'])>0:
            if request.GET['work_experience'] == '0-1 Year':
                emp_pool=emp_pool.filter(
                    Q(work_exp__startswith="0 Years") 
                    | Q(work_exp__startswith="0") 
                    | Q(work_exp="0-1")
                    | Q(work_exp="1 Year")
                    | Q(work_exp="1 Years")
                )
            elif request.GET['work_experience'] == '10+ Years':
                emp_pool=emp_pool.filter( 
                    Q(work_exp="10+")
                    | Q(work_exp__startswith="11 Years")
                    | Q(work_exp__startswith="12 Years")
                    | Q(work_exp__startswith="13 Years")
                    | Q(work_exp__startswith="14 Years")
                    | Q(work_exp__startswith="15 Years")
                    | Q(work_exp__startswith="16 Years")
                    | Q(work_exp__startswith="17 Years")
                    | Q(work_exp__startswith="18 Years")
                    | Q(work_exp__startswith="19 Years")
                    | Q(work_exp__startswith="20 Years")
                    | Q(work_exp__startswith="21 Years")
                    | Q(work_exp__startswith="22 Years")
                    | Q(work_exp__startswith="23 Years")
                    | Q(work_exp__startswith="24 Years")
                    | Q(work_exp__startswith="25 Years")
                    | Q(work_exp__startswith="26 Years")
                    | Q(work_exp__startswith="27 Years")
                    | Q(work_exp__startswith="28 Years")
                    | Q(work_exp__startswith="29 Years")
                    | Q(work_exp__startswith="30 Years")
                )
            elif request.GET['work_experience'] == "10-30":
                emp_pool=emp_pool.filter( 
                    Q(work_exp="10+")
                    | Q(work_exp__startswith="11 Years")
                    | Q(work_exp__startswith="12 Years")
                    | Q(work_exp__startswith="13 Years")
                    | Q(work_exp__startswith="14 Years")
                    | Q(work_exp__startswith="15 Years")
                    | Q(work_exp__startswith="16 Years")
                    | Q(work_exp__startswith="17 Years")
                    | Q(work_exp__startswith="18 Years")
                    | Q(work_exp__startswith="19 Years")
                    | Q(work_exp__startswith="20 Years")
                    | Q(work_exp__startswith="21 Years")
                    | Q(work_exp__startswith="22 Years")
                    | Q(work_exp__startswith="23 Years")
                    | Q(work_exp__startswith="24 Years")
                    | Q(work_exp__startswith="25 Years")
                    | Q(work_exp__startswith="26 Years")
                    | Q(work_exp__startswith="27 Years")
                    | Q(work_exp__startswith="28 Years")
                    | Q(work_exp__startswith="29 Years")
                    | Q(work_exp__startswith="30 Years")
                )
            elif request.GET['work_experience']=='3-5 Years':
                emp_pool=emp_pool.filter(
                    Q (work_exp__startswith="3 Years") 
                    | Q(work_exp__startswith="4 Years") 
                    | Q(work_exp__startswith="5 Years") 
                    | Q(work_exp="3-5"))
            elif request.GET['work_experience'] == '1-2 Years':
                emp_pool=emp_pool.filter(
                    Q(work_exp__startswith="1 Years ")  
                    | Q(work_exp="1-2")
                    | Q(work_exp__startswith="2 Years")  
                )
            elif request.GET['work_experience'] == '6-10 Years':
               emp_pool=emp_pool.filter( 
                Q(work_exp="6-10")
                | Q(work_exp__startswith="6 Years")
                | Q(work_exp__startswith="7 Years") 
                | Q(work_exp__startswith="8 Years") 
                | Q(work_exp__startswith="9 Years") 
                | Q(work_exp__startswith="10 Years"))
            else:
               emp_pool=emp_pool.filter(work_exp__icontains=request.GET['work_experience'])
        if 'willing_to_relocate' in request.GET:
            relocate=json.loads(request.GET.get('willing_to_relocate'))
            if relocate:
                emp_pool=emp_pool.filter(relocate=True)
        if 'education_level' in request.GET and request.GET['education_level'].strip():
            education_level = [level.strip() for level in request.GET['education_level'].split(',')]
            if 'others' in education_level:
              additional_levels = ['Professional', 'HighSchool', 'College', 'Vocational', 'Certification', 'Associates']
              education_level.extend(additional_levels)      
            emp_pool = emp_pool.filter(reduce(operator.or_, (Q(qualification__icontains=qual) for qual in education_level)))
       
        if 'location' in request.GET and len(request.GET['location'])>0:
            emp_pool=emp_pool.filter(location__icontains=request.GET['location'])
        if 'skill_match' in request.GET and request.GET['skill_match'].strip():
            skill_match_list = [skill.strip() for skill in request.GET['skill_match'].split(',')]
            emp_pool = emp_pool.filter(reduce(or_ , (Q(skills__icontains=item) for item in skill_match_list)))
      
        if 'search' in request.GET:
            if '@' in request.GET['search']:
                emp_pool=emp_pool.filter(email__icontains=request.GET['search'])
            elif len(request.GET['search']) > 0:
                emp_pool=emp_pool.filter(first_name__icontains=request.GET['search'])
        total_count=emp_pool.count()
        completed=emp_pool.filter(first_name__isnull=False,email__isnull=False).count()
        incompleted=emp_pool.filter(Q(first_name__isnull=True) | Q(email__isnull=True)).count()
        if not 'total' in request.GET :
            if 'completed' in request.GET:
                emp_pool=emp_pool.filter(first_name__isnull=False,email__isnull=False)
            elif 'incompleted' in request.GET:
                emp_pool=emp_pool.filter(Q(first_name__isnull=True) | Q(email__isnull=True))
        search = 1
        if emp_pool.count() == 0:
            search = 0
        page = request.GET.get('page', 1)
        page_count = request.GET.get('pagecount',None)
        if page_count:
            if 'jd_id' in request.GET:
                if pagination.objects.filter(user_id=request.user,page_id=4).exists():
                    if page_count:
                        pagination.objects.filter(user_id=request.user,page_id=4).update(pages=page_count)
                page_count =  pagination.objects.get(user_id=request.user,page_id=4).pages
            elif not pagination.objects.filter(user_id=request.user,page_id=4).exists():
                page_count = tmete_pages.objects.get(id=4).default_value
            else:
                if pagination.objects.filter(user_id=request.user,page_id=3).exists():
                    if page_count:
                        pagination.objects.filter(user_id=request.user,page_id=3).update(pages=page_count)
                    page_count =  pagination.objects.get(user_id=request.user,page_id=3).pages
                elif not pagination.objects.filter(user_id=request.user,page_id=3).exists():
                    page_count = tmete_pages.objects.get(id=3).default_value
        else:
            if 'jd_id' in request.GET:
                if pagination.objects.filter(user_id=request.user,page_id_id=4).exists():
                    page_count = pagination.objects.get(user_id=request.user,page_id_id=4).pages
                else:
                    page_count = tmete_pages.objects.get(id=4).default_value
            else:
                if pagination.objects.filter(user_id=request.user,page_id_id=3).exists():
                    page_count = pagination.objects.get(user_id=request.user,page_id_id=3).pages
                else:
                    page_count = tmete_pages.objects.get(id=3).default_value
        paginator = Paginator(emp_pool, page_count)
        try:
            emp_pool = paginator.page(page)
        except PageNotAnInteger:
            emp_pool = paginator.page(1)

        except EmptyPage:
            emp_pool = paginator.page(paginator.num_pages)
        emp_pool=emp_pool.object_list
        get_dict_copy = request.GET.copy()
        params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()
        try:
            data=matching_loader.objects.filter(user_id=user_id).exists()     
        except:
            data=False

        candidate_location = [] 
        candidatelocation = employer_pool.objects.filter(user_id_id = user_id).values_list('id',flat=True).distinct() 
        for data in candidatelocation: 
            if 'jd_id' in request.GET and employer_pool.objects.filter(id = data,location__isnull = False,jd_id_id__isnull = False).exists():
                lo = employer_pool.objects.get(id = data).location
                
            elif employer_pool.objects.filter(id = data,location__isnull = False,jd_id_id__isnull = True).exists():
                lo = employer_pool.objects.get(id = data).location
            else:
                lo = None
            if lo not in candidate_location and lo:
                candidate_location.append(lo)
        jd_id_in = None
        if 'jd_id' in request.GET:
            jd_id_in = 1
        else:
            jd_id_in = 0

        context= {"success":True,
        'emp_pool': emp_pool.values(),
        'params':params,
        'completed':completed,
        'incompleted':incompleted,
        'questionnaire':questionnaire,
        'total_count':total_count,
        'search':search,
        'career_url':career_url,
        'job':job,
        'data':data,
        'candidate_location':candidate_location,
        'jd_id_in':str(jd_id_in)
         }
        return Response(context)

    def post(self,request,*args, **kwargs):
        user_id ,updated_by = admin_account(self.request)
        if 'name' in self.request.POST:
            from django.utils import timezone
            employer_pool.objects.filter(id=self.request.POST['pk']).update(updated_on=timezone.now())
            jd_id = self.request.POST.get("jd_id",None)
            updated_on = datetime.now().strftime('%Y-%m-%d')
            if self.request.POST['name']== 'email':
                emp_table = employer_pool.objects.get(id=self.request.POST['pk'])
                if employer_pool.objects.filter(email=self.request.POST['value'],client_id=user_id).exists():
                    data = {'success': False,'error_msg': 'Email ID already exists'}
                    return Response(data)
                employer_pool.objects.filter(id=self.request.POST['pk']).update(email=self.request.POST['value'])
                update_email = candidate_parsed_details.objects.get(candidate_id= self.request.POST['pk'])
                parsed_text = json.loads(update_email.parsed_text)
                parsed_text['Email'] = self.request.POST['value']
                update_email.parsed_text = json.dumps(parsed_text)
                update_email.save()
        
                if emp_table.jd_id !=None:
                    user = User_Info.objects.get(user_id=emp_table.candidate_id.user_id)
                    user.email =self.request.POST['value']
                    user.save()
                if employer_pool.objects.get(id=self.request.POST['pk']).first_name == None:
                    data = {'first_name': False,'pk':self.request.POST['pk']}
                else:
                    if employer_pool.objects.get(id=self.request.POST['pk']).email != None:
                        if jd_id:
                            candd = self.request.POST['pk']
                            if not applicants_status.objects.filter(jd_id = jd_id ,candidate_id = candd).exists():
                                applicants_status.objects.create(jd_id = JD_form.objects.get(id=jd_id),candidate_id = employer_pool.objects.get(id = candd),status_id_id=1,client_id=user_id,source='Imported Applicants')
                                candidate_notification_upload(candd,jd_id,user_id)
                                email_automation(candd,jd_id,user_id)
                        data = {'first_name': True,'pk':self.request.POST['pk'], "success":True,'msg':'successfully updated','updated_on': updated_on}
                        
                    try:
                        company_name = company_details.objects.get(recruiter_id_id=user_id).company_name
                    except:
                        company_name = ''
                    if emp_table.jd_id !=None:
                        Personal_Info.objects.filter(application_id=employer_pool.objects.get(id=self.request.POST['pk']).candidate_id.pk).update(email=self.request.POST['value'])
                        user = User_Info.objects.get(user_id=emp_table.candidate_id.user_id)
                        user.email =self.request.POST['value']
                        user.save()
                        User.objects.filter(id=user.user_id.pk).update(email=self.request.POST['value'])

                return Response(data)


            if self.request.POST['name']== 'username': 
                emp_table = employer_pool.objects.get(id=self.request.POST['pk'])
                employer_pool.objects.filter(id=self.request.POST['pk']).update(first_name=self.request.POST['value'])
                update_name = candidate_parsed_details.objects.get(candidate_id= self.request.POST['pk'])
                parsed_text = json.loads(update_name.parsed_text)
                parsed_text['Name'] = self.request.POST['value']
                update_name.parsed_text = json.dumps(parsed_text)
                update_name.save()
                if emp_table.jd_id !=None:
                    emp_table = employer_pool.objects.get(id=self.request.POST['pk'])
                    user = User_Info.objects.get(user_id=emp_table.candidate_id.user_id)
                    user.first_name =self.request.POST['value']
                    user.save()
                    User.objects.filter(id=user.user_id.pk).update(first_name=self.request.POST['value'])
                    Personal_Info.objects.filter(application_id=employer_pool.objects.get(id=self.request.POST['pk']).candidate_id.pk,).update(firstname=self.request.POST['value'])
                if employer_pool.objects.get(id=self.request.POST['pk']).email == None:
                    data = {'email': False,'pk':self.request.POST['pk']}
                else:
                    if employer_pool.objects.get(id=self.request.POST['pk']).first_name != None:
                        if jd_id:
                            candd = self.request.POST['pk']
                            if not applicants_status.objects.filter(jd_id = jd_id ,candidate_id = candd).exists():
                                applicants_status.objects.create(jd_id = JD_form.objects.get(id=jd_id),candidate_id = employer_pool.objects.get(id = candd),status_id_id=1,client_id=user_id,source='Imported Applicants')
                                candidate_notification_upload(candd,jd_id,user_id)
                                email_automation(candd,jd_id,user_id)              
                        data = {'email': True,'pk':self.request.POST['pk'], "success":True,'msg':'successfully updated','updated_on': updated_on}
                       

                    try:
                        data = {'email': True,'pk':self.request.POST['pk'], "success":True,'msg':'successfully updated','updated_on': updated_on}
                       
                        try:
                            company_name = company_details.objects.get(recruiter_id_id=user_id).company_name
                        except:
                            company_name = ''
                    except Exception as e:
                        data = {"success":True,"Error":str(e)}
                return Response(data)


            if self.request.POST['name']== 'sent_email':
                emp_table = employer_pool.objects.get(id=self.request.POST['pk'])
                try:
                    company_name = company_details.objects.get(recruiter_id_id=user_id).company_name
                except:
                    company_name = ''
                emp_table = employer_pool.objects.get(id=self.request.POST['pk'])
                user = User_Info.objects.get(user_id=emp_table.candidate_id.user_id)
                jd_title = emp_table.jd_id.job_title
                try:
                    domain= settings.CLIENT_URL
                    htmly = get_template('email_templates/applicants_login.html')
                    subject, from_email, to = str(company_name)+' Login ', email_main, user.email
                   
                    html_content = htmly.render({'jd_title':jd_title,'company_name':company_name,'user':user,'domain':domain})
                    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                    msg.attach_alternative(html_content, "text/html")
                    msg.mixed_subtype = 'related'
                    image_data =['twitter.png','linkedin.png','youtube.png','new_zita_white.png']
                    for i in image_data:
                        msg.attach(logo_data(i))
                    msg.send()

                    employer_pool.objects.filter(id=self.request.POST['pk']).update(login_shared=True)
                except Exception as e:
                    logger.error("Applicants Email error ---- "+str(e))
                data = {'pk':request.POST['pk'], "success":True,'msg':'successfully updated','updated_on':updated_on}
                return Response(data)


            if self.request.POST['name']== 'contact':
                emp_table = employer_pool.objects.get(id=self.request.POST['pk'])
                employer_pool.objects.filter(id=self.request.POST['pk']).update(contact=self.request.POST['value'])
                if emp_table.jd_id !=None:
                    Personal_Info.objects.filter(application_id=employer_pool.objects.get(id=self.request.POST['pk']).candidate_id.pk).update(contact_no=self.request.POST['value'])
            if self.request.POST['name']== 'relocate':
                employer_pool.objects.filter(id=self.request.POST['pk']).update(relocate=self.request.POST['value'])
            if self.request.POST['name']== 'linkedin_url':
                employer_pool.objects.filter(id=self.request.POST['pk']).update(linkedin_url=self.request.POST['value'])
            if self.request.POST['name']== 'exp_salary':
                employer_pool.objects.filter(id=self.request.POST['pk']).update(exp_salary=self.request.POST['value'])
            if self.request.POST['name']== 'qualification':
                employer_pool.objects.filter(id=self.request.POST['pk']).update(qualification=self.request.POST['value'])
                can = self.request.POST['pk']
                update_qual = candidate_parsed_details.objects.get(candidate_id= self.request.POST['pk'])
                parsed_text = json.loads(update_qual.parsed_text)
                parsed_text['Highest Qualifications'] = self.request.POST['value']
                update_qual.parsed_text = json.dumps(parsed_text)
                update_qual.save()
                data = {'pk':self.request.POST['pk'], "success":True,'msg':'successfully updated','updated_on': updated_on}
                return Response(data)
            if self.request.POST['name']== 'experience':
                employer_pool.objects.filter(id=self.request.POST['pk']).update(work_exp=self.request.POST['value'])
                exp = self.request.POST['value']
                can = self.request.POST['pk']
                update_exp = candidate_parsed_details.objects.get(candidate_id= self.request.POST['pk'])
                parsed_text = json.loads(update_exp.parsed_text)
                parsed_text['Total years of Experience'] = exp + ' years'
                update_exp.parsed_text = json.dumps(parsed_text)
                update_exp.save()
                data = {'pk':self.request.POST['pk'], "success":True,'msg':'successfully updated','updated_on': updated_on}
                return Response(data)

            if self.request.POST['name']== 'skills':
                skills =self.request.POST['value'].replace(", ", ",").replace(",", ", ")
                employer_pool.objects.filter(id=self.request.POST['pk']).update(skills=skills)
                emp_table = employer_pool.objects.get(id=self.request.POST['pk'])
                can = self.request.POST['pk']
                update_skill = candidate_parsed_details.objects.get(candidate_id= self.request.POST['pk'])
                parsed_text = json.loads(update_skill.parsed_text)
                if isinstance(skills,str):
                    skills = skills.split(',')
                parsed_text['Technical skills'] = skills
                update_skill.parsed_text = json.dumps(parsed_text)
                update_skill.save()
                jd_list = JD_form.objects.filter(user_id =emp_table.client_id,jd_status = 1).values_list('id',flat = True)
                for y in jd_list:
                    if not applicants_status.objects.filter(jd_id = y,candidate_id = self.request.POST['pk']).exists():
                        basic_matching(self.request.POST['pk'],y,emp_table.client_id,request)
                
                if emp_table.jd_id !=None:
                    if Skills.objects.filter(application_id=emp_table.candidate_id).exists():

                        Skills.objects.filter(application_id=emp_table.candidate_id).update(tech_skill =self.request.POST['value'] )
                    else:
                        Skills.objects.create(application_id=emp_table.candidate_id,tech_skill =self.request.POST['value'] )

                data = {'pk':request.POST['pk'], "success":True,'msg':'successfully updated','updated_on':updated_on}
                return Response(data)

            if self.request.POST['name']== 'location':
                employer_pool.objects.filter(id=self.request.POST['pk']).update(location=self.request.POST['value'])
                if employer_pool.objects.get(id=self.request.POST['pk']).email != None:
                    update_loc = candidate_parsed_details.objects.get(candidate_id= self.request.POST['pk'])
                    parsed_text = json.loads(update_loc.parsed_text)
                    parsed_text['Location'] = self.request.POST['value']
                    update_loc.parsed_text = json.dumps(parsed_text)
                    update_loc.save()
                    data = {'pk':self.request.POST['pk'], "success":True,'msg':'successfully updated','updated_on': updated_on}
                    return Response(data)

        try:
            return Response(data)
        except Exception as e:
            logger.error("Data update error ---- "+str(e))
            return Response({'data':1, "success":True,'updated_on': updated_on})
        

class Dr_Job_Integration(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        pk=request.POST.get('pk')
        action = self.request.POST.get('action')
        job_boards_raw = request.POST.get('job_boards', '{}')
        job_boards_dict = eval(job_boards_raw)
        print("&&&&&&&&&&&&&&&&",job_boards_dict,"&&&^&&^&^&^",pk,"^^^^^^^^^^",action)
        jd=JD_form.objects.get(id=pk)
        if not job_board_list.objects.filter(job_id=jd,name="drjob").exists():
            job_board_list.objects.get_or_create(name="drjob",job_id=jd,is_active=job_boards_dict['drjob'])
        else:
            job_board_list.objects.filter(job_id=jd,name="drjob").update(is_active=job_boards_dict['drjob'])
        if action=='True':

            try:
                jd=JD_form.objects.get(id=pk)
                company=company_details.objects.get(recruiter_id=jd.user_id)
                location = JD_locations.objects.get(jd_id=pk)
                job_type=jd.work_space_type
                if job_type==3:
                    job_type=8
                else:
                    job_type=1       
                skill=[]
                d=JD_skills_experience.objects.filter(jd_id_id=jd).values('skill')
                for i in d:
                    skill.append(i['skill'])
                skill = ','.join(skill)   
                url="https://drjobfeedapi.drjobpro.com/api/postJobs"    
                
                headers={
                    "Content-Type":"application/json",
                    "x-auth-token":"uS1E342OOi90OUxOUmgjtm7Vl"
                }
                payload={
                    "job_id":int(pk),
                    "ats_job_id":int(pk),
                    "job_source":52,
                    "language":1,
                    "company_id":85300,
                    "job_title":jd.job_title,
                    "job_description":jd.richtext_job_description,
                    "company_name":company.company_name,
                    "skills":skill,
                    "cv_email":company.email,
                    "no_of_vacancies": jd.no_of_vacancies,
                    "city":location.city.name ,
                    "job_type": job_type,
                    "country": location.country.name ,
                    "logo_pic":"https://api.zita.ai/media/{}".format(company.logo)
                }

                response = requests.post(url=url,json=payload, headers=headers)
                data=response.json()
                job_board_list.objects.filter(job_id=jd,name="drjob").update(job_board_id=data["job_id"])
                return Response({"data": data})
        
            except Exception as e:
                return Response({"status": 503, "msg": e}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            response_data = {
                "id": pk,
                "success": True
                
            }
            return Response(response_data, status=status.HTTP_201_CREATED)        
    def put(self, request):
        pk=request.POST.get('pk')

        try:
            jd=JD_form.objects.get(id=pk)
            job_board_id=job_board_list.objects.get(job_id=pk).job_board_id
            job=pk
            company=company_details.objects.get(recruiter_id=jd.user_id)
            skill=[]
            d=JD_skills_experience.objects.filter(jd_id_id=jd).values('skill')
            for i in d:
                skill.append(i['skill'])
            skill = ','.join(skill)  
            location = JD_locations.objects.get(jd_id=pk)

            job_type=jd.work_space_type
            if job_type==3:
                job_type=8
            else:
                job_type=1    
           
            url="https://drjobfeedapi.drjobpro.com/api/editJobs"

            headers={
                "Content-Type":"application/json",
                "x-auth-token":"uS1E342OOi90OUxOUmgjtm7Vl"
            }
            payload={
               "job_id":job_board_id,
                "ats_job_id":int(pk),
                "job_source":52,
                "language":1,
                "company_id":85300,
                "job_title":"django developer",
                "job_description":jd.richtext_job_description,
                "company_description": "Zita024 is a leading tech company specializing in software development and IT services.",  
                "company_name":company.company_name,
                "skills":skill,
                "cv_email":company.email,
                "no_of_vacancies": jd.no_of_vacancies,
                "city":location.city.name ,
                "job_type": job_type,
                "country": location.country.name ,
                "logo_pic":"https://api.zita.ai/media/{}".format(company.logo)
            }
            response = requests.post(url=url,json=payload, headers=headers)
            return Response({"data": response.json()})
        
        except Exception as e:
            return Response({"status": 503, "msg": e}, status=status.HTTP_503_SERVICE_UNAVAILABLE)        
    def delete(self, request):
        pk=request.POST.get('pk')
        job_id=job_board_list.objects.get(job_id=pk).job_board_id
        url="https://drjobfeedapi.drjobpro.com/api/removeJobs"    

        headers={
                "Content-Type":"application/json",
                "x-auth-token":"uS1E342OOi90OUxOUmgjtm7Vl"
            }
        payload={
            "job_id":job_id,
            "ats_job_id":int(pk)
        }
        response = requests.post(url=url,json=payload, headers=headers)

        job_board_list.objects.filter(job_id=pk).update(is_active=0)
        return Response({"data": response.json()})
    def get(self, request):

        pk=request.POST.get('pk')
        job_id=job_board_list.objects.get(job_id=pk,name="drjob").job_board_id
        url="https://drjobfeedapi.drjobpro.com/api/getLiveJobs"    

        headers={
                "Content-Type":"application/json",
                "x-auth-token":"uS1E342OOi90OUxOUmgjtm7Vl"
            }
        payload={
            "job_id":job_id
        }
        response = requests.post(url=url,json=payload, headers=headers)
        return Response({"data": response.json()})
def calculate_experience_duration(experiences):
    total_months = 0
    
    for exp in experiences:
        start_date = datetime.strptime(exp["Work_Duration_From"], "%m-%Y")
        
        if exp["Work_Duration_To"].lower() == "tillnow":
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(exp["Work_Duration_To"], "%m-%Y")
        
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        total_months += months
    
    total_years = total_months // 12
    remaining_months = total_months % 12
    
    return total_years, remaining_months
# import fitz 
# class dr_job_board_apply(generics.GenericAPIView):
#     #permission_classes = [permissions.IsAuthenticated]
#     permission_classes = [permissions.AllowAny]
#     def post(self, request, *args, **kwargs):
#         ats_job_id = self.kwargs.get('ats_job_id')

#         resumes=request.data.get('resumes')
#         job_id=request.data.get('ats_job_id')
#         first_name = request.data.get('first_name')
#         last_name = request.data.get('last_name')
#         email = request.data.get('email')
#         mobile = request.data.get('mobile')
#         phone = request.data.get('phone')
#         skills = request.data.get('skills')
#         job_title = request.data.get('job_title')
#         street = request.data.get('street')
#         city = request.data.get('city')
#         state=request.data.get('state')
#         country= request.data.get('country')
#         zipcode = request.data.get('zipcode')
#         educations= request.data.get('educations')
#         experience=request.data.get('experience')
#         resumes=request.data.get('resumes')
#         years, months = calculate_experience_duration(experience)
#         experience="{} years {} months".format(years,months)
#         location=city+','+state+','+country
#         resumes = request.data.get('resumes', [])
#         user_id=JD_form.objects.get(id=job_id).user_id.id
#         updated_by=JD_form.objects.get(id=job_id).user_id
#         def extract_pdf(file_path):
#             doc = fitz.open(file_path)
#             text = ""
#             for page_num in range(len(doc)):
#                 page = doc.load_page(page_num)
#                 text += page.get_text()
#             return text

#         for resume in resumes:
#             filename = resume.get('filename')
#             content = resume.get('content')
#             binary_data = base64.b64decode(content)
            
#             file_path = base_dir+ "/media/dr_job/"+filename
#             with open(file_path, 'wb') as resume_file:
#                 resume_file.write(binary_data)
            
#             file_content = extract_pdf(file_path)
#         candidate_profile = profile_summary(file_content)  
#         emp_id = employer_pool.objects.create(
#                         can_source_id=5,
#                         client_id=user_id,
#                         updated_by=updated_by,
#                         candidate_id=None,
#                         job_type=None,
#                         first_name=first_name,
#                         last_name=last_name,
#                         email=email,
#                         linkedin_url=None,
#                         contact=mobile,
#                         work_exp=experience,
#                         relocate=None,
#                         qualification=educations["Degree"],
#                         exp_salary=None,
#                         user_id=user_id,
#                         job_title=job_title,
#                         skills=skills,
#                         location=location,
#                     )
#         candidate_profile_detail.objects.create(candidate_id=emp_id, profile_summary=candidate_profile)
        
#         response_data = {
#                 "id":ats_job_id,
#                 "status": "updated/added"
#                 }
        

#         return Response(response_data, status=status.HTTP_201_CREATED)        



import json
import string
from deep_translator import GoogleTranslator
translator = GoogleTranslator(source='auto', target='en')

def is_english(text):
    return all(char in string.ascii_letters + string.punctuation + string.whitespace for char in text)
def remove_emojis(text):
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs 
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # other symbols
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)
def translate_selected_fields(json_data):
    data = ["name", "first_name", "last_name", "title", "user_generated_headline","summary"]
    translation_flag = False 
    for i in data:
        if i in json_data and isinstance(json_data[i], str):  
            json_data[i] = remove_emojis(json_data[i])
            if not is_english(json_data[i]): 
                json_data[i] = translator.translate(json_data[i])  
                translation_flag = True
    
    if "member_experience_collection" in json_data and isinstance(json_data["member_experience_collection"], list):
        for experience in json_data["member_experience_collection"]:
            if "company_name" in experience and not is_english(experience["company_name"]):
                experience["company_name"] = translator.translate(experience["company_name"])
                translation_flag = True
    if "member_certifications_collection" in json_data and isinstance(json_data["member_certifications_collection"], list):
        for certification in json_data["member_certifications_collection"]:
            if "name" in certification and not is_english(certification["name"]):
                certification["name"] = translator.translate(certification["name"])   
                translation_flag = True         
    if "member_education_collection" in json_data and isinstance(json_data["member_education_collection"], list):
        for education in json_data["member_education_collection"]:
            if "title" in education and not is_english(education["title"]):
                education["title"] = translator.translate(education["title"])   
                translation_flag = True 
            if  education["subtitle"]!=None:
                if "subtitle" in education and not is_english(education["subtitle"]):
                    if education["subtitle"]!=None:
                        education["subtitle"] = translator.translate(education["subtitle"])         
                        translation_flag = True   

    return json_data,translation_flag



class ZitaAPIService(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user_id = request.user
        api_key = request.GET.get('api_key',None)
        if not zita_api_service.objects.filter(user_id = user_id).exists():
            zita_api_service.objects.create(user_id = user_id,is_active = True,api_key = api_key)
        user_details = FT.standalone_userdetails(user_id)
        if isinstance(user_details,str):
            user_details = json.loads(user_details)
        # if isinstance(user_details,dict):
        #     for key,value in user_details.items():
        #         find_id = FT.identify_api_name(key)
        #         if find_id:
        #             if client_features_balance.objects.filter(client_id = user_id,feature_id = find_id).exists():
        #                 client_features_balance.objects.filter(client_id = user_id,feature_id = find_id).update(available_count =value,plan_count = value)
        #             print(key,value)
        data = client_features_balance.objects.filter(client_id = user_id).values()
        return Response({"success": True,"message": "User Added SuccessFully","response":user_details,"client_data":data})


from django.utils.html import strip_tags
from django.conf import settings
from xml.etree import ElementTree as ET
from xml.dom import minidom
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import generics
import os
from xml.etree import ElementTree as ET

class job_board_integration(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        pk = self.request.POST.get('pk')#'pk']
        job_boards_raw = request.POST.get('job_boards', '{}')
        action = self.request.POST.get('action')
        job_boards_dict = eval(job_boards_raw)

        print("*******************************************",job_boards_dict)
        job_boards = {board: value for board, value in job_boards_dict.items() if value}
        #if not job_board_list.objects.filter(job_id=pk).exists():
        jd_id=JD_form.objects.get(id=pk)
        if not job_board_list.objects.filter(job_id=jd_id,name="jora").exists():
            job_board_list.objects.get_or_create(name="jora",job_id=jd_id,is_active=job_boards_dict['jora'])
        print("&*&*&*&*&*&")
        if not job_board_list.objects.filter(job_id=jd_id,name="career_jet").exists():
            job_board_list.objects.get_or_create(name="career_jet",job_id=jd_id,is_active=job_boards_dict['career_jet'])
        print("33333333")
        if not job_board_list.objects.filter(job_id=jd_id,name="myjobhelper").exists():
            job_board_list.objects.get_or_create(name="myjobhelper",job_id=jd_id,is_active=job_boards_dict['myjobhelper'])
            #job_board_list.objects.get_or_create(name=",drjob",job_id=pk,is_active=job_boards_dict['drjob'])

        #else:
        job_board_list.objects.filter(job_id=jd_id,name="jora").update(is_active=job_boards_dict['jora'])
        job_board_list.objects.filter(job_id=jd_id,name="career_jet").update(is_active=job_boards_dict['career_jet'])
        job_board_list.objects.filter(job_id=jd_id,name="myjobhelper").update(is_active=job_boards_dict['myjobhelper'])
            #job_board_list.objects.filter(job_id=pk,name="drjob").update(is_active=job_boards_dict['drjob'])


            
        job_activated=job_board_list.objects.filter(job_id=jd_id).values('name','is_active')
        print("************",job_activated)
        activated_list = {item['name']: item['is_active'] for item in job_activated}
        print("*(*(*(*(*(*)))))",activated_list)
        file_paths = {
            'career_jet': base_dir + "/media/job_board/career_jet.xml",
            'jora': base_dir + "/media/job_board/jora.xml",
            'myjobhelper': base_dir + "/media/job_board/myjobhelper.xml",

        }


        job = JD_form.objects.get(id=pk)
        print(job.job_title.replace(' ','-'),'_+_+_+_+_+_+_+_+_+_+_+')
        try:
            location = JD_locations.objects.get(jd_id=pk)
            location_data = {
                "city": location.city,
                "region": location.state,
                "country": location.country
            }
        except JD_locations.DoesNotExist:
            location_data = {
                "city": "",
                "region": "",
                "country": ""
            }

        # Generate domain and company details
        domain = settings.CLIENT_URL
        company = company_details.objects.get(recruiter_id=job.user_id)
        url=career_page_setting.objects.get(recruiter_id=job.user_id).career_page_url
        skill = []
        d = JD_skills_experience.objects.filter(jd_id_id=job).values('skill')
        for i in d:
            skill.append(i['skill'])
        skill = ','.join(skill)
        active_status={}

 
        print("&&&&&&&&&&&&",action,type(action))
        if action=='True':
            for job_board in job_boards:
                print("!!!!!!!!!!!!!!!!!!!!!!!",job_board,)
                if job_board in file_paths:
                    file_path = file_paths[job_board]
                    print("&&&&&&&*(((((((((())))))))))",file_path)
                    # Load or create the XML root
                    if os.path.exists(file_path):
                        tree = ET.parse(file_path)
                        root = tree.getroot()
                    else:
                        root = ET.Element("jobs")

                    # Check for existing job and remove if found
                    job_id = str(pk)
                    jobs_to_remove = []

                    for job_elem in root.findall(".//job"):
                        job_id_elem = job_elem.find("job-id")
                        if job_id_elem is not None:
                            def strip_cdata(text):
                                if text.startswith('<![CDATA[') and text.endswith(']]>'):
                                    return text[9:-3]
                                return text

                            clean_job_id = strip_cdata(job_id_elem.text.strip())
                            if clean_job_id == job_id:
                                jobs_to_remove.append(job_elem)

                    if jobs_to_remove:
                        for job_elem in jobs_to_remove:
                            root.remove(job_elem)

                    # Add job data to XML based on job board type
                    print("333344455566666666666")
                    #if not  job_board_list.objects.filter(job_id=pk,name="career_jet",is_active=1).exists():
                    #    print("*******111111111111111*")
                    if 'career_jet' in job_board:
                            print("!!!!!!!!!!!!!!!!!!eeeeeeeee!!!!!!!!!!!!!!!!")
                            job_elem = ET.SubElement(root, "job")
                            self.add_cdata_element(job_elem, "job-id", str(job.id))
                            self.add_cdata_element(job_elem, "title", job.job_title)
                            self.add_cdata_element(job_elem, "url", f"{domain}{url}/{company.company_name}/career_job_view/{job.id}/{job.job_title}")

                            # Location details
                            if JD_locations.objects.filter(jd_id=pk).exists():
                                location_elem = ET.SubElement(job_elem, "location")
                                self.add_cdata_element(location_elem, "city", location_data["city"])
                                self.add_cdata_element(location_elem, "region", location_data["region"])
                                self.add_cdata_element(location_elem, "country", location_data["country"])
                                self.add_cdata_element(location_elem, "zip", company.zipcode)
                            # Company details
                            self.add_cdata_element(job_elem, "company", company.company_name)
                            self.add_cdata_element(job_elem, "company_url", company.company_website)

                            # Job description
                            description_elem = ET.SubElement(job_elem, "description")
                            self.add_cdata_element(description_elem, "full-text", job.job_description)
                            try:
                                Education = JD_qualification.objects.get(jd_id=pk)
                                self.add_cdata_element(job_elem, "qualificationt", Education.qualification)
                            except:
                                pass    
                            self.add_cdata_element(job_elem, "contract_type", "permanent")
                            self.add_cdata_element(job_elem, "working_hours", "full-time")
                            self.add_cdata_element(job_elem, "salary", f"${job.salary_min} - ${job.salary_max}")


                            self.add_cdata_element(job_elem, "application_email", company.email)
                            self.add_cdata_element(job_elem, "job_reference", f"FXGT-{job.job_id}")
                            self.add_cdata_element(job_elem, "apply_url", f"{domain}/{url}/career_job_view/{job.id}/{job.job_title}")
                            self.add_cdata_element(job_elem, "skill", skill)

                            careerjet_data = (
                                "apply_key=043762d616698aa9ddef8a93624ee314&jobTitle={}&jobLocation={}, {}, {}&jobCompanyName={}&postUrl={}&phone=optional&coverletter=optional&hl=en_US"
                                .format(job.job_title, location_data["city"], location_data["region"], location_data["country"], company.company_name,
                                        f"https://www.example.com/apply/careerjet?ref=FXGT-{job.job_id}")
                            )
                            self.add_cdata_element(job_elem, "careerjet-apply-data", careerjet_data)
                            # Convert the XML to a pretty-printed string
                            xml_str = ET.tostring(root, encoding='utf-8')
                            xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")

                            # Write to file
                            with open(file_path, "w", encoding='utf-8') as file:
                                file.write(xml_str)
                                job_board_list.objects.get_or_create(name="career_jet",job_id=job,is_active=1)
                                active_status['career_jet'] = True
                    #elif not  job_board_list.objects.filter(job_id=pk,name="jora",is_active=1).exists():
                    #    print("22222222222222")
                    if job_board == 'jora':
                            print("&*&*&*&*&*&*&*&*********((((((((((((()))))))))))))")
                            job_elem = ET.Element("job")
                            source_elem = ET.SubElement(job_elem, "source")
                            ET.SubElement(source_elem, "publisher").text = "zita"

                            ET.SubElement(job_elem, "title").text = f"<![CDATA[{job.job_title}]]>"
                            ET.SubElement(job_elem, "id").text = f"<![CDATA[{job.id}]]>"
                            ET.SubElement(job_elem, "listed_date").text = "<![CDATA[{}]]>".format(job.created_on.strftime("%a, %d %b %Y %H:%M:%S %Z"))
                            ET.SubElement(job_elem, "organisation").text = f"<![CDATA[{company.company_name}]]>"
                            if JD_locations.objects.filter(jd_id=pk).exists():
                                ET.SubElement(job_elem, "location").text = f"<![CDATA[{location_data['city']}, {location_data['region']}, {location_data['country']}]]>"
                                ET.SubElement(job_elem, "city").text = f"<![CDATA[{location_data['city']}]]>"
                                ET.SubElement(job_elem, "state").text = f"<![CDATA[{location_data['region']}]]>"
                                ET.SubElement(job_elem, "country").text = f"<![CDATA[{location_data['country']}]]>"
                                ET.SubElement(job_elem, "zip").text = f"<![CDATA[{company.zipcode}]]>"
                            ET.SubElement(job_elem, "description").text = f"<![CDATA[{job.job_description}]]>"
                            try:
                                ET.SubElement(job_elem, "qualificationt").text = f"<![CDATA[{Education.qualification}]]>"
                            except:
                                pass
                            ET.SubElement(job_elem, "skill").text = f"<![CDATA[{skill}]]>"
                            salary_elem = ET.SubElement(job_elem, "salary")
                            ET.SubElement(salary_elem, "type").text = "monthly"
                            ET.SubElement(salary_elem, "min").text = f"{job.salary_min}"
                            ET.SubElement(salary_elem, "max").text = f"{job.salary_max}"
                            ET.SubElement(salary_elem, "currency").text = "$"

                            ET.SubElement(job_elem, "jobtype").text = f"<![CDATA[Full Time]]>"
                            ET.SubElement(job_elem, "url").text = f"<![CDATA[{domain}{url}/career_job_view/{job.id}/{job.job_title}]]>"

                            root.append(job_elem)

                            # Convert the XML to a pretty-printed string
                            xml_str = ET.tostring(root, encoding='utf-8')
                            xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")

                            
                            with open(file_path, "w", encoding='utf-8') as file:
                                file.write(xml_str)
                                job_board_list.objects.get_or_create(name="jora",job_id=job,is_active=1)
                                active_status['jora'] = True
                    #elif not  job_board_list.objects.filter(job_id=pk,name="myjobhelper",is_active=1).exists():
                    print("33333333333333333")
                    if job_board == 'myjobhelper':
                            job_elem = ET.Element("job")
                            source_elem = ET.SubElement(job_elem, "source")


                            ET.SubElement(job_elem, "title").text = f"<![CDATA[{job.job_title}]]>"
                            ET.SubElement(job_elem, "id").text = f"<![CDATA[{job.id}]]>"
                            ET.SubElement(job_elem, "listed_date").text = "<![CDATA[{}]]>".format(job.created_on.strftime("%a, %d %b %Y %H:%M:%S %Z"))
                            ET.SubElement(job_elem, "organisation").text = f"<![CDATA[{company.company_name}]]>"
                            if JD_locations.objects.filter(jd_id=pk).exists():
                                ET.SubElement(job_elem, "location").text = f"<![CDATA[{location_data['city']}, {location_data['region']}, {location_data['country']}]]>"
                                ET.SubElement(job_elem, "city").text = f"<![CDATA[{location_data['city']}]]>"
                                ET.SubElement(job_elem, "state").text = f"<![CDATA[{location_data['region']}]]>"
                                ET.SubElement(job_elem, "country").text = f"<![CDATA[{location_data['country']}]]>"
                                ET.SubElement(job_elem, "zip").text = f"<![CDATA[{company.zipcode}]]>"

                            else:    
                                wrk="remote"
                                ET.SubElement(job_elem, "work_mode").text = f"<![CDATA[{wrk}]]>"
                            ET.SubElement(job_elem, "description").text = f"<![CDATA[{job.job_description}]]>"
                            try:
                                ET.SubElement(job_elem, "qualificationt").text = f"<![CDATA[{Education.qualification}]]>"
                            except:
                                pass    
                            ET.SubElement(job_elem, "skill").text = f"<![CDATA[{skill}]]>"

                            salary_elem = ET.SubElement(job_elem, "salary")
                            ET.SubElement(salary_elem, "type").text = "monthly"
                            ET.SubElement(salary_elem, "min").text = f"{job.salary_min}"
                            ET.SubElement(salary_elem, "max").text = f"{job.salary_max}"
                            ET.SubElement(salary_elem, "currency").text = "$"
                            ET.SubElement(salary_elem, "additionalText").text = "Award rates"

                            ET.SubElement(job_elem, "jobtype").text = f"<![CDATA[Full Time]]>"

                            ET.SubElement(job_elem, "url").text = f"<![CDATA[{domain}{url}/career_job_view/{job.id}/{job.job_title.replace(' ','-')}]]>"

                            root.append(job_elem)

                            # Convert the XML to a pretty-printed string
                            xml_str = ET.tostring(root, encoding='utf-8')
                            xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")

                            # Write to file
                            with open(file_path, "w", encoding='utf-8') as file:
                                file.write(xml_str)        
                                job_board_list.objects.get_or_create(name="myjobhelper",job_id=job,is_active=1)
                                active_status['myjobhelper'] = True
            response_data = {
                "id": pk,
                "success": activated_list
                
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                "id": pk,
                "success": True
                
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
    def get(self, request):
        pk=self.request.GET.get('pk')
        print("^^^^^^^^^^^^^^^^^^^",pk)
        if job_board_list.objects.filter(job_id=pk).exists():
            job_boards = job_board_list.objects.filter(job_id=pk)

            # Prepare the response data
            active_job_boards = {
                job_board.name: job_board.is_active for job_board in job_boards
            }
            response_data = {
                "success": True,
                "data":active_job_boards
                #   {
                #     "active_job_boards": active_job_boards
                # }
            }

            return Response(response_data)
        else:
            response_data={
                "success":False,
                "Data":"jd is not exist"
            }
            return Response(response_data)
    def add_cdata_element(self, parent, tag, text):
        """Helper function to add CDATA section in an XML element."""
        element = ET.SubElement(parent, tag)
        element.text = f"<![CDATA[{strip_tags(text)}]]>"
     

    def delete_job_from_xml(self, file_path, job_id,job_board):
        """Deletes all jobs from the XML file based on job_id."""
        print("^^&^&^&^&^&^&^&^&^",job_board)
        print("File path:", file_path)  
        if os.path.exists(file_path):
            print("File exists, proceeding to delete the job with ID:", job_id) 
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                def strip_cdata(text):
                    if text.startswith('<![CDATA[') and text.endswith(']]>'):
                        return text[9:-3]
                    return text

                jobs_to_remove = []
                for job_elem in root.findall(".//job"):
                    job_id_elem = job_elem.find("id")  # Adjust tag based on XML structure
                    if job_id_elem is not None:
                        clean_job_id = strip_cdata(job_id_elem.text.strip())
                        if clean_job_id == job_id:
                            jobs_to_remove.append(job_elem)

                if jobs_to_remove:
                    for job_elem in jobs_to_remove:
                        root.remove(job_elem)
                        print("Job element removed.") 

                    xml_str = ET.tostring(root, encoding='utf-8')
                    xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
                    with open(file_path, "w", encoding='utf-8') as file:
                        file.write(xml_str)
                    print("XML file updated successfully.")
                else:
                    print(f"No matching job element found for job-id: {job_id}")  #

            except ET.ParseError as e:
                print(f"Error parsing XML file: {e}") 
        else:
            print("File does not exist at the path:", file_path)
    def career_delete_job_from_xml(self, file_path, job_id,job_board):
        """Deletes all jobs from the XML file based on job_id."""
        print("File path:", file_path)  
        if os.path.exists(file_path):
            print("File exists, proceeding to delete the job with ID:", job_id) 
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                xml_str = ET.tostring(root, encoding='unicode')
                jobs_to_remove = []
                for job_elem in root.findall(".//job"):
                    job_id_elem = job_elem.find("job-id")
                    if job_id_elem is not None:
                        def strip_cdata(text):
                            if text.startswith('<![CDATA[') and text.endswith(']]>'):
                                return text[9:-3]
                            return text
                        clean_job_id = strip_cdata(job_id_elem.text.strip())
                        print(f"Found job-id: '{clean_job_id}'") 
                        if clean_job_id == job_id:
                            jobs_to_remove.append(job_elem)

                if jobs_to_remove:
                    for job_elem in jobs_to_remove:
                        print("Found job element:", ET.tostring(job_elem, encoding='unicode'))  
                        root.remove(job_elem)
                        print("Job element removed.") 

                    
                    xml_str = ET.tostring(root, encoding='utf-8')
                    xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
                    with open(file_path, "w", encoding='utf-8') as file:
                        file.write(xml_str)
                    print("XML file updated successfully.")
                else:
                    print(f"No matching job element found for job-id: {job_id}")  #

            except ET.ParseError as e:
                print(f"Error parsing XML file: {e}") 
        else:
            print("File does not exist at the path:", file_path)
        

