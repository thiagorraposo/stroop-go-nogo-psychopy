-- Identidade local explicita, sem reassociacao de qualquer principal historico.
ALTER TABLE app_users DROP CONSTRAINT app_users_issuer_check;
ALTER TABLE app_users ADD CONSTRAINT app_users_issuer_check CHECK (
    issuer IN ('https://accounts.google.com', 'accounts.google.com', 'urn:stroop:local')
);
ALTER TABLE app_users ADD CONSTRAINT app_users_local_subject CHECK (
    issuer <> 'urn:stroop:local' OR subject ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
);

CREATE TABLE web_local_credentials (
    principal_id UUID PRIMARY KEY,
    issuer TEXT NOT NULL DEFAULT 'urn:stroop:local' CHECK (issuer = 'urn:stroop:local'),
    subject TEXT GENERATED ALWAYS AS (principal_id::text) STORED,
    username VARCHAR(64) NOT NULL UNIQUE CHECK (username ~ '^[a-z0-9_.-]{1,64}$'),
    password_hash TEXT NOT NULL CHECK (password_hash LIKE '$argon2id$v=19$%'),
    credential_version BIGINT NOT NULL DEFAULT 1 CHECK (credential_version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issuer,subject) REFERENCES app_users(issuer,subject)
);
-- A tabela representa futuros principais; bootstrap desta versao serializa e
-- recusa segunda conta. Runtime nao tem INSERT/DELETE ou funcao de bootstrap.
CREATE TABLE web_local_sessions (
    token_sha256 TEXT PRIMARY KEY CHECK (token_sha256 ~ '^[0-9a-f]{64}$'),
    principal_id UUID NOT NULL REFERENCES web_local_credentials(principal_id),
    credential_version BIGINT NOT NULL CHECK (credential_version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    absolute_expires_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP + INTERVAL '8 hours',
    revoked_at TIMESTAMPTZ,
    CHECK (last_activity_at >= created_at AND absolute_expires_at > created_at
        AND absolute_expires_at <= created_at + INTERVAL '8 hours')
);
CREATE INDEX web_local_sessions_principal ON web_local_sessions(principal_id);
CREATE INDEX web_local_sessions_expiration ON web_local_sessions(absolute_expires_at);
CREATE TABLE web_local_auth_limits (
    bucket_sha256 TEXT PRIMARY KEY CHECK (bucket_sha256 ~ '^[0-9a-f]{64}$'),
    window_started_at TIMESTAMPTZ NOT NULL,
    failure_count INTEGER NOT NULL CHECK (failure_count >= 0)
);
CREATE TABLE web_local_auth_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    principal_id UUID REFERENCES web_local_credentials(principal_id),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL CHECK (action IN (
        'bootstrap','login_success','login_failure','rate_limited','password_change',
        'recovery','logout','sessions_revoke'
    ))
);
