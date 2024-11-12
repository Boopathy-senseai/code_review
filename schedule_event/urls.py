from django.conf.urls import url, include
from django.urls import path, include
from schedule_event import api
from schedule_event import views

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from login.apis import *

urlpatterns = [
    path(
        "api/scheduler_dashboard",
        api.scheduler_dashboard.as_view(),
        name="scheduler_dashboard",
    ),
    url(
        r"api/slotter_interview/(?P<uidb64>[0-9A-Za-z_\-]+)/",
        api.slotter_interview.as_view(),
        name="slotter_interview",
    ),
    path(
        "api/slotter_availble", api.slotter_availble.as_view(), name="slotter_availble"
    ),
    path(
        "api/calender_scheduled_events",
        api.calender_scheduled_events.as_view(),
        name="calender_scheduled_events",
    ),
    path("api/website_access", api.website_access.as_view(), name="website_access"),
    path(
        "api/Email_Notification",
        api.Email_Notification.as_view(),
        name="Email_Notification",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
