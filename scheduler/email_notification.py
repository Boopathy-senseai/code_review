from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.mail import send_mail
from calendarapp.models import CalEvents, Questions_Generation
from chatbot.models import ChatBot
from main.models import *
from jobs.models import *
from payment.models import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.shortcuts import render
from zita import settings
import requests
import logging
from email.mime.image import MIMEImage
import stripe
from django.contrib.staticfiles import finders
from django.utils import timezone
import pytz
from django.db.models import *

logger = logging.getLogger()
from jobs.views import *
from jobs.utils import *
from payment.views import *
from chatbot.views import FileDownload


logger.setLevel(logging.DEBUG)
# from django.contrib.sites.shortcuts import get_current_site
Host_mail = settings.EMAIL_HOST_USER


def email_reminders_cpf():
    from django.utils import timezone

    user_data = User.objects.filter(
        user_info__application_status__gt=0, user_info__application_status__lt=100
    )
    from django.utils import timezone
    from datetime import datetime

    today = datetime.now().date()
    for i in user_data:
        if i.last_login != None:
            days_3 = (i.last_login + timedelta(days=3)).date()
            days_7 = (i.last_login + timedelta(days=7)).date()
            days_10 = (i.last_login + timedelta(days=10)).date()
            try:

                if today == days_3:
                    htmly = get_template("email_templates/AF_reminder1.html")
                    subject, from_email, to = (
                        "Reminder: You are 1 step away from your most awaiting Career move.",
                        Host_mail,
                        i.email,
                    )
                    html_content = htmly.render(
                        {"first_name": i.first_name, "last_name": i.last_name}
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.mixed_subtype = "related"
                    image_data = [
                        "facebook.png",
                        "twitter.png",
                        "linkedin.png",
                        "youtube.png",
                        "new_zita_white.png",
                        "img_1.png",
                        "img_2.png",
                        "img_3.png",
                        "ques.png",
                        "email.png",
                    ]
                    for i in image_data:
                        msg.attach(logo_data(i))
                    try:
                        msg.send()
                        Email_Notification.objects.create(
                            user_id=i.id, email_reminder_id=1, is_sent=1
                        )
                    except Exception as e:
                        Email_Notification.objects.create(
                            user_id=i.id, email_reminder_id=1, is_sent=0
                        )
                        logger.error(
                            "error in sending sending application reminder1 mail to "
                            + str(i.email)
                            + " and the Error is "
                            + str(e)
                        )

                elif today == days_7:
                    htmly = get_template("email_templates/AF_reminder2.html")
                    subject, from_email, to = (
                        "Reminder: We miss you in Zita. Come back to complete your profile and get hired.",
                        Host_mail,
                        i.email,
                    )
                    html_content = htmly.render(
                        {"first_name": i.first_name, "last_name": i.last_name}
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.mixed_subtype = "related"
                    image_data = [
                        "facebook.png",
                        "twitter.png",
                        "linkedin.png",
                        "youtube.png",
                        "new_zita_white.png",
                        "img_1.png",
                        "img_2.png",
                        "img_3.png",
                        "ques.png",
                        "email.png",
                    ]
                    for i in image_data:
                        msg.attach(logo_data(i))
                    try:
                        msg.send()
                        Email_Notification.objects.create(
                            user_id=i.id, email_reminder_id=2, is_sent=1
                        )
                    except Exception as e:
                        Email_Notification.objects.create(
                            user_id=i.id, email_reminder_id=2, is_sent=0
                        )
                        logger.error(
                            "error in sending sending application reminder2 mail to "
                            + str(i.email)
                            + " and the Error is "
                            + str(e)
                        )

                # elif today==days_10:
                # 	htmly = get_template('email_templates/AF_reminder3.html')
                # 	subject, from_email, to = 'Reminder: Your zita profile is awaiting your inputs. Please login and complete your profile for better job matching. ', Host_mail, i.email
                # 	html_content = htmly.render({ 'first_name':i.first_name, 'last_name':i.last_name })
                # 	msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                # 	msg.attach_alternative(html_content, "text/html")
                # 	msg.mixed_subtype = 'related'
                # 	image_data =['facebook.png','twitter.png','linkedin.png','youtube.png','new_zita_white.png','img_1.png','img_2.png','img_3.png','ques.png','email.png']
                # 	for i in image_data:
                # 		msg.attach(logo_data(i))
                # 	try:
                # 		msg.send()
                # 		Email_Notification.objects.create(user_id=i.id,email_reminder_id=3,is_sent=1)
                # 	except Exception as e :
                # 		Email_Notification.objects.create(user_id=i.id,email_reminder_id=3,is_sent=0)
                # 		logger.error("error in sending sending application reminder3 mail to "+str(i.email)+' and the Error is '+str(e))
            except Exception as e:
                logger.error(
                    "error in sending sending application reminder mails to all user, and the Error is "
                    + str(e)
                )

    return


def email_reminders_epf():
    zita_match = JD_form.objects.filter(jd_status_id=1)
    for i in zita_match:
        new_count = jd_candidate_analytics.objects.filter(jd_id=i, status_id=5).count()
        try:
            old_count = Zita_match_count.objects.get(jd_id=i).count
        except:
            old_count = 0
        user_id = JD_form.objects.get(id=i.id).user_id
        if old_count < new_count:
            try:
                htmly = get_template("email_templates/zita_match.html")
                subject, from_email, to = (
                    "Knock! Knock! Look at the new match for your JD",
                    Host_mail,
                    user_id.email,
                )
                html_content = htmly.render(
                    {"count": new_count, "user": user_id, "jd_form": i}
                )
                msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                image_data = [
                    "twitter.png",
                    "linkedin.png",
                    "youtube.png",
                    "new_zita_white.png",
                ]
                for i in image_data:
                    msg.attach(logo_data(i))
                msg.send()
                Zita_match_count.objects.filter(jd_id=i).update(count=new_count)
            except Exception as e:
                logger.error(
                    "error in sending  new match to all user, and the Error is "
                    + str(e)
                )
        else:
            Zita_match_count.objects.filter(jd_id=i).update(count=new_count)

    draft = User.objects.filter(is_staff=1, is_active=1)

    for d in draft:
        jd_form = JD_form.objects.filter(user_id=d, jd_status_id=2)
        draft_status = False
        for x in jd_form:
            draft_status = JD_profile.objects.filter(jd_id=x).exists()
        if jd_form.count() > 0:
            if draft_status:
                try:
                    htmly = get_template(
                        "email_templates/reminder_draft_after_profiling.html"
                    )
                    subject, from_email, to = (
                        "Just One step away from posting your job on Zita Smart Jobs",
                        Host_mail,
                        d.email,
                    )
                    html_content = htmly.render(
                        {
                            "user": d,
                        }
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except Exception as e:
                    logger.error(
                        "error in sending Draft status to all user, and the Error is "
                        + str(e)
                    )
            else:
                try:
                    htmly = get_template(
                        "email_templates/reminder_draft_before_profiling.html"
                    )
                    subject, from_email, to = (
                        "Your talent hire is just a job post away.",
                        Host_mail,
                        d.email,
                    )
                    html_content = htmly.render(
                        {
                            "user": d,
                        }
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                except Exception as e:
                    logger.error(
                        "error in sending Draft status to all user, and the Error is "
                        + str(e)
                    )

    return


def email_reminders_shortlisted():

    user_list = (
        jd_candidate_analytics.objects.filter(status_id=7)
        .values_list("jd_id_id", flat=True)
        .distinct()
    )
    applicants_list = JD_form.objects.filter(id__in=user_list)
    # applicants_list = JD_form.objects.filter(id=210)
    for i in applicants_list:
        count = jd_candidate_analytics.objects.filter(jd_id=i, status_id=7).count()
        user_id = i.user_id
        try:
            htmly = get_template("email_templates/shortlisted_reminder.html")
            subject, from_email, to = (
                "Knock! Knock! Look at the new match for your JD",
                Host_mail,
                user_id.email,
            )
            html_content = htmly.render({"count": count, "user": user_id, "jd_form": i})
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            logger.error(
                "error in sending  Shortlisted to all user, and the Error is " + str(e)
            )
    return


def logo_data(img):
    with open(finders.find("images/" + img), "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", img)
    return logo


def plan_cron_jobs():
    domain = settings.CLIENT_URL
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_customer = SubscriptionCustomer.objects.all()
    try:
        for s in stripe_customer:
            subscription_stripe = stripe.Subscription.retrieve(s.stripeSubscriptionId)
            status = subscription_stripe["status"]
            if not status == "active":
                try:
                    subscription = subscriptions.objects.get(
                        client_id=s.user, is_active=True
                    )
                    subscription.is_active = False
                    subscription.subscription_remains_days = 0
                    subscription.subscription_changed_to = -2
                    subscription.save()
                    client_features_balance.objects.filter(client_id=s.user).update(
                        available_count=0
                    )
                except Exception as e:
                    logger.error(
                        "error in "
                        + str(s.user.username)
                        + ", and the Error is "
                        + str(e)
                    )
    except:
        pass
    free_trail = subscriptions.objects.filter(plan_id_id=1)
    from django.utils import timezone

    # Free Trial
    for i in free_trail:
        end_date = i.subscription_valid_till - timezone.now()
        i.subscription_remains_days = int(end_date.days)
        i.save()
        date = int(end_date.days)
        if date < 0:
            # i.is_active = False
            i.subscription_changed_to = -2
            i.save()
        if email_preference.objects.filter(
            user_id=i.client_id, stage_id_id=3, is_active=True
        ).exists():
            if int(date) == 7:

                try:
                    htmly = get_template("email_templates/freetrial_7days.html")
                    subject, from_email, to = (
                        "Your free trial expires soon",
                        Host_mail,
                        i.client_id.email,
                    )
                    html_content = htmly.render(
                        {"plan": i, "domain": domain, "user": i.client_id}
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
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
                except Exception as e:
                    logger.error(
                        "error in sending  Free trail reminder to all users, and the Error is "
                        + str(e)
                    )
            elif int(date) == 3:
                try:
                    htmly = get_template("email_templates/freetrial_3days.html")
                    subject, from_email, to = (
                        "Your free trial expires soon",
                        Host_mail,
                        i.client_id.email,
                    )
                    html_content = htmly.render(
                        {"plan": i, "user": i.client_id, "domain": domain}
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
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
                except Exception as e:
                    logger.error(
                        "error in sending  Free trail reminder to all users, and the Error is "
                        + str(e)
                    )
            elif int(date) == 0:
                try:
                    htmly = get_template("email_templates/freetrial_end.html")
                    subject, from_email, to = (
                        "Your free trial expires today!",
                        Host_mail,
                        i.client_id.email,
                    )
                    html_content = htmly.render(
                        {"plan": i, "user": i.client_id, "domain": domain}
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
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
                except Exception as e:
                    logger.error(
                        "error in sending  Free trail reminder to all users, and the Error is "
                        + str(e)
                    )

    # Subscription
    plan = subscriptions.objects.filter(
        is_active=True, subscription_changed_to=-1
    ).exclude(plan_id_id=1)
    for i in plan:
        end_date = i.subscription_valid_till - timezone.now()
        i.subscription_remains_days = int(end_date.days)
        i.save()
        date = int(end_date.days)
        if date < 0:
            i.subscription_changed_to = -2
            i.save()
        if email_preference.objects.filter(
            user_id=i.client_id, stage_id_id=3, is_active=True
        ).exists():
            if int(date) == 7:
                try:
                    htmly = get_template("email_templates/subscription_end_7days.html")
                    subject, from_email, to = (
                        "Your subscription expires soon!",
                        Host_mail,
                        i.client_id.email,
                    )
                    html_content = htmly.render(
                        {"plan": i, "user": i.client_id, "domain": domain}
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
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
                except Exception as e:
                    logger.error(
                        "error in sending  Free trail reminder to all users, and the Error is "
                        + str(e)
                    )
            elif int(date) == 3:
                try:
                    htmly = get_template("email_templates/subscription_end_3days.html")
                    subject, from_email, to = (
                        "Your subscription expires soon!",
                        Host_mail,
                        i.client_id.email,
                    )
                    html_content = htmly.render(
                        {"plan": i, "user": i.client_id, "domain": domain}
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
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
                except Exception as e:
                    logger.error(
                        "error in sending  Free trail reminder to all users, and the Error is "
                        + str(e)
                    )
            elif int(date) == 0:
                try:
                    htmly = get_template("email_templates/subscription_end.html")
                    subject, from_email, to = (
                        "Your subscription has expired!",
                        Host_mail,
                        i.client_id.email,
                    )
                    html_content = htmly.render(
                        {"plan": i, "user": i.client_id, "domain": domain}
                    )
                    msg = EmailMultiAlternatives(
                        subject, html_content, from_email, [to]
                    )
                    msg.attach_alternative(html_content, "text/html")
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
                except Exception as e:
                    logger.error(
                        "error in sending  Free trail reminder to all users, and the Error is "
                        + str(e)
                    )

    return True


def reminder_mail(d, mail):
    htmly = get_template("reminder_evaluation.html")
    subject = "Reminder for Evaluation"
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_FROM, [mail])
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = "related"
    msg.send()


def reminder_for_evaulation():
    from dateutil.parser import parse
    from django.utils import timezone

    domain = settings.CLIENT_URL
    evaluation = (
        Questions_Generation.objects.filter(
            interview_id__e_time__lte=datetime.now(), scorecard__isnull=True
        )
        .distinct()
        .values(
            "jd_id", "candidate_id", "interview_id", "attendees", "interview_id__e_time"
        )
    )
    evaluation = evaluation.annotate(count=Count("interview_id"))
    date = datetime.now()
    date = date.date()

    for i in evaluation:
        if i["count"] > 10 or i["count"] == 10:
            email = User.objects.get(id=i["attendees"]).email
            interview = CalEvents.objects.get(id=i["interview_id"])
            day = parse(i["interview_id__e_time"])
            day1 = day + timedelta(days=1)
            day2 = day + timedelta(days=2)
            day3 = day + timedelta(days=3)
            company_name = ''
            if company_details.objects.filter(recruiter_id=i["attendees"]).exists():
                company_name = company_details.objects.get(recruiter_id=i["attendees"]).company_name
            d = {
                "domain": domain,
                "interview": interview,
                "jd_id": i["jd_id"],
                "can_id": i["candidate_id"],
                "company": company_name,
            }
            if day1.date() == date:
                d["reminder"] = "Reminder1 for Evaluation"
                reminder_mail(d, email)
            if day2.date() == date:
                d["reminder"] = "Reminder2 for Evaluation"
            if day3.date() == date:
                d["reminder"] = "Reminder3 for Evaluation"
                reminder_mail(d, email)


# def subscription_expire():
# 	dates = datetime.now()
# 	data = client_features_balance.objects.filter(client_id=6904,feature_id=10).values("client_id_id")
# 	for i in data:
# 		client_id = i["client_id_id"]
# 		last_plan = subscriptions.objects.filter(client_id=client_id).last()
# 		plan = last_plan.plan_id.pk
# 		if last_plan.subscription_valid_till != None:
# 			end_subscription = last_plan.subscription_valid_till.replace(tzinfo=None)
# 			startdate = None
# 			if dates > end_subscription:
# 				count_reset = client_features_balance.objects.filter(client_id = client_id).values("add_ons_id","feature_id","client_id")
# 				descriptive = applicant_descriptive.objects.filter(is_active = False).delete()
# 				if len(count_reset) > 0:
# 					for i in count_reset:
# 						client_id = i["client_id"]
# 						if addons_plan_features.objects.filter(plan_id=plan,addon_id=i['add_ons_id']).exists():
# 							add_ons = addons_plan_features.objects.get(plan_id=plan,addon_id=i['add_ons_id']).carry_forward
# 							if not add_ons:
# 								startdate = last_plan.subscription_start_ts.replace(tzinfo=None)
# 								checking = comparative(one_month_checking(startdate,1),dates)
# 								if not checking:
# 									client_features_balance.objects.filter(client_id=client_id,add_ons_id__is_carry=False).delete()
# 							else:
# 								client_features_balance.objects.filter(client_id=client_id,add_ons_id__is_carry= True,add_ons_id =i["add_ons_id"],available_count = 0).delete()
# 						else:
# 							if client_features_balance.objects.filter(client_id = client_id,feature_id = expire_addons(i["feature_id"])).exists():
# 								plans_count = client_features_balance.objects.get(client_id = client_id,feature_id=i["feature_id"]).plan_count
# 								if plans_count == 0:
# 									client_features_balance.objects.filter(client_id = client_id,feature_id=i["feature_id"]).update(available_count = client_features_balance.objects.get(client_id = client_id,feature_id = expire_addons(i["feature_id"])).available_count)
# 							else:
# 								client_features_balance.objects.filter(client_id=client_id,feature_id=i["feature_id"]).update(available_count=0)

# 			if plan == 12 or plan == 11:
# 				monthy_renewal = last_plan.subscription_start_ts.replace(tzinfo=None)
# 				monthy_renewal = one_month_checking(monthy_renewal,1)
# 				if dates > monthy_renewal:
# 					features_balance = plan_features.objects.filter(plan_id=plan,feature_id_id__in=[10,27,53,6])
# 					for i in features_balance:
# 						feature_update = Plan_upgrade(client_id,i)


def transcript_email():
    current_date = datetime.now().date()
    previous_date, format_date = FileDownload.previous_date(current_date)
    data = ChatBot.objects.filter(chat_id=previous_date).values("user_id")
    for i in data:
        emailshare = FileDownload.emailshare(i["user_id"])
    return True


def remainder_send_mail():  # No need
    today = datetime.now().date()
    events = CalEvents.objects.filter(remainder__isnull=False)
    if not events.exists():
        return Response({"message": "No events found!", "status": False})
    filtered_events = [
        event for event in events if event.s_time.split("T")[0] == str(today)
    ]
    for event in filtered_events:
        can_id = event.cand_id
        if employer_pool.objects.filter(id=can_id).exists():
            can_email = employer_pool.objects.get(id=can_id).email
            rem = event.remainder
            start_time = event.s_time.replace("T", " ").split(".")[0]
            event_time = datetime.strptime(
                start_time, "%Y-%m-%d %H:%M:%S"
            )  # to convert str to datetime object
            rem_time = event_time - timedelta(minutes=int(rem))

            current_time = datetime.now().replace(microsecond=0)

            # Check if current time matches the reminder time
            if rem_time.strftime("%H:%M") == current_time.strftime("%H:%M"):
                subject = f"Reminder: Upcoming Interview Event"
                message = f"Dear Candidate,\n\n This is a reminder for your upcoming interview scheduled at {event_time.strftime('%Y-%m-%d %H:%M')}.\n"
                send_mail(subject, message, settings.EMAIL_FROM, [can_email])
