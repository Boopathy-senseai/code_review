import json

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
from django.core.mail import send_mail
from jobs.models import *
from users.models import UserHasComapny
from jobs.views import admin_account
from django.utils import timezone
import pytz
import datetime
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

domain = "192.168.3.156:84"


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        """
        Join channel group by chatname.
        """
        self.group_name = "chat_{0}".format(
            self.scope["url_route"]["kwargs"]["chatname"]
        )
        self.jd_id = "jd_id_{0}".format(self.scope["url_route"]["kwargs"]["jd_id"])

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name,
        )

        self.accept()

    def disconnect(self, close_code):
        """
        Leave channel by group name.
        """

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name,
        )

    def receive(self, text_data):
        """
        Receive message from websocket and send message to channel group.
        """
        text_data_json = json.loads(text_data)
        username = text_data_json["username"]
        message = text_data_json["message"]
        # Store message.
        users = self.group_name.replace("chat_", "").split("-")
        jd_id = self.jd_id.replace("jd_id_", "")
        if self.scope["user"].is_staff:

            if company_details.objects.filter(recruiter_id=self.scope["user"]).exists():
                sender = self.scope["user"]
            else:
                sender = UserHasComapny.objects.get(user=self.scope["user"]).company
                sender = sender.recruiter_id
            users.remove(str(sender.id))
            company_name = company_details.objects.get(recruiter_id=sender).company_name
        else:
            users.remove(str(self.scope["user"].id))
            sender = self.scope["user"]
            company_name = sender.first_name

        receiver = User.objects.get(id=int(users[0]))
        Message(sender=sender, receiver=receiver, text=message, jd_id_id=jd_id).save()
        self.receiver = receiver
        if self.scope["user"].is_staff:
            try:
                emp_can = employer_pool.objects.get(
                    client_id=self.scope["user"], email=receiver.email
                )
            except:
                emp_can = None
            if (
                applicants_status.objects.filter(
                    client_id=self.scope["user"], candidate_id=emp_can, jd_id_id=jd_id
                ).exists()
                == False
                or Candi_invite_to_apply.objects.filter(
                    client_id=self.scope["user"], candidate_id=emp_can, jd_id_id=jd_id
                ).exists()
                == False
            ):
                Candi_invite_to_apply.objects.create(
                    client_id=self.scope["user"], candidate_id=emp_can, jd_id_id=jd_id
                )
            htmly = get_template("jobs/message.html")

            subject, from_email, to = (
                "You got a message from " + company_name,
                "support@zita.ai",
                "support@zita.ai",
            )
            html_content = htmly.render(
                {
                    "sender": sender,
                    "receiver": receiver,
                    "jd_id": jd_id,
                    "company_name": company_name,
                    "message": message,
                    "domain": domain,
                    "date": timezone.now(),
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            msg.send()
        else:
            htmly = get_template("jobs/message_staff.html")

            subject, from_email, to = (
                "You got a message from " + company_name,
                "support@zita.ai",
                receiver.email,
            )
            html_content = htmly.render(
                {
                    "sender": sender,
                    "receiver": receiver,
                    "jd_id": jd_id,
                    "company_name": company_name,
                    "message": message,
                    "domain": domain,
                    "date": timezone.now(),
                }
            )
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = "related"
            msg.send()

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                "type": "chat_message",
                "username": sender.first_name,
                "message": message,
                "sender": sender.id,
                "jd_id": jd_id,
                "date_created": str(timezone.now()),
            },
        )

    def chat_message(self, event):
        """
        Receive message from channel group and send message to websocket.
        """

        self.send(
            text_data=json.dumps(
                {
                    "username": event["username"],
                    "message": event["message"],
                    "sender": event["sender"],
                    "jd_id": event["jd_id"],
                    "date_created": str(timezone.now()),
                }
            )
        )
