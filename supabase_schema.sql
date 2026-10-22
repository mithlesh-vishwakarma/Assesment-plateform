-- =============================================================================
-- AMERIGAM ENGINEERING CHALLENGE - SUPABASE DATABASE SCHEMA
-- Project ID: lomvdampiyqwicofxsxa
-- Project Name: Amerigam-assesment-test
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. ACCOUNTS & PROFILES
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT NOT NULL CHECK (role IN ('ADMIN', 'REVIEWER', 'CANDIDATE')) DEFAULT 'CANDIDATE',
    phone TEXT,
    bio TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS candidate_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE UNIQUE,
    technical_track TEXT NOT NULL DEFAULT 'fullstack',
    years_of_experience NUMERIC(4, 1) DEFAULT 0.0,
    resume_url TEXT,
    github_url TEXT,
    linkedin_url TEXT,
    status TEXT NOT NULL CHECK (status IN ('INVITED', 'ACTIVE', 'SUBMITTED', 'EVALUATING', 'SELECTED', 'WAITLISTED', 'REJECTED', 'WITHDRAWN')) DEFAULT 'ACTIVE',
    admin_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviewer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE UNIQUE,
    specialization TEXT DEFAULT 'General Engineering',
    max_assigned_candidates INT DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 2. CAMPAIGNS, VERSIONS & STAGES
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessment_campaigns (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    max_attempts_per_candidate INT DEFAULT 1,
    pass_threshold_score NUMERIC(5, 2) DEFAULT 70.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assessment_versions (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT REFERENCES assessment_campaigns(id) ON DELETE CASCADE,
    version_number INT DEFAULT 1,
    changelog TEXT,
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    configuration_snapshot JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (campaign_id, version_number)
);

CREATE TABLE IF NOT EXISTS assessment_stages (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT REFERENCES assessment_campaigns(id) ON DELETE CASCADE,
    version_id BIGINT REFERENCES assessment_versions(id) ON DELETE SET NULL,
    stage_type TEXT NOT NULL CHECK (stage_type IN ('STAGE_1_FUNDAMENTALS', 'STAGE_2_CODING', 'STAGE_3_CHALLENGES', 'STAGE_4_REASONING')),
    name TEXT NOT NULL,
    description TEXT,
    stage_order INT DEFAULT 1,
    time_limit_minutes INT DEFAULT 60,
    pass_threshold_score NUMERIC(5, 2) DEFAULT 70.00,
    requires_manual_review BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    max_attempts INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (campaign_id, stage_order)
);

CREATE TABLE IF NOT EXISTS stage_prerequisites (
    id BIGSERIAL PRIMARY KEY,
    stage_id BIGINT REFERENCES assessment_stages(id) ON DELETE CASCADE,
    prerequisite_stage_id BIGINT REFERENCES assessment_stages(id) ON DELETE CASCADE,
    minimum_score NUMERIC(5, 2) DEFAULT 70.00,
    UNIQUE (stage_id, prerequisite_stage_id)
);

-- -----------------------------------------------------------------------------
-- 3. QUESTIONS, CHALLENGES & TEST CASES
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS questions (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    prompt TEXT NOT NULL,
    question_type TEXT NOT NULL CHECK (question_type IN (
        'MCQ', 'SHORT_ANSWER', 'LONG_REASONING', 'DSA_CODING', 'DEBUGGING',
        'CODE_REVIEW', 'FRONTEND', 'BACKEND', 'DATABASE_SQL', 'SECURITY',
        'MOBILE', 'DEVOPS_TESTING', 'SYSTEM_DESIGN'
    )) DEFAULT 'DSA_CODING',
    difficulty TEXT NOT NULL CHECK (difficulty IN ('EASY', 'MEDIUM', 'HARD')) DEFAULT 'MEDIUM',
    category TEXT DEFAULT 'General Engineering',
    points INT DEFAULT 10,
    instructions TEXT,
    constraints TEXT,
    time_expected_minutes INT DEFAULT 15,
    tags JSONB DEFAULT '[]'::jsonb,
    mcq_options JSONB DEFAULT '[]'::jsonb,
    rubric_guide TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    version INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_questions (
    id BIGSERIAL PRIMARY KEY,
    stage_id BIGINT REFERENCES assessment_stages(id) ON DELETE CASCADE,
    question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
    question_order INT DEFAULT 1,
    points_weight NUMERIC(4, 2) DEFAULT 1.00,
    UNIQUE (stage_id, question_id)
);

CREATE TABLE IF NOT EXISTS challenges (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE UNIQUE,
    allowed_languages JSONB DEFAULT '["python", "javascript", "typescript"]'::jsonb,
    starter_code JSONB DEFAULT '{}'::jsonb,
    function_signature TEXT,
    time_limit_seconds NUMERIC(4, 2) DEFAULT 2.00,
    memory_limit_mb INT DEFAULT 128,
    run_quota_per_attempt INT DEFAULT 20,
    expected_output_format TEXT
);

CREATE TABLE IF NOT EXISTS test_cases (
    id BIGSERIAL PRIMARY KEY,
    challenge_id BIGINT REFERENCES challenges(id) ON DELETE CASCADE,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_sample BOOLEAN DEFAULT FALSE,
    weight NUMERIC(4, 2) DEFAULT 1.00,
    case_order INT DEFAULT 1,
    explanation TEXT
);

-- -----------------------------------------------------------------------------
-- 4. ATTEMPTS, SUBMISSIONS & CODE EXECUTION
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS assessment_attempts (
    id BIGSERIAL PRIMARY KEY,
    candidate_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    campaign_id BIGINT REFERENCES assessment_campaigns(id) ON DELETE CASCADE,
    assessment_version_id BIGINT REFERENCES assessment_versions(id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (status IN ('NOT_STARTED', 'IN_PROGRESS', 'SUBMITTED', 'EVALUATING', 'PASSED', 'FAILED', 'MANUAL_REVIEW', 'EXPIRED')) DEFAULT 'IN_PROGRESS',
    start_time TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    final_score NUMERIC(5, 2) DEFAULT 0.00,
    passed BOOLEAN DEFAULT FALSE,
    attempt_number INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stage_attempts (
    id BIGSERIAL PRIMARY KEY,
    assessment_attempt_id BIGINT REFERENCES assessment_attempts(id) ON DELETE CASCADE,
    stage_id BIGINT REFERENCES assessment_stages(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('NOT_STARTED', 'IN_PROGRESS', 'SUBMITTED', 'EVALUATING', 'PASSED', 'FAILED', 'MANUAL_REVIEW', 'EXPIRED')) DEFAULT 'NOT_STARTED',
    start_time TIMESTAMPTZ,
    deadline TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    score NUMERIC(5, 2) DEFAULT 0.00,
    passed BOOLEAN DEFAULT FALSE,
    attempt_number INT DEFAULT 1,
    run_quota_used INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (assessment_attempt_id, stage_id, attempt_number)
);

CREATE TABLE IF NOT EXISTS submissions (
    id BIGSERIAL PRIMARY KEY,
    stage_attempt_id BIGINT REFERENCES stage_attempts(id) ON DELETE CASCADE,
    question_id BIGINT REFERENCES questions(id) ON DELETE CASCADE,
    submission_type TEXT NOT NULL CHECK (submission_type IN ('CODE', 'WRITTEN', 'MCQ')) DEFAULT 'CODE',
    content TEXT DEFAULT '',
    selected_options JSONB DEFAULT '[]'::jsonb,
    language TEXT,
    is_draft BOOLEAN DEFAULT TRUE,
    version_number INT DEFAULT 1,
    score NUMERIC(5, 2) DEFAULT 0.00,
    evaluated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (stage_attempt_id, question_id)
);

CREATE TABLE IF NOT EXISTS submission_versions (
    id BIGSERIAL PRIMARY KEY,
    submission_id BIGINT REFERENCES submissions(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    content TEXT NOT NULL,
    language TEXT,
    selected_options JSONB DEFAULT '[]'::jsonb,
    is_final BOOLEAN DEFAULT FALSE,
    saved_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS written_responses (
    id BIGSERIAL PRIMARY KEY,
    submission_id BIGINT REFERENCES submissions(id) ON DELETE CASCADE UNIQUE,
    reasoning_text TEXT,
    architectural_decisions TEXT,
    trade_offs TEXT,
    security_considerations TEXT,
    assumptions TEXT,
    incident_mitigation TEXT
);

CREATE TABLE IF NOT EXISTS execution_jobs (
    id BIGSERIAL PRIMARY KEY,
    submission_id BIGINT REFERENCES submissions(id) ON DELETE SET NULL,
    stage_attempt_id BIGINT REFERENCES stage_attempts(id) ON DELETE CASCADE,
    challenge_id BIGINT REFERENCES challenges(id) ON DELETE CASCADE,
    is_sample_run BOOLEAN DEFAULT TRUE,
    language TEXT NOT NULL,
    source_code TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'TIMED_OUT')) DEFAULT 'QUEUED',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS execution_results (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT REFERENCES execution_jobs(id) ON DELETE CASCADE UNIQUE,
    stdout TEXT DEFAULT '',
    stderr TEXT DEFAULT '',
    compile_output TEXT DEFAULT '',
    exit_code INT DEFAULT 0,
    execution_time_ms NUMERIC(8, 2) DEFAULT 0.00,
    memory_used_kb INT DEFAULT 0,
    status_message TEXT DEFAULT 'Success',
    passed_test_cases_count INT DEFAULT 0,
    total_test_cases_count INT DEFAULT 0,
    score_earned NUMERIC(5, 2) DEFAULT 0.00,
    test_results_sanitized JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 5. RUBRICS & EVALUATION
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS evaluation_rubrics (
    id BIGSERIAL PRIMARY KEY,
    stage_id BIGINT REFERENCES assessment_stages(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rubric_criteria (
    id BIGSERIAL PRIMARY KEY,
    rubric_id BIGINT REFERENCES evaluation_rubrics(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    weight_percent NUMERIC(5, 2) DEFAULT 20.00,
    max_points NUMERIC(5, 2) DEFAULT 10.00,
    description TEXT,
    criteria_order INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS stage_evaluations (
    id BIGSERIAL PRIMARY KEY,
    stage_attempt_id BIGINT REFERENCES stage_attempts(id) ON DELETE CASCADE UNIQUE,
    evaluator_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'IN_REVIEW', 'COMPLETED')) DEFAULT 'PENDING',
    automated_score NUMERIC(5, 2) DEFAULT 0.00,
    manual_score NUMERIC(5, 2) DEFAULT 0.00,
    total_score NUMERIC(5, 2) DEFAULT 0.00,
    is_passed BOOLEAN DEFAULT FALSE,
    reviewer_notes TEXT,
    evaluated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS criterion_scores (
    id BIGSERIAL PRIMARY KEY,
    stage_evaluation_id BIGINT REFERENCES stage_evaluations(id) ON DELETE CASCADE,
    criterion_id BIGINT REFERENCES rubric_criteria(id) ON DELETE CASCADE,
    score NUMERIC(5, 2) DEFAULT 0.00,
    comments TEXT,
    UNIQUE (stage_evaluation_id, criterion_id)
);

CREATE TABLE IF NOT EXISTS reviewer_assignments (
    id BIGSERIAL PRIMARY KEY,
    stage_attempt_id BIGINT REFERENCES stage_attempts(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    assigned_by_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (status IN ('ASSIGNED', 'IN_PROGRESS', 'COMPLETED')) DEFAULT 'ASSIGNED',
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    UNIQUE (stage_attempt_id, reviewer_id)
);

-- -----------------------------------------------------------------------------
-- 6. INTEGRITY & AUDIT LOGS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS integrity_events (
    id BIGSERIAL PRIMARY KEY,
    stage_attempt_id BIGINT REFERENCES stage_attempts(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'BROWSER_BLUR', 'TAB_SWITCH', 'COPY_PASTE', 'DEVTOOLS_OPENED',
        'FULLSCREEN_EXIT', 'MULTIPLE_IPS', 'SUSPICIOUS_PASTE'
    )),
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    target_model TEXT,
    target_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS candidate_selections (
    id BIGSERIAL PRIMARY KEY,
    candidate_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    campaign_id BIGINT REFERENCES assessment_campaigns(id) ON DELETE CASCADE,
    decision TEXT NOT NULL CHECK (decision IN ('SELECTED', 'WAITLISTED', 'REJECTED', 'PENDING')) DEFAULT 'PENDING',
    ranking INT,
    notes TEXT,
    decided_by_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    decided_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (candidate_id, campaign_id)
);

CREATE TABLE IF NOT EXISTS report_exports (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT REFERENCES assessment_campaigns(id) ON DELETE CASCADE,
    requested_by_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    export_type TEXT NOT NULL CHECK (export_type IN ('CSV', 'JSON', 'SUMMARY')) DEFAULT 'CSV',
    status TEXT DEFAULT 'COMPLETED',
    result_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 7. INITIAL SEED DATA
-- -----------------------------------------------------------------------------

-- Create default Campaign
INSERT INTO assessment_campaigns (id, title, slug, description, is_active, pass_threshold_score)
VALUES (
    1,
    'Amerigam Engineering Challenge 2026',
    'amerigam-engineering-challenge-2026',
    'Evaluates practical engineering capabilities, algorithmic reasoning, architecture decisions, and code quality.',
    TRUE,
    70.00
) ON CONFLICT (id) DO NOTHING;

-- Create default Version
INSERT INTO assessment_versions (id, campaign_id, version_number, changelog, is_published, published_at)
VALUES (
    1,
    1,
    1,
    'Initial baseline version for Amerigam Assessment Platform',
    TRUE,
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Create 4 Standard Stages
INSERT INTO assessment_stages (id, campaign_id, version_id, stage_type, name, description, stage_order, time_limit_minutes, pass_threshold_score, requires_manual_review)
VALUES 
    (1, 1, 1, 'STAGE_1_FUNDAMENTALS', 'Engineering Fundamentals', 'Core CS fundamentals, data structures, and algorithm complexity.', 1, 45, 70.00, FALSE),
    (2, 1, 1, 'STAGE_2_CODING', 'Hands-on Coding Workspace', 'Solve practical algorithmic and engineering implementation challenges with real-time test execution.', 2, 60, 70.00, FALSE),
    (3, 1, 1, 'STAGE_3_CHALLENGES', 'Systems & Architecture Challenge', 'Fullstack, API design, data modeling, and performance optimization scenarios.', 3, 60, 75.00, TRUE),
    (4, 1, 1, 'STAGE_4_REASONING', 'Engineering Judgment & Trade-offs', 'Written explanation of technical trade-offs, debugging approach, and architectural decisions.', 4, 30, 70.00, TRUE)
ON CONFLICT (id) DO NOTHING;

-- Stage Prerequisites
INSERT INTO stage_prerequisites (stage_id, prerequisite_stage_id, minimum_score)
VALUES 
    (2, 1, 70.00),
    (3, 2, 70.00),
    (4, 3, 70.00)
ON CONFLICT DO NOTHING;

-- Seed Question 1: Find a pair (Two Sum)
INSERT INTO questions (id, title, prompt, question_type, difficulty, category, points, instructions, constraints, time_expected_minutes, tags)
VALUES (
    1,
    'Find a pair',
    'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
    'DSA_CODING',
    'EASY',
    'Arrays & Hash Maps',
    20,
    'Each input has exactly one valid solution. You may not use the same element twice. Aim for O(n) time complexity.',
    '2 <= nums.length <= 10^4; -10^9 <= nums[i] <= 10^9; -10^9 <= target <= 10^9',
    20,
    '["arrays", "hash-map", "two-sum", "dsa"]'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- Link Question to Stage 2
INSERT INTO stage_questions (stage_id, question_id, question_order, points_weight)
VALUES (2, 1, 1, 1.00)
ON CONFLICT DO NOTHING;

-- Coding Challenge configuration for Question 1
INSERT INTO challenges (id, question_id, allowed_languages, starter_code, time_limit_seconds, memory_limit_mb)
VALUES (
    1,
    1,
    '["typescript", "javascript", "python"]'::jsonb,
    '{
        "typescript": "function findPair(nums: number[], target: number): number[] {\n  const seen = new Map<number, number>();\n  for (let i = 0; i < nums.length; i++) {\n    const complement = target - nums[i];\n    if (seen.has(complement)) {\n      return [seen.get(complement)!, i];\n    }\n    seen.set(nums[i], i);\n  }\n  return [];\n}",
        "python": "def find_pair(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, n in enumerate(nums):\n        complement = target - n\n        if complement in seen:\n            return [seen[complement], i]\n        seen[n] = i\n    return []"
    }'::jsonb,
    2.00,
    128
) ON CONFLICT (id) DO NOTHING;

-- Sample & Private Test Cases
INSERT INTO test_cases (challenge_id, input_data, expected_output, is_sample, case_order, explanation)
VALUES 
    (1, '{"nums": [2, 7, 11, 15], "target": 9}', '[0, 1]', TRUE, 1, 'nums[0] + nums[1] == 9'),
    (1, '{"nums": [3, 2, 4], "target": 6}', '[1, 2]', TRUE, 2, 'nums[1] + nums[2] == 6'),
    (1, '{"nums": [3, 3], "target": 6}', '[0, 1]', FALSE, 3, 'Handles duplicate values properly')
ON CONFLICT DO NOTHING;

-- Reset sequence IDs
SELECT setval('assessment_campaigns_id_seq', (SELECT MAX(id) FROM assessment_campaigns));
SELECT setval('assessment_versions_id_seq', (SELECT MAX(id) FROM assessment_versions));
SELECT setval('assessment_stages_id_seq', (SELECT MAX(id) FROM assessment_stages));
SELECT setval('questions_id_seq', (SELECT MAX(id) FROM questions));
SELECT setval('challenges_id_seq', (SELECT MAX(id) FROM challenges));
SELECT setval('test_cases_id_seq', (SELECT MAX(id) FROM test_cases));
