-- Vinculo explicito para consulta WEB de projetos locais existentes.
-- Nao preencher por coincidencia de nomes/codigos: somente operacao autorizada.
CREATE TABLE web_legacy_project_links (
    legacy_project TEXT PRIMARY KEY CHECK (btrim(legacy_project) <> ''),
    project_id UUID NOT NULL REFERENCES web_projects(project_id),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_web_legacy_project_links_active
    ON web_legacy_project_links(project_id) WHERE active;
