from django.http import JsonResponse
from .models import *
from rest_framework import generics, permissions, status
from rest_framework.response import Response
import json
from jobs.models import *
from users.models import *
from django.db.models import Q
import datetime
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("jobs_api")
from jobs.views import admin_account, user_permission

import zipfile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from jobs.utils import plan_checking


def zita_default(user):
    valid = Employee_workflow.objects.filter(emp_id=user)
    if Employee_workflow.objects.filter(
        emp_id=user, pipeline_name="Zita Pipeline"
    ).exists():
        wk = Employee_workflow.objects.filter(
            emp_id=user, pipeline_name="Zita Pipeline"
        ).update(pipeline_name="Default Pipeline")

    if valid.exists():
        pass
    else:
        stages = [
            #  {"stage_order":"1","stage_name":"New Applicant","stage_color":"#581845","is_disabled":True},
            {
                "stage_order": 2,
                "stage_name": "Shortlisted",
                "stage_color": "#80C0D0",
                "is_disabled": True,
            },
            {
                "stage_order": 3,
                "stage_name": "Interviewed",
                "stage_color": "#F29111",
                "is_disabled": False,
            },
            {
                "stage_order": 4,
                "stage_name": "Hired",
                "stage_color": "#00BE4B",
                "is_disabled": True,
            },
            {
                "stage_order": 5,
                "stage_name": "Rejected",
                "stage_color": "#ED4857",
                "is_disabled": True,
            },
            {
                "stage_order": 6,
                "stage_name": "Screening",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            {
                "stage_order": 7,
                "stage_name": "Assessment",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            {
                "stage_order": 8,
                "stage_name": "Scheduling Interview",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            {
                "stage_order": 9,
                "stage_name": "Phone Interview",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            {
                "stage_order": 10,
                "stage_name": "On-site Interview",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            {
                "stage_order": 11,
                "stage_name": "HR Interview",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            {
                "stage_order": 12,
                "stage_name": "Final Interview",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            #  {"stage_order":13,"stage_name":"Scheduling Interview","stage_color":"#888888","is_disabled":False},
            {
                "stage_order": 13,
                "stage_name": "On-Hold",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            {
                "stage_order": 14,
                "stage_name": "On Boarding",
                "stage_color": "#888888",
                "is_disabled": False,
            },
            {
                "stage_order": 15,
                "stage_name": "Probation",
                "stage_color": "#888888",
                "is_disabled": False,
            },
        ]
        try:
            for index, i in enumerate(stages):
                Stages_suggestion.objects.create(
                    wk_id=user,
                    stage_name=i["stage_name"],
                    stage_color=i["stage_color"],
                    stage_order=i["stage_order"],
                    is_disabled=i["is_disabled"],
                )
        except:
            pass
        try:
            pipeline_name = "Default Pipeline"
            set_as_default = True

            data = Employee_workflow.objects.create(
                pipeline_name=pipeline_name,
                set_as_default=set_as_default,
                emp_id=user,
                is_active=True,
            )
            for index, i in enumerate(stages):
                if index <= 3:
                    Stages_Workflow.objects.create(
                        workflow_id_id=data.wk_id,
                        stage_name=i["stage_name"],
                        stage_color=i["stage_color"],
                        stage_order=i["stage_order"],
                        is_disabled=i["is_disabled"],
                    )
        except:
            pass


def existing_code(wk_id, user):
    check = Employee_workflow.objects.get(wk_id=wk_id).pipeline_name
    value = Stages_Workflow.objects.filter(workflow_id=wk_id)
    checkdata = Stages_suggestion.objects.filter(
        wk_id=user, stage_name="Interviewed"
    ).exists()
    if check == "Default Pipeline":
        if Stages_Workflow.objects.filter(
            workflow_id=wk_id, stage_name="Interviewed"
        ).exists():
            pass
        # elif Stages_Workflow.objects.filter(workflow_id=wk_id,stage_name__in = includes).exists() and len(value) == 3:
        elif checkdata == False:
            # if check:
            stages = [
                {
                    "stage_order": 3,
                    "stage_name": "Interviewed",
                    "stage_color": "#F29111",
                    "is_disabled": False,
                }
            ]
            for i in stages:
                Stages_Workflow.objects.filter(workflow_id=wk_id).create(
                    workflow_id=Employee_workflow.objects.get(wk_id=wk_id),
                    stage_order=i["stage_order"],
                    stage_name=i["stage_name"],
                    stage_color=i["stage_color"],
                    is_disabled=i["is_disabled"],
                )
        else:
            pass
    else:
        pass


def stage_suggestion(stages_name, emp_id):
    value = []
    for i in json.loads(stages_name):
        if Stages_suggestion.objects.filter(wk_id=emp_id).exists():
            if Stages_suggestion.objects.filter(
                wk_id=emp_id, stage_name=i["stage_name"]
            ).exists():
                pass
            else:
                Stages_suggestion.objects.create(
                    wk_id=emp_id,
                    stage_name=i["stage_name"],
                    stage_color=i["stage_color"],
                    stage_order=i["stage_order"],
                )
            value = Stages_suggestion.objects.filter(wk_id=emp_id).values()
    return value


def set_as_default(set_as_default, workflow_id, user):
    default = Employee_workflow.objects.filter(emp_id=user, set_as_default=True)
    value = Employee_workflow.objects.filter(wk_id=workflow_id)
    for i in value:
        for obj in default:
            if obj.wk_id != i.wk_id:
                obj.set_as_default = not obj.set_as_default
                i.set_as_default = not i.set_as_default
                obj.save()
                i.save()
    default = Employee_workflow.objects.filter(emp_id=user, default_all=True)
    value = Employee_workflow.objects.filter(wk_id=workflow_id)
    for i in value:
        for obj in default:
            if obj.wk_id != i.wk_id:
                obj.default_all = not obj.default_all
                i.default_all = not i.default_all
                obj.save()
                i.save()
    return None


def delete_suggestion(suggestion, user):
    if len(suggestion) > 0 and suggestion != None:
        shortlisted = Stages_suggestion.objects.get(
            wk_id=user, stage_name="Shortlisted"
        )
        interviewed = Stages_suggestion.objects.filter(
            wk_id=user, stage_name="Interviewed"
        ).update(stage_color="#888888")
        offered = Stages_suggestion.objects.get(wk_id=user, stage_name="Hired")
        rejected = Stages_suggestion.objects.get(wk_id=user, stage_name="Rejected")
        suggestion = json.loads(suggestion)
        suggestion += [
            shortlisted.suggestion_id,
            offered.suggestion_id,
            rejected.suggestion_id,
        ]

        delete_stages = (
            Stages_suggestion.objects.filter(wk_id=user)
            .exclude(suggestion_id__in=suggestion)
            .delete()
        )
    else:
        pass
    return None


def Default_create(data, user, jd_id):
    if not pipeline_view.objects.filter(jd_id=jd_id, emp_id=user).exists():
        stages = Stages_Workflow.objects.filter(workflow_id=data).values()
        for i in stages:
            pipeline_view.objects.create(
                jd_id=JD_form.objects.get(id=jd_id),
                emp_id=user,
                stage_order=i["stage_order"],
                stage_name=i["stage_name"],
                stage_color=i["stage_color"],
                workflow_id=Employee_workflow.objects.get(wk_id=data.wk_id),
            )
        default_save = Employee_workflow.objects.get(wk_id=data.wk_id)
        default_save.default_all = True
        default_save.save()
        set_as_default(None, default_save.wk_id, user)
    return None


def ChangingPipeline(user):
    if Employee_workflow.objects.filter(emp_id=user, default_all=True).exists():
        if Employee_workflow.objects.filter(emp_id=user, set_as_default=True).exists():
            setasDefault = Employee_workflow.objects.get(
                emp_id=user, set_as_default=True
            )
            newid = Employee_workflow.objects.get(emp_id=user, default_all=True).wk_id
            set_as_default(None, newid, user)
    return None


class Job_Pipeline_Stage(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = self.request.user
        if "pipeline_name" in self.request.POST:
            pipeline_name = self.request.POST["pipeline_name"].strip()
        else:
            pipeline_name = None
        if "stages" in self.request.POST:
            stages_name = self.request.POST["stages"]
        else:
            stages_name = None
        if "suggestion" in self.request.POST:
            suggestion = self.request.POST["suggestion"]
            delete_suggestion(suggestion, user)
        else:
            suggestion = None
        try:
            if "workflow_id" in self.request.POST:
                workflow_id = self.request.POST["workflow_id"].strip()
                # Rename
                if pipeline_name and workflow_id != None and stages_name == None:
                    do = Employee_workflow.objects.filter(wk_id=workflow_id).values(
                        "pipeline_name"
                    )
                    if "set_as_default" in self.request.POST:
                        default = self.request.POST["set_as_default"]
                        if default.lower() == "true":
                            set_as_default(default, workflow_id, user)
                    if do[0]["pipeline_name"] != "Default Pipeline":
                        if Employee_workflow.objects.filter(
                            emp_id=user, pipeline_name=pipeline_name
                        ).exists():
                            message = "Pipeline Title already exist!"
                            return Response({"message": message})
                        else:
                            Employee_workflow.objects.filter(wk_id=workflow_id).update(
                                pipeline_name=pipeline_name
                            )
                            message = "Renamed sucessfully"
                    else:
                        message = "cant be update Default pipeline"
                    return Response({"message": message})

                # update
                if (
                    stages_name != None
                    and pipeline_name != None
                    and workflow_id != None
                ):
                    for i in json.loads(stages_name):
                        Employee_workflow.objects.filter(wk_id=workflow_id).update(
                            pipeline_name=pipeline_name
                        )
                        if Stages_Workflow.objects.filter(
                            workflow_id=workflow_id, stage_name=i["stage_name"]
                        ).exists():
                            data = Stages_Workflow.objects.filter(
                                workflow_id=workflow_id, stage_name=i["stage_name"]
                            ).update(
                                stage_order=i["stage_order"],
                                stage_name=i["stage_name"],
                                stage_color=i["stage_color"],
                                is_disabled=i["is_disabled"],
                            )
                            create_suggestion = stage_suggestion(stages_name, user)

                        else:
                            wk_id = Employee_workflow.objects.get(wk_id=workflow_id)

                            data = Stages_Workflow.objects.filter(
                                workflow_id=workflow_id
                            ).create(
                                # stage_id = stage_id,
                                workflow_id=wk_id,
                                stage_order=i["stage_order"],
                                stage_name=i["stage_name"],
                                stage_color=i["stage_color"],
                            )
                            create_suggestion = stage_suggestion(stages_name, user)
                            continue
                    delete_stages = [i["stage_name"] for i in json.loads(stages_name)]
                    delete_stages = (
                        Stages_Workflow.objects.filter(workflow_id=workflow_id)
                        .exclude(stage_name__in=delete_stages)
                        .delete()
                    )
                    # delete_suggestion(suggestion,user)
                    message = "Updated succesfully"
                    return Response({"message": message})

            # Create
            else:
                if pipeline_name and stages_name:
                    exist = Employee_workflow.objects.filter(
                        emp_id=user, pipeline_name=pipeline_name
                    ).exists()
                    if exist:
                        message = "Same pipeline Name can't be created"
                        context = {"message": message}
                        return Response(context, status=400)
                    else:
                        data = Employee_workflow.objects.create(
                            emp_id=user, pipeline_name=pipeline_name
                        )
                        id = data.wk_id

                        for i in json.loads(stages_name):
                            Stages_Workflow.objects.create(
                                workflow_id_id=data.wk_id,
                                stage_name=i["stage_name"],
                                stage_color=i["stage_color"],
                                stage_order=i["stage_order"],
                                is_disabled=i["is_disabled"],
                            )
                            create_suggestion = stage_suggestion(stages_name, user)
                        defaults = self.request.POST.get("setdefault", None)
                        jd_id = self.request.POST.get("jd_id", 0)
                        if json.loads(defaults) == True and json.loads(jd_id) != 0:
                            create_default = Default_create(data, user, jd_id)
                        # suggest = Stages_suggestion.objects.filter(wk_id=user).latest("suggestion_id")
                        # delete_suggestion(suggestion,user)
                        message = "Pipeline Created sucessfully"
                        context = {"message": message}
                        return Response(context)

        except Exception as e:
            pass

    def get(self, request):
        user = self.request.user
        zita_default(user)
        # ChangingPipeline(user)
        admin_id, updated_by = admin_account(request)
        plan_id, plan = plan_checking(admin_id)

        if "wk_id" in self.request.GET:
            wk_id = self.request.GET["wk_id"].strip()
            if Employee_workflow.objects.filter(wk_id=wk_id).exists():
                # existing_code(wk_id,user)
                data = Employee_workflow.objects.filter(wk_id=wk_id).values()
                stages = Stages_Workflow.objects.filter(workflow_id=wk_id).values()
                created_on = Employee_workflow.objects.filter(wk_id=wk_id).values_list(
                    "created_on"
                )
                # suggestion = Stages_suggestion.objects.filter(created_at__lt = created_on,wk_id = user).values()[4:]
                stage_name = ["Shortlisted", "Hired", "Rejected"]
                suggestion = (
                    Stages_suggestion.objects.filter(wk_id=user)
                    .exclude(Q(stage_name__in=stage_name))
                    .values()
                )
                # stages = sorted(stages, key=lambda x: x['stage_order'])
                message = wk_id + "-" + "readed successfully"
                context = {
                    "messaage": message,
                    "data": data,
                    "stages": stages,
                    "suggestion": suggestion,
                    "user_plan": plan_id,
                    "plan": plan,
                }
                return Response(context)

        else:
            stages = [
                {
                    "stage_order": "2",
                    "stage_name": "Shortlisted",
                    "stage_color": "#80C0D0",
                    "is_disabled": True,
                },
                {
                    "stage_order": "3",
                    "stage_name": "Hired",
                    "stage_color": "#00BE4B",
                    "is_disabled": True,
                },
                {
                    "stage_order": "4",
                    "stage_name": "Rejected",
                    "stage_color": "#ED4857",
                    "is_disabled": True,
                },
            ]
            data = Employee_workflow.objects.filter(emp_id=user).values()
            stage_name = ["Shortlisted", "Hired", "Rejected"]
            suggestion = (
                Stages_suggestion.objects.filter(wk_id=user)
                .exclude(Q(stage_name__in=stage_name))
                .values()
            )
            message = "successfully readed"
            context = {
                "messaage": message,
                "data": data,
                "stages": stages,
                "suggestion": suggestion,
                "user_plan": plan_id,
                "plan": plan,
            }
            return Response(context)

    def delete(self, request):
        user = self.request.user
        if "workflow_id" in self.request.GET:
            workflow_id = self.request.GET["workflow_id"].strip()
            if "stages" in self.request.GET:
                stages = self.request.GET["stages"].strip()
            else:
                stages = None
            data = []
            if stages != None:
                if Employee_workflow.objects.filter(wk_id=workflow_id).exists():
                    if Stages_Workflow.objects.filter(workflow_id=workflow_id).exists():
                        for i in json.loads(stages):
                            Stages_Workflow.objects.filter(
                                workflow_id=workflow_id, stage_name=i["stage_name"]
                            ).delete()
                            message = "deleted successfully"

            else:
                value = Employee_workflow.objects.filter(
                    emp_id=user, wk_id=workflow_id
                ).values_list("set_as_default")
                associate = Employee_workflow.objects.filter(
                    emp_id=user, wk_id=workflow_id
                ).values_list("associate")
                if associate != True and value[0][0] != True:
                    delete = Employee_workflow.objects.filter(wk_id=workflow_id)
                    if delete.exists():
                        Employee_workflow.objects.filter(wk_id=workflow_id).delete()
                        message = "deleted successfully"
                else:
                    message = "Associate with more than one Job cant deleted "

        else:
            message = "workflow_id doesn't exist"
            data = []
        context = {"messaage": message, "data": data}
        return Response(context)
