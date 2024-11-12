from application import views as app_view
from main import views as main_view
from jobs import views as jobs_view
from django.conf.urls import url, include
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.static import serve
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

# import notifications.urls
from jobs.views import MessagesAPIView, messages_data

urlpatterns = [
    path("<str:url>/career/", jobs_view.career_page, name="career_page"),
    # url(r'^application/', include(('application.urls', 'application'), namespace='application')),
    path("myprofile/<str:username>/", app_view.Profile_Page, name="profile_list"),
    path("", include("login.urls")),
    path("", include("accounts.urls")),
    path("", include("users.urls")),
    path("", include("role.urls")),
    path("", include("permission.urls")),
    path("", include("reports.urls")),
    path("", include("application.urls")),
    path("", include("calendarapp.urls")),
    path("", include("jobspipeline.urls")),
    path("", include("schedule_event.urls")),
    path("", include("chatbot.urls")),
    url(r"^", include(("jobs.urls", "jobs"), namespace="jobs")),
    url(r"^", include(("payment.urls", "payment"), namespace="payment")),
    url(r"^", include(("bulk_upload.urls", "bulk_upload"), namespace="bulk_upload")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    # url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path(
        "api/messages/<str:chatname>/<int:jd_id>/",
        MessagesAPIView.as_view(),
        name="messages",
    ),
    path("messages/<str:chatname>/<int:jd_id>/", messages_data, name="messages_data"),
    url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    url(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
