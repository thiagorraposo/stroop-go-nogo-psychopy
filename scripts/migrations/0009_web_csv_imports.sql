CREATE TABLE web_csv_imports (
    operation_id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES web_projects(project_id),
    issuer TEXT NOT NULL,
    subject TEXT NOT NULL,
    content_sha256 CHAR(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    status TEXT NOT NULL CHECK (status IN ('recebido', 'validado', 'importado', 'rejeitado')),
    error_code TEXT CHECK (error_code IS NULL OR error_code IN (
        'invalid_csv', 'duplicate_assessment', 'validation_or_service_failure'
    )),
    assessment_id TEXT UNIQUE REFERENCES assessments(assessment_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issuer, subject) REFERENCES app_users(issuer, subject),
    CONSTRAINT web_csv_import_state_consistent CHECK (
        (status = 'rejeitado' AND error_code IS NOT NULL AND assessment_id IS NULL)
        OR (status = 'importado' AND error_code IS NULL AND assessment_id IS NOT NULL)
        OR (status IN ('recebido', 'validado') AND error_code IS NULL AND assessment_id IS NULL)
    )
);

CREATE INDEX idx_web_csv_imports_project_updated
    ON web_csv_imports(project_id, updated_at DESC);
