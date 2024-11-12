from django.conf.urls import url, include
from django.urls import path, include
from django.contrib.auth import views as auth_views
from jobs import views
from jobs import api
from django.views.static import serve

from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

# from django.views.generic import TemplateView

urlpatterns = [
    path("xml_test", views.xml_test, name="xml_test"),
    path("jobs/list", views.create_job_listing, name="jobs_main"),
    path("invoice", views.invoice, name="invoice"),
    path("plan/", views.career_page_plan, name="career_page_plan"),
    path("dashboard_message/", views.dashboard_message, name="dashboard_message"),
    path(
        "account/settings/user-profile/",
        views.user_profile_setting,
        name="user_profile_setting",
    ),
    # path('url_verification/', views.url_verification, name='url_verification'),
    path("candidate_view/", views.candidate_view, name="candidate_view"),
    path("unlock_candidates/", views.unlock_candidates, name="unlock_candidates"),
    url(r"^mydatabase/", views.my_database, name="my_database"),
    url(r"^my_database_bulk/", views.my_database_bulk, name="my_database_bulk"),
    url(r"^my_database_ajax/", views.my_database_ajax, name="my_database_ajax"),
    url(
        r"^account/company/", views.company_detail_signup, name="company_detail_signup"
    ),
    url(r"^setting_page/", views.setting_page_signup, name="setting_page_signup"),
    path("account/settings/company/", views.company_detail, name="company_detail"),
    path("account/settings/career-page/", views.setting_page, name="setting_page"),
    path("jobs/select/", views.select_ds_or_non_ds, name="select_ds_or_non_ds"),
    path(
        "applicant_genarate_json/<int:pk>",
        views.applicant_genarate_json,
        name="applicant_genarate_json",
    ),
    path("applicant_inflow/<int:pk>", views.applicant_inflow, name="applicant_inflow"),
    path("job_view_count/<int:pk>", views.job_view_count_fun, name="job_view_count"),
    path("generate_jd_json/<int:pk>", views.generate_jd_json, name="generate_jd_json"),
    path(
        "generate_candidate_json/<int:pk>",
        views.generate_candidate_json,
        name="generate_candidate_json",
    ),
    path(
        "external_job_posting/<int:pk>",
        views.external_job_posting,
        name="external_job_posting",
    ),
    path(
        "show_all_match/<int:jd>/<int:pk>", views.show_all_match, name="show_all_match"
    ),
    path(
        "favourite_post/<int:jd>/<int:pk>", views.favourite_post, name="favourite_post"
    ),
    path(
        "remove_external_job_posting/<int:pk>",
        views.remove_external_job_posting,
        name="remove_external_job_posting",
    ),
    path(
        "jobs/draft-questionnaire/<int:pk>", views.questionnaire, name="questionnaire"
    ),
    path("<str:url>/job-view/<int:pk>", views.career_job_view, name="career_job_view"),
    path("cal_event/<int:can_id>", views.cal_event, name="cal_event"),
    path(
        "generate_invoice_test/<int:pk>",
        views.generate_invoice_test,
        name="generate_invoice_test",
    ),
    path("generate_invoice/<int:pk>", views.generate_invoice, name="generate_invoice"),
    path("mydashboard/", views.dashboard, name="dashboard"),
    path("download_jd/<int:pk>", views.download_jd, name="download_jd"),
    path(
        "create_job_listing_ajax",
        views.create_job_listing_ajax,
        name="create_job_listing_ajax",
    ),
    path("jobs/create/", views.post_job, name="post_job"),
    url(
        r"^plan/(?P<uidb64>[0-9A-Za-z_\-]+)/$",
        views.job_posting_plan_page,
        name="job_posting_plan_page",
    ),
    path("validate", views.validate_job_id, name="validate_job_id"),
    path("delete_profile", views.delete_profile, name="delete_profile"),
    path("jd_profile/<int:pk>", views.profile, name="profile"),
    path("jd_profile/", views.profile, name="profile"),
    path("applicant_qus/<int:pk>", views.applicant_qus, name="applicant_qus"),
    path("user-management/", views.user_management, name="user_management"),
    path("bulk_action/", views.bulk_action, name="bulk_action"),
    path(
        "dashboard_job_metrics/",
        views.dashboard_job_metrics,
        name="dashboard_job_metrics",
    ),
    path("parsing/<int:pk>", views.parsing, name="parsing"),
    path("candidate_list/<str:pk>", views.candidate_list, name="candidate_list"),
    path("parsing/", views.parsing, name="parsing"),
    path(
        "jobs/<int:jd_id>/applicant/<int:can_id>/",
        views.applicant_profile,
        name="applicant_profile",
    ),
    path("jobs/applicant/<int:can_id>/", views.applicant_profile, name="appli_profile"),
    path(
        "jobs/<int:jd_id>/candidate/<int:can_id>/",
        views.candidate_profile,
        name="candidate_profile",
    ),
    path("jobs/candidate/<int:can_id>/", views.candidate_profile, name="candi_profile"),
    path("parsed_text/", views.parsed_text, name="parsed_text"),
    url(r"^recom_cand/(?P<pk>\d+)/$", views.recom_cand, name="recom_cand"),
    url(r"^hiring_process/$", views.hiring_process, name="hiring_process"),
    url(
        r"^ajax_hiring_process/(?P<pk>\d+)/(?P<string>\d+)/$",
        views.ajax_hiring_process,
        name="ajax_hiring_process",
    ),
    url(r"^applicants/(?P<pk>\d+)/$", views.applicants_list, name="applicants"),
    url(r"^applicant_ajax/(?P<pk>\d+)/$", views.applicant_ajax, name="applicant_ajax"),
    path("sorting/<int:pk>/<int:id>", views.sorting, name="shorting"),
    url(r"^jobs/(?P<pk>\d+)/applicants/$", views.applicant, name="applicant"),
    url(r"^jobs/(?P<pk>\d+)/zita-match/$", views.zita_match, name="zita_match"),
    url(
        r"^zita_match_ajax/(?P<pk>\d+)/$", views.zita_match_ajax, name="zita_match_ajax"
    ),
    url(r"^contact_zita/(?P<pk>\d+)/$", views.contact_zita, name="contact_zita"),
    path("sorting/<int:pk>/<int:id>/<int:status_id>", views.sorting, name="shorting"),
    path("talent-sourcing/", views.zita_talent_pool, name="zita_talent_pool"),
    path(
        "zita_talent_pool/",
        views.zita_talent_pool_ajax.as_view(),
        name="zita_talent_pool_ajax",
    ),
    path("analytics", views.analytics, name="analytics"),
    path(
        "generate_candidate_load_all",
        views.generate_candidate_load_all,
        name="generate_candidate_load_all",
    ),
    path(
        "generate_jd_json_all", views.generate_jd_json_all, name="generate_jd_json_all"
    ),
    path("jobs/preview/", views.Preview, name="preview"),
    path("jobs/preview/<int:pk>", views.Preview, name="preview_pk"),
    path("feedback_form/<int:pk>", views.feedback_form, name="feedback_form"),
    url(
        r"^jobs/update/(?P<pk>\d+)/",
        views.update_or_duplicate_jd,
        name="update_or_duplicate_jd",
    ),
    path("missing_skills", views.missing_skills, name="missing_skills"),
    path("missing_skills/<int:pk>", views.missing_skills, name="missing_skills"),
    path("jobs/description/<int:pk>", views.pre_jdView, name="pre_jd"),
    path("jobs/description/", views.pre_jdView, name="pre_jd"),
    path("jd_form_to_jd_list/", views.jd_form_to_jd_list, name="jd_form_to_jd_list"),
    url(r"^jobs/view/(?P<pk>\d+)/", views.jd_view, name="jd_view"),
    path(
        "render/download_interested/<int:pk>",
        views.download_interested.as_view(),
        name="download_interested",
    ),
    path(
        "render/download_interested_search/",
        views.download_interested_search.as_view(),
        name="download_interested_search",
    ),
    path(
        "render/download_invoices/",
        views.download_invoices.as_view(),
        name="download_invoices",
    ),
    path(
        "render/download_shortlist/<int:pk>",
        views.download_shortlist.as_view(),
        name="download_shortlist",
    ),
    url(r"^generate/(?P<pk>\d+)/$", views.generate_pdf, name="generate_pdf"),
    url(r"^test/(?P<pk>\d+)/$", views.test, name="test"),
    path("candidate_notes/<int:pk>", views.candidate_notes, name="candidate_notes"),
    url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    url(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    url(r"^download/(?P<path>.*)$", serve, {"document root": settings.MEDIA_ROOT}),
    ############ API URLs
    # API  for talent sourcing
    path(
        "api/zita_talent_sourcing_api/",
        api.zita_talent_pool_api.as_view(),
        name="zita_talent_sourcing_api",
    ),
    path(
        "api/zita_talent_sourcing_search_api/",
        api.zita_talent_pool_search_api.as_view(),
        name="zita_talent_sourcing_search_api",
    ),
    path(
        "api/bulk_action_sourcing_api/",
        api.bulk_action_api.as_view(),
        name="bulk_action_sourcing_api",
    ),
    path(
        "api/download_bulk_export/",
        api.download_bulk_export.as_view(),
        name="download_bulk_export",
    ),
    path(
        "api/candidate_view_sourcing_api/",
        api.candidate_view_api,
        name="candidate_view_sourcing_api",
    ),
    path(
        "api/unlock_candidates_api/",
        api.unlock_candidates_api.as_view(),
        name="unlock_candidates_api",
    ),
    path(
        "api/parsed_text_sourcing_api/",
        api.parsed_text_api,
        name="parsed_text_sourcing_api",
    ),
    path("api/candidate_view_api/", api.candidate_view_api, name="candidate_view_api"),
    # Applicants and candidates profile APIs
    path(
        "api/applicants_profile_api",
        api.applicants_profile_api.as_view(),
        name="applicants_profile_api",
    ),
    path("api/messages", api.MessagesAPIView.as_view(), name="Messages"),
    path("api/messages_data", api.messages_data.as_view(), name="messages_data"),
    path(
        "api/messages_templates",
        api.Messages_templates.as_view(),
        name="messages_templates",
    ),
    path(
        "api/applicants_status",
        api.applicant_status.as_view(),
        name="applicants_status",
    ),
    path(
        "api/interview_scorecard", api.scorecard.as_view(), name="interview_scorecard"
    ),
    path(
        "api/message_non_applicants",
        api.message_non_applicants.as_view(),
        name="message_non_applicants",
    ),
    path("api/calender_event", api.calender_event.as_view(), name="calender_event"),
    # API for whatjobs external job posting  APIs
    path("api/what_jobs_posting/", api.what_jobs_posting, name="what_jobs_posting"),
    path("api/google_job_posting/", api.google_job_posting, name="google_job_posting"),
    path(
        "api/remove_what_jobs_posting/",
        api.remove_what_jobs_posting,
        name="remove_what_jobs_posting",
    ),
    # Applicant pipline  APIs
    path(
        "api/applicants_pipline/<int:jd_id>",
        api.applicants_pipline.as_view(),
        name="applicants_pipline",
    ),
    path(
        "api/update_status/<int:jd_id>",
        api.update_status.as_view(),
        name="update_status",
    ),
    path(
        "api/applicant_data/<int:jd_id>",
        api.applicants_data.as_view(),
        name="applicants_data",
    ),
    # Zita Match APIs
    path("api/zita_match", api.zita_match.as_view(), name="zita_match"),
    path("api/zita_match_data", api.zita_match_data.as_view(), name="zita_match_data"),
    # My database APIs
    path("api/my_database", api.my_database.as_view(), name="my_database_api"),
    path(
        "api/my_database_data", api.my_database_data.as_view(), name="my_database_data"
    ),
    # Accounts setting APIs
    path(
        "api/company_details", api.company_detail.as_view(), name="company_details_api"
    ),
    path("api/password_change", api.Password_Change.as_view(), name="password_change"),
    path("api/user_profile", api.user_profile.as_view(), name="user_profile"),
    path(
        "api/build_career_page",
        api.build_career_page.as_view(),
        name="build_career_page",
    ),
    path(
        "api/url_verification", api.url_verification.as_view(), name="url_verification"
    ),
    path("api/career_page/<str:url>", api.career_page.as_view(), name="career_page"),
    # Common APIs
    path("api/candidate_notes", api.candidate_notes.as_view(), name="candidate_notes"),
    path(
        "api/mention_notification_candidate_notes",
        api.mention_notification_candidate_notes.as_view(),
        name="mention_notification_candidate_notes",
    ),
    path(
        "api/matching_analysis",
        api.matching_analysis.as_view(),
        name="matching_analysis",
    ),
    path("api/show_all_match", api.show_all_match.as_view(), name="show_all_match_api"),
    path("api/invite_to_apply", api.invite_to_apply.as_view(), name="invite_to_apply"),
    path("api/bulk_download", api.bulk_download.as_view(), name="bulk_download"),
    path("api/favourite", api.favourite.as_view(), name="favourite"),
    path("api/company_logo", api.LogoUpdateAPIView.as_view(), name="company_logo"),
    # Jd From
    path(
        "api/select_ds_or_non_ds",
        api.select_ds_or_non_ds.as_view(),
        name="select_ds_or_non_ds_api",
    ),
    path("api/create_jd", api.create_jd.as_view(), name="create_jd_api"),
    path("api/jd_templates", api.JD_templates.as_view(), name="JD_templates"),
    path("api/edit_jd/<int:pk>", api.edit_jd.as_view(), name="edit_jd_api"),
    path("api/duplicate/<int:pk>", api.duplicate.as_view(), name="duplicate_api"),
    path("api/jd_profile/<int:pk>", api.jd_profile.as_view(), name="jd_profile"),
    path(
        "api/missing_skills/<int:pk>",
        api.missing_skills.as_view(),
        name="missing_skills_api",
    ),
    path("api/jd_parser", api.jd_parser.as_view(), name="jd_parser"),
    path(
        "api/questionnaire_templates",
        api.questionnaire_templates.as_view(),
        name="questionnaire_templates",
    ),
    path(
        "api/questionnaire_for_jd/<int:pk>",
        api.questionnaire_for_jd.as_view(),
        name="questionnaire_for_jd",
    ),
    path(
        "api/questionnaire_save/<int:pk>",
        api.questionnaire_save.as_view(),
        name="questionnaire_save",
    ),
    path("api/jd_preview/<int:pk>", api.jd_preview.as_view(), name="jd_preview_api"),
    path("api/post_jd/<int:pk>", api.post_jd.as_view(), name="post_jd_api"),
    path(
        "api/job_post_confirmation/<int:pk>",
        api.job_post_confirmation.as_view(),
        name="job_post_confirmation",
    ),
    path("api/dst_or_not/<int:pk>", api.dst_or_not.as_view(), name="dst_or_not"),
    path("api/validate_job_id/", api.validate_job_id.as_view(), name="validate_job_id"),
    path(
        "api/external_job_post",
        api.external_job_post.as_view(),
        name="external_job_post",
    ),
    #####################
    path("api/email_label", api.email_label.as_view(), name="email_label"),
    path(
        "api/matching_algorithm",
        api.matching_algorithm.as_view(),
        name="matching_algorithm",
    ),
    path("api/match_alg_api", api.match_alg_api.as_view(), name="match_alg_api"),
    path(
        "api/job_matching_api", api.job_matching_api.as_view(), name="job_matching_api"
    ),
    path("api/job_changes_api", api.job_changes_api.as_view(), name="job_changes_api"),
    path(
        "api/pipeline_status_api",
        api.pipeline_status_api.as_view(),
        name="pipeline_status_api",
    ),
    #####################
    # JD_view API
    path("api/jd_view/<int:pk>", api.jd_view.as_view(), name="jd_view_api"),
    path("api/inactive_jd/<int:pk>", api.inactive_jd.as_view(), name="inactive_jd"),
    path("api/download_jd", api.download_jd.as_view(), name="download_jd"),
    path("api/my_job_posting", api.my_job_posting.as_view(), name="my_job_posting"),
    path(
        "api/my_job_posting_data",
        api.my_job_posting_data.as_view(),
        name="my_job_posting_data",
    ),
    # path('api/myjobpostingdata',api.MyJobPostingData.as_view(),name='MyJobPostingData'),
    path("api/dashboard_emp", api.dashboard.as_view(), name="dashboard_api_emp"),
    path(
        "api/dashboard_job_metrics",
        api.dashboard_job_metrics.as_view(),
        name="dashboard_job_metrics_api",
    ),
    path(
        "api/dashboard_message",
        api.dashboard_message.as_view(),
        name="dashboard_message_api",
    ),
    path(
        "api/dashboard_calender",
        api.dashboard_calender.as_view(),
        name="dashboard_calender",
    ),
    path(
        "api/candi_invite_status/<int:pk>",
        api.candi_invite_status.as_view(),
        name="candi_invite_status",
    ),
    path(
        "api/career_job_view/<int:pk>",
        api.career_job_view_api.as_view(),
        name="career_job_view_api",
    ),
    path(
        "api/download_profile", api.download_profile.as_view(), name="download_profile"
    ),
    path(
        "api/email_preference",
        api.email_preference_api.as_view(),
        name="email_preference",
    ),
    path("api/notification", api.notification.as_view(), name="notification"),
    path("api/country", api.country.as_view(), name="country"),
    path(
        "api/job_view_count_fun/<int:pk>",
        api.job_view_count_fun.as_view(),
        name="job_view_countun",
    ),
    path(
        "api/kanban_pipeline_view",
        api.kanban_pipeline_view.as_view(),
        name="kanban_Pipeline_view",
    ),
    path("api/kanban_updation", api.kanban_updation.as_view(), name="Kanban_updation"),
    # jd_industry_type
    path('api/jd_industry_type',api.jd_industry_type.as_view(),name="jd_industry_type"),
    path('api/interview_role',api.roles.as_view(),name="interview_role"),
    

    #  praticed to test the functions 
    path('api/testapi',api.JD_Conversion.as_view(),name='testapi'),
    path('api/testapi2',api.RESUME_Conversion.as_view(),name='testapi2'),

#Match_db_api:
    path('api/match_canid_jdid',api.match_canid_jdid.as_view(),name="match_canid_jdid"),
    path('api/match_canid',api.match_canid.as_view(),name="match_canid"),
    path('api/match_jdid',api.match_jdid.as_view(),name="match_jdid"),
    path('api/jd_creation_ai',api.jd_creation_ai.as_view(),name="jd_creation_ai"),

#jd_match_skills
    path('api/weightage_matching',api.weightage_matching.as_view(),name='weightage_matching'),
    path('api/weightage_score',api.weightage_score.as_view(),name='weightage_score'),

# Matching analysis
    path('api/get_comparative_analysis', api.get_comparative_analysis.as_view(), name="get_comparative_analysis"),
    path('api/subscription_scheduler_api', api.subscription_scheduler_api.as_view(), name='job_to_candidate'),
    path('api/candidate_to_job', api.candidate_to_job.as_view(), name='candidate_to_job'),
    path('api/candidate_searching_api', api.candidate_searching_api.as_view(), name='candidate_searching_api'),
    path('api/download_analysis_csv', api.download_analysis_csv.as_view(), name='download_analysis_csv'),
    path('api/subs_details_api', api.subs_details_api.as_view(), name='subs_details_api'),
    path('api/plan_details', api.plan_details.as_view(), name='plan_details'),
    path('api/matching_process',api.matching_process.as_view(), name='matching_process'),
#profile summary
    path('api/profile_summary',api.profile_summary_api.as_view(), name='profile_summary'),
    path('api/email_automation',api.Email_automation.as_view(), name='email_automation'),

#tour path
    path('api/tour_data',api.tour_data_api.as_view(), name='tour_data'),
    #core_signla_linkedin_integration
    path('api/coresignal_integration',api.Coresignalintegration.as_view(), name='coresignal_integration'),
    
    path('api/linkedin_unlocked_candidate',api.linkedin_unlocked_candidate.as_view(), name='linkedin_unlocked_candidate'),
    path('api/linkedin__candidate',api.linkedin__candidate.as_view(), name='linkedin_unlocked_candidate'),

    path('api/linkedin_integration',api.linkedin_integration.as_view(), name='linkedin_integration'),
    path('api/linkedin_message',api.linkedin_message.as_view(), name='linkedin_message'),

    path('api/sourced_candidates_api',api.sourced_candidates_api.as_view(), name='sourced_candidates'),

    path("api/dr_job_integration",api.Dr_Job_Integration.as_view(),name="Dr_Job_Integration"),
    path("api/zita_api_service_api",api.ZitaAPIService.as_view(),name="zita_api_service_api"),
    path('api/job_board',api.job_board_integration.as_view(),name="job_board_integration")
    
    #  path('job/<int:ats_job_id>/apply', api.dr_job_board_apply.as_v   iew(), name='dr_job_board_apply'),
    # path(
    #     # "job/<int:ats_job_id>/apply",api.dr_job_board_apply.as_view(),name="dr_job_board_apply"
        
    # )
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



