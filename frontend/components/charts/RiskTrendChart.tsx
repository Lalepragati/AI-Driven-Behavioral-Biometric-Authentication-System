"use client"

import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip, Legend } from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip, Legend)

export function RiskTrendChart({ scores }: { scores: number[] }) {
  const labels = scores.map((_, index) => `S${index + 1}`)
  const data = {
    labels,
    datasets: [
      {
        label: 'Risk score',
        data: scores,
        tension: 0.38,
        borderColor: '#67e8f9',
        backgroundColor: 'rgba(103, 232, 249, 0.16)',
        pointBackgroundColor: '#22c55e',
        fill: true,
      },
    ],
  }

  return <Line data={data} options={{ responsive: true, plugins: { legend: { labels: { color: '#dbe7f6' } } }, scales: { x: { ticks: { color: '#9db0cf' }, grid: { color: 'rgba(148,163,184,0.12)' } }, y: { min: 0, max: 100, ticks: { color: '#9db0cf' }, grid: { color: 'rgba(148,163,184,0.12)' } } } }} />
}
