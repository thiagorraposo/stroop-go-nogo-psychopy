export type EnvironmentCheck = { supported: boolean; reason: 'mobile' | 'system' | 'browser' | null }

/** Verificacao local conservadora; nao comprova hardware nem equivale a homologacao. */
export function checkEnvironment(userAgent: string): EnvironmentCheck {
  if (/Android|iPhone|iPad|iPod|Mobile|Tablet|Windows Phone/i.test(userAgent)) return { supported: false, reason: 'mobile' }
  if (!/Windows NT|Linux/i.test(userAgent) || /Macintosh|Mac OS X|CrOS/i.test(userAgent)) return { supported: false, reason: 'system' }
  if (/(?:OPR|Opera|Vivaldi|SamsungBrowser|YaBrowser)\//i.test(userAgent)
    || !/(?:Chrome|Chromium|Edg|Firefox)\/\d+/i.test(userAgent)) return { supported: false, reason: 'browser' }
  return { supported: true, reason: null }
}
