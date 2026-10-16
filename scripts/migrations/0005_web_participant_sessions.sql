ALTER TABLE auth_audit_events DROP CONSTRAINT auth_audit_events_action_check;
ALTER TABLE auth_audit_events ADD CONSTRAINT auth_audit_events_action_check CHECK (
    action IN (
        'view_dashboard', 'export_dashboard', 'import_csv', 'manage_users',
        'manage_projects', 'manage_project_members', 'create_invitation',
        'revoke_invitation', 'bootstrap_admin', 'recover_admin'
    )
);

CREATE TABLE web_projects (
    project_id UUID PRIMARY KEY,
    code VARCHAR(64) NOT NULL UNIQUE CHECK (code ~ '^[A-Za-z0-9_.-]{1,64}$'),
    name VARCHAR(200) NOT NULL CHECK (char_length(btrim(name)) BETWEEN 1 AND 200),
    collection_mode TEXT NOT NULL DEFAULT 'synthetic'
        CHECK (collection_mode = 'synthetic'),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_issuer TEXT NOT NULL,
    created_by_subject TEXT NOT NULL,
    FOREIGN KEY (created_by_issuer, created_by_subject)
        REFERENCES app_users(issuer, subject)
);

CREATE TABLE web_project_members (
    project_id UUID NOT NULL REFERENCES web_projects(project_id),
    issuer TEXT NOT NULL,
    subject TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, issuer, subject),
    FOREIGN KEY (issuer, subject) REFERENCES app_users(issuer, subject)
);

CREATE INDEX idx_web_project_members_user_active
    ON web_project_members(issuer, subject, project_id) WHERE active;

CREATE TABLE web_invitations (
    invitation_id UUID PRIMARY KEY,
    session_id UUID NOT NULL UNIQUE,
    project_id UUID NOT NULL REFERENCES web_projects(project_id),
    code_sha256 CHAR(64) NOT NULL UNIQUE CHECK (code_sha256 ~ '^[0-9a-f]{64}$'),
    participant_id VARCHAR(64) NOT NULL CHECK (participant_id ~ '^[A-Za-z0-9_.-]{1,64}$'),
    visit VARCHAR(64) NOT NULL CHECK (visit ~ '^[A-Za-z0-9_.-]{1,64}$'),
    evaluator_issuer TEXT NOT NULL,
    evaluator_subject TEXT NOT NULL,
    protocol_id TEXT NOT NULL DEFAULT 'stroop_go_nogo_ptbr/0.2.2-web.1'
        CHECK (protocol_id = 'stroop_go_nogo_ptbr/0.2.2-web.1'),
    state TEXT NOT NULL DEFAULT 'issued'
        CHECK (state IN ('issued', 'redeemed', 'expired', 'revoked')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    redeemed_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    FOREIGN KEY (evaluator_issuer, evaluator_subject)
        REFERENCES app_users(issuer, subject),
    CONSTRAINT web_invitations_expiration_valid CHECK (
        expires_at > created_at AND expires_at <= created_at + INTERVAL '24 hours'
    ),
    CONSTRAINT web_invitations_state_timestamps CHECK (
        (state IN ('issued','expired') AND redeemed_at IS NULL AND revoked_at IS NULL)
        OR (state = 'revoked' AND redeemed_at IS NULL AND revoked_at IS NOT NULL)
        OR (state = 'redeemed' AND redeemed_at IS NOT NULL)
    )
);

CREATE INDEX idx_web_invitations_project_created
    ON web_invitations(project_id, created_at DESC);
CREATE INDEX idx_web_invitations_expiration
    ON web_invitations(expires_at) WHERE state = 'issued';

CREATE TABLE web_participant_sessions (
    session_id UUID PRIMARY KEY REFERENCES web_invitations(session_id),
    participant_token_sha256 CHAR(64) NOT NULL UNIQUE
        CHECK (participant_token_sha256 ~ '^[0-9a-f]{64}$'),
    state TEXT NOT NULL CHECK (state IN ('preparing', 'running', 'aborted', 'expired')),
    activated_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    app_version VARCHAR(64),
    abort_reason TEXT CHECK (abort_reason IS NULL OR abort_reason IN (
        'focus_lost', 'visibility_hidden', 'escape', 'reload', 'page_closed',
        'timing_invalid', 'user_cancelled'
    )),
    revoked_at TIMESTAMPTZ,
    CONSTRAINT web_participant_sessions_expiration_valid CHECK (
        expires_at > activated_at
        AND expires_at <= activated_at + INTERVAL '30 minutes'
    ),
    CONSTRAINT web_participant_sessions_state_valid CHECK (
        (started_at IS NULL) = (app_version IS NULL)
        AND (state <> 'running' OR started_at IS NOT NULL)
        AND (state <> 'preparing' OR started_at IS NULL)
    )
);

CREATE INDEX idx_web_participant_sessions_expiration
    ON web_participant_sessions(expires_at) WHERE state IN ('preparing', 'running');

CREATE TABLE web_session_main_order (
    session_id UUID NOT NULL REFERENCES web_participant_sessions(session_id) ON DELETE CASCADE,
    trial_number SMALLINT NOT NULL CHECK (trial_number BETWEEN 1 AND 16),
    condition_id SMALLINT NOT NULL CHECK (condition_id BETWEEN 1 AND 16),
    PRIMARY KEY (session_id, trial_number),
    UNIQUE (session_id, condition_id)
);

CREATE TABLE web_participant_redeem_limits (
    remote_sha256 CHAR(64) PRIMARY KEY CHECK (remote_sha256 ~ '^[0-9a-f]{64}$'),
    window_started_at TIMESTAMPTZ NOT NULL,
    request_count INTEGER NOT NULL CHECK (request_count > 0)
);

CREATE INDEX idx_web_participant_redeem_limits_window
    ON web_participant_redeem_limits(window_started_at);

CREATE TABLE web_professional_request_limits (
    credential_sha256 CHAR(64) NOT NULL CHECK (credential_sha256 ~ '^[0-9a-f]{64}$'),
    operation TEXT NOT NULL CHECK (operation IN ('read','write')),
    window_started_at TIMESTAMPTZ NOT NULL,
    request_count INTEGER NOT NULL CHECK (request_count > 0),
    PRIMARY KEY (credential_sha256, operation)
);

CREATE INDEX idx_web_professional_request_limits_window
    ON web_professional_request_limits(window_started_at);
