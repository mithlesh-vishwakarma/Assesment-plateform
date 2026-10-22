from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserRole,
    UserProfile,
    CandidateProfile,
    ReviewerProfile,
    Assessment,
    AssessmentCampaign,
    AssessmentVersion,
    AssessmentStage,
    StagePrerequisite,
    Question,
    QuestionType,
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

# -------------------------------------------------------------
# 1. Accounts & Authentication Serializers
# -------------------------------------------------------------

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'bio', 'avatar_url', 'created_at']


class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ['technical_track', 'years_of_experience', 'resume_url', 'github_url', 'linkedin_url', 'status', 'created_at']


class ReviewerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewerProfile
        fields = ['specialization', 'max_assigned_candidates', 'is_active']


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    candidate_profile = CandidateProfileSerializer(read_only=True)
    reviewer_profile = ReviewerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'candidate_profile', 'reviewer_profile']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.CANDIDATE, required=False)
    technical_track = serializers.CharField(required=False, default='fullstack')
    years_of_experience = serializers.FloatField(required=False, default=0.0)

    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate(self, attrs):
        if not attrs.get('username'):
            email = attrs.get('email', '')
            base_username = email.split('@')[0] if email else 'user'
            candidate = base_username
            idx = 1
            while User.objects.filter(username=candidate).exists():
                candidate = f"{base_username}{idx}"
                idx += 1
            attrs['username'] = candidate
        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if not attrs.get('username') and not attrs.get('email'):
            raise serializers.ValidationError("Please provide either your username or email address.")
        return attrs


# -------------------------------------------------------------
# 2. Existing Assessment & Campaign Configuration
# -------------------------------------------------------------

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'


class AssessmentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentVersion
        fields = '__all__'


class StagePrerequisiteSerializer(serializers.ModelSerializer):
    prerequisite_stage_name = serializers.ReadOnlyField(source='prerequisite_stage.name')

    class Meta:
        model = StagePrerequisite
        fields = ['id', 'stage', 'prerequisite_stage', 'prerequisite_stage_name', 'minimum_score']


class AssessmentStageSerializer(serializers.ModelSerializer):
    prerequisites = StagePrerequisiteSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentStage
        fields = '__all__'


class AssessmentCampaignSerializer(serializers.ModelSerializer):
    stages = AssessmentStageSerializer(many=True, read_only=True)
    versions = AssessmentVersionSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentCampaign
        fields = '__all__'


# -------------------------------------------------------------
# 3. Questions, Challenges & Test Cases
# -------------------------------------------------------------

class TestCaseSerializer(serializers.ModelSerializer):
    """
    Serializes test cases. When accessed by candidates, hidden test cases
    are filtered out or their inputs/outputs are never returned.
    """
    class Meta:
        model = TestCase
        fields = ['id', 'order', 'input_data', 'expected_output', 'is_sample', 'weight', 'explanation']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        is_staff_or_admin = request and (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin))
        # Mask private hidden test case data for candidates
        if not is_staff_or_admin and not instance.is_sample:
            data['input_data'] = '[HIDDEN]'
            data['expected_output'] = '[HIDDEN]'
            data['explanation'] = '[HIDDEN]'
        return data


class ChallengeSerializer(serializers.ModelSerializer):
    test_cases = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id', 'allowed_languages', 'starter_code', 'function_signature',
            'time_limit_seconds', 'memory_limit_mb', 'run_quota_per_attempt',
            'expected_output_format', 'test_cases'
        ]

    def get_test_cases(self, obj):
        request = self.context.get('request')
        is_staff = request and (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin))
        if is_staff:
            tcs = obj.test_cases.all()
        else:
            # Candidates only see sample test cases
            tcs = obj.test_cases.filter(is_sample=True)
        return TestCaseSerializer(tcs, many=True, context=self.context).data


class QuestionSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'prompt', 'question_type', 'difficulty', 'category',
            'points', 'instructions', 'constraints', 'time_expected_minutes',
            'tags', 'mcq_options', 'rubric_guide', 'is_active', 'version', 'challenge'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        is_staff = request and (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin))
        # Strip correct answer flags from MCQ options for candidate queries
        if not is_staff and instance.question_type == QuestionType.MCQ and data.get('mcq_options'):
            safe_opts = []
            for opt in data['mcq_options']:
                safe_opts.append({'id': opt.get('id'), 'text': opt.get('text')})
            data['mcq_options'] = safe_opts
        return data


# -------------------------------------------------------------
# 4. Submissions, Attempts & Execution
# -------------------------------------------------------------

class SubmissionVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionVersion
        fields = '__all__'


class WrittenResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WrittenResponse
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    versions = SubmissionVersionSerializer(many=True, read_only=True)
    written_response = WrittenResponseSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'stage_attempt', 'question', 'submission_type', 'content',
            'selected_options', 'language', 'is_draft', 'version_number',
            'score', 'evaluated', 'created_at', 'updated_at', 'versions', 'written_response'
        ]


class StageAttemptSerializer(serializers.ModelSerializer):
    stage_name = serializers.ReadOnlyField(source='stage.name')
    stage_order = serializers.ReadOnlyField(source='stage.order')
    stage_type = serializers.ReadOnlyField(source='stage.stage_type')
    time_limit_minutes = serializers.ReadOnlyField(source='stage.time_limit_minutes')
    submissions = SubmissionSerializer(many=True, read_only=True)

    class Meta:
        model = StageAttempt
        fields = [
            'id', 'assessment_attempt', 'stage', 'stage_name', 'stage_order', 'stage_type',
            'time_limit_minutes', 'status', 'start_time', 'deadline', 'submitted_at',
            'score', 'passed', 'attempt_number', 'run_quota_used', 'submissions'
        ]


class AssessmentAttemptSerializer(serializers.ModelSerializer):
    candidate_username = serializers.ReadOnlyField(source='candidate.username')
    campaign_title = serializers.ReadOnlyField(source='campaign.title')
    stage_attempts = StageAttemptSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentAttempt
        fields = [
            'id', 'candidate', 'candidate_username', 'campaign', 'campaign_title',
            'assessment_version', 'status', 'start_time', 'submitted_at',
            'final_score', 'passed', 'attempt_number', 'stage_attempts'
        ]


class ExecutionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionResult
        fields = [
            'id', 'job', 'stdout', 'stderr', 'compile_output', 'exit_code',
            'execution_time_ms', 'memory_used_kb', 'status_message',
            'passed_test_cases_count', 'total_test_cases_count', 'score_earned',
            'test_results_sanitized', 'created_at'
        ]


class ExecutionJobSerializer(serializers.ModelSerializer):
    result = ExecutionResultSerializer(read_only=True)

    class Meta:
        model = ExecutionJob
        fields = [
            'id', 'submission', 'stage_attempt', 'challenge', 'is_sample_run',
            'language', 'source_code', 'status', 'created_at', 'started_at', 'completed_at', 'result'
        ]


# -------------------------------------------------------------
# 5. Rubrics, Evaluations & Reviews
# -------------------------------------------------------------

class RubricCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricCriterion
        fields = '__all__'


class EvaluationRubricSerializer(serializers.ModelSerializer):
    criteria = RubricCriterionSerializer(many=True, read_only=True)

    class Meta:
        model = EvaluationRubric
        fields = '__all__'


class CriterionScoreSerializer(serializers.ModelSerializer):
    criterion_name = serializers.ReadOnlyField(source='criterion.name')
    max_points = serializers.ReadOnlyField(source='criterion.max_points')
    weight_percent = serializers.ReadOnlyField(source='criterion.weight_percent')

    class Meta:
        model = CriterionScore
        fields = ['id', 'stage_evaluation', 'criterion', 'criterion_name', 'max_points', 'weight_percent', 'score', 'comments']


class StageEvaluationSerializer(serializers.ModelSerializer):
    evaluator_username = serializers.ReadOnlyField(source='evaluator.username')
    criterion_scores = CriterionScoreSerializer(many=True, read_only=True)

    class Meta:
        model = StageEvaluation
        fields = [
            'id', 'stage_attempt', 'evaluator', 'evaluator_username', 'status',
            'automated_score', 'manual_score', 'total_score', 'is_passed',
            'reviewer_notes', 'evaluated_at', 'criterion_scores'
        ]


class ReviewerAssignmentSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.ReadOnlyField(source='reviewer.username')
    stage_name = serializers.ReadOnlyField(source='stage_attempt.stage.name')
    candidate_username = serializers.ReadOnlyField(source='stage_attempt.assessment_attempt.candidate.username')

    class Meta:
        model = ReviewerAssignment
        fields = '__all__'


# -------------------------------------------------------------
# 6. Integrity, Audit & Reports
# -------------------------------------------------------------

class IntegrityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrityEvent
        fields = '__all__'
        read_only_fields = ['candidate', 'timestamp']


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.ReadOnlyField(source='actor.username')

    class Meta:
        model = AuditLog
        fields = '__all__'


class CandidateSelectionSerializer(serializers.ModelSerializer):
    candidate_username = serializers.ReadOnlyField(source='candidate.username')
    candidate_email = serializers.ReadOnlyField(source='candidate.email')

    class Meta:
        model = CandidateSelection
        fields = '__all__'


class ReportExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = '__all__'
