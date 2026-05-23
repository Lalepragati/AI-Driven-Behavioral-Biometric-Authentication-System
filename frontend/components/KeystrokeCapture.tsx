"use client"

import { useId, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { submitLogin } from '@/lib/api'

export type KeystrokeEvent = {
  key: string
  event_type: 'keydown' | 'keyup'
  timestamp: number
  code?: string
  is_error?: boolean
}

type LoginResult = {
  user_id: string
  session_id: string
  risk_score: number
  decision: string
  anomaly_confidence: number
  token?: string | null
  explanation: string
  model_kind: string
  signals: Record<string, number>
}

export function KeystrokeCapture({ onResult }: { onResult: (result: LoginResult) => void }) {
  const [userId, setUserId] = useState('doctor.singh')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState<'idle' | 'capturing' | 'submitting' | 'error' | 'success'>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [sampleCount, setSampleCount] = useState(0)
  const sessionId = useId().replace(/:/g, '')
  const eventsRef = useRef<KeystrokeEvent[]>([])

  const recordEvent = (event: KeyboardEvent<HTMLInputElement>, eventType: 'keydown' | 'keyup') => {
    setStatus('capturing')
    const shouldFlagError = event.key === 'Backspace' || event.key === 'Delete'
    eventsRef.current.push({
      key: event.key,
      event_type: eventType,
      timestamp: performance.now(),
      code: event.code,
      is_error: shouldFlagError,
    })
    setSampleCount(eventsRef.current.length)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setStatus('submitting')
    setErrorMessage('')
    try {
      const response = await submitLogin({
        user_id: userId,
        password,
        sample: {
          user_id: userId,
          session_id: sessionId,
          text: password,
          events: eventsRef.current,
          context: {
            source: 'nextjs-dashboard',
            sample_count: eventsRef.current.length,
          },
        },
        failed_attempts: 0,
      })
      onResult(response)
      setStatus('success')
      eventsRef.current = []
      setSampleCount(0)
    } catch (submitError) {
      setStatus('error')
      setErrorMessage(submitError instanceof Error ? submitError.message : 'Unable to authenticate')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-[28px] border border-white/10 bg-white/5 p-6 shadow-[0_28px_90px_rgba(0,0,0,0.28)] backdrop-blur-2xl">
      <div>
        <div className="text-[0.72rem] uppercase tracking-[0.28em] text-cyan-300/80">Behavioral Access</div>
        <h2 className="mt-3 text-2xl font-semibold text-white">Continuous typing signal capture</h2>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          Capture keystroke rhythm while the operator authenticates. The password field doubles as a privacy-safe behavioral sample source.
        </p>
      </div>

      <label className="block space-y-2">
        <span className="text-sm font-medium text-slate-200">User ID</span>
        <input
          value={userId}
          onChange={(event) => setUserId(event.target.value)}
          className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-cyan-300/70 focus:ring-2 focus:ring-cyan-300/20"
          placeholder="doctor.singh"
        />
      </label>

      <label className="block space-y-2">
        <span className="text-sm font-medium text-slate-200">Password</span>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          onKeyDown={(event) => recordEvent(event, 'keydown')}
          onKeyUp={(event) => recordEvent(event, 'keyup')}
          className="w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-white outline-none transition focus:border-cyan-300/70 focus:ring-2 focus:ring-cyan-300/20"
          placeholder="Enter password"
        />
      </label>

      <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">Session {sessionId.slice(0, 8)}</span>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">{sampleCount} events captured</span>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">{status}</span>
      </div>

      {errorMessage ? <div className="rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{errorMessage}</div> : null}

      <button
        type="submit"
        className="w-full rounded-2xl bg-gradient-to-r from-cyan-300 to-emerald-400 px-4 py-3 font-semibold text-slate-950 transition hover:brightness-110"
      >
        Analyze login behavior
      </button>
    </form>
  )
}
