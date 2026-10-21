from django.db import models
from django.contrib.auth.models import User

# Existing Assessment model preserved for full backward compatibility
class Assessment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'api_assessment'

    def __str__(self):
        return self.title


class AssessmentCampaign(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    legacy_assessment = models.ForeignKey(
        Assessment, on_delete=models.SET_NULL, null=True, blank=True, related_name='campaigns'
    )
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    max_attempts_per_candidate = models.PositiveIntegerField(default=1)
    pass_threshold_score = models.FloatField(default=70.0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class AssessmentVersion(models.Model):
    campaign = models.ForeignKey(AssessmentCampaign, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField(default=1)
    changelog = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    configuration_snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('campaign', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        status = "Published" if self.is_published else "Draft"
        return f"{self.campaign.title} v{self.version_number} ({status})"


class StageType(models.TextChoices):
    STAGE_1_FUNDAMENTALS = 'STAGE_1_FUNDAMENTALS', 'Stage 1: Engineering Fundamentals'
    STAGE_2_CODING = 'STAGE_2_CODING', 'Stage 2: Hands-on Coding'
    STAGE_3_CHALLENGES = 'STAGE_3_CHALLENGES', 'Stage 3: Engineering Challenges'
    STAGE_4_REASONING = 'STAGE_4_REASONING', 'Stage 4: Engineering Reasoning'


class AssessmentStage(models.Model):
    campaign = models.ForeignKey(AssessmentCampaign, on_delete=models.CASCADE, related_name='stages')
    version = models.ForeignKey(AssessmentVersion, on_delete=models.SET_NULL, null=True, blank=True, related_name='stages')
    stage_type = models.CharField(max_length=50, choices=StageType.choices, default=StageType.STAGE_1_FUNDAMENTALS)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    time_limit_minutes = models.PositiveIntegerField(default=60)
    pass_threshold_score = models.FloatField(default=70.0)
    requires_manual_review = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    max_attempts = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('campaign', 'order')
        ordering = ['order']

    def __str__(self):
        return f"Stage {self.order}: {self.name} ({self.campaign.title})"


class StagePrerequisite(models.Model):
    stage = models.ForeignKey(AssessmentStage, on_delete=models.CASCADE, related_name='prerequisites')
    prerequisite_stage = models.ForeignKey(AssessmentStage, on_delete=models.CASCADE, related_name='dependent_stages')
    minimum_score = models.FloatField(default=70.0)

    class Meta:
        unique_together = ('stage', 'prerequisite_stage')

    def __str__(self):
        return f"{self.stage.name} requires {self.prerequisite_stage.name} (>= {self.minimum_score}%)"
