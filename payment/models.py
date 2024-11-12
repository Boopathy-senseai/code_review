from django.contrib.auth.models import User
from django.db import models


class SubscriptionCustomer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255, null=True)

    class Meta:
        app_label = "payment"


class website_details(models.Model):
    addons = models.TextField(null=True)
    card_view = models.TextField(null=True)
