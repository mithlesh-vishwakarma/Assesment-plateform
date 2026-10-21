from django.db import models
from .submissions import Submission, StageAttempt
from .questions import Challenge

class JobStatus(models.TextChoices):
    QUEUED = 'QUEUED', 'Queued'
    RUNNING = 'RUNNING', 'Running'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    TIMED_OUT = 'TIMED_OUT', 'Timed Out'


class ExecutionJob(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.SET_NULL, null=True, blank=True, related_name='execution_jobs')
    stage_attempt = models.ForeignKey(StageAttempt, on_delete=models.CASCADE, related_name='execution_jobs')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='execution_jobs')
    is_sample_run = models.BooleanField(default=True)  # True = sample tests; False = all (hidden included)
    language = models.CharField(max_length=50)
    source_code = models.TextField()
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.QUEUED)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        kind = "Sample Run" if self.is_sample_run else "Evaluation Run"
        return f"Job #{self.id} [{kind}] - {self.language} ({self.status})"


class ExecutionResult(models.Model):
    job = models.OneToOneField(ExecutionJob, on_delete=models.CASCADE, related_name='result')
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    compile_output = models.TextField(blank=True)
    exit_code = models.IntegerField(default=0)
    execution_time_ms = models.FloatField(default=0.0)
    memory_used_kb = models.IntegerField(default=0)
    status_message = models.CharField(max_length=255, default='Success')
    passed_test_cases_count = models.IntegerField(default=0)
    total_test_cases_count = models.IntegerField(default=0)
    score_earned = models.FloatField(default=0.0)
    # Sanitized list of test case runs (safe for candidate view, omitting private hidden test inputs/outputs)
    test_results_sanitized = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for Job #{self.job_id}: {self.passed_test_cases_count}/{self.total_test_cases_count} passed"
