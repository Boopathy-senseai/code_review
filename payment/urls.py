from django.urls import path

from . import views
from . import api

urlpatterns = [
    # path('payment/', views.home, name='home'),
    # path('api/create-checkout-session/', api.create_checkout_session),
    path("create-subscription-session/", views.create_subscription_session),
    path("success/", views.SuccessView, name="success"),
    path("summary/", views.order_summary, name="order_summary"),
    path("credits_purchase/", views.credits_purchase, name="credits_purchase"),
    path("cancel_subscription/", views.cancel_subscription, name="cancel_subscription"),
    path("renew-subscription/", views.renew_subscription, name="renew_subscription"),
    path("cancelled/", views.CancelledView.as_view()),
    path("webhook/", views.stripe_webhook),
    path(
        "account/subscription/", views.manage_subscription, name="manage_subscription"
    ),
    path("billing_portal/<int:pk>", views.billing_portal, name="billing_portal"),
    path("api/config/", views.stripe_config),
    path(
        "api/manage_subscription",
        api.manage_subscription.as_view(),
        name="manage_subscription_api",
    ),
    path("api/order_summary", api.order_summary.as_view(), name="order_summary_api"),
    path(
        "api/renew_subscription",
        api.renew_subscription.as_view(),
        name="renew_subscription_api",
    ),
    path(
        "api/cancel_subscription",
        api.cancel_subscription.as_view(),
        name="cancel_subscription_api",
    ),
    path("api/billing_portal", api.billing_portal.as_view(), name="billing_portal_api"),
    path(
        "api/create-checkout-session/",
        api.create_checkout_session,
        name="create_checkout_session_api",
    ),
    path(
        "api/create_subscription_session",
        api.create_subscription_session,
        name="create_subscription_session_api",
    ),
    path(
        "api/backend_process", api.backend_process.as_view(), name="backend_process_api"
    ),
    path(
        "api/credits_purchase",
        api.credits_purchase.as_view(),
        name="credits_purchase_api",
    ),
    path(
        "api/checkout_session", api.checkout_session.as_view(), name="checkout_session"
    ),
    path("api/stripe_config", api.stripe_config, name="stripe_config_api"),
    path(
        "api/website_details_api",
        api.website_details_api.as_view(),
        name="website_details_api",
    ),
    path("api/plan_change", api.plan_change_api.as_view(), name="plan_change"),
    path(
        "api/auto_payment", api.auto_payment_stripe_api.as_view(), name="auto_payment"
    ),
    path("api/subscription_email",api.subscription_email_api.as_view(),name="subscription_email"),
    path("api/coupon_api",api.coupon_code_api.as_view(),name="coupon_api"),
]
