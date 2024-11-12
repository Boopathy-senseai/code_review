from django.db import models
from users.models import UserListWithDetail, UserHasComapny
from calendarapp.models import *
from jobs.models import *

# Create your models here.


class Event_scheduler(models.Model):
    emp_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(UserHasComapny, on_delete=models.CASCADE, null=True)
    event_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True)
    daterange = models.CharField(max_length=100)
    days = models.CharField(max_length=100)
    startdate = models.CharField(max_length=100)
    enddate = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    times_zone = models.CharField(max_length=100)
    interviewer = models.CharField(max_length=100)
    times_zone_display = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    updatedby = models.DateTimeField(null=True, auto_now_add=True)
    isdeleted = models.BooleanField(default=False)
    ischecked = models.CharField(max_length=100, default=True)


class Interview_slot(models.Model):
    candidate_id = models.ForeignKey(employer_pool, on_delete=models.CASCADE, null=True)
    event_id = models.ForeignKey(
        Event_scheduler, on_delete=models.CASCADE, null=True
    )  #
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=True)
    startevent = models.CharField(max_length=100, null=True)
    endevent = models.CharField(max_length=100, null=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    calendar_id = models.CharField(max_length=500, null=True)
    join_url = models.TextField(null=True)
    jd_id = models.ForeignKey(JD_form, on_delete=models.CASCADE, null=True)
    interview_id = models.ForeignKey(CalEvents, on_delete=models.CASCADE, null=True)


class Scheduled_Time(models.Model):
    index = models.IntegerField(null=True)
    day = models.CharField(max_length=100, null=True)
    starttime = models.CharField(max_length=100, null=True)
    endtime = models.CharField(max_length=100, null=True)
    event_id = models.ForeignKey(Event_scheduler, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Schedule_interview(models.Model):
    emp_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.ForeignKey(UserHasComapny, on_delete=models.CASCADE, null=True)
    event_id = models.ForeignKey(Event_scheduler, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AvailbleSlot(models.Model):
    event_id = models.ForeignKey(Event_scheduler, on_delete=models.CASCADE, null=True)
    date = models.CharField(max_length=100, null=True)
    index = models.IntegerField(null=True)
    starttime = models.CharField(max_length=100, null=True)
    endtime = models.CharField(max_length=100, null=True)


class website_userinfo(models.Model):
    company = models.CharField(max_length=1000, null=True)
    name = models.CharField(max_length=1000, null=True)
    email = models.CharField(max_length=1000, null=True)
    description = models.TextField(null=True)
    contact = models.TextField(max_length=1000, null=True)
    destination = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    event_id = models.ForeignKey(Event_scheduler, on_delete=models.CASCADE, null=True)


class website_event(models.Model):
    candidate_id = models.ForeignKey(
        website_userinfo, on_delete=models.CASCADE, null=True
    )
    event_id = models.ForeignKey(
        Event_scheduler, on_delete=models.CASCADE, null=True
    )  #
    date = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    email = models.CharField(max_length=100, null=True)
    startevent = models.CharField(max_length=100, null=True)
    endevent = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255)
    calendar_id = models.TextField(null=True)
    join_url = models.TextField(null=True)
    interview_id = models.ForeignKey(CalEvents, on_delete=models.CASCADE, null=True)


class website_useraccess(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
