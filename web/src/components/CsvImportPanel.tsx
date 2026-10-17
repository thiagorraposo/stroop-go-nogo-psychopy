import { useEffect, useRef, useState } from 'react'
import type { ChangeEvent } from 'react'
import type { ProfessionalProfile } from '../api/client'
import { getCsvImportStatus, uploadCsvImport } from '../api/imports'
import type { CsvImportEvent } from '../api/imports'
import { ApiError, apiErrorMessage } from '../api/client'
import type { Project } from '../api/assessments'
import { CsvMinimizationError, minimizeCsv } from '../imports/minimize'

type Operation = {
  projectId: string; projectLabel: string; operationId: string
  event: CsvImportEvent | null; unknown: boolean
}

function outcome(event: CsvImportEvent): string {
  if (event.status === 'importado') return 'Importação concluída. Consulte os resultados deste projeto.'
  if (event.status === 'rejeitado' && event.error_code === 'duplicate_assessment') return 'Esta avaliação já existe. Nenhum dado foi substituído.'
  if (event.status === 'rejeitado') return 'Arquivo rejeitado. Confira o formato oficial e a minimização antes de tentar novamente.'
  if (event.status === 'recebido') return 'Arquivo recebido. A validação ainda não foi confirmada.'
  return 'Arquivo validado. A gravação ainda não foi confirmada.'
}

export function CsvImportPanel({ project, profile, onImported }: {
  project: Project; profile: ProfessionalProfile; onImported: () => void
}) {
  const [file, setFile] = useState<File | null>(null)
  const [operation, setOperation] = useState<Operation | null>(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const blob = useRef<Blob | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)
  const unresolved = operation !== null && (operation.unknown
    || operation.event?.status === 'recebido' || operation.event?.status === 'validado')

  useEffect(() => {
    setFile(null)
    if (fileInput.current) fileInput.current.value = ''
  }, [project.id])

  async function select(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.currentTarget.files?.[0] ?? null)
    setMessage(null)
    blob.current = null
    if (!unresolved) setOperation(null)
  }

  function received(event: CsvImportEvent, current: Operation) {
    setOperation({ ...current, event, unknown: false })
    setMessage(outcome(event))
    if (event.status === 'importado') {
      setFile(null); blob.current = null
      if (fileInput.current) fileInput.current.value = ''
      onImported()
    }
  }

  async function submit() {
    if (busy) return
    let current = operation
    if (!current || !unresolved) {
      if (!file) return
      try { blob.current = await minimizeCsv(file) }
      catch (error) {
        setMessage(error instanceof CsvMinimizationError ? error.message : 'Não foi possível preparar o arquivo.')
        return
      }
      current = {
        projectId: project.id, projectLabel: `${project.code} — ${project.name}`,
        operationId: crypto.randomUUID(), event: null, unknown: false,
      }
      setOperation(current)
    }
    if (!blob.current || current.projectId !== project.id
      && !window.confirm(`Esta operação continua vinculada ao projeto ${current.projectLabel}. Reenviar os mesmos dados?`)) return
    setBusy(true); setMessage('Enviando cópia minimizada…')
    try {
      const result = await uploadCsvImport(current.projectId, current.operationId, blob.current, profile)
      received(result, current)
    } catch {
      setOperation({ ...current, unknown: true })
      setMessage('O envio não foi confirmado. Consulte o estado antes de iniciar outra importação.')
    } finally { setBusy(false) }
  }

  async function checkStatus() {
    if (!operation || busy) return
    setBusy(true); setMessage('Consultando o estado da importação…')
    try {
      const result = await getCsvImportStatus(operation.projectId, operation.operationId)
      received(result, operation)
    } catch (error) {
      setMessage(error instanceof ApiError && error.status === 404
        ? 'Ainda não há confirmação para esta operação. Você pode reenviar a mesma cópia usando o mesmo identificador.'
        : apiErrorMessage(error))
      setOperation({ ...operation, unknown: true })
    } finally { setBusy(false) }
  }

  return <section className="csv-import-panel" aria-labelledby="csv-import-title">
    <h3 id="csv-import-title">Importar CSV</h3>
    <p>O arquivo original permanece no seu dispositivo. Antes do envio, o navegador cria uma cópia e substitui nome por <code>NAO_COLETADO</code> e iniciais por vazio.</p>
    <p className="quiet">Destino: <strong>{project.code} — {project.name}</strong>. São aceitos CSVs oficiais dos instrumentos registrados, UTF-8, até 5 MiB e 10.000 registros.</p>
    <label htmlFor="research-csv">Arquivo CSV (até 5 MiB)</label>
    <input ref={fileInput} id="research-csv" type="file" accept=".csv,text/csv" disabled={busy || Boolean(unresolved)} onChange={event => void select(event)} />
    {file && <p className="quiet">Arquivo selecionado: {Math.ceil(file.size / 1024)} KiB. Nome e conteúdo não são exibidos.</p>}
    {!unresolved && <button className="button primary" disabled={!file || busy || !project.active}
      onClick={() => void submit()}>{busy ? 'Importando…' : 'Minimizar e importar CSV'}</button>}
    {unresolved && <div className="csv-import-actions">
      <button className="button primary" disabled={busy || !blob.current} onClick={() => void submit()}>{busy ? 'Verificando…' : 'Reenviar a mesma cópia'}</button>{' '}
      <button className="button secondary" disabled={busy} onClick={() => void checkStatus()}>Consultar estado</button>
    </div>}
    {operation && <p className="quiet">Operação {operation.operationId} · {operation.projectLabel}</p>}
    {message && <p role={message.startsWith('O envio') || message.startsWith('Arquivo rejeitado') ? 'alert' : 'status'}>{message}</p>}
  </section>
}
