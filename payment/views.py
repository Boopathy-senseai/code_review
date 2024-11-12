import stripe
from jobs.utils import add_ons, date_exceed_checking
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
from jobs.views import admin_account, update_addons, user_permission
from django.urls import reverse
from .models import *
from login.decorators import *
from django.contrib.auth.decorators import login_required
import datetime
from django.views.decorators.cache import never_cache
from django.contrib.sites.shortcuts import get_current_site
import time
import pytz
from rest_framework.decorators import api_view
from django.contrib import messages

Host_mail = settings.EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.shortcuts import render
from django.contrib.auth.models import Permission

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
from collections import defaultdict
from users.models import UserHasComapny, CompanyHasInvite
import ast
import json

stripe.api_key = settings.STRIPE_SECRET_KEY
contact_credit = settings.contact_credit
from django.db.models import Case, When, Value, CharField, F, Q, Exists
from django.contrib.staticfiles import finders
from email.mime.image import MIMEImage
from copy import deepcopy
from .stripe_service import *
from jobs.models import *
email_main = settings.EMAIL_HOST_USER
EMAIL_TO = settings.EMAIL_TO


def credits_purchase(request):
    user_id, updated_by = admin_account(request)
    if "session_id" in request.GET:
        session_id = request.GET["session_id"]
        checkout = stripe.checkout.Session.retrieve(
            session_id,
        )
        metadata = checkout.get("metadata")
        product_name = metadata["product_name"]
        quantity = metadata["quantity"]
        if product_name == "Source_Credit":
            try:
                available_count = client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=11
                ).available_count
            except client_features_balance.DoesNotExist:
                client_features_balance.objects.create(
                    client_id=user_id, feature_id_id=11, available_count=0
                )
                available_count = client_features_balance.objects.get(
                    client_id=user_id, feature_id_id=11
                ).available_count
            total = int(quantity) + available_count
            client_features_balance.objects.filter(
                client_id=user_id, feature_id_id=11
            ).update(available_count=total)
            client_addons_purchase_history.objects.create(
                client_id=user_id,
                feature_id_id=11,
                purchased_count=int(quantity),
            )
    return HttpResponseRedirect(
        reverse("payment:manage_subscription") + "#%s" % "credits"
    )


@never_cache
@login_required
@recruiter_required
def order_summary(request):
    # try:
    user, updated_by = admin_account(request)
    has_permission = user_permission(request, "manage_account_settings")
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )
    if not has_permission == True:
        return render(request, "jobs/no_permission.html", {"permission": permission})
    subscription_cus = SubscriptionCustomer.objects.get(user=user)
    plan = tmeta_plan.objects.get(plan_id=int(request.GET["key"]))
    proration_date = int(time.time())
    local_sub = subscriptions.objects.filter(client_id=user).last()
    update_user = 0
    if local_sub.plan_id.pk == plan.pk:
        update_user = 1
    if "discounts" in request.GET:
        del request.session["discounts"]
        request.session.modified = True
        domain_url = request.build_absolute_uri("/")
        return redirect(
            domain_url + "summary/?key=" + request.GET["key"] + "&c=" + request.GET["c"]
        )
    if request.method == "POST":

        if "update" in request.POST:
            try:
                if update_user == 0:
                    stripe.Subscription.modify(
                        request.session["subscription"],
                        cancel_at_period_end=False,
                        proration_behavior="always_invoice",
                        proration_date=request.session["proration_date"],
                        items=request.session["items"],
                        billing_cycle_anchor="now",
                        coupon=request.session["discounts"],
                        metadata={
                            "subscription_name": request.GET["key"],
                            "quantity": request.GET["c"],
                        },
                    )
                else:
                    stripe.Subscription.modify(
                        request.session["subscription"],
                        cancel_at_period_end=False,
                        proration_behavior="always_invoice",
                        proration_date=request.session["proration_date"],
                        items=request.session["items"],
                        coupon=request.session["discounts"],
                        metadata={
                            "subscription_name": request.GET["key"],
                            "quantity": request.GET["c"],
                        },
                    )
                discount_codes_claimed.objects.get_or_create(
                    client_id=user,
                    discount_id=discounts.objects.get(
                        discount_code=request.session["discounts"]
                    ),
                    subscription_id=local_sub,
                )
            except:
                if update_user == 0:
                    stripe.Subscription.modify(
                        request.session["subscription"],
                        cancel_at_period_end=False,
                        proration_behavior="always_invoice",
                        proration_date=request.session["proration_date"],
                        items=request.session["items"],
                        billing_cycle_anchor="now",
                        metadata={
                            "subscription_name": request.GET["key"],
                            "quantity": request.GET["c"],
                        },
                    )
                else:
                    stripe.Subscription.modify(
                        request.session["subscription"],
                        cancel_at_period_end=False,
                        proration_behavior="always_invoice",
                        proration_date=request.session["proration_date"],
                        items=request.session["items"],
                        metadata={
                            "subscription_name": request.GET["key"],
                            "quantity": request.GET["c"],
                        },
                    )
            return redirect("payment:home")
        elif "discounts" in request.POST:
            domain_url = request.build_absolute_uri()
            try:
                discount = discounts.objects.get(
                    discount_name=request.POST["discounts"]
                )
                if not discount.discount_end_date == None:
                    if discount.discount_end_date < timezone.now():
                        messages.success(request, "Promo code invalid")
                        return redirect(domain_url)

                if discount_codes_claimed.objects.filter(
                    subscription_id=local_sub, discount_id=discount
                ).exists():
                    try:
                        del request.session["discounts"]
                        request.session.modified = True
                    except:
                        pass
                    discount_added = False
                else:
                    if local_sub.plan_id.pk in [2, 4] and plan.pk in [3, 5]:
                        request.session["discounts"] = discount.discount_code
                        discount_added = True
                    else:
                        messages.success(request, "Promo code invalid")
                        return redirect(domain_url)
            except:
                discount_added = 2
            if discount_added == False:
                messages.success(request, "Promo code invalid")
                return redirect(domain_url)
            elif discount_added == 2:
                messages.success(request, "Promo code invalid")
                return redirect(domain_url)
            else:
                return redirect(domain_url)
        else:
            domain_url = request.build_absolute_uri()
            billing_portal = stripe.billing_portal.Session.create(
                customer=subscription_cus.stripeCustomerId,
                return_url=domain_url,
            )
            return redirect(billing_portal["url"])

    if "key" in request.GET and request.method == "GET":
        plan = tmeta_plan.objects.get(plan_id=int(request.GET["key"]))
        subscription = stripe.Subscription.retrieve(
            subscription_cus.stripeSubscriptionId
        )
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
        try:
            if discount_codes_claimed.objects.filter(
                subscription_id=local_sub,
                discount_id=discounts.objects.get(
                    discount_code=request.session["discounts"]
                ),
            ).exists():
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
        except:
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
        un_used = invoice["lines"]["data"][0].amount / 100
        request.session["proration_date"] = proration_date

        new_price = invoice["lines"]["data"][-1].amount / 100
        final = invoice["total"] / 100
        subtotal = invoice["subtotal"] / 100
        # tax=invoice['tax']/100
        # tax_rate=invoice['total_tax_amounts']
        tax_list = []

        # for i in tax_rate:
        #     tax_data=stripe.TaxRate.retrieve(
        #       i.tax_rate,
        #     )
        #     tax_data['amount'] = i.amount/100
        #     tax_list.append(tax_data)
        if final < 0:
            available_balance = final
        else:
            available_balance = 0
        try:

            stripe_balance = stripe.Customer.list_balance_transactions(
                subscription_cus.stripeCustomerId
            )
            try:
                stripe_balance = stripe_balance["data"][0]["ending_balance"] / 100
            except:
                stripe_balance = 0

        except:

            stripe_balance = 0
        try:
            total_discount_amounts = (
                invoice["total_discount_amounts"][0]["amount"] / 100
            )
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
            discount_added = discounts.objects.get(
                discount_code=request.session["discounts"]
            )
        except:
            discount_added = False

        date = local_sub.subscription_start_ts + timezone.timedelta(
            days=plan.subscription_value_days
        )
        context = {
            "plan": plan,
            "un_used": un_used,
            "count": count,
            "final": final,
            "available_balance": available_balance,
            "total_discount_amounts": total_discount_amounts,
            "local_sub": local_sub,
            "date": date,
            # 'tax':tax,
            "tax_list": tax_list,
            "stripe_balance": stripe_balance,
            "permission": permission,
            "discount_added": discount_added,
            "update_user": update_user,
            "subtotal": subtotal,
            "subscription_cus": subscription_cus,
            "new_price": new_price,
        }
        return render(request, "payment/order_summary.html", context)
    # except:

    #     return redirect('jobs:manage_subscription')


@never_cache
@login_required
@recruiter_required
def manage_subscription(request):
    basic_month = settings.basic_month
    basic_year = settings.basic_year
    pro_year = settings.pro_year
    pro_month = settings.pro_month
    user_id, updated_by = admin_account(request)
    has_permission = user_permission(request, "manage_account_settings")
    if not has_permission == True:
        permission = Permission.objects.filter(user=request.user).values_list(
            "codename", flat=True
        )
        return render(request, "jobs/no_permission.html", {"permission": permission})
    permission = Permission.objects.filter(user=request.user).values_list(
        "codename", flat=True
    )

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
            if int(subscription.subscription_remains_days) == 0:
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
        price = subscription.plan_id.price * subscription.no_of_users

    except:
        sub_id = 0
        user_count = 1
        subscription = None
        free_expired = None
        expire_in = None
        price = 0
    downgrade = 0
    try:
        cur_active_job = JD_form.objects.filter(user_id=user_id, jd_status_id=1).count()
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
        setting = career_page_setting.objects.get(recruiter_id=user_id)
    except:
        setting = None
    try:
        setting1 = company_details.objects.get(recruiter_id=user_id)
        invites = CompanyHasInvite.objects.get(company_id=setting1).invites
        total_user = UserHasComapny.objects.filter(company_id=setting1).count()
        balance = subscription.no_of_users - total_user
        CompanyHasInvite.objects.filter(company_id=setting1).update(invites=balance)
    except:
        # setting=None
        invites = 0
        total_user = 0
    try:
        available = client_features_balance.objects.get(
            client_id=user_id, feature_id_id=11
        ).available_count
    except:
        available = 0
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
        "user_count": user_count,
        "setting": setting,
        "pro_year": pro_year,
        "pro_month": pro_month,
        "price": price,
        "CustomerId": CustomerId,
        "available": available,
    }
    return render(request, "jobs/manage_subscription.html", context)


def logo_data(img):
    # image_data =['facebook.png','twitter.png','linkedin.png','youtube.png','new_zita.png']
    with open(finders.find("images/" + img), "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", img)
    return logo


def cancel_subscription(request):
    if request.method == "POST":
        user, updated_by = admin_account(request)
        subscription_cus = SubscriptionCustomer.objects.get(user=user)
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
    try:
        domain = get_current_site(request)
        htmly = get_template("email_templates/subscription_cancelled.html")
        subject, from_email, to = (
            "Subscription cancelled successfully",
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
        msg.send()
    except Exception as e:
        pass
    return HttpResponseRedirect(
        reverse("payment:manage_subscription") + "#%s" % "cancelled"
    )


def renew_subscription(request):
    user, updated_by = admin_account(request)
    subscription_cus = SubscriptionCustomer.objects.get(user=user)
    plan = tmeta_plan.objects.get(plan_id=int(request.GET["key"]))
    subscription = stripe.Subscription.retrieve(subscription_cus.stripeSubscriptionId)
    stripe.Subscription.modify(
        subscription.id,
        cancel_at_period_end=False,
        proration_behavior="create_prorations",
        items=[
            {
                "id": subscription["items"]["data"][0].id,
                "price": plan.stripe_id,
            }
        ],
    )
    subscriptions.objects.filter(client_id=user, is_active=True).update(
        has_client_changed_subscription=False,
        subscription_changed_date=None,
        subscription_changed_to=None,
    )

    return HttpResponseRedirect(
        reverse("payment:manage_subscription") + "#%s" % "renew"
    )


@csrf_exempt
def stripe_config(request):
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_subscription_session(request):
    if request.method == "GET":
        domain_url = request.build_absolute_uri("/")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user_id, updated_by = admin_account(request)
        try:
            if SubscriptionCustomer.objects.filter(user=user_id).exists():
                CustomerId = SubscriptionCustomer.objects.get(
                    user=user_id
                ).stripeCustomerId
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=user_id.id,
                    success_url=domain_url
                    + "payment/?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=domain_url + "account/subscription/",
                    payment_method_types=["card"],
                    customer=CustomerId,
                    billing_address_collection="required",
                    mode="subscription",
                    allow_promotion_codes=True,
                    line_items=[
                        {
                            "price": request.GET["plan"],
                            "quantity": request.GET["count"],
                        }
                    ],
                    metadata={
                        "subscription_name": request.GET["plan_name"],
                        "quantity": request.GET["count"],
                    },
                )
            else:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=user_id.id,
                    success_url=domain_url
                    + "payment/?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=domain_url + "account/subscription/",
                    payment_method_types=["card"],
                    customer_email=request.user.email,
                    billing_address_collection="required",
                    mode="subscription",
                    allow_promotion_codes=True,
                    line_items=[
                        {
                            "price": request.GET["plan"],
                            "quantity": request.GET["count"],
                        }
                    ],
                    metadata={
                        "subscription_name": request.GET["plan_name"],
                        "quantity": request.GET["count"],
                    },
                )
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


def billing_portal(request, pk=None):
    domain_url = request.build_absolute_uri("/")
    user_id, updated_by = admin_account(request)
    CustomerId = SubscriptionCustomer.objects.get(user=user_id).stripeCustomerId
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if "downgrade" in request.GET:
        billing_portal = stripe.billing_portal.Session.create(
            customer=CustomerId,
            return_url=domain_url + "account/subscription/",
        )
    else:
        billing_portal = stripe.billing_portal.Session.create(
            customer=CustomerId,
            return_url=domain_url + "account/subscription/",
        )
    return redirect(billing_portal["url"])


def create_checkout_session(request):
    user_id, updated_by = admin_account(request)
    if request.method == "GET":
        domain_url = settings.CLIENT_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            if "candicates" in request.GET:
                if "manage_sub" in request.GET:
                    url = domain_url + "/credits_purchase/"
                else:
                    url = domain_url + "/talent_sourcing/"

                request.session["source_candi"] = request.GET["candicates"]
                if SubscriptionCustomer.objects.filter(user=user_id).exists():
                    CustomerId = SubscriptionCustomer.objects.get(
                        user=user_id
                    ).stripeCustomerId
                    checkout_session = stripe.checkout.Session.create(
                        client_reference_id=user_id.id,
                        success_url=url + "?session_id={CHECKOUT_SESSION_ID}",
                        cancel_url=url + "?cancelled=source_credit",
                        payment_method_types=["card"],
                        payment_intent_data={"setup_future_usage": "off_session"},
                        customer=CustomerId,
                        billing_address_collection="required",
                        mode="payment",
                        line_items=[
                            {
                                "price": contact_credit,
                                "quantity": request.GET["candicates"],
                            }
                        ],
                        metadata={
                            "product_name": "Source_Credit",
                            "quantity": request.GET["candicates"],
                        },
                    )
                else:
                    checkout_session = stripe.checkout.Session.create(
                        client_reference_id=user_id.id,
                        success_url=url + "?session_id={CHECKOUT_SESSION_ID}",
                        cancel_url=url + "?cancelled=source_credit",
                        payment_method_types=["card"],
                        payment_intent_data={"setup_future_usage": "off_session"},
                        customer_email=request.user.email,
                        billing_address_collection="required",
                        mode="payment",
                        line_items=[
                            {
                                "price": contact_credit,
                                "quantity": request.GET["candicates"],
                            }
                        ],
                        metadata={
                            "product_name": "Source_Credit",
                            "quantity": request.GET["candicates"],
                        },
                    )

                return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    if event["type"] == "charge.succeeded":
        session = event["data"]["object"]
    if event["type"] == "customer.subscription.deleted":
        session = event["data"]["object"]
        metadata = session["plan"]["metadata"]
        stripe_customer_id = session.get("customer")
        user = SubscriptionCustomer.objects.get(
            stripeCustomerId=stripe_customer_id
        ).user
        subscription_name = metadata["subscription_plan"]
        plan = tmeta_plan.objects.get(plan_id=int(subscription_name))
        if subscriptions.objects.filter(
            client_id=user, is_active=True, plan_id=plan
        ).exists():
            subscriptions.objects.filter(
                client_id=user, is_active=True, plan_id=plan
            ).update(
                has_client_changed_subscription=True,
                subscription_changed_to=-2,
                subscription_changed_date=None,
                is_active=False,
            )
    if event["type"] == "customer.subscription.updated":
        session = event["data"]["object"]
        metadata = session["plan"]["metadata"]
        quantity = session["quantity"]
        current_period_end = session["current_period_end"]
        current_period_start = session["current_period_start"]

        start_date = datetime.datetime.fromtimestamp(
            int(current_period_start)
        ).strftime("%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime.fromtimestamp(int(current_period_end)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        stripe_customer_id = session.get("customer")
        user = SubscriptionCustomer.objects.get(
            stripeCustomerId=stripe_customer_id
        ).user
        if session["cancel_at"] == None:
            # try:
            subscription_name = metadata["subscription_plan"]
            plan = tmeta_plan.objects.get(plan_id=int(subscription_name))
            if subscriptions.objects.filter(
                client_id=user, is_active=True, plan_id=plan, subscription_changed_to=-1
            ).exists():
                subscriptions.objects.filter(
                    client_id=user, is_active=True, plan_id=plan
                ).update(
                    has_client_changed_subscription=False,
                    subscription_start_ts=start_date,
                    subscription_valid_till=end_date,
                    subscription_changed_to=None,
                    subscription_changed_date=None,
                )
            else:
                if subscriptions.objects.filter(
                    client_id=user, is_active=True
                ).exists():
                    subscriptions.objects.filter(client_id=user, is_active=True).update(
                        has_client_changed_subscription=True,
                        is_active=False,
                        subscription_changed_date=timezone.now(),
                    )
                features_balance = plan_features.objects.filter(
                    plan_id=plan, feature_id_id__in=[10, 12]
                )
                subscriptions.objects.get_or_create(
                    client_id=user,
                    plan_id=plan,
                    no_of_users=int(quantity),
                    subscription_valid_till=timezone.now()
                    + timezone.timedelta(days=plan.subscription_value_days),
                    updated_by=user.username,
                    subscription_remains_days=plan.subscription_value_days,
                )
                for i in features_balance:
                    if client_features_balance.objects.filter(
                        client_id=user, feature_id=i.feature_id
                    ).exists():
                        last_plan = subscriptions.objects.filter(
                            client_id=user, is_active=False
                        ).last()
                        if i.feature_id.pk == 10:
                            available_count = client_features_balance.objects.get(
                                client_id=user, feature_id=i.feature_id
                            ).available_count
                            if i.feature_value == None:
                                total = i.feature_value
                            else:
                                if available_count == None:
                                    balance = JD_form.objects.filter(
                                        user_id=user, jd_status_id=1
                                    ).count()
                                    total = i.feature_value - balance
                                    if total <= 0:
                                        total = 0
                                else:
                                    total = available_count
                            client_features_balance.objects.filter(
                                client_id=user,
                                feature_id=i.feature_id,
                            ).update(
                                available_count=total,
                            )
                        if i.feature_id.pk == 12:
                            available_count = client_features_balance.objects.get(
                                client_id=user, feature_id=i.feature_id
                            ).available_count
                            if i.feature_value == None:
                                total = i.feature_value
                            else:
                                if available_count == None:
                                    balance = employer_pool.objects.filter(
                                        client_id=user,
                                    ).count()
                                    total = i.feature_value - balance
                                    if total <= 0:
                                        total = 0
                                else:
                                    total = available_count
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
            # except:
            #     pass
        else:
            subscriptions.objects.filter(client_id=user, is_active=True).update(
                has_client_changed_subscription=True,
                subscription_changed_date=timezone.now(),
                subscription_changed_to=-1,
            )
    elif event["type"] == "customer.subscription.created":
        session = event["data"]["object"]
        metadata = session["plan"]["metadata"]
        quantity = session["quantity"]
        current_period_end = session["current_period_end"]
        current_period_start = session["current_period_start"]
        start_date = datetime.datetime.fromtimestamp(
            int(current_period_start)
        ).strftime("%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime.fromtimestamp(int(current_period_end)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        stripe_customer_id = session.get("customer")
        user = SubscriptionCustomer.objects.get(
            stripeCustomerId=stripe_customer_id
        ).user
        if session["cancel_at"] == None:
            # try:
            subscription_name = metadata["subscription_plan"]
            plan = tmeta_plan.objects.get(plan_id=int(subscription_name))
            if subscriptions.objects.filter(
                client_id=user, is_active=True, plan_id=plan, subscription_changed_to=-1
            ).exists():
                subscriptions.objects.filter(
                    client_id=user, is_active=True, plan_id=plan
                ).update(
                    has_client_changed_subscription=False,
                    subscription_start_ts=start_date,
                    subscription_valid_till=end_date,
                    subscription_changed_to=None,
                    subscription_changed_date=None,
                )
            else:
                if subscriptions.objects.filter(
                    client_id=user, is_active=True
                ).exists():
                    subscriptions.objects.filter(client_id=user, is_active=True).update(
                        has_client_changed_subscription=True,
                        is_active=False,
                        subscription_changed_date=timezone.now(),
                    )
                features_balance = plan_features.objects.filter(
                    plan_id=plan, feature_id_id__in=[10, 12]
                )
                subscriptions.objects.get_or_create(
                    client_id=user,
                    plan_id=plan,
                    no_of_users=int(quantity),
                    subscription_valid_till=timezone.now()
                    + timezone.timedelta(days=plan.subscription_value_days),
                    updated_by=user.username,
                    subscription_remains_days=plan.subscription_value_days,
                )
                for i in features_balance:
                    if client_features_balance.objects.filter(
                        client_id=user, feature_id=i.feature_id
                    ).exists():
                        last_plan = subscriptions.objects.filter(
                            client_id=user, is_active=False
                        ).last()

                        # this is for contact credits
                        # if i.feature_id.pk == 11:
                        #     features_balance = plan_features.objects.get(plan_id=last_plan.plan_id,feature_id_id=11).feature_value
                        #     available_count=client_features_balance.objects.get( client_id=user,feature_id=i.feature_id).available_count
                        #     if available_count == None or i.feature_value ==None :
                        #         total =i.feature_value
                        #     else:
                        #         total =i.feature_value +available_count
                        #         total = total-features_balance
                        #     client_features_balance.objects.filter(
                        #         client_id=user,
                        #         feature_id=i.feature_id,).update(
                        #             available_count=total,
                        #         )
                        # else:
                        if i.feature_id.pk == 10:
                            available_count = client_features_balance.objects.get(
                                client_id=user, feature_id=i.feature_id
                            ).available_count
                            if i.feature_value == None:
                                total = i.feature_value
                            else:
                                if available_count == None:
                                    balance = JD_form.objects.filter(
                                        user_id=user, jd_status_id=1
                                    ).count()
                                    total = i.feature_value - balance
                                    if total <= 0:
                                        total = 0
                                else:
                                    total = available_count
                            client_features_balance.objects.filter(
                                client_id=user,
                                feature_id=i.feature_id,
                            ).update(
                                available_count=total,
                            )
                        if i.feature_id.pk == 12:
                            available_count = client_features_balance.objects.get(
                                client_id=user, feature_id=i.feature_id
                            ).available_count
                            if i.feature_value == None:
                                total = i.feature_value
                            else:
                                if available_count == None:
                                    balance = employer_pool.objects.filter(
                                        client_id=user,
                                    ).count()
                                    total = i.feature_value - balance
                                    if total <= 0:
                                        total = 0
                                else:
                                    total = available_count
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
            # except:
            #     pass
        else:
            subscriptions.objects.filter(client_id=user, is_active=True).update(
                has_client_changed_subscription=True,
                subscription_changed_date=timezone.now(),
                subscription_changed_to=-1,
            )

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata")
        product_name = metadata["product_name"]
        quantity = metadata["quantity"]
        if product_name == "Source_Credit":
            try:
                available_count = client_features_balance.objects.get(
                    client_id=user, feature_id_id=11
                ).available_count
            except client_features_balance.DoesNotExist:
                client_features_balance.objects.create(
                    client_id=user, feature_id_id=11, available_count=0
                )
                available_count = client_features_balance.objects.get(
                    client_id=user, feature_id_id=11
                ).available_count
            total = int(quantity) + available_count
            client_features_balance.objects.filter(
                client_id=user, feature_id_id=11
            ).update(available_count=total)
            client_addons_purchase_history.objects.create(
                client_id=user,
                feature_id_id=11,
                purchased_count=int(quantity),
            )

    return HttpResponse(status=200)


# def handle_checkout_session(session):
#     # client_reference_id = user's id
#     client_reference_id = session.get("client_reference_id")
#     payment_intent = session.get("payment_intent")

#     if client_reference_id is None:
#         # Customer wasn't logged in when purchasing
#         return

#     # Customer was logged in we can now fetch the Django user and make changes to our models
#     try:
#         user = User.objects.get(id=client_reference_id)

#         # TODO: make changes to our models.

#     except User.DoesNotExist:
#         pass


def SuccessView(request):
    if "update" in request.GET:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve("sub_JeRca9G56QIn9m")

        stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=True,
            proration_behavior="create_prorations",
            items=[
                {
                    "id": subscription["items"]["data"][0].id,
                    "price": "price_1IxRHFSFU1EGDQUIdLxmpk9y",
                }
            ],
        )
    return render(request, "payment/success.html")


def expire_addons(num):
    if num == "10" or num == 10:
        return 51
    elif num == "27" or num == 27:
        return 52
    elif num == "53" or num == 53:
        return 58
    elif num == "6" or num == 6:
        return 56
    else:
        return 0


def subs_add_on_creation(user_id, quantity, feature_id, addon_id):
    # try:
    available_count = client_features_balance.objects.get(
        client_id=user_id, feature_id_id=feature_id
    ).available_count
    # except client_features_balance.DoesNotExist:
    #     client_features_balance.objects.create(client_id=user_id,feature_id_id=feature_id,available_count=0)
    #     available_count=client_features_balance.objects.get(client_id=user_id,feature_id_id=feature_id,).available_count
    total = int(quantity) + available_count
    client_features_balance.objects.filter(
        client_id=user_id, feature_id_id=feature_id
    ).update(available_count=total)
    client_addons_purchase_history.objects.create(
        client_id=user_id,
        feature_id_id=feature_id,
        purchased_count=int(quantity),
    )
    return True


class CancelledView(TemplateView):
    template_name = "payment/cancelled.html"


# stripe.checkout.Session.retrieve(
#   "cs_test_a1EUkR5OteiiGGgavkwNzjhCe5VgtGVNaFbvwdhaFt38ullPaLrUUIgR7o",
# )
def remove_headings(data):
    new_data = []
    for plan_type, plan_data in data.items():
        plan_entry = {
            "name": plan_type,
            "id": plan_data["id"],
            "content": plan_data["content"],
        }
        new_data.append(plan_entry)
    return new_data


def transform_data(data):
    new_data = []
    for plan_type, addons in data.items():
        plan_entry = {
            "name": plan_type,
            "id": addons[0]["plan_id_id"],
            "content": addons,
        }
        new_data.append(plan_entry)
    return new_data


def addon_format_changes(available_addons, total_plan_name):
    organized_data = defaultdict(list)
    for item in available_addons:
        plan_id = item.get("plan_id_id")
        organized_data[plan_id].append(item)
    output_format = [
        {
            "name": total_plan_name[index],
            "id": int(plan_id),
            "content": [
                addon
                for addon in organized_data[plan_id]
                if addon["plan_id_id"] == int(plan_id)
            ],
        }
        for index, plan_id in enumerate(organized_data.keys())
    ]
    addon_id_order = json.loads(
        addons_plan_features.objects.get(plan_id=1, addon=4).content
    )
    result = {}
    print("output_format@@@@",output_format)
    for plan_data in output_format:
        plan_name = plan_data["name"]
        addon_order = addon_id_order.get(plan_name)
        if addon_order:
            print("addon_order@@@@",addon_order)
            try:
                ordered_addons = sorted(
                    plan_data["content"], key=lambda x: addon_order.index(x["addon_id"]))
                result[plan_name] = ordered_addons
            except Exception as e:
                print("Manage Subscription Error",str(e))
                pass
    result = transform_data(result)
    return result


from calendarapp.models import *


def addon_creation(user, subscription_name, quantity):
    user_id = user
    qual = quantity
    sub_name = subscription_name
    quantity = int((ast.literal_eval(quantity))[0])
    subscription_name = int((ast.literal_eval(subscription_name))[0])
    quantity_total = (ast.literal_eval(qual))[1:]

    product_name_total = (ast.literal_eval(sub_name))[1:]

    for quantity, product_name in zip(quantity_total, product_name_total):
        feature_id = add_ons(user, product_name, quantity)

        addons_qual = quantity
        plan_id = subscriptions.objects.filter(client_id=user_id).last().plan_id.pk
        try:
            available_count = client_features_balance.objects.get(
                client_id=user, feature_id_id=feature_id
            ).available_count
            if client_features_balance.objects.filter(
                client_id=user_id, feature_id_id=feature_id
            ).exists():
                if addons_plan_features.objects.get(
                    plan_id=plan_id, addon_id=product_name
                ).value:
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
                from django.db.models import F, Func

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
        if available_count != None:
            total = quantity + available_count
            addons_count = client_features_balance.objects.get(
                client_id=user, feature_id_id=feature_id
            ).addons_count
            addons_count = addons_count if addons_count else 0
            # client_features_balance.objects.filter(client_id=user,feature_id_id=feature_id).update(available_count=total,addons_count=addons_count+addons_qual)
            count_condition = update_addons(feature_id)
            if count_condition > 0:
                available_count = client_features_balance.objects.get(
                    client_id=user, feature_id_id=count_condition
                ).available_count
                total = quantity + available_count
                client_features_balance.objects.filter(
                    client_id=user, feature_id_id=count_condition
                ).update(available_count=total)
            if feature_id == "56" or feature_id == 56:
                buy_match = update_addons(feature_id)
                ai_buy = client_features_balance.objects.get(
                    client_id_id=user_id, feature_id=buy_match
                ).available_count
                descriptive = len(applicant_descriptive.objects.filter(user_id=user_id))
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
            client_id=user,
            feature_id_id=feature_id,
            purchased_count=int(quantity),
        )

        # ------------- Payment Rework ------------------#


def Plan_upgrade(user, i):
    success = True
    if client_features_balance.objects.filter(
        client_id=user, feature_id=i.feature_id
    ).exists():
        available_count = client_features_balance.objects.get(
            client_id=user, feature_id=i.feature_id
        ).available_count
        balance_job = JD_form.objects.filter(user_id=user, jd_status_id=1).count()
        total = i.feature_value
        client_features_balance.objects.filter(
            client_id=user,
            feature_id=i.feature_id,
        ).update(available_count=total, plan_count=total)
    elif not client_features_balance.objects.filter(
        client_id=user, feature_id=i.feature_id
    ).exists():
        client_features_balance.objects.create(
            client_id=user, feature_id=i.feature_id, available_count=i.feature_value
        )
    # delete_values = delete_addon(user)
    add_value = Plan_addon_upgrade(user, i)
    return success


def Plan_addon_upgrade(user, i):  # -----> Need to work for Resume Parsing
    if (
        client_features_balance.objects.filter(client_id_id=user, feature_id=6).exists()
        and i.feature_id.feature_id == 6
    ):
        ai_buy = client_features_balance.objects.get(
            client_id_id=user, feature_id=6
        ).available_count
        descriptive = len(applicant_descriptive.objects.filter(user_id=user))
        if ai_buy > 0 and descriptive > 0:
            update_data = (applicant_descriptive.objects.filter(user_id=user).order_by("id").values_list("id", flat=True)[:ai_buy])
            decrease_ai_count = ai_buy - descriptive
            client_features_balance.objects.filter(client_id_id=user, feature_id=6).update(available_count = decrease_ai_count )
            for x in update_data:
                applicant_descriptive.objects.filter(id=x).update(is_active=False)
    if (
        client_features_balance.objects.filter(
            client_id_id=user, feature_id=27
        ).exists()
        and i.feature_id.feature_id == 27
    ):
        ai_buy = client_features_balance.objects.get(
            client_id_id=user, feature_id=27
        ).available_count
        descriptive = len(applicants_list.objects.filter(user_id=user))
        if ai_buy > 0 and descriptive > 0:
            update_data = (applicants_list.objects.filter(user_id=user).order_by("id").values_list("id", flat=True)[:ai_buy])
            decrease_resume_count = ai_buy - descriptive
            client_features_balance.objects.filter(client_id_id=user, feature_id=27).update(available_count = decrease_resume_count)
            for x in update_data:
                applicants_list.objects.filter(id=x).update(is_active=False)


def Count_increase(feature):
    feature_id = 0
    if feature == "51" or feature == 51:
        feature_id = 10
    if feature == "52" or feature == 52:
        feature_id = 27
    if feature == "58" or feature == 58:
        feature_id = 53
    if feature == "56" or feature == 56:
        feature_id = 6
    return feature_id


def delete_addon(user):
    plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
    if Change_Validation(user) == True:
        remove_addon = client_features_balance.objects.filter(
            client_id=user, feature_id__in=[59, 60, 61, 62, 63]
        ).delete()


def Change_Validation(user):
    success = True
    plan_id = subscriptions.objects.filter(client_id=user).last().plan_id.pk
    if len(subscriptions.objects.filter(client_id=user)) > 2:
        preview_plan_id = (
            subscriptions.objects.filter(client_id=user)
            .order_by("-subscription_id")
            .values_list("plan_id", flat=True)[1]
        )

        if preview_plan_id == 7 and plan_id == 11:
            success = False
        elif preview_plan_id == 8 and plan_id == 12:
            success = False
        elif preview_plan_id == 11 and plan_id == 7:
            success = False
        elif preview_plan_id == 12 and plan_id == 8:
            success = False

    return success


def Invoice_retrieve(customer_id, amount):
    success = False
    try:
        balance = stripe.Customer.retrieve(customer_id).balance
        amount = json.loads(amount)
        if isinstance(amount, str):
            amount = int(amount)
        if isinstance(amount, float):
            amount = round(amount)
        if round(int(amount)) != 0:
            if balance > int(amount) or balance == int(amount):
                success = True
        else:
            success = True
    except Exception as e:
        pass
    return success

###: get the Stripe Date Convertions
def get_stripedate(timestamp : int):
    if timestamp:
        # Convert Unix timestamp to a datetime object in UTC
        invoice_date = datetime.utcfromtimestamp(timestamp)
        return invoice_date
    return None

##: Get the Date Between the dates
def get_compare_date(timestamp):
    if timestamp:
        date = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        # Calculate the difference in days
        difference = (date - now).days
        return difference
    return 0

#### Here update The Plan Count and Availble Count &&  Existsing-Addons
def Plan_with_Addon_Upgrade(user,plankey):
    if client_features_balance.objects.filter(client_id = user).exists() and plankey:
        features_balance = plan_features.objects.filter(plan_id=plankey, feature_id_id__in=[10, 27,53,6])
        for i in features_balance:
            if client_features_balance.objects.filter(client_id=user, feature_id=i.feature_id).exists():
                available_count = client_features_balance.objects.get(client_id=user, feature_id=i.feature_id).available_count
                addon_total = 0
                addon_id = expire_addons(i.feature_id.feature_id)
                if client_features_balance.objects.filter(client_id=user, feature_id=addon_id).exists():
                    addon_total = client_features_balance.objects.get(client_id=user, feature_id=addon_id).available_count
                total = i.feature_value + addon_total 
                plan_total = i.feature_value
                client_features_balance.objects.filter(client_id=user,feature_id=i.feature_id).update(available_count=total, plan_count=plan_total)
            elif not client_features_balance.objects.filter(client_id=user, feature_id=i.feature_id).exists():
                client_features_balance.objects.create(client_id=user, feature_id=i.feature_id, available_count=i.feature_value)


##### Here its a Auto Renewal Payment Based on Recurrent
def auto_renew_payment(user_id):
    if SubscriptionCustomer.objects.filter(user_id=user_id).exists():
        cus = SubscriptionCustomer.objects.get(user_id=user_id)
        subscr = subscriptions.objects.filter(client_id = user_id,is_active = True).last()

        if subscriptions.objects.filter(client_id=user_id).exists():
            try:
                from datetime import datetime, timedelta
                from django.utils import timezone
                subscription_id = get_last_subscription(cus.stripeCustomerId)
                if subscription_id:
                    subscription_start = get_stripedate(subscription_id.start_date)
                    subscription_current_period_start = get_stripedate(subscription_id.current_period_start)
                    print("When Auto Renewal Exists:-",subscription_start,subscription_current_period_start)
                    if subscription_start != subscription_current_period_start:  # Chnage
                        subs = stripe.Subscription.retrieve(subscription_id.id)
                        perid_end = subs.current_period_end
                        subs_last = subscriptions.objects.filter(client_id=user_id).last()
                        converted_time = datetime.fromtimestamp(perid_end).replace(tzinfo=pytz.utc)
                        time_period = subs_last.plan_id.subscription_value_days
                        last_payment = subs_last.subscription_valid_till  # chnage
                        print(f"Last Payment Date:{last_payment} \n Subscription End Date{converted_time}")
                        print("When Payment Date is Exceed:-",date_exceed_checking(last_payment, converted_time))
                        if date_exceed_checking(last_payment, converted_time):
                            record = subs_last  # duplicate subscriptions
                            new_record = deepcopy(record)
                            new_record.subscription_id = None
                            new_record.subscription_start_ts = datetime.fromtimestamp(subs.current_period_start).replace(tzinfo=pytz.utc)
                            new_record.subscription_end_ts = datetime.fromtimestamp(subs.current_period_end).replace(tzinfo=pytz.utc)
                            new_record.subscription_valid_till = datetime.fromtimestamp(subs.current_period_end).replace(tzinfo=pytz.utc)
                            new_record.subscription_remains_days = get_compare_date(subs.current_period_end)
                            new_record.is_active = True
                            new_record.no_of_users = 1
                            new_record.auto_renewal = 1
                            new_record.subscription_changed_to = None
                            new_record.created_at = datetime.fromtimestamp(subs.current_period_start).replace(tzinfo=pytz.utc)
                            subs_last.is_active = False
                            subs_last.save()
                            new_record.save()
                            Plan_with_Addon_Upgrade(user_id,subs_last.plan_id)
                return True
            except Exception as e:
                print("Auto Renewal Exceptions",str(e))
                return False
    else:
        return None


def get_last_subscription(customer_id):
    subscriptions = stripe.Subscription.list(customer=customer_id)

    # Sort subscriptions by creation date (in descending order)
    sorted_subscriptions = sorted(
        subscriptions.data, key=lambda x: x.created, reverse=True
    )

    if sorted_subscriptions:
        return sorted_subscriptions[0]  # Return the most recent subscription
    else:
        return None  # No subscriptions found for the customer


def subscription_sendmail(userid, name=None):
    domain = settings.CLIENT_URL
    if subscriptions.objects.filter(client_id=userid, is_active=True).exists():
        response = subscriptions.objects.filter(
            client_id=userid, is_active=True
        ).values()
        result = response.annotate(
            plan_name=Subquery(
                tmeta_plan.objects.filter(plan_id=OuterRef("plan_id"))[:1].values(
                    "plan_name"
                )
            ),
            price=Subquery(
                tmeta_plan.objects.filter(plan_id=OuterRef("plan_id"))[:1].values(
                    "price"
                )
            ),
        )
        plandetails = result[0]

        subscription = subscriptions.objects.filter(client_id=userid)
        if name == "renewal":
            subject = "Your Zita Subscription Has Been Successfully Renewed"
            email_template_name = get_template(
                "email_templates/plan_renewal_email.html"
            )
            c = {"user": userid, "plandetails": plandetails, "domain": domain}
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

            return name
        if len(subscription) == 1 and subscription.first().plan_id.pk > 1:
            if client_features_balance.objects.filter(
                client_id=userid,
                add_ons_id__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            ).exists():
                addon = True
                addon_values = client_features_balance.objects.filter(
                    client_id=userid,
                    add_ons_id__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                ).values()
                result = addon_purchase(userid, planname="plan_and_pricing")
                subject = "Welcome to Zita – Your Smart Hiring Starts Here"
                email_template_name = get_template(
                    "email_templates/subscription_template.html"
                )
                final_value = plandetails["price"]
                for i in result:
                    final_value += int(i["price"])
                total_cost = final_value
                c = {
                    "user": userid,
                    "plandetails": plandetails,
                    "domain": domain,
                    "result": result,
                    "total_cost": total_cost,
                }
            else:
                addon = False
                subject = "Welcome to Zita – Your Smart Hiring Starts Here"
                email_template_name = get_template(
                    "email_templates/subscription_template.html"
                )
                c = {"user": userid, "plandetails": plandetails, "domain": domain}
        else:
            second_last = None
            if subscription.count() > 1:
                last_sub = subscription.last().subscription_id
                second_last = subscription.exclude(
                    subscription_id=last_sub
                )  # Assuming id is the ordering field
                second_last_subscription = second_last.last().plan_id.plan_name

            if (
                second_last
                and subscription.last().plan_id.pk < second_last.last().plan_id.pk
            ):
                subject = "Confirmation of Your Plan Downgrade at Zita"
                email_template_name = get_template("email_templates/downgrade.html")
                c = {
                    "user": userid,
                    "plandetails": plandetails,
                    "domain": domain,
                    "second_last_subscription": second_last_subscription,
                }
            else:
                subject = "Confirmation of Your Plan Upgrade at Zita"
                email_template_name = get_template("email_templates/upgrade.html")
                c = {
                    "user": userid,
                    "plandetails": plandetails,
                    "domain": domain,
                    "second_last_subscription": second_last_subscription,
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
        return result


def stripe_plan_price(planKey):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    price_id = planKey
    price = stripe.Price.retrieve(price_id)
    amount = price.unit_amount
    amount_in_dollars = amount / 100.0


def addon_purchase(
    userid, addon=None, quantity=None, planname=None
):  # along with credits purchase Quantity,product
    if subscriptions.objects.filter(client_id=userid, is_active=True).exists():
        plan = (
            subscriptions.objects.filter(client_id=userid, is_active=True)
            .last()
            .plan_id.pk
        )
        response = []
        if addon and quantity and planname == None:
            for x, y in zip(addon, quantity):
                feature_count = addons_plan_features.objects.get(
                    plan_id=plan, addon_id=x
                ).value
                # final_count = final_count if final_count else 0
                # final_count = int(feature_count) * int(y)
                final_count = (
                    int(feature_count) * int(y)
                    if feature_count
                    else "Unlimited (During subscription)"
                )
                addon_name = tmeta_addons.objects.get(id=x).name
                decription = tmeta_addons.objects.get(id=x).display_name
                price = addons_plan_features.objects.get(plan_id=plan, addon_id=x).price
                price = int(price) * int(y) if price else 0
                obj = {
                    "name": addon_name,
                    "price": price,
                    "quantity": final_count,
                    "description": decription.replace('"', ""),
                }
                response.append(obj)
        elif (
            planname and addon and quantity
        ):  # subscription with addons(userid,plan=newplanwithaddons)
            resp = subscriptions.objects.filter(
                client_id=userid, is_active=True
            ).values()  # new API
            resp = resp.annotate(
                plan_name=Subquery(
                    tmeta_plan.objects.filter(plan_id=OuterRef("plan_id"))[:1].values(
                        "plan_name"
                    )
                ),
                price=Subquery(
                    tmeta_plan.objects.filter(plan_id=OuterRef("plan_id"))[:1].values(
                        "price"
                    )
                ),
            )
            for x, y in zip(addon, quantity):
                feature_count = addons_plan_features.objects.get(
                    plan_id=plan, addon_id=x
                ).value
                final_count = (
                    int(feature_count) * int(y)
                    if feature_count
                    else "Unlimited (During subscription)"
                )
                addon_name = tmeta_addons.objects.get(id=x).name
                decription = tmeta_addons.objects.get(id=x).display_name
                price = addons_plan_features.objects.get(plan_id=plan, addon_id=x).price
                price = int(price) * int(y) if price else 0
                obj = {
                    "name": addon_name,
                    "price": price,
                    "quantity": final_count,
                    "description": decription.replace('"', ""),
                }
                response.append(obj)

        elif planname == "plan_and_pricing":  # Plan and Pricing Calculate
            if client_features_balance.objects.filter(
                client_id=userid,
                add_ons_id__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            ).exists():
                data = client_features_balance.objects.filter(
                    client_id=userid,
                    add_ons_id__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                ).values()
                for i in data:
                    feature_count = addons_plan_features.objects.get(
                        plan_id=plan, addon_id=i["add_ons_id"]
                    ).value
                    final_count = (
                        int(feature_count) * int(i["addons_count"])
                        if feature_count
                        else "Unlimited (During subscription)"
                    )
                    addon_name = tmeta_addons.objects.get(id=i["add_ons_id"]).name
                    decription = tmeta_addons.objects.get(
                        id=i["add_ons_id"]
                    ).display_name
                    price = addons_plan_features.objects.get(
                        plan_id=plan, addon_id=i["add_ons_id"]
                    ).price
                    price = int(price) * int(i["addons_count"]) if price else 0
                    obj = {
                        "name": addon_name,
                        "price": price,
                        "quantity": final_count,
                        "description": decription.replace('"', ""),
                    }
                    response.append(obj)
        return response


def description_change(key):
    if key == "1":
        return ""



''' This Function Will Send CouponCode to the User With Templates'''
def senduser_couponcode(user,coupon,expired_date=None,type_coupon = None):
    if expired_date:
        expired_date = expired_date.date()
    plan_type = coupon.discount_type
    coupon_type = "%"
    coupon_category = "OFF"
    if plan_type == "Fixed":
        coupon_type = ""
        coupon_category = "Flat Discount"
    discount_amount = f'{coupon.discount_value}{coupon_type}'
    d = {   
        "user": user,"code": coupon.discount_name,
        "date": expired_date,
        "discounts":discount_amount,
        "purchase_amount":coupon.min_amount,   ## Min Amount Will Replace it After the Implementation
        "type_coupon":type_coupon,
        "coupon_category":coupon_category
        }
    htmly = get_template("coupon_code/coupon.html")
    subject, from_email, to = (f"Exclusive Discount Inside: Use Code {coupon.discount_name} for {discount_amount} {coupon_category}! ",email_main,user.email)
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
    return True


## verify that Function Are Coupon are currently associated with that
def verify_Coupon(coupon):
    coupon_details  = Coupon.listof_coupon(limit=1000)
    if isinstance(coupon_details,dict):
        coupon_check = coupon_details.get('data',[])
        exitsing_coupon = [i.get('name') for i in coupon_check]
        if coupon in  exitsing_coupon:
            promo_details = PromoCode.listof_promocode(limit=1000)
            if isinstance(promo_details,dict):
                promo_check = promo_details.get('data',[])
                availble_promo = promo_details = [i.get('coupon').get('name') for i in promo_details if i.get('coupon')]
                if coupon not in availble_promo:
                    return True
    return False

## Here its a Coupon Claimed By User 
def Coupon_claimed(checkout,invoice = None):
    print("checkkkkkkkk",checkout,invoice)
    if invoice:
        user_invoice = Invoice.retrieve_invoice(invoice)
        customer_id = user_invoice.customer
        user_id = None
        if customer_id:
            if SubscriptionCustomer.objects.filter(stripeCustomerId=customer_id).exists():
                user_id = SubscriptionCustomer.objects.get(stripeCustomerId=customer_id).user_id

    else:
        user_id = checkout.get('client_reference_id')
        if user_id == None:
            user_email = checkout.get('customer_email')
            if User.objects.filter(email = user_email).exists():
                user_id = User.objects.get(email = user_email)
        invoice = checkout.get('invoice')
    if invoice and user_id:
        print("##@!@@@",user_id)
        invoice = Invoice.retrieve_invoice(invoice)
        discounts_coupon = invoice.get('discount')
        print("@@_@)@)@)@",discounts_coupon)
        if discounts_coupon and discounts_coupon.get('coupon'):
            coupon = discounts_coupon.get('coupon')
            print("coupon",coupon)
            if coupon:
                coupon_name = coupon.get('name')
                coupon_id = coupon.get('id')
                discount = None
                addons = False
                if discounts.objects.filter(discount_name = coupon_name,discount_code = coupon_id).exists():
                    discount = discounts.objects.get(discount_name = coupon_name,discount_code = coupon_id)
                if discounts_addon.objects.filter(discount_name = coupon_name,discount_code = coupon_id).exists():
                    addons = True
                    discount = discounts_addon.objects.get(discount_name = coupon_name,discount_code = coupon_id)
                if discount:
                    if not isinstance(user_id,User):
                        user_id = User.objects.get(id = user_id)
                    if addons == True:
                        discount_codes_claimed.objects.create(client_id = user_id,discount_addon = discount,is_claimed = True)
                    elif addons == False:
                        local_sub = subscriptions.objects.filter(client_id=user_id).last()
                        discount_codes_claimed.objects.create(client_id = user_id,discount_id = discount,is_claimed = True,subscription_id = local_sub )
    return True
