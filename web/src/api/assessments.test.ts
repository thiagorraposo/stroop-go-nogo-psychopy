import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { exportAssessment, getAssessment, getAssessmentOptions, listAssessments, listProjects } from './assessments';

const projectId = '00000000-0000-4000-8000-000000000001';
const project = { id: projectId, code: 'P_SINTETICO', name: 'Pesquisa sintética', active: true,
  created_at: '2026-10-16T12:00:00+00:00' };
const summary = { accuracy: 50, response_time_seconds: 0.5, total_trials: 16,
  accuracy_go_trials: 50, accuracy_no_go_trials: 50, total_go_trials: 8, total_no_go_trials: 8,
  hits: 4, omission_errors: 4, commission_errors: 4, correct_rejections: 4 };
const item = { assessment_id: 'A_SINTETICA', participant_id: 'P_SINTETICO', visit: 'V1',
  evaluator_id: null, created_at: '2026-10-16T12:00:00Z', started_at: '2026-10-16T11:00:00',
  platform: 'psychopy', test_code: 'stroop_go_nogo_ptbr', test_version: 'legacy',
  protocol_id: null, app_version: null, summary };
const trial = { trial_number: 1, condition_id: null, word: 'AZUL', ink_color: 'blue',
  condition: 'congruent', correct_response: 'space', key_pressed: 'space', correct: true,
  error_type: 'hit', trial_start_ms: null, stimulus_onset_ms: null, stimulus_offset_ms: null,
  trial_end_ms: null, key_at_ms: null, reaction_time_ms: null, reaction_time_seconds: 0.5 };
const detail = { ...item, project_id: projectId, session_id: null, completed_at: null,
  metrics: [{ metric_code: 'hits', metric_label: 'Acertos', metric_value: 4, unit: 'count' }],
  frame_period_ms: null, trials: [trial] };
const filename = 'stroop_go_nogo_ptbr_2026-10-16_12h00m00s_trials.csv';
let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>;
function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}
beforeEach(() => { fetchMock = vi.fn<typeof fetch>(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); vi.restoreAllMocks(); });

describe('consulta profissional paginada', () => {
  it('lista projetos sem dados de identidade e preserva transporte seguro', async () => {
    fetchMock.mockResolvedValue(json({ items: [project], next_cursor: 'cursor_sintetico' }));
    await expect(listProjects({ limit: 100 })).resolves.toEqual({ items: [project], next_cursor: 'cursor_sintetico' });
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/projects?limit=100', expect.objectContaining({
      method: 'GET', credentials: 'same-origin', cache: 'no-store', redirect: 'error', headers: { Accept: 'application/json' },
    }));
  });
  it('envia somente filtros canonicos e cursor opaco junto ao mesmo projeto', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ items: [item], next_cursor: null }), { headers: { 'X-Assessment-Snapshot': 'snapshot_sintetico' } }));
    await expect(listAssessments(projectId, { participant_id: 'P_1', visit: 'V.1', cursor: 'opaco_1', limit: 100 }))
      .resolves.toEqual({ items: [item], next_cursor: null, snapshot: 'snapshot_sintetico' });
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/v1/projects/${projectId}/assessments?limit=100&cursor=opaco_1&participant_id=P_1&visit=V.1`);
  });
  it('recusa snapshot malformado e preserva paginas antigas sem cabecalho', async () => {
    fetchMock.mockResolvedValue(json({ items: [], next_cursor: null }));
    await expect(listAssessments(projectId)).resolves.toEqual({ items: [], next_cursor: null });
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ items: [], next_cursor: null }), { headers: { 'X-Assessment-Snapshot': 'https://externo.invalid' } }));
    await expect(listAssessments(projectId)).rejects.toMatchObject({ code: 'invalid_response' });
  });
  it('conserva metricas genericas sem fabricar resumo Stroop', async () => {
    const generic = { ...item, test_code: 'outro_teste', summary: { metrics: { response_time: 12, items: 3 } } };
    fetchMock.mockResolvedValue(json({ items: [generic], next_cursor: null }));
    await expect(listAssessments(projectId)).resolves.toMatchObject({ items: [generic] });
  });
  it.each([
    { items: [{ ...project, email: 'sintetico@example.invalid' }], next_cursor: null },
    { items: [project], next_cursor: 'https://externo.invalid' },
    { items: [{ ...project, created_at: '2026-02-30T12:00:00Z' }], next_cursor: null },
    { items: [project], next_cursor: null, participant_name: 'SINTETICO' },
  ])('recusa pagina/projeto com dados ou formato inesperados %#', async (body) => {
    fetchMock.mockResolvedValue(json(body));
    await expect(listProjects()).rejects.toMatchObject({ code: 'invalid_response' });
  });
  it.each([
    { ...item, participant_name: 'SINTETICO' }, { ...item, initials: 'SS' },
    { ...item, summary: { ...summary, name: 'SINTETICO' } },
    { ...item, summary: { ...summary, accuracy: 101 } },
  ])('recusa dados pessoais/campos desconhecidos na avaliacao %#', async (value) => {
    fetchMock.mockResolvedValue(json({ items: [value], next_cursor: null }));
    await expect(listAssessments(projectId)).rejects.toMatchObject({ code: 'invalid_response' });
  });
  it('recusa filtros/ids/limites invalidos antes da rede', async () => {
    for (const invoke of [() => listProjects({ limit: 101 }), () => listProjects({ cursor: '../x' }),
      () => listAssessments('https://externo.invalid'), () => listAssessments(projectId, { participant_id: 'codigo\ncontrole' }),
      () => getAssessment(projectId, '../segredo'), () => exportAssessment(projectId, '..')]) {
      expect(invoke).toThrowError(expect.objectContaining({ code: 'invalid_request' }));
    }
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
describe('detalhe e CSV autenticados', () => {
  it('aceita proveniencia e tempos nulos legados sem converter horario civil', async () => {
    fetchMock.mockResolvedValue(json(detail));
    await expect(getAssessment(projectId, item.assessment_id)).resolves.toEqual(detail);
  });
  it.each([
    { ...detail, project_id: '00000000-0000-4000-8000-000000000002' },
    { ...detail, assessment_id: 'OUTRA' },
    { ...detail, trials: [{ ...trial, participant_name: 'SINTETICO' }] },
    { ...detail, metrics: [{ ...detail.metrics[0], source_file: 'privado.csv' }] },
    { ...detail, trials: [{ ...trial, trial_number: 2 }] },
    { ...detail, metrics: [...detail.metrics, ...detail.metrics] },
  ])('recusa detalhe extra, fora de escopo ou inconsistente %#', async (value) => {
    fetchMock.mockResolvedValue(json(value));
    await expect(getAssessment(projectId, item.assessment_id)).rejects.toMatchObject({ code: 'invalid_response' });
  });
  it('baixa CSV como blob e nome canonico, reconsultando a rota autenticada', async () => {
    fetchMock.mockResolvedValue(new Response('colunas\r\nsintetico\r\n', { headers: {
      'Content-Type': 'text/csv; charset=utf-8', 'Content-Disposition': `attachment; filename="${filename}"`,
    } }));
    const result = await exportAssessment(projectId, item.assessment_id);
    expect(result.filename).toBe(filename); expect(result.blob.size).toBeGreaterThan(0);
    expect(fetchMock).toHaveBeenCalledWith(`/api/v1/projects/${projectId}/assessments/A_SINTETICA/export`,
      expect.objectContaining({ credentials: 'same-origin', redirect: 'error', cache: 'no-store', method: 'GET' }));
  });
  it.each([
    ['text/html', `attachment; filename="${filename}"`, 'html'],
    ['text/csv', 'attachment; filename="../../pessoa.csv"', 'csv'],
    ['text/csv', 'inline', 'csv'], ['text/csv', `attachment; filename="${filename}"`, ''],
  ])('recusa tipo/nome/conteudo de exportacao inseguro %#', async (type, disposition, content) => {
    fetchMock.mockResolvedValue(new Response(content, { headers: { 'Content-Type': type, 'Content-Disposition': disposition } }));
    await expect(exportAssessment(projectId, item.assessment_id)).rejects.toMatchObject({ code: 'invalid_response' });
  });
  it('fecha mensagens externas, preserva 401/403/429 e cancelamento', async () => {
    for (const [status, code] of [[401, 'authentication_required'], [403, 'permission_denied'], [429, 'rate_limited']] as const) {
      fetchMock.mockResolvedValue(new Response('dados privados', { status, headers: { 'Retry-After': '12' } }));
      await expect(listProjects()).rejects.toMatchObject({ code, status, retryAfter: status === 429 ? 12 : null });
    }
    const abort = new AbortController(); abort.abort(); fetchMock.mockClear();
    await expect(listProjects({ signal: abort.signal })).rejects.toMatchObject({ code: 'request_cancelled' });
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('cancela exportacao durante leitura do corpo sem liberar arquivo parcial', async () => {
    const abort = new AbortController();
    const response = new Response('csv', { headers: { 'Content-Type': 'text/csv', 'Content-Disposition': `attachment; filename="${filename}"` } });
    vi.spyOn(response, 'blob').mockImplementation(() => new Promise(() => undefined));
    fetchMock.mockResolvedValue(response);
    const result = exportAssessment(projectId, item.assessment_id, abort.signal);
    await Promise.resolve(); abort.abort();
    await expect(result).rejects.toMatchObject({ code: 'request_cancelled' });
  });
});

describe('filtros completos e facetas autorizadas W15A', () => {
  const facets = { participant_id: ['P_SINTETICO'], visit: ['V1', 'V2'], evaluator_id: ['LEGADO_NAO_MAPEADO', 'avaliador_sintetico'],
    test_version: ['1.0.0', '1.0.0+web'], platform: ['web', 'psychopy'], test_code: ['stroop_go_nogo_ptbr'] };
  it('envia valores repetidos sem juntar delimitadores e contexto de datas inclusivas', async () => {
    fetchMock.mockResolvedValue(json({ items: [], next_cursor: null }));
    await listAssessments(projectId, { start_date: '2026-10-01', end_date: '2026-10-17',
      participant_id: ['P_1', 'P_2'], visit: ['V1', 'V2'], evaluator_id: ['LEGADO_NAO_MAPEADO', 'avaliador_sintetico'],
      test_version: ['1.0.0+web', 'legacy'], platform: ['web', 'psychopy'], test_code: 'stroop_go_nogo_ptbr' });
    const url = new URL(String(fetchMock.mock.calls[0]?.[0]), 'https://synthetic.invalid');
    expect(url.pathname).toBe(`/api/v1/projects/${projectId}/assessments`);
    expect(url.searchParams.get('start_date')).toBe('2026-10-01'); expect(url.searchParams.get('end_date')).toBe('2026-10-17');
    expect(url.searchParams.getAll('participant_id')).toEqual(['P_1', 'P_2']);
    expect(url.searchParams.getAll('visit')).toEqual(['V1', 'V2']);
    expect(url.searchParams.getAll('evaluator_id')).toEqual(['LEGADO_NAO_MAPEADO', 'avaliador_sintetico']);
    expect(url.searchParams.getAll('test_version')).toEqual(['1.0.0+web', 'legacy']);
    expect(url.searchParams.getAll('platform')).toEqual(['web', 'psychopy']);
    expect(url.searchParams.getAll('test_code')).toEqual(['stroop_go_nogo_ptbr']);
  });
  it.each([
    { start_date: '2026-02-30' }, { end_date: '2026-10-17T00:00:00Z' },
    { start_date: '2026-10-18', end_date: '2026-10-17' }, { participant_id: ['P'.repeat(513)] },
    { participant_id: ['P_1', 'P_1'] }, { participant_id: ['   '] }, { visit: ['  '] }, { visit: ['codigo\ncontrole'] }, { evaluator_id: ['../privado'] },
    { test_version: ['v'.repeat(65)] }, { platform: ['externa'] }, { test_code: '../privado' },
    { visit: Array.from({ length: 101 }, (_, i) => `V${i}`) },
  ])('rejeita filtro invalido antes da rede %#', options => {
    expect(() => listAssessments(projectId, options as Parameters<typeof listAssessments>[1]))
      .toThrowError(expect.objectContaining({ code: 'invalid_request' }));
    expect(fetchMock).not.toHaveBeenCalled();
  });
  it('consulta facetas do projeto com somente periodo/instrumento', async () => {
    fetchMock.mockResolvedValue(json(facets));
    await expect(getAssessmentOptions(projectId, { start_date: '2026-10-01', end_date: '2026-10-17', test_code: 'stroop_go_nogo_ptbr' }))
      .resolves.toEqual(facets);
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/v1/projects/${projectId}/assessments/options?start_date=2026-10-01&end_date=2026-10-17&test_code=stroop_go_nogo_ptbr`);
  });
  it.each([
    { ...facets, participant_name: ['SINTETICO'] }, { ...facets, participant_id: ['   '] }, { ...facets, visit: ['  '] }, { ...facets, visit: ['V1', 'V1'] },
    { ...facets, platform: ['externa'] }, { ...facets, evaluator_id: ['pessoa@example.invalid'] },
    { ...facets, test_version: ['segredo\n'] }, { ...facets, test_code: [null] },
    { ...facets, participant_id: Array.from({ length: 201 }, (_, i) => `P_${i}`) },
    { ...facets, participant_id: null }, {},
  ])('rejeita faceta fora do contrato fechado %#', body => {
    fetchMock.mockResolvedValue(json(body));
    return expect(getAssessmentOptions(projectId)).rejects.toMatchObject({ code: 'invalid_response' });
  });
  it('facetas vazias sao validas e cancelamento nao inicia requisicao', async () => {
    const empty = { participant_id: [], visit: [], evaluator_id: [], test_version: [], platform: [], test_code: [] };
    fetchMock.mockResolvedValue(json(empty)); await expect(getAssessmentOptions(projectId)).resolves.toEqual(empty);
    const abort = new AbortController(); abort.abort(); fetchMock.mockClear();
    await expect(getAssessmentOptions(projectId, { signal: abort.signal })).rejects.toMatchObject({ code: 'request_cancelled' });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

 it('consulta preserva identificadores historicos com espacos e vazio significa sem restricao', async () => {
 fetchMock.mockResolvedValue(json({ items: [], next_cursor: null }));
 await listAssessments(projectId, {participant_id: ['P sintetico legado'], visit: [], platform: []});
 expect(String(fetchMock.mock.calls[0]?.[0])).toContain('participant_id=P+sintetico+legado');
 expect(String(fetchMock.mock.calls[0]?.[0])).not.toContain('visit=');
 });

describe('summary profissional Go/No-Go W15B', () => {
  it('exige os onze campos e aceita proporcoes distintas por condicao', async () => {
    const values = { ...summary, accuracy: 62.5, hits: 6, omission_errors: 2,
      correct_rejections: 4, commission_errors: 4, accuracy_go_trials: 75, accuracy_no_go_trials: 50 };
    fetchMock.mockResolvedValue(json({ items: [{ ...item, summary: values }], next_cursor: null }));
    await expect(listAssessments(projectId)).resolves.toMatchObject({ items: [{ summary: values }] });
  });
  it.each([
    { ...summary, total_go_trials: 7 }, { ...summary, total_no_go_trials: 7 },
    { ...summary, accuracy_go_trials: 51 }, { ...summary, accuracy_no_go_trials: 49 },
    { ...summary, accuracy_go_trials: null }, { ...summary, accuracy_no_go_trials: null },
    { ...summary, accuracy_go_trials: -1 }, { ...summary, accuracy_no_go_trials: 101 },
    { ...summary, accuracy_go_trials: '50' }, { ...summary, total_go_trials: 8.5 },
    { ...summary, total_no_go_trials: -1 },
    { accuracy: 50, response_time_seconds: 0.5, total_trials: 16,
      hits: 4, omission_errors: 4, commission_errors: 4, correct_rejections: 4 },
  ])('recusa shape antigo ou projecao Go/No-Go inconsistente %#', async values => {
    fetchMock.mockResolvedValue(json({ items: [{ ...item, summary: values }], next_cursor: null }));
    await expect(listAssessments(projectId)).rejects.toMatchObject({ code: 'invalid_response' });
  });
  it.each([
    { ...summary, accuracy: 50, total_trials: 8, total_go_trials: 0, total_no_go_trials: 8,
      hits: 0, omission_errors: 0, commission_errors: 4, correct_rejections: 4,
      accuracy_go_trials: null, accuracy_no_go_trials: 50, response_time_seconds: null },
    { ...summary, accuracy: 50, total_trials: 8, total_go_trials: 8, total_no_go_trials: 0,
      hits: 4, omission_errors: 4, commission_errors: 0, correct_rejections: 0,
      accuracy_go_trials: 50, accuracy_no_go_trials: null, response_time_seconds: 0.5 },
  ])('preserva precisao ausente quando nao ha tentativas da condicao %#', async values => {
    fetchMock.mockResolvedValue(json({ items: [{ ...item, summary: values }], next_cursor: null }));
    await expect(listAssessments(projectId)).resolves.toMatchObject({ items: [{ summary: values }] });
    const incorrect = { ...values, ...(values.total_go_trials === 0 ? { accuracy_go_trials: 0 } : { accuracy_no_go_trials: 0 }) };
    fetchMock.mockResolvedValue(json({ items: [{ ...item, summary: incorrect }], next_cursor: null }));
    await expect(listAssessments(projectId)).rejects.toMatchObject({ code: 'invalid_response' });
  });
});
