-- Cadastros centrais de pacientes e avaliadores responsaveis (CHG-005 / ADR-007).
-- Evolucao estritamente aditiva sobre 0001..0013; FKs com ON DELETE RESTRICT.

ALTER TABLE auth_audit_events DROP CONSTRAINT auth_audit_events_action_check;
ALTER TABLE auth_audit_events ADD CONSTRAINT auth_audit_events_action_check CHECK (
    action IN (
        'view_dashboard', 'export_dashboard', 'import_csv', 'manage_users',
        'manage_projects', 'manage_project_members', 'create_invitation',
        'revoke_invitation', 'bootstrap_admin', 'recover_admin',
        'manage_patients', 'manage_evaluators'
    )
);

CREATE SEQUENCE web_patient_code_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE web_evaluator_code_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE web_patients (
    id UUID PRIMARY KEY,
    participant_code VARCHAR(64) NOT NULL UNIQUE CHECK (
        participant_code ~ '^PAT-[0-9]{8}-[0-9]{6,}$'
        AND char_length(participant_code) BETWEEN 2 AND 64
    ),
    full_name TEXT NOT NULL CHECK (
        char_length(btrim(full_name)) BETWEEN 2 AND 120
        AND full_name !~ '[\x00-\x1F\x7F]'
    ),
    normalized_name TEXT NOT NULL CHECK (
        char_length(btrim(normalized_name)) BETWEEN 2 AND 120
        AND normalized_name !~ '[\x00-\x1F\x7F]'
    ),
    initials TEXT NOT NULL DEFAULT '' CHECK (
        char_length(btrim(initials)) <= 16
        AND initials !~ '[\x00-\x1F\x7F]'
    ),
    disambiguation_note TEXT NOT NULL DEFAULT '' CHECK (
        char_length(btrim(disambiguation_note)) <= 160
        AND disambiguation_note !~ '[\x00-\x1F\x7F]'
    ),
    is_homonym_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_issuer TEXT NOT NULL,
    created_by_subject TEXT NOT NULL,
    FOREIGN KEY (created_by_issuer, created_by_subject)
        REFERENCES app_users(issuer, subject) ON DELETE RESTRICT
);

CREATE INDEX idx_web_patients_normalized_name ON web_patients(normalized_name);
CREATE INDEX idx_web_patients_participant_code ON web_patients(participant_code);

CREATE TABLE web_evaluators (
    id UUID PRIMARY KEY,
    evaluator_code VARCHAR(64) NOT NULL UNIQUE CHECK (
        evaluator_code ~ '^EVA-[0-9]{6,}$'
        AND char_length(evaluator_code) BETWEEN 2 AND 64
    ),
    full_name TEXT NOT NULL CHECK (
        char_length(btrim(full_name)) BETWEEN 2 AND 120
        AND full_name !~ '[\x00-\x1F\x7F]'
    ),
    normalized_name TEXT NOT NULL CHECK (
        char_length(btrim(normalized_name)) BETWEEN 2 AND 120
        AND normalized_name !~ '[\x00-\x1F\x7F]'
    ),
    initials TEXT NOT NULL DEFAULT '' CHECK (
        char_length(btrim(initials)) <= 16
        AND initials !~ '[\x00-\x1F\x7F]'
    ),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_issuer TEXT NOT NULL,
    created_by_subject TEXT NOT NULL,
    FOREIGN KEY (created_by_issuer, created_by_subject)
        REFERENCES app_users(issuer, subject) ON DELETE RESTRICT
);

CREATE INDEX idx_web_evaluators_normalized_name ON web_evaluators(normalized_name);
CREATE INDEX idx_web_evaluators_evaluator_code ON web_evaluators(evaluator_code);

CREATE TABLE web_registry_audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL CHECK (
        entity_type IN ('patient', 'evaluator', 'participant_link', 'invitation_link')
    ),
    entity_id UUID NOT NULL,
    action TEXT NOT NULL CHECK (
        action IN ('create', 'update', 'deactivate', 'reactivate', 'relink')
    ),
    actor_issuer TEXT NOT NULL,
    actor_subject TEXT NOT NULL,
    reason_code TEXT NOT NULL DEFAULT '' CHECK (
        char_length(reason_code) <= 120
        AND reason_code !~ '[\x00-\x1F\x7F]'
    ),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actor_issuer, actor_subject)
        REFERENCES app_users(issuer, subject) ON DELETE RESTRICT
);

CREATE INDEX idx_web_registry_audit_events_entity
    ON web_registry_audit_events(entity_type, entity_id, occurred_at DESC);

CREATE TABLE web_legacy_entity_links (
    link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('patient', 'evaluator')),
    legacy_participant_uuid UUID NULL
        REFERENCES web_project_participants(participant_uuid) ON DELETE RESTRICT,
    legacy_evaluator_label TEXT NULL CHECK (
        legacy_evaluator_label IS NULL
        OR (char_length(btrim(legacy_evaluator_label)) BETWEEN 1 AND 120
            AND legacy_evaluator_label !~ '[\x00-\x1F\x7F]')
    ),
    patient_id UUID NULL REFERENCES web_patients(id) ON DELETE RESTRICT,
    evaluator_uuid UUID NULL REFERENCES web_evaluators(id) ON DELETE RESTRICT,
    reason_code TEXT NOT NULL CHECK (
        char_length(btrim(reason_code)) BETWEEN 1 AND 120
        AND reason_code !~ '[\x00-\x1F\x7F]'
    ),
    linked_by_issuer TEXT NOT NULL,
    linked_by_subject TEXT NOT NULL,
    linked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (linked_by_issuer, linked_by_subject)
        REFERENCES app_users(issuer, subject) ON DELETE RESTRICT,
    CHECK (
        (entity_type = 'patient'
            AND legacy_participant_uuid IS NOT NULL
            AND patient_id IS NOT NULL
            AND legacy_evaluator_label IS NULL
            AND evaluator_uuid IS NULL)
        OR (entity_type = 'evaluator'
            AND legacy_evaluator_label IS NOT NULL
            AND evaluator_uuid IS NOT NULL
            AND legacy_participant_uuid IS NULL
            AND patient_id IS NULL)
    )
);

ALTER TABLE web_project_participants
    ADD COLUMN patient_id UUID NULL REFERENCES web_patients(id) ON DELETE RESTRICT;
CREATE INDEX idx_web_project_participants_patient_id
    ON web_project_participants(patient_id);

ALTER TABLE web_invitations
    ADD COLUMN patient_id UUID NULL REFERENCES web_patients(id) ON DELETE RESTRICT,
    ADD COLUMN evaluator_uuid UUID NULL REFERENCES web_evaluators(id) ON DELETE RESTRICT,
    ADD COLUMN evaluator_id VARCHAR(64) NULL CHECK (
        evaluator_id IS NULL OR evaluator_id ~ '^[A-Za-z0-9_.-]{1,64}$'
    ),
    ADD COLUMN participant_initials TEXT NOT NULL DEFAULT '' CHECK (
        char_length(btrim(participant_initials)) <= 16
        AND participant_initials !~ '[\x00-\x1F\x7F]'
    ),
    ADD COLUMN test_code VARCHAR(64) NOT NULL DEFAULT 'stroop_go_nogo_ptbr' CHECK (
        test_code ~ '^[A-Za-z0-9_.-]{1,64}$'
    ),
    ADD COLUMN test_version VARCHAR(64) NOT NULL DEFAULT '0.2.2-web.1' CHECK (
        test_version ~ '^[A-Za-z0-9_.+-]{1,64}$'
    );
CREATE INDEX idx_web_invitations_patient_id ON web_invitations(patient_id);
CREATE INDEX idx_web_invitations_evaluator_uuid ON web_invitations(evaluator_uuid);

ALTER TABLE web_assessments
    ADD COLUMN patient_id UUID NULL REFERENCES web_patients(id) ON DELETE RESTRICT,
    ADD COLUMN evaluator_uuid UUID NULL REFERENCES web_evaluators(id) ON DELETE RESTRICT;
CREATE INDEX idx_web_assessments_patient_id ON web_assessments(patient_id);
CREATE INDEX idx_web_assessments_evaluator_uuid ON web_assessments(evaluator_uuid);
