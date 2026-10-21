from django.db import models
from django.contrib.auth.models import User
from .assessments import AssessmentStage
from .questions import Question
from .submissions import StageAttempt

class EvaluationRubric(models.Model):
    stage = models.ForeignKey(AssessmentStage, on_delete=models.CASCADE, null=True, blank=True, related_name='rubrics')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True, related_name='rubrics')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RubricCriterion(models.Model):
    rubric = models.ForeignKey(EvaluationRubric, on_delete=models.CASCADE, related_name='criteria')
    name = models.CharField(max_length=150)  # e.g., "Correctness and edge cases", "Problem-solving and reasoning"
    weight_percent = models.FloatField(default=20.0)  # e.g. 25.0
    max_points = models.FloatField(default=10.0)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.weight_percent}%)"


class EvaluationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    IN_REVIEW = 'IN_REVIEW', 'In Review'
    COMPLETED = 'COMPLETED', 'Completed'


class StageEvaluation(models.Model):
    stage_attempt = models.OneToOneField(StageAttempt, on_delete=models.CASCADE, related_name='evaluation')
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations')
    status = models.CharField(max_length=20, choices=EvaluationStatus.choices, default=EvaluationStatus.PENDING)
    automated_score = models.FloatField(default=0.0)
    manual_score = models.FloatField(default=0.0)
    total_score = models.FloatField(default=0.0)
    is_passed = models.BooleanField(default=False)
    reviewer_notes = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evaluation for {self.stage_attempt} - Score: {self.total_score} ({self.status})"


class CriterionScore(models.Model):
    stage_evaluation = models.ForeignKey(StageEvaluation, on_delete=models.CASCADE, related_name='criterion_scores')
    criterion = models.ForeignKey(RubricCriterion, on_delete=models.CASCADE, related_name='criterion_scores')
    score = models.FloatField(default=0.0)
    comments = models.TextField(blank=True)

    class Meta:
        unique_together = ('stage_evaluation', 'criterion')

    def __str__(self):
        return f"{self.criterion.name}: {self.score}/{self.criterion.max_points}"


class ReviewerAssignmentStatus(models.TextChoices):
    ASSIGNED = 'ASSIGNED', 'Assigned'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'


class ReviewerAssignment(models.Model):
    stage_attempt = models.ForeignKey(StageAttempt, on_delete=models.CASCADE, related_name='reviewer_assignments')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_reviews')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_by_reviews')
    status = models.CharField(max_length=20, choices=ReviewerAssignmentStatus.choices, default=ReviewerAssignmentStatus.ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('stage_attempt', 'reviewer')
        ordering = ['-assigned_at']

    def __str__(self):
        return f"Reviewer {self.reviewer.username} -> {self.stage_attempt}"
