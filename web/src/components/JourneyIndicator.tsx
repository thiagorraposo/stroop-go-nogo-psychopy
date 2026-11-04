const stages = ['Orientações', 'Convite', 'Prática', 'Tarefa']

export function JourneyIndicator({ current }: { current: 1 | 2 | 3 | 4 }) {
  return <ol className="journey-indicator" aria-label="Etapas da participação">
    {stages.map((label, index) => {
      const number = index + 1
      return <li key={label} aria-current={number === current ? 'step' : undefined}>
        <span className="journey-number" aria-hidden="true">{String(number).padStart(2, '0')}</span>
        <span>{label}</span>
      </li>
    })}
  </ol>
}
