from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
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
    ReviewerAssignmentStatus,
    SelectionDecision,
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

    if data.get('name'):
        names = data['name'].strip().split(' ', 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
        user.save()

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

    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    password = serializer.validated_data['password']

    user = None
    if username:
        user = authenticate(username=username, password=password)

    if not user and (email or username):
        lookup = email or username
        try:
            user_obj = User.objects.get(email__iexact=lookup)
            user = authenticate(username=user_obj.username, password=password)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            pass

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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_password_reset_request(request):
    """
    Initiates password reset process by generating a cryptographically secure reset token.
    Works for Candidate, Reviewer, and Admin accounts.
    """
    email = request.data.get('email', '').strip()
    if not email:
        return Response({"error": "Email address is required."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response({
            "message": "If an account exists for this email, password reset instructions have been generated."
        }, status=status.HTTP_200_OK)

    token = default_token_generator.make_token(user)

    subject = "Amerigam Platform - Password Reset Request"
    message = (
        f"Hello {user.first_name or user.username},\n\n"
        f"You requested to reset your password for your Amerigam account.\n\n"
        f"Your password reset token is:\n{token}\n\n"
        f"Enter this token along with your new password to complete the reset.\n\n"
        f"If you did not request this, you can safely ignore this message.\n\n"
        f"Amerigam Assessment Platform"
    )
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@amerigam.com')
        send_mail(subject, message, from_email, [user.email], fail_silently=True)
    except Exception:
        pass

    AuditService.log(user, 'PASSWORD_RESET_REQUESTED', 'User', str(user.id), request=request)

    return Response({
        "message": "Password reset instructions sent. Please check your email or use the reset token below.",
        "reset_token": token,
        "email": user.email
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_password_reset_confirm(request):
    """
    Validates token and updates user password securely.
    """
    email = request.data.get('email', '').strip()
    token = request.data.get('token', '').strip()
    new_password = request.data.get('new_password', '')

    if not email or not token or not new_password:
        return Response({"error": "Email, reset token, and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 8:
        return Response({"error": "New password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response({"error": "No account found matching this email address."}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"error": "Invalid or expired password reset token. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    # Invalidate old auth tokens and issue fresh token
    Token.objects.filter(user=user).delete()
    new_auth_token, _ = Token.objects.get_or_create(user=user)

    AuditService.log(user, 'PASSWORD_RESET_COMPLETED', 'User', str(user.id), request=request)

    return Response({
        "message": "Password has been successfully updated. You can now log in.",
        "token": new_auth_token.key
    }, status=status.HTTP_200_OK)


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
@permission_classes([permissions.AllowAny])
def candidate_stages(request):
    """
    Returns dynamic assessment stages matching the frontend Stage interface.
    Computes live stage progress and scores if candidate is authenticated.
    """
    campaign = AssessmentCampaign.objects.filter(is_active=True).order_by('-created_at').first()
    if not campaign:
        campaign = AssessmentCampaign.objects.first()
    if not campaign:
        return Response([])

    stages = campaign.stages.filter(is_active=True).annotate(
        questions_count=Count('stage_questions')
    ).order_by('order')

    attempt = None
    st_attempt_map = {}
    max_completed_order = 0

    if request.user and request.user.is_authenticated:
        attempt = AssessmentAttempt.objects.filter(candidate=request.user, campaign=campaign).order_by('-created_at').first()
        if attempt:
            # Single batch-query for all stage attempts under this assessment attempt
            st_attempts = StageAttempt.objects.filter(assessment_attempt=attempt).select_related('stage').order_by('stage_id', '-attempt_number')
            for sa in st_attempts:
                if sa.stage_id not in st_attempt_map:
                    st_attempt_map[sa.stage_id] = sa
                if sa.status in [AttemptStatus.PASSED, AttemptStatus.SUBMITTED]:
                    if sa.stage and sa.stage.order > max_completed_order:
                        max_completed_order = sa.stage.order

    stage_list = []
    for s in stages:
        category = s.stage_type.split('_')[-1] if '_' in s.stage_type else s.stage_type.upper()
        if category == 'FUNDAMENTALS':
            category = 'CORE'
        elif category == 'CODING':
            category = 'PRACTICAL'
        elif category == 'CHALLENGES':
            category = 'DESIGN'
        elif category == 'REASONING':
            category = 'REASONING'

        st_status = 'locked'
        st_score = None

        if attempt:
            st_attempt = st_attempt_map.get(s.id)
            if st_attempt:
                if st_attempt.status == AttemptStatus.PASSED:
                    st_status = 'completed'
                    st_score = int(st_attempt.score) if (st_attempt.score is not None and st_attempt.score > 0) else None
                elif st_attempt.status == AttemptStatus.IN_PROGRESS:
                    st_status = 'in-progress'
                elif st_attempt.status == AttemptStatus.SUBMITTED:
                    st_status = 'completed'
                    st_score = int(st_attempt.score) if (st_attempt.score is not None and st_attempt.score > 0) else None
            else:
                if s.order <= max_completed_order + 1:
                    st_status = 'available'
        else:
            # Fresh candidate with no attempt: Stage 1 is available, subsequent stages are locked, 0% progress, no fake scores
            st_status = 'available' if s.order == 1 else 'locked'
            st_score = None

        stage_list.append({
            "id": s.order,
            "backend_id": s.id,
            "title": s.name.split(': ')[-1] if ': ' in s.name else s.name,
            "subtitle": s.description,
            "category": category,
            "duration": f"{s.time_limit_minutes} min",
            "questions": s.questions_count,
            "status": st_status,
            "score": st_score,
        })

    return Response(stage_list)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def candidate_stage_questions(request, stage_id):
    """
    Retrieves question contents for the specified stage order or ID.
    Returns question details, starter code, and sample test cases.
    """
    stage = None
    try:
        stage_id_int = int(stage_id)
        stage = AssessmentStage.objects.filter(Q(id=stage_id_int) | Q(order=stage_id_int)).first()
    except (ValueError, TypeError):
        stage = AssessmentStage.objects.first()

    if not stage:
        stage = AssessmentStage.objects.first()
    if not stage:
        return Response([])

    questions = [sq.question for sq in stage.stage_questions.select_related('question', 'question__challenge').order_by('order')]
    return Response(QuestionSerializer(questions, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_autosave_draft(request):
    """
    Autosaves candidate's work (code or written answers) without finalizing the stage.
    """
    stage_attempt_id = request.data.get('stage_attempt_id')
    question_id = request.data.get('question_id') or request.data.get('stage_question_id')
    submission_type = request.data.get('submission_type', 'CODE')
    content = request.data.get('content') or request.data.get('code') or ''
    selected_options = request.data.get('selected_options', [])
    language = request.data.get('language', '')
    written_details = request.data.get('written_details') or {}
    if not written_details and request.data.get('written_response'):
        written_details = {'explanation': request.data.get('written_response')}

    # Resolve question
    question = None
    if question_id:
        question = Question.objects.filter(id=question_id).first()
        if not question:
            sq = StageQuestion.objects.filter(id=question_id).select_related('question').first()
            if sq:
                question = sq.question
    if not question:
        question = Question.objects.first()

    if not question:
        return Response({"error": "No question found to save work against."}, status=status.HTTP_400_BAD_REQUEST)

    # Resolve stage attempt
    stage_attempt = None
    if stage_attempt_id:
        try:
            stage_attempt = SubmissionService.validate_candidate_access(request.user, stage_attempt_id)
        except Exception:
            stage_attempt = None

    if not stage_attempt:
        stage_attempt = StageAttempt.objects.filter(
            assessment_attempt__candidate=request.user,
            status=AttemptStatus.IN_PROGRESS
        ).order_by('-created_at').first()

    if not stage_attempt:
        # Auto-start stage for candidate if not yet started
        sq = StageQuestion.objects.filter(question=question).select_related('stage').first()
        target_stage = sq.stage if sq else None
        if not target_stage:
            campaign = AssessmentCampaign.objects.filter(is_active=True).first()
            if campaign:
                target_stage = campaign.stages.filter(is_active=True).order_by('order').first()

        if target_stage:
            try:
                stage_attempt = StageService.start_stage(request.user, target_stage.id, request=request)
            except Exception as e:
                return Response({"error": f"Failed to initialize stage attempt: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    if not stage_attempt:
        return Response({"error": "No active stage attempt found. Please enter the challenge from the overview."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        sub = SubmissionService.autosave_draft(
            candidate=request.user,
            stage_attempt_id=stage_attempt.id,
            question_id=question.id,
            submission_type=submission_type,
            content=content,
            selected_options=selected_options,
            language=language,
            written_details=written_details,
            request=request,
            stage_attempt=stage_attempt,
            question=question
        )
        return Response({
            "status": "saved",
            "id": sub.id,
            "version_number": sub.version_number,
            "saved_at": timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_finalize_submission(request):
    """
    Finalizes candidate's stage attempt, freezing submissions and initiating grading.
    """
    stage_attempt_id = request.data.get('stage_attempt_id')
    stage_attempt = None
    if stage_attempt_id:
        try:
            stage_attempt = SubmissionService.validate_candidate_access(request.user, stage_attempt_id)
        except Exception:
            stage_attempt = None

    if not stage_attempt:
        stage_attempt = StageAttempt.objects.filter(
            assessment_attempt__candidate=request.user,
            status=AttemptStatus.IN_PROGRESS
        ).order_by('-created_at').first()

    if not stage_attempt:
        return Response({"error": "No active stage attempt found to finalize."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        st_attempt = SubmissionService.finalize_stage_submission(
            candidate=request.user,
            stage_attempt_id=stage_attempt.id,
            request=request
        )
        return Response(StageAttemptSerializer(st_attempt).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def candidate_run_sample_code(request):
    """
    Executes code against sample test cases using the secure isolated runner adapter.
    Never executes via eval() / exec() in Django!
    """
    stage_attempt_id = request.data.get('stage_attempt_id')
    challenge_id = request.data.get('challenge_id')
    stage_question_id = request.data.get('stage_question_id') or request.data.get('question_id')
    language = request.data.get('language', 'typescript')
    source_code = request.data.get('source_code') or request.data.get('code') or ''

    # Check for empty or placeholder starter code
    if not source_code or not source_code.strip() or source_code.strip() == '// Write your solution here':
        return Response({
            "error": "Please write your solution code before running tests."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Resolve Challenge
    challenge = None
    if stage_question_id:
        sq = StageQuestion.objects.filter(id=stage_question_id).select_related('question__challenge').first()
        if sq and sq.question:
            challenge = getattr(sq.question, 'challenge', None)
        if not challenge:
            q = Question.objects.filter(id=stage_question_id).select_related('challenge').first()
            if q:
                challenge = getattr(q, 'challenge', None)

    if not challenge and challenge_id:
        challenge = Challenge.objects.filter(id=challenge_id).first()

    if not challenge:
        challenge = Challenge.objects.first()

    if not challenge:
        return Response({"error": "No challenge found to evaluate this code against."}, status=status.HTTP_400_BAD_REQUEST)

    # Resolve Stage Attempt
    stage_attempt = None
    if stage_attempt_id:
        try:
            stage_attempt = SubmissionService.validate_candidate_access(request.user, stage_attempt_id)
        except Exception:
            stage_attempt = None

    if not stage_attempt:
        stage_attempt = StageAttempt.objects.filter(
            assessment_attempt__candidate=request.user,
            status=AttemptStatus.IN_PROGRESS
        ).order_by('-created_at').first()

    if not stage_attempt:
        campaign = AssessmentCampaign.objects.filter(is_active=True).first()
        if campaign:
            st = campaign.stages.filter(is_active=True).order_by('order').first()
            if st:
                try:
                    stage_attempt = StageService.start_stage(request.user, st.id, request=request)
                except Exception:
                    pass

    if not stage_attempt:
        return Response({"error": "Active stage attempt not found. Please start the stage first."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = ExecutionService.execute_challenge(
            stage_attempt=stage_attempt,
            challenge=challenge,
            language=language,
            source_code=source_code,
            is_sample_run=True,
        )
        return Response(ExecutionResultSerializer(result).data, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


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
    queryset = Question.objects.all().select_related('challenge').prefetch_related('challenge__test_cases').order_by('-created_at')
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


@api_view(['GET'])
@permission_classes([IsReviewerRole])
def admin_candidates_list(request):
    """
    Returns live list of candidates with their active statuses and scores for the Admin/Reviewer dashboards.
    Optimized with bulk prefetches to prevent N+1 query latency over remote database.
    """
    candidates = list(
        User.objects.filter(profile__role=UserRole.CANDIDATE)
        .select_related('profile', 'candidate_profile')
        .order_by('-date_joined')
    )
    
    cand_ids = [c.id for c in candidates]
    
    # Pre-fetch latest attempt for each candidate in one bulk query
    attempts = {}
    for att in AssessmentAttempt.objects.filter(candidate_id__in=cand_ids).order_by('created_at'):
        attempts[att.candidate_id] = att

    # Pre-fetch candidate selections in one bulk query
    selections = {s.candidate_id: s for s in CandidateSelection.objects.filter(candidate_id__in=cand_ids)}

    # Pre-fetch pending reviewer assignments in one bulk query
    pending_reviews = set(
        ReviewerAssignment.objects.filter(
            stage_attempt__assessment_attempt__candidate_id__in=cand_ids,
            status=ReviewerAssignmentStatus.ASSIGNED
        ).values_list('stage_attempt__assessment_attempt__candidate_id', flat=True)
    )

    results = []
    for c in candidates:
        attempt = attempts.get(c.id)
        selection = selections.get(c.id)
        has_pending = c.id in pending_reviews

        status_str = 'Not started'
        score_val = None
        if selection and selection.decision == SelectionDecision.SELECTED:
            status_str = 'Selected'
            score_val = int(attempt.final_score) if (attempt and attempt.final_score) else None
        elif attempt:
            if attempt.status == AttemptStatus.PASSED:
                status_str = 'Passed'
                score_val = int(attempt.final_score) if attempt.final_score > 0 else None
            elif attempt.status == AttemptStatus.SUBMITTED:
                status_str = 'Needs review' if has_pending else 'Submitted'
                score_val = int(attempt.final_score) if attempt.final_score > 0 else None
            elif attempt.status == AttemptStatus.IN_PROGRESS:
                status_str = 'In progress'
            else:
                status_str = 'Not started'

        if has_pending:
            status_str = 'Needs review'

        track = getattr(getattr(c, 'candidate_profile', None), 'technical_track', '') or 'Full Stack'
        role_str = f"{track.capitalize()} Engineer" if not track.endswith('Engineer') else track
        full_name = f"{c.first_name} {c.last_name}".strip() or c.username

        results.append({
            "id": f"AEC-20{c.id:02d}",
            "user_id": c.id,
            "name": full_name,
            "email": c.email,
            "role": role_str,
            "status": status_str,
            "score": score_val,
            "updated": "Today",
        })

    return Response(results)


@api_view(['GET'])
@permission_classes([IsReviewerRole])
def admin_overview_metrics(request):
    """
    Returns live aggregate platform metrics for Admin and Reviewer dashboards.
    """
    total_candidates = User.objects.filter(profile__role=UserRole.CANDIDATE).count()
    selected_count = CandidateSelection.objects.filter(decision=SelectionDecision.SELECTED).count()
    awaiting_review = ReviewerAssignment.objects.filter(status=ReviewerAssignmentStatus.ASSIGNED).count()
    in_progress_count = AssessmentAttempt.objects.filter(status=AttemptStatus.IN_PROGRESS).count()

    return Response({
        "total_candidates": total_candidates,
        "in_progress": in_progress_count,
        "awaiting_review": awaiting_review,
        "selected": selected_count,
        "selection_rate": f"{round((selected_count / max(1, total_candidates)) * 100, 1)}%",
    })
