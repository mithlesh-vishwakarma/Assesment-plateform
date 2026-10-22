from django.contrib import admin
from .models import (
    Assessment,
    UserProfile,
    CandidateProfile,
    ReviewerProfile,
    AssessmentCampaign,
    AssessmentVersion,
    AssessmentStage,
    StagePrerequisite,
    Question,
    StageQuestion,
    Challenge,
    TestCase,
    AssessmentAttempt,
    StageAttempt,
    Submission,
    SubmissionVersion,
    WrittenResponse,
    ExecutionJob,
    ExecutionResult,
    EvaluationRubric,
    RubricCriterion,
    StageEvaluation,
    CriterionScore,
    ReviewerAssignment,
    IntegrityEvent,
    AuditLog,
    CandidateSelection,
    ReportExport,
)

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'technical_track', 'years_of_experience', 'status', 'created_at')
    list_filter = ('status', 'technical_track')
    search_fields = ('user__username', 'user__email')


@admin.register(ReviewerProfile)
class ReviewerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'max_assigned_candidates', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'specialization')


@admin.register(AssessmentCampaign)
class AssessmentCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'pass_threshold_score', 'start_date', 'end_date')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')


@admin.register(AssessmentVersion)
class AssessmentVersionAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'version_number', 'is_published', 'published_at', 'created_at')
    list_filter = ('is_published', 'campaign')


@admin.register(AssessmentStage)
class AssessmentStageAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'stage_type', 'order', 'time_limit_minutes', 'pass_threshold_score', 'requires_manual_review', 'is_active')
    list_filter = ('campaign', 'stage_type', 'is_active')
    ordering = ('campaign', 'order')


@admin.register(StagePrerequisite)
class StagePrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('stage', 'prerequisite_stage', 'minimum_score')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question_type', 'difficulty', 'category', 'points', 'is_active')
    list_filter = ('question_type', 'difficulty', 'is_active', 'category')
    search_fields = ('title', 'prompt')


@admin.register(StageQuestion)
class StageQuestionAdmin(admin.ModelAdmin):
    list_display = ('stage', 'question', 'order', 'points_weight')
    list_filter = ('stage',)
    ordering = ('stage', 'order')


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('question', 'time_limit_seconds', 'memory_limit_mb', 'run_quota_per_attempt')


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'order', 'is_sample', 'weight')
    list_filter = ('is_sample', 'challenge')


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'campaign', 'attempt_number', 'status', 'final_score', 'passed', 'start_time')
    list_filter = ('status', 'passed', 'campaign')
    search_fields = ('candidate__username', 'campaign__title')


@admin.register(StageAttempt)
class StageAttemptAdmin(admin.ModelAdmin):
    list_display = ('assessment_attempt', 'stage', 'status', 'score', 'passed', 'deadline')
    list_filter = ('status', 'passed')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('stage_attempt', 'question', 'submission_type', 'is_draft', 'score', 'evaluated')
    list_filter = ('submission_type', 'is_draft', 'evaluated')


@admin.register(SubmissionVersion)
class SubmissionVersionAdmin(admin.ModelAdmin):
    list_display = ('submission', 'version_number', 'is_final', 'saved_at')
    list_filter = ('is_final',)


@admin.register(WrittenResponse)
class WrittenResponseAdmin(admin.ModelAdmin):
    list_display = ('submission',)


@admin.register(ExecutionJob)
class ExecutionJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'stage_attempt', 'language', 'is_sample_run', 'status', 'created_at')
    list_filter = ('status', 'is_sample_run', 'language')


@admin.register(ExecutionResult)
class ExecutionResultAdmin(admin.ModelAdmin):
    list_display = ('job', 'passed_test_cases_count', 'total_test_cases_count', 'score_earned', 'status_message')


@admin.register(EvaluationRubric)
class EvaluationRubricAdmin(admin.ModelAdmin):
    list_display = ('name', 'stage', 'created_at')


@admin.register(RubricCriterion)
class RubricCriterionAdmin(admin.ModelAdmin):
    list_display = ('name', 'rubric', 'weight_percent', 'max_points', 'order')


@admin.register(StageEvaluation)
class StageEvaluationAdmin(admin.ModelAdmin):
    list_display = ('stage_attempt', 'evaluator', 'status', 'automated_score', 'manual_score', 'total_score', 'is_passed')
    list_filter = ('status', 'is_passed')


@admin.register(CriterionScore)
class CriterionScoreAdmin(admin.ModelAdmin):
    list_display = ('stage_evaluation', 'criterion', 'score')


@admin.register(ReviewerAssignment)
class ReviewerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('stage_attempt', 'reviewer', 'assigned_by', 'status', 'assigned_at')
    list_filter = ('status', 'reviewer')


@admin.register(IntegrityEvent)
class IntegrityEventAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'event_type', 'stage_attempt', 'timestamp')
    list_filter = ('event_type',)
    search_fields = ('candidate__username',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'target_model', 'target_id', 'ip_address')
    list_filter = ('action', 'target_model')
    search_fields = ('actor__username', 'action', 'target_id')


@admin.register(CandidateSelection)
class CandidateSelectionAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'campaign', 'decision', 'ranking', 'decided_by', 'decided_at')
    list_filter = ('decision', 'campaign')
    ordering = ('ranking', '-decided_at')


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'requested_by', 'export_type', 'status', 'created_at')
    list_filter = ('export_type', 'status')
