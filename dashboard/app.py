#!/usr/bin/env python3
"""Ponto de entrada e composicao do dashboard Stroop Go/No-Go."""

from __future__ import annotations

import os
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from dashboard.auth import (
    AppUser,
    AuthError,
    BlockedUserError,
    ExpiredIdentityError,
    ROLES,
    RateLimitedError,
    UnregisteredUserError,
    authorize,
    create_user,
    list_users,
    parse_identity,
    record_import_result,
    record_operation,
    update_user,
)

from dashboard.components import (
    format_percent,
    format_seconds,
    render_assessment_detail,
    render_assessment_table,
    render_charts,
    render_metric_card,
    render_summary_cards,
)
from dashboard.data_access import (
    DEFAULT_DB_PATH,
    REQUIRED_COLUMNS,
    REQUIRED_TABLES,
    DashboardDataError,
    connect_readonly,
    fetch_all_rows,
    load_sqlite_data,
    table_columns,
    validate_schema,
)
from dashboard.instrumentos import instrument_view, supported_codes
from dashboard.transformations import (
    AGGREGATED_COLUMNS,
    METRIC_CODES,
    DashboardFilters,
    accuracy_by_visit,
    build_assessment_table,
    calculate_cards,
    count_by_date,
    error_type_counts,
    errors_by_project,
    filter_assessment_table,
    filtered_csv_bytes,
    matches_selection,
    metric_map,
    metrics_for_assessment,
    numeric_values,
    option_values,
    parse_iso_date,
    participant_evolution,
    to_dataframe,
    trials_for_assessment,
    visible_assessment_rows,
)
from scripts.upload_local import MAX_BYTES, process_upload


DISCLAIMER_TEXT = (
    "Resultados descritivos. Este dashboard não representa avaliação clínica ou diagnóstico."
)


def _claims(streamlit_module: Any) -> dict[str, Any]:
    try:
        return dict(streamlit_module.user.to_dict())
    except (AttributeError, TypeError):
        return {}


def _is_logged_in(streamlit_module: Any) -> bool:
    try:
        return bool(streamlit_module.user.is_logged_in)
    except AttributeError:
        return False


def _render_login(streamlit_module: Any) -> None:
    streamlit_module.title("Acesso ao dashboard")
    streamlit_module.info("Entre com a conta Google previamente autorizada.")
    if streamlit_module.button("Entrar com Google"):
        streamlit_module.login("google")


def _render_denied(
    streamlit_module: Any,
    claims: Mapping[str, Any],
    error: AuthError,
) -> None:
    streamlit_module.title("Acesso ao dashboard")
    if isinstance(error, UnregisteredUserError):
        streamlit_module.error("Conta Google nao cadastrada para este sistema.")
        try:
            identity = parse_identity(claims)
        except AuthError:
            identity = None
        if identity is not None:
            streamlit_module.caption(
                "Informe estes identificadores ao administrador para o cadastro manual:"
            )
            streamlit_module.code(
                f"iss={identity.issuer}\nsub={identity.subject}", language=None
            )
    elif isinstance(error, ExpiredIdentityError):
        streamlit_module.error("Sessao expirada. Entre novamente.")
    elif isinstance(error, BlockedUserError):
        streamlit_module.error("Conta bloqueada.")
    elif isinstance(error, RateLimitedError):
        streamlit_module.error("Acesso temporariamente limitado.")
    else:
        streamlit_module.error("Acesso nao autorizado.")
    if streamlit_module.button("Encerrar sessao"):
        streamlit_module.logout()


def _authorize_or_stop(streamlit_module: Any, action: str) -> tuple[AppUser, dict[str, Any]] | None:
    claims = _claims(streamlit_module)
    try:
        user = authorize(os.environ.get("AUTH_DATABASE_URL", ""), claims, action)
    except AuthError as exc:
        _render_denied(streamlit_module, claims, exc)
        return None
    return user, claims


def _render_session_sidebar(streamlit_module: Any, user: AppUser) -> None:
    streamlit_module.sidebar.caption(f"Perfil: {user.role}")
    if user.email:
        streamlit_module.sidebar.caption(f"Conta: {user.email}")
    if streamlit_module.sidebar.button("Encerrar sessao"):
        streamlit_module.logout()


def available_sections(user: AppUser) -> list[str]:
    sections = ["Resultados"]
    if user.role in {"importacao", "administracao"}:
        sections.append("Importacao")
    if user.role == "administracao":
        sections.append("Administracao")
    return sections


def _protected_export(
    claims: Mapping[str, Any],
    rows: list[dict[str, Any]],
    metric_codes: tuple[str, ...] | None,
) -> bytes:
    database_url = os.environ.get("AUTH_DATABASE_URL", "")
    try:
        user = authorize(database_url, claims, "export_dashboard")
        payload = filtered_csv_bytes(rows, metric_codes)
        record_operation(database_url, user, "export_dashboard", "success")
        return payload
    except AuthError:
        return b""


def _render_upload(streamlit_module: Any, claims: Mapping[str, Any]) -> None:
    streamlit_module.header("Importar CSV")
    streamlit_module.caption(
        "Um CSV UTF-8 de ate 5 MiB. O temporario e removido ao finalizar."
    )
    uploaded = streamlit_module.file_uploader("Arquivo CSV", type=["csv"])
    if not streamlit_module.button("Validar e importar", disabled=uploaded is None):
        return
    try:
        user = authorize(
            os.environ.get("AUTH_DATABASE_URL", ""), claims, "import_csv"
        )
        if uploaded is None or not 0 < uploaded.size <= MAX_BYTES:
            raise ValueError
        result = process_upload(
            uploaded.getvalue(),
            uploaded.name,
            os.environ.get("DATABASE_URL", ""),
            origin="upload autenticado",
        )
        outcome = "success" if result["statuses"][-1] == "importado" else "rejected"
        try:
            record_import_result(
                os.environ.get("AUTH_DATABASE_URL", ""),
                result["id"],
                result["content_sha256"],
                result["status"],
                result["error_code"],
            )
        except AuthError:
            # A importacao ja foi processada; nao a reapresente como rejeitada.
            streamlit_module.error(
                "Importacao processada, mas o registro de auditoria nao foi confirmado. "
                "Nao repita o arquivo sem verificar o estado."
            )
            return
        record_operation(
            os.environ.get("AUTH_DATABASE_URL", ""), user, "import_csv", outcome
        )
        if outcome == "success":
            streamlit_module.success("Importacao concluida.")
        else:
            streamlit_module.error(result["message"])
    except (AuthError, ValueError):
        streamlit_module.error("Importacao nao autorizada ou arquivo rejeitado.")


def _render_user_admin(streamlit_module: Any, claims: Mapping[str, Any]) -> None:
    streamlit_module.header("Usuarios e permissoes")
    try:
        actor = authorize(
            os.environ.get("AUTH_DATABASE_URL", ""), claims, "manage_users"
        )
        users = list_users(os.environ.get("AUTH_DATABASE_URL", ""))
    except AuthError:
        streamlit_module.error("Operacao administrativa nao autorizada.")
        return

    streamlit_module.dataframe(
        [
            {
                "iss": user.issuer,
                "sub": user.subject,
                "email_auxiliar": user.email,
                "perfil": user.role,
                "ativo": user.active,
            }
            for user in users
        ],
        use_container_width=True,
        hide_index=True,
    )

    with streamlit_module.form("create-user"):
        streamlit_module.subheader("Cadastrar usuario")
        issuer = streamlit_module.text_input(
            "iss", value="https://accounts.google.com", key="create-issuer"
        )
        subject = streamlit_module.text_input("sub", key="create-subject")
        email = streamlit_module.text_input(
            "E-mail auxiliar (opcional)", key="create-email"
        )
        role = streamlit_module.selectbox("Perfil", ROLES, key="create-role")
        submitted = streamlit_module.form_submit_button("Cadastrar")
    if submitted:
        try:
            actor = authorize(
                os.environ.get("AUTH_DATABASE_URL", ""), claims, "manage_users"
            )
            create_user(
                os.environ.get("AUTH_DATABASE_URL", ""),
                issuer.strip(),
                subject.strip(),
                role,
                email.strip() or None,
                actor,
            )
            streamlit_module.success("Usuario cadastrado.")
            streamlit_module.rerun()
        except AuthError as exc:
            try:
                record_operation(
                    os.environ.get("AUTH_DATABASE_URL", ""),
                    actor,
                    "manage_users",
                    "failure",
                )
            except AuthError:
                pass
            streamlit_module.error(str(exc))

    if not users:
        return
    labels = [f"{user.subject} | {user.role}" for user in users]
    selected_label = streamlit_module.selectbox("Alterar usuario", labels)
    selected = users[labels.index(selected_label)]
    with streamlit_module.form("update-user"):
        updated_email = streamlit_module.text_input(
            "E-mail auxiliar", value=selected.email or "", key="update-email"
        )
        updated_role = streamlit_module.selectbox(
            "Perfil", ROLES, index=ROLES.index(selected.role), key="update-role"
        )
        updated_active = streamlit_module.checkbox(
            "Conta ativa", value=selected.active, key="update-active"
        )
        updated = streamlit_module.form_submit_button("Salvar alteracoes")
    if updated:
        try:
            actor = authorize(
                os.environ.get("AUTH_DATABASE_URL", ""), claims, "manage_users"
            )
            update_user(
                os.environ.get("AUTH_DATABASE_URL", ""),
                selected.issuer,
                selected.subject,
                role=updated_role,
                active=updated_active,
                email=updated_email.strip() or None,
                actor=actor,
            )
            streamlit_module.success("Usuario atualizado.")
            streamlit_module.rerun()
        except AuthError as exc:
            try:
                record_operation(
                    os.environ.get("AUTH_DATABASE_URL", ""),
                    actor,
                    "manage_users",
                    "failure",
                )
            except AuthError:
                pass
            streamlit_module.error(str(exc))


def _render_results(
    streamlit_module: Any,
    claims: Mapping[str, Any],
    db_path: Path,
) -> None:
    """Compoe a interface Streamlit com dados e componentes modulares."""
    st = streamlit_module
    st.header("Resultados")

    try:
        data = load_sqlite_data(db_path)
        assessment_rows = build_assessment_table(data)
    except DashboardDataError as exc:
        st.error(str(exc))
        return
    except sqlite3.Error as exc:
        st.error(f"Erro ao ler SQLite: {exc}")
        return

    dates = [parse_iso_date(row["assessment_date"]) for row in assessment_rows]
    valid_dates = [value for value in dates if value is not None]
    min_date = min(valid_dates) if valid_dates else None
    max_date = max(valid_dates) if valid_dates else None

    st.sidebar.header("Filtros")
    start_date = st.sidebar.date_input(
        "Inicio", value=min_date, min_value=min_date, max_value=max_date
    )
    end_date = st.sidebar.date_input(
        "Fim", value=max_date, min_value=min_date, max_value=max_date
    )

    filters = DashboardFilters(
        start_date=start_date if isinstance(start_date, date) else None,
        end_date=end_date if isinstance(end_date, date) else None,
        project=tuple(
            st.sidebar.multiselect("Projeto", option_values(assessment_rows, "project"))
        ),
        participant_id=tuple(
            st.sidebar.multiselect(
                "Participant ID", option_values(assessment_rows, "participant_id")
            )
        ),
        participant_name=tuple(
            st.sidebar.multiselect(
                "Participant name", option_values(assessment_rows, "participant_name")
            )
        ),
        visit=tuple(
            st.sidebar.multiselect("Visita", option_values(assessment_rows, "visit"))
        ),
        evaluator=tuple(
            st.sidebar.multiselect(
                "Avaliador", option_values(assessment_rows, "evaluator")
            )
        ),
        test_code=(
            st.sidebar.selectbox(
                "Instrumento",
                [code for code in supported_codes() if code in option_values(assessment_rows, "test_code")],
            ),
        ),
        test_version=tuple(
            st.sidebar.multiselect(
                "Versao", option_values(assessment_rows, "test_version")
            )
        ),
    )

    filtered_rows = filter_assessment_table(assessment_rows, filters)
    if not filtered_rows:
        st.info("Nenhuma avaliacao encontrada para os filtros selecionados.")
        return

    view = instrument_view(filters.test_code[0])
    render_summary_cards(st, filtered_rows, view)
    render_charts(st, filtered_rows, view)
    metric_codes = None if view.code == "stroop_go_nogo_ptbr" else view.metric_codes
    render_assessment_table(
        st,
        filtered_rows,
        view,
        export_factory=lambda: _protected_export(claims, filtered_rows, metric_codes),
    )
    render_assessment_detail(st, data, filtered_rows, view)


def render_dashboard(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Autentica, autoriza e compoe as areas permitidas do dashboard."""
    import streamlit as st

    st.set_page_config(
        page_title="Dashboard Stroop Go/No-Go",
        page_icon="ST",
        layout="wide",
    )
    if not _is_logged_in(st):
        _render_login(st)
        return

    authorized = _authorize_or_stop(st, "view_dashboard")
    if authorized is None:
        return
    user, claims = authorized

    st.title("Dashboard Stroop Go/No-Go")
    st.warning(DISCLAIMER_TEXT)
    _render_session_sidebar(st, user)
    sections = available_sections(user)
    initial = os.environ.get("STROOP_INITIAL_SECTION", "")
    index = sections.index(initial) if initial in sections else 0
    section = st.sidebar.radio("Area", sections, index=index)
    if section == "Resultados":
        _render_results(st, claims, db_path)
    elif section == "Importacao":
        _render_upload(st, claims)
    else:
        _render_user_admin(st, claims)


def main() -> None:
    render_dashboard(DEFAULT_DB_PATH)


if __name__ == "__main__":
    main()
