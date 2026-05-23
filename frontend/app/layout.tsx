import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Behavioral Authentication Console',
  description: 'Offline-first behavioral biometric authentication dashboard',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
