import type { MainTimingTrace } from '../experiment/main-engine'

type Props = { traces: MainTimingTrace[]; onClear: () => void }

/** Local-only evidence helper, rendered only in an explicitly opted-in build and URL. */
export function W16TimingCapturePanel({ traces, onClear }: Props) {
  function download() {
    const evidence = {
      schema: 'stroop-w16-timing-batch-v1',
      environment: {
        user_agent: navigator.userAgent,
        platform: navigator.platform,
        viewport: { width: innerWidth, height: innerHeight },
        screen: { width: screen.width, height: screen.height, color_depth: screen.colorDepth },
        device_pixel_ratio: devicePixelRatio,
        captured_at: new Date().toISOString(),
      },
      replicas: traces.map((trace, index) => ({ replica: index + 1, trace })),
    }
    const url = URL.createObjectURL(new Blob([JSON.stringify(evidence, null, 2)], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'w16_timing_traces.json'
    link.click()
    URL.revokeObjectURL(url)
  }
  return <aside aria-label="Captura técnica W16" style={{ position: 'fixed', zIndex: 20, right: 8, bottom: 8,
    maxWidth: 310, padding: 10, background: '#fff', color: '#111', border: '1px solid #555', fontSize: 12 }}>
    <strong>Captura W16 · somente sintética</strong>
    <p>Não use convites ou dados de participantes. Tentativas interrompidas também são preservadas nesta memória local.</p>
    <p role="status">Réplicas nesta aba: {traces.length}</p>
    <button type="button" onClick={download} disabled={!traces.length}>Exportar JSON</button>{' '}
    <button type="button" onClick={onClear} disabled={!traces.length}>Limpar</button>
  </aside>
}
