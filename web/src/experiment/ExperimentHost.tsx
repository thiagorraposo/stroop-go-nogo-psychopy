import { useEffect, useRef } from 'react'

export type MountExperiment = (container: HTMLDivElement) => () => void

/** O motor imperativo controla quadros/teclado; React controla somente o ciclo de vida. */
export function ExperimentHost({ mount }: { mount: MountExperiment }) {
  const host = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (host.current) return mount(host.current)
  }, [mount])
  return <div ref={host} className="experiment-host" aria-label="Tarefa experimental" />
}
