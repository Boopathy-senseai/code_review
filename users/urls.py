from django.urls import path, include
from .api import (
    CompanyInvite,
    DepartmentAPI,
    UserCheckToken,
    UserConfirmation,
    UserResendMail,
)
from knox import views as knox_view
from users import api

urlpatterns = [
    # path('api/users', UserAPI.as_view()),
    # path('api/users/<int:pk>', UserDeleteAPI.as_view()),
    path("api/users", api.UserList.as_view()),
    path("api/users/<int:pk>/", api.UserDetail.as_view()),
    path("api/user-activity-list/<int:pk>/", api.UserActivityList.as_view()),
    path("api/user-activity-count/<int:pk>/", api.UserActivityCount.as_view()),
    path("api/user-update-status/<int:pk>/", api.UserUpdateStatus.as_view()),
    path("api/users/resend-mail", UserResendMail.as_view()),
    path("api/users/confirmation", UserConfirmation.as_view()),
    path("api/users/check-token", UserCheckToken.as_view()),
    path("api/users/company-invites", CompanyInvite.as_view()),
    path("api/departments", DepartmentAPI.as_view()),
]
