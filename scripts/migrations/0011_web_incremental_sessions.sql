-- Evolucao aditiva: somente convites WEB determinam os vinculos; nunca texto legado.
CREATE TABLE web_project_participants (
    participant_uuid UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES web_projects(project_id),
    pseudonym VARCHAR(64) NOT NULL CHECK (pseudonym ~ '^[A-Za-z0-9_.-]{1,64}$'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id,pseudonym),
    UNIQUE (project_id,pseudonym,participant_uuid),
    UNIQUE (project_id,participant_uuid)
);
CREATE TABLE web_participant_visits (
    visit_uuid UUID PRIMARY KEY,
    project_id UUID NOT NULL,
    participant_uuid UUID NOT NULL,
    label VARCHAR(64) NOT NULL CHECK (label ~ '^[A-Za-z0-9_.-]{1,64}$'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id,participant_uuid)
        REFERENCES web_project_participants(project_id,participant_uuid),
    UNIQUE (project_id,participant_uuid,label),
    UNIQUE (project_id,participant_uuid,label,visit_uuid)
);
INSERT INTO web_project_participants(participant_uuid,project_id,pseudonym)
SELECT gen_random_uuid(),project_id,participant_id FROM web_invitations
GROUP BY project_id,participant_id;
INSERT INTO web_participant_visits(visit_uuid,project_id,participant_uuid,label)
SELECT gen_random_uuid(),i.project_id,p.participant_uuid,i.visit
FROM web_invitations i JOIN web_project_participants p
 ON (p.project_id,p.pseudonym)=(i.project_id,i.participant_id)
GROUP BY i.project_id,p.participant_uuid,i.visit;
ALTER TABLE web_invitations ADD COLUMN participant_uuid UUID;
ALTER TABLE web_invitations ADD COLUMN visit_uuid UUID;
UPDATE web_invitations i SET participant_uuid=p.participant_uuid,visit_uuid=v.visit_uuid
FROM web_project_participants p JOIN web_participant_visits v
 ON (v.project_id,v.participant_uuid)=(p.project_id,p.participant_uuid)
WHERE (i.project_id,i.participant_id,i.visit)=(p.project_id,p.pseudonym,v.label);
ALTER TABLE web_invitations ALTER COLUMN participant_uuid SET NOT NULL;
ALTER TABLE web_invitations ALTER COLUMN visit_uuid SET NOT NULL;
ALTER TABLE web_invitations ADD CONSTRAINT web_invitation_participant_fk
 FOREIGN KEY (project_id,participant_id,participant_uuid)
 REFERENCES web_project_participants(project_id,pseudonym,participant_uuid);
ALTER TABLE web_invitations ADD CONSTRAINT web_invitation_visit_fk
 FOREIGN KEY (project_id,participant_uuid,visit,visit_uuid)
 REFERENCES web_participant_visits(project_id,participant_uuid,label,visit_uuid);
ALTER TABLE web_invitations ADD CONSTRAINT web_invitation_session_project_unique UNIQUE (session_id,project_id);
ALTER TABLE web_assessments ADD CONSTRAINT web_assessment_session_project_fk
 FOREIGN KEY (session_id,project_id) REFERENCES web_invitations(session_id,project_id);

-- Nao fabricar ACK/hash de checkpoints para sessoes anteriores. Observacoes oficiais
-- existentes continuam em web_trial_observations, ligadas pela sessao original.
CREATE TABLE web_session_checkpoints (
    session_id UUID PRIMARY KEY REFERENCES web_participant_sessions(session_id),
    provenance JSONB NOT NULL CHECK (jsonb_typeof(provenance)='object'),
    confirmed_through SMALLINT NOT NULL CHECK (confirmed_through BETWEEN 1 AND 16),
    prefix_hash CHAR(64) NOT NULL CHECK (prefix_hash ~ '^[0-9a-f]{64}$'),
    received_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE web_session_observations (
    session_id UUID NOT NULL,
    trial_number SMALLINT NOT NULL,
    condition_id SMALLINT NOT NULL,
    payload JSONB NOT NULL CHECK (jsonb_typeof(payload)='object'),
    payload_sha256 CHAR(64) NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    received_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (session_id,trial_number),
    FOREIGN KEY (session_id,trial_number) REFERENCES web_session_main_order(session_id,trial_number),
    CHECK ((payload->>'trial_number')::integer=trial_number),
    CHECK ((payload->>'condition_id')::integer=condition_id)
);
ALTER TABLE web_session_main_order ADD CONSTRAINT web_order_position_condition_unique
 UNIQUE (session_id,trial_number,condition_id);
ALTER TABLE web_session_observations ADD CONSTRAINT web_observation_order_fk
 FOREIGN KEY (session_id,trial_number,condition_id)
 REFERENCES web_session_main_order(session_id,trial_number,condition_id);
CREATE TABLE web_session_invalidations (
    session_id UUID PRIMARY KEY REFERENCES web_participant_sessions(session_id),
    reason TEXT NOT NULL CHECK (reason IN (
        'focus_lost','visibility_hidden','escape','reload','page_closed',
        'timing_invalid','user_cancelled','integrity_conflict'
    )),
    source TEXT NOT NULL CHECK (source IN ('participant','professional','server')),
    event_at_ms DOUBLE PRECISION CHECK (event_at_ms >= 0 AND event_at_ms < 'Infinity'::float8),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    actor_id TEXT
);
