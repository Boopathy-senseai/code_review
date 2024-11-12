from distutils.command import build
from django.shortcuts import render
from datetime import datetime
from h11 import Request
from google.oauth2.credentials import Credentials
import pytz
import json
from calendarapp.api.google import convert_to_iso8601
from calendarapp.auth_helper import Google, Outlook
from calendarapp.graph_helper import outlook_create_event
from calendarapp.models import *
from calendarapp.utils import CalendarMailFun, get_fullname

from schedule_event.models import *

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

from google.oauth2.credentials import Credentials
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
import calendar
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import pytz
from calendarapp.api.outlook import *
from schedule_event.api import *
from schedule_event.models import Event_scheduler, Schedule_interview
from .models import *
from django.views.decorators.cache import never_cache
from zita import settings
import re

base_dir = settings.BASE_DIR
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, timedelta
from dateutil import tz, parser
from django.views.generic import ListView
from login.decorators import *
from calendarapp.models import Event
from jobs.views import user_permission
from django.contrib.auth.models import Permission
from google_auth_httplib2 import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from calendarapp.graph_helper import *


# user checking with their integration Account
def CalendarAddEvent(webevent, request, user, can_id):
    from calendarapp.api.outlook import (
        convert_to_datetime_with_timezone,
        inter_slot,
        titleConvertion,
    )
    from calendarapp.views import slotter_convertion
    from jobs.views import addon_interview_question
    from calendarapp.api import integrate_calendar_invite_mail

    # GoogleAddEvent
    join_url = None
    calendar_id = None
    schedule_time = request.POST.get("time", None)
    schedule_date = request.POST.get("date", None)
    if google_return_details.objects.filter(client_id=user).exists():
        if "id" in request.POST:
            event = Event_scheduler.objects.get(id=request.POST["id"])
            location = event.location
            description = event.description
        if "date" in request.POST:
            date = request.POST["date"]
        if "time" in request.POST:
            time = request.POST["time"]
        if "timezone" in request.POST:
            timezone = request.POST["timezone"]
            title = event.event_name
            event_type = event.event_type
            if event_type == "On-site Interview" or event_type == "Phone Interview":
                title = title + " " + "(" + " " + event_type + " " + ")"
                title = titleConvertion(title, time, date, can_id, website=True)
            else:
                title = titleConvertion(title, time, date, can_id, website=True)
        else:
            title = None

        if date and time and timezone:
            starttime, endtime = convert_to_datetime_with_timezone(date, time, timezone)
            starttime = convert_to_iso8601(starttime)
            endtime = convert_to_iso8601(endtime)
        if title and starttime and endtime and timezone:
            attendees = []
            website_email = website_userinfo.objects.get(id=can_id.id).email
            attendees.append({"email": website_email})
            event_info = {
                "summary": title,
                "location": location,
                "description": description,
                "start": {
                    "dateTime": str(starttime),
                    "timeZone": timezone,
                },
                "end": {"dateTime": str(endtime), "timeZone": timezone},
                "recurrence": ["RRULE:FREQ=DAILY;COUNT=1"],
                "attendees": attendees,
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},
                        {"method": "popup", "minutes": 10},
                    ],
                },
                "conferenceDataVersion": 1,
                "conferenceData": {
                    "createRequest": {
                        "requestId": "SecureRandom.uuid",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    },
                },
            }

        authcreds = None

        if request.user.id != None:
            request = request.user
        else:
            request = user

        if Google.auth_token_user_exists(request):
            authcreds = Credentials.from_authorized_user_file(
                Google.auth_token_user_exists(request),
                Google.SCOPES,
            )
        from google_auth_oauthlib.flow import InstalledAppFlow

        # If there are no (valid) credentials available, let the user log in.
        if not authcreds or not authcreds.valid:
            if authcreds and authcreds.expired and authcreds.refresh_token:
                authcreds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json", Google.SCOPES
                )
                authcreds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(
                Google.auth_token_path(request),
                "w",
            ) as token:
                token.write(authcreds.to_json())
        try:
            service = build("calendar", "v3", credentials=authcreds)
            event_info = (
                service.events()
                .insert(
                    calendarId="primary",
                    body=event_info,
                    conferenceDataVersion=1,
                    sendNotifications=True,
                    sendUpdates="all",
                )
                .execute()
            )
            join_url = event_info.get("hangoutLink", None)
            calendar_id = event_info.get("id", None)
        except HttpError as error:
            pass

    # Outlook AddEvent
    elif outlook_return_details.objects.filter(client_id=user).exists():
        if "id" in request.POST:
            event = request.POST["id"]
            event = Event_scheduler.objects.get(id=event)
            title = event.event_name
            timezone = request.POST["timezone"]
        if "date" in request.POST:
            date = request.POST["date"]
        if "time" in request.POST:
            time = request.POST["time"]
        showas = "Busy"
        if request.user.id == None:
            request = event.emp_id
            event_type = event.event_type
            if event_type == "On-site Interview" or event_type == "Phone Interview":
                isOnlineMeeting = True
                title = title + " " + "(" + event_type + ")" + " "
                title = titleConvertion(title, time, date, can_id, website=True)
            else:
                title = titleConvertion(title, time, date, can_id, website=True)
                isOnlineMeeting = True
        refresh_token = Outlook.get_token_from_refresh_token(request, user_id=request)
        with open(
            Outlook.auth_token_path(request),
            "r",
        ) as f:
            temp2 = json.load(f)
        if date and time and timezone:
            starttime, endtime = convert_to_datetime_with_timezone(date, time, timezone)
        if title and starttime and endtime:
            attendees = []
            website_email = website_userinfo.objects.get(id=can_id.id).email
            attendees.append(website_email)
            event_info = outlook_create_event(
                temp2["access_token"],
                title,
                str(starttime),
                str(endtime),
                isOnlineMeeting,
                showas,
                attendees=json.dumps(attendees),
                timezone=timezone,
                description=str(event.description),
            )
            if isOnlineMeeting == True:
                join_url = event_info["onlineMeeting"]["joinUrl"]
                calendar_id = event_info["id"]

    # Zita-Event Calevents
    if schedule_time and schedule_date and join_url and calendar_id:
        can_id = website_userinfo.objects.get(id=can_id.id)
        user = event.emp_id.id
        admin_id = UserHasComapny.objects.get(user=user).company
        s_time, e_time = slotter_convertion(schedule_time, schedule_date)
        if website_event.objects.filter(id=webevent.id).exists():
            interviews = Schedule_interview.objects.filter(event_id=event).values_list(
                "name_id__user_id__email", flat=True
            )
            interviews = list(interviews)
            meeting_interviews = interviews.append(can_id.email)
            meeting_interviews = interviews
            if meeting_interviews:
                meeting_interviews = ",".join(meeting_interviews)
            applicant = can_id.name
            interview_slot = website_event.objects.get(id=webevent.id)
            event_type = interview_slot.event_id.event_type
            emaill = list(
                Schedule_interview.objects.filter(event_id=event).values_list(
                    "name_id__user_id", flat=True
                )
            )
            email, alertmail = CalendarMailFun(emaill)
            if alertmail != []:
                integrate_calendar_invite_mail(
                    alertmail
                )  # Notification & Invite For Integration
            addon, validating = addon_interview_question(admin_id.recruiter_id)
            location = ""
            if event_type == "On-site Interview":
                location = event.location

            calevent = CalEvents.objects.create(
                applicant=applicant,
                s_time=s_time,
                e_time=e_time,
                jd="",
                event_type=event_type,
                timezone=timezone,
                private_notes="",
                interviewers=meeting_interviews,
                email=email,
                join_url=join_url,
                eventId=calendar_id,
                jd_id=0,
                org_id=user,
                cand_id=can_id.id,
                addon=addon,
                location=location,
            )
            interview_slot.interview_id = calevent
            interview_slot.join_url = join_url
            interview_slot.calendar_id = calendar_id
            interview_slot.save()

    # update on interview_id and join url
    website_event.objects.filter(id=webevent.id).update(
        calendar_id=calendar_id, join_url=join_url
    )
    context = {"success": True, "message": "Event Created Successfully"}
    return context
