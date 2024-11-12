import os
#111111111
# 1234545555555555
global BASE_DIR, matching_api_url, matching_auth_token, matching_keyword_filter
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
matching_api_url = "http://192.168.3.170:9999"  # example 'http://192.168.3.243,,http://192.168.3.170:9999/'

matching_auth_token = "Token 05db283c458e978adcbcdbd19015da4456acfb7c"  # example 'Token 05db283c458e978adcbcdbd19015da4456acfb7c'
matching_keyword_filter = (
    1  # type bool 0 or 1# do the keyword match with keyword filters
)
# rp_api_url ='http://192.168.3.231:81/parse-resume/'
# rp_api_url ='http://203.223.190.79:5666/parse-resume/'
rp_api_url = "http://192.168.3.238/parse-resume/"

from openai import OpenAI

openai_key = "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"
organization_key = "org-i1EAnwbqVcTX9b9O5yunvThu"
client = OpenAI(organization="org-i1EAnwbqVcTX9b9O5yunvThu", api_key=openai_key)

# core-signl integration token

# coresignal_token="eyJhbGciOiJFZERTQSIsImtpZCI6IjJiZTc5MzU4LWNlYTMtOGJmMS1kN2UzLTI5NjBhYzkzNTE1MiJ9.eyJhdWQiOiJzZW5zZTdhaSIsImV4cCI6MTczNTgwNzI0NiwiaWF0IjoxNzA0MjUwMjk0LCJpc3MiOiJodHRwczovL29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2Vuc2U3YWkiLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVhZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ.o5HQ135JSQ55mZGgeSBASKz9GAzsMPLhiBaloaWQ2OV-5KrdWKSCdVfwfUC58KJgIYu3Kr0VW4iv2ZqptOs1CA"
# coresignal_token="eyJhbGciOiJFZERTQSIsImtpZCI6IjhhYWRlYjc4LWE5MDItN2FiZC1iYzExLWVjNWYzOTEzZTEzYyJ9.eyJhdWQiOiJuYW5kaGFlbmdnIiwiZXhwIjoxNzM5MDE0Nzk1LCJpYXQiOjE3MDc0NTc4NDMsImlzcyI6Imh0dHBzOi8vb3BzLmNvcmVzaWduYWwuY29tOjgzMDAvdjEvaWRlbnRpdHkvb2lkYyIsIm5hbWVzcGFjZSI6InJvb3QiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJuYW5kaGFlbmdnIiwic3ViIjoiZmEwYzRjOWMtYzIxYy1mZmRmLWMwYjktNDhhZWQ1YWY5YzE2IiwidXNlcmluZm8iOnsic2NvcGVzIjoiY2RhcGkifX0.OFMWnHO3ENGGKt5R_cfc8gIWHs_MQXtFdPVAMGpXpVplwFkwyHlA1xpmDA7NBnLp7eXTLplQ1myPMej_OIWlAw"
# coresignal_token="eyJhbGciOiJFZERTQSIsImtpZCI6ImY4MzQ2ZDNkLWYzZTEtZmJkMS05MTdjLTU3ZWI1ODA2M2I2YyJ9.eyJhdWQiOiJmb2N1c2VkdW1hdGljcy5pbiIsImV4cCI6MTc0NDU3OTI4OSwiaWF0IjoxNzEzMDIyMzM3LCJpc3MiOiJodHRwczovL29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJlZmVycmVkX3VzZXJuYW1lIjoiZm9jdXNlZHVtYXRpY3MuaW4iLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVhZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ.EOoK4bxR_3V40e9Kyn-Ji8QamGdShMrlR7dnXbI_Ytuh1MXVCaIf2dDZ6OFsUW2pwxDaeA631HsgJ98OdbzMCQ"
# coresignal_token="eyJhbGciOiJFZERTQSIsImtpZCI6ImNiY2NlM2Y0LWY5NGQtYTI1MC02NTMyLTQ2YTcyOGE4ZjVkZiJ9.eyJhdWQiOiJuYW5kaGF0ZWNoLm9yZyIsImV4cCI6MTc0Mzk3NjA4NSwiaWF0IjoxNzEyNDE5MTMzLCJpc3MiOiJodHRwczovL29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJlZmVycmVkX3VzZXJuYW1lIjoibmFuZGhhdGVjaC5vcmciLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVhZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ.RsHZFlpeoegbu-wKVBSbWcd482DaRotodBOUSUPe8l9rsZRzwgJjGZXte7cz78v-SvKYJZAN-r-ZspRb5M2yBA"
# coresignal_token="eyJhbGciOiJFZERTQSIsImtpZCI6IjJiZTc5MzU4LWNlYTMtOGJmMS1kN2UzLTI5NjBhYzkzNTE1MiJ9.eyJhdWQiOiJzZW5zZTdhaSIsImV4cCI6MTczNTgwNzI0NiwiaWF0IjoxNzA0MjUwMjk0LCJpc3MiOiJodHRwczovL29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2Vuc2U3YWkiLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVhZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ.o5HQ135JSQ55mZGgeSBASKz9GAzsMPLhiBaloaWQ2OV-5KrdWKSCdVfwfUC58KJgIYu3Kr0VW4iv2ZqptOs1CA"
# coresignal_token="eyJhbGciOiJFZERTQSIsImtpZCI6IjcyNWM2M2I2LTcwMGUtNTQzZi0wNDg2LTgyYTFlZDMxNzBlZiJ9.eyJhdWQiOiJrb25ndSIsImV4cCI6MTczNTEyMDYwNywiaWF0IjoxNzAzNTYzNjU1LCJpc3MiOiJodHRwczovL29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJlZmVycmVkX3VzZXJuYW1lIjoia29uZ3UiLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVhZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ.YAfY7_T_ejlLz1YQFTSPB7K59XcxZTv5ZLJRTIR0E3bwTlPaFr41MlI13wwEZXLmFRtWiCpieJQviPzCyIUvBA"
coresignal_email_token = "av7nXpfremTKIrB2a4E2C2rxsXaCWraqNie96zq1"
# coresignal_token = "eyJhbGciOiJFZERTQSIsImtpZCI6IjE4MDk2YTQ3LThiY2YtYWZjMy01ZjVlLTE5MzllZDM2ODdlNyJ9.eyJhdWQiOiJmcmFuY2lzeGF2aWVyLmFjLmluIiwiZXhwIjoxNzQ0OTEyMzY3LCJpYXQiOjE3MTMzNTU0MTUsImlzcyI6Imh0dHBzOi8vb3BzLmNvcmVzaWduYWwuY29tOjgzMDAvdjEvaWRlbnRpdHkvb2lkYyIsIm5hbWVzcGFjZSI6InJvb3QiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJmcmFuY2lzeGF2aWVyLmFjLmluIiwic3ViIjoiZmEwYzRjOWMtYzIxYy1mZmRmLWMwYjktNDhhZWQ1YWY5YzE2IiwidXNlcmluZm8iOnsic2NvcGVzIjoiY2RhcGkifX0.kD2f8l8w_FpCuyaVbLXmRV0XxQIVrlESZiIYXOfugqPxI6tKJGUwzOHAOpU2nCG7nbYddNQwUCz4-SHI69gGBg"
# coresignal_token ="eyJhbGciOiJFZERTQSIsImtpZCI6IjJiZTc5MzU4LWNlYTMtOGJmMS1kN2UzLTI5NjBhYzkzNTE1MiJ9.eyJhdWQiOiJzZW5zZTdhaSIsImV4cCI6MTczNTgwNzI0NiwiaWF0IjoxNzA0MjUwMjk0LCJpc3MiOiJodHRwczovL29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2Vuc2U3YWkiLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVhZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ.o5HQ135JSQ55mZGgeSBASKz9GAzsMPLhiBaloaWQ2OV-5KrdWKSCdVfwfUC58KJgIYu3Kr0VW4iv2ZqptOs1CA"
# coresignal_token="eyJhbGciOiJFZERTQSIsImtpZCI6IjE4MDk2YTQ3LThiY2YtYWZjMy01ZjVlLTE5MzllZDM2ODdlNyJ9.eyJhdWQiOiJmcmFuY2lzeGF2aWVyLmFjLmluIiwiZXhwIjoxNzQ0OTEyMzY3LCJpYXQiOjE3MTMzNTU0MTUsImlzcyI6Imh0dHBzOi8vb3BzLmNvcmVzaWduYWwuY29tOjgzMDAvdjEvaWRlbnRpdHkvb2lkYyIsIm5hbWVzcGFjZSI6InJvb3QiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJmcmFuY2lzeGF2aWVyLmFjLmluIiwic3ViIjoiZmEwYzRjOWMtYzIxYy1mZmRmLWMwYjktNDhhZWQ1YWY5YzE2IiwidXNlcmluZm8iOnsic2NvcGVzIjoiY2RhcGkifX0.kD2f8l8w_FpCuyaVbLXmRV0XxQIVrlESZiIYXOfugqPxI6tKJGUwzOHAOpU2nCG7nbYddNQwUCz4-SHI69gGBg"
coresignal_token="eyJhbGciOiJFZERTQSIsImtpZCI6IjJiZTc5MzU4LWNlYTMtOGJmMS1kN2UzLTI5NjBhYzkzNTE1MiJ9.eyJhdWQiOiJzZW5zZTdhaSIsImV4cCI6MTczNTgwNzI0NiwiaWF0IjoxNzA0MjUwMjk0LCJpc3MiOiJodHRwczovL29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2Vuc2U3YWkiLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVhZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ.o5HQ135JSQ55mZGgeSBASKz9GAzsMPLhiBaloaWQ2OV-5KrdWKSCdVfwfUC58KJgIYu3Kr0VW4iv2ZqptOs1CA"
rp_api_auth_token = "Token 656652cd1afc42e3fa121946ecc0f5a7a4a10856"
matching_application_jd_endpoint = "/match/matchapplication-with-jd-id/"
# profile_pdf_url = 'http://stagapi.zita.ai/'
profile_pdf_url = "http://localhost:3000/"

profile_api_url = "http://192.168.3.231:83/predict-profiles/"
profile_api_auth_token = "Token 5db91a9eefb60d7e569091f803f82d28ef8e7c03"
classification_url = "http://192.168.3.231:83/dst-classification/"

# jdp_api_url = "http://192.168.3.231:82/parse-jd/"
# jdp_api_url = "http://203.223.190.79:5665/parse-jd/"
jdp_api_url = "http://192.168.3.236/parse-jd/"


jdp_api_auth_token = "Token b2192e4be38e0f364e999967b8d08c637b1596b6"
SECRET_KEY = "(@*s@ln^)ow%buadmu3#@lccz+4@$uy^ev%i+1cc9$sebyd3#i"

DEBUG = True

CORS_ORIGIN_ALLOW_ALL = True

rl_search_url = "https://api.resume-library.com/v1/candidate/backfill/search"
rl_job_posting_url = "https://api.resume-library.com/v2/job/create"
rl_job_removing_url = "https://api.resume-library.com/v2/job/delete/"


what_jobs_posting_url = (
    "https://api.whatjobs.com/api/v1/ats/b8b77f3286c2819f6971c9bdeeb2b9f8/json"
)
what_jobs_token = "b8b77f3286c2819f6971c9bdeeb2b9f8"


rl_username = "975486"
rl_password = "a4afe1a58d53"

ALLOWED_HOSTS = ["*"]

# CLIENT_URL = "/manage-user"
# CLIENT_URL = "http://192.168.3.251:3000"
CLIENT_URL = "http://localhost:3000"
# CLIENT_URL = "https://staging.zita.ai"
# CLIENT_URL = "https://www.app.zita.ai"
# Application definition


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "main.apps.MainConfig",
    "job_pool.apps.JobPoolConfig",
    "notifications",
    "bootstrap_modal_forms",
    "application",
    "widget_tweaks",
    "jobs",
    "login",
    "payment",
    "bootstrap_datepicker_plus",
    "django_filters",
    "crispy_forms",
    "bulk_upload",
    "tempus_dominus",
    "calendarapp",
    "reports",
    "users",
    "rest_framework",
    "knox",
    "accounts",
    "permission",
    "role",
    "corsheaders",
    "jobspipeline",
    "schedule_event",
    "chatbot",
]
CRISPY_TEMPLATE_PACK = "bootstrap4"
# User_management
REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": ("knox.auth.TokenAuthentication",)}


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_session_timeout.middleware.SessionTimeoutMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# CORS_ALLOWED_ORIGINS = [
#     "https://dev185.d36oiy1kqukg1u.amplifyapp.com/"
# ]
CORS_ORIGIN_WHITELIST = [
    # "https://dev185.d36oiy1kqukg1u.amplifyapp.com "
    "http://localhost:3000"
]
# CACHE_MULTISITE_ALIAS = 'multisite'
ROOT_URLCONF = "zita.urls"

SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_SECONDS = 3600  # 1 hour
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "zita.wsgi.application"




# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'z_match_new',
#         'USER': 'admin',
#         'PASSWORD': 'Secur1ty@!@#',
#         'HOST': '103.169.245.2',
#         'PORT': '25252',
#     }
# }


#  <-----Local Database --->

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "z_match_new",
        "USER": "admin",
        "PASSWORD": "Secur1ty@!@#",
        "HOST": "192.168.3.235",
        "PORT": "3306",
    }
}

#  <-----Staging Database --->

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'staging',
#         'USER': 'admin',
#         'PASSWORD': 'S3cur1ty@!@#',
#         'HOST': '18.191.124.165',
#         'PORT': '3306',
#     }
# }

#  <-----Zita Database --->

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'zita_production',
#         'USER': 'admin',
#         'PASSWORD': 'S3cur1ty@!@#',
#         'HOST': '18.191.124.165',
#         'PORT': '3306',
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "login.auth_backend.EmailBackend",
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1


LOGIN_REDIRECT_URL = "user_details"
LOGOUT_REDIRECT_URL = "login"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"
STATICFILES_DIR = [os.path.join(BASE_DIR, "static")]
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


EMAIL_TO = "support@zita.ai"
EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.office365.com"
EMAIL_HOST_USER = "support@zita.ai"
DEFAULT_FROM_EMAIL = "support@zita.ai"
EMAIL_FROM = "support@zita.ai"
EMAIL_HOST_PASSWORD = "Grad@!#%&("
EMAIL_PORT = 587


#####  Education Category list
dip = [
    "diploma",
    "diplomacy",
    "dip.",
    "dip",
    "d.i.p",
    "d.i.p.",
    "dip.soc.sc.",
    "dip.soc.sc",
    "dip.ed",
    "dip.ed.",
]
ug = [
    "bachelors",
    "bachelor",
    "bs",
    "ba",
    "graduate",
    "btech",
    "b.tech/b.e",
    "b-tech",
    "undergraduate",
    "b.s.c.",
    "bsc",
    "b.s.c",
    "b.sc.",
    "bscs",
    "bsce",
    "graduation",
    "bca",
    "arts",
    "bca",
    "bcom",
    "graduated",
    "bac",
    "ug",
    "undergrad",
    "b.s.",
    "be",
    "b.e",
    "b.tech",
    "Bachelor's",
]
pg = [
    "masters",
    "ms",
    "master",
    "mba",
    "mca",
    "msc",
    "mscs",
    "mtech",
    "mcs",
    "m.sc.",
    "m.s.c",
    "m.s.c.",
    "pg",
    "postgraduate",
    "majors",
    "pgdm",
    "postgrad",
]
phd = ["phd", "doctorate", "Doctor"]


with open("zita/.env", "r") as file:
    for line in file:
        if "STRIPE_PUBLISHABLE_KEY" in line:
            stripe_publishable_key = line.split("=")[1].strip().strip("'")
        elif "STRIPE_SECRET_KEY" in line:
            stripe_secret_key = line.split("=")[1].strip().strip("'")

STRIPE_PUBLISHABLE_KEY = stripe_publishable_key
STRIPE_SECRET_KEY = stripe_secret_key


basic_month = "price_1JkXgQJK7wwywY1K8B2fXhQt"
basic_year = "price_1JkXh3JK7wwywY1KfFE5qZL7"
pro_month = "price_1JkXioJK7wwywY1KrEJnPqHV"
pro_year = "price_1JkXjKJK7wwywY1KqAZVd7aX"
contact_credit = "price_1Jnbf4JK7wwywY1KIXKaxhRi"


# basic_month='price_1JpQ5gJK7wwywY1Kou5IN2wl'
# basic_year='price_1JpQ76JK7wwywY1K3bh9VLTg'
# pro_month='price_1JpQ7qJK7wwywY1KdoyvS6x3'
# pro_year='price_1JpQKNJK7wwywY1KeyzJ23ur'
# contact_credit = 'price_1JpQScJK7wwywY1Kk7JbyiY2'


# indexing URL
# index_url = "https://app.zita.ai/v5_8/IndexService?WSDL"
# match_url = "https://app.zita.ai/v5_8/MatchService?WSDL"
# gap_url   = "https://app.zita.ai/v5_8/GapService?WSDL"

# localhost
index_url = "https://localhost:3000/v5_8/IndexService?WSDL"
match_url = "https://localhost:3000/v5_8/MatchService?WSDL"
gap_url = "https://localhost:3000/v5_8/GapService?WSDL"

#### Standalone API Intergration URL
standalone_url = 'https://uotxnvwte6.execute-api.us-east-1.amazonaws.com/prod'
standalone_apikey = 'XRBsq43D6g608kqPE9s0Z8tgNnc8vlMn3wrpIZRh'

# index_url = "http://192.168.3.251:8080/v5_8/IndexService?WSDL"
# match_url = "http://192.168.3.251:8080/v5_8/MatchService?WSDL"
# gap_url = "http://192.168.3.251:8080/v5_8/GapService?WSDL"

xmp_headers = {"content-type": "application/soap+xml"}
