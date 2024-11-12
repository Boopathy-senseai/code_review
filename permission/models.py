from django.contrib.auth.models import Permission
from django.db import models


if not hasattr(Permission, "order"):
    order = models.IntegerField(default=0)
    order.contribute_to_class(Permission, "order")
