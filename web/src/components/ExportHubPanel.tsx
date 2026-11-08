import { useState, useEffect } from 'react'
import type { ProfessionalProfile } from '../api/client'
import type { Project } from '../api/assessments'
import {
  previewExport,
  downloadExport,
  type ExportGranularity,
  type IdentificationMode,
  type ExportPreviewResponse,
} from '../api/exports'

const GRANULARITY_OPTIONS: {
  id: ExportGranularity
  title: string
  description: string
  columns: string[]
}[] = [
  {
    id: 'pacientes',
    title: 'Pacientes',
    description: 'Dados cadastrais, código PAT-..., status e data de criação.',
    columns: ['patient_id', 'participant_code', 'participant_name', 'initials', 'active', 'created_at'],
  },
  {
    id: 'avaliacoes',
    title: 'Avaliações',
    description: 'Metadados de sessão, datas, projeto, avaliador e status de conclusão.',
    columns: [
      'assessment_id',
      'project_id',
      'project_code',
      'participant_code',
      'participant_name',
      'evaluator_code',
      'evaluator_name',
      'visit',
      'started_at',
      'completed_at',
      'platform',
      'test_code',
      'test_version',
    ],
  },
  {
    id: 'tentativas',
    title: 'Tentativas',
    description: 'Registro individual de cada tentativa com palavra, cor, condição, tecla e RT.',
    columns: [
      'assessment_id',
      'project_code',
      'participant_code',
      'participant_name',
      'visit',
      'trial_number',
      'block',
      'word',
      'ink_color',
      'condition',
      'correct_response',
      'key_pressed',
      'correct',
      'error_type',
      'reaction_time_seconds',
    ],
  },
  {
    id: 'metricas',
    title: 'Métricas',
    description: 'As 12 métricas oficiais do Stroop com valores, rótulos e unidades padronizadas.',
    columns: [
      'assessment_id',
      'project_code',
      'participant_code',
      'participant_name',
      'visit',
      'metric_code',
      'metric_label',
      'metric_value',
      'unit',
    ],
  },
  {
    id: 'stroop_21_colunas',
    title: 'Stroop 21 colunas',
    description: 'Formato clássico canônico compatível com PsychoPy Builder e scripts históricos.',
    columns: [
      'participant_id',
      'participant_name',
      'session',
      'date',
      'expName',
      'psychopyVersion',
      'frameRate',
      'OS',
      'trial_number',
      'word',
      'ink_color',
      'condition',
      'correct_response',
      'key_pressed',
      'key_at',
      'reaction_time',
      'correct',
      'error_type',
      'trial_start',
      'stimulus_onset',
      'stimulus_offset',
    ],
  },
]

type Props = {
  profile: ProfessionalProfile
  project: Project | null
}

export function ExportHubPanel({ profile, project }: Props) {
  const [granularity, setGranularity] = useState<ExportGranularity>('avaliacoes')
  const [mode, setMode] = useState<IdentificationMode>('deidentified')
  const [selectedColumns, setSelectedColumns] = useState<string[]>([])
  const [preview, setPreview] = useState<ExportPreviewResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const currentGranularityOption = GRANULARITY_OPTIONS.find(g => g.id === granularity)!

  // Ao mudar de granularidade, reseta as colunas para o catálogo padrão
  useEffect(() => {
    setSelectedColumns([...currentGranularityOption.columns])
    setPreview(null)
    setError(null)
    setMessage(null)
  }, [granularity])

  const toggleColumn = (col: string) => {
    setSelectedColumns(prev =>
      prev.includes(col) ? prev.filter(c => c !== col) : [...prev, col]
    )
    setPreview(null)
  }

  const selectAllColumns = () => {
    setSelectedColumns([...currentGranularityOption.columns])
    setPreview(null)
  }

  const handlePreview = async () => {
    if (!project) {
      setError('Selecione um projeto para pré-visualizar a exportação.')
      return
    }
    setLoading(true)
    setError(null)
    setMessage(null)
    try {
      const res = await previewExport(
        {
          project_id: project.id,
          granularity,
          columns: selectedColumns,
          identification_mode: mode,
        },
        profile.csrf_token,
      )
      setPreview(res)
      setMessage(`Pré-visualização gerada: ${res.total_rows} registro(s) encontrado(s).`)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao gerar pré-visualização.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!project || !preview) return
    setDownloading(true)
    setError(null)
    try {
      const { filename, blob } = await downloadExport(
        {
          project_id: project.id,
          granularity,
          columns: selectedColumns,
          identification_mode: mode,
          export_token: preview.export_token,
        },
        profile.csrf_token,
      )
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      setMessage(`Arquivo ${filename} baixado com sucesso.`)
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao baixar arquivo CSV.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="export-hub-panel" aria-label="Central de exportações multi-granularidade">
      <h2>Central de exportações avançada (REQ-CSV-005)</h2>
      <p className="quiet">
        Granularidades e políticas de exportação (REQ-CSV-005). Exportação estruturada em formato CSV com escolha de granularidade, seleção de colunas e
        controle de privacidade.
      </p>

      {/* 1. Escolha de Granularidade */}
      <fieldset className="export-section">
        <legend>1. Granularidade dos dados</legend>
        <div className="granularity-cards">
          {GRANULARITY_OPTIONS.map(opt => (
            <label
              key={opt.id}
              className={`granularity-card ${granularity === opt.id ? 'active' : ''}`}
            >
              <input
                type="radio"
                name="granularity"
                value={opt.id}
                checked={granularity === opt.id}
                onChange={() => setGranularity(opt.id)}
              />
              <strong>{opt.title}</strong>
              <p className="quiet">{opt.description}</p>
            </label>
          ))}
        </div>
      </fieldset>

      {/* 2. Modo de Identificação */}
      <fieldset className="export-section">
        <legend>2. Modo de identificação (Privacidade e DEC-03)</legend>
        <div className="mode-options">
          <label>
            <input
              type="radio"
              name="id_mode"
              value="deidentified"
              checked={mode === 'deidentified'}
              onChange={() => {
                setMode('deidentified')
                setPreview(null)
              }}
            />
            <span>
              <strong>Desidentificado (padrão seguro)</strong>: utiliza códigos PAT-... e EVA-...
              sem expor nomes nominais ou iniciais.
            </span>
          </label>
          <label>
            <input
              type="radio"
              name="id_mode"
              value="nominal"
              disabled={profile.role !== 'administracao'}
              checked={mode === 'nominal'}
              onChange={() => {
                setMode('nominal')
                setPreview(null)
              }}
            />
            <span>
              <strong>Nominal (restrito à Administração)</strong>: inclui nomes completos e
              iniciais, mediante autorização e habilitação institucional.
            </span>
          </label>
        </div>
      </fieldset>

      {/* 3. Seleção de Colunas */}
      <fieldset className="export-section">
        <legend>
          3. Colunas da granularidade ({selectedColumns.length}/{currentGranularityOption.columns.length})
        </legend>
        <div className="column-actions">
          <button type="button" className="button secondary" onClick={selectAllColumns}>
            Selecionar todas
          </button>
        </div>
        <div className="columns-grid">
          {currentGranularityOption.columns.map(col => (
            <label key={col} className="column-checkbox">
              <input
                type="checkbox"
                checked={selectedColumns.includes(col)}
                onChange={() => toggleColumn(col)}
              />
              <code>{col}</code>
            </label>
          ))}
        </div>
      </fieldset>

      {/* 4. Ações de Prévia e Download */}
      <div className="export-actions">
        <button
          type="button"
          className="button secondary"
          disabled={loading || selectedColumns.length === 0 || !project}
          onClick={() => void handlePreview()}
        >
          {loading ? 'Consultando contagem…' : 'Pré-visualizar contagem e amostra'}
        </button>

        <button
          type="button"
          className="button primary"
          disabled={downloading || !preview || preview.total_rows === 0}
          onClick={() => void handleDownload()}
        >
          {downloading ? 'Baixando CSV…' : `Baixar arquivo CSV (${preview?.total_rows ?? 0} registros)`}
        </button>
      </div>

      {error && <p role="alert" className="notice error">{error}</p>}
      {message && <p role="status" className="notice success">{message}</p>}

      {/* 5. Tabela de Amostra da Pré-visualização */}
      {preview && (
        <section className="export-preview-section" aria-label="Pré-visualização da exportação">
          <h3>Amostra dos dados ({preview.sample_rows.length} de {preview.total_rows} registros)</h3>
          {preview.sample_rows.length === 0 ? (
            <p role="status">Nenhum registro encontrado para os critérios selecionados.</p>
          ) : (
            <div className="table-scroll">
              <table>
                <caption>Amostra da exportação ({preview.applied_criteria.granularity})</caption>
                <thead>
                  <tr>
                    {preview.columns.map(col => (
                      <th key={col}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.sample_rows.map((row, idx) => (
                    <tr key={idx}>
                      {preview.columns.map(col => (
                        <td key={col} className="tabular-nums">
                          {String(row[col] ?? '')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* 6. Aviso de Segurança */}
      <div className="notice" role="region" aria-label="Proteção contra Formula Injection">
        <strong>Proteção ativa contra CSV Formula Injection:</strong>
        <p className="quiet">
          Células iniciadas por =, +, -, @, tabulação ou quebras de linha são neutralizadas
          automaticamente com prefixo seguro antes da serialização, garantindo conformidade com
          planilhas externas (Excel, LibreOffice, SPSS).
        </p>
      </div>
    </div>
  )
}
