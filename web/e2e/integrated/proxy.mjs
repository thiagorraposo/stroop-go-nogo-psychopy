// Proxy de teste local; nao e configuracao de hospedagem/produção.
import { createServer } from 'node:https'
import { request } from 'node:http'
import { readFileSync, existsSync } from 'node:fs'
import { dirname, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
// integrated -> e2e -> web -> dist
const dist = resolve(dirname(fileURLToPath(import.meta.url)), '../../dist')
const securityHeaders = JSON.parse(readFileSync(resolve(dist, '../security-headers.json'), 'utf8'))
const mime = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml' }
const server = createServer({ key: readFileSync(process.env.STROOP_TEST_TLS_KEY), cert: readFileSync(process.env.STROOP_TEST_TLS_CERT) }, (incoming, outgoing) => {
  const pathname = new URL(incoming.url, 'https://127.0.0.1:4373').pathname
  if (pathname.startsWith('/api/') || pathname.startsWith('/health/')) {
    const upstream = request({ host: '127.0.0.1', port: 4381, path: incoming.url, method: incoming.method,
      headers: { ...incoming.headers, 'x-forwarded-proto': 'https',
        'x-forwarded-for': incoming.socket.remoteAddress ?? '127.0.0.1' } }, response => {
      outgoing.writeHead(response.statusCode, response.headers)
      response.pipe(outgoing)
    })
    upstream.on('error', () => {
      if (!outgoing.headersSent) outgoing.writeHead(503, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' })
      outgoing.end('{"error":{"code":"service_unavailable"}}')
    })
    incoming.pipe(upstream)
    return
  }
  let file
  try { file = resolve(dist, '.' + decodeURIComponent(pathname)) }
  catch { outgoing.writeHead(400); outgoing.end(); return }
  if (file !== dist && !file.startsWith(dist + sep)) { outgoing.writeHead(404); outgoing.end(); return }
  if (!existsSync(file) || pathname === '/') file = resolve(dist, 'index.html')
  const extension = file.slice(file.lastIndexOf('.'))
  try {
    const content = readFileSync(file)
    outgoing.writeHead(200, { ...securityHeaders, 'Content-Type': mime[extension] ?? 'application/octet-stream', 'Cache-Control': 'no-store' })
    outgoing.end(content)
  } catch { outgoing.writeHead(404); outgoing.end() }
})
server.listen(4373, '127.0.0.1')
process.on('SIGTERM', () => { server.close(() => process.exit(0)); setTimeout(() => process.exit(0), 1500).unref() })
