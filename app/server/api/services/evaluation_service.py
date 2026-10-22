from django.utils import timezone
from django.db import transaction
from api.models import (
    StageAttempt,
    Submission,
    StageEvaluation,
    CriterionScore,
    EvaluationRubric,
    RubricCriterion,
    EvaluationStatus,
    AttemptStatus,
    QuestionType,
    AssessmentAttempt,
)
from .execution_service import ExecutionService

DEFAULT_RUBRIC_CRITERIA = [
    {"name": "Correctness and edge cases", "weight_percent": 25.0, "max_points": 10.0, "order": 1},
    {"name": "Problem-solving and reasoning", "weight_percent": 20.0, "max_points": 10.0, "order": 2},
    {"name": "Code quality and maintainability", "weight_percent": 15.0, "max_points": 10.0, "order": 3},
    {"name": "Testing and debugging", "weight_percent": 15.0, "max_points": 10.0, "order": 4},
    {"name": "Security and reliability", "weight_percent": 10.0, "max_points": 10.0, "order": 5},
    {"name": "Architecture and system design", "weight_percent": 15.0, "max_points": 10.0, "order": 6},
]

class EvaluationService:
    @staticmethod
    def ensure_default_rubric(stage):
        """
        Ensures a rubric with standard criteria exists for a stage.
        """
        rubric, created = EvaluationRubric.objects.get_or_create(
            stage=stage,
            defaults={'name': f"Rubric for {stage.name}", 'description': 'Standard engineering evaluation rubric'}
        )
        if created or not rubric.criteria.exists():
            for crit in DEFAULT_RUBRIC_CRITERIA:
                RubricCriterion.objects.create(
                    rubric=rubric,
                    name=crit['name'],
                    weight_percent=crit['weight_percent'],
                    max_points=crit['max_points'],
                    order=crit['order'],
                )
        return rubric

    @classmethod
    def evaluate_stage_attempt(cls, stage_attempt: StageAttempt):
        """
        Evaluates objective components (MCQ and code executions) for a submitted stage attempt.
        """
        submissions = Submission.objects.filter(stage_attempt=stage_attempt).select_related('question')
        total_points_possible = 0.0
        total_points_earned = 0.0

        for sub in submissions:
            q = sub.question
            points = q.points or 10.0
            total_points_possible += points

            if q.question_type == QuestionType.MCQ:
                # Calculate MCQ score
                correct_opts = {opt.get('id') for opt in (q.mcq_options or []) if opt.get('is_correct')}
                selected_opts = set(sub.selected_options or [])
                if correct_opts and correct_opts == selected_opts:
                    sub.score = points
                else:
                    sub.score = 0.0
                sub.evaluated = True
                sub.save(update_fields=['score', 'evaluated'])
                total_points_earned += sub.score

            elif hasattr(q, 'challenge') and sub.content:
                # Coding Challenge execution evaluation (using full test set including hidden tests)
                challenge = q.challenge
                try:
                    result = ExecutionService.execute_challenge(
                        stage_attempt=stage_attempt,
                        challenge=challenge,
                        language=sub.language or 'python',
                        source_code=sub.content,
                        is_sample_run=False,
                        submission=sub,
                    )
                    earned = (result.score_earned / 100.0) * points
                    sub.score = earned
                except Exception:
                    sub.score = 0.0
                sub.evaluated = True
                sub.save(update_fields=['score', 'evaluated'])
                total_points_earned += sub.score

            elif q.question_type in [QuestionType.SHORT_ANSWER, QuestionType.LONG_REASONING, QuestionType.SYSTEM_DESIGN]:
                # Written responses will be reviewed manually
                sub.evaluated = False
                sub.save(update_fields=['evaluated'])

        # Percentage score for automated components
        automated_percentage = (total_points_earned / total_points_possible * 100.0) if total_points_possible > 0 else 0.0

        # Create or update StageEvaluation
        evaluation, _ = StageEvaluation.objects.get_or_create(
            stage_attempt=stage_attempt,
            defaults={
                'automated_score': automated_percentage,
                'total_score': automated_percentage,
                'status': EvaluationStatus.PENDING if stage_attempt.stage.requires_manual_review else EvaluationStatus.COMPLETED,
            }
        )
        evaluation.automated_score = automated_percentage

        if not stage_attempt.stage.requires_manual_review:
            # Stage does not require manual review, decide pass/fail directly
            evaluation.total_score = automated_percentage
            evaluation.is_passed = automated_percentage >= stage_attempt.stage.pass_threshold_score
            evaluation.status = EvaluationStatus.COMPLETED
            evaluation.evaluated_at = timezone.now()
            evaluation.save()

            stage_attempt.score = automated_percentage
            stage_attempt.passed = evaluation.is_passed
            stage_attempt.status = AttemptStatus.PASSED if evaluation.is_passed else AttemptStatus.FAILED
            stage_attempt.save(update_fields=['score', 'passed', 'status', 'updated_at'])

            # Check if all stages for assessment are completed
            cls.check_and_update_assessment_attempt(stage_attempt.assessment_attempt)
        else:
            evaluation.status = EvaluationStatus.IN_REVIEW
            evaluation.save(update_fields=['automated_score', 'status'])
            stage_attempt.status = AttemptStatus.MANUAL_REVIEW
            stage_attempt.save(update_fields=['status', 'updated_at'])

        return evaluation

    @classmethod
    def record_manual_review(cls, stage_evaluation: StageEvaluation, reviewer, criteria_scores: list, reviewer_notes: str = ""):
        """
        Records human reviewer evaluation across rubric criteria.
        """
        with transaction.atomic():
            total_rubric_weight = 0.0
            weighted_score = 0.0

            for item in criteria_scores:
                criterion_id = item.get('criterion_id')
                score_val = float(item.get('score', 0.0))
                comments = item.get('comments', '')

                criterion = RubricCriterion.objects.get(id=criterion_id)
                # Cap score at criterion.max_points
                score_capped = min(max(score_val, 0.0), criterion.max_points)

                CriterionScore.objects.update_or_create(
                    stage_evaluation=stage_evaluation,
                    criterion=criterion,
                    defaults={'score': score_capped, 'comments': comments}
                )

                # Weight contribution
                normalized_score = (score_capped / criterion.max_points) * 100.0
                weighted_score += (normalized_score * (criterion.weight_percent / 100.0))
                total_rubric_weight += criterion.weight_percent

            # Normalize if weights don't equal 100 exactly
            if total_rubric_weight > 0:
                manual_percentage = (weighted_score / total_rubric_weight) * 100.0
            else:
                manual_percentage = weighted_score

            # Blend automated (40%) and manual (60%) if automated tests exist, or 100% manual
            if stage_evaluation.automated_score > 0:
                total_final = (stage_evaluation.automated_score * 0.4) + (manual_percentage * 0.6)
            else:
                total_final = manual_percentage

            stage = stage_evaluation.stage_attempt.stage
            is_passed = total_final >= stage.pass_threshold_score

            stage_evaluation.evaluator = reviewer
            stage_evaluation.manual_score = manual_percentage
            stage_evaluation.total_score = total_final
            stage_evaluation.is_passed = is_passed
            stage_evaluation.reviewer_notes = reviewer_notes
            stage_evaluation.status = EvaluationStatus.COMPLETED
            stage_evaluation.evaluated_at = timezone.now()
            stage_evaluation.save()

            # Update StageAttempt
            st = stage_evaluation.stage_attempt
            st.score = total_final
            st.passed = is_passed
            st.status = AttemptStatus.PASSED if is_passed else AttemptStatus.FAILED
            st.save(update_fields=['score', 'passed', 'status', 'updated_at'])

            cls.check_and_update_assessment_attempt(st.assessment_attempt)

            return stage_evaluation

    @staticmethod
    def check_and_update_assessment_attempt(assessment_attempt: AssessmentAttempt):
        """
        Updates overall assessment attempt status when all stages are resolved.
        """
        stages = assessment_attempt.campaign.stages.filter(is_active=True)
        stage_attempts = StageAttempt.objects.filter(assessment_attempt=assessment_attempt)

        # Check if all stages have been completed (passed/failed)
        completed_attempts = stage_attempts.filter(status__in=[AttemptStatus.PASSED, AttemptStatus.FAILED])
        if stages.count() > 0 and completed_attempts.count() >= stages.count():
            # Average score across all stages
            avg_score = sum(st.score for st in completed_attempts) / completed_attempts.count()
            all_passed = all(st.passed for st in completed_attempts)

            assessment_attempt.final_score = avg_score
            assessment_attempt.passed = all_passed and (avg_score >= assessment_attempt.campaign.pass_threshold_score)
            assessment_attempt.status = AttemptStatus.PASSED if assessment_attempt.passed else AttemptStatus.FAILED
            assessment_attempt.submitted_at = timezone.now()
            assessment_attempt.save(update_fields=['final_score', 'passed', 'status', 'submitted_at', 'updated_at'])
