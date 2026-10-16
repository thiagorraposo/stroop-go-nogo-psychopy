import { expect, test } from 'vitest'
import { checkEnvironment } from './environment'
import { PRACTICE_CONDITIONS, PROTOCOL, parsePracticeSource } from './protocol'
import practiceSource from '../../../condicoes/pratica_stroop_go_nogo_ptbr.csv?raw'

test.each([
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/155.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/155.0.0.0 Edg/155.0.0.0',
  'Mozilla/5.0 (X11; Linux x86_64; rv:157.0) Gecko/20100101 Firefox/157.0',
])('aceita familias desktop aprovadas: %s', ua => { expect(checkEnvironment(ua).supported).toBe(true) })

test.each([
  '', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) Chrome/155.0.0.0',
  'Mozilla/5.0 (Linux; Android 15) Chrome/155.0.0.0 Mobile',
  'Mozilla/5.0 (iPad; CPU OS 18_0) AppleWebKit/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 Safari/605.1.15',
  'Mozilla/5.0 (X11; CrOS x86_64) Chrome/155.0.0.0',
  'Mozilla/5.0 (X11; Linux x86_64) Chrome/155.0.0.0 Safari/537.36 OPR/130.0.0.0',
])('recusa ambiente fora do MVP: %s', ua => { expect(checkEnvironment(ua).supported).toBe(false) })

test('pool de pratica vem das quatro linhas-fonte com a paleta efetiva aprovada', () => {
  expect(PRACTICE_CONDITIONS.map(row => row.condition_id)).toEqual([1, 2, 3, 4])
  expect(PRACTICE_CONDITIONS.filter(row => row.correct_response === 'space')).toHaveLength(2)
  expect(PRACTICE_CONDITIONS[0]?.ink_color_display).toBe('#40FF00')
  expect(PRACTICE_CONDITIONS[1]?.ink_color_display).toBe('#9A24FF')
  expect(PROTOCOL.practice).toMatchObject({ reminder_ms: 1500, trials: 4, fixation_ms: 300,
    stimulus_window_ms: 2000, blank_interval_ms: 500, feedback_ms: 500 })
  expect(PROTOCOL.countdown_segment_ms).toBe(550)
  expect(() => parsePracticeSource(practiceSource.replace('trial_number', 'changed_header'))).toThrow()
  expect(() => parsePracticeSource(practiceSource.replace('1,VERDE', '2,VERDE'))).toThrow()
})
