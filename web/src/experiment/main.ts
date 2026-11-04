import { initJsPsych, ParameterType } from 'jspsych'
import type { JsPsych, JsPsychPlugin } from 'jspsych'
import { createMainRuntime } from './main-engine'
import type { MainOptions, MainResult } from './main-engine'
import type { InterruptionReason } from './protocol'

export type { MainOptions, MainResult, MainTrial } from './main-engine'

const info = { name: 'stroop-main-block', version: '0.1.0', parameters: {},
  data: { completed_trials: { type: ParameterType.INT } } } as const

/** Runtime jsPsych real. Somente o callback da aplicacao recebe o resultado em RAM. */
export function mountMain(container: HTMLDivElement, options: MainOptions): () => void {
  let active = true
  let started = false
  let cleanupRuntime: (() => void) | undefined
  let result: MainResult | undefined
  const root = document.createElement('div')
  container.replaceChildren(root)
  const onClose = () => interrupted('page_closed')
  const jsPsych = initJsPsych({
    display_element: root, use_webaudio: false, show_progress_bar: false, on_close: onClose,
    on_finish: () => {
      release()
      if (active && result) { active = false; options.onComplete(result) }
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
    result = undefined
    release()
    if (started) jsPsych.abortExperiment()
    root.remove()
    options.onInterrupted(reason)
  }
  class MainPlugin implements JsPsychPlugin<typeof info> {
    static info = info
    constructor(private instance: JsPsych) {}
    trial(display: HTMLElement) {
      started = true
      if (!active) { this.instance.finishTrial(); return }
      cleanupRuntime = createMainRuntime(display, { ...options,
        onComplete: value => {
          if (!active) return
          result = value
          this.instance.finishTrial({ completed_trials: value.trials.length })
        }, onInterrupted: interrupted,
      })
    }
  }
  function run() {
    if (!active) return
    void jsPsych.run({ timeline: [{ type: MainPlugin }], conditional_function: () => active })
      .catch(() => interrupted('timing_invalid')).finally(() => { release() })
  }
  if (document.readyState === 'complete') run()
  else window.addEventListener('load', run, { once: true })
  return () => {
    active = false
    result = undefined
    release()
    if (started) { started = false; jsPsych.abortExperiment() }
    root.remove()
  }
}
