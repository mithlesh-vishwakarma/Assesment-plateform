from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from api.models import (
    Assessment,
    UserProfile,
    UserRole,
    CandidateProfile,
    ReviewerProfile,
    AssessmentCampaign,
    AssessmentVersion,
    AssessmentStage,
    StageType,
    StagePrerequisite,
    Question,
    QuestionType,
    StageQuestion,
    Challenge,
    TestCase as ChallengeTestCase,
    AssessmentAttempt,
    StageAttempt,
    AttemptStatus,
    Submission,
    SubmissionVersion,
    WrittenResponse,
    ExecutionJob,
    ExecutionResult,
    EvaluationRubric,
    RubricCriterion,
    StageEvaluation,
    ReviewerAssignment,
    IntegrityEvent,
    AuditLog,
    CandidateSelection,
)


class AmerigamPlatformTests(APITestCase):
    def setUp(self):
        # 1. Create Administrator
        self.admin_user = User.objects.create_superuser(
            username='admin_amerigam',
            email='admin@amerigam.com',
            password='Password123!'
        )
        UserProfile.objects.create(user=self.admin_user, role=UserRole.ADMIN)
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)

        # 2. Create Reviewer
        self.reviewer_user = User.objects.create_user(
            username='reviewer_sarah',
            email='reviewer@amerigam.com',
            password='Password123!'
        )
        UserProfile.objects.create(user=self.reviewer_user, role=UserRole.REVIEWER)
        ReviewerProfile.objects.create(user=self.reviewer_user, specialization='Backend & Architecture')
        self.reviewer_token, _ = Token.objects.get_or_create(user=self.reviewer_user)

        # 3. Create Candidate A
        self.cand_a = User.objects.create_user(
            username='candidate_alex',
            email='alex@example.com',
            password='Password123!'
        )
        UserProfile.objects.create(user=self.cand_a, role=UserRole.CANDIDATE)
        CandidateProfile.objects.create(user=self.cand_a, technical_track='backend', years_of_experience=4.5)
        self.cand_a_token, _ = Token.objects.get_or_create(user=self.cand_a)

        # 4. Create Candidate B (for security isolation verification)
        self.cand_b = User.objects.create_user(
            username='candidate_bob',
            email='bob@example.com',
            password='Password123!'
        )
        UserProfile.objects.create(user=self.cand_b, role=UserRole.CANDIDATE)
        CandidateProfile.objects.create(user=self.cand_b, technical_track='frontend', years_of_experience=3.0)
        self.cand_b_token, _ = Token.objects.get_or_create(user=self.cand_b)

        # 5. Set up Assessment Campaign with 4 Stages
        self.campaign = AssessmentCampaign.objects.create(
            title='Amerigam Engineering Challenge 2026',
            slug='amerigam-2026',
            description='Select top 4 engineers across 4 stages',
            is_active=True,
            pass_threshold_score=70.0,
            created_by=self.admin_user
        )

        # Stage 1: Engineering fundamentals
        self.stage_1 = AssessmentStage.objects.create(
            campaign=self.campaign,
            stage_type=StageType.STAGE_1_FUNDAMENTALS,
            name='Engineering Fundamentals',
            order=1,
            time_limit_minutes=45,
            pass_threshold_score=70.0,
            requires_manual_review=False
        )

        # Stage 2: Hands-on coding
        self.stage_2 = AssessmentStage.objects.create(
            campaign=self.campaign,
            stage_type=StageType.STAGE_2_CODING,
            name='Hands-on Coding',
            order=2,
            time_limit_minutes=60,
            pass_threshold_score=70.0,
            requires_manual_review=False
        )

        # Stage 3: Engineering challenges
        self.stage_3 = AssessmentStage.objects.create(
            campaign=self.campaign,
            stage_type=StageType.STAGE_3_CHALLENGES,
            name='Engineering Challenges',
            order=3,
            time_limit_minutes=90,
            pass_threshold_score=70.0,
            requires_manual_review=True
        )

        # Stage 4: Engineering reasoning
        self.stage_4 = AssessmentStage.objects.create(
            campaign=self.campaign,
            stage_type=StageType.STAGE_4_REASONING,
            name='Engineering Reasoning & Architecture',
            order=4,
            time_limit_minutes=60,
            pass_threshold_score=70.0,
            requires_manual_review=True
        )

        # Stage 2 requires Stage 1
        StagePrerequisite.objects.create(
            stage=self.stage_2,
            prerequisite_stage=self.stage_1,
            minimum_score=70.0
        )

        # 6. Create Questions and Challenges
        # MCQ question for Stage 1
        self.mcq_q = Question.objects.create(
            title='Time Complexity of Binary Search',
            prompt='What is the average time complexity of binary search on a sorted array?',
            question_type=QuestionType.MCQ,
            points=10,
            mcq_options=[
                {"id": "A", "text": "O(n)", "is_correct": False},
                {"id": "B", "text": "O(log n)", "is_correct": True},
                {"id": "C", "text": "O(n^2)", "is_correct": False},
            ]
        )
        StageQuestion.objects.create(stage=self.stage_1, question=self.mcq_q, order=1)

        # Coding challenge for Stage 2
        self.code_q = Question.objects.create(
            title='Two Sum Algorithm',
            prompt='Given an array of integers, return indices of the two numbers such that they add up to target.',
            question_type=QuestionType.DSA_CODING,
            points=20
        )
        StageQuestion.objects.create(stage=self.stage_2, question=self.code_q, order=1)

        self.challenge = Challenge.objects.create(
            question=self.code_q,
            allowed_languages=['python', 'javascript'],
            starter_code={'python': 'def two_sum(nums, target):\n    pass'},
            time_limit_seconds=2.0,
            memory_limit_mb=128,
            run_quota_per_attempt=10
        )

        # Sample test case (public)
        self.sample_tc = ChallengeTestCase.objects.create(
            challenge=self.challenge,
            input_data='[2, 7, 11, 15]\n9',
            expected_output='[0, 1]',
            is_sample=True,
            order=1
        )

        # Hidden test case (private!)
        self.hidden_tc = ChallengeTestCase.objects.create(
            challenge=self.challenge,
            input_data='[3, 2, 4]\n6',
            expected_output='[1, 2]',
            is_sample=False,
            order=2
        )

    # -------------------------------------------------------------
    # 1. Health & Legacy Endpoints Verification
    # -------------------------------------------------------------
    def test_health_check_preserved(self):
        """Frontend relies on /api/health/ for server connectivity."""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'success')

    def test_legacy_assessments_endpoint_preserved(self):
        """Frontend queries /api/assessments/ on startup."""
        Assessment.objects.create(title='Preserved Assessment Title', description='Existing test')
        response = self.client.get('/api/assessments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    # -------------------------------------------------------------
    # 2. Authentication & Roles
    # -------------------------------------------------------------
    def test_user_registration_and_login(self):
        """Candidates can register and receive authentication tokens."""
        reg_payload = {
            'username': 'new_developer',
            'email': 'newdev@amerigam.com',
            'password': 'SecurePassword456!',
            'role': 'CANDIDATE',
            'technical_track': 'fullstack',
            'years_of_experience': 3.5
        }
        res = self.client.post('/api/auth/register/', reg_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', res.data)
        self.assertEqual(res.data['user']['candidate_profile']['technical_track'], 'fullstack')

        # Test login
        login_res = self.client.post('/api/auth/login/', {
            'username': 'new_developer',
            'password': 'SecurePassword456!'
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertIn('token', login_res.data)

    def test_auth_me_profile_retrieval(self):
        """Candidate can inspect their profile using token authentication."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'candidate_alex')
        self.assertEqual(res.data['profile']['role'], 'CANDIDATE')

    # -------------------------------------------------------------
    # 3. Privacy & Hidden Test Case Protection
    # -------------------------------------------------------------
    def test_hidden_test_cases_masked_from_candidates(self):
        """
        Critical security requirement: Candidates must NEVER receive
        hidden test case inputs or expected outputs from the API!
        """
        # Candidate views question/challenge
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        res = self.client.get('/api/admin/questions/')
        # Candidate does not have access to admin question viewset
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin views test cases
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        admin_res = self.client.get(f'/api/admin/testcases/{self.hidden_tc.id}/')
        self.assertEqual(admin_res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(admin_res.data['input_data'], '[HIDDEN]')

    def test_mcq_correct_answers_masked_from_candidates(self):
        """
        Candidates must not be sent correct answer indicators in MCQ options.
        """
        # Start stage 1 to gain question access
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        self.client.post(f'/api/candidate/stages/{self.stage_1.id}/start/')
        res = self.client.get(f'/api/candidate/stages/{self.stage_1.id}/questions/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        mcq_data = res.data[0]
        options = mcq_data.get('mcq_options', [])
        for opt in options:
            self.assertNotIn('is_correct', opt)

    # -------------------------------------------------------------
    # 4. Stage Progression & Server-Controlled Deadlines
    # -------------------------------------------------------------
    def test_sequential_progression_enforcement(self):
        """
        Candidate cannot jump ahead to Stage 2 without completing Stage 1.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        # Try to start Stage 2 directly
        res = self.client.post(f'/api/candidate/stages/{self.stage_2.id}/start/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Prerequisite", str(res.data))

    def test_stage_start_and_deadline_generation(self):
        """
        Starting a stage establishes a server-controlled deadline.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        res = self.client.post(f'/api/candidate/stages/{self.stage_1.id}/start/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], AttemptStatus.IN_PROGRESS)
        self.assertIsNotNone(res.data['deadline'])

    def test_expired_attempt_cannot_submit(self):
        """
        If a deadline has expired, saving drafts or finalizing is blocked.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        start_res = self.client.post(f'/api/candidate/stages/{self.stage_1.id}/start/')
        attempt_id = start_res.data['id']

        # Artificially expire the stage attempt deadline
        st_attempt = StageAttempt.objects.get(id=attempt_id)
        st_attempt.deadline = timezone.now() - timedelta(minutes=10)
        st_attempt.save()

        # Attempt to autosave draft
        res = self.client.post('/api/candidate/submissions/autosave/', {
            'stage_attempt_id': attempt_id,
            'question_id': self.mcq_q.id,
            'submission_type': 'MCQ',
            'selected_options': ['B']
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("expired", str(res.data))

    # -------------------------------------------------------------
    # 5. Draft Autosave & Submission Finalization
    # -------------------------------------------------------------
    def test_draft_autosave_preserves_versions(self):
        """
        Autosaving draft answers does not finalize the attempt and increments version snapshots.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        start_res = self.client.post(f'/api/candidate/stages/{self.stage_1.id}/start/')
        attempt_id = start_res.data['id']

        # Draft 1
        d1 = self.client.post('/api/candidate/submissions/autosave/', {
            'stage_attempt_id': attempt_id,
            'question_id': self.mcq_q.id,
            'submission_type': 'MCQ',
            'selected_options': ['A']
        }, format='json')
        self.assertEqual(d1.status_code, status.HTTP_200_OK)
        self.assertTrue(d1.data['is_draft'])
        self.assertEqual(d1.data['version_number'], 1)

        # Draft 2
        d2 = self.client.post('/api/candidate/submissions/autosave/', {
            'stage_attempt_id': attempt_id,
            'question_id': self.mcq_q.id,
            'submission_type': 'MCQ',
            'selected_options': ['B']
        }, format='json')
        self.assertEqual(d2.status_code, status.HTTP_200_OK)
        self.assertTrue(d2.data['is_draft'])
        self.assertEqual(d2.data['version_number'], 2)

        # Confirm stage attempt is STILL IN_PROGRESS
        st = StageAttempt.objects.get(id=attempt_id)
        self.assertEqual(st.status, AttemptStatus.IN_PROGRESS)

    def test_final_submission_locks_and_evaluates_mcq(self):
        """
        Finalizing submissions freezes the draft, transitions stage, and grades objective questions.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        start_res = self.client.post(f'/api/candidate/stages/{self.stage_1.id}/start/')
        attempt_id = start_res.data['id']

        # Save correct option 'B'
        self.client.post('/api/candidate/submissions/autosave/', {
            'stage_attempt_id': attempt_id,
            'question_id': self.mcq_q.id,
            'submission_type': 'MCQ',
            'selected_options': ['B']
        }, format='json')

        # Finalize
        finalize_res = self.client.post('/api/candidate/submissions/finalize/', {
            'stage_attempt_id': attempt_id
        }, format='json')
        self.assertEqual(finalize_res.status_code, status.HTTP_200_OK)
        self.assertEqual(finalize_res.data['status'], AttemptStatus.PASSED)
        self.assertEqual(finalize_res.data['score'], 100.0)

        # Confirm submission is no longer a draft
        sub = Submission.objects.get(stage_attempt_id=attempt_id, question=self.mcq_q)
        self.assertFalse(sub.is_draft)

    # -------------------------------------------------------------
    # 6. Object-Level Access Control (Candidate Isolation)
    # -------------------------------------------------------------
    def test_candidate_cannot_modify_or_view_another_candidates_submission(self):
        """
        Candidate B cannot modify or autosave into Candidate A's stage attempt.
        """
        # Candidate A starts stage
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        start_res = self.client.post(f'/api/candidate/stages/{self.stage_1.id}/start/')
        cand_a_attempt_id = start_res.data['id']

        # Candidate B attempts to autosave answer to Candidate A's attempt
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_b_token.key}')
        malicious_res = self.client.post('/api/candidate/submissions/autosave/', {
            'stage_attempt_id': cand_a_attempt_id,
            'question_id': self.mcq_q.id,
            'submission_type': 'MCQ',
            'selected_options': ['C']
        }, format='json')

        self.assertEqual(malicious_res.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------------------------------------------
    # 7. Secure Code Runner & Sandbox Adapter
    # -------------------------------------------------------------
    def test_candidate_run_sample_code_executes_safely(self):
        """
        Candidate can run sample tests via secure adapter with run quota enforcement.
        """
        # Advance candidate to stage 2
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        start_1 = self.client.post(f'/api/candidate/stages/{self.stage_1.id}/start/')
        self.client.post('/api/candidate/submissions/autosave/', {
            'stage_attempt_id': start_1.data['id'],
            'question_id': self.mcq_q.id,
            'submission_type': 'MCQ',
            'selected_options': ['B']
        }, format='json')
        self.client.post('/api/candidate/submissions/finalize/', {'stage_attempt_id': start_1.data['id']}, format='json')

        # Now start Stage 2
        start_2 = self.client.post(f'/api/candidate/stages/{self.stage_2.id}/start/')
        self.assertEqual(start_2.status_code, status.HTTP_200_OK)
        st_2_id = start_2.data['id']

        # Run sample code
        sample_code = "def two_sum(nums, target):\n    return [0, 1]"
        run_res = self.client.post('/api/candidate/execution/run-sample/', {
            'stage_attempt_id': st_2_id,
            'challenge_id': self.challenge.id,
            'language': 'python',
            'source_code': sample_code
        }, format='json')

        self.assertEqual(run_res.status_code, status.HTTP_200_OK)
        self.assertIn('test_results_sanitized', run_res.data)
        # Check quota increment
        st_2 = StageAttempt.objects.get(id=st_2_id)
        self.assertEqual(st_2.run_quota_used, 1)

    # -------------------------------------------------------------
    # 8. Evaluation Rubrics & Reviewer Workflow
    # -------------------------------------------------------------
    def test_reviewer_assignment_and_rubric_scoring(self):
        """
        Reviewers can view assigned stage attempts and score against configured rubrics.
        """
        # Candidate submits Stage 3
        st_3_attempt = StageAttempt.objects.create(
            assessment_attempt=AssessmentAttempt.objects.create(candidate=self.cand_a, campaign=self.campaign),
            stage=self.stage_3,
            status=AttemptStatus.MANUAL_REVIEW,
            start_time=timezone.now(),
            deadline=timezone.now() + timedelta(hours=1),
            attempt_number=1
        )

        # Assign Reviewer
        assignment = ReviewerAssignment.objects.create(
            stage_attempt=st_3_attempt,
            reviewer=self.reviewer_user,
            assigned_by=self.admin_user,
            status='ASSIGNED'
        )

        # Reviewer views assigned submissions
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reviewer_token.key}')
        assigned_res = self.client.get('/api/reviewer/assignments/')
        self.assertEqual(assigned_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(assigned_res.data), 1)

        # Reviewer inspects evaluation details
        eval_res = self.client.get(f'/api/reviewer/evaluations/{st_3_attempt.id}/')
        self.assertEqual(eval_res.status_code, status.HTTP_200_OK)
        rubric_criteria = eval_res.data['rubric']['criteria']
        self.assertTrue(len(rubric_criteria) >= 6)

        # Reviewer submits scores
        score_payload = {
            'criteria_scores': [
                {'criterion_id': crit['id'], 'score': 9.0, 'comments': 'Strong solution'}
                for crit in rubric_criteria
            ],
            'reviewer_notes': 'Candidate demonstrates clean architecture and high code quality.'
        }
        score_res = self.client.post(f'/api/reviewer/evaluations/{st_3_attempt.id}/score/', score_payload, format='json')
        self.assertEqual(score_res.status_code, status.HTTP_200_OK)
        self.assertTrue(score_res.data['is_passed'])
        self.assertEqual(score_res.data['status'], 'COMPLETED')

    # -------------------------------------------------------------
    # 9. Integrity Events & Proctoring
    # -------------------------------------------------------------
    def test_candidate_integrity_event_capture(self):
        """
        Proctoring anomalies (window blur, tab switch) are logged in the audit database.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.cand_a_token.key}')
        start_res = self.client.post(f'/api/candidate/stages/{self.stage_1.id}/start/')
        attempt_id = start_res.data['id']

        res = self.client.post('/api/candidate/integrity/events/', {
            'stage_attempt_id': attempt_id,
            'event_type': 'TAB_SWITCH',
            'metadata': {'time_spent_away_seconds': 14.5}
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IntegrityEvent.objects.filter(stage_attempt_id=attempt_id).count(), 1)

    # -------------------------------------------------------------
    # 10. Administrator Candidate Selection & Reports
    # -------------------------------------------------------------
    def test_admin_candidate_selection_top_four(self):
        """
        Administrator can designate and rank candidates (1..4) for final hiring.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        sel_payload = {
            'candidate': self.cand_a.id,
            'campaign': self.campaign.id,
            'decision': 'SELECTED',
            'ranking': 1,
            'notes': 'Rank 1 candidate - exceptional problem solving and clean reasoning.'
        }
        res = self.client.post('/api/admin/selections/', sel_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CandidateSelection.objects.filter(campaign=self.campaign, ranking=1).count(), 1)

    def test_admin_campaign_summary_and_export_csv(self):
        """
        Administrator can retrieve campaign summaries and export CSV spreadsheets.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        summary_res = self.client.get(f'/api/admin/reports/campaign-summary/{self.campaign.id}/')
        self.assertEqual(summary_res.status_code, status.HTTP_200_OK)
        self.assertIn('candidates', summary_res.data)

        csv_res = self.client.post(f'/api/admin/reports/export-csv/{self.campaign.id}/')
        self.assertEqual(csv_res.status_code, status.HTTP_200_OK)
        self.assertIn('Candidate ID', csv_res.data['csv_text'])
