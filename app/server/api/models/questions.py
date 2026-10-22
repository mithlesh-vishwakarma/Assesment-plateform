from django.db import models
from .assessments import AssessmentStage

class QuestionType(models.TextChoices):
    MCQ = 'MCQ', 'Multiple Choice Question'
    SHORT_ANSWER = 'SHORT_ANSWER', 'Short Answer'
    LONG_REASONING = 'LONG_REASONING', 'Long-form Reasoning'
    DSA_CODING = 'DSA_CODING', 'DSA Coding Problem'
    DEBUGGING = 'DEBUGGING', 'Debugging Task'
    CODE_REVIEW = 'CODE_REVIEW', 'Code Review Task'
    FRONTEND = 'FRONTEND', 'Frontend Implementation Challenge'
    BACKEND = 'BACKEND', 'Backend & API Challenge'
    DATABASE_SQL = 'DATABASE_SQL', 'Database & SQL Challenge'
    SECURITY = 'SECURITY', 'Application Security Challenge'
    MOBILE = 'MOBILE', 'Mobile Development Challenge'
    DEVOPS_TESTING = 'DEVOPS_TESTING', 'Testing & DevOps Challenge'
    SYSTEM_DESIGN = 'SYSTEM_DESIGN', 'System Design Scenario'


class DifficultyLevel(models.TextChoices):
    EASY = 'EASY', 'Easy'
    MEDIUM = 'MEDIUM', 'Medium'
    HARD = 'HARD', 'Hard'


class Question(models.Model):
    title = models.CharField(max_length=255)
    prompt = models.TextField()
    question_type = models.CharField(max_length=30, choices=QuestionType.choices, default=QuestionType.DSA_CODING)
    difficulty = models.CharField(max_length=10, choices=DifficultyLevel.choices, default=DifficultyLevel.MEDIUM)
    category = models.CharField(max_length=100, default='General Engineering')
    points = models.PositiveIntegerField(default=10)
    instructions = models.TextField(blank=True)
    constraints = models.TextField(blank=True)
    time_expected_minutes = models.PositiveIntegerField(default=15)
    tags = models.JSONField(default=list, blank=True)
    # For MCQ questions: [{"id": "A", "text": "...", "is_correct": bool}]
    mcq_options = models.JSONField(default=list, blank=True)
    rubric_guide = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.title} ({self.difficulty})"


class StageQuestion(models.Model):
    stage = models.ForeignKey(AssessmentStage, on_delete=models.CASCADE, related_name='stage_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='stage_questions')
    order = models.PositiveIntegerField(default=1)
    points_weight = models.FloatField(default=1.0)

    class Meta:
        unique_together = ('stage', 'question')
        ordering = ['order']

    def __str__(self):
        return f"{self.stage.name} - Q{self.order}: {self.question.title}"


class Challenge(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='challenge')
    allowed_languages = models.JSONField(default=list)  # e.g. ["python", "javascript", "typescript", "java", "cpp", "go"]
    starter_code = models.JSONField(default=dict)       # e.g. {"python": "def solution():\n    pass"}
    function_signature = models.CharField(max_length=255, blank=True)
    time_limit_seconds = models.FloatField(default=2.0)
    memory_limit_mb = models.PositiveIntegerField(default=128)
    run_quota_per_attempt = models.PositiveIntegerField(default=20)
    expected_output_format = models.TextField(blank=True)

    def __str__(self):
        return f"Challenge for {self.question.title}"


class TestCase(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)  # True = sample/public test, False = private hidden test!
    weight = models.FloatField(default=1.0)
    order = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        visibility = "Sample" if self.is_sample else "Hidden"
        return f"TestCase #{self.order} [{visibility}] for {self.challenge.question.title}"
