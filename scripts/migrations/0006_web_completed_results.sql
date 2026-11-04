ALTER TABLE web_participant_sessions DROP CONSTRAINT web_participant_sessions_state_check;
ALTER TABLE web_participant_sessions ADD CONSTRAINT web_participant_sessions_state_check
    CHECK (state IN ('preparing','running','completed','aborted','expired'));
ALTER TABLE web_participant_sessions ADD CONSTRAINT web_completed_requires_start
    CHECK (state <> 'completed' OR started_at IS NOT NULL);

CREATE TABLE web_participant_request_limits (
    credential_sha256 CHAR(64) NOT NULL CHECK (credential_sha256 ~ '^[0-9a-f]{64}$'),
    operation TEXT NOT NULL CHECK (operation IN ('read','write')),
    window_started_at TIMESTAMPTZ NOT NULL,
    request_count INTEGER NOT NULL CHECK (request_count > 0),
    PRIMARY KEY (credential_sha256, operation)
);
CREATE INDEX idx_web_participant_request_limits_window
    ON web_participant_request_limits(window_started_at);

-- Proveniencia WEB aditiva: linhas legadas conservam seus valores e contratos.
CREATE TABLE web_assessments (
    assessment_id TEXT PRIMARY KEY REFERENCES assessments(assessment_id),
    session_id UUID NOT NULL UNIQUE REFERENCES web_participant_sessions(session_id),
    project_id UUID NOT NULL REFERENCES web_projects(project_id),
    platform TEXT NOT NULL DEFAULT 'web' CHECK (platform = 'web'),
    protocol_id TEXT NOT NULL CHECK (protocol_id = 'stroop_go_nogo_ptbr/0.2.2-web.1'),
    app_version VARCHAR(64) NOT NULL,
    frame_period_ms DOUBLE PRECISION NOT NULL CHECK (frame_period_ms BETWEEN 4 AND 50),
    payload_sha256 CHAR(64) NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    completed_at TIMESTAMPTZ NOT NULL,
    receipt JSONB NOT NULL CHECK (jsonb_typeof(receipt) = 'object')
);

CREATE INDEX idx_web_assessments_project_completed
    ON web_assessments(project_id, completed_at, assessment_id);

CREATE TABLE web_trial_observations (
    assessment_id TEXT NOT NULL REFERENCES web_assessments(assessment_id),
    trial_number SMALLINT NOT NULL CHECK (trial_number BETWEEN 1 AND 16),
    condition_id SMALLINT NOT NULL CHECK (condition_id BETWEEN 1 AND 16),
    trial_start_ms DOUBLE PRECISION NOT NULL CHECK (trial_start_ms >= 0),
    stimulus_onset_ms DOUBLE PRECISION NOT NULL,
    stimulus_offset_ms DOUBLE PRECISION NOT NULL,
    trial_end_ms DOUBLE PRECISION NOT NULL CHECK (trial_end_ms <= 60100),
    key_at_ms DOUBLE PRECISION,
    reaction_time_ms DOUBLE PRECISION,
    PRIMARY KEY (assessment_id,trial_number),
    UNIQUE (assessment_id,condition_id),
    CHECK (trial_start_ms < stimulus_onset_ms
        AND stimulus_onset_ms < stimulus_offset_ms AND stimulus_offset_ms < trial_end_ms),
    CHECK ((key_at_ms IS NULL AND reaction_time_ms IS NULL)
        OR (key_at_ms IS NOT NULL AND reaction_time_ms IS NOT NULL
            AND key_at_ms > stimulus_onset_ms AND key_at_ms < stimulus_offset_ms
            AND reaction_time_ms > 0 AND reaction_time_ms < 2500))
);
