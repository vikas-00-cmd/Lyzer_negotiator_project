/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        buyer: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        vendor: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        status: {
          pending: '#f59e0b',
          progress: '#3b82f6',
          accepted: '#22c55e',
          deadlock: '#ef4444',
        },
      },
    },
  },
  plugins: [],
}
