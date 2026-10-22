from django.db import models
from django.contrib.auth.models import User
from .assessments import AssessmentCampaign, AssessmentVersion, AssessmentStage
from .questions import Question

class AttemptStatus(models.TextChoices):
    NOT_STARTED = 'NOT_STARTED', 'Not Started'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    EVALUATING = 'EVALUATING', 'Evaluating'
    PASSED = 'PASSED', 'Passed'
    FAILED = 'FAILED', 'Failed'
    MANUAL_REVIEW = 'MANUAL_REVIEW', 'Manual Review Required'
    EXPIRED = 'EXPIRED', 'Expired'


class AssessmentAttempt(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_attempts')
    campaign = models.ForeignKey(AssessmentCampaign, on_delete=models.CASCADE, related_name='attempts')
    assessment_version = models.ForeignKey(AssessmentVersion, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=AttemptStatus.choices, default=AttemptStatus.IN_PROGRESS)
    start_time = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    final_score = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    attempt_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate.username} - {self.campaign.title} (Attempt #{self.attempt_number}: {self.status})"


class StageAttempt(models.Model):
    assessment_attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='stage_attempts')
    stage = models.ForeignKey(AssessmentStage, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=AttemptStatus.choices, default=AttemptStatus.NOT_STARTED)
    start_time = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    attempt_number = models.PositiveIntegerField(default=1)
    run_quota_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assessment_attempt', 'stage', 'attempt_number')
        ordering = ['stage__order']

    def __str__(self):
        return f"{self.assessment_attempt.candidate.username} - {self.stage.name} [{self.status}]"


class SubmissionType(models.TextChoices):
    CODE = 'CODE', 'Code Submission'
    WRITTEN = 'WRITTEN', 'Written Reasoning'
    MCQ = 'MCQ', 'Multiple Choice Response'


class Submission(models.Model):
    stage_attempt = models.ForeignKey(StageAttempt, on_delete=models.CASCADE, related_name='submissions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='submissions')
    submission_type = models.CharField(max_length=20, choices=SubmissionType.choices, default=SubmissionType.CODE)
    content = models.TextField(blank=True)
    selected_options = models.JSONField(default=list, blank=True)  # For MCQ
    language = models.CharField(max_length=50, blank=True)
    is_draft = models.BooleanField(default=True)  # True = draft autosave, False = final
    version_number = models.PositiveIntegerField(default=1)
    score = models.FloatField(default=0.0)
    evaluated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('stage_attempt', 'question')

    def __str__(self):
        status = "Draft" if self.is_draft else "Final"
        return f"{self.stage_attempt.assessment_attempt.candidate.username} - Q: {self.question.title} ({status})"


class SubmissionVersion(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    content = models.TextField()
    language = models.CharField(max_length=50, blank=True)
    selected_options = models.JSONField(default=list, blank=True)
    is_final = models.BooleanField(default=False)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']

    def __str__(self):
        return f"v{self.version_number} of {self.submission}"


class WrittenResponse(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='written_response')
    reasoning_text = models.TextField(blank=True)
    architectural_decisions = models.TextField(blank=True)
    trade_offs = models.TextField(blank=True)
    security_considerations = models.TextField(blank=True)
    assumptions = models.TextField(blank=True)
    incident_mitigation = models.TextField(blank=True)

    def __str__(self):
        return f"Written Response for {self.submission}"
