PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS assessments (
    assessment_id TEXT PRIMARY KEY,
    test_code TEXT NOT NULL,
    test_version TEXT NOT NULL,
    project TEXT NOT NULL,
    participant_id TEXT NOT NULL,
    participant_name TEXT NOT NULL,
    initials TEXT,
    visit TEXT NOT NULL,
    evaluator TEXT NOT NULL,
    assessment_date TEXT NOT NULL,
    started_at TEXT NOT NULL,
    source_file TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    import_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assessment_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT NOT NULL,
    metric_code TEXT NOT NULL,
    metric_label TEXT NOT NULL,
    metric_value REAL NOT NULL,
    unit TEXT,
    calculated_at TEXT NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trial_results (
    trial_result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT NOT NULL,
    block TEXT NOT NULL,
    trial_number INTEGER NOT NULL,
    word TEXT NOT NULL,
    ink_color TEXT NOT NULL,
    condition TEXT NOT NULL,
    correct_response TEXT,
    key_pressed TEXT,
    reaction_time REAL,
    correct INTEGER NOT NULL,
    error_type TEXT NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_assessments_participant_id
    ON assessments(participant_id);

CREATE INDEX IF NOT EXISTS idx_assessments_project
    ON assessments(project);

CREATE INDEX IF NOT EXISTS idx_assessments_assessment_date
    ON assessments(assessment_date);

CREATE INDEX IF NOT EXISTS idx_assessments_visit
    ON assessments(visit);

CREATE INDEX IF NOT EXISTS idx_assessments_evaluator
    ON assessments(evaluator);

CREATE INDEX IF NOT EXISTS idx_assessment_metrics_assessment_metric
    ON assessment_metrics(assessment_id, metric_code);

CREATE INDEX IF NOT EXISTS idx_trial_results_assessment_block
    ON trial_results(assessment_id, block);
