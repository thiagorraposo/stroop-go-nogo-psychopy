/** Deriva os headers da fonte WEB canonica; executado somente no build. */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
const headers = JSON.parse(readFileSync(new URL('../security-headers.json', import.meta.url), 'utf8'))
const expected = ['Content-Security-Policy', 'X-Content-Type-Options', 'X-Frame-Options', 'Referrer-Policy', 'Cross-Origin-Resource-Policy', 'Permissions-Policy']
if (Object.keys(headers).length !== expected.length || expected.some(key => typeof headers[key] !== 'string'
  || /["\\\r\n$]/.test(headers[key]))) throw new Error('Headers WEB invalidos para Nginx.')
const directory = process.argv[2]
if (!directory) throw new Error('Diretorio de saida obrigatorio.')
mkdirSync(directory, { recursive: true })
function emit(name, values) {
  const lines = Object.entries(values).map(([key, value]) => `add_header ${key} "${value}" always;`)
  lines.push('add_header Strict-Transport-Security "$web_hsts" always;')
  writeFileSync(`${directory}/${name}`, `${lines.join('\n')}\n`)
}
emit('web-headers.conf', { ...headers, 'Cache-Control': 'no-store' })
emit('error-headers.conf', { ...headers, 'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'", 'Cache-Control': 'no-store' })
emit('proxy-headers.conf', { 'Permissions-Policy': headers['Permissions-Policy'] })
