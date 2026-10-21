from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied, ValidationError

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
    StageQuestion,
    Challenge,
    TestCase,
    AssessmentAttempt,
    StageAttempt,
    Submission,
    ExecutionJob,
    ExecutionResult,
    EvaluationRubric,
    RubricCriterion,
    StageEvaluation,
    ReviewerAssignment,
    IntegrityEvent,
    AuditLog,
    CandidateSelection,
    ReportExport,
    AttemptStatus,
)

from .serializers import (
    AssessmentSerializer,
    UserDetailSerializer,
    RegisterSerializer,
    LoginSerializer,
    AssessmentCampaignSerializer,
    AssessmentVersionSerializer,
    AssessmentStageSerializer,
    StagePrerequisiteSerializer,
    QuestionSerializer,
    ChallengeSerializer,
    TestCaseSerializer,
    AssessmentAttemptSerializer,
    StageAttemptSerializer,
    SubmissionSerializer,
    ExecutionJobSerializer,
    ExecutionResultSerializer,
    EvaluationRubricSerializer,
    StageEvaluationSerializer,
    ReviewerAssignmentSerializer,
    IntegrityEventSerializer,
    AuditLogSerializer,
    CandidateSelectionSerializer,
    ReportExportSerializer,
)

from .permissions import (
    IsAdminRole,
    IsReviewerRole,
    IsCandidateRole,
    IsAttemptOwnerOrStaff,
)

from .services import (
    StageService,
    SubmissionService,
    ExecutionService,
    EvaluationService,
    AuditService,
    ReportService,
)

# -------------------------------------------------------------
# 1. Health Check & Legacy Assessment ViewSet (Preserved for Frontend)
# -------------------------------------------------------------

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Health check endpoint preserved for frontend connection monitoring.
    """
    return Response({
        "status": "success",
        "message": "Amerigam Engineering Challenge Backend is online and healthy!",
        "version": "2.0.0",
        "active_models": [
            "accounts", "assessments", "stages", "questions",
            "challenges", "submissions", "execution", "evaluation",
            "integrity", "reviews", "audit", "reports"
        ]
    }, status=status.HTTP_200_OK)


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    Existing Assessment ViewSet preserved for backward compatibility.
    """
    queryset = Assessment.objects.all().order_by('-created_at')
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.AllowAny]


# -------------------------------------------------------------
# 2. Authentication & Profile Endpoints
# -------------------------------------------------------------

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    role = data.get('role', UserRole.CANDIDATE)
    UserProfile.objects.create(user=user, role=role)

    if role == UserRole.CANDIDATE:
        CandidateProfile.objects.create(
            user=user,
            technical_track=data.get('technical_track', 'fullstack'),
            years_of_experience=data.get('years_of_experience', 0.0),
        )
    elif role == UserRole.REVIEWER:
        ReviewerProfile.objects.create(user=user)

    token, _ = Token.objects.get_or_create(user=user)
    AuditService.log(user, 'USER_REGISTERED', 'User', str(user.id), request=request)

    return Response({
        "token": token.key,
        "user": UserDetailSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    AuditService.log(user, 'USER_LOGGED_IN', 'User', str(user.id), request=request)

    return Response({
        "token": token.key,
        "user": UserDetailSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def auth_logout(request):
    Token.objects.filter(user=request.user).delete()
    AuditService.log(request.user, 'USER_LOGGED_OUT', 'User', str(request.user.id), request=request)
    return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def auth_me(request):
    if request.method == 'PATCH':
        profile = getattr(request.user, 'profile', None)
        if profile:
            for field in ['phone', 'bio', 'avatar_url']:
                if field in request.data:
                    setattr(profile, field, request.data[field])
            profile.save()

        cand_prof = getattr(request.user, 'candidate_profile', None)
        if cand_prof and profile and profile.role == UserRole.CANDIDATE:
            for field in ['technical_track', 'years_of_experience', 'resume_url', 'github_url', 'linkedin_url']:
                if field in request.data:
                    setattr(cand_prof, field, request.data[field])
            cand_prof.save()

    return Response(UserDetailSerializer(request.user).data)


# -------------------------------------------------------------
# 3. Candidate Assessment & Progression Endpoints
# -------------------------------------------------------------

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def candidate_campaigns(request):
    """
    List published assessment campaigns for candidates.
    """
    campaigns = AssessmentCampaign.objects.filter(is_active=True).order_by('-created_at')
    return Response(AssessmentCampaignSerializer(campaigns, many=True).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def candidate_assessment_status(request, campaign_id):
    """
    Retrieves the candidate's active stage, progression eligibility, and remaining deadlines.
    """
    campaign = get_object_or_404(AssessmentCampaign, id=campaign_id)
    attempt = AssessmentAttempt.objects.filter(candidate=request.user, campaign=campaign).order_by('-created_at').first()

    stages = campaign.stages.filter(is_active=True).order_by('order')
    stage_statuses = []

    for st in stages:
        eligible, reason = StageService.is_stage_eligible(request.user, st, attempt)
        st_attempt = None
        if attempt:
            st_attempt = StageAttempt.objects.filter(assessment_attempt=attempt, stage=st).order_by('-attempt_number').first()
            if st_attempt:
                StageService.check_and_update_expired_attempts(st_attempt)

        stage_statuses.append({
            "stage_id": st.id,
            "stage_name": st.name,
            "stage_type": st.stage_type,
            "order": st.order,
            "time_limit_minutes": st.time_limit_minutes,
            "is_eligible": eligible,
            "eligibility_reason": reason,
            "requires_manual_review": st.requires_manual_review,
            "attempt": StageAttemptSerializer(st_attempt).data if st_attempt else None,
        })

    return Response({
        "campaign_id": campaign.id,
        "campaign_title": campaign.title,
        "assessment_attempt": AssessmentAttemptSerializer(attempt).data if attempt else None,
        "stages": stage_statuses,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_start_stage(request, stage_id):
    """
    Starts an assessment stage, recording the server-controlled deadline.
    """
    stage_attempt = StageService.start_stage(request.user, stage_id, request=request)
    return Response(StageAttemptSerializer(stage_attempt).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def candidate_stage_questions(request, stage_id):
    """
    Retrieves question contents for the current stage.
    Ensures hidden test cases are never returned to candidate.
    """
    stage = get_object_or_404(AssessmentStage, id=stage_id)
    attempt = AssessmentAttempt.objects.filter(candidate=request.user, campaign=stage.campaign).first()
    if not attempt:
        raise PermissionDenied("You must start the assessment before viewing questions.")

    st_attempt = StageAttempt.objects.filter(assessment_attempt=attempt, stage=stage).order_by('-attempt_number').first()
    if not st_attempt:
        raise PermissionDenied("You must start this stage before accessing questions.")

    StageService.check_and_update_expired_attempts(st_attempt)
    if st_attempt.status == AttemptStatus.EXPIRED:
        raise PermissionDenied("Stage attempt time limit has expired.")

    questions = [sq.question for sq in stage.stage_questions.select_related('question').order_by('order')]
    return Response(QuestionSerializer(questions, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_autosave_draft(request):
    """
    Autosaves candidate's work (code or written answers) without finalizing the stage.
    """
    stage_attempt_id = request.data.get('stage_attempt_id')
    question_id = request.data.get('question_id')
    submission_type = request.data.get('submission_type', 'CODE')
    content = request.data.get('content', '')
    selected_options = request.data.get('selected_options', [])
    language = request.data.get('language', '')
    written_details = request.data.get('written_details', {})

    if not stage_attempt_id or not question_id:
        return Response({"error": "stage_attempt_id and question_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    sub = SubmissionService.autosave_draft(
        candidate=request.user,
        stage_attempt_id=stage_attempt_id,
        question_id=question_id,
        submission_type=submission_type,
        content=content,
        selected_options=selected_options,
        language=language,
        written_details=written_details,
        request=request
    )
    return Response(SubmissionSerializer(sub).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_finalize_submission(request):
    """
    Finalizes candidate's stage attempt, freezing submissions and initiating grading.
    """
    stage_attempt_id = request.data.get('stage_attempt_id')
    if not stage_attempt_id:
        return Response({"error": "stage_attempt_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    st_attempt = SubmissionService.finalize_stage_submission(
        candidate=request.user,
        stage_attempt_id=stage_attempt_id,
        request=request
    )
    return Response(StageAttemptSerializer(st_attempt).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_run_sample_code(request):
    """
    Executes code against sample test cases using the secure isolated runner adapter.
    Never executes via eval() / exec() in Django!
    """
    stage_attempt_id = request.data.get('stage_attempt_id')
    challenge_id = request.data.get('challenge_id')
    language = request.data.get('language', 'python')
    source_code = request.data.get('source_code', '')

    if not stage_attempt_id or not challenge_id:
        return Response({"error": "stage_attempt_id and challenge_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    stage_attempt = SubmissionService.validate_candidate_access(request.user, stage_attempt_id)
    challenge = get_object_or_404(Challenge, id=challenge_id)

    result = ExecutionService.execute_challenge(
        stage_attempt=stage_attempt,
        challenge=challenge,
        language=language,
        source_code=source_code,
        is_sample_run=True,
    )

    return Response(ExecutionResultSerializer(result).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_record_integrity_event(request):
    """
    Records candidate window blur, tab switch, copy/paste, or devtools detection.
    """
    stage_attempt_id = request.data.get('stage_attempt_id')
    event_type = request.data.get('event_type')
    metadata = request.data.get('metadata', {})

    if not stage_attempt_id or not event_type:
        return Response({"error": "stage_attempt_id and event_type required."}, status=status.HTTP_400_BAD_REQUEST)

    stage_attempt = get_object_or_404(StageAttempt, id=stage_attempt_id, assessment_attempt__candidate=request.user)
    event = AuditService.record_integrity_event(request.user, stage_attempt, event_type, metadata)

    return Response(IntegrityEventSerializer(event).data, status=status.HTTP_201_CREATED)


# -------------------------------------------------------------
# 4. Reviewer Endpoints
# -------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsReviewerRole])
def reviewer_assigned_submissions(request):
    """
    Returns submissions assigned to the authenticated reviewer.
    """
    assignments = ReviewerAssignment.objects.filter(reviewer=request.user).select_related(
        'stage_attempt__assessment_attempt__candidate',
        'stage_attempt__stage'
    )
    return Response(ReviewerAssignmentSerializer(assignments, many=True).data)


@api_view(['GET'])
@permission_classes([IsReviewerRole])
def reviewer_get_evaluation(request, stage_attempt_id):
    """
    Retrieves full evaluation details, including candidate code and rubric criteria.
    """
    stage_attempt = get_object_or_404(StageAttempt, id=stage_attempt_id)
    # Check assignment permission if not admin
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin)):
        if not ReviewerAssignment.objects.filter(stage_attempt=stage_attempt, reviewer=request.user).exists():
            raise PermissionDenied("You are not assigned to review this submission.")

    # Ensure rubric exists
    EvaluationService.ensure_default_rubric(stage_attempt.stage)
    evaluation, _ = StageEvaluation.objects.get_or_create(stage_attempt=stage_attempt)

    rubric = EvaluationRubric.objects.filter(stage=stage_attempt.stage).first()

    return Response({
        "stage_attempt": StageAttemptSerializer(stage_attempt).data,
        "evaluation": StageEvaluationSerializer(evaluation).data,
        "rubric": EvaluationRubricSerializer(rubric).data if rubric else None,
    })


@api_view(['POST'])
@permission_classes([IsReviewerRole])
def reviewer_submit_scores(request, stage_attempt_id):
    """
    Submits scores against defined rubric criteria with qualitative notes.
    """
    stage_attempt = get_object_or_404(StageAttempt, id=stage_attempt_id)
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin)):
        if not ReviewerAssignment.objects.filter(stage_attempt=stage_attempt, reviewer=request.user).exists():
            raise PermissionDenied("You are not assigned to review this submission.")

    criteria_scores = request.data.get('criteria_scores', [])
    reviewer_notes = request.data.get('reviewer_notes', '')

    evaluation, _ = StageEvaluation.objects.get_or_create(stage_attempt=stage_attempt)
    updated_eval = EvaluationService.record_manual_review(
        stage_evaluation=evaluation,
        reviewer=request.user,
        criteria_scores=criteria_scores,
        reviewer_notes=reviewer_notes
    )

    # Mark reviewer assignment completed
    ReviewerAssignment.objects.filter(stage_attempt=stage_attempt, reviewer=request.user).update(
        status='COMPLETED',
        completed_at=timezone.now()
    )

    AuditService.log(request.user, 'STAGE_EVALUATED', 'StageEvaluation', str(updated_eval.id), request=request)

    return Response(StageEvaluationSerializer(updated_eval).data, status=status.HTTP_200_OK)


# -------------------------------------------------------------
# 5. Administrator Management ViewSets
# -------------------------------------------------------------

class AdminCampaignViewSet(viewsets.ModelViewSet):
    queryset = AssessmentCampaign.objects.all().order_by('-created_at')
    serializer_class = AssessmentCampaignSerializer
    permission_classes = [IsAdminRole]

    @action(detail=True, methods=['post'])
    def publish_version(self, request, pk=None):
        campaign = self.get_object()
        changelog = request.data.get('changelog', 'Published new assessment version')

        latest = campaign.versions.order_by('-version_number').first()
        new_v = (latest.version_number + 1) if latest else 1

        # Snapshot active stages and questions configuration
        snapshot = {
            "title": campaign.title,
            "pass_threshold_score": campaign.pass_threshold_score,
            "stages": [
                {
                    "name": s.name,
                    "order": s.order,
                    "time_limit_minutes": s.time_limit_minutes,
                    "stage_type": s.stage_type,
                    "questions": [sq.question.title for sq in s.stage_questions.all()]
                }
                for s in campaign.stages.filter(is_active=True).order_by('order')
            ]
        }

        version = AssessmentVersion.objects.create(
            campaign=campaign,
            version_number=new_v,
            changelog=changelog,
            is_published=True,
            published_at=timezone.now(),
            configuration_snapshot=snapshot
        )
        AuditService.log(request.user, 'VERSION_PUBLISHED', 'AssessmentVersion', str(version.id), request=request)
        return Response(AssessmentVersionSerializer(version).data, status=status.HTTP_201_CREATED)


class AdminStageViewSet(viewsets.ModelViewSet):
    queryset = AssessmentStage.objects.all().order_by('campaign', 'order')
    serializer_class = AssessmentStageSerializer
    permission_classes = [IsAdminRole]


class AdminQuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by('-created_at')
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminRole]


class AdminChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [IsAdminRole]


class AdminTestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.all().order_by('challenge', 'order')
    serializer_class = TestCaseSerializer
    permission_classes = [IsAdminRole]


class AdminCandidateSelectionViewSet(viewsets.ModelViewSet):
    """
    Manages final selection decisions, including assigning ranks 1..4 for the top four candidates.
    """
    queryset = CandidateSelection.objects.all().order_by('ranking')
    serializer_class = CandidateSelectionSerializer
    permission_classes = [IsAdminRole]

    def perform_create(self, serializer):
        serializer.save(decided_by=self.request.user)


class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminRole]


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_campaign_summary(request, campaign_id):
    campaign = get_object_or_404(AssessmentCampaign, id=campaign_id)
    summary = ReportService.generate_campaign_summary(campaign)
    return Response(summary, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminRole])
def admin_export_csv(request, campaign_id):
    campaign = get_object_or_404(AssessmentCampaign, id=campaign_id)
    report, csv_text = ReportService.export_report_csv(campaign, request.user)
    return Response({
        "report_id": report.id,
        "csv_text": csv_text,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminRole])
def admin_assign_reviewer(request):
    stage_attempt_id = request.data.get('stage_attempt_id')
    reviewer_id = request.data.get('reviewer_id')

    stage_attempt = get_object_or_404(StageAttempt, id=stage_attempt_id)
    reviewer = get_object_or_404(User, id=reviewer_id)

    assignment, _ = ReviewerAssignment.objects.update_or_create(
        stage_attempt=stage_attempt,
        reviewer=reviewer,
        defaults={'assigned_by': request.user, 'status': 'ASSIGNED'}
    )
    AuditService.log(request.user, 'REVIEWER_ASSIGNED', 'ReviewerAssignment', str(assignment.id), request=request)
    return Response(ReviewerAssignmentSerializer(assignment).data, status=status.HTTP_200_OK)
