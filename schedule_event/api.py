from django.utils.html import strip_tags
from calendarapp.utils import IntegrationMail, get_fullname
from jobs.views import admin_account
from django.db.models import (
    Case,
    When,
    Value,
    CharField,
    Subquery,
    OuterRef,
    IntegerField,
    BooleanField,
)
from django.db.models.functions import Concat
from login.tokens import account_activation_token
from login.apis import SignInAPI, user_details
from django.db.models import F, Count, Sum, Q
from jobs.api import *
from datetime import datetime, timedelta
from dateutil.parser import parse
from django.shortcuts import render, redirect
from login.views import account_activation_sent
from schedule_event.function import *
from schedule_event.views import (
    convert_to_different_timezone,
    convert_utc_to_timezone,
    slotterevents_verify,
)
from .models import *
import json
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import get_template
from email.mime.image import MIMEImage
import logging
from django.contrib.staticfiles import finders
from email.mime.image import MIMEImage
from django.http import JsonResponse
from django.contrib.staticfiles import finders
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from notifications.signals import notify

email_main = settings.EMAIL_HOST_USER
EMAIL_TO = settings.EMAIL_TO
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("jobs_api")
# Host_mail = settings.EMAIL_HOST_USER


def error_message(e):
    error = [
        {
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }
    ]
    return error


def logo_data(img):
    # image_data =['facebook.png','twitter.png','linkedin.png','youtube.png','new_zita.png']
    with open(finders.find("images/" + img), "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", img)
    return logo


def Daytime(value, id, name, day):
    if value != None:
        if name == "update":
            for index, i in enumerate(json.loads(value)):
                if Scheduled_Time.objects.filter(
                    event_id=id, day=day, index=index
                ).exists():
                    Scheduled_Time.objects.filter(
                        event_id=id, day=day, index=index
                    ).update(
                        day=day,
                        starttime=i["starttime"],
                        endtime=i["endtime"],
                    )
                else:
                    Scheduled_Time.objects.create(
                        day=day,
                        starttime=i["starttime"],
                        endtime=i["endtime"],
                        event_id=id,
                        index=index,
                    )
            delete_slot = [index for index, i in enumerate(json.loads(value))]
            delete_slot = (
                Scheduled_Time.objects.filter(event_id=id, day=day)
                .exclude(index__in=delete_slot)
                .delete()
            )
        else:
            for index, i in enumerate(json.loads(value)):
                Scheduled_Time.objects.create(
                    day=day,
                    starttime=i["starttime"],
                    endtime=i["endtime"],
                    event_id=id,
                    index=index,
                )
        return None
    else:
        delete_slot = Scheduled_Time.objects.filter(event_id=id, day=day).delete()
        pass


def add_Members(interviewer, user, event_id):
    delete_stages = (
        Schedule_interview.objects.filter(event_id=event_id)
        .exclude(name__user__in=json.loads(interviewer))
        .delete()
    )

    for i in json.loads(interviewer):
        x = User.objects.get(id=i)
        i = UserHasComapny.objects.get(user_id=i)
        if Schedule_interview.objects.filter(event_id=event_id, name=i).exists():
            pass
        else:
            Schedule_interview.objects.create(emp_id=user, event_id=event_id, name=i)


def convert(datee):
    check = {}
    grouped_data = {}
    for item in datee:
        day = item["day"]
        if day not in grouped_data:
            grouped_data[day] = []
        grouped_data[day].append(item)
    for day, items in grouped_data.items():
        check[day] = items
    return check


def onDuplicate(pk):
    from copy import deepcopy

    success = False
    try:
        record = Event_scheduler.objects.get(id=pk)
        # duplicate time
        time = Scheduled_Time.objects.filter(event_id=record)
        new_record = deepcopy(record)
        new_record.id = None
        new_record.save()
        duplicated_objects = []
        if time.count() != 0:
            for obj in time:
                obj.id = None
                obj.event_id = new_record
                duplicated_objects.append(obj)
        Scheduled_Time.objects.bulk_create(duplicated_objects)
        # duplicate interviewer
        interviewer = Schedule_interview.objects.filter(event_id=record)
        duplicate_schedule = []
        if interviewer.count() != 0:
            for obj in interviewer:
                obj.id = None
                obj.event_id = new_record
                duplicate_schedule.append(obj)
        Schedule_interview.objects.bulk_create(duplicate_schedule)
        availble = AvailbleSlot.objects.filter(event_id=record)
        duplicate_availble = []
        if interviewer.count() != 0:
            for obj in availble:
                obj.id = None
                obj.event_id = new_record
                duplicate_availble.append(obj)
        AvailbleSlot.objects.bulk_create(duplicate_availble)

        success = True
        return success
    except:
        raise ValueError("value error during duplicate")


def MailShare(user, candi_id, d, company):
    try:
        d["uid"] = urlsafe_base64_encode(force_bytes(candi_id.pk)).decode()
    except:
        d["uid"] = urlsafe_base64_encode(force_bytes(candi_id.pk))
    success = False
    recipient_email = candi_id.email
    htmly = get_template("event_share/schedule_event.html")
    subject, from_email, to = (
        "Invitation For Select Interview Time Schedule By " + company.company_name,
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


def EventMailSending(recipient_email, d):
    htmly = get_template("event_share/schedule_event_confirmation.html")
    subject, from_email, to = "Event Confirmation Details", email_main, recipient_email
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    confirmation = True
    msg.mixed_subtype = "related"
    image_data = ["twitter.png", "linkedin.png", "youtube.png", "new_zita_white.png"]
    for i in image_data:
        msg.attach(logo_data(i))
    if d["interviewer"] == True:
        if candidate_parsed_details.objects.filter(candidate_id=d["can_id"]).exists():
            resume_file_path = candidate_parsed_details.objects.get(
                candidate_id=d["can_id"]
            ).resume_file_path
            resume_file_path = base_dir + "/media/" + str(resume_file_path)
            msg.attach_file(resume_file_path)

    # --->
    # htmly = get_template('meeting_info.html')
    # interviewers = d.get('interviewers', '').split()  # Split the interviewers string into a list
    # unique_interviewers = list(set(interviewers))  # Use set to remove duplicates, then convert back to a list
    # d['interviewers'] = ','.join(unique_interviewers)
    # html_content = htmly.render(d)
    # msg = EmailMultiAlternatives(subject, html_content, from_email,to)
    # msg.attach_alternative(html_content, "text/html")
    # msg.mixed_subtype = 'related'
    # msg.attach_file(resume_file_path)
    try:
        msg.send()
    except:
        pass
    return confirmation


def time_slot(d):  
    slot_id = d["slot"].id
    slot = Interview_slot.objects.get(id=slot_id)
    can_id = slot.candidate_id.id
    if employer_pool.objects.filter(id=can_id, candidate_id__isnull=False).exists():
        emp = employer_pool.objects.get(id=can_id)
        appli_id = emp.candidate_id.application_id
        target = Personal_Info.objects.get(application_id=appli_id)
        s_event = slot.startevent
        jd_id = slot.jd_id
        from calendarapp.api import get_date_and_time
        date = get_date_and_time(s_event, "date")
        # time = get_date_and_time(s_event, "time")
        time_obj = datetime.strptime(s_event, "%Y-%m-%d %H:%M:%S")  
        t = time_obj.strftime("%I:%M %p") 
        data = f"Interview scheduled for {jd_id.job_title} on {date} at {t}. Please check your registered email's calendar."
        notify.send(
            jd_id.user_id,
            recipient=target.user_id,
            description="Schedule Event",
            verb=data,
            action_object=slot.jd_id,
        )
        return Response({"success": True})


def EventConfirmation(user, candi_id, event, company, d, attendee_user):
    attendee_user = list(attendee_user)
    if isinstance(candi_id.email, str):
        d["interviewer"] = False
        recipient_email = [candi_id.email]
        EventMailSending(recipient_email, d)
        time_slot(d)
    if isinstance(attendee_user, list):
        for i in attendee_user:
            d["interviewer"] = True
            candi_fullname = employer_pool.objects.filter(id=d["can_id"].id).values(
                "first_name", "last_name", "email"
            )[0]
            d["applicant"] = get_fullname(candi_fullname)
            user = User.objects.filter(email=i).values(
                "first_name", "last_name", "email"
            )[0]
            d["candi"] = get_fullname(user)
            requiredmail = IntegrationMail(i)
            recipient_email = [requiredmail]
            EventMailSending(recipient_email, d)
    return True


def slotavailble(pk, slot, name):
    if name == "update":  # update
        for i in json.loads(slot):
            for index, x in enumerate(i["slot"]):
                if AvailbleSlot.objects.filter(
                    event_id=pk, date=i["date"], index=index
                ).exists():
                    AvailbleSlot.objects.filter(
                        event_id=pk, date=i["date"], index=index
                    ).update(
                        date=i["date"],
                        starttime=x["starttime"],
                        endtime=x["endtime"],
                    )
                else:
                    # pk = Event_scheduler.objects.get(id =pk)
                    AvailbleSlot.objects.create(
                        date=i["date"],
                        starttime=x["starttime"],
                        endtime=x["endtime"],
                        event_id=pk,
                        index=index,
                    )
            timedelete = [index for index, i in enumerate(i["slot"])]
            timedelete = (
                AvailbleSlot.objects.filter(event_id=pk, date=i["date"])
                .exclude(index__in=timedelete)
                .delete()
            )
        delete_slot = [i["date"] for i in json.loads(slot)]
        delete_slot = (
            AvailbleSlot.objects.filter(event_id=pk)
            .exclude(date__in=delete_slot)
            .delete()
        )
        context = {"message": "Updated Event Successfully"}

        return Response(context)
    else:  # create
        # pk = Event_scheduler.objects.get(id=pk)
        for i in json.loads(slot):
            for index, x in enumerate(i["slot"]):
                AvailbleSlot.objects.create(
                    index=index,
                    event_id=pk,
                    date=i["date"],
                    starttime=x["starttime"],
                    endtime=x["endtime"],
                )
        context = {"message": "Created Event Successfully"}
    return None


def Event_Ids(user):
    company = UserHasComapny.objects.get(user_id=user).id
    event_ids = (
        Schedule_interview.objects.filter(name_id=company)
        .values_list("event_id", flat=True)
        .distinct()
    )
    # event_ids = []
    # event_ids.append(id)
    # if Event_scheduler.objects.filter(emp_id__in = admin).exists():
    #     event_ids = Event_scheduler.objects.filter(emp_id=id).values_list('id',flat=True)
    #     event_ids = event_ids.annotate(
    #         checking = Subquery(Schedule_interview.objects.filter(event_id=OuterRef('id')).values('event_id').annotate(count=Count('id'))[:1].values('count'),output_field=CharField())
    #         )
    #     event_ids = event_ids.filter(checking__gt=1).values_list('id',flat=True)

    return event_ids


from django.db.models.functions import Coalesce


class scheduler_dashboard(generics.GenericAPIView):

    def get(self, request):
        user_id = self.request.user
        try:
            if "pk" in self.request.GET:
                pk = self.request.GET["pk"]
                duplicate = self.request.GET.get("duplicate", None)
                sharelink = self.request.GET.get("sharelink", None)
                if pk and duplicate == None and sharelink == None:
                    if Event_scheduler.objects.filter(id=pk).exists():
                        if user_id.id == None:
                            user_id = Event_scheduler.objects.get(id=pk).emp_id
                        else:
                            user_id = user_id
                        data = (
                            Event_scheduler.objects.filter(id=pk)
                            .values()
                            .annotate(
                                company_name=Subquery(
                                    UserHasComapny.objects.filter(user=user_id).values(
                                        "company__company_name"
                                    )[:1]
                                ),
                                company_logo=Subquery(
                                    UserHasComapny.objects.filter(user=user_id).values(
                                        "company__logo"
                                    )[:1]
                                ),
                            )
                        )
                        interviewer = (
                            Schedule_interview.objects.filter(event_id=pk)
                            .values("id", "event_id", "name__user", "name__user__email")
                            .exclude(name__user=user_id)
                        )
                        interviewer = interviewer.annotate(
                            full_name=Concat(
                                "name__user__first_name",
                                Value(" "),
                                "name__user__last_name",
                                output_field=CharField(),
                            ),
                            google_calendar=Subquery(
                                google_return_details.objects.filter(
                                    client_id=OuterRef("name__user")
                                ).values("email")[:1]
                            ),
                            outlook_calendar=Subquery(
                                outlook_return_details.objects.filter(
                                    client_id=OuterRef("name__user")
                                ).values("email")[:1]
                            ),
                        )
                        datetime = convert(
                            Scheduled_Time.objects.filter(event_id=pk).values(
                                "day", "starttime", "endtime"
                            )
                        )
                        google = google_return_details.objects.filter(
                            client_id=user_id
                        ).exists()
                        if google:
                            google = google_return_details.objects.get(
                                client_id=user_id
                            ).email
                        else:
                            google = False
                        outlook = outlook_return_details.objects.filter(
                            client_id=user_id
                        ).exists()
                        if outlook:
                            outlook = outlook_return_details.objects.get(
                                client_id=user_id
                            ).email
                        else:
                            outlook = False
                        context = {
                            "suceess": True,
                            "data": data,
                            "interviewer": interviewer,
                            "datetime": datetime,
                            "google": google,
                            "outlook": outlook,
                        }
                    else:
                        data = []
                        interviewer = []
                        datetime = {}
                        google = False
                        outlook = False
                        context = {
                            "suceess": True,
                            "data": data,
                            "interviewer": interviewer,
                            "datetime": datetime,
                            "google": google,
                            "outlook": outlook,
                        }
                    return Response(context)
                if pk and duplicate:
                    messgae = onDuplicate(pk)
                    if messgae == True:
                        return Response({"message": "Duplicated Successfully"})

                if pk and sharelink:
                    from django.contrib.sites.shortcuts import get_current_site

                    current_site = get_current_site(request)
                    domain = settings.CLIENT_URL
                    event = Event_scheduler.objects.get(id=pk)
                    jd_id = self.request.GET.get("jd_id", None)
                    for i in json.loads(sharelink):
                        candi_id = employer_pool.objects.get(id=i)
                        company = UserHasComapny.objects.get(user=user_id).company
                        d = {
                            "user": user_id,
                            "eventid": self.request.GET["pk"],
                            "candi": candi_id,
                            "event": event,
                            "company_name": company,
                            "domain": domain,
                            "jd_id": jd_id,
                        }
                        try:
                            d["uid"] = urlsafe_base64_encode(
                                force_bytes(candi_id.pk)
                            ).decode()
                        except:
                            d["uid"] = urlsafe_base64_encode(force_bytes(candi_id.pk))
                        # url = f"http://{d['domain']}/schedule_event/{d['uid']}"
                        success = MailShare(user_id, candi_id, d, company)
                        slot_notify(d)
                    if success == True:
                        return Response({"message": "Event Shared Successfully"})
                    else:
                        raise ValueError("does not send Mail")

            else:
                admin_id, updated_by = admin_account(request)
                id__list = Event_Ids(user_id)
                data = Event_scheduler.objects.filter(id__in=id__list).values()
                candidate = employer_pool.objects.filter(
                    client_id=admin_id, first_name__isnull=False, email__isnull=False
                ).values("id", "candidate_id__application_id", "email")
                candidate = candidate.annotate(
                    type=Case(
                        When(candidate_id__isnull=True, then=Value("Candidate")),
                        default=Value("Applicant", output_field=CharField()),
                    ),
                    full_name=Concat(
                        "first_name", Value(" "), "last_name", output_field=CharField()
                    ),
                )
                interviewer = Schedule_interview.objects.filter(
                    event_id__in=id__list
                ).values("id", "event_id", "name_id")
                interviewer = interviewer.annotate(
                    full_name=Concat(
                        "name__user__first_name",
                        Value(" "),
                        "name__user__last_name",
                        output_field=CharField(),
                    )
                )
                company = UserHasComapny.objects.get(user=user_id).company
                teammembers = (
                    UserHasComapny.objects.filter(
                        company=company, user_id__is_active=True
                    )
                    .values("id", "user", "user__first_name", "user__last_name")
                    .exclude(user=user_id)
                )
                teammembers = teammembers.annotate(
                    full_name=Concat(
                        "user__first_name",
                        Value(" "),
                        "user__last_name",
                        output_field=CharField(),
                    ),
                    google_calendar=Coalesce(
                        Subquery(
                            google_return_details.objects.filter(
                                client_id=OuterRef("user_id")
                            ).values("client_id")[:1],
                            output_field=IntegerField(),
                        ),
                        Value(None),
                    ),
                    outlook_calendar=Coalesce(
                        Subquery(
                            outlook_return_details.objects.filter(
                                client_id=OuterRef("user_id")
                            ).values("client_id")[:1],
                            output_field=IntegerField(),
                        ),
                        Value(None),
                    ),
                )
                google = google_return_details.objects.filter(
                    client_id=user_id
                ).exists()
                if google:
                    google = True
                else:
                    google = False
                outlook = outlook_return_details.objects.filter(
                    client_id=user_id
                ).exists()
                if outlook:
                    outlook = True
                else:
                    outlook = False
                context = {
                    "suceess": False,
                    "data": data,
                    "interviewer": interviewer,
                    "shareLink": candidate,
                    "addmembers": teammembers,
                    "google": google,
                    "outlook": outlook,
                }
                return Response(context)
        except (ValueError, KeyError, AssertionError) as e:
            error = error_message(e)
            return Response(error, status=400)

    def post(self, request):
        user_id = self.request.user
        try:
            checking = self.request.POST
            event_name = self.request.POST["event_name"].strip()
            event_type = self.request.POST["event_type"].strip()
            company = UserHasComapny.objects.get(user=user_id)
            if "location" in self.request.POST:
                location = self.request.POST["location"].strip()
            else:
                location = None
            startdate = self.request.POST["startdate"].strip()
            days = self.request.POST["days"].strip()
            enddate = self.request.POST["enddate"].strip()
            duration = self.request.POST["duration"].strip()
            timezone = self.request.POST["timezone"].strip()
            interviewer = self.request.POST["interviewer"].strip()
            interviewer = interviewer
            organiser = User.objects.get(username=user_id)
            organiser = f"{organiser.first_name} {organiser.last_name}"

            if "sunday" in self.request.POST:
                sunday = self.request.POST["sunday"].strip()
            else:
                sunday = None
            if "monday" in self.request.POST:
                monday = self.request.POST["monday"].strip()
            else:
                monday = None
            if "tuesday" in self.request.POST:
                tuesday = self.request.POST["tuesday"].strip()
            else:
                tuesday = None
            if "wednesday" in self.request.POST:
                wednesday = self.request.POST["wednesday"].strip()
            else:
                wednesday = None
            if "thursday" in self.request.POST:
                thursday = self.request.POST["thursday"].strip()
            else:
                thursday = None
            if "friday" in self.request.POST:
                friday = self.request.POST["friday"].strip()
            else:
                friday = None
            if "saturday" in self.request.POST:
                saturday = self.request.POST["saturday"].strip()
            else:
                saturday = None
            if "slot" in self.request.POST:
                slot = self.request.POST["slot"]
            else:
                slot = None
            times_zone_display = self.request.POST["times_zone_display"].strip()
            description = self.request.POST["description"].strip()

            if (
                event_name
                and event_type
                and days
                and startdate
                and enddate
                and duration
                and timezone
                and times_zone_display
                and description
                and interviewer
            ):
                if "pk" in self.request.POST:  # update
                    pk = self.request.POST["pk"]
                    data = Event_scheduler.objects.filter(id=pk).update(
                        emp_id=user_id,
                        company=company,
                        event_name=event_name,
                        event_type=event_type,
                        location=location,
                        # daterange=dateRange,
                        days=days,
                        interviewer=organiser,
                        startdate=startdate,
                        enddate=enddate,
                        duration=duration,
                        times_zone=timezone,
                        description=description,
                        times_zone_display=times_zone_display,
                    )
                    data = Event_scheduler.objects.get(id=pk)
                    Daytime(sunday, data, "update", "sunday")
                    Daytime(monday, data, "update", "monday")
                    Daytime(tuesday, data, "update", "tuesday")
                    Daytime(wednesday, data, "update", "wednesday"),
                    Daytime(thursday, data, "update", "thursday")
                    Daytime(friday, data, "update", "friday")
                    Daytime(saturday, data, "update", "saturday")
                    context = {"message": "Updated Event Successfully"}
                    add_Members(interviewer, user_id, data)
                    slotavailble(data, slot, "update")
                    return Response(context)
                else:  # create
                    data = Event_scheduler.objects.create(
                        emp_id=user_id,
                        company=company,
                        event_name=event_name,
                        event_type=event_type,
                        # daterange=dateRange,
                        days=days,
                        location=location,
                        interviewer=organiser,
                        startdate=startdate,
                        enddate=enddate,
                        duration=duration,
                        times_zone=timezone,
                        description=description,
                        times_zone_display=times_zone_display,
                    )
                    Daytime(sunday, data, "create", "sunday")
                    Daytime(monday, data, "create", "monday")
                    Daytime(tuesday, data, "create", "tuesday")
                    Daytime(wednesday, data, "create", "wednesday")
                    Daytime(thursday, data, "create", "thursday")
                    Daytime(friday, data, "create", "friday")
                    Daytime(saturday, data, "create", "saturday")
                    add_Members(interviewer, user_id, data)
                    slotavailble(data, slot, "create")
                    context = {"message": "Created Event Successfully"}
                    return Response(context)
            else:
                raise ValueError("One or more required value are missing")
        except (KeyError, ValueError, Exception) as e:
            error = error_message(e)
            return Response(error, status=400)

    def delete(self, request):
        user_id = self.request.user
        try:
            if "pk" in self.request.GET:
                pk = self.request.GET["pk"]
                valid = Event_scheduler.objects.filter(emp_id=user_id, id=pk).exists()
                if valid:
                    Event_scheduler.objects.filter(id=pk).delete()
                    Interview_slot.objects.filter(event_id=pk).delete()
                    Scheduled_Time.objects.filter(event_id=pk).delete()
                    AvailbleSlot.objects.filter(event_id=pk).delete()
                    message = pk + "-Deleted Successfully"
                    context = {"message": message}
                    return Response(context)
                else:
                    raise ValueError("already deleted")
            else:
                raise KeyError("pk doesnot exist")
        except (KeyError, ValueError) as e:
            error = error_message(e)
            return Response(error, status=400)


def event_calender(date, time):
    date_str = date
    time_range = time
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
    start_time, end_time = time_range.split(" - ")
    start_datetime = datetime.strptime(start_time, "%I:%M %p")
    start_datetime = datetime.combine(date_obj.date(), start_datetime.time())
    end_datetime = datetime.strptime(end_time, "%I:%M %p")
    end_datetime = datetime.combine(date_obj.date(), end_datetime.time())
    return start_datetime, end_datetime


def slot_notify(d):
    jd_id = JD_form.objects.get(id=d["jd_id"])  # must be id
    can = d["candi"]
    if employer_pool.objects.filter(id=can.id, candidate_id__isnull=False).exists():
        emp = employer_pool.objects.get(id=can.id)
        appli_id = emp.candidate_id.application_id
        target = Personal_Info.objects.get(application_id=appli_id)
        data = f"You have received the interview slots for {jd_id.job_title}.Please check your registered email inbox."
        notify.send(
            jd_id.user_id,
            recipient=target.user_id,
            description="Schedule",
            verb=data,
            action_object=jd_id,
        )
        return Response({"success": True})


class slotter_interview(generics.GenericAPIView):
    def get(self, request, uidb64):
        user = self.request.user
        user_id = self.request.user

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            if "date" in self.request.GET:
                date = self.request.GET["date"].strip()
            else:
                date = None
            if "time" in self.request.GET:
                time = self.request.GET["time"].strip()
            else:
                time = None
            if "event_id" in self.request.GET:
                event_id = self.request.GET["event_id"].strip()
            else:
                event_id = None
            if Event_scheduler.objects.filter(id=event_id).exists():
                if user.id == None:
                    user = Event_scheduler.objects.get(id=event_id).emp_id
                else:
                    user = user
                candi_id = employer_pool.objects.get(id=uid)
                jd_id = self.request.GET.get("jd_id", None)
                if Interview_slot.objects.filter(
                    event_id=event_id, candidate_id=candi_id, jd_id=jd_id
                ).exists():
                    user = Event_scheduler.objects.get(id=event_id).emp_id
                    data = Interview_slot.objects.filter(
                        event_id=event_id, candidate_id=candi_id, jd_id=jd_id
                    ).values(
                        "event_id",
                        "event_id__event_name",
                        "date",
                        "time",
                        "candidate_id__first_name",
                        "candidate_id__email",
                    )
                    interviewer = Schedule_interview.objects.filter(
                        event_id=event_id
                    ).values()
                    interviewer = interviewer.annotate(
                        full_name=Concat(
                            "name__user__first_name",
                            Value(" "),
                            "name__user__last_name",
                            output_field=CharField(),
                        )
                    )
                    if candi_id.last_name != None:
                        candidate_full_name = (
                            f"{candi_id.first_name} {candi_id.last_name}"
                        )
                    else:
                        candidate_full_name = f"{candi_id.first_name}"
                    return Response(
                        {
                            "slotterdata": data,
                            "slotmembers": interviewer,
                            "success": True,
                            "candidate_name": candidate_full_name,
                            "message": "dashboard",
                            "can_id": candi_id.id,
                        }
                    )
                elif date and time and event_id:
                    startevent, endevent = event_calender(date, time)
                    event_id = Event_scheduler.objects.get(id=event_id)
                    jd_id = JD_form.objects.get(id=jd_id)
                    success = Interview_slot.objects.create(
                        date=date,
                        time=time,
                        event_id=event_id,
                        candidate_id=candi_id,
                        email=candi_id.email,
                        is_active=True,
                        startevent=startevent,
                        endevent=endevent,
                        jd_id=jd_id,
                    )
                    if success:
                        sharelink = Schedule_interview.objects.filter(
                            event_id=event_id
                        ).values("name__user", "name__user", "name__user__email")
                        sharelink = sharelink.annotate(
                            full_name=Concat(
                                "name__user__first_name",
                                Value(" "),
                                "name__user__last_name",
                                output_field=CharField(),
                            )
                        )
                        for i in sharelink:
                            name_user = i["full_name"]
                            event_name = event_id.event_name
                            email = i["name__user__email"]
                            data = f"{user.username.title()} has invited you to an event for {event_name.title()}"
                            if i["name__user"] != user.id:
                                recipient_user = User.objects.get(id=i["name__user"])
                                notify.send(
                                    sender=user,
                                    recipient=recipient_user,
                                    description="event",
                                    verb=data,
                                    target=event_id,
                                )
                    return Response({"message": "Event Scheduled Successfully"})
                else:
                    if candi_id.last_name != None:
                        candidate_full_name = (
                            f"{candi_id.first_name} {candi_id.last_name}"
                        )
                    else:
                        candidate_full_name = f"{candi_id.first_name}"
                    return Response(
                        {
                            "slotterdata": [],
                            "success": False,
                            "slotmembers": [],
                            "candidate_name": candidate_full_name,
                            "can_id": candi_id.id,
                        }
                    )

            else:
                return Response(
                    {
                        "slotterdata": [],
                        "success": False,
                        "slotmembers": [],
                        "candidate_name": None,
                        "can_id": None,
                    }
                )

        except (KeyError, ValueError) as e:
            error = error_message(e)
            return Response(error, status=400)

    def post(self, request):
        user_id = self.request.user
        try:
            checking = self.request.POST
            required_keys = ["pk", "date", "time"]
            if not all(key in checking for key in required_keys):
                raise KeyError("One or more required keys are missing")
            pk = self.request.POST["pk"].strip()
            pk = Event_scheduler.objects.get(id=pk)
            if user_id.id == None:
                user_id = pk.emp_id
            else:
                user_id = user_id
            date = self.request.POST["date"].strip()
            time = self.request.POST["time"].strip()
            if pk and date and time:
                data = Interview_slot.objects.create(
                    event_id=pk,
                    date=date,
                    time=time,
                )
                sharelink = Schedule_interview.objects.filter(event_id=pk).values(
                    "name__user", "name__user", "name__user__email"
                )
                sharelink = sharelink.annotate(
                    full_name=Concat(
                        "name__user__first_name",
                        Value(" "),
                        "name__user__last_name",
                        output_field=CharField(),
                    )
                )
                for i in sharelink:
                    name_user = i["full_name"]
                    email = i["name__user__email"]
                    data = f"{user_id.username.title()} has invited you to an event: {name_user.title()}"
                    recipient_user = User.objects.get(email=email)
                    notify.send(sender=user_id, recipient=recipient_user, verb=data)

        except (KeyError, ValueError) as e:
            error = error_message(e)
            return Response(error, status=400)

    def delete(self, request):
        try:
            if "pk" in self.request.GET:
                pk = self.request.GET["pk"]
                if Interview_slot.objects.filter(interview_id=pk).exists():
                    Interview_slot.objects.filter(interview_id=pk).delete()
                    context = {"success": True}
                    return Response(context)
            else:
                raise KeyError("pk doesnot exist")
        except (KeyError, ValueError) as e:
            error = error_message(e)
            return Response(error, status=400)


def timezoneconvert(datee):
    check = {}
    grouped_data = {}
    for item in datee:
        date = item["date"]
        starttime = item["starttime"]
        endtime = item["endtime"]
        if date not in grouped_data:
            grouped_data[date] = []
        grouped_data[date].append({"starttime": starttime, "endtime": endtime})
    for date, items in grouped_data.items():
        check[date] = items
    return check


class slotter_availble(generics.GenericAPIView):
    def get(self, request):
        pk = self.request.GET.get("pk", None)
        if Event_scheduler.objects.filter(id=pk).exists():
            data = timezoneconvert(AvailbleSlot.objects.filter(event_id=pk).values())
            context = {"availbleslot": data}
            return Response(context)
        else:
            availbleslot = {}
            return Response({"availbleslot": availbleslot})


class calender_scheduled_events(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from login.models import Profile

        request = self.request
        user = request.user
        com_name = UserHasComapny.objects.get(user_id=user).company
        name = UserHasComapny.objects.filter(company_id=com_name).values("id")
        name1 = UserHasComapny.objects.filter(company_id=com_name).values("id")
        interviewer = Schedule_interview.objects.filter(name__in=name).values(
            "id", "event_id", "name_id"
        )
        interviewer = interviewer.annotate(
            full_name=Concat(
                "name__user__first_name",
                Value(" "),
                "name__user__last_name",
                output_field=CharField(),
            ),
        )
        interviewer = interviewer.annotate(
            profile=Subquery(Profile.objects.filter(user__in=name)[:1].values("image"))
        )
        event_id = Schedule_interview.objects.filter(name__in=name).values("event_id")
        teammembers = UserHasComapny.objects.filter(
            company=com_name, user_id__is_active=True
        ).values("id", "user", "user__first_name", "user__last_name")
        teammembers = teammembers.annotate(
            full_name=Concat(
                "user__first_name",
                Value(" "),
                "user__last_name",
                output_field=CharField(),
            ),
        )
        gmail_subquery = google_return_details.objects.filter(
            client_id=OuterRef("user_id")
        )
        outlook_subquery = outlook_return_details.objects.filter(
            client_id=OuterRef("user_id")
        )
        teammembers = teammembers.annotate(
            gmail=Subquery(gmail_subquery.values("email")[:1]),
            outlookmail=Subquery(outlook_subquery.values("email")[:1]),
        )
        teammembers = teammembers.annotate(
            name_id=Subquery(
                Schedule_interview.objects.filter(name__user=user)[:1].values("name")
            )
        )
        company_members = UserHasComapny.objects.filter(
            company_id=com_name
        ).values_list("user_id")
        final_email = User.objects.filter(id__in=company_members).values(
            "id", "first_name", "last_name"
        )
        final_email = final_email.annotate(
            full_name=Concat(
                "first_name", Value(" "), "last_name", output_field=CharField()
            )
        )
        for i in list(final_email):
            id = i["id"]
            user_mail = User.objects.get(id=id).email
            if google_return_details.objects.filter(client_id=id).exists():
                user_mail = google_return_details.objects.get(client_id=id).email
            elif outlook_return_details.objects.filter(client_id=id).exists():
                user_mail = outlook_return_details.objects.get(client_id=id).email
            i["email"] = user_mail
        event = request.GET["event"]
        if event == "True":
            my_events = UserHasComapny.objects.filter(user=user).values("id")
            event_id = Schedule_interview.objects.filter(name__in=my_events).values(
                "event_id"
            )
            event_id = Event_scheduler.objects.filter(id__in=event_id).values("id")
            user_mail = User.objects.get(username=user).email
            if google_return_details.objects.filter(client_id=user).exists():
                user_mail = google_return_details.objects.get(client_id=user).email
            elif outlook_return_details.objects.filter(client_id=user).exists():
                user_mail = outlook_return_details.objects.get(client_id=user).email
            calevents_event_id = list(
                CalEvents.objects.filter(email__contains=user_mail).values_list(
                    "eventId", flat=True
                )
            )
        else:
            if "other_user" in request.GET:
                other_user = json.loads(self.request.GET["other_user"])
                namedata = UserHasComapny.objects.filter(user_id__in=other_user).values(
                    "id"
                )
                event_id = Schedule_interview.objects.filter(name__in=namedata).values(
                    "event_id"
                )
                # other_user =list(User.objects.filter(id__in=other_user).values_list('email',flat=True))
                calevents_event_id = []
                for i in other_user:
                    user_mail = User.objects.get(id=i).email
                    if google_return_details.objects.filter(client_id=i).exists():
                        user_mail = google_return_details.objects.get(client_id=i).email
                    elif outlook_return_details.objects.filter(client_id=i).exists():
                        user_mail = outlook_return_details.objects.get(
                            client_id=i
                        ).email
                    cal_list = CalEvents.objects.filter(
                        email__contains=user_mail
                    ).values_list("eventId", flat=True)
                    calevents_event_id.extend(cal_list)
            else:
                event_id = Schedule_interview.objects.filter(name__in=name).values(
                    "event_id"
                )
                other_user = ",".join(
                    list(
                        User.objects.filter(id__in=name1).values_list(
                            "email", flat=True
                        )
                    )
                )
                calevents_event_id = CalEvents.objects.filter(
                    email__contains=other_user
                ).values("eventId")
        given_time_zone = request.GET["timeZone"]
        if "date" in request.GET:
            date = request.GET["date"]
            desired_datetime_format = f"%Y-%m-%dT%H:%M:%S.%fZ"
            desired_date = datetime.strptime(date, f"%d/%m/%Y").replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            calevents_start_time = desired_date + timedelta(hours=0, minutes=0)
            calevents_start_time = (
                calevents_start_time.strftime(desired_datetime_format)
            ).replace("z", "")
            calevents_end_time = desired_date + timedelta(hours=23, minutes=59)
            calevents_end_time = (
                calevents_end_time.strftime(desired_datetime_format)
            ).replace("z", "")
            events = Interview_slot.objects.filter(
                event_id__in=event_id, date=date
            ).values(
                "id",
                "event_id",
                "date",
                "time",
                "event_id__duration",
                "event_id__event_name",
                "event_id__event_type",
                "candidate_id",
                "event_id__interviewer",
                "startevent",
                "join_url",
                "event_id__emp_id",
            )
            events = events.annotate(
                candidate_name=Concat(
                    "candidate_id__first_name",
                    Value(" "),
                    "candidate_id__last_name",
                    output_field=CharField(),
                )
            )
            calevents_events = []
            org_name = []
            org_name_final = []
            if event == "True":
                for c in calevents_event_id:
                    c = CalEvents.objects.filter(eventId=c).last().eventId
                    try:
                        if CalEvents.objects.filter(eventId=c).exists():
                            time_zone = (
                                CalEvents.objects.filter(eventId=c).last().timezone
                            )
                            if time_zone == given_time_zone:
                                calevents_start_times = calevents_start_time
                                calevents_end_times = calevents_end_time
                            else:
                                calevents_start_times = convert_to_different_timezone(
                                    calevents_start_time,
                                    given_time_zone,
                                    time_zone,
                                )
                                calevents_end_times = convert_to_different_timezone(
                                    calevents_end_time, given_time_zone, time_zone
                                )
                    except Exception as e:
                        calevents_start_times = calevents_start_time
                        calevents_end_times = calevents_end_time
                        pass
                    if CalEvents.objects.filter(
                        eventId=c,
                        s_time__gt=calevents_start_times,
                        s_time__lt=calevents_end_times,
                    ).exists():
                        cal_event = list(
                            CalEvents.objects.filter(
                                eventId=c,
                                s_time__gt=calevents_start_times,
                                s_time__lt=calevents_end_times,
                            ).values(
                                "applicant",
                                "jd",
                                "notes",
                                "location",
                                "event_type",
                                "timezone",
                                "private_notes",
                                "interviewers",
                                "eventId",
                                "jd_id",
                                "cand_id",
                                "org_id",
                                "join_url",
                                "extra_notes",
                                "interviewer_notes",
                                "email",
                                "addon",
                            )
                        )
                        org_id = CalEvents.objects.get(eventId=c).org_id
                        org_name = (
                            User.objects.get(id=org_id).first_name
                            + " "
                            + User.objects.get(id=org_id).last_name
                        )
                        time_zone = CalEvents.objects.get(eventId=c).timezone
                        if given_time_zone != time_zone:
                            cal_event[0]["s_time"] = convert_to_different_timezone(
                                CalEvents.objects.get(eventId=c).s_time,
                                given_time_zone,
                                time_zone,
                            )
                            cal_event[0]["e_time"] = convert_to_different_timezone(
                                CalEvents.objects.get(eventId=c).e_time,
                                given_time_zone,
                                time_zone,
                            )
                            cal_event[0]["slotter_event"] = (
                                Interview_slot.objects.filter(
                                    interview_id__eventId=c
                                ).exists()
                            )
                            if cal_event[0]["slotter_event"] == True:
                                cal_event[0]["slotter_title"] = (
                                    Interview_slot.objects.get(
                                        interview_id__eventId=c
                                    ).event_id.event_name
                                )
                                cal_event[0]["join_link"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c,
                                        event_id__event_type__in=[
                                            "Google Hangouts/Meet",
                                            "Microsoft Teams",
                                        ],
                                    ).exists()
                                )
                        else:
                            cal_event[0]["s_time"] = CalEvents.objects.get(
                                eventId=c
                            ).s_time
                            cal_event[0]["e_time"] = CalEvents.objects.get(
                                eventId=c
                            ).e_time
                            cal_event[0]["slotter_event"] = (
                                Interview_slot.objects.filter(
                                    interview_id__eventId=c
                                ).exists()
                            )
                            if cal_event[0]["slotter_event"] == True:
                                cal_event[0]["slotter_title"] = (
                                    Interview_slot.objects.get(
                                        interview_id__eventId=c
                                    ).event_id.event_name
                                )
                                cal_event[0]["join_link"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c,
                                        event_id__event_type__in=[
                                            "Google Hangouts/Meet",
                                            "Microsoft Teams",
                                        ],
                                    ).exists()
                                )
                        cal_event[0]["org_name"] = org_name
                        calevents_events.append(cal_event[0])
            else:
                for c in set(calevents_event_id):
                    c = CalEvents.objects.filter(eventId=c).last().eventId
                    if CalEvents.objects.filter(eventId=c).exists():
                        try:
                            time_zone = (
                                CalEvents.objects.filter(eventId=c).last().timezone
                            )
                            if time_zone == given_time_zone:
                                calevents_start_times = calevents_start_time
                                calevents_end_times = calevents_end_time
                            else:
                                calevents_start_times = convert_to_different_timezone(
                                    calevents_start_time,
                                    given_time_zone,
                                    time_zone,
                                )
                                calevents_end_times = convert_to_different_timezone(
                                    calevents_end_time, given_time_zone, time_zone
                                )
                        except Exception as e:
                            calevents_start_times = calevents_start_time
                            calevents_end_times = calevents_end_time
                            pass
                    if CalEvents.objects.filter(
                        eventId=c,
                        s_time__gt=calevents_start_times,
                        s_time__lt=calevents_end_times,
                    ).exists():
                        cal_event = list(
                            CalEvents.objects.filter(
                                eventId=c,
                                s_time__gt=calevents_start_times,
                                s_time__lt=calevents_end_times,
                            ).values(
                                "applicant",
                                "jd",
                                "notes",
                                "location",
                                "event_type",
                                "timezone",
                                "private_notes",
                                "interviewers",
                                "eventId",
                                "jd_id",
                                "cand_id",
                                "org_id",
                                "join_url",
                                "extra_notes",
                                "interviewer_notes",
                                "email",
                                "addon",
                            )
                        )
                        org_id = CalEvents.objects.get(eventId=c).org_id
                        org_name = (
                            User.objects.get(id=org_id).first_name
                            + " "
                            + User.objects.get(id=org_id).last_name
                        )
                        time_zone = CalEvents.objects.get(eventId=c).timezone
                        if given_time_zone != time_zone:
                            cal_event[0]["s_time"] = convert_to_different_timezone(
                                CalEvents.objects.get(eventId=c).s_time,
                                given_time_zone,
                                time_zone,
                            )
                            cal_event[0]["e_time"] = convert_to_different_timezone(
                                CalEvents.objects.get(eventId=c).e_time,
                                given_time_zone,
                                time_zone,
                            )
                            cal_event[0]["slotter_event"] = (
                                Interview_slot.objects.filter(
                                    interview_id__eventId=c
                                ).exists()
                            )
                            if cal_event[0]["slotter_event"] == True:
                                cal_event[0]["slotter_title"] = (
                                    Interview_slot.objects.get(
                                        interview_id__eventId=c
                                    ).event_id.event_name
                                )
                                cal_event[0]["join_link"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c,
                                        event_id__event_type__in=[
                                            "Google Hangouts/Meet",
                                            "Microsoft Teams",
                                        ],
                                    ).exists()
                                )
                        else:
                            cal_event[0]["s_time"] = CalEvents.objects.get(
                                eventId=c
                            ).s_time
                            cal_event[0]["e_time"] = CalEvents.objects.get(
                                eventId=c
                            ).e_time
                            cal_event[0]["slotter_event"] = (
                                Interview_slot.objects.filter(
                                    interview_id__eventId=c
                                ).exists()
                            )
                            if cal_event[0]["slotter_event"] == True:
                                cal_event[0]["slotter_title"] = (
                                    Interview_slot.objects.get(
                                        interview_id__eventId=c
                                    ).event_id.event_name
                                )
                                cal_event[0]["join_link"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c,
                                        event_id__event_type__in=[
                                            "Google Hangouts/Meet",
                                            "Microsoft Teams",
                                        ],
                                    ).exists()
                                )
                        cal_event[0]["org_name"] = org_name
                        calevents_events.append(cal_event[0])
                        org_id = CalEvents.objects.filter(eventId=c).values("org_id")
                        org_name = User.objects.filter(id__in=org_id).values(
                            "id", "first_name", "last_name"
                        )
                        org_name = org_name.annotate(
                            full_name=Concat(
                                "first_name",
                                Value(" "),
                                "last_name",
                                output_field=CharField(),
                            )
                        )
                        org_name_final.append(
                            org_name.values(
                                "id", "first_name", "last_name", "full_name", "email"
                            )[0]
                        )
            context = {
                "event": events,
                "interviewer": interviewer,
                "teammembers": teammembers,
                "calevents_events": calevents_events,
                "org_name": org_name_final,
                "calevents_interviewer": final_email,
            }
        else:
            current_date_time = datetime.now()
            date_time = str(current_date_time)

            calevents_datetime_format = f"%Y-%m-%dT%H:%M:%S.%fZ"
            parsed_datetime = datetime.strptime(date_time, f"%Y-%m-%d %H:%M:%S.%f")
            calevents_datetime_str = parsed_datetime.strftime(calevents_datetime_format)
            upcoming_event = Interview_slot.objects.filter(
                event_id__in=event_id
            ).values(
                "id",
                "event_id",
                "date",
                "time",
                "event_id__duration",
                "event_id__event_name",
                "event_id__event_type",
                "candidate_id",
                "event_id__interviewer",
                "startevent",
                "event_id__emp_id",
                "join_url",
                "endevent",
            )
            upcoming_event = upcoming_event.annotate(
                candidate_name=Concat(
                    "candidate_id__first_name",
                    Value(" "),
                    "candidate_id__last_name",
                    output_field=CharField(),
                )
            )
            changeslotterdata = slotterevents_verify(
                upcoming_event, calevents_datetime_str
            )
            upcoming_event = changeslotterdata["upcoming"]
            past_event = Interview_slot.objects.filter(
                event_id__in=event_id, startevent__lte=current_date_time
            ).values(
                "id",
                "event_id",
                "date",
                "time",
                "event_id__duration",
                "event_id__event_name",
                "event_id__event_type",
                "candidate_id",
                "event_id__interviewer",
                "startevent",
                "event_id__emp_id",
                "join_url",
            )
            past_event = past_event.annotate(
                candidate_name=Concat(
                    "candidate_id__first_name",
                    Value(" "),
                    "candidate_id__last_name",
                    output_field=CharField(),
                )
            )
            past_event = changeslotterdata["past"]
            calevents_upcoming_event = []
            calevents_past_event = []
            org_name_final = []
            org_id_set = set()
            if event == "True":
                for c in calevents_event_id:
                    c = CalEvents.objects.filter(eventId=c).last().eventId
                    if CalEvents.objects.filter(eventId=c).exists():
                        try:
                            time_zone = CalEvents.objects.get(eventId=c).timezone
                            calevents_datetime_strs = convert_utc_to_timezone(
                                calevents_datetime_str, time_zone
                            )
                        except:
                            calevents_datetime_strs = calevents_datetime_str
                            pass
                        if CalEvents.objects.filter(
                            s_time__gt=calevents_datetime_strs, eventId=c
                        ).exists():
                            calevents_upcoming_event1 = list(
                                CalEvents.objects.filter(
                                    s_time__gt=calevents_datetime_strs, eventId=c
                                ).values(
                                    "applicant",
                                    "jd",
                                    "notes",
                                    "location",
                                    "event_type",
                                    "timezone",
                                    "private_notes",
                                    "interviewers",
                                    "eventId",
                                    "jd_id",
                                    "cand_id",
                                    "org_id",
                                    "join_url",
                                    "extra_notes",
                                    "interviewer_notes",
                                    "email",
                                    "addon",
                                )
                            )
                            org_id = CalEvents.objects.get(eventId=c).org_id
                            org_name = (
                                User.objects.get(id=org_id).first_name
                                + " "
                                + User.objects.get(id=org_id).last_name
                            )
                            time_zone = CalEvents.objects.get(eventId=c).timezone
                            if given_time_zone != time_zone:
                                calevents_upcoming_event1[0]["s_time"] = (
                                    convert_to_different_timezone(
                                        CalEvents.objects.get(eventId=c).s_time,
                                        given_time_zone,
                                        time_zone,
                                    )
                                )
                                calevents_upcoming_event1[0]["e_time"] = (
                                    convert_to_different_timezone(
                                        CalEvents.objects.get(eventId=c).e_time,
                                        given_time_zone,
                                        time_zone,
                                    )
                                )
                                calevents_upcoming_event1[0]["slotter_event"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c
                                    ).exists()
                                )
                                if (
                                    calevents_upcoming_event1[0]["slotter_event"]
                                    == True
                                ):
                                    calevents_upcoming_event1[0]["slotter_title"] = (
                                        Interview_slot.objects.get(
                                            interview_id__eventId=c
                                        ).event_id.event_name
                                    )
                                    calevents_upcoming_event1[0]["join_link"] = (
                                        Interview_slot.objects.filter(
                                            interview_id__eventId=c,
                                            event_id__event_type__in=[
                                                "Google Hangouts/Meet",
                                                "Microsoft Teams",
                                            ],
                                        ).exists()
                                    )
                            else:
                                calevents_upcoming_event1[0]["s_time"] = (
                                    CalEvents.objects.get(eventId=c).s_time
                                )
                                calevents_upcoming_event1[0]["e_time"] = (
                                    CalEvents.objects.get(eventId=c).e_time
                                )
                                calevents_upcoming_event1[0]["slotter_event"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c
                                    ).exists()
                                )
                                if (
                                    calevents_upcoming_event1[0]["slotter_event"]
                                    == True
                                ):
                                    calevents_upcoming_event1[0]["slotter_title"] = (
                                        Interview_slot.objects.get(
                                            interview_id__eventId=c
                                        ).event_id.event_name
                                    )
                                    calevents_upcoming_event1[0]["join_link"] = (
                                        Interview_slot.objects.filter(
                                            interview_id__eventId=c,
                                            event_id__event_type__in=[
                                                "Google Hangouts/Meet",
                                                "Microsoft Teams",
                                            ],
                                        ).exists()
                                    )
                            calevents_upcoming_event1[0]["org_name"] = org_name
                            org_id = CalEvents.objects.filter(eventId=c).values(
                                "org_id"
                            )
                            org_name = User.objects.filter(id__in=org_id).values(
                                "id", "first_name", "last_name"
                            )
                            org_name = org_name.annotate(
                                full_name=Concat(
                                    "first_name",
                                    Value(" "),
                                    "last_name",
                                    output_field=CharField(),
                                )
                            )
                            calevents_upcoming_event.append(
                                calevents_upcoming_event1[0]
                            )

                        if CalEvents.objects.filter(
                            s_time__lt=calevents_datetime_strs, eventId=c
                        ).exists():
                            calevents_past_event1 = list(
                                CalEvents.objects.filter(
                                    s_time__lt=calevents_datetime_strs, eventId=c
                                ).values(
                                    "applicant",
                                    "jd",
                                    "notes",
                                    "location",
                                    "event_type",
                                    "timezone",
                                    "private_notes",
                                    "interviewers",
                                    "eventId",
                                    "jd_id",
                                    "cand_id",
                                    "org_id",
                                    "join_url",
                                    "extra_notes",
                                    "interviewer_notes",
                                    "email",
                                    "addon",
                                )
                            )
                            org_id = CalEvents.objects.get(eventId=c).org_id
                            org_name = (
                                User.objects.get(id=org_id).first_name
                                + " "
                                + User.objects.get(id=org_id).last_name
                            )
                            time_zone = CalEvents.objects.get(eventId=c).timezone
                            if given_time_zone != time_zone:
                                calevents_past_event1[0]["s_time"] = (
                                    convert_to_different_timezone(
                                        CalEvents.objects.get(eventId=c).s_time,
                                        given_time_zone,
                                        time_zone,
                                    )
                                )
                                calevents_past_event1[0]["e_time"] = (
                                    convert_to_different_timezone(
                                        CalEvents.objects.get(eventId=c).e_time,
                                        given_time_zone,
                                        time_zone,
                                    )
                                )
                                calevents_past_event1[0]["slotter_event"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c
                                    ).exists()
                                )
                                if calevents_past_event1[0]["slotter_event"] == True:
                                    calevents_past_event1[0]["slotter_title"] = (
                                        Interview_slot.objects.get(
                                            interview_id__eventId=c
                                        ).event_id.event_name
                                    )
                                    calevents_past_event1[0]["join_link"] = (
                                        Interview_slot.objects.filter(
                                            interview_id__eventId=c,
                                            event_id__event_type__in=[
                                                "Google Hangouts/Meet",
                                                "Microsoft Teams",
                                            ],
                                        ).exists()
                                    )
                            else:
                                calevents_past_event1[0]["s_time"] = (
                                    CalEvents.objects.get(eventId=c).s_time
                                )
                                calevents_past_event1[0]["e_time"] = (
                                    CalEvents.objects.get(eventId=c).e_time
                                )
                                calevents_past_event1[0]["slotter_event"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c
                                    ).exists()
                                )
                                if calevents_past_event1[0]["slotter_event"] == True:
                                    calevents_past_event1[0]["slotter_title"] = (
                                        Interview_slot.objects.get(
                                            interview_id__eventId=c
                                        ).event_id.event_name
                                    )
                                    calevents_past_event1[0]["join_link"] = (
                                        Interview_slot.objects.filter(
                                            interview_id__eventId=c,
                                            event_id__event_type__in=[
                                                "Google Hangouts/Meet",
                                                "Microsoft Teams",
                                            ],
                                        ).exists()
                                    )
                            calevents_past_event1[0]["org_name"] = org_name
                            org_id = CalEvents.objects.filter(eventId=c).values(
                                "org_id"
                            )
                            org_name = User.objects.filter(id__in=org_id).values(
                                "id", "first_name", "last_name"
                            )
                            org_name = org_name.annotate(
                                full_name=Concat(
                                    "first_name",
                                    Value(" "),
                                    "last_name",
                                    output_field=CharField(),
                                )
                            )
                            calevents_past_event.append(calevents_past_event1[0])
            else:
                for c in set(calevents_event_id):
                    c = CalEvents.objects.filter(eventId=c).last().eventId
                    if CalEvents.objects.filter(eventId=c).exists():
                        try:
                            time_zone = CalEvents.objects.get(eventId=c).timezone
                            calevents_datetime_strs = convert_utc_to_timezone(
                                calevents_datetime_str, time_zone
                            )
                        except Exception as e:
                            calevents_datetime_strs = calevents_datetime_str
                            pass
                        if CalEvents.objects.filter(
                            s_time__gt=calevents_datetime_strs, eventId=c
                        ).exists():
                            calevents_upcoming_event1 = list(
                                CalEvents.objects.filter(
                                    s_time__gt=calevents_datetime_strs, eventId=c
                                ).values(
                                    "applicant",
                                    "jd",
                                    "notes",
                                    "location",
                                    "event_type",
                                    "timezone",
                                    "private_notes",
                                    "interviewers",
                                    "eventId",
                                    "jd_id",
                                    "cand_id",
                                    "org_id",
                                    "join_url",
                                    "extra_notes",
                                    "interviewer_notes",
                                    "email",
                                    "addon",
                                )
                            )
                            org_id = CalEvents.objects.get(eventId=c).org_id
                            org_name = (
                                User.objects.get(id=org_id).first_name
                                + " "
                                + User.objects.get(id=org_id).last_name
                            )
                            time_zone = CalEvents.objects.get(eventId=c).timezone
                            if given_time_zone != time_zone:
                                calevents_upcoming_event1[0]["s_time"] = (
                                    convert_to_different_timezone(
                                        CalEvents.objects.get(eventId=c).s_time,
                                        given_time_zone,
                                        time_zone,
                                    )
                                )
                                calevents_upcoming_event1[0]["e_time"] = (
                                    convert_to_different_timezone(
                                        CalEvents.objects.get(eventId=c).e_time,
                                        given_time_zone,
                                        time_zone,
                                    )
                                )
                                calevents_upcoming_event1[0]["slotter_event"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c
                                    ).exists()
                                )
                                if (
                                    calevents_upcoming_event1[0]["slotter_event"]
                                    == True
                                ):
                                    calevents_upcoming_event1[0]["slotter_title"] = (
                                        Interview_slot.objects.get(
                                            interview_id__eventId=c
                                        ).event_id.event_name
                                    )
                                    calevents_upcoming_event1[0]["join_link"] = (
                                        Interview_slot.objects.filter(
                                            interview_id__eventId=c,
                                            event_id__event_type__in=[
                                                "Google Hangouts/Meet",
                                                "Microsoft Teams",
                                            ],
                                        ).exists()
                                    )
                            else:
                                calevents_upcoming_event1[0]["s_time"] = (
                                    CalEvents.objects.get(eventId=c).s_time
                                )
                                calevents_upcoming_event1[0]["e_time"] = (
                                    CalEvents.objects.get(eventId=c).e_time
                                )
                                calevents_upcoming_event1[0]["slotter_event"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c
                                    ).exists()
                                )
                                if (
                                    calevents_upcoming_event1[0]["slotter_event"]
                                    == True
                                ):
                                    calevents_upcoming_event1[0]["slotter_title"] = (
                                        Interview_slot.objects.get(
                                            interview_id__eventId=c
                                        ).event_id.event_name
                                    )
                                    calevents_upcoming_event1[0]["join_link"] = (
                                        Interview_slot.objects.filter(
                                            interview_id__eventId=c,
                                            event_id__event_type__in=[
                                                "Google Hangouts/Meet",
                                                "Microsoft Teams",
                                            ],
                                        ).exists()
                                    )
                            calevents_upcoming_event1[0]["org_name"] = org_name
                            org_id = CalEvents.objects.filter(eventId=c).values(
                                "org_id"
                            )
                            org_name = User.objects.filter(id__in=org_id).values(
                                "id", "first_name", "last_name"
                            )
                            org_name = org_name.annotate(
                                full_name=Concat(
                                    "first_name",
                                    Value(" "),
                                    "last_name",
                                    output_field=CharField(),
                                )
                            )
                            calevents_upcoming_event.append(
                                calevents_upcoming_event1[0]
                            )
                        if CalEvents.objects.filter(
                            s_time__lt=calevents_datetime_strs, eventId=c
                        ).exists():
                            calevents_past_event1 = list(
                                CalEvents.objects.filter(
                                    s_time__lt=calevents_datetime_strs, eventId=c
                                ).values(
                                    "applicant",
                                    "jd",
                                    "notes",
                                    "location",
                                    "event_type",
                                    "timezone",
                                    "private_notes",
                                    "interviewers",
                                    "eventId",
                                    "jd_id",
                                    "cand_id",
                                    "org_id",
                                    "join_url",
                                    "extra_notes",
                                    "interviewer_notes",
                                    "email",
                                    "addon",
                                )
                            )
                            org_id = CalEvents.objects.get(eventId=c).org_id
                            org_name = (
                                User.objects.get(id=org_id).first_name
                                + " "
                                + User.objects.get(id=org_id).last_name
                            )
                            time_zone = CalEvents.objects.get(eventId=c).timezone
                            if given_time_zone != time_zone:
                                calevents_past_event1[0]["s_time"] = (
                                    convert_to_different_timezone(
                                        CalEvents.objects.get(eventId=c).s_time,
                                        given_time_zone,
                                        time_zone,
                                    )
                                )
                                calevents_past_event1[0]["e_time"] = (
                                    convert_to_different_timezone(
                                        CalEvents.objects.get(eventId=c).e_time,
                                        given_time_zone,
                                        time_zone,
                                    )
                                )
                                calevents_past_event1[0]["slotter_event"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c
                                    ).exists()
                                )
                                if calevents_past_event1[0]["slotter_event"] == True:
                                    calevents_past_event1[0]["slotter_title"] = (
                                        Interview_slot.objects.get(
                                            interview_id__eventId=c
                                        ).event_id.event_name
                                    )
                                    calevents_past_event1[0]["join_link"] = (
                                        Interview_slot.objects.filter(
                                            interview_id__eventId=c,
                                            event_id__event_type__in=[
                                                "Google Hangouts/Meet",
                                                "Microsoft Teams",
                                            ],
                                        ).exists()
                                    )
                            else:
                                calevents_past_event1[0]["s_time"] = (
                                    CalEvents.objects.get(eventId=c).s_time
                                )
                                calevents_past_event1[0]["e_time"] = (
                                    CalEvents.objects.get(eventId=c).e_time
                                )
                                calevents_past_event1[0]["slotter_event"] = (
                                    Interview_slot.objects.filter(
                                        interview_id__eventId=c
                                    ).exists()
                                )
                                if calevents_past_event1[0]["slotter_event"] == True:
                                    calevents_past_event1[0]["slotter_title"] = (
                                        Interview_slot.objects.get(
                                            interview_id__eventId=c
                                        ).event_id.event_name
                                    )
                                    calevents_past_event1[0]["join_link"] = (
                                        Interview_slot.objects.filter(
                                            interview_id__eventId=c,
                                            event_id__event_type__in=[
                                                "Google Hangouts/Meet",
                                                "Microsoft Teams",
                                            ],
                                        ).exists()
                                    )
                            calevents_past_event1[0]["org_name"] = org_name

                            org_id = CalEvents.objects.filter(eventId=c).values(
                                "org_id"
                            )
                            org_name = User.objects.filter(id__in=org_id).values(
                                "id", "first_name", "last_name"
                            )
                            org_name = org_name.annotate(
                                full_name=Concat(
                                    "first_name",
                                    Value(" "),
                                    "last_name",
                                    output_field=CharField(),
                                )
                            )
                            org_name = Subquery(
                                org_name.filter(id=OuterRef("org_id")).values(
                                    "full_name"
                                )[:1]
                            )
                            calevents_past_event.append(calevents_past_event1[0])
            context = {
                "past_event": past_event,
                "upcoming_event": upcoming_event,
                "interviewer": interviewer,
                "teammembers": teammembers,
                "calevents_upcoming_event": calevents_upcoming_event,
                "calevents_past_event": calevents_past_event,
                "calevents_interviewer": final_email,
            }
        return Response(context)

    def delete(self, request):
        request = self.request
        if "id" in request.GET:
            id = request.GET["id"]
            Interview_slot.objects.filter(id=id).delete()
            string = "Deleted Successfully"
            return Response(string)
        if "cal_id" in request.GET:
            cal_id = request.GET["cal_id"]
            CalEvents.objects.filter(id=cal_id).delete()
            string = "CalEvents Deleted Successfully"
            return Response(string)


class website_access(generics.GenericAPIView):
    def get(self, request):
        request = self.request
        if request.GET.get("website", None):
            user_id, updated_by = admin_account(request)
            is_active = request.GET.get("website")
            if not website_useraccess.objects.filter(user_id=user_id).exists():
                website_useraccess.objects.create(
                    user_id=user_id, is_active=json.loads(is_active)
                )
                success = is_active
            else:
                website_useraccess.objects.filter(user_id=user_id).update(
                    is_active=json.loads(is_active)
                )
                success = is_active
            return Response({"success": success})
        if request.GET.get("id", None):
            pk = request.GET["id"]
            user_id = Event_scheduler.objects.get(id=pk).emp_id
            website = website_useraccess.objects.filter(is_active=True).values_list(
                "user_id", flat=True
            )
            success = website_useraccess.objects.filter(user_id=user_id).exists()
            return Response({"websitedata": website, "success": success})
        if "email" in request.GET:
            data = request.GET["email"]
            associated_users = website_userinfo.objects.filter(Q(email=data))
            if associated_users.exists():
                return Response(
                    {
                        "success": False,
                        "value": "email",
                        "error": "email is already exists",
                    }
                )
            else:
                if not request.GET["domain"] == "undefined":
                    try:
                        domain = data.split("@")[1]
                        if website_userinfo.objects.filter(
                            email__icontains=domain
                        ).exists():
                            return Response({"success": True, "value": "domain"})
                    except:
                        pass
            return Response({"success": True})

    def post(self, request):
        request = self.request
        success = True
        if request.POST.get("id", None):
            event = Event_scheduler.objects.get(id=request.POST["id"])
            # Create userInfo
            userinfo = website_userinfo.objects.create(
                event_id=event,
                email=request.POST["email"],
                name=request.POST["name"],
                contact=request.POST["contact"],
                description=request.POST["description"],
                destination=request.POST.get("destination", None),
                company=request.POST["company"],
                user_id=event.emp_id,
            )
            # Add event to
            date = request.POST["date"]
            time = request.POST["time"]
            startevent, endevent = event_calender(date, time)
            webevent = website_event.objects.create(
                event_id=event,
                date=request.POST["date"],
                time=request.POST["time"],
                candidate_id=userinfo,
                startevent=startevent,
                endevent=endevent,
                email=userinfo.email,
            )
            addevent = CalendarAddEvent(webevent, request, event.emp_id, userinfo)
            return Response({"success": success})


class Email_Notification(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id = request.user
        candi_ids = self.request.GET.get("candi_id")
        # jd_id=self.request.GET.get('jd_id')
        # d={
        #     'candi_id':candi_id,
        #     'user_id':user_id,
        #     'jd_id':jd_id,
        # }
        if not candi_ids:
            return Response(
                {"success": False, "error": "candi_id parameter is required"}
            )
        success = email_notification(candi_ids, user_id)
        if success:
            return Response({"success": True})
        else:
            return Response({"success": False})


def email_notification(candi_ids, user_id):
    for candi_id in json.loads(candi_ids):
        if employer_pool.objects.filter(
            id=candi_id, candidate_id__isnull=False
        ).exists():
            emp = employer_pool.objects.get(id=candi_id)
            appli_id = emp.candidate_id.application_id
            target = Personal_Info.objects.get(application_id=appli_id)
            # user_id=User.objects.get(id=user_id.id)
            # jd_id=JD_form.objects.get(id=d['jd_id'])
            data = f"You have a new email from {user_id.get_full_name()}.Please check your registered email inbox"
            notify.send(
                user_id,
                recipient=target.user_id,
                description="Email Notification",
                verb=data,
                action_object=user_id,
            )
        return True
