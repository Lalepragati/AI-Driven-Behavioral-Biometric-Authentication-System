import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          50: '#f5f7fb',
          100: '#e6ebf5',
          200: '#c9d4ea',
          300: '#a6b7db',
          400: '#7e93c5',
          500: '#5a73a9',
          600: '#43598c',
          700: '#33446d',
          800: '#23304d',
          900: '#101a2b',
        },
        aurora: '#67e8f9',
        pulse: '#22c55e',
        flame: '#f97316',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(103,232,249,0.16), 0 20px 60px rgba(15,23,42,0.45)',
      },
      backgroundImage: {
        'dashboard-grid': 'radial-gradient(circle at 1px 1px, rgba(148,163,184,0.18) 1px, transparent 0)',
      },
    },
  },
  plugins: [],
}

export default config
