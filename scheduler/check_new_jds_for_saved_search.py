from job_pool.models import *
from datetime import datetime
from django.db.models import Value


def initial_start():

    for z in list(
        Saved_searches.objects.values_list("application_id_id", flat=True).distinct()
    ):
        check_for_new_jds(z)


def check_for_new_jds(appl_id):

    len(JD_list.objects.all())
    filters1 = {"role_searched_criteria": "prof_role", "loc_searched_criteria": "state"}
    # counter=0
    for i in Saved_searches.objects.filter(
        application_id_id=appl_id, is_active=1
    ).order_by("-created_at")[:10]:
        temp_list = JD_list.objects.filter(updated_at=i.created_at.date())
        role = i.role_searched_criteria
        if len(i.role_searched_criteria) > 0:
            temp_list = temp_list.filter(prof_role=role)

        loc = i.loc_searched_criteria
        if len(loc) > 0:
            temp_list = temp_list.filter(state=loc)
        i.new_jd_count = len(temp_list)
        i.save()
