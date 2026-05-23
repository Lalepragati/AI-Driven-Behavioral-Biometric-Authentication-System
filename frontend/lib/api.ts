export type KeystrokeEvent = {
  key: string
  event_type: 'keydown' | 'keyup'
  timestamp: number
  code?: string
  is_error?: boolean
}

export type KeystrokeSample = {
  user_id: string
  session_id: string
  text?: string
  events: KeystrokeEvent[]
  context?: Record<string, unknown>
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export async function registerUser(payload: {
  user_id: string
  password: string
  role: string
  full_name?: string
  email?: string
}) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
  return handleResponse(response)
}

export async function submitLogin(payload: {
  user_id: string
  password: string
  sample: {
    user_id: string
    session_id: string
    text?: string
    events: KeystrokeEvent[]
    context?: Record<string, unknown>
  }
  failed_attempts?: number
}) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
  return handleResponse(response)
}

async function handleResponse(response: Response) {
  const body = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(body.detail ?? 'Request failed')
  }
  return body
}
