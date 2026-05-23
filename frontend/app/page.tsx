"use client"

import { useState } from 'react'
import { ShieldCheck, AlertTriangle, Fingerprint, Activity } from 'lucide-react'

import { KeystrokeCapture } from '@/components/KeystrokeCapture'
import { MetricCard } from '@/components/MetricCard'
import { RiskTrendChart } from '@/components/charts/RiskTrendChart'

const demoScores = [12, 18, 25, 34, 42]

export default function HomePage() {
  const [riskScore, setRiskScore] = useState(18)
  const [decision, setDecision] = useState('allow')
  const [explanation, setExplanation] = useState('Ready to evaluate the next hospital login session.')
  const [scores, setScores] = useState<number[]>(demoScores)

  return (
    <main className="relative min-h-screen overflow-hidden px-6 py-8 text-white lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-8">
        <header className="flex flex-col gap-4 rounded-[32px] border border-white/10 bg-white/5 p-6 shadow-glow backdrop-blur-2xl lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-4 py-1 text-xs uppercase tracking-[0.28em] text-cyan-200">
              Offline-first hospital security console
            </div>
            <div>
              <h1 className="max-w-3xl text-4xl font-semibold leading-tight lg:text-6xl">
                Behavioral authentication for high-trust clinical operations.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300 lg:text-lg">
                This module captures typing behavior, scores session risk locally, and explains the result with an Ollama-backed security summary.
              </p>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 lg:w-[28rem] lg:grid-cols-1">
            <MetricCard label="Risk score" value={`${riskScore}/100`} detail="Higher scores trigger step-up or block decisions." />
            <MetricCard label="Decision" value={decision.toUpperCase()} detail="Derived from the local risk engine." />
            <MetricCard label="Mode" value="LOCAL AI" detail="Detection stays on-device; explanations are generated via Ollama." />
          </div>
        </header>

        <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <KeystrokeCapture
            onResult={(result) => {
              setRiskScore(Math.round(result.risk_score))
              setDecision(result.decision)
              setExplanation(result.explanation)
              setScores((current) => [...current.slice(-4), Math.round(result.risk_score)])
            }}
          />

          <div className="space-y-6">
            <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 shadow-[0_28px_90px_rgba(0,0,0,0.28)] backdrop-blur-2xl">
              <div className="flex items-center gap-3 text-cyan-300">
                <Fingerprint size={20} />
                <span className="text-sm uppercase tracking-[0.26em]">Security Summary</span>
              </div>
              <p className="mt-4 text-lg leading-8 text-slate-100">{explanation}</p>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-slate-950/70 p-6 shadow-[0_28px_90px_rgba(0,0,0,0.28)] backdrop-blur-2xl">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="text-sm uppercase tracking-[0.28em] text-slate-400">Risk trend</div>
                  <h3 className="mt-2 text-xl font-semibold">Recent authentication sessions</h3>
                </div>
                <Activity className="text-emerald-300" />
              </div>
              <div className="mt-6 h-72">
                <RiskTrendChart scores={scores} />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <div className="flex items-center gap-3 text-emerald-300">
                  <ShieldCheck size={18} />
                  <span className="text-sm uppercase tracking-[0.24em]">Allow zone</span>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-300">0-30 keeps sessions active without interruption.</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <div className="flex items-center gap-3 text-amber-300">
                  <AlertTriangle size={18} />
                  <span className="text-sm uppercase tracking-[0.24em]">Escalation zone</span>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-300">31-70 requests step-up verification before continuation.</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
