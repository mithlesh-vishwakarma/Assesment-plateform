from django.db import models
from django.contrib.auth.models import User
from .submissions import StageAttempt
from .assessments import AssessmentCampaign

class IntegrityEventType(models.TextChoices):
    BROWSER_BLUR = 'BROWSER_BLUR', 'Window/Tab Lost Focus'
    TAB_SWITCH = 'TAB_SWITCH', 'Switched Browser Tab'
    COPY_PASTE = 'COPY_PASTE', 'Large Clipboard Paste'
    DEVTOOLS_OPENED = 'DEVTOOLS_OPENED', 'Developer Tools Opened'
    FULLSCREEN_EXIT = 'FULLSCREEN_EXIT', 'Exited Fullscreen Mode'
    MULTIPLE_IPS = 'MULTIPLE_IPS', 'Session Active from Multiple IPs'
    SUSPICIOUS_PASTE = 'SUSPICIOUS_PASTE', 'Suspicious Code Insertion'


class IntegrityEvent(models.Model):
    stage_attempt = models.ForeignKey(StageAttempt, on_delete=models.CASCADE, related_name='integrity_events')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integrity_events')
    event_type = models.CharField(max_length=40, choices=IntegrityEventType.choices)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.event_type}] {self.candidate.username} at {self.timestamp}"


class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        actor_name = self.actor.username if self.actor else "System"
        return f"{self.timestamp} | {actor_name} -> {self.action} on {self.target_model}:{self.target_id}"


class SelectionDecision(models.TextChoices):
    SELECTED = 'SELECTED', 'Selected (Top 4 Candidate)'
    WAITLISTED = 'WAITLISTED', 'Waitlisted'
    REJECTED = 'REJECTED', 'Rejected'
    PENDING = 'PENDING', 'Pending Decision'


class CandidateSelection(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='selection_decisions')
    campaign = models.ForeignKey(AssessmentCampaign, on_delete=models.CASCADE, related_name='selections')
    decision = models.CharField(max_length=20, choices=SelectionDecision.choices, default=SelectionDecision.PENDING)
    ranking = models.PositiveIntegerField(null=True, blank=True)  # e.g. 1, 2, 3, 4
    notes = models.TextField(blank=True)
    decided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='decided_selections')
    decided_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('candidate', 'campaign')
        ordering = ['ranking', '-decided_at']

    def __str__(self):
        rank_str = f"Rank #{self.ranking}" if self.ranking else "No Rank"
        return f"{self.candidate.username} - {self.decision} ({rank_str})"


class ExportType(models.TextChoices):
    CSV = 'CSV', 'CSV Export'
    JSON = 'JSON', 'JSON Export'
    SUMMARY = 'SUMMARY', 'Executive Summary'


class ReportExport(models.Model):
    campaign = models.ForeignKey(AssessmentCampaign, on_delete=models.CASCADE, related_name='reports')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_exports')
    export_type = models.CharField(max_length=20, choices=ExportType.choices, default=ExportType.CSV)
    status = models.CharField(max_length=20, default='COMPLETED')
    result_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.export_type} for {self.campaign.title} by {self.requested_by.username}"
