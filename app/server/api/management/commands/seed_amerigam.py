from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from api.models import (
    UserRole,
    UserProfile,
    CandidateProfile,
    ReviewerProfile,
    AssessmentCampaign,
    AssessmentVersion,
    AssessmentStage,
    StageType,
    StagePrerequisite,
    Question,
    QuestionType,
    DifficultyLevel,
    StageQuestion,
    Challenge,
    TestCase,
    EvaluationRubric,
    RubricCriterion,
)

class Command(BaseCommand):
    help = 'Seeds initial demonstration data for Amerigam Engineering Challenge'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Amerigam Engineering Challenge data...")

        # 1. Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@amerigam.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('AmerigamAdmin2026!')
            admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': UserRole.ADMIN})

        # 2. Reviewer User
        reviewer_user, created = User.objects.get_or_create(
            username='reviewer1',
            defaults={'email': 'reviewer@amerigam.com'}
        )
        if created:
            reviewer_user.set_password('ReviewerPass2026!')
            reviewer_user.save()
        UserProfile.objects.get_or_create(user=reviewer_user, defaults={'role': UserRole.REVIEWER})
        ReviewerProfile.objects.get_or_create(
            user=reviewer_user,
            defaults={'specialization': 'System Architecture & Code Quality'}
        )

        # 3. Candidate User
        cand_user, created = User.objects.get_or_create(
            username='candidate1',
            defaults={'email': 'candidate@amerigam.com'}
        )
        if created:
            cand_user.set_password('CandidatePass2026!')
            cand_user.save()
        UserProfile.objects.get_or_create(user=cand_user, defaults={'role': UserRole.CANDIDATE})
        CandidateProfile.objects.get_or_create(
            user=cand_user,
            defaults={'technical_track': 'fullstack', 'years_of_experience': 4.0}
        )

        # 4. Assessment Campaign
        campaign, _ = AssessmentCampaign.objects.get_or_create(
            slug='amerigam-challenge-2026',
            defaults={
                'title': 'Amerigam Engineering Challenge 2026',
                'description': 'Assessment to evaluate and select the top 4 software engineers for Amerigam.',
                'pass_threshold_score': 70.0,
                'created_by': admin_user,
                'is_active': True,
            }
        )

        # 5. Four Stages
        # Stage 1: Engineering Fundamentals
        stage_1, _ = AssessmentStage.objects.get_or_create(
            campaign=campaign,
            order=1,
            defaults={
                'stage_type': StageType.STAGE_1_FUNDAMENTALS,
                'name': 'Stage 1: Engineering Fundamentals',
                'description': 'Assess problem decomposition, complexity analysis, logic, and debugging foundations.',
                'time_limit_minutes': 45,
                'pass_threshold_score': 70.0,
                'requires_manual_review': False,
            }
        )

        # Stage 2: Hands-on Coding
        stage_2, _ = AssessmentStage.objects.get_or_create(
            campaign=campaign,
            order=2,
            defaults={
                'stage_type': StageType.STAGE_2_CODING,
                'name': 'Stage 2: Hands-on Coding',
                'description': 'Solve core algorithmic and data structure problems in an interactive browser environment.',
                'time_limit_minutes': 60,
                'pass_threshold_score': 70.0,
                'requires_manual_review': False,
            }
        )

        # Stage 3: Engineering Challenges
        stage_3, _ = AssessmentStage.objects.get_or_create(
            campaign=campaign,
            order=3,
            defaults={
                'stage_type': StageType.STAGE_3_CHALLENGES,
                'name': 'Stage 3: Engineering Challenges',
                'description': 'Domain-specific engineering challenges covering backend APIs, SQL data modeling, and security.',
                'time_limit_minutes': 90,
                'pass_threshold_score': 70.0,
                'requires_manual_review': True,
            }
        )

        # Stage 4: Engineering Reasoning
        stage_4, _ = AssessmentStage.objects.get_or_create(
            campaign=campaign,
            order=4,
            defaults={
                'stage_type': StageType.STAGE_4_REASONING,
                'name': 'Stage 4: Engineering Reasoning & Architecture',
                'description': 'Deep-dive architectural scenarios, trade-offs, incident mitigation, and design decisions.',
                'time_limit_minutes': 60,
                'pass_threshold_score': 70.0,
                'requires_manual_review': True,
            }
        )

        # Prerequisites
        StagePrerequisite.objects.get_or_create(stage=stage_2, prerequisite_stage=stage_1, defaults={'minimum_score': 70.0})
        StagePrerequisite.objects.get_or_create(stage=stage_3, prerequisite_stage=stage_2, defaults={'minimum_score': 70.0})
        StagePrerequisite.objects.get_or_create(stage=stage_4, prerequisite_stage=stage_3, defaults={'minimum_score': 70.0})

        # 6. Sample Questions
        # Q1: MCQ for Stage 1
        q1, _ = Question.objects.get_or_create(
            title='Hash Table Average vs Worst-Case Lookup',
            defaults={
                'prompt': 'What is the average and worst-case time complexity for lookups in a hash table with separate chaining?',
                'question_type': QuestionType.MCQ,
                'difficulty': DifficultyLevel.EASY,
                'category': 'DSA & Complexity',
                'points': 10,
                'mcq_options': [
                    {'id': 'A', 'text': 'Average: O(1), Worst: O(n)', 'is_correct': True},
                    {'id': 'B', 'text': 'Average: O(log n), Worst: O(n)', 'is_correct': False},
                    {'id': 'C', 'text': 'Average: O(1), Worst: O(log n)', 'is_correct': False},
                    {'id': 'D', 'text': 'Average: O(n), Worst: O(n^2)', 'is_correct': False},
                ]
            }
        )
        StageQuestion.objects.get_or_create(stage=stage_1, question=q1, defaults={'order': 1})

        # Q2: Coding Challenge for Stage 2
        q2, _ = Question.objects.get_or_create(
            title='Two Sum Algorithm',
            defaults={
                'prompt': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\nAssume each input has exactly one solution, and do not use the same element twice.',
                'question_type': QuestionType.DSA_CODING,
                'difficulty': DifficultyLevel.MEDIUM,
                'category': 'Algorithms & Hash Maps',
                'points': 25,
                'constraints': '2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\nOnly one valid answer exists.',
                'time_expected_minutes': 25,
            }
        )
        StageQuestion.objects.get_or_create(stage=stage_2, question=q2, defaults={'order': 1})

        challenge2, _ = Challenge.objects.get_or_create(
            question=q2,
            defaults={
                'allowed_languages': ['python', 'javascript', 'typescript'],
                'starter_code': {
                    'python': 'def two_sum(nums, target):\n    # Write your solution here\n    pass',
                    'javascript': 'function twoSum(nums, target) {\n    // Write your solution here\n}',
                },
                'time_limit_seconds': 2.0,
                'memory_limit_mb': 128,
                'run_quota_per_attempt': 15,
            }
        )

        TestCase.objects.get_or_create(
            challenge=challenge2,
            order=1,
            defaults={
                'input_data': '[2, 7, 11, 15]\n9',
                'expected_output': '[0, 1]',
                'is_sample': True,
                'weight': 1.0,
                'explanation': 'nums[0] + nums[1] = 2 + 7 = 9'
            }
        )
        TestCase.objects.get_or_create(
            challenge=challenge2,
            order=2,
            defaults={
                'input_data': '[3, 2, 4]\n6',
                'expected_output': '[1, 2]',
                'is_sample': False,
                'weight': 1.0,
            }
        )

        # Q3: Engineering Reasoning for Stage 4
        q4, _ = Question.objects.get_or_create(
            title='High-Concurrency Distributed Idempotency',
            defaults={
                'prompt': 'Design an idempotent payment processing workflow that handles network timeouts, duplicate webhook deliveries, and database lock contention under 10,000 requests per second. Explain your architectural choices, failure domains, and recovery strategies.',
                'question_type': QuestionType.SYSTEM_DESIGN,
                'difficulty': DifficultyLevel.HARD,
                'category': 'Distributed Systems & Architecture',
                'points': 40,
                'time_expected_minutes': 45,
            }
        )
        StageQuestion.objects.get_or_create(stage=stage_4, question=q4, defaults={'order': 1})

        # 7. Evaluation Rubrics for Stage 4
        rubric, _ = EvaluationRubric.objects.get_or_create(
            stage=stage_4,
            defaults={'name': 'Stage 4 Architecture & Reasoning Rubric'}
        )
        criteria_defs = [
            ("Correctness and edge cases", 25.0, 1),
            ("Problem-solving and reasoning", 20.0, 2),
            ("Code quality and maintainability", 15.0, 3),
            ("Testing and debugging", 15.0, 4),
            ("Security and reliability", 10.0, 5),
            ("Architecture and system design", 15.0, 6),
        ]
        for name, weight, ord_num in criteria_defs:
            RubricCriterion.objects.get_or_create(
                rubric=rubric,
                name=name,
                defaults={'weight_percent': weight, 'max_points': 10.0, 'order': ord_num}
            )

        # 8. Published Version 1 Snapshot
        AssessmentVersion.objects.get_or_create(
            campaign=campaign,
            version_number=1,
            defaults={
                'changelog': 'Initial published assessment configuration for 2026',
                'is_published': True,
                'published_at': timezone.now(),
                'configuration_snapshot': {
                    'title': campaign.title,
                    'stages_count': 4,
                    'pass_threshold': campaign.pass_threshold_score,
                }
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Amerigam Engineering Challenge 2026!"))
        self.stdout.write("Credentials created:")
        self.stdout.write("  Admin:     admin / AmerigamAdmin2026!")
        self.stdout.write("  Reviewer:  reviewer1 / ReviewerPass2026!")
        self.stdout.write("  Candidate: candidate1 / CandidatePass2026!")
