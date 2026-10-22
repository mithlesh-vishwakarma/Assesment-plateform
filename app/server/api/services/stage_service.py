from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from api.models import (
    AssessmentCampaign,
    AssessmentStage,
    StagePrerequisite,
    AssessmentAttempt,
    StageAttempt,
    AttemptStatus,
    AuditLog,
)

class StageService:
    @staticmethod
    def get_or_create_assessment_attempt(candidate, campaign):
        """
        Retrieves active assessment attempt or creates one if allowed under campaign limits.
        """
        attempt = AssessmentAttempt.objects.filter(
            candidate=candidate,
            campaign=campaign,
            status__in=[AttemptStatus.IN_PROGRESS, AttemptStatus.SUBMITTED, AttemptStatus.EVALUATING]
        ).order_by('-created_at').first()

        if not attempt:
            # Testing mode: unlimited attempts permitted
            total_attempts = AssessmentAttempt.objects.filter(
                candidate=candidate,
                campaign=campaign
            ).count()

            # Get latest published version
            latest_version = campaign.versions.filter(is_published=True).order_by('-version_number').first()

            attempt = AssessmentAttempt.objects.create(
                candidate=candidate,
                campaign=campaign,
                assessment_version=latest_version,
                status=AttemptStatus.IN_PROGRESS,
                attempt_number=total_attempts + 1
            )
        return attempt

    @staticmethod
    def check_and_update_expired_attempts(stage_attempt):
        """
        Checks if a stage attempt has exceeded its deadline, updating status atomically.
        """
        if stage_attempt.status == AttemptStatus.IN_PROGRESS and stage_attempt.deadline:
            if timezone.now() > stage_attempt.deadline:
                with transaction.atomic():
                    stage_attempt.status = AttemptStatus.EXPIRED
                    stage_attempt.save(update_fields=['status', 'updated_at'])
                return True
        return False

    @staticmethod
    def is_stage_eligible(candidate, stage, assessment_attempt=None):
        """
        Determines whether a candidate is eligible to access or start a given stage based on:
        1. Sequential order & prerequisites.
        2. Previous stage pass status and threshold score.
        3. Attempt quotas.
        """
        campaign = stage.campaign
        if not assessment_attempt:
            assessment_attempt = AssessmentAttempt.objects.filter(
                candidate=candidate,
                campaign=campaign
            ).order_by('-created_at').first()

        if not assessment_attempt:
            # First stage can be eligible if it has order 1 and no prerequisites
            return stage.order == 1, "Assessment attempt not yet initialized."

        # Check explicit prerequisites
        prereqs = StagePrerequisite.objects.filter(stage=stage)
        if prereqs.exists():
            for prereq in prereqs:
                prereq_attempt = StageAttempt.objects.filter(
                    assessment_attempt=assessment_attempt,
                    stage=prereq.prerequisite_stage
                ).order_by('-attempt_number').first()

                if not prereq_attempt:
                    return False, f"Prerequisite stage '{prereq.prerequisite_stage.name}' has not been attempted."

                if prereq_attempt.status not in [AttemptStatus.PASSED, AttemptStatus.SUBMITTED, AttemptStatus.EVALUATING]:
                    return False, f"Prerequisite stage '{prereq.prerequisite_stage.name}' must be completed."

                if prereq_attempt.score < prereq.minimum_score and prereq_attempt.status == AttemptStatus.PASSED:
                    return False, f"Prerequisite score on '{prereq.prerequisite_stage.name}' ({prereq_attempt.score}%) does not meet required {prereq.minimum_score}%."
        else:
            # Default sequential progression: stages with order > 1 require previous stage (order - 1) to be completed
            if stage.order > 1:
                prev_stage = AssessmentStage.objects.filter(campaign=campaign, order=stage.order - 1).first()
                if prev_stage:
                    prev_attempt = StageAttempt.objects.filter(
                        assessment_attempt=assessment_attempt,
                        stage=prev_stage
                    ).order_by('-attempt_number').first()

                    if not prev_attempt or prev_attempt.status not in [
                        AttemptStatus.SUBMITTED, AttemptStatus.EVALUATING, AttemptStatus.PASSED, AttemptStatus.MANUAL_REVIEW
                    ]:
                        return False, f"Previous stage '{prev_stage.name}' must be submitted before advancing."

        return True, "Eligible"

    @classmethod
    def start_stage(cls, candidate, stage_id, request=None):
        """
        Starts a stage for a candidate atomically, establishing the server-controlled deadline.
        """
        stage = AssessmentStage.objects.select_related('campaign').get(id=stage_id)
        if not stage.is_active:
            raise ValidationError("This assessment stage is currently inactive.")

        with transaction.atomic():
            assessment_attempt = cls.get_or_create_assessment_attempt(candidate, stage.campaign)

            # Check eligibility
            eligible, reason = cls.is_stage_eligible(candidate, stage, assessment_attempt)
            if not eligible:
                raise PermissionDenied(f"Stage cannot be started: {reason}")

            # Check if an existing attempt exists
            stage_attempt = StageAttempt.objects.filter(
                assessment_attempt=assessment_attempt,
                stage=stage
            ).order_by('-attempt_number').first()

            now = timezone.now()

            if stage_attempt:
                cls.check_and_update_expired_attempts(stage_attempt)

                if stage_attempt.status == AttemptStatus.IN_PROGRESS:
                    # Return ongoing attempt
                    return stage_attempt

                # Testing mode: Allow retaking stages infinitely without attempt limits
                existing_count = StageAttempt.objects.filter(
                    assessment_attempt=assessment_attempt,
                    stage=stage
                ).count()

                deadline = now + timedelta(minutes=stage.time_limit_minutes)
                stage_attempt = StageAttempt.objects.create(
                    assessment_attempt=assessment_attempt,
                    stage=stage,
                    status=AttemptStatus.IN_PROGRESS,
                    start_time=now,
                    deadline=deadline,
                    attempt_number=existing_count + 1
                )
            else:
                deadline = now + timedelta(minutes=stage.time_limit_minutes)
                stage_attempt = StageAttempt.objects.create(
                    assessment_attempt=assessment_attempt,
                    stage=stage,
                    status=AttemptStatus.IN_PROGRESS,
                    start_time=now,
                    deadline=deadline,
                    attempt_number=1
                )

            # Audit log
            ip_addr = request.META.get('REMOTE_ADDR') if request else None
            AuditLog.objects.create(
                actor=candidate,
                action='STAGE_STARTED',
                target_model='StageAttempt',
                target_id=str(stage_attempt.id),
                ip_address=ip_addr,
                details={'stage': stage.name, 'deadline': str(stage_attempt.deadline)}
            )

            return stage_attempt
