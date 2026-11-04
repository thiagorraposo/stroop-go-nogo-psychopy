CREATE TABLE web_oidc_transactions (
    state_sha256 CHAR(64) PRIMARY KEY CHECK (state_sha256 ~ '^[0-9a-f]{64}$'),
    nonce VARCHAR(128) NOT NULL,
    code_verifier VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT web_oidc_transactions_nonce_valid CHECK (
        nonce ~ '^[A-Za-z0-9_-]{32,128}$'
    ),
    CONSTRAINT web_oidc_transactions_verifier_valid CHECK (
        code_verifier ~ '^[A-Za-z0-9_-]{43,128}$'
    ),
    CONSTRAINT web_oidc_transactions_expiration_valid CHECK (
        expires_at > created_at
        AND expires_at <= created_at + INTERVAL '10 minutes'
    )
);

CREATE INDEX idx_web_oidc_transactions_expiration
    ON web_oidc_transactions(expires_at);

CREATE TABLE web_professional_sessions (
    token_sha256 CHAR(64) PRIMARY KEY CHECK (token_sha256 ~ '^[0-9a-f]{64}$'),
    issuer TEXT NOT NULL CHECK (
        issuer IN ('https://accounts.google.com', 'accounts.google.com')
    ),
    subject TEXT NOT NULL CHECK (char_length(subject) BETWEEN 1 AND 255),
    oidc_expires_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issuer, subject)
        REFERENCES app_users(issuer, subject) ON DELETE CASCADE,
    CONSTRAINT web_professional_sessions_expiration_valid CHECK (
        expires_at > created_at
        AND expires_at <= oidc_expires_at
        AND expires_at <= created_at + INTERVAL '8 hours'
    )
);

CREATE INDEX idx_web_professional_sessions_expiration
    ON web_professional_sessions(expires_at);

CREATE TABLE web_login_rate_limits (
    remote_sha256 TEXT PRIMARY KEY CHECK (remote_sha256 ~ '^[0-9a-f]{64}$'),
    window_started_at TIMESTAMPTZ NOT NULL,
    request_count INTEGER NOT NULL CHECK (request_count > 0)
);

CREATE INDEX idx_web_login_rate_limits_window
    ON web_login_rate_limits(window_started_at);
