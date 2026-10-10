-- Conversational onboarding -- MySQL schema changes.
--
-- students == users (the app's student table). m3_students is untouched.
-- letta_agent_id already exists on users -- do not re-add it here.
--
-- Idempotent: safe to run against a fresh DB that already got the schema from
-- ORM create_all/init_db, and against an existing DB that hasn't. ALTER ADD
-- COLUMN guards against already-present columns via information_schema;
-- CREATE TABLE uses IF NOT EXISTS against information_schema.tables.
--
-- Apply to the app schema, e.g.:
--   mysql -u root -p novi_db < backend/migrations/0001_conversational_onboarding.sql

-- 1) users: onboarding progress per student.

SET @ddl := (
    SELECT IF(
        COUNT(*) = 0,
        'ALTER TABLE `users` ADD COLUMN `onboarding_step` VARCHAR(50) NOT NULL DEFAULT ''name''',
        'SELECT 1'
    )
    FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'users' AND column_name = 'onboarding_step'
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ddl := (
    SELECT IF(
        COUNT(*) = 0,
        'ALTER TABLE `users` ADD COLUMN `onboarding_completed_at` DATETIME NULL',
        'SELECT 1'
    )
    FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'users' AND column_name = 'onboarding_completed_at'
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2) Append-only log of raw answers per onboarding step.

CREATE TABLE IF NOT EXISTS onboarding_answers (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    step_id     VARCHAR(50) NOT NULL,
    raw_value   JSON NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_onboarding_answers_student (student_id),
    CONSTRAINT fk_onboarding_answers_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3) Distilled profile written from the onboarding answers (one row per student).

CREATE TABLE IF NOT EXISTS student_profile (
    student_id                 INT PRIMARY KEY,
    preferred_name             VARCHAR(100),
    country_code               VARCHAR(2),
    curriculum_id              VARCHAR(50),
    grade_id                   VARCHAR(50),
    saturday_activities        JSON,
    strengths                  JSON,
    enjoyed_subjects           JSON,
    difficult_subjects         JSON,
    learning_preference        VARCHAR(50),
    confidence_choice          VARCHAR(50),
    university_raw_text        TEXT,
    university_name            VARCHAR(255),
    university_location        VARCHAR(255),
    university_extraction_conf VARCHAR(50),
    has_career_in_mind         BOOLEAN,
    career_name                VARCHAR(255),
    career_interest_reason     TEXT,
    primary_goal               TEXT,
    updated_at                 DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_profile_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4) Onboarding lookup catalog (seeded separately).

CREATE TABLE IF NOT EXISTS countries (
    code VARCHAR(2) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS curriculums (
    id           VARCHAR(50) PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL,
    name         VARCHAR(100) NOT NULL,
    KEY idx_curriculums_country (country_code),
    CONSTRAINT fk_curriculums_country FOREIGN KEY (country_code) REFERENCES countries(code) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS grades (
    id               VARCHAR(50) PRIMARY KEY,
    country_code     VARCHAR(2),
    curriculum_id    VARCHAR(50),
    label            VARCHAR(100),
    normalized_level VARCHAR(50),
    KEY idx_grades_country (country_code),
    KEY idx_grades_curriculum (curriculum_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subjects (
    id            VARCHAR(100) PRIMARY KEY,
    country_code  VARCHAR(2),
    curriculum_id VARCHAR(50),
    grade_id      VARCHAR(50),
    name          VARCHAR(100),
    KEY idx_subjects_country (country_code),
    KEY idx_subjects_curriculum (curriculum_id),
    KEY idx_subjects_grade (grade_id)
) ENGINE=InnoDB;