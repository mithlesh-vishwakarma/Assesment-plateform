from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health_check,
    AssessmentViewSet,
    auth_register,
    auth_login,
    auth_logout,
    auth_me,
    candidate_campaigns,
    candidate_assessment_status,
    candidate_start_stage,
    candidate_stage_questions,
    candidate_autosave_draft,
    candidate_finalize_submission,
    candidate_run_sample_code,
    candidate_record_integrity_event,
    reviewer_assigned_submissions,
    reviewer_get_evaluation,
    reviewer_submit_scores,
    AdminCampaignViewSet,
    AdminStageViewSet,
    AdminQuestionViewSet,
    AdminChallengeViewSet,
    AdminTestCaseViewSet,
    AdminCandidateSelectionViewSet,
    AdminAuditLogViewSet,
    admin_campaign_summary,
    admin_export_csv,
    admin_assign_reviewer,
    candidate_stages,
    admin_candidates_list,
    admin_overview_metrics,
)

router = DefaultRouter()
# Preserved legacy endpoint for frontend backwards-compatibility
router.register(r'assessments', AssessmentViewSet, basename='assessment')

# Admin CRUD routers
router.register(r'admin/campaigns', AdminCampaignViewSet, basename='admin-campaign')
router.register(r'admin/stages', AdminStageViewSet, basename='admin-stage')
router.register(r'admin/questions', AdminQuestionViewSet, basename='admin-question')
router.register(r'admin/challenges', AdminChallengeViewSet, basename='admin-challenge')
router.register(r'admin/testcases', AdminTestCaseViewSet, basename='admin-testcase')
router.register(r'admin/selections', AdminCandidateSelectionViewSet, basename='admin-selection')
router.register(r'admin/audit-logs', AdminAuditLogViewSet, basename='admin-audit-log')

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),

    # Authentication & Profile
    path('auth/register/', auth_register, name='auth-register'),
    path('auth/login/', auth_login, name='auth-login'),
    path('auth/logout/', auth_logout, name='auth-logout'),
    path('auth/me/', auth_me, name='auth-me'),

    # Candidate Progression & Attempt Lifecycles
    path('candidate/campaigns/', candidate_campaigns, name='candidate-campaigns'),
    path('candidate/stages/', candidate_stages, name='candidate-stages'),
    path('candidate/status/<int:campaign_id>/', candidate_assessment_status, name='candidate-status'),
    path('candidate/stages/<int:stage_id>/start/', candidate_start_stage, name='candidate-start-stage'),
    path('candidate/stages/<int:stage_id>/questions/', candidate_stage_questions, name='candidate-stage-questions'),
    path('candidate/submissions/autosave/', candidate_autosave_draft, name='candidate-autosave'),
    path('candidate/submissions/finalize/', candidate_finalize_submission, name='candidate-finalize'),
    path('candidate/execution/run-sample/', candidate_run_sample_code, name='candidate-run-sample'),
    path('candidate/integrity/events/', candidate_record_integrity_event, name='candidate-integrity-event'),

    # Reviewer Rubrics & Scoring
    path('reviewer/assignments/', reviewer_assigned_submissions, name='reviewer-assignments'),
    path('reviewer/evaluations/<int:stage_attempt_id>/', reviewer_get_evaluation, name='reviewer-get-evaluation'),
    path('reviewer/evaluations/<int:stage_attempt_id>/score/', reviewer_submit_scores, name='reviewer-submit-scores'),

    # Admin Operations & Reporting
    path('admin/candidates/', admin_candidates_list, name='admin-candidates-list'),
    path('admin/overview-metrics/', admin_overview_metrics, name='admin-overview-metrics'),
    path('admin/reports/campaign-summary/<int:campaign_id>/', admin_campaign_summary, name='admin-campaign-summary'),
    path('admin/reports/export-csv/<int:campaign_id>/', admin_export_csv, name='admin-export-csv'),
    path('admin/assign-reviewer/', admin_assign_reviewer, name='admin-assign-reviewer'),

    # Router endpoints
    path('', include(router.urls)),
]
