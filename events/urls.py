from django.urls import path
from . import views, dashboard_api

urlpatterns = [
    path('create/', views.create_event, name='create_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('available/', views.available_events, name='available_events'),
    path('register/<str:event_id>/', views.register_event, name='register_event'),
    path('assessments/', views.assessment_list, name='assessment_list'),
    path('student-assessments/', views.student_assessment_list, name='student_assessment_list'),
    path('create-assessment/', views.create_assessment, name='create_assessment'),
    path('submit-assessment/<str:assessment_id>/', views.submit_assessment, name='submit_assessment'),
    path('assessment-result/<str:submission_id>/', views.assessment_result, name='assessment_result'),
    path('grade-assessment/<str:submission_id>/', views.grade_assessment, name='grade_assessment'),
    path('certificates/', views.certificates, name='certificates'),
    path('approvals/', views.event_approval_list, name='event_approval_list'),
    path('analytics/', views.analytics, name='analytics'),
    path('event/<str:event_id>/', views.event_detail, name='event_detail'),
    path('event/<str:event_id>/edit/', views.create_event, name='edit_event'),
    path('scheduler/', views.event_scheduler, name='event_scheduler'),
    path('delete-schedule/<str:schedule_id>/', views.delete_schedule, name='delete_schedule'),

    path('assessment/<str:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    path('assessment/<str:assessment_id>/submissions/', views.assessment_submissions, name='assessment_submissions'),
    path('assessment/<str:assessment_id>/edit/', views.edit_assessment, name='edit_assessment'),
    path('assessment/<str:assessment_id>/delete/', views.delete_assessment, name='delete_assessment'),

    path('hod/pending-events/', views.hod_pending_events, name='hod_pending_events'),
    path('hod/approved-events/', views.hod_approved_events, name='hod_approved_events'),
    path('hod/rejected-events/', views.hod_rejected_events, name='hod_rejected_events'),

    path('principal/pending-events/', views.principal_pending_events, name='principal_pending_events'),
    path('principal/approved-events/', views.principal_approved_events, name='principal_approved_events'),
    path('principal/rejected-events/', views.principal_rejected_events, name='principal_rejected_events'),

    path('api/event/<str:event_id>/', views.event_detail_api, name='event_detail_api'),
    path('api/event/<str:event_id>/approve/', views.approve_event, name='approve_event'),
    path('api/event/<str:event_id>/reject/', views.reject_event, name='reject_event'),
    path('api/event/<str:event_id>/analytics/', views.get_event_analytics, name='event_analytics'),
    path('api/event/<str:event_id>/participants/', views.event_participants, name='event_participants'),
    path('api/event/<str:event_id>/generate-certificates/', views.generate_certificates, name='generate_certificates'),

    path('api/dashboard/coordinator/', dashboard_api.get_coordinator_dashboard_data, name='coordinator_dashboard_api'),
    path('api/dashboard/hod/', dashboard_api.get_hod_dashboard_data, name='hod_dashboard_api'),
    path('api/dashboard/principal/', dashboard_api.get_principal_dashboard_data, name='principal_dashboard_api'),
    path('api/dashboard/student/', dashboard_api.get_student_dashboard_data, name='student_dashboard_api'),

    path('feedback/<str:event_id>/', views.submit_feedback, name='submit_feedback'),
    path('feedback/report/<str:event_id>/', views.event_feedback_report, name='event_feedback_report'),

    path('upload-material/', views.upload_material, name='upload_material'),
    path('view-materials/', views.view_materials, name='view_materials'),

    path('online-events/', views.online_events, name='online_events'),
]
