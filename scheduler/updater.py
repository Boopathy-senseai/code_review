from datetime import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
from scheduler import job_listingfunction
from scheduler import email_notification
from scheduler import check_new_jds_for_saved_search

# from main import views
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger


def start():

    scheduler = BackgroundScheduler()

    # email_trigger_cpf = OrTrigger([CronTrigger(hour='08', minute='01')])
    email_trigger_epf = OrTrigger([CronTrigger(hour="00", minute="01")])
    email_transcript = OrTrigger(
        [CronTrigger(hour="03", minute="30")]
    )  # Set On IST - 9.00 AM

    # email_reminder = OrTrigger([CronTrigger(minute='*/1')])     # Interview Reminder (Trigger every 1 minute)

    # email_trigger_cpf = OrTrigger([CronTrigger(second="*/10")])

    # remove_old = OrTrigger([CronTrigger(hour='19', minute='08')])
    # scheduler.add_job(email_notification.email_reminders_cpf,email_trigger_cpf)
    scheduler.add_job(
        email_notification.plan_cron_jobs, email_trigger_epf
    )  # Free Trail Notification
    scheduler.add_job(
        email_notification.reminder_for_evaulation, email_trigger_epf
    )  # Interview Evaluation Notification
    scheduler.add_job(
        email_notification.transcript_email, email_transcript
    )  # Transcript Mail

    # scheduler.add_job(email_notification.remainder_send_mail,email_reminder)   # Interview Remainder

    # scheduler.add_job(email_notification.plan_cron_jobs, 'interval', minutes=1)
    # scheduler.add_job(job_listingfunction.remove_old_data,remove_old)
    # scheduler.add_job(job_listingfunction.remove_old_data, 'interval', weeks=2)

    scheduler.start()
