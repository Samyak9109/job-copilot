/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#7C3AED',
          600: '#7C3AED',
          700: '#6D28D9',
          50: '#F5F3FF',
          100: '#EDE9FE',
        },
        accent: '#EC4899',
        ink: '#0F172A',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(16,24,40,0.04), 0 8px 24px -12px rgba(16,24,40,0.12)',
      },
      borderRadius: {
        xl: '0.9rem',
        '2xl': '1.15rem',
      },
    },
  },
  plugins: [],
}
