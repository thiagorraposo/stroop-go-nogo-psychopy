import { initJsPsych, ParameterType } from 'jspsych'
import type { JsPsych, JsPsychPlugin } from 'jspsych'
import { PRACTICE_CONDITIONS } from './protocol'
import type { InterruptionReason, PracticeSummary } from './protocol'
import { createPracticeRuntime } from './practice-engine'
import type { PracticeOptions } from './practice-engine'

/** Plugin real do jsPsych; uma rodada contem quatro tentativas de treino. */
const info = {
  name: 'stroop-practice-round', version: '0.1.0', parameters: {},
  data: { correct: { type: ParameterType.INT }, total: { type: ParameterType.INT } },
} as const

export function mountPractice(container: HTMLDivElement, options: PracticeOptions): () => void {
  let active = true
  let started = false
  let cleanupRuntime: (() => void) | undefined
  let summary: PracticeSummary | undefined
  const root = document.createElement('div')
  container.replaceChildren(root)
  const onClose = () => interrupted('page_closed')
  const jsPsych = initJsPsych({
    display_element: root, use_webaudio: false, show_progress_bar: false,
    on_close: onClose,
    on_finish: () => {
      release()
      if (active && summary) {
        active = false
        options.onComplete(summary)
      }
    },
  })

  function release() {
    cleanupRuntime?.()
    jsPsych.pluginAPI.cancelAllKeyboardResponses()
    jsPsych.pluginAPI.clearAllTimeouts()
    jsPsych.data.removeInteractionListeners()
    window.removeEventListener('beforeunload', onClose)
    window.removeEventListener('load', run)
  }

  function interrupted(reason: InterruptionReason) {
    if (!active) return
    active = false
    release()
    if (started) jsPsych.abortExperiment()
    root.remove()
    options.onInterrupted(reason)
  }

  class PracticePlugin implements JsPsychPlugin<typeof info> {
    static info = info
    constructor(private instance: JsPsych) {}
    trial(display: HTMLElement) {
      started = true
      if (!active) { this.instance.finishTrial(); return }
      cleanupRuntime = createPracticeRuntime(display,
        jsPsych.randomization.shuffle([...PRACTICE_CONDITIONS]), {
          ...options,
          onComplete: result => {
            if (!active) return
            summary = result
            this.instance.finishTrial(result)
          },
          onInterrupted: interrupted,
        })
    }
  }

  function run() {
    if (!active) return
    void jsPsych.run({ timeline: [{ type: PracticePlugin }], conditional_function: () => active })
      .catch(() => interrupted('timing_invalid'))
      .finally(() => { release() })
  }
  // Evita criar a espera interna nao cancelavel de prepareDom() do jsPsych.
  // A espera local e removida mesmo se React desmontar antes do window.load.
  if (document.readyState === 'complete') run()
  else window.addEventListener('load', run, { once: true })

  return () => {
    if (!active) { release(); root.remove(); return }
    active = false
    release()
    if (started) jsPsych.abortExperiment()
    root.remove()
  }
}
