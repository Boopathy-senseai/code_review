import stripe
from payment.views import *
from zita import settings
from django.http.response import (
    JsonResponse,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotModified,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from jobs.models import *
from jobs.views import *
from django.urls import reverse
from .models import *
from login.decorators import *
from django.contrib.auth.decorators import login_required
import datetime
from django.views.decorators.cache import never_cache
from django.contrib.sites.shortcuts import get_current_site
import time
import json
import pytz
from rest_framework.decorators import api_view
from django.contrib import messages

Host_mail = settings.EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.shortcuts import render
from django.contrib.auth.models import Permission
from users.models import UserHasComapny, CompanyHasInvite

stripe.api_key = settings.STRIPE_SECRET_KEY
contact_credit = settings.contact_credit
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Case, When, Value, CharField, F, Q, Exists
from django.db.models import Subquery
from jobs.models import *
import ast
from datetime import datetime, timedelta
from django.db.models.functions import Coalesce
from django.db.models import Func, F, ExpressionWrapper, DateField
from django.db.models.functions import Coalesce, TruncDate


class manage_subscription(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        basic_month = settings.basic_month
        basic_year = settings.basic_year
        pro_year = settings.pro_year
        pro_month = settings.pro_month
        user_id, updated_by = admin_account(request)
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        from django.utils import timezone

        try:
            subscription = subscriptions.objects.filter(client_id=user_id).last()
            end_date = subscription.subscription_valid_till - timezone.now()
            subscription.subscription_remains_days = int(end_date.days)
            subscription.save()
            if subscription.plan_id.pk == 1:
                end_date = (
                    subscription.subscription_valid_till.date() - timezone.now().date()
                )
                subscription.subscription_remains_days = int(end_date.days)
                subscription.save()
                if int(subscription.subscription_remains_days) <= 0:
                    free_expired = 0
                elif int(subscription.subscription_remains_days) < 7:
                    free_expired = 1
                else:
                    free_expired = None
            else:
                if int(subscription.subscription_remains_days) <= 0:
                    free_expired = 0
                elif int(subscription.subscription_remains_days) < 15:
                    free_expired = 1
                else:
                    free_expired = None
            request.session["expire_in"] = subscription.subscription_remains_days
            expire_in = request.session["expire_in"]
            sub_id = subscription.plan_id.pk
            user_count = subscription.no_of_users
            addons_count = list(
                client_features_balance.objects.filter(
                    client_id=user_id, addons_count__isnull=False
                ).values("add_ons", "addons_count")
            )
            price = subscription.plan_id.price
            if len(addons_count) > 0:
                for i in addons_count:
                    plan_id = (
                        subscriptions.objects.filter(client_id=user_id)
                        .last()
                        .plan_id.pk
                    )
                    addon_id = i["add_ons"]
                    count = i["addons_count"]
                    if addons_plan_features.objects.filter(
                        plan_id=plan_id, addon=addon_id
                    ).exists():
                        addon_price = addons_plan_features.objects.get(
                            plan_id=plan_id, addon=addon_id
                        ).price
                        price = price + addon_price * count
                else:
                    price = price
            base_price = subscription.plan_id.price
        except Exception as e:
            sub_id = 0
            user_count = 1
            subscription = None
            free_expired = None
            expire_in = None
            base_price = None
            price = 0
        downgrade = 0
        try:
            cur_active_job = JD_form.objects.filter(
                user_id=user_id, jd_status_id=1
            ).count()
            if cur_active_job > 3:
                downgrade = 1
            if (
                client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=12
                ).available_count
                == 0
            ):
                downgrade = 1
        except:
            pass
        try:
            del request.session["discounts"]
            request.session.modified = True
        except:
            pass
        try:
            CustomerId = SubscriptionCustomer.objects.get(user=user_id).user.id
        except SubscriptionCustomer.DoesNotExist:
            CustomerId = 0
        try:
            setting = career_page_setting.objects.filter(recruiter_id=user_id).values()
        except:
            setting = None
        try:
            setting1 = company_details.objects.get(recruiter_id=user_id)
            invites = CompanyHasInvite.objects.get(company_id=setting1).invites
            total_user = UserHasComapny.objects.filter(
                company_id=setting1, user_id__is_active=True
            ).count()
            balance = subscription.no_of_users - total_user
            CompanyHasInvite.objects.filter(company_id=setting1).update(invites=balance)
        except:

            invites = 0
            total_user = 0
        try:
            available = client_features_balance.objects.get(
                client_id=user_id, feature_id_id=11
            ).available_count
        except:
            available = 0
        from django.db.models.functions import Length
        from django.db.models import (
            Case,
            F,
            Value,
            When,
            BooleanField,
            Subquery,
            OuterRef,
        )

        try:
            subscription = (
                subscriptions.objects.filter(client_id=user_id)
                .order_by("-subscription_id")
                .values()
            )
            plan_id = subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
            subscription = subscription.annotate(
                plan_name=Subquery(
                    tmeta_plan.objects.filter(plan_id=plan_id).values("plan_name")
                ),
                days=Subquery(
                    tmeta_plan.objects.filter(plan_id=plan_id).values(
                        "subscription_value_days",
                    )
                ),
            )
            subscription = subscription[0]
            if subscription.get('auto_renewal'):
                plan_days = tmeta_plan.objects.get(plan_id = subscription["plan_id_id"]).subscription_value_days + 1
                invoice_created_at =  subscription["subscription_valid_till"] - timedelta(plan_days)
                subscription['created_at'] = invoice_created_at
        except Exception as e:
            subscription = None
        if subscriptions.objects.filter(client_id=user_id).exists():
            current_plan = (
                subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
            )
        else:
            current_plan = None
        yearly_plan = list(
            tmeta_plan.objects.filter(is_active=True)
            .annotate(subscription_days_length=Length("subscription_value_days"))
            .filter(subscription_days_length__exact=3)
            .values_list("plan_id", flat=True)
        )
        yearly_plan.append(1)
        yearly_plan = tmeta_plan.objects.filter(
            is_active=True, plan_id__in=yearly_plan
        ).values()
        yearly_plan = yearly_plan.annotate(
            sub_heading=Subquery(
                subscription_content.objects.filter(plan_id=OuterRef("plan_id")).values(
                    "subscription_content"
                )[:1]
            ),
            data=Subquery(
                subscription_content.objects.filter(plan_id=OuterRef("plan_id")).values(
                    "rich_text_content"
                )[:1]
            ),
            days_length=Length(F("subscription_value_days")),
            current_plan=Subquery(
                subscriptions.objects.filter(client_id=user_id)
                .order_by("-subscription_id")
                .values("plan_id__pk")[:1]
            ),
            is_month=Case(
                When(days_length__exact=2, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            jd_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=10
                ).values("feature_value")[:1]
            ),
            resume_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=27
                ).values("feature_value")[:1]
            ),
            ai_matched_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=6
                ).values("feature_value")[:1]
            ),
            user_price=Case(
                When(plan_id=1, then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            ),
            final_price=Case(
                When(price=0, then=Value("FREE")),
                default=F("price"),
                output_field=CharField(),
            ),
            days=Case(
                When(plan_id=1, then=Value("for 14 Days")),
                default=Value("Year"),
                output_field=CharField(),
            ),
            is_plan=Case(
                When(~Q(current_plan=None), then=Value(True)),
                default=False,
                output_field=BooleanField(),
            ),
            button=Case(
                When(plan_id=current_plan, then=Value("Current Plan")),
                When(Q(plan_id=1) & Q(current_plan=1), then=Value("Current Plan")),
                When(Q(plan_id=1) & ~Q(current_plan=1), then=Value("14 Days Trial")),
                default=Value("Choose Plan"),
                output_field=CharField(),
            ),
        )

        monthly_plan = list(
            tmeta_plan.objects.filter(is_active=True)
            .exclude(plan_id=1)
            .annotate(subscription_days_length=Length("subscription_value_days"))
            .filter(subscription_days_length__exact=2)
            .values_list("plan_id", flat=True)
        )
        monthly_plan.append(1)
        monthly_plan = tmeta_plan.objects.filter(
            is_active=True, plan_id__in=monthly_plan
        ).values()
        monthly_plan = monthly_plan.annotate(
            sub_heading=Subquery(
                subscription_content.objects.filter(plan_id=OuterRef("plan_id")).values(
                    "subscription_content"
                )[:1]
            ),
            data=Subquery(
                subscription_content.objects.filter(plan_id=OuterRef("plan_id")).values(
                    "rich_text_content"
                )[:1]
            ),
            days_length=Length(F("subscription_value_days")),
            is_month=Case(
                When(days_length__exact=2, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            jd_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=10
                ).values("feature_value")[:1]
            ),
            resume_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=27
                ).values("feature_value")[:1]
            ),
            ai_matched_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=6
                ).values("feature_value")[:1]
            ),
            current_plan=Subquery(
                subscriptions.objects.filter(client_id=user_id)
                .order_by("-subscription_id")
                .values("plan_id__pk")[:1]
            ),
            user_price=Case(
                When(plan_id=1, then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            ),
            days=Case(
                When(plan_id=1, then=Value("for 14 Days")),
                default=Value("Month"),
                output_field=CharField(),
            ),
            is_plan=Case(
                When(~Q(current_plan=None), then=Value(True)),
                default=False,
                output_field=BooleanField(),
            ),
            final_price=Case(
                When(price=0, then=Value("FREE")),
                default=F("price"),
                output_field=CharField(),
            ),
            button=Case(
                When(plan_id=current_plan, then=Value("Current Plan")),
                When(Q(plan_id=1) & Q(current_plan=1), then=Value("Current Plan")),
                When(Q(plan_id=1) & ~Q(current_plan=1), then=Value("14 Days Trial")),
                default=Value("Choose Plan"),
                output_field=CharField(),
            ),
        )
        total_plan = list(
            tmeta_plan.objects.filter(
                is_active=1, subscription_value_days=30
            ).values_list("plan_id", flat=True)
        )
        total_plan.append(1)
        total_plan = sorted(map(int, total_plan))
        total_plan_name = list(
            tmeta_plan.objects.filter(plan_id__in=total_plan).values_list(
                "plan_name", flat=True
            )
        )
        available_addons = addons_plan_features.objects.filter(
            plan_id__in=total_plan
        ).values()
        available_addons = available_addons.annotate(
            add_on=F("addon_id"),
            display_name=Case(
                When(addon_id__id=1, then=Value("Job Posting")),
                When(addon_id__id=2, then=Value("AI Resume Parsing")),
                When(
                    addon_id__id=3,
                    then=Value(
                        "AI Resume Comparitive Analytics & Recommendation to Hire"
                    ),
                ),
                When(addon_id__id=4, then=Value("Sourcing Contact Unlock")),
                When(addon_id__id=7, then=Value("AI Interview Questions Generation")),
                When(addon_id__id=9, then=Value("Priority Support")),
                When(
                    addon_id__id=10, then=Value("AI Resume Matching for Multiple Jobs")
                ),
                When(
                    addon_id__id=11,
                    then=Value("AI Matching with Descriptive Analytics"),
                ),
                default=Value(None),  # Default value if none of the conditions match
                output_field=CharField(),
            ),
            usage=Case(
                When(
                    add_on=1,
                    then=Subquery(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=10
                        ).values("available_count")[:1]
                    ),
                ),
                When(
                    add_on=2,
                    then=Subquery(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=27
                        ).values("available_count")[:1]
                    ),
                ),
                When(
                    add_on=4,
                    then=Subquery(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=53
                        ).values("available_count")[:1]
                    ),
                ),
                When(
                    add_on=11,
                    then=Subquery(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=6
                        ).values("available_count")[:1]
                    ),
                ),
                default=Value(
                    "unlimited"
                ),  # Default value if add_on is neither 1 nor 2
                output_field=CharField(),
            ),
            addon_exist=Case(
                When(
                    add_on=1,
                    then=Exists(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=51
                        )
                    ),
                ),
                When(
                    add_on=2,
                    then=Exists(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=52
                        )
                    ),
                ),
                When(
                    add_on=4,
                    then=Exists(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=58
                        )
                    ),
                ),
                When(
                    add_on=11,
                    then=Exists(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=56
                        )
                    ),
                ),
                When(
                    add_on=3,
                    then=Exists(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=60
                        )
                    ),
                ),
                When(
                    add_on=7,
                    then=Exists(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=59
                        )
                    ),
                ),
                When(
                    add_on=9,
                    then=Exists(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=61
                        )
                    ),
                ),
                When(
                    add_on=10,
                    then=Exists(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=62
                        )
                    ),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
            created_at=Case(
                When(
                    add_on=3,
                    then=Subquery(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=60
                        ).values("created_at")[:1]
                    ),
                ),
                When(
                    add_on=7,
                    then=Subquery(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=59
                        ).values("created_at")[:1]
                    ),
                ),
                When(
                    add_on=9,
                    then=Subquery(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=61
                        ).values("created_at")[:1]
                    ),
                ),
                When(
                    add_on=10,
                    then=Subquery(
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id=62
                        ).values("created_at")[:1]
                    ),
                ),
                default=Value(None),
                output_field=DateField(),
            ),
            next_month_created_at=Coalesce(
                ExpressionWrapper(
                    Case(
                        When(
                            add_on=3,
                            then=Subquery(
                                client_features_balance.objects.filter(
                                    client_id=user_id, feature_id=60
                                ).values("created_at")[:1]
                            ),
                        ),
                        When(
                            add_on=7,
                            then=Subquery(
                                client_features_balance.objects.filter(
                                    client_id=user_id, feature_id=59
                                ).values("created_at")[:1]
                            ),
                        ),
                        When(
                            add_on=9,
                            then=Subquery(
                                client_features_balance.objects.filter(
                                    client_id=user_id, feature_id=61
                                ).values("created_at")[:1]
                            ),
                        ),
                        When(
                            add_on=10,
                            then=Subquery(
                                client_features_balance.objects.filter(
                                    client_id=user_id, feature_id=62
                                ).values("created_at")[:1]
                            ),
                        ),
                        default=Value(None),
                        output_field=DateField(),
                    )
                    + timedelta(days=30),
                    output_field=DateField(),
                ),
                Value(None),
            ),
        )
        available_addons = addon_format_changes(available_addons, total_plan_name)
        content_text = list(
            addons_plan_features.objects.filter(addon=1, plan_id__in=total_plan)
            .order_by("plan_id")
            .values_list("content")
        )
        content_text = [
            {"name": name, "content": json.loads(content[0])}
            for name, content in zip(total_plan_name, content_text)
        ]
        user_credit = user_credits(user_id)
        expire_content = expire_details(user_id)
        addons_content_01 = json.loads(website_details.objects.get(id=5).addons)
        addons_content_02 = json.loads(website_details.objects.get(id=5).card_view)
        avail_addons = len(
            list(
                client_features_balance.objects.filter(
                    client_id=user_id, add_ons__isnull=False
                ).values_list("add_ons")
            )
        )
        # avail_addons = len(avail_addons)
        unlimited = unlimited_addons(user_id)
        context = {
            "subscription": subscription,
            "sub_id": sub_id,
            "downgrade": downgrade,
            "basic_month": basic_month,
            "basic_year": basic_year,
            "free_expired": free_expired,
            "permission": permission,
            "expire_in": expire_in,
            "invites": invites,
            "total_user": total_user,
            "base_price": base_price,
            "user_count": user_count,
            "setting": setting,
            "pro_year": pro_year,
            "pro_month": pro_month,
            "price": price,
            "CustomerId": CustomerId,
            "available": available,
            "yearly_plan": yearly_plan,
            "monthly_plan": monthly_plan,
            "available_addons": available_addons,
            "content_text": content_text,
            "user_credits": user_credit,
            "expire_details": expire_content,
            "addons_content_01": addons_content_01,
            "addons_content_02": addons_content_02,
            "avail_addons": avail_addons,
            "unlimited": unlimited,
        }
        return Response(context)


from email.mime.image import MIMEImage
from django.contrib.staticfiles import finders


def logo_data(img):
    # image_data =['facebook.png','twitter.png','linkedin.png','youtube.png','new_zita.png']
    with open(finders.find("images/" + img), "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", img)
    return logo


class checkout_session(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request = self.request
        user, updated_by = admin_account(request)

        if "session_id" in request.GET:

            session_id = request.GET["session_id"]
            checkout = stripe.checkout.Session.retrieve(session_id)
            SubscriptionCustomer.objects.filter(user=user).delete()
            SubscriptionCustomer.objects.get_or_create(
                user=user,
                stripeCustomerId=checkout["customer"],
                stripeSubscriptionId=checkout["subscription"],
            )
            subscription = stripe.Subscription.retrieve(checkout["subscription"])
            subscription_name = checkout["metadata"]["subscription_name"]
            quantity = checkout["metadata"]["quantity"]
        else:
            subscription = stripe.Subscription.retrieve(request.session["subscription"])
            subscription_name = subscription["metadata"]["subscription_name"]
            quantity = subscription["metadata"]["quantity"]
        import datetime

        end_date = datetime.datetime.fromtimestamp(subscription["current_period_end"]).replace(tzinfo=pytz.utc)
        start_date = datetime.datetime.fromtimestamp(subscription["current_period_start"]).replace(tzinfo=pytz.utc)
        days = end_date - start_date
        plan = tmeta_plan.objects.get(plan_id=int(subscription_name))
        if subscriptions.objects.filter(client_id=user, is_active=True, plan_id=plan).exists():
            old_count = subscriptions.objects.get(client_id=user, is_active=True, plan_id=plan).no_of_users
            subscriptions.objects.filter(client_id=user, is_active=True).update(
                subscription_valid_till=end_date,
                subscription_start_ts=start_date,
                no_of_users=int(quantity),
            )
            if old_count > int(quantity):
                return Response({"data": "user_dec"})
            else:
                return Response({"data": "user_ase"})

        elif subscriptions.objects.filter(client_id=user, is_active=True).exists():
            if subscriptions.objects.filter(client_id=user, is_active=True, plan_id_id=1).exists():
                try:
                    domain = get_current_site(request)
                    htmly = get_template("email_templates/subscription.html")
                    subject, from_email, to = "Welcome Onboard", Host_mail, user.email
                    html_content = htmly.render(
                        {"user": user, "plan": plan, "end_date": end_date}
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
                        "img_1.png",
                        "img_2.png",
                        "img_3.png",
                    ]
                    for i in image_data:
                        msg.attach(logo_data(i))
                    msg.send()
                except Exception as e:
                    pass
            subscriptions.objects.filter(client_id=user, is_active=True).update(
                has_client_changed_subscription=True,
                is_active=False,
                subscription_changed_date=timezone.now(),
            )
        features_balance = plan_features.objects.filter(plan_id=plan, feature_id_id__in=[10, 12])
        credits = plan_features.objects.filter(plan_id=plan, feature_id_id=11)
        if not client_features_balance.objects.filter(client_id=user, feature_id_id=11).exists():
            client_features_balance.objects.create(client_id=user, feature_id_id=11, available_count=0)
        subscriptions.objects.get_or_create(
            client_id=user,
            plan_id=plan,
            no_of_users=int(quantity),
            subscription_valid_till=end_date,
            subscription_start_ts=start_date,
            updated_by=user.username,
            subscription_remains_days=int(days.days),
        )
        for i in features_balance:
            if client_features_balance.objects.filter(client_id=user, feature_id=i.feature_id).exists():
                if i.feature_id.pk == 10:
                    available_count = client_features_balance.objects.get(client_id=user, feature_id=i.feature_id).available_count
                    balance_job = JD_form.objects.filter(user_id=user, jd_status_id=1).count()
                    if i.feature_value == None:
                        total = i.feature_value
                    else:
                        total = i.feature_value - balance_job
                    client_features_balance.objects.filter(client_id=user,feature_id=i.feature_id).update(available_count=total)
                if i.feature_id.pk == 12:
                    available_count = client_features_balance.objects.get(
                        client_id=user, feature_id=i.feature_id
                    ).available_count
                    balance_can = employer_pool.objects.filter(
                        client_id=user,
                    ).count()
                    if i.feature_value == None:
                        total = i.feature_value
                    else:
                        total = i.feature_value - balance_can

                    client_features_balance.objects.filter(
                        client_id=user,
                        feature_id=i.feature_id,
                    ).update(
                        available_count=total,
                    )
            else:
                client_features_balance.objects.create(
                    client_id=user,
                    feature_id=i.feature_id,
                    available_count=i.feature_value,
                )

        return Response({"data": "success"})


import datetime


class order_summary(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        request = self.request
        user, updated_by = admin_account(request)
        has_permission = user_permission(request, "manage_account_settings")
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        plan_id = int(request.GET["key"])
        state = request.GET["state"]
        if (
            state == False
            or state == "False"
            or state == "false"
            and not "discounts" in request.GET
        ):
            if len(ast.literal_eval(request.GET["add_on_id"])) >= 1:
                local_sub = subscriptions.objects.filter(client_id=user).values()
                plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
                plan_detail = tmeta_plan.objects.filter(plan_id=plan_id).values()[0]
                local_sub = local_sub.annotate(
                    days=Subquery(
                        tmeta_plan.objects.filter(plan_id=plan_id).values(
                            "subscription_value_days"
                        )
                    ),
                    plan_name=Subquery(
                        tmeta_plan.objects.filter(plan_id=plan_id).values("plan_name")
                    ),
                )
                local_sub = local_sub.last()
                subscription_cus = SubscriptionCustomer.objects.filter(
                    user=user
                ).values()[0]
                addon_response = []
                add_on_total = 0
                add_on_id = ast.literal_eval(request.GET["add_on_id"])
                add_on_count = ast.literal_eval(request.GET["add_on_count"])
                zipped_data = list(zip(add_on_id, add_on_count))
                sorted_list = sorted(zipped_data, key=lambda x: x[0])
                add_on_id, add_on_count = zip(*sorted_list)
                add_on_id = list(add_on_id)
                add_on_count = list(add_on_count)
                addon_contens = list(
                    addons_plan_features.objects.filter(
                        plan_id=plan_id, addon__in=add_on_id
                    ).values("addon", "price", "value", "carry_forward", "addon__name")
                )
                addon_contens = sorted(addon_contens, key=lambda x: x["addon"])
                for item, i in zip(addon_contens, add_on_count):
                    item["addon_count"] = i
                    item["addon_price"] = int(item["price"]) * item["addon_count"]
                    add_on_total = add_on_total + int(item["addon_price"])
                    addon_response.append(item)
                context = {
                    "plan": plan_detail,
                    "local_sub": local_sub,
                    "addon_response": addon_response,
                    "add_on_total": add_on_total,
                }
                return Response(context)
        if not has_permission == True:
            return render(
                request, "jobs/no_permission.html", {"permission": permission}
            )
        subscription_cus = SubscriptionCustomer.objects.get(user=user)
        plan = tmeta_plan.objects.get(plan_id=int(request.GET["key"]))
        proration_date = int(time.time())
        try:
            local_sub = subscriptions.objects.filter(client_id=user).last()
        except:
            pass
        update_user = 0
        if local_sub.plan_id.pk == plan.pk:
            update_user = 1
        if "discounts" in request.GET:
            request.session["discounts"] = request.GET["discounts"]
        if "key" in request.GET and request.method == "GET":
            plan = tmeta_plan.objects.get(plan_id=int(request.GET["key"]))
            subscription = stripe.Subscription.retrieve(subscription_cus.stripeSubscriptionId)
            count = request.GET["c"]
            items = [
                {
                    "id": subscription["items"]["data"][0].id,
                    "price": plan.stripe_id,
                    "quantity": request.GET["c"],
                }
            ]
            request.session["items"] = items
            request.session["subscription"] = subscription.id
            canceled_status = stripe.Subscription.retrieve(subscription_cus.stripeSubscriptionId)
            print(request.session.get("discounts"),"+++++++++++++=","update_user",update_user)
            if canceled_status.status == "canceled":
                invoice = stripe.Invoice.upcoming(customer=subscription_cus.stripeCustomerId)
            else:
                try:
                    if discount_codes_claimed.objects.filter(subscription_id=local_sub,discount_id=discounts.objects.get(discount_code=request.session["discounts"])).exists():
                        del request.session["discounts"]
                    if update_user == 0:
                        invoice = stripe.Invoice.upcoming(
                            customer=subscription_cus.stripeCustomerId,
                            subscription=subscription_cus.stripeSubscriptionId,
                            subscription_items=items,
                            subscription_proration_behavior="always_invoice",
                            subscription_billing_cycle_anchor="now",
                            coupon=request.session["discounts"],
                            # automatic_tax={
                            #   "enabled": True,
                            # },
                            subscription_proration_date=proration_date,
                        )
                    else:
                        invoice = stripe.Invoice.upcoming(
                            customer=subscription_cus.stripeCustomerId,
                            subscription=subscription_cus.stripeSubscriptionId,
                            subscription_items=items,
                            subscription_proration_behavior="always_invoice",
                            coupon=request.session["discounts"],
                            # automatic_tax={
                            #   "enabled": True,
                            # },
                            subscription_proration_date=proration_date,
                        )
                except Exception as e:
                    print("Order Summary Exception in GETT",e,update_user)
                    if update_user == 0:
                        invoice = stripe.Invoice.upcoming(
                            customer=subscription_cus.stripeCustomerId,
                            subscription=subscription_cus.stripeSubscriptionId,
                            subscription_items=items,
                            subscription_proration_behavior="always_invoice",
                            subscription_billing_cycle_anchor="now",
                            # automatic_tax={
                            #      "enabled": True,
                            #    },
                            subscription_proration_date=proration_date,
                        )
                    else:
                        invoice = stripe.Invoice.upcoming(
                            customer=subscription_cus.stripeCustomerId,
                            subscription=subscription_cus.stripeSubscriptionId,
                            subscription_items=items,
                            # automatic_tax={
                            #   "enabled": True,
                            # },
                            subscription_proration_behavior="always_invoice",
                            subscription_proration_date=proration_date,
                        )
            print("invoice@@@@@@@@@@@@@@@",invoice)
            un_used = invoice["lines"]["data"][0].amount / 100
            request.session["proration_date"] = proration_date
            new_price = invoice["lines"]["data"][-1].amount / 100
            final = invoice["total"] / 100
            subtotal = invoice["subtotal"] / 100
            print("stripe_balance@@",subtotal,final)
            if subtotal != final:
                subtotal = final

            tax_list = []
            if final < 0:
                available_balance = final
            else:
                available_balance = 0
            try:
                stripe_balance = stripe.Customer.list_balance_transactions(subscription_cus.stripeCustomerId)
                print("stripe_balance@@@@@@@",stripe_balance)
                try:
                    stripe_balance = stripe_balance.get("data")
                    if stripe_balance and len(stripe_balance) > 1:
                        stripe_balance = stripe_balance[0]["ending_balance"]
                        stripe_balance = (stripe_balance)/100
                    else:
                        stripe_balance = 0
                    # stripe_balance = (stripe_balance["data"][0]["ending_balance"]) / 100
                except:
                    stripe_balance = 0
            except:
                stripe_balance = 0
                
            try:
                total_discount_amounts = (invoice["total_discount_amounts"][0]["amount"] / 100)
            except:
                total_discount_amounts = 0
            if round(final) < 0 and stripe_balance != 0 and available_balance == 0:
                final = final - stripe_balance
            else:
                final = final + stripe_balance
                # available_balance = 0
            if final < 0:
                stripe_balance = subtotal
                final = "0.00"
            else:
                available_balance = 0

            if subtotal < 0:
                subtotal = 0.00
            try:
                discount_added = False
                if discounts.objects.filter(discount_code=request.session["discounts"]).exists():
                    discount_added = discounts.objects.filter(discount_code=request.session["discounts"]).values()[0]
                if discounts_addon.objects.filter(discount_code=request.session["discounts"]).exists():
                    discount_added = discounts_addon.objects.filter(discount_code=request.session["discounts"]).values()[0]


            except:
                discount_added = False
            from datetime import timedelta
            from django.utils import timezone

            date = local_sub.subscription_start_ts + timezone.timedelta(days=plan.subscription_value_days)
            plan_detail = tmeta_plan.objects.filter(plan_id=int(request.GET["key"])).values()[0]
            local_sub = subscriptions.objects.filter(client_id=user).values()
            plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
            local_sub = local_sub.annotate(
                days=Subquery(tmeta_plan.objects.filter(plan_id=plan_id).values("subscription_value_days")),
                plan_name=Subquery(tmeta_plan.objects.filter(plan_id=plan_id).values("plan_name")),
            )
            local_sub = local_sub.last()
            subscription_cus = {}
            if SubscriptionCustomer.objects.filter(user=user).exists():
                subscription_cus = SubscriptionCustomer.objects.filter(user=user).values()[0]
            addon_response = []
            add_on_total = 0
            print("FInalllll",final)
            if "add_on_id" in request.GET:
                if len(ast.literal_eval(request.GET["add_on_id"])) >= 1:
                    add_on_id = ast.literal_eval(request.GET["add_on_id"])
                    add_on_count = ast.literal_eval(request.GET["add_on_count"])
                    addon_contens = list(addons_plan_features.objects.filter(plan_id=int(request.GET["key"]), addon__in=add_on_id).values("addon", "price", "value", "carry_forward", "addon__name"))
                    for item, i in zip(addon_contens, add_on_count):
                        item["addon_count"] = i
                        item["addon_price"] = int(item["price"]) * item["addon_count"]
                        add_on_total = add_on_total + int(item["addon_price"])
                        addon_response.append(item)
                    if "discounts" in request.GET:
                        if request.GET["discounts"] != "":
                            print("###########ENTERRRRR",invoice.get("discount"))
                            if invoice.get("discount"):
                                percent = (invoice.get("discount", {}).get("coupon", {}).get("percent_off"))
                                if percent == None:
                                    percent = (invoice.get("discount", {}).get("coupon", {}).get("amount_off"))
                                if isinstance(final,str):
                                    final = float(final)
                                print(final,"percent",percent)
                                reduction_amount = None
                                if discounts.objects.filter(discount_code=request.session["discounts"]).exists():
                                    reduction_amount = discounts.objects.get(discount_code=request.session["discounts"])
                                if discounts_addon.objects.filter(discount_code=request.session["discounts"]).exists():
                                    reduction_amount = discounts_addon.objects.get(discount_code=request.session["discounts"])
                                print("reduction_amount@@@@",reduction_amount)
                                if isinstance(reduction_amount,dict):
                                    reduce_type = reduction_amount.discount_type
                                    reduce_amount = reduction_amount.discount_value
                                    if reduce_type == "Fixed":
                                        final = max(final - reduce_amount,0)
                                        subtotal = final
                                    elif reduce_type == "Percentage":
                                        final = final - round((final * percent) / 100)
                                        subtotal = final
                                    else:
                                        final = final - round((final * percent) / 100)
                                        subtotal = final
                                    print("+++++!!!!!!!",final,subtotal)
                        if request.GET["discounts"] == "" and state == 'false':
                            print("_____#######",add_on_total,final,new_price)
                            final = 0
                            new_price = 0
                    if discounts_addon.objects.filter(discount_code=request.session.get("discounts")).exists():
                        addon_reduce = discounts_addon.objects.get(discount_code=request.session.get("discounts"))
                        reduce_amount = addon_reduce.discount_value
                        final_addon = add_on_total
                        if addon_reduce.discount_type == 'Fixed':
                            add_on_total = max(add_on_total - reduce_amount,0)
                        if addon_reduce.discount_type == 'Percentage':
                            add_on_total = add_on_total - round((add_on_total * reduce_amount) / 100)
                        if "discounts" in request.GET:
                            if request.GET["discounts"] != "" and invoice.get('discount') == None:
                                print("__#_#(@((@(@()))))")
                                final = final
                                new_price = 0
                            if request.GET["discounts"] != "":
                                final = final
                                if addon_reduce.discount_type == 'Fixed':
                                    total_discount_amounts = reduce_amount
                                if addon_reduce.discount_type == 'Percentage':
                                    total_discount_amounts = round((final_addon * reduce_amount) / 100)
                                if state == 'false':
                                    final = 0
                                new_price = add_on_total
                                print("@@_@__@_@_@_@_!_!_!+!+!+",final,add_on_total,total_discount_amounts)
                        
                    print("finalfinal@@@",final)
                    if int(float(final)) < 0:
                        final = 0
                        add_on_total = 0
                        

            if "discounts" in request.GET:   #### Min Amount is Required Condition
                if discounts.objects.filter(discount_code=request.GET["discounts"]).exists():
                    discount = discounts.objects.get(discount_code=request.GET["discounts"])
                    min_amount = discount.min_amount
                    if int(float(final)) > 1:
                        if int(float(final)) < int(min_amount):
                            return Response({
                                "success":False,
                                "message":"Minimum purchase required for this coupon",
                                "coupon":"subscription",
                                "amount":min_amount,
                                "plan": plan_detail,
                                "un_used": un_used,
                                "count": count,
                                "final": final,
                                "available_balance": available_balance,
                                "total_discount_amounts": total_discount_amounts,
                                "local_sub": local_sub,
                                "date": date,
                                "tax_list": tax_list,
                                "stripe_balance": stripe_balance,
                                "permission": permission,
                                "discount_added": discount_added,
                                "update_user": update_user,
                                "subtotal": subtotal,
                                "subscription_cus": subscription_cus,
                                "new_price": new_price,
                                "addon_response": addon_response,
                                "add_on_total": add_on_total,
                                })
                if discounts_addon.objects.filter(discount_code=request.GET["discounts"]).exists():
                    discount = discounts_addon.objects.get(discount_code=request.GET["discounts"])
                    min_amount = discount.min_amount
                    print("final",final)
                    if int(float(final)) > 1:
                        if int(float(final)) < int(min_amount):
                            return Response({
                                "success":False,
                                "message":"Minimum purchase required for this coupon",
                                "coupon":"addon",
                                "amount":min_amount,
                                "plan": plan_detail,
                                "un_used": un_used,
                                "count": count,
                                "final": final,
                                "available_balance": available_balance,
                                "total_discount_amounts": total_discount_amounts,
                                "local_sub": local_sub,
                                "date": date,
                                "tax_list": tax_list,
                                "stripe_balance": stripe_balance,
                                "permission": permission,
                                "discount_added": discount_added,
                                "update_user": update_user,
                                "subtotal": subtotal,
                                "subscription_cus": subscription_cus,
                                "new_price": new_price,
                                "addon_response": addon_response,
                                "add_on_total": add_on_total,
                                })
            print("final@@@@@@",final,type(final),subtotal)
            if isinstance(final,float):
                final = str(final)
                if len(final) > 6:
                    final = round(float(final), 2)  
            context = {
                "plan": plan_detail,
                "un_used": un_used,
                "count": count,
                "final": final,
                "available_balance": available_balance,
                "total_discount_amounts": total_discount_amounts,
                "local_sub": local_sub,
                "date": date,
                "tax_list": tax_list,
                "stripe_balance": stripe_balance,
                "permission": permission,
                "discount_added": discount_added,
                "update_user": update_user,
                "subtotal": subtotal,
                "subscription_cus": subscription_cus,
                "new_price": new_price,
                "addon_response": addon_response,
                "add_on_total": add_on_total,
            }
            return Response(context)

    def post(self,request,):
        request = self.request
        user, updated_by = admin_account(request)
        has_permission = user_permission(request, "manage_account_settings")
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        if not has_permission == True:
            return render(
                request, "jobs/no_permission.html", {"permission": permission}
            )
        subscription_cus = SubscriptionCustomer.objects.get(user=user)
        try:
            subscription = stripe.Subscription.retrieve(subscription_cus.stripeSubscriptionId)
        except:
            return Response({"success":False,"message":"Subscription Id not Found in Stripe Database"})
        keys = request.POST["key"]
        count = request.POST["c"]
        addon_coupon = request.POST.get("addon")
        add_on_id = request.POST.get("addon_status")
        if add_on_id == 'false':
            add_on_id = None
        plan = tmeta_plan.objects.get(plan_id=keys)
        proration_date = int(time.time())
        request.session["proration_date"] = proration_date
        local_sub = subscriptions.objects.filter(client_id=user).last()
        update_user = 0
        if local_sub.plan_id.pk == plan.pk:
            update_user = 1
        items = [
            {
                "id": subscription["items"]["data"][0].id,
                "price": plan.stripe_id,
                "quantity": count,
            }
        ]
        request.session["items"] = items
        request.session["subscription"] = subscription.id
        if "discounts" in request.POST and request.POST["discounts"] != "":
            request.session["discounts"] = request.POST["discounts"]
            if discounts_addon.objects.filter(discount_code=request.POST.get("discounts")).exists():
                request.session["discounts"] = ''
        # else:
        #     request.session['discounts'] = request.POST['discounts']
        if "update" in request.POST:
            try:
                if update_user == 0:
                    update_stripe = stripe.Subscription.modify(
                        request.session["subscription"],
                        cancel_at_period_end=False,
                        proration_behavior="always_invoice",
                        proration_date=request.session["proration_date"],
                        items=request.session["items"],
                        billing_cycle_anchor="now",
                        coupon=request.session["discounts"],
                        metadata={
                            "subscription_name": keys,
                            "quantity": count,
                        },
                    )
                else:
                    update_stripe = stripe.Subscription.modify(
                        request.session["subscription"],
                        cancel_at_period_end=False,
                        proration_behavior="always_invoice",
                        proration_date=request.session["proration_date"],
                        items=request.session["items"],
                        coupon=request.session["discounts"],
                        metadata={
                            "subscription_name": keys,
                            "quantity": count,
                        },
                    )
                # discount_codes_claimed.objects.get_or_create(
                #     client_id=user,
                #     discount_id=discounts.objects.get(
                #         discount_code=request.session["discounts"]
                #     ),
                #     subscription_id=local_sub,
                # )
            except:
                if update_user == 0:
                    update_stripe = stripe.Subscription.modify(
                        request.session["subscription"],
                        cancel_at_period_end=False,
                        proration_behavior="always_invoice",
                        proration_date=request.session["proration_date"],
                        items=request.session["items"],
                        billing_cycle_anchor="now",
                        metadata={
                            "subscription_name": keys,
                            "quantity": count,
                        },
                    )
                else:
                    update_stripe = stripe.Subscription.modify(
                        request.session["subscription"],
                        cancel_at_period_end=False,
                        proration_behavior="always_invoice",
                        proration_date=request.session["proration_date"],
                        items=request.session["items"],
                        metadata={
                            "subscription_name": keys,
                            "quantity": count,
                        },
                    )
            if "add_on_id" in request.POST:
                add_on_id = ast.literal_eval(request.GET["add_on_id"])
                add_on_count = ast.literal_eval(request.GET["add_on_count"])
                for addon, count in zip(add_on_id, add_on_count):
                    feature_id = add_ons(user, addon, count)
                    subs_add_on_creation(user, count, feature_id, addon)
            amount = update_stripe["items"]["data"][0]["plan"]["amount"]
            customer_id = update_stripe.get("customer", None)
            update_value = False
            finalvalue = request.POST.get("finalvalue", None)
            if "live" in settings.STRIPE_SECRET_KEY:
                if Invoice_retrieve(customer_id, finalvalue) == True:
                    update_value = True
            else:
                update_value = True
            return Response({"update": update_value})
        elif "discounts" in request.POST:
            domain_url = request.build_absolute_uri()
            from django.utils import timezone
            try:
                
                ''' BY CHecking Two Coupon At a Time'''
                if ',' in request.POST["discounts"]: ## by checking Two Promo Code
                    return Response({"success": True, "url": domain_url, "msg": "9Promo code invalid","message": 'Only one coupon allowed per transaction','id':9})
                

                # ''' Checking the Coupon is Exists in Stripe Accounts'''
                # if verify_Coupon(request.POST["discounts"]):
                #     return Response({"success": True, "url": domain_url, "msg": "7Promo code invalid","message": 'Coupon not applicable to selected items','id':7})
                

                '''Invalid & Valid Coupon Validations For Subscription & Addons'''
                if not discounts.objects.filter(discount_name=request.POST["discounts"]).exists() and addon_coupon == None and add_on_id == None:    ## coupon code is Invalid for Subscription
                    if discounts_addon.objects.filter(discount_name=request.POST["discounts"]).exists():
                        return Response({"success": True, "url": domain_url, "msg": "6Promo code invalid","message": 'This coupon is valid for add-ons only','id':6.1})
                    return Response({"success": True, "url": domain_url, "msg": "3Promo code invalid","message": 'Invalid coupon code','id':3.1})
                if not discounts.objects.filter(discount_name=request.POST["discounts"]).exists() and addon_coupon and add_on_id:    ## coupon code is Invalid for Subscription
                    if not discounts_addon.objects.filter(discount_name=request.POST["discounts"]).exists():
                        return Response({"success": True, "url": domain_url, "msg": "3Promo code invalid","message": 'Invalid coupon code','id':3.1})
                if not discounts_addon.objects.filter(discount_name=request.POST["discounts"]).exists() and addon_coupon and add_on_id == None:   ## coupon code is Invalid For Addon
                    if discounts.objects.filter(discount_name=request.POST["discounts"]).exists():
                        print("####",addon_coupon,"add_on_id",add_on_id)
                        if addon_coupon:
                            return Response({"success": True, "url": domain_url, "msg": "6Promo code invalid","message": 'This coupon is valid for subscriptions only','id':6.2})
                    if addon_coupon:
                        return Response({"success": True, "url": domain_url, "msg": "3Promo code invalid", "message": 'Invalid coupon code','id':3.2})

                '''### Here its the Subscripion Validation'''
                if discounts.objects.filter(discount_name=request.POST["discounts"],is_active = True).exists():
                    discount = discounts.objects.get(discount_name=request.POST["discounts"])
                
                    ## start_date validation for coupon code 
                    if not discount.discount_start_date == None:
                        if discount.discount_start_date > timezone.now():
                            coupon_start_date = discount.discount_start_date.date()
                            return Response({
                                    "success": True,
                                    "url": domain_url,
                                    "msg": "1Promo code invalid",
                                    "date": discount.discount_start_date,
                                    "message":f"Coupon Code in Apply on {coupon_start_date}",'id':1.1})

                    ## end_date validation for coupon code 
                    if not discount.discount_end_date == None:
                        if discount.discount_end_date < timezone.now():
                            return Response({
                                    "success": True,
                                    "url": domain_url,
                                    "msg": "1Promo code invalid",
                                    "message":"This coupon has expired",'id':1.2})
                    
                    if discount.plan_id:
                        if int(discount.plan_id.plan_id) != int(keys):
                            return Response({"success": True,"url": domain_url,"msg": "4Promo code invalid","message":"The coupon is not applicable to this plan.",'id':4.1})

                    ## Discounts Features Addons Checking
                    subs_list = discounts_features.objects.filter(discount_id = discount,plan_id = keys).values_list('plan_id',flat=True)
                    subs_list = list(subs_list)
                    subs_exists = True if int(keys) in subs_list else False
                    print("subs_list@@@@@@@@",subs_list,subs_exists,keys)
                    if subs_exists == False:
                        return Response({"success": True, "url": domain_url, "msg": "7Promo code invalid","message": 'Coupon not applicable to selected items','id':7})

                    '''Redeem By This User'''
                    if discount_codes_claimed.objects.filter(client_id = user,discount_id=discount,discount_addon_id=None,is_claimed = True).exists():     ###### Already Reddem Check BY Subscription Based on USer
                        return Response({"success": True,"url": domain_url,"msg": "8Promo code invalid",'message':'This coupon has already been redeemed','id':8.1})
                    elif discount.usage_per_client == "Single" and discount_codes_claimed.objects.filter(discount_id=discount,is_claimed = True).exists():  ##### Per Coupon As Per Transaction Only
                        return Response({"success": True,"url": domain_url,"msg": "5Promo code invalid",'message':'Only one coupon allowed per transaction','id':5})
                    else:
                        if local_sub.plan_id.plan_id > 1:
                            request.session["discounts"] = discount.discount_code
                            request.session["min_amount"] = discount.min_amount
                            discount_added = True
                        else:  ##For Free Trial User Enter this Page
                            return Response({"success": True,"url": domain_url,"msg": "2Promo code invalid",'id':2})

                if discounts.objects.filter(discount_name=request.POST["discounts"],is_active = False).exists():    ### Inactive Code for Subscription
                    return Response({"success": True,"url": domain_url,"msg": "2Promo code invalid",'message':'This Coupon Code is Inactive For Subscription','id':2.1})

                
                '''### Here its the Addon Validation'''
                if addon_coupon and discounts_addon.objects.filter(discount_name=request.POST["discounts"]).exists():
                    discount = discounts_addon.objects.get(discount_name=request.POST["discounts"])

                    ## start_date validation for coupon code 
                    if not discount.discount_start_date == None:
                        if discount.discount_start_date > timezone.now():
                            coupon_start_date = discount.discount_start_date.date()
                            return Response({
                                    "success": True,
                                    "url": domain_url,
                                    "msg": "1Promo code invalid",
                                    "date": discount.discount_start_date,
                                    "message":f"Coupon Code in Apply on {coupon_start_date}",'id':1.3})

                    ## end_date validation for coupon code 
                    if not discount.discount_end_date == None:
                        if discount.discount_end_date < timezone.now():
                            return Response({
                                    "success": True,
                                    "url": domain_url,
                                    "msg": "1Promo code invalid",
                                    "message":"Coupon Code in Expired",'id':1.4})
                    
                    ## Discounts Features Addons Checking
                    addon_list = discounts_features.objects.filter(discount_addon = discount,plan_id = keys).values_list('addon_id',flat=True)
                    addon_list = list(addon_list)
                    addon_exists = any(str(item) in addon_coupon for item in addon_list)
                    print("addon_list@@@@@@@@",addon_list,addon_coupon,addon_exists)
                    if addon_exists == False:
                        return Response({"success": True, "url": domain_url, "msg": "7Promo code invalid","message": 'Coupon not applicable to selected items','id':7})

                    if discount_codes_claimed.objects.filter(client_id = user,discount_addon_id=discount,discount_id=None,is_claimed = True).exists():  ###### Already Reddem Check BY Addon Based on USer
                        return Response({"success": True,"url": domain_url,"msg": "8Promo code invalid",'message':'This Addon Coupon Already Redeem By This User','id':8.2})
                    elif discount.usage_per_client == "Single" and discount_codes_claimed.objects.filter(discount_addon_id=discount,is_claimed = True).exists():  ##### Per Coupon As Per Transaction Only
                        return Response({"success": True,"url": domain_url,"msg": "5Promo code invalid",'message':'Only one coupon allowed per transaction','id':5})
                    else:
                        if local_sub.plan_id.plan_id > 1:
                            request.session["discounts"] = discount.discount_code
                            request.session["min_amount"] = discount.min_amount
                            discount_added = True
                        else:   ##For Free Trial User Enter this Page
                            return Response({"success": True,"url": domain_url,"msg": "2Promo code invalid",'id':2})
                    ##################################

                if addon_coupon and discounts_addon.objects.filter(discount_name=request.POST["discounts"],is_active = False).exists():
                    return Response({"success": True,"url": domain_url,"msg": "2Promo code invalid",'message':'Coupon Code is Inactive For Addon','id':2.2})
                    
               

            except Exception as e:
                print("Order Summary Exceptions",e)
                pass
                discount_added = 2


            '''User Specific Handled for Subscription'''
            if discounts.objects.filter(discount_name=request.POST["discounts"]).exists():
                discount = discounts.objects.get(discount_name=request.POST["discounts"])
                if not discount_user.objects.filter(client_id = user,discount_id = discount).exists():
                    return Response({"success": True,"url": domain_url,"msg": "10Promo code invalid","message": "The coupon is not applicable to this user.",'id':10})
                if discount_user.objects.filter(client_id = user,discount_id = discount).exists():
                    discount = discount_user.objects.get(client_id = user,discount_id = discount)
                    if not discount.discount_start_date == None:
                        if discount.discount_start_date > timezone.now():
                            coupon_start_date = discount.discount_start_date.date()
                            return Response({
                                    "success": True,
                                    "url": domain_url,
                                    "msg": "1Promo code invalid",
                                    "date": discount.discount_start_date,
                                    "message":f"Coupon Code in Apply {coupon_start_date}",'id':1.3})

                    ## end_date validation for coupon code 
                    if not discount.discount_end_date == None:
                        if discount.discount_end_date < timezone.now():
                            return Response({
                                    "success": True,
                                    "url": domain_url,
                                    "msg": "1Promo code invalid",
                                    "message":"Coupon Code in Expired",'id':1.4})


            '''User Specific Handled for ADD-ONS'''
            if discounts_addon.objects.filter(discount_name=request.POST["discounts"]).exists():
                discount = discounts_addon.objects.get(discount_name=request.POST["discounts"])
                if not discount_user.objects.filter(client_id = user,discount_addon = discount).exists():
                    return Response({"success": True,"url": domain_url,"msg": "10Promo code invalid","message": "The coupon is not applicable to this user.",'id':10})
                if discount_user.objects.filter(client_id = user,discount_addon = discount).exists():
                    discount = discount_user.objects.get(client_id = user,discount_addon = discount)
                    if not discount.discount_start_date == None:
                            if discount.discount_start_date > timezone.now():
                                coupon_start_date = discount.discount_start_date.date()
                                return Response({
                                        "success": True,
                                        "url": domain_url,
                                        "msg": "1Promo code invalid",
                                        "date": discount.discount_start_date,
                                        "message":f"Coupon Code in Apply on {coupon_start_date}",'id':1.3})

                    ## end_date validation for coupon code 
                    if not discount.discount_end_date == None:
                        if discount.discount_end_date < timezone.now():
                            return Response({
                                    "success": True,
                                    "url": domain_url,
                                    "msg": "1Promo code invalid",
                                    "message":"Coupon Code in Expired",'id':1.4})


            return Response({
                    "success": True,
                    "url": domain_url,
                    "discounts": request.session["discounts"],
                    "min_amount": request.session.get("min_amount",0)})
        else:
            domain_url = request.build_absolute_uri()
            billing_portal = stripe.billing_portal.Session.create(
                customer=subscription_cus.stripeCustomerId,
                return_url=domain_url,
            )

            return Response({"success": True, "url": billing_portal["url"]})


class renew_subscription(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        from django.utils import timezone

        user, updated_by = admin_account(request)
        subscription_cus = SubscriptionCustomer.objects.get(user=user)
        plan = tmeta_plan.objects.get(plan_id=int(request.GET["key"]))
        subscription = stripe.Subscription.retrieve(
            subscription_cus.stripeSubscriptionId
        )
        domain_url = settings.CLIENT_URL
        if subscription.status == "canceled":
            checkout_session = stripe.Subscription.create(
                customer=subscription_cus.stripeCustomerId,
                items=[{"price": plan.stripe_id}],
                proration_behavior="always_invoice",
            )
            subscription_cus.stripeSubscriptionId = checkout_session.id
            subscription_cus.save()
            subscription = stripe.Subscription.retrieve(checkout_session.id)
            import datetime

            start_date = datetime.datetime.fromtimestamp(
                subscription["current_period_start"]
            ).replace(tzinfo=pytz.utc)
            if subscriptions.objects.filter(client_id=user, is_active=True).exists():
                subscriptions.objects.filter(client_id=user).update(is_active=False)
            subscriptions.objects.create(
                client_id=user,
                is_active=True,
                has_client_changed_subscription=False,
                subscription_changed_date=None,
                subscription_changed_to=None,
                subscription_remains_days=plan.subscription_value_days,
                subscription_valid_till=timezone.now()
                + timezone.timedelta(days=plan.subscription_value_days - 1),
                subscription_end_ts=timezone.now()
                + timezone.timedelta(days=plan.subscription_value_days - 1),
                updated_by=request.user.username,
                subscription_start_ts=start_date,
                plan_id_id=plan.plan_id,
            )

            features_value = plan_features.objects.filter(
                plan_id=request.GET["key"], feature_id_id__in=[10, 27, 53, 6]
            )
            for i in features_value:
                if client_features_balance.objects.filter(
                    client_id=user, feature_id=i.feature_id
                ).exists():
                    client_features_balance.objects.filter(
                        client_id=user, feature_id=i.feature_id
                    ).update(
                        available_count=i.feature_value, plan_count=i.feature_value
                    )
        else:
            stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=False,
                proration_behavior="always_invoice",
                billing_cycle_anchor="now",
                items=[
                    {
                        "id": subscription["items"]["data"][0].id,
                        "price": plan.stripe_id,
                    }
                ],
            )
            last_sub = None
            if subscriptions.objects.filter(client_id=user, is_active=True).exists():
                last_sub = (
                    subscriptions.objects.filter(client_id=user, is_active=True)
                    .last()
                    .subscription_id
                )
            if (
                subscriptions.objects.filter(
                    subscription_id=last_sub, subscription_changed_to=-2
                ).exists()
                and last_sub
            ):  # When the user renew AFTER the subscription end
                start_date = timezone.now()
                subscriptions.objects.filter(subscription_id=last_sub).update(
                    is_active=False
                )
                subscriptions.objects.create(
                    client_id=user,
                    is_active=True,
                    has_client_changed_subscription=False,
                    subscription_changed_date=None,
                    subscription_changed_to=None,
                    subscription_remains_days=plan.subscription_value_days,
                    subscription_valid_till=timezone.now()
                    + timezone.timedelta(days=plan.subscription_value_days - 1),
                    subscription_end_ts=timezone.now()
                    + timezone.timedelta(days=plan.subscription_value_days - 1),
                    updated_by=request.user.username,
                    subscription_start_ts=start_date,
                    plan_id_id=plan.plan_id,
                )
            else:  # When the user renew BEFORE the subscription end
                subscriptions.objects.filter(client_id=user, is_active=True).update(
                    has_client_changed_subscription=False,
                    subscription_changed_date=None,
                    subscription_changed_to=None,
                    subscription_remains_days=plan.subscription_value_days,
                    subscription_valid_till=timezone.now()
                    + timezone.timedelta(days=plan.subscription_value_days - 1),
                    subscription_end_ts=timezone.now()
                    + timezone.timedelta(days=plan.subscription_value_days - 1),
                    updated_by=request.user.username,
                    is_active=1,
                )

        subscription_sendmail(user, "renewal")
        return Response({"success": True})


class cancel_subscription(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request,
    ):
        request = self.request
        from django.utils import timezone

        domain = settings.CLIENT_URL
        user, updated_by = admin_account(request)
        subscription_cus = SubscriptionCustomer.objects.get(user=user)
        subscription = stripe.Subscription.retrieve(
            subscription_cus.stripeSubscriptionId
        )
        plan_sub = subscriptions.objects.get(client_id=user, is_active=True)
        if subscription.status == "canceled":
            checkout_session = stripe.Subscription.create(
                customer=subscription_cus.stripeCustomerId,
                items=[{"price": plan_sub.plan_id.stripe_id}],
                proration_behavior="always_invoice",
            )
            subscription_cus.stripeSubscriptionId = checkout_session.id
            subscription_cus.save()
            stripe.Subscription.modify(checkout_session.id, cancel_at_period_end=True)
        else:
            stripe.Subscription.modify(
                subscription_cus.stripeSubscriptionId, cancel_at_period_end=True
            )
        subscriptions.objects.filter(client_id=user, is_active=True).update(
            has_client_changed_subscription=True,
            subscription_changed_date=timezone.now(),
            subscription_changed_to=-1,
        )
        subscription = subscriptions.objects.get(client_id=user, is_active=True)
        for i in request.POST.getlist("feedback"):
            subscriptions_feedback.objects.get_or_create(
                user_id=user,
                subscription_id=subscriptions.objects.get(
                    client_id=user, is_active=True
                ),
                feedback=i,
            )
        if email_preference.objects.filter(
            user_id=user, stage_id_id=4, is_active=True
        ).exists():
            try:
                domain = settings.CLIENT_URL
                htmly = get_template("email_templates/subscription_cancelled.html")
                subject, from_email, to = (
                    "Your subscription has been cancelled successfully!!!",
                    Host_mail,
                    user.email,
                )
                html_content = htmly.render(
                    {"user": user, "subscription": subscription, "domain": domain}
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
                msg.mixed_subtype = "related"
                msg.send()
            except Exception as e:
                pass
        return Response({"success": True})


class billing_portal(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        domain_url = settings.CLIENT_URL
        user_id, updated_by = admin_account(request)
        try:
            CustomerId = SubscriptionCustomer.objects.get(user=user_id).stripeCustomerId
            stripe.api_key = settings.STRIPE_SECRET_KEY
            if "order_summary" in request.GET:
                billing_portal = stripe.billing_portal.Session.create(
                    customer=CustomerId,
                    return_url=request.GET["order_summary"],
                )
            else:
                billing_portal = stripe.billing_portal.Session.create(
                    customer=CustomerId,
                    return_url=domain_url + "/account_setting/subscription",
                )
            return Response({"success": True, "url": billing_portal["url"]})
        except SubscriptionCustomer.DoesNotExist:
            return Response(
                {"success": False, "message": "Free Trail has No Payment and Info"}
            )


@csrf_exempt
def stripe_config(request):
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@api_view(["GET", "POST"])
def create_checkout_session(request):
    user_id, updated_by = admin_account(request)
    if request.method == "GET":
        domain_url = settings.CLIENT_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            if "candicates" in request.GET:
                if "manage_sub" in request.GET:
                    url = domain_url + "/account_setting/subscription"
                else:
                    url = domain_url + "/talent_sourcing/"
                if "add_on" in request.GET:
                    add_on = request.GET.get("add_on", None)
                if "back_url" in request.GET:
                    success_url = (
                        domain_url
                        + request.GET["back_url"]
                        + "?session={CHECKOUT_SESSION_ID}"
                    )
                    cancel_url = (
                        domain_url + request.GET["back_url"] + "?cancelled={add_on}"
                    )
                else:
                    success_url = url + "?session={CHECKOUT_SESSION_ID}"
                    cancel_url = url + "?cancelled={add_on}"
                print("::::::",request.GET.get("discounts"))
                if discounts.objects.filter(discount_code=request.GET.get("discounts")).exists():
                    discounts_code = ''
                else:
                    discounts_code = request.GET.get("discounts", None)
                price_list = request.GET["plan"]
                count_list = request.GET["candicates"]
                price_list = ast.literal_eval(price_list)
                count_list = ast.literal_eval(count_list)
                result = [
                    {
                        "price": price,
                        "quantity": count,
                    }
                    for price, count in zip(price_list, count_list)
                ]

                request.session["source_candi"] = request.GET["candicates"]
                if SubscriptionCustomer.objects.filter(user=user_id).exists():
                    CustomerId = SubscriptionCustomer.objects.get(user=user_id).stripeCustomerId
                    print("discounts@@",discounts_code)
                    if 'discounts' in request.GET and discounts_code:
                        checkout_session = stripe.checkout.Session.create(
                            client_reference_id=user_id.id,
                            success_url=success_url,
                            cancel_url=cancel_url,
                            payment_method_types=["card"],
                            payment_intent_data={"setup_future_usage": "off_session"},
                            customer=CustomerId,
                            billing_address_collection="required",
                            mode="payment",
                            line_items=result,
                            discounts=[{"coupon":discounts_code}],
                            invoice_creation={"enabled": True},
                            metadata={
                                "product_name": add_on,
                                "quantity": request.GET["candicates"],
                            },
                        )
                    else:
                        checkout_session = stripe.checkout.Session.create(
                            client_reference_id=user_id.id,
                            success_url=success_url,
                            cancel_url=cancel_url,
                            payment_method_types=["card"],
                            payment_intent_data={"setup_future_usage": "off_session"},
                            customer=CustomerId,
                            billing_address_collection="required",
                            mode="payment",
                            line_items=result,
                            allow_promotion_codes=False,
                            invoice_creation={"enabled": True},
                            metadata={
                                "product_name": add_on,
                                "quantity": request.GET["candicates"],
                            },
                        )
                else:
                    if 'discounts' in request.GET and discounts_code:
                        checkout_session = stripe.checkout.Session.create(
                            client_reference_id=user_id.id,
                            success_url=success_url,
                            cancel_url=cancel_url,
                            payment_method_types=["card"],
                            payment_intent_data={"setup_future_usage": "off_session"},
                            customer_email=request.user.email,
                            billing_address_collection="required",
                            coupon=discounts_code if discounts_code else None,
                            mode="payment",
                            # line_items=[
                            #  {
                            #     'price': request.GET["plan"],
                            #     'quantity': request.GET['candicates'],
                            # }
                            # ],
                            allow_promotion_codes=True,
                            invoice_creation={
                                "enabled": True,
                            },
                            line_items=result,
                            metadata={
                                "product_name": add_on,
                                "quantity": request.GET["candicates"],
                            })
                    else:
                        checkout_session = stripe.checkout.Session.create(
                            client_reference_id=user_id.id,
                            success_url=success_url,
                            cancel_url=cancel_url,
                            payment_method_types=["card"],
                            payment_intent_data={"setup_future_usage": "off_session"},
                            customer_email=request.user.email,
                            billing_address_collection="required",
                            coupon=discounts if discounts else None,
                            mode="payment",
                            # line_items=[
                            #  {
                            #     'price': request.GET["plan"],
                            #     'quantity': request.GET['candicates'],
                            # }
                            # ],
                              allow_promotion_codes=False,
                            invoice_creation={
                                "enabled": True,
                            },
                            line_items=result,
                            metadata={
                                "product_name": add_on,
                                "quantity": request.GET["candicates"],
                            })
                return JsonResponse({
                        "sessionId": checkout_session["id"],
                        "checkout_session": checkout_session})
        except Exception as e:
            return JsonResponse({"error": str(e)})


@api_view(["GET", "POST"])
def create_subscription_session(request):
    if request.method == "GET":
        domain_url = settings.CLIENT_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user_id, updated_by = admin_account(request)
        if "back_url" in request.GET:
            cancel_url = domain_url + request.GET["back_url"]
            success_url = (
                domain_url
                + request.GET["back_url"]
                + "?session_id={CHECKOUT_SESSION_ID}"
            )
        else:
            cancel_url = domain_url + "/account_setting/subscription"
            first_value = subscriptions.objects.filter(client_id=user_id)
            success_url = (
                domain_url
                + "/account_setting/subscription?session_id={CHECKOUT_SESSION_ID}"
            )
            if len(first_value) == 1 and first_value.first().plan_id.pk > 1:
                success_url = (
                    domain_url
                    + "/account_setting/profiles?session_id={CHECKOUT_SESSION_ID}"
                )
        # try:
        price_list = request.GET["plan"]
        count_list = request.GET["count"]
        price_list = ast.literal_eval(price_list)
        count_list = ast.literal_eval(count_list)
        result = [
            {"price": price, "quantity": int(count)}
            for price, count in zip(price_list, count_list)
        ]
        if SubscriptionCustomer.objects.filter(user=user_id).exists():
            CustomerId = SubscriptionCustomer.objects.get(user=user_id).stripeCustomerId
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=user_id.id,
                success_url=success_url,
                cancel_url=cancel_url,
                payment_method_types=["card"],
                customer=CustomerId,
                billing_address_collection="required",
                mode="subscription",
                allow_promotion_codes=True,
                # line_items=[
                #     {
                #         'price': request.GET['plan'],
                #         'quantity': request.GET['count'],
                #     }
                # ],
                line_items=result,
                metadata={
                    "subscription_name": request.GET["plan_name"],
                    "quantity": request.GET["count"],
                },
            )
        else:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=user_id.id,
                success_url=success_url,
                cancel_url=cancel_url,
                payment_method_types=["card"],
                customer_email=request.user.email,
                billing_address_collection="required",
                mode="subscription",
                allow_promotion_codes=True,
                # line_items=[
                #     {
                #         'price': request.GET['plan'],
                #         'quantity': request.GET['count'],
                #     }
                # ],
                line_items=result,
                metadata={
                    "subscription_name": request.GET["plan_name"],
                    "quantity": request.GET["count"],
                },
            )
        return JsonResponse(
            {"sessionId": checkout_session["id"], "url": checkout_session}
        )
        # except Exception as e:
        #     return JsonResponse({'error': str(e)})


class backend_process(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        request = self.request
        user, updated_by = admin_account(request)
        # if request.GET["state"] == True:
        #     pass
        from django.utils import timezone
        checkout = None
        if "session_id" in request.GET:
            session_id = request.GET["session_id"]
            checkout = stripe.checkout.Session.retrieve(session_id)
            SubscriptionCustomer.objects.filter(user=user).delete()
            SubscriptionCustomer.objects.create(
                user=user,
                stripeCustomerId=checkout["customer"],
                stripeSubscriptionId=checkout["subscription"],
            )
            subscription = stripe.Subscription.retrieve(checkout["subscription"])
            subscription_name = checkout["metadata"]["subscription_name"]
            quantity = checkout["metadata"]["quantity"]
        else:
            subscription_cus = SubscriptionCustomer.objects.get(user=user)
            subscription__ = stripe.Subscription.retrieve(
                subscription_cus.stripeSubscriptionId
            )
            subscription = stripe.Subscription.retrieve(
                subscription__.id,
            )
            subscription_name = subscription["metadata"]["subscription_name"]
            quantity = subscription["metadata"]["quantity"]
        import datetime

        end_date = datetime.datetime.fromtimestamp(subscription["current_period_end"]).replace(tzinfo=pytz.utc)
        start_date = datetime.datetime.fromtimestamp(subscription["current_period_start"]).replace(tzinfo=pytz.utc)
        days = end_date - start_date
        plans = ""
        qual = quantity
        plans = subscription_name
        plan_list = []
        if "[" in qual:
            plan_list = ast.literal_eval(subscription_name)
            count_list = ast.literal_eval(quantity)
            subscription_name = plan_list[0]
            quantity = int(count_list[0])
        plan = tmeta_plan.objects.get(plan_id=int(subscription_name))
        if subscriptions.objects.filter(
            client_id=user, is_active=True, plan_id=plan
        ).exists():
            old_count = subscriptions.objects.get(client_id=user, is_active=True, plan_id=plan).no_of_users
            subscriptions.objects.filter(client_id=user, is_active=True).update(
                subscription_valid_till=end_date,
                subscription_start_ts=start_date,
                no_of_users=quantity,
            )
            if len(plan_list) > 1:
                addon_creation(user, plans, qual)
            subscription_sendmail(user)
            if int(old_count) > int(quantity):
                return Response({"success": True, "user_count": "user_dec"})
            else:
                return Response({"success": True, "user_count": "user_ase"})

        elif subscriptions.objects.filter(client_id=user, is_active=True).exists():
            if subscriptions.objects.filter(client_id=user, is_active=True, plan_id_id=1).exists():
                if email_preference.objects.filter(user_id=user, stage_id_id=2, is_active=True).exists():
                    try:
                        domain = get_current_site(request)
                        htmly = get_template("email_templates/subscription.html")
                        subject, from_email, to = (
                            "Welcome Onboard",
                            Host_mail,
                            user.email,
                        )
                        html_content = htmly.render(
                            {"user": user, "plan": plan, "end_date": end_date}
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
                            "img_1.png",
                            "img_2.png",
                            "img_3.png",
                        ]
                        for i in image_data:
                            msg.attach(logo_data(i))
                        msg.mixed_subtype = "related"
                    except Exception as e:
                        pass
            from django.utils import timezone

            subscriptions.objects.filter(client_id=user, is_active=True).update(
                has_client_changed_subscription=True,
                is_active=False,
                subscription_changed_date=timezone.now(),
            )
        else:
            if email_preference.objects.filter(
                user_id=user, stage_id_id=2, is_active=True
            ).exists():
                try:
                    domain = settings.CLIENT_URL
                    htmly = get_template("email_templates/subscription.html")
                    subject, from_email, to = "Welcome Onboard", Host_mail, user.email
                    html_content = htmly.render(
                        {"user": user, "plan": plan, "end_date": end_date}
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
                        "img_1.png",
                        "img_2.png",
                        "img_3.png",
                    ]
                    for i in image_data:
                        msg.attach(logo_data(i))
                    msg.mixed_subtype = "related"
                    msg.send()
                except Exception as e:
                    pass
        features_balance = plan_features.objects.filter(
            plan_id=plan, feature_id_id__in=[10, 27, 53, 6]
        )
        credits = plan_features.objects.filter(plan_id=plan, feature_id_id=11)
        # if not client_features_balance.objects.filter( client_id=user,feature_id_id=11).exists():
        #     client_features_balance.objects.create(client_id=user,feature_id_id=11,available_count = 0)
        subscriptions.objects.get_or_create(
            client_id=user,
            plan_id=plan,
            no_of_users=quantity,
            subscription_valid_till=end_date,
            subscription_start_ts=start_date,
            updated_by=user.username,
            subscription_remains_days=int(days.days),
        )
        delete_addon(user)
        for i in features_balance:
            feature_update = Plan_upgrade(user, i)

        addon_data = [51, 52, 58, 56]
        for x in addon_data:
            if client_features_balance.objects.filter(
                client_id=user, feature_id=x
            ).exists():
                add_counts = client_features_balance.objects.get(
                    client_id=user, feature_id=x
                ).available_count
                feature_ids = Count_increase(x)
                client_features_balance.objects.filter(
                    client_id=user, feature_id=feature_ids
                ).update(available_count=F("available_count") + add_counts)
        if len(plan_list) > 1:
            addon_creation(user, plans, qual)
        subscription_sendmail(user)
        invoice = subscription.latest_invoice
        if "session_id" in request.GET:
            invoice = None
        coupon_code_claimed = Coupon_claimed(checkout,invoice=invoice)
        return Response({"success": True})


from jobs.utils import *


class credits_purchase(generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request,
    ):
        request = self.request
        user_id, updated_by = admin_account(request)
        if "session" in request.GET:
            session_id = request.GET["session"]
            checkout = stripe.checkout.Session.retrieve(
                session_id,
            )
            metadata = checkout.get("metadata")
            product_name = metadata["product_name"]
            quantity = metadata["quantity"]
            quantity_total = ast.literal_eval(quantity)
            product_name_total = ast.literal_eval(product_name)
            for quantity, product_name in zip(quantity_total, product_name_total):
                addons_qual = quantity
                feature_id = add_ons(user_id, product_name, quantity)
                plan_id = (
                    subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
                )
                try:
                    available_count = client_features_balance.objects.get(
                        client_id=user_id, feature_id_id=feature_id
                    ).available_count
                    if client_features_balance.objects.filter(
                        client_id=user_id, feature_id_id=feature_id
                    ).exists():
                        plan_id = (subscriptions.objects.filter(client_id=user_id).last().plan_id.pk)
                        if addons_plan_features.objects.get(plan_id=plan_id, addon_id=product_name).value:
                            addons_feature_values = int(addons_qual) * int(
                                addons_plan_features.objects.get(
                                    plan_id=plan_id, addon_id=product_name
                                ).value
                            )
                            feature_values = (
                                int(
                                    client_features_balance.objects.get(
                                        client_id=user_id, feature_id_id=feature_id
                                    ).available_count
                                )
                                + addons_feature_values
                            )
                        else:
                            addons_feature_values = None
                            feature_values = None
                        client_features_balance.objects.filter(
                            client_id=user_id, feature_id_id=feature_id
                        ).update(
                            addons_count=F("addons_count") + addons_qual,
                            available_count=feature_values,
                        )
                except client_features_balance.DoesNotExist:
                    increase_count = addons_qual
                    tmeta_add = tmeta_addons.objects.get(id=product_name)
                    if addons_plan_features.objects.get(
                        plan_id=plan_id, addon_id=product_name
                    ).value:
                        addons_feature = int(addons_qual) * int(
                            addons_plan_features.objects.get(
                                plan_id=plan_id, addon_id=product_name
                            ).value
                        )
                    else:
                        addons_feature = None
                    client_features_balance.objects.create(
                        client_id=user_id,
                        feature_id_id=feature_id,
                        available_count=addons_feature,
                        add_ons=tmeta_add,
                        addons_count=increase_count,
                    )
                    available_count = client_features_balance.objects.get(
                        client_id=user_id, feature_id_id=feature_id
                    ).available_count
                quali = addons_plan_features.objects.get(
                    plan_id=plan_id, addon=product_name
                ).value
                if quali != None:
                    quantity = int(quantity) * int(
                        addons_plan_features.objects.get(
                            plan_id=plan_id, addon=product_name
                        ).value
                    )
                else:
                    quantity = 0
                if available_count:
                    total = quantity + available_count
                else:
                    total = None
                count_condition = update_addons(feature_id)
                if count_condition > 0:
                    available_count = client_features_balance.objects.get(
                        client_id=user_id, feature_id_id=count_condition
                    ).available_count
                    total = quantity + available_count
                    client_features_balance.objects.filter(
                        client_id=user_id, feature_id_id=count_condition
                    ).update(available_count=total)
                if feature_id == "56" or feature_id == 56:
                    buy_match = update_addons(feature_id)
                    ai_buy = client_features_balance.objects.get(
                        client_id_id=user_id, feature_id=buy_match
                    ).available_count
                    descriptive = len(
                        applicant_descriptive.objects.filter(user_id=user_id)
                    )
                    if ai_buy > 0 and descriptive > 0:
                        update_data = (
                            applicant_descriptive.objects.filter(user_id=user_id)
                            .order_by("id")
                            .values_list("id", flat=True)[:ai_buy]
                        )
                        for i in update_data:
                            applicant_descriptive.objects.filter(id=i).update(
                                is_active=False
                            )
                if feature_id == "59" or feature_id == 59:
                    import datetime

                    today_date = datetime.datetime.now()
                    today_date = today_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
                    group_members = UserHasComapny.objects.get(user_id=user_id).company
                    group_members = UserHasComapny.objects.filter(
                        company=group_members
                    ).values_list("user_id", flat=True)
                    group_members = (
                        attendees_role.objects.filter(user_id__in=group_members)
                        .values_list("interview_id", flat=True)
                        .distinct()
                    )

                    for i in group_members:
                        CalEvents.objects.filter(id=i).update(addon=True)
                client_addons_purchase_history.objects.create(
                    client_id=user_id,
                    feature_id_id=feature_id,
                    purchased_count=int(quantity),
                    plan_id = tmeta_plan.objects.get(plan_id= plan_id)
                )
                if feature_id == "52" or feature_id == 52:
                    ai_buy = client_features_balance.objects.get(
                        client_id_id=user_id, feature_id=27
                    ).available_count
                    descriptive = len(applicants_list.objects.filter(user_id=user_id))
                    if ai_buy > 0 and descriptive > 0:
                        update_data = (
                            applicants_list.objects.filter(user_id=user_id)
                            .order_by("id")
                            .values_list("id", flat=True)[:ai_buy]
                        )
                        for x in update_data:
                            applicants_list.objects.filter(id=x).update(is_active=False)
            domain = settings.CLIENT_URL
            response = subscriptions.objects.filter(client_id=user_id, is_active=True).values()
            result = response.annotate(
                plan_name=Subquery(tmeta_plan.objects.filter(plan_id=OuterRef("plan_id"))[:1].values("plan_name")),
                price=Subquery(tmeta_plan.objects.filter(plan_id=OuterRef("plan_id"))[:1].values("price")),
            )
            plandetails = result[0]
            result = addon_purchase(user_id, addon=product_name_total, quantity=quantity_total)
            coupon_claimed = Coupon_claimed(checkout)
            subject = "Unlock New Features with Your Zita Add-On"
            email_template_name = get_template(
                "email_templates/addon_purchase_confirmation.html"
            )
            c = {
                "user": user_id,
                "plandetails": plandetails,
                "domain": domain,
                "result": result,
            }
            try:
                email = email_template_name.render(c)
                msg = EmailMultiAlternatives(subject, email, settings.EMAIL_HOST_USER, [user_id.email])
                msg.attach_alternative(email, "text/html")
                msg.mixed_subtype = "related"
                image_data = [
                    "twitter.png",
                    "linkedin.png",
                    "youtube.png",
                    "new_zita_white.png",
                    "img_1.png",
                    "img_2.png",
                    "img_3.png",
                ]
                for i in image_data:
                    msg.attach(logo_data(i))
                msg.mixed_subtype = "related"
                msg.send()
            except Exception as e:
                pass
        return Response({"success": True})


from rest_framework.response import Response
from rest_framework import generics
from django.db.models.functions import Length
from django.db.models import (Case,F,Value,When,BooleanField,Subquery,OuterRef,IntegerField)


class website_details_api(generics.GenericAPIView):
    def get(self, request):
        yearly_plan = list(
            tmeta_plan.objects.filter(is_active=True)
            .annotate(subscription_days_length=Length("subscription_value_days"))
            .filter(subscription_days_length__exact=3)
            .values_list("plan_id", flat=True)
        )
        yearly_plan.extend([1, 13])
        yearly_plan = tmeta_plan.objects.filter(plan_id__in=yearly_plan).values()
        yearly_plan = yearly_plan.annotate(
            sub_heading=Subquery(
                subscription_content.objects.filter(plan_id=OuterRef("plan_id")).values(
                    "subscription_content"
                )[:1]
            ),
            data=Subquery(
                subscription_content.objects.filter(plan_id=OuterRef("plan_id")).values(
                    "rich_text_content"
                )[:1]
            ),
            days_length=Length(F("subscription_value_days")),
            is_month=Case(
                When(days_length__exact=2, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            jd_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=10
                ).values("feature_value")[:1]
            ),
            resume_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=27
                ).values("feature_value")[:1]
            ),
            ai_matched_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=6
                ).values("feature_value")[:1]
            ),
            user_price=Case(
                When(plan_id=1, then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            ),
            final_price=Case(
                When(price=0, then=Value("FREE")),
                default=F("price"),
                output_field=CharField(),
            ),
            days=Case(
                When(plan_id=1, then=Value("for 14 Days")),
                default=Value("Year"),
                output_field=CharField(),
            ),
        )
        monthly_plan = list(
            tmeta_plan.objects.filter(is_active=True)
            .exclude(plan_id=1)
            .annotate(subscription_days_length=Length("subscription_value_days"))
            .filter(subscription_days_length__exact=2)
            .values_list("plan_id", flat=True)
        )
        monthly_plan.extend([1, 9])
        monthly_plan = tmeta_plan.objects.filter(plan_id__in=monthly_plan).values()
        monthly_plan = monthly_plan.annotate(
            sub_heading=Subquery(
                subscription_content.objects.filter(plan_id=OuterRef("plan_id")).values(
                    "subscription_content"
                )[:1]
            ),
            data=Subquery(
                subscription_content.objects.filter(plan_id=OuterRef("plan_id")).values(
                    "rich_text_content"
                )[:1]
            ),
            days_length=Length(F("subscription_value_days")),
            is_month=Case(
                When(days_length__exact=2, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            jd_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=10
                ).values("feature_value")[:1]
            ),
            resume_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=27
                ).values("feature_value")[:1]
            ),
            ai_matched_count=Subquery(
                plan_features.objects.filter(
                    plan_id=OuterRef("plan_id"), feature_id=6
                ).values("feature_value")[:1]
            ),
            user_price=Case(
                When(plan_id=1, then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            ),
            days=Case(
                When(plan_id=1, then=Value("for 14 Days")),
                default=Value("Month"),
                output_field=CharField(),
            ),
            final_price=Case(
                When(price=0, then=Value("FREE")),
                default=F("price"),
                output_field=CharField(),
            ),
        )
        web_content_01 = website_details.objects.get(id=1).card_view
        web_content_02 = website_details.objects.get(id=2).card_view
        add_ons_01 = website_details.objects.get(id=3).addons
        add_ons_02 = website_details.objects.get(id=4).addons
        context = {
            "yearly_plan": yearly_plan,
            "monthly_plan": monthly_plan,
            "web_content_01": json.loads(web_content_01),
            "web_content_02": json.loads(web_content_02),
            "standard_plan": json.loads(add_ons_01),
            "premium_plan": json.loads(add_ons_02),
        }
        return Response(context)


class plan_change_api(generics.GenericAPIView):
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]
    def delete(self, request):
        request = self.request
        success = False
        users = request.GET.get("users", None)
        if users:
            users = json.loads(users)
            for i in users:
                if SubscriptionCustomer.objects.filter(user=i).exists():
                    SubscriptionCustomer.objects.filter(user=i).delete()
                    if subscriptions.objects.filter(
                        client_id=i, plan_id__gt=1
                    ).exists():
                        subscriptions.objects.filter(
                            client_id=i, plan_id__gt=1
                        ).delete()
                        client_features_balance.objects.filter(
                            client_id=i, feature_id__in=[6, 10, 27, 53]
                        ).update(available_count=0, plan_count=0)
                        client_features_balance.objects.filter(client_id=i).exclude(
                            feature_id__in=[6, 10, 27, 53]
                        ).delete()
                        success = True
        return Response({"success": success})


class auto_payment_stripe_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id, updated_by = admin_account(request)
        data = addon_purchase(user_id)
        return Response({"success": data})


class subscription_email_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        userid, updated_by = admin_account(request)
        request = self.request
        plan_id = request.POST.get("planID", None)
        addon_id = request.POST.get("addonID", None)
        addon_count = request.POST.get("count", None)
        if plan_id and addon_id and addon_count:
            domain = settings.CLIENT_URL
            if subscriptions.objects.filter(client_id=userid, is_active=True).exists():
                addon_id = json.loads(addon_id)
                addon_count = json.loads(addon_count)
                response = subscriptions.objects.filter(
                    client_id=userid, is_active=True
                ).values()
                response = response.annotate(
                    plan_name=Subquery(
                        tmeta_plan.objects.filter(plan_id=OuterRef("plan_id"))[
                            :1
                        ].values("plan_name")
                    ),
                    price=Subquery(
                        tmeta_plan.objects.filter(plan_id=OuterRef("plan_id"))[
                            :1
                        ].values("price")
                    ),
                )

                addon_value = addon_purchase(
                    userid, addon_id, addon_count, planname="addonwithplan"
                )
                final_value = 0
                for i in addon_value:
                    final_value += int(i["price"])
                plandetails = response[0]
                plandetails["1  "] = plandetails["price"] + final_value
                subject = "Welcome to Zita – Your Smart Hiring Starts Here"
                email_template_name = get_template(
                    "email_templates/subscription_template.html"
                )
                c = {
                    "user": userid,
                    "plandetails": plandetails,
                    "domain": domain,
                    "result": addon_value,
                }
                try:
                    email = email_template_name.render(c)
                    msg = EmailMultiAlternatives(
                        subject, email, settings.EMAIL_HOST_USER, [userid.email]
                    )
                    msg.attach_alternative(email, "text/html")
                    msg.mixed_subtype = "related"
                    image_data = [
                        "twitter.png",
                        "linkedin.png",
                        "youtube.png",
                        "new_zita_white.png",
                        "img_1.png",
                        "img_2.png",
                        "img_3.png",
                    ]
                    for i in image_data:
                        msg.attach(logo_data(i))
                    msg.mixed_subtype = "related"
                    msg.send()
                except Exception as e:
                    pass
            return Response({"success": True})

        return Response({"success": False})


''' Here its Coupon Code Send api With Templates'''
class coupon_code_api(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        userid, updated_by = admin_account(request)
        request = self.request
        receiver = request.GET.get("user_id", None)
        coupon = request.GET.get("coupon", None)
        try:
            if receiver and coupon:
                receiver = json.loads(receiver)
                if not discounts.objects.filter(discount_name = coupon).exists():
                    if not discounts_addon.objects.filter(discount_name = coupon).exists():
                        return Response({"success": False,'error':"Coupon Code not in Database"})

                for ids,i in enumerate(receiver):
                    if company_details.objects.filter(recruiter_id=i).exists() and User.objects.filter(id = i).exists():
                        userobj = User.objects.get(id=i)
                        coupon_type = False
                        if discounts.objects.filter(discount_name = coupon).exists():
                            coupon_type = True
                            coupon_obj = discounts.objects.get(discount_name = coupon)
                        elif discounts_addon.objects.filter(discount_name = coupon).exists():
                            coupon_obj = discounts_addon.objects.get(discount_name = coupon)
                        print("coupon_obj@@",coupon_obj,coupon_type)
                        days = coupon_obj.days
                        dt_start = datetime.now()
                        dt_end = dt_start + timedelta(days=days)
                        expired_date = None
                        if coupon_type:
                            if not discount_user.objects.filter(client_id = userobj,discount_id = coupon_obj).exists():
                                discount_user.objects.create(client_id = userobj,discount_id = coupon_obj,discount_start_date = dt_start,discount_end_date = dt_end)
                        if coupon_type == False:
                            if not discount_user.objects.filter(client_id = userobj,discount_addon = coupon_obj).exists():
                                discount_user.objects.create(client_id = userobj,discount_addon = coupon_obj,discount_start_date = dt_start,discount_end_date = dt_end)

                        print("COupon_type",coupon_type,coupon_obj)
                        if coupon_type:
                            if discount_user.objects.filter(client_id = userobj,discount_id = coupon_obj).exists():
                                expired_date = discount_user.objects.get(client_id = userobj,discount_id = coupon_obj).discount_end_date
                        if coupon_type == False:
                            if discount_user.objects.filter(client_id = userobj,discount_addon = coupon_obj).exists():
                                expired_date = discount_user.objects.get(client_id = userobj,discount_addon = coupon_obj).discount_end_date
                        senduser_couponcode(userobj,coupon_obj,expired_date=expired_date,type_coupon = coupon_type)
                return Response({"success": True,"message": "Email Send SuccessFully"})
            else:
                return Response({"success": False,'error':"user_id and coupon key is missing"})
        except Exception as e:
            print("Coupon Code Exception",str(e))
            return Response({"success": False,'error':str(e)})

    def post(self, request):
        userid, updated_by = admin_account(request)
        request = self.request
        method = request.POST.get("coupon_method", None)
        coupon_code = request.POST.get("coupon_code", None)
        coupon_name = request.POST.get("coupon_name", None)
        discount_type = request.POST.get("type", None)
        discount_value = request.POST.get("discount_value", None)
        currency = request.POST.get("currency", None)
        usgae = request.POST.get("usage", None)
        plan_id = request.POST.get("plan_id", None)
        addon_id = request.POST.get("addon_id", None)

        if  method == "addon":
            if not discounts_addon.objects.filter(discount_name=coupon_name,discount_code=coupon_code).exists():
                if plan_id:
                    plan_id = tmeta_plan.objects.get(plan_id = plan_id)
                discounts_addon.objects.create(discount_name=coupon_name,discount_code=coupon_code,
                    discount_type=discount_type,discount_value=discount_value,discount_currency = currency,usage_per_client = usgae,plan_id = plan_id,addon_id= addon_id)
                return Response({"success": True,'messae':'Addon Coupon code created successfully'})
            else:
                return Response({"success": False,'messae':'Addon Coupon code is Already Exists'})

        if  method == "subscription":
            if not discounts.objects.filter(discount_name=coupon_name,discount_code=coupon_code).exists():
                if plan_id:
                    plan_id = tmeta_plan.objects.get(plan_id = plan_id)
                discounts.objects.create(discount_name=coupon_name,discount_code=coupon_code,
                    discount_type=discount_type,discount_value=discount_value,discount_currency = currency,usage_per_client = usgae,plan_id = plan_id)
                return Response({"success": True,'messae':'Plan Coupon code created successfully'})
            else:
                return Response({"success": False,'messae':'Plan Coupon code is Already Exists'})
        return Response({"success": False})

