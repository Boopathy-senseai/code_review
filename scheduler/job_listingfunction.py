import requests
import datetime
import os
from job_pool.models import *
from django.db.models import *
from django.utils import timezone
import pytz
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("jd_list_old_data")


def remove_old_data():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=60)
    jd_list = JD_list.objects.all()
    logger.info(
        "Total number of JDs in the Main Table(JD_list) -- " + str(jd_list.count())
    )
    fav = favourites.objects.all().values_list("JD_list", flat=True).distinct()
    jd_list = (
        jd_list.exclude(zita_jd_id__isnull=False)
        .exclude(job_posted_date__range=(start_date, end_date))
        .exclude(jd__in=fav)
    )
    logger.info("Total number of JDs are not valid -- " + str(jd_list.count()))
    try:
        # JD_list_old.objects.bulk_create(jd_list, batch_size=500, ignore_conflicts=True)
        logger.info(
            "Total number of JDs are moved to JD_list_old table -- "
            + str(jd_list.count())
        )
        logger.info(
            "Total number of JDs deleted in JD_list Table -- " + str(jd_list.count())
        )
        jd_list.delete()
        jd_list = JD_list.objects.all()
        logger.info(
            "Total number of JDs deleted in JD_list Table -- " + str(jd_list.count())
        )
    except Exception as e:
        logger.info("JD_list_old Table update issue -- " + str(e))

    return
