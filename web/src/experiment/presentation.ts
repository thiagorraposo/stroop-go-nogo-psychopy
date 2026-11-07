import { PROTOCOL } from './protocol'

/** DOM do plugin: nenhuma renderização React ou fonte temporal própria. */
export function createExperimentHud(block: 'practice' | 'main', total: number) {
  const element = document.createElement('div')
  element.className = `${block}-hud experiment-hud`
  const progress = document.createElement('div')
  progress.className = 'experiment-progress'
  const label = document.createElement('span')
  label.dataset.hud = 'progress'
  const track = document.createElement('div')
  track.className = 'experiment-progress-track'
  track.setAttribute('role', 'progressbar')
  track.setAttribute('aria-label', block === 'practice' ? 'Progresso da prática' : 'Progresso do bloco principal')
  track.setAttribute('aria-valuemin', '0')
  track.setAttribute('aria-valuemax', String(total))
  const fill = document.createElement('span')
  track.append(fill)
  progress.append(label, track)
  element.append(progress)
  const time = block === 'main' ? document.createElement('span') : null
  if (time) {
    time.dataset.hud = 'time'
    time.className = 'experiment-timer'
    element.append(time)
  }
  let renderedCompleted = -1
  let renderedSecond = -1
  return { element, update(completed: number, elapsed = 0) {
    if (renderedCompleted !== completed) {
      label.textContent = `${block === 'practice' ? 'Prática' : 'Bloco principal'} · ${completed} / ${total}`
      track.setAttribute('aria-valuenow', String(completed))
      fill.style.width = `${completed / total * 100}%`
      renderedCompleted = completed
    }
    if (time) {
      const seconds = Math.floor(Math.min(PROTOCOL.main.duration_ms, Math.max(0, elapsed)) / 1000)
      if (renderedSecond !== seconds) {
        time.textContent = `Tempo: ${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`
        renderedSecond = seconds
      }
    }
  } }
}
