from datetime import datetime
from calendarapp.models import google_return_details, outlook_return_details
from jobs.models import (
    JD_form,
    applicants_status,
    company_details,
    employer_pool,
    pipeline_view,
    subscriptions,
    tour_data,
)
from jobs.views import admin_account
from login.models import *
from cryptography.fernet import InvalidToken
from zita.helper import EncryptDecrypt, Helper
from django.contrib.auth.hashers import make_password
from permission.serializers import PermissionSerializer
from rest_framework.views import APIView
from users.mailer import Mailer
from django.conf import settings
from users.models import (
    CompanyHasInvite,
    Department,
    UserAction,
    UserActivityListModel,
    UserHasComapny,
    UserListWithDetail,
    UserStatus,
    UserWithDetail,
    UserActivity,
)
from django.contrib.auth.models import Group, Permission, User
from django.http.response import Http404, HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import (
    ActionSerializer,
    ActivityListSerializer,
    CompanyInviteSerializer,
    CompanySerializer,
    DepartmentSerializer,
    GetUserHasCompanySerializer,
    UserDetailSerializer,
    UserHasCompanySerializer,
    UserInviteSerializer,
    UserListSerializer,
    UserListWithDetailSerializer,
    UserSerializer,
    UserStatusSerializer,
    UserUpdateSerializer,
    UserWithDetailSerializer,
)
from accounts.serializers import UserSerializer as MainUserSerializer
import collections
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from login.views import expire_link
from zita.settings import CLIENT_URL
from django.template.loader import get_template
from email.mime.image import MIMEImage
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives


def logo_data(img):
    with open(finders.find("images/" + img), "rb") as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header("Content-ID", img)
    return logo


class UserList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserListWithDetail.objects.all()
    serializer_class = UserListWithDetailSerializer

    def get(self, request, format=None):
        domain1 = Signup_Form.objects.filter(user_id=request.user.id).values("domain")
        data = domain1[0]
        domain = data["domain"]
        allowed_domains = [domain]
        try:
            plan = subscriptions.objects.get(
                client_id=self.request.user, is_active=True
            ).plan_id.pk
        except:
            plan = 0
        try:
            profile_pic = str(Profile.objects.get(user=self.request.user).image)
        except:
            profile_pic = None
        try:
            company = company_details.objects.get(recruiter_id=self.request.user)
        except company_details.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "msg": "The Company does not exist",
                    "data": {"plan": plan, "profile_pic": profile_pic},
                }
            )

        company_serializer = CompanySerializer(company).data
        users = UserListWithDetail.objects.raw(
            "SELECT auth_user.id, auth_user.first_name, auth_user.last_name, jobs_company_details.id as company_id, jobs_company_details.company_name, auth_user.email, auth_user.date_joined, user_details.contact as contact_number, departments.name as department_name, auth_group.name as group_name, tmeta_user_status.status, user_has_company.invited_at FROM auth_user INNER JOIN user_has_company ON user_has_company.user_id = auth_user.id LEFT JOIN jobs_company_details ON jobs_company_details.id = user_has_company.company_id INNER JOIN tmeta_user_status ON tmeta_user_status.user_id = auth_user.id LEFT JOIN user_details ON user_details.user_id = auth_user.id LEFT JOIN departments ON departments.id = user_has_company.department_id INNER JOIN auth_user_groups ON auth_user_groups.user_id = auth_user.id LEFT JOIN auth_group ON auth_group.id = auth_user_groups.group_id WHERE user_has_company.company_id = "
            + str(company_serializer["id"])
        )
        serializer = UserListWithDetailSerializer(users, many=True)
        serializer.context["self"] = self
        try:
            plan = subscriptions.objects.get(
                client_id=self.request.user, is_active=True
            ).plan_id.pk
        except:
            plan = 0
        try:
            profile_pic = str(Profile.objects.get(user=self.request.user).image)
        except:
            profile_pic = None
            return Response(
                {"success": False, "msg": "The Company does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer.context["request"] = request
        return Response(
            {
                "success": True,
                "data": {
                    "users": serializer.data,
                    "plan": plan,
                    "profile_pic": profile_pic,
                    "email_domain": domain,
                },
            }
        )

    def post(self, request, format=None):
        cur_datetime = datetime.now()

        try:
            company = company_details.objects.get(recruiter_id=self.request.user)
        except company_details.DoesNotExist:
            return Response(
                {"success": False, "msg": "The Company does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        company_serializer = CompanySerializer(company).data
        check_invite_available = CompanyInvite.checkHasInvites(company_serializer["id"])
        if not check_invite_available:
            return Response(
                {"success": False, "msg": "Insufficient invites"},
                status=status.HTTP_404_NOT_FOUND,
            )

        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if email and user:
            return Response(
                {"success": False, "msg": "This email Id is already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        role = request.data["role"]
        permissions = request.data["permissions"]
        permission_ids = tuple(permissions)
        user_input_data = request.data
        user_input_data["username"] = request.data["email"]
        user_input_data["is_staff"] = 1
        user_input_data["is_active"] = 0
        user_input_data["detail"] = {"contact": user_input_data["contact"]}
        user_input_data["status"] = {"status": 0}
        user_input_data["department"] = {"name": request.data["department"]}

        # return Response(company_serializer)
        serializer = UserInviteSerializer(data=user_input_data)
        serializer.context["company_id"] = company_serializer["id"]

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            group = Group.objects.get(id=role)
        except Group.DoesNotExist:
            return Response(
                {"success": False, "msg": "The role does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.groups.add(group)
        try:
            permissions = Permission.objects.filter(id__in=permission_ids)
        except Permission.DoesNotExist:
            return Response(
                {"success": False, "msg": "The permission does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.user_permissions.set(permissions)
        user_data = UserSerializer(user, context=UserInviteSerializer()).data

        CompanyInvite.decreaseInvite(company_serializer["id"], "-")

        enc_data = str(user_data["id"]) + "{0}" + str(cur_datetime)
        enc_data = EncryptDecrypt.encrypt_message(enc_data)
        encrypt = str(enc_data, "utf-8")
        current_site = get_current_site(self.request)
        url = settings.CLIENT_URL + "/set-password/" + encrypt
        admin_id, updated_by = admin_account(request)
        admin_name = (
            User.objects.get(username=admin_id).first_name
            + " "
            + User.objects.get(username=admin_id).last_name
        )
        Company_Name = company_details.objects.get(recruiter_id=admin_id).company_name
        privacy_url = "https://www.zita.ai/privacy-policy"
        Privacy_Policy = f'<a href={privacy_url} target="_blank" rel="noopener noreferrer">Privacy Policy</a>'
        email_template_name = get_template("email_templates/invite_user.html")
        c = {
            "admin_name": admin_name,
            "Company_Name": Company_Name,
            "Privacy_Policy": Privacy_Policy,
            "url": url,
            "user": user,
            "privacy_url": privacy_url,
        }
        try:
            email = email_template_name.render(c)
            subject = "Email Confirmation"
            msg = EmailMultiAlternatives(
                subject, email, settings.EMAIL_HOST_USER, [user_data["email"]]
            )
            msg.attach_alternative(email, "text/html")
            msg.mixed_subtype = "related"
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

        # html = "<p>Hi "+user_data['first_name']+",</p>"  [user_data['email']]
        # html += "<p><b>Join your team in Zita.</b></p>"
        # html += f"<p>Hi! {admin_name} invited you to the <b>{Company_Name}</b> team in Zita. Join now and start recruiting together.</p>"
        # html += "<p>Zita is an AI powered Talent Acquisition Platform for recruiters and hiring managers.</p>"
        # html += f'<p>By clicking <b>"Join now"</b> you confirm that you read Zita’s {Privacy_Policy}</p>'
        # html += f'<a href={url} target="_blank" rel="noopener noreferrer" style="display: inline-block; padding: 10px 20px; background-color: #581845; color: #ffffff; text-decoration: none; border-radius: 5px;">Join Now</a>'
        # html += "<br><br>"
        # html += '<p>Regards,</p>'
        # html += '<p>Zita</p>'
        # mail = Mailer.send(user_data['email'],settings.DEFAULT_FROM_EMAIL, "Email Confirmation", html, "html")
        except Exception as e:
            pass
        return Response({"success": True, "data": user_data})


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserListSerializer

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        users = UserWithDetail.objects.raw(
            "SELECT auth_user.id, auth_user.first_name, auth_user.last_name, jobs_company_details.id as company_id, jobs_company_details.company_name, auth_user.email, auth_user.date_joined, user_details.contact as contact_number, departments.id as department_id, departments.name as department_name, auth_group.id as group_id, auth_group.name as group_name, tmeta_user_status.status, user_has_company.invited_at FROM auth_user INNER JOIN user_has_company ON user_has_company.user_id = auth_user.id LEFT JOIN jobs_company_details ON jobs_company_details.id = user_has_company.company_id INNER JOIN tmeta_user_status ON tmeta_user_status.user_id = auth_user.id LEFT JOIN user_details ON user_details.user_id = auth_user.id LEFT JOIN departments ON departments.id = user_has_company.department_id INNER JOIN auth_user_groups ON auth_user_groups.user_id = auth_user.id LEFT JOIN auth_group ON auth_group.id = auth_user_groups.group_id WHERE auth_user.id = "
            + str(pk)
            + " LIMIT 1"
        )
        user_serializer = UserWithDetailSerializer(users, many=True).data
        user_permissions = Permission.objects.filter(user__id=pk)
        permission_serializer = PermissionSerializer(user_permissions, many=True).data

        return Response(
            {
                "success": True,
                "data": {"user": user_serializer, "permissions": permission_serializer},
            }
        )

    def delete(self, request, pk, format=None):
        try:
            company = company_details.objects.get(recruiter_id=self.request.user)
        except company_details.DoesNotExist:
            return Response(
                {"success": False, "msg": "The Company does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if google_return_details.objects.filter(client_id=pk).exists():
            google_return_details.objects.filter(client_id=pk).delete()
        elif outlook_return_details.objects.filter(client_id=pk).exists():
            outlook_return_details.objects.filter(client_id=pk).delete()
        company_serializer = CompanySerializer(company).data

        user = self.get_object(pk)
        user.delete()
        CompanyInvite.decreaseInvite(company_serializer["id"], "+")
        return Response({"success": True, "msg": "Deleted successfull"})

    def put(self, request, pk, format=None):
        profile = Profile.objects.get(user_id=pk)
        if profile.image == '' or not profile.image:
            profile.image = 'default.jpg'
            profile.save()
        try:
            company = company_details.objects.get(recruiter_id=self.request.user)
        except company_details.DoesNotExist:
            return Response(
                {"success": False, "msg": "The Company does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        company_serializer = CompanySerializer(company).data
        role = request.data["role"]
        permissions = request.data["permissions"]
        permission_ids = tuple(permissions)
        user_input_data = request.data
        user_input_data["username"] = request.data["email"]
        user_input_data["is_staff"] = 1
        user_input_data["is_active"] = 0
        user_input_data["detail"] = {"contact": user_input_data["contact"]}
        user_input_data["status"] = {"status": 0}
        user_input_data["department"] = {"name": request.data["department"]}

        user_obj = self.get_object(pk)
        serializer = UserInviteSerializer(user_obj, data=request.data)
        serializer.context["pk"] = pk
        serializer.context["company_id"] = company_serializer["id"]
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            group = Group.objects.get(id=role)
        except Group.DoesNotExist:
            return Response(
                {"success": False, "msg": "The role does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.groups.clear()
        user.groups.add(group)
        try:
            permissions = Permission.objects.filter(id__in=permission_ids)
        except Permission.DoesNotExist:
            return Response(
                {"success": False, "msg": "The permission does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.user_permissions.set(permissions)
        user_data = UserSerializer(user, context=UserInviteSerializer()).data

        return Response({"success": True, "data": user_data})


class UserUpdateStatus(generics.GenericAPIView):
    def put(self, request, pk, format=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"success": False, "msg": "The user does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.data.get("status") == 1:
            user.is_active = 1
        else:
            user.is_active = 0
        user.save()

        user_status = UserStatus.objects.get(user=user)
        user_status.status = request.data.get("status")
        user_status.save()

        return Response({"success": True, "msg": "Updated successfull"})


class UserActivityList(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {"success": False, "msg": "The user does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user = UserSerializer(user).data

        activities = UserActivityListModel.objects.raw(
            "SELECT user_activity.id,user_action.action_description, user_activity.action_detail, user_activity.created_at FROM user_activity LEFT JOIN user_action ON user_action.id = user_activity.action_id WHERE user_activity.user_id = "
            + str(user["id"])
        )

        activities = ActivityListSerializer(activities, many=True).data

        return Response(
            {"success": True, "data": {"user": user, "activities": activities}}
        )


from collections import defaultdict
from django.db.models import Count


class UserActivityCount(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(id=pk)
            emp = pk
            sub_user = pk
        except User.DoesNotExist:
            return Response(
                {"success": False, "msg": "The user does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user = UserSerializer(user).data

        actions = UserAction.objects.all()
        actions = ActionSerializer(actions, many=True).data
        counts_list = collections.defaultdict(list)
        for action in actions:
            data_time = 0
            date_time_data = ActivityListSerializer(
                UserActivityListModel.objects.raw(
                    "SELECT user_activity.id,user_action.action_description, user_action.category_id, user_activity.action_detail, user_activity.created_at FROM user_activity LEFT JOIN user_action ON user_action.id = user_activity.action_id WHERE user_activity.user_id = "
                    + str(user["id"])
                    + " AND user_activity.action_id="
                    + str(action["id"])
                    + " ORDER BY user_activity.id DESC"
                ),
                many=True,
            ).data
            if len(date_time_data) > 0:
                data_time = date_time_data[0]["created_at"]
            # if actions['description'] ==
            pk = JD_form.objects.filter(user_id=emp).values_list("id", flat=True)
            emp,updated_by = admin_account(request)
            employers = employer_pool.objects.filter(client_id=emp).values("id")
            Shortlisted = pipeline_view.objects.filter(
                jd_id__in=pk, emp_id=emp, stage_name="Shortlisted"
            ).values("id")
            Offered = pipeline_view.objects.filter(
                jd_id__in=pk, emp_id=emp, stage_name="Hired"
            ).values("id")
            Rejected = pipeline_view.objects.filter(
                jd_id__in=pk, emp_id=emp, stage_name="Rejected"
            ).values("id")
            shortlisted = applicants_status.objects.filter(
                jd_id_id__in=pk, stage_id__in=Shortlisted, client_id=emp
            ).values("candidate_id")
            offered = applicants_status.objects.filter(
                jd_id_id__in=pk, stage_id__in=Offered, client_id=emp
            ).values("candidate_id")
            rejected = applicants_status.objects.filter(
                jd_id_id__in=pk, stage_id__in=Rejected, client_id=emp
            ).values("candidate_id")
            if action["action_description"] == "Shortlisted":
                shortlisted = shortlisted.filter(candidate_id__user_id = sub_user)
                count = len(shortlisted)
            elif action["action_description"] == "Offered":
                offered = offered.filter(candidate_id__user_id = sub_user)
                count = len(offered)
            elif action["action_description"] == "Rejected":
                rejected = rejected.filter(candidate_id__user_id = sub_user)
                count = len(rejected)
            elif action["action_description"] == "Imported Applicants":
                applicants = employers.filter(can_source_id__in=[1],candidate_id__isnull = False,user_id = sub_user)
                count = len(applicants)
            elif action["action_description"] == "Imported Candidates":
                candidates = employers.filter(can_source_id__in=[1],candidate_id__isnull = True,user_id = sub_user)
                count = len(candidates)
            elif action["action_description"] == "Unlocked":
                unlocked = employers.filter(can_source_id__in=[2,5],candidate_id__isnull = True,user_id = sub_user)
                count = len(unlocked)
            else:
                # count = len(ActivityListSerializer(UserActivityListModel.objects.raw('SELECT user_activity.id, user_action.category_id, user_action.action_description, user_activity.action_detail, user_activity.created_at FROM user_activity LEFT JOIN user_action ON user_action.id = user_activity.action_id WHERE user_activity.user_id = '+str(user['id'])+' AND user_activity.action_id='+str(action['id'])), many=True).data),
                count = UserActivity.objects.filter(
                    user_id=user["id"], action_id=action["id"]
                ).count()

            counts = {
                "category": action["category_id"],
                "name": action["action_description"],
                "count": count,
                "date_time": data_time,
            }

            counts_list[action["category_id"]].append(counts)

        return Response(
            {"success": True, "data": {"user": user, "activities": counts_list}}
        )


class UserResendMail(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListSerializer

    def post(self, request, *args, **kwargs):
        admin_id, updated_by = admin_account(request)
        cur_datetime = datetime.now()
        try:
            user = User.objects.get(id=request.data["id"])
        except User.DoesNotExist:
            return Response(
                {"success": False, "msg": "The user does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            company = UserHasComapny.objects.get(user=user)
        except UserHasComapny.DoesNotExist:
            return Response(
                {"success": False, "msg": "The user does not have company"},
                status=status.HTTP_404_NOT_FOUND,
            )

        company.invited_at = cur_datetime
        company.save()
        user = UserSerializer(user).data
        enc_data = str(user["id"]) + "{0}" + str(cur_datetime)
        enc_data = EncryptDecrypt.encrypt_message(enc_data)
        encrypt = str(enc_data, "utf-8")
        current_site = get_current_site(self.request)
        url = settings.CLIENT_URL + "/set-password/" + encrypt
        Company_Name = company_details.objects.get(recruiter_id=admin_id).company_name
        admin_name = (
            User.objects.get(username=admin_id).first_name
            + " "
            + User.objects.get(username=admin_id).last_name
        )
        privacy_url = "https://www.zita.ai/privacy-policy"
        Privacy_Policy = f'<a href={privacy_url} target="_blank" rel="noopener noreferrer">Privacy Policy</a>'
        # html = "<p>Hi "+user['first_name']+",</p>"
        # html += "<p><b>Join your team in Zita.</b></p>"
        # html += f"<p>Hi! {admin_name} invited you to the <b>{Company_Name}</b> team in Zita. Join now and start recruiting together.</p>"
        # html += "<p>Zita is an AI powered Talent Acquisition Platform for recruiters and hiring managers.</p>"
        # html += f'<p>By clicking <b>"Join now"</b> you confirm that you read Zita’s {Privacy_Policy}</p>'
        # html += f'<a href={url} target="_blank" rel="noopener noreferrer" style="display: inline-block; padding: 10px 20px; background-color: #581845; color: #ffffff; text-decoration: none; border-radius: 5px;">Join Now</a>'
        # html += "<br><br>"
        # html += '<p>Regards,</p>'
        # html += '<p>Zita</p>'
        # mail = Mailer.send(user['email'],settings.DEFAULT_FROM_EMAIL, "Email Confirmation", html, "html")
        email_template_name = get_template("email_templates/invite_user.html")
        c = {
            "admin_name": admin_name,
            "Company_Name": Company_Name,
            "Privacy_Policy": Privacy_Policy,
            "url": url,
            "user": user,
            "privacy_url": privacy_url,
        }
        try:
            email = email_template_name.render(c)
            subject = "Email Confirmation"
            msg = EmailMultiAlternatives(
                subject, email, settings.EMAIL_HOST_USER, [user["email"]]
            )
            msg.attach_alternative(email, "text/html")
            msg.mixed_subtype = "related"
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
        return Response({"success": True, "data": user})


class UserConfirmation(generics.UpdateAPIView):
    # queryset = User.objects.all()
    # serializer_class = UserUpdateSerializer

    def patch(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username=request.data["email"])
        except User.DoesNotExist:
            return Response(
                {"success": False, "msg": "The user does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.password = make_password(request.data["password"])
        user.is_active = 1
        user.save()
        if not tour_data.objects.filter(user_id=user.id).exists():
            tour_data.objects.create(
                user_id=User.objects.get(id=user.id), skip_id=0, is_first_login=True
            )
        user_status = UserStatus.objects.get(user=user)
        user_status.status = 1
        user_status.save()
        return Response({"ststus": True, "msg": "Email Confirmed!"})


class CompanyInvite(generics.GenericAPIView):
    # queryset = User.objects.all()
    # serializer_class = UserUpdateSerializer

    def get(self, request, *args, **kwargs):
        try:
            company = company_details.objects.get(recruiter_id=self.request.user)
        except company_details.DoesNotExist:
            return Response(
                {"success": False, "msg": "The Company does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        company_serializer = CompanySerializer(company).data

        try:
            invite = CompanyHasInvite.objects.get(company_id=company_serializer["id"])
        except CompanyHasInvite.DoesNotExist:
            return Response(
                {"success": False, "msg": "The invite does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        invite_serializer = CompanyInviteSerializer(invite).data

        return Response({"status": True, "data": invite_serializer})

    def decreaseInvite(company_id, cal="-", amount=1):
        try:
            invite = CompanyHasInvite.objects.get(company_id=company_id)
        except CompanyHasInvite.DoesNotExist:
            return Response(
                {"success": False, "msg": "The invite does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        invite_serializer = CompanyInviteSerializer(invite).data

        count = invite_serializer["invites"]
        if cal == "-":
            new_count = count - amount
        else:
            new_count = count + amount

        invite.invites = new_count
        invite.save()
        return True

    def checkHasInvites(company_id):
        try:
            invite = CompanyHasInvite.objects.get(company_id=company_id)
        except CompanyHasInvite.DoesNotExist:
            return Response(
                {"success": False, "msg": "The invite does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        invite_serializer = CompanyInviteSerializer(invite).data
        count = invite_serializer["invites"]

        # if count>0:
        return True
        # return False


class UserCheckToken(generics.UpdateAPIView):
    # queryset = User.objects.all()
    # serializer_class = UserUpdateSerializer

    def patch(self, request, *args, **kwargs):

        try:
            decrypt = EncryptDecrypt.decrypt_message(
                bytes(request.data.get("token"), encoding="raw_unicode_escape")
            )
        except InvalidToken:
            return Response(
                {"success": False, "msg": "Invalid Token"},
                status=status.HTTP_404_NOT_FOUND,
            )

        get_enc_list = str(decrypt, "utf-8").split("{0}")
        user_id = get_enc_list[0]
        datetime = get_enc_list[1]
        if Helper.checkDatetimeExpiry(datetime, 24, "h"):
            # expire_user = expire_link(user_id)
            user = None
            if User.objects.filter(id=user_id).exists():
                user = User.objects.filter(id=user_id).values()[0]
            return Response(
                {
                    "success": False,
                    "msg": "Token expired!",
                    "user": user,
                },
                status=status.HTTP_200_OK,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "msg": "The user does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        user_serializer = UserSerializer(user).data

        if user_serializer["is_active"] > 0:
            return Response(
                {"success": True, "msg": "Already veryfied!"}, status=status.HTTP_200_OK
            )

        return Response(
            {"status": True, "data": user_serializer, "msg": "Token Checked!"}
        )


# Department Viewset
class DepartmentAPI(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        try:
            company = company_details.objects.get(recruiter_id=self.request.user)
        except company_details.DoesNotExist:
            return Response(
                {"success": False, "msg": "The Company does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        company_serializer = CompanySerializer(company).data
        queryset = Department.objects.filter(company_id=company_serializer["id"])
        serializer = DepartmentSerializer(queryset, many=True)
        return Response({"status": True, "data": serializer.data})
