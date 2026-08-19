/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        vbc: {
          navy: {
            DEFAULT: '#0B1E36', // Primary Navy Text / Dark headers
            light: '#1B3B5F',
            dark: '#05101E',
          },
          blue: {
            DEFAULT: '#2563EB', // Blue accent
            light: '#EFF6FF', // Light gray/blue backgrounds
            medium: '#3B82F6',
          },
          green: {
            DEFAULT: '#10B981', // Good standing
            light: '#ECFDF5',
            dark: '#047857',
          },
          orange: {
            DEFAULT: '#F97316', // Needs attention
            light: '#FFF7ED',
            dark: '#C2410C',
          },
          red: {
            DEFAULT: '#EF4444', // At risk
            light: '#FEF2F2',
            dark: '#B91C1C',
          },
          gray: {
            DEFAULT: '#6B7280',
            light: '#F3F4F6',
            hover: '#E5E7EB',
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        dropdown: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      }
    },
  },
  plugins: [],
}
