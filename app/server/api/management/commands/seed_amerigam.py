from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
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
    AssessmentAttempt,
    StageAttempt,
    AttemptStatus,
    Submission,
    SubmissionType,
    EvaluationRubric,
    RubricCriterion,
    StageEvaluation,
    CriterionScore,
    EvaluationStatus,
    ReviewerAssignment,
    ReviewerAssignmentStatus,
    IntegrityEvent,
    IntegrityEventType,
    CandidateSelection,
    SelectionDecision,
)

class Command(BaseCommand):
    help = 'Seeds initial realistic live data for Amerigam Engineering Challenge'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Amerigam Engineering Challenge live database...")

        # 1. Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@amerigam.com', 'first_name': 'Sarah', 'last_name': 'Connor', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('AmerigamAdmin2026!')
            admin_user.save()
        UserProfile.objects.update_or_create(user=admin_user, defaults={'role': UserRole.ADMIN, 'phone': '+1 555-0199', 'bio': 'Platform Lead'})

        # 2. Reviewer User
        reviewer_user, created = User.objects.get_or_create(
            username='reviewer1',
            defaults={'email': 'reviewer@amerigam.com', 'first_name': 'Vikram', 'last_name': 'Rao'}
        )
        if created:
            reviewer_user.set_password('ReviewerPass2026!')
            reviewer_user.save()
        UserProfile.objects.update_or_create(user=reviewer_user, defaults={'role': UserRole.REVIEWER, 'phone': '+1 555-0245', 'bio': 'Senior Staff Evaluator'})
        ReviewerProfile.objects.update_or_create(
            user=reviewer_user,
            defaults={'specialization': 'System Architecture & Code Quality'}
        )

        # 3. Candidate Users
        candidate_data = [
            {'username': 'aarav', 'name': 'Aarav Shah', 'email': 'aarav.shah@example.com', 'role': 'Frontend Engineer', 'status': 'Needs review', 'score': 88, 'track': 'frontend', 'exp': 3.5},
            {'username': 'meera', 'name': 'Meera Patel', 'email': 'meera.patel@example.com', 'role': 'Full Stack Engineer', 'status': 'Submitted', 'score': 82, 'track': 'fullstack', 'exp': 4.0},
            {'username': 'devm', 'name': 'Dev Mehta', 'email': 'dev.mehta@example.com', 'role': 'Backend Engineer', 'status': 'In progress', 'score': None, 'track': 'backend', 'exp': 2.5},
            {'username': 'riya', 'name': 'Riya Desai', 'email': 'riya.desai@example.com', 'role': 'Full Stack Engineer', 'status': 'Selected', 'score': 94, 'track': 'fullstack', 'exp': 5.0},
            {'username': 'kabir', 'name': 'Kabir Joshi', 'email': 'kabir.joshi@example.com', 'role': 'DevOps Engineer', 'status': 'Submitted', 'score': 76, 'track': 'devops', 'exp': 3.0},
            {'username': 'harshani', 'name': 'Harshani Patil', 'email': 'harshani@example.com', 'role': 'Full Stack Engineer', 'status': 'In progress', 'score': 86, 'track': 'fullstack', 'exp': 4.5},
        ]

        cand_users = {}
        for c in candidate_data:
            first, *last = c['name'].split()
            u, created = User.objects.get_or_create(
                username=c['username'],
                defaults={'email': c['email'], 'first_name': first, 'last_name': ' '.join(last)}
            )
            if created:
                u.set_password('CandidatePass2026!')
                u.save()
            UserProfile.objects.update_or_create(user=u, defaults={'role': UserRole.CANDIDATE})
            CandidateProfile.objects.update_or_create(
                user=u,
                defaults={'technical_track': c['track'], 'years_of_experience': c['exp']}
            )
            cand_users[c['username']] = u

        # 4. Campaigns
        campaign_main, _ = AssessmentCampaign.objects.get_or_create(
            slug='amerigam-challenge-2026',
            defaults={
                'title': 'Full Stack Engineer · October 2026',
                'description': 'Assessment to evaluate and select top software engineers for Amerigam product squads.',
                'pass_threshold_score': 70.0,
                'created_by': admin_user,
                'is_active': True,
            }
        )

        AssessmentCampaign.objects.get_or_create(
            slug='backend-engineer-q4',
            defaults={
                'title': 'Backend Engineer · Q4 intake',
                'description': 'Targeted backend and distributed systems assessment.',
                'pass_threshold_score': 75.0,
                'created_by': admin_user,
                'is_active': False,
            }
        )

        AssessmentCampaign.objects.get_or_create(
            slug='frontend-internship-sept',
            defaults={
                'title': 'Frontend Internship · September',
                'description': 'Foundational frontend web challenge completed in September.',
                'pass_threshold_score': 65.0,
                'created_by': admin_user,
                'is_active': False,
            }
        )

        # 5. Four Stages for Main Campaign
        stages_info = [
            (1, StageType.STAGE_1_FUNDAMENTALS, 'Engineering fundamentals', 'DSA & problem solving', 45, False),
            (2, StageType.STAGE_2_CODING, 'Build & ship', 'Practical coding challenge', 60, False),
            (3, StageType.STAGE_3_CHALLENGES, 'Systems thinking', 'Architecture & trade-offs', 35, True),
            (4, StageType.STAGE_4_REASONING, 'Engineering judgment', 'Written reasoning', 25, True),
        ]

        stage_objects = {}
        for ord_num, st_type, name, desc, duration, req_review in stages_info:
            st, _ = AssessmentStage.objects.update_or_create(
                campaign=campaign_main,
                order=ord_num,
                defaults={
                    'stage_type': st_type,
                    'name': name,
                    'description': desc,
                    'time_limit_minutes': duration,
                    'pass_threshold_score': 70.0,
                    'requires_manual_review': req_review,
                    'is_active': True,
                }
            )
            stage_objects[ord_num] = st

        # Prerequisites
        StagePrerequisite.objects.get_or_create(stage=stage_objects[2], prerequisite_stage=stage_objects[1], defaults={'minimum_score': 70.0})
        StagePrerequisite.objects.get_or_create(stage=stage_objects[3], prerequisite_stage=stage_objects[2], defaults={'minimum_score': 70.0})
        StagePrerequisite.objects.get_or_create(stage=stage_objects[4], prerequisite_stage=stage_objects[3], defaults={'minimum_score': 70.0})

        # 6. Questions
        # Stage 1: MCQ
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
        StageQuestion.objects.get_or_create(stage=stage_objects[1], question=q1, defaults={'order': 1})

        # Stage 2: Coding Challenge (Find a pair / Two sum)
        q2, _ = Question.objects.get_or_create(
            title='Find a pair',
            defaults={
                'prompt': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\nAssume each input has exactly one solution, and do not use the same element twice.',
                'question_type': QuestionType.DSA_CODING,
                'difficulty': DifficultyLevel.EASY,
                'category': 'Arrays & Hash Maps',
                'points': 25,
                'constraints': '2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\nOnly one valid answer exists.',
                'time_expected_minutes': 25,
                'instructions': 'Return indices [i, j] in any order.'
            }
        )
        StageQuestion.objects.get_or_create(stage=stage_objects[2], question=q2, defaults={'order': 1})

        challenge2, _ = Challenge.objects.get_or_create(
            question=q2,
            defaults={
                'allowed_languages': ['typescript', 'javascript', 'python', 'java'],
                'starter_code': {
                    'typescript': 'function findPair(nums: number[], target: number): number[] {\n  const seen = new Map<number, number>();\n  for (let i = 0; i < nums.length; i++) {\n    const comp = target - nums[i];\n    if (seen.has(comp)) return [seen.get(comp)!, i];\n    seen.set(nums[i], i);\n  }\n  return [];\n}',
                    'javascript': 'function findPair(nums, target) {\n  const seen = new Map();\n  for (let i = 0; i < nums.length; i++) {\n    const comp = target - nums[i];\n    if (seen.has(comp)) return [seen.get(comp), i];\n    seen.set(nums[i], i);\n  }\n  return [];\n}',
                    'python': 'def find_pair(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        comp = target - num\n        if comp in seen:\n            return [seen[comp], i]\n        seen[num] = i\n    return []',
                    'java': 'import java.util.*;\nclass Solution {\n    public int[] findPair(int[] nums, int target) {\n        Map<Integer, Integer> map = new HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            int comp = target - nums[i];\n            if (map.containsKey(comp)) return new int[]{map.get(comp), i};\n            map.put(nums[i], i);\n        }\n        return new int[]{};\n    }\n}'
                },
                'time_limit_seconds': 2.0,
                'memory_limit_mb': 128,
                'run_quota_per_attempt': 20,
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
                'is_sample': True,
                'weight': 1.0,
                'explanation': 'nums[1] + nums[2] = 2 + 4 = 6'
            }
        )
        TestCase.objects.get_or_create(
            challenge=challenge2,
            order=3,
            defaults={
                'input_data': '[3, 3]\n6',
                'expected_output': '[0, 1]',
                'is_sample': False,
                'weight': 1.0,
            }
        )

        # Stage 3: System Design / Systems thinking
        q3, _ = Question.objects.get_or_create(
            title='Design a distributed rate limiter',
            defaults={
                'prompt': 'Design a distributed rate limiter for a multi-tenant API serving 50,000 requests per second. Explain token bucket vs sliding window log, Redis cluster storage layout, and failure modes when cache instances crash.',
                'question_type': QuestionType.SYSTEM_DESIGN,
                'difficulty': DifficultyLevel.MEDIUM,
                'category': 'Architecture & Trade-offs',
                'points': 30,
                'time_expected_minutes': 35,
            }
        )
        StageQuestion.objects.get_or_create(stage=stage_objects[3], question=q3, defaults={'order': 1})

        # Stage 4: 3 Written Reasoning Questions
        written_q_data = [
            ('Trade-offs', 'You can ship a feature today with a quick fix or delay it to refactor a fragile area. What factors influence your decision?', 'Consider user impact, risk, reversibility and technical debt.'),
            ('Debugging', 'A service starts returning intermittent 500 errors after a release. Describe your first three steps.', 'Explain how you would gather evidence before changing code.'),
            ('Collaboration', 'A teammate disagrees with your proposed API design. How would you resolve the disagreement?', 'Focus on shared goals, evidence and documenting a decision.')
        ]
        for i, (w_title, w_prompt, w_rubric) in enumerate(written_q_data, start=1):
            wq, _ = Question.objects.get_or_create(
                title=w_title,
                defaults={
                    'prompt': w_prompt,
                    'question_type': QuestionType.LONG_REASONING,
                    'difficulty': DifficultyLevel.MEDIUM,
                    'category': 'Engineering Judgment',
                    'points': 15,
                    'rubric_guide': w_rubric,
                    'time_expected_minutes': 10,
                }
            )
            StageQuestion.objects.get_or_create(stage=stage_objects[4], question=wq, defaults={'order': i})

        # 7. Evaluation Rubrics for Stages 3 & 4
        rubric4, _ = EvaluationRubric.objects.get_or_create(
            stage=stage_objects[4],
            defaults={'name': 'Stage 4 Engineering Judgment Rubric'}
        )
        criteria_defs = [
            ("Correctness & problem solving", 25.0, 1),
            ("Code quality & structure", 25.0, 2),
            ("Testing & validation", 25.0, 3),
            ("Reasoning & trade-offs", 25.0, 4),
        ]
        for c_name, weight, ord_num in criteria_defs:
            RubricCriterion.objects.get_or_create(
                rubric=rubric4,
                name=c_name,
                defaults={'weight_percent': weight, 'max_points': 5.0, 'order': ord_num}
            )

        # 8. Version 1 Snapshot
        AssessmentVersion.objects.get_or_create(
            campaign=campaign_main,
            version_number=1,
            defaults={
                'changelog': 'Production v1 configuration for Amerigam Engineering Challenge 2026',
                'is_published': True,
                'published_at': timezone.now(),
                'configuration_snapshot': {
                    'title': campaign_main.title,
                    'stages_count': 4,
                    'pass_threshold': campaign_main.pass_threshold_score,
                }
            }
        )

        # 9. Attempts and Selections for Candidates
        now = timezone.now()
        for c in candidate_data:
            user = cand_users[c['username']]
            c_status = AttemptStatus.PASSED if c['score'] is not None else AttemptStatus.IN_PROGRESS
            attempt, _ = AssessmentAttempt.objects.get_or_create(
                candidate=user,
                campaign=campaign_main,
                defaults={
                    'status': c_status,
                    'final_score': c['score'] or 0.0,
                    'passed': (c['score'] or 0) >= 70,
                    'start_time': now - timedelta(hours=3),
                    'submitted_at': now - timedelta(minutes=45) if c['score'] else None,
                }
            )

            # Create Stage Attempts
            st1_att, _ = StageAttempt.objects.get_or_create(
                assessment_attempt=attempt,
                stage=stage_objects[1],
                defaults={
                    'status': AttemptStatus.PASSED,
                    'attempt_number': 1,
                    'score': 85.0,
                    'passed': True,
                    'start_time': now - timedelta(hours=3),
                    'submitted_at': now - timedelta(hours=2, minutes=15),
                    'deadline': now - timedelta(hours=2),
                }
            )

            st2_status = AttemptStatus.PASSED if c['score'] else AttemptStatus.IN_PROGRESS
            st2_att, _ = StageAttempt.objects.get_or_create(
                assessment_attempt=attempt,
                stage=stage_objects[2],
                defaults={
                    'status': st2_status,
                    'attempt_number': 1,
                    'score': float(c['score']) if c['score'] else 0.0,
                    'passed': (c['score'] or 0) >= 70,
                    'start_time': now - timedelta(hours=2),
                    'submitted_at': now - timedelta(hours=1) if c['score'] else None,
                    'deadline': now + timedelta(minutes=45) if not c['score'] else now - timedelta(hours=1),
                }
            )

            # Assign review if submitted / needs review
            if c['status'] in ['Needs review', 'Submitted']:
                ReviewerAssignment.objects.get_or_create(
                    stage_attempt=st2_att,
                    reviewer=reviewer_user,
                    defaults={
                        'assigned_by': admin_user,
                        'status': ReviewerAssignmentStatus.ASSIGNED,
                    }
                )

            # Candidate Selection for Riya / selected candidates
            if c['status'] == 'Selected':
                CandidateSelection.objects.get_or_create(
                    candidate=user,
                    campaign=campaign_main,
                    defaults={
                        'ranking': 1,
                        'decision': SelectionDecision.SELECTED,
                        'notes': 'Top performer across all algorithmic and architectural stages.',
                        'decided_by': admin_user,
                    }
                )

        # 10. Integrity Events
        aarav_st = StageAttempt.objects.filter(assessment_attempt__candidate=cand_users['aarav']).first()
        devm_st = StageAttempt.objects.filter(assessment_attempt__candidate=cand_users['devm']).first()
        kabir_st = StageAttempt.objects.filter(assessment_attempt__candidate=cand_users['kabir']).first()

        if aarav_st:
            IntegrityEvent.objects.get_or_create(
                stage_attempt=aarav_st,
                candidate=cand_users['aarav'],
                event_type=IntegrityEventType.BROWSER_BLUR,
                defaults={
                    'metadata': {'screen': 'build-and-ship', 'count': 2, 'window_blur_seconds': 4},
                }
            )
        if devm_st:
            IntegrityEvent.objects.get_or_create(
                stage_attempt=devm_st,
                candidate=cand_users['devm'],
                event_type=IntegrityEventType.TAB_SWITCH,
                defaults={
                    'metadata': {'reason': 'Switched to reference documentation tab'},
                }
            )
        if kabir_st:
            IntegrityEvent.objects.get_or_create(
                stage_attempt=kabir_st,
                candidate=cand_users['kabir'],
                event_type=IntegrityEventType.COPY_PASTE,
                defaults={
                    'metadata': {'chars_pasted': 142, 'stage': 'Systems thinking'},
                }
            )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully with 100% dynamic live entities!"))
