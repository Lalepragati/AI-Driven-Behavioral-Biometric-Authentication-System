export function MetricCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_24px_80px_rgba(0,0,0,0.24)] backdrop-blur-xl">
      <div className="text-[0.72rem] uppercase tracking-[0.26em] text-slate-400">{label}</div>
      <div className="mt-2 text-3xl font-semibold text-white">{value}</div>
      <p className="mt-2 text-sm leading-6 text-slate-300">{detail}</p>
    </div>
  )
}
