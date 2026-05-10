/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Fond principal — gris clair/blanc (style Fortuneo)
        slate: {
          950: '#0B0F0D',
          900: '#0E1410',
          800: '#131A15',
          700: '#1A2420',
          600: '#213029',
          500: '#2C3F36'
        },
        // Accent vert Fortuneo vibrant
        brand: {
          DEFAULT: '#7AC94F',
          light: '#8FD65F',
          glow: '#7AC94F',
          subtle: '#E8F5EE'
        },
        // Or/accent secondaire (Fortuneo style)
        gold: {
          DEFAULT: '#7AC94F',
          light: '#8FD65F',
          dark: '#5FA83E'
        },
        // Texte et surface secondaires
        ink: {
          100: '#E8EDE9',
          200: '#C4CEC6',
          400: '#7A9180',
          600: '#4A5E52'
        }
      },
      fontFamily: {
        syne: ['Syne', 'sans-serif'],
        dm: ['DM Sans', 'sans-serif']
      },
      backdropBlur: {
        xs: '2px'
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        gradient: 'gradient 8s ease infinite',
        shimmer: 'shimmer 2s linear infinite'
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' }
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' }
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' }
        }
      }
    }
  },
  plugins: []
}
