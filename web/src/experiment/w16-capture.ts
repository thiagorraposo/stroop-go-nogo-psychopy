/** Opt-in guard for the local synthetic timing evidence tool. */
export function w16CaptureEnabled(buildFlag: string | undefined, search: string): boolean {
  return buildFlag === 'synthetic-only' && new URLSearchParams(search).get('w16') === '1'
}
