from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from api.models import (
    StageAttempt,
    Question,
    Submission,
    SubmissionVersion,
    WrittenResponse,
    AttemptStatus,
    AuditLog,
)
from .stage_service import StageService

class SubmissionService:
    @staticmethod
    def validate_candidate_access(candidate, stage_attempt_id):
        """
        Validates that stage attempt belongs to the candidate, is active, and is not expired.
        """
        stage_attempt = StageAttempt.objects.select_related('assessment_attempt__candidate', 'stage').filter(id=stage_attempt_id).first()
        if not stage_attempt:
            raise ValidationError("Stage attempt not found.")

        if stage_attempt.assessment_attempt.candidate != candidate:
            raise PermissionDenied("You do not have permission to modify this stage attempt.")

        # Check deadline expiration
        StageService.check_and_update_expired_attempts(stage_attempt)

        if stage_attempt.status == AttemptStatus.EXPIRED:
            raise PermissionDenied("The time limit for this stage attempt has expired.")

        if stage_attempt.status != AttemptStatus.IN_PROGRESS:
            raise PermissionDenied(f"Cannot save or modify submissions for a stage in '{stage_attempt.status}' state.")

        return stage_attempt

    @classmethod
    def autosave_draft(cls, candidate, stage_attempt_id=None, question_id=None, submission_type="CODE", content="", selected_options=None, language="", written_details=None, request=None, stage_attempt=None, question=None):
        """
        Saves candidate draft answer efficiently without finalizing the stage attempt.
        Updates the draft in-place without generating excessive version/audit spam.
        """
        if not stage_attempt:
            stage_attempt = cls.validate_candidate_access(candidate, stage_attempt_id)
        if not question:
            question = Question.objects.filter(id=question_id).first()
            if not question:
                raise ValidationError("Question not found.")

        # Payload size validation (max 500KB)
        total_payload_bytes = len((content or '').encode('utf-8'))
        if total_payload_bytes > 500 * 1024:
            raise ValidationError("Payload size exceeds 500KB limit.")

        selected_options = selected_options or []
        written_details = written_details or {}

        with transaction.atomic():
            submission, created = Submission.objects.select_for_update().get_or_create(
                stage_attempt=stage_attempt,
                question=question,
                defaults={
                    'submission_type': submission_type,
                    'content': content,
                    'selected_options': selected_options,
                    'language': language,
                    'is_draft': True,
                    'version_number': 1,
                }
            )

            if not created:
                submission.content = content
                submission.selected_options = selected_options
                submission.language = language
                submission.is_draft = True
                submission.version_number += 1
                submission.save(update_fields=['content', 'selected_options', 'language', 'is_draft', 'version_number', 'updated_at'])

            # Update or create WrittenResponse if details provided
            if written_details or submission_type == 'WRITTEN':
                WrittenResponse.objects.update_or_create(
                    submission=submission,
                    defaults={
                        'reasoning_text': written_details.get('reasoning_text', content),
                        'architectural_decisions': written_details.get('architectural_decisions', ''),
                        'trade_offs': written_details.get('trade_offs', ''),
                        'security_considerations': written_details.get('security_considerations', ''),
                        'assumptions': written_details.get('assumptions', ''),
                        'incident_mitigation': written_details.get('incident_mitigation', ''),
                    }
                )

            return submission

    @classmethod
    def finalize_stage_submission(cls, candidate, stage_attempt_id, request=None):
        """
        Finalizes stage attempt: locks all submissions, marks final versions,
        transitions state to EVALUATING or MANUAL_REVIEW, and initiates evaluation.
        """
        stage_attempt = cls.validate_candidate_access(candidate, stage_attempt_id)

        with transaction.atomic():
            submissions = Submission.objects.filter(stage_attempt=stage_attempt)
            now = timezone.now()

            for sub in submissions:
                sub.is_draft = False
                sub.save(update_fields=['is_draft', 'updated_at'])

                # Create final immutable version record
                SubmissionVersion.objects.create(
                    submission=sub,
                    version_number=sub.version_number + 1,
                    content=sub.content,
                    language=sub.language,
                    selected_options=sub.selected_options,
                    is_final=True,
                )

            # Set status based on manual review requirement
            new_status = AttemptStatus.MANUAL_REVIEW if stage_attempt.stage.requires_manual_review else AttemptStatus.EVALUATING
            stage_attempt.status = new_status
            stage_attempt.submitted_at = now
            stage_attempt.save(update_fields=['status', 'submitted_at', 'updated_at'])

            # Audit log
            ip_addr = request.META.get('REMOTE_ADDR') if request else None
            AuditLog.objects.create(
                actor=candidate,
                action='STAGE_SUBMITTED',
                target_model='StageAttempt',
                target_id=str(stage_attempt.id),
                ip_address=ip_addr,
                details={'submissions_count': submissions.count(), 'status': new_status}
            )

            # Automatically run evaluation for objective portions
            from .evaluation_service import EvaluationService
            EvaluationService.evaluate_stage_attempt(stage_attempt)

            return stage_attempt
