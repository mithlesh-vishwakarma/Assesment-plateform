from django.db import models
from django.contrib.auth.models import User

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    REVIEWER = 'REVIEWER', 'Reviewer'
    CANDIDATE = 'CANDIDATE', 'Candidate'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CANDIDATE)
    phone = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.user.is_superuser

    @property
    def is_reviewer(self):
        return self.role == UserRole.REVIEWER

    @property
    def is_candidate(self):
        return self.role == UserRole.CANDIDATE


class CandidateStatus(models.TextChoices):
    INVITED = 'INVITED', 'Invited'
    ACTIVE = 'ACTIVE', 'Active'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    EVALUATING = 'EVALUATING', 'Evaluating'
    SELECTED = 'SELECTED', 'Selected'
    WAITLISTED = 'WAITLISTED', 'Waitlisted'
    REJECTED = 'REJECTED', 'Rejected'
    WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    technical_track = models.CharField(max_length=100, default='fullstack')
    years_of_experience = models.FloatField(default=0.0)
    resume_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=CandidateStatus.choices, default=CandidateStatus.ACTIVE)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Candidate: {self.user.username} [{self.technical_track}]"


class ReviewerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reviewer_profile')
    specialization = models.CharField(max_length=150, default='General Engineering')
    max_assigned_candidates = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reviewer: {self.user.username} [{self.specialization}]"
