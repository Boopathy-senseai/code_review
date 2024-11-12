from django.urls import path

from . import views
from jobspipeline import api


urlpatterns = [
    path(
        "api/jobspipeline", api.Job_Pipeline_Stage.as_view(), name="Job_Pipeline_Stage"
    ),
]
