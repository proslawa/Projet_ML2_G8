import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Zap, BarChart3, Brain, Users, Home, Sun, Moon } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/overview', label: 'Overview', icon: BarChart3 },
  { path: '/prediction', label: 'Prédiction', icon: Brain },
  { path: '/methodology', label: 'Méthodologie', icon: Zap },
  { path: '/team', label: 'Équipe', icon: Users }
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark') || 
             localStorage.getItem('theme') === 'dark'
    }
    return true
  })

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark])

  const toggleTheme = () => setIsDark(!isDark)

  return (
    <motion.nav
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="nav-glass fixed top-0 left-0 right-0 z-50 px-6 py-3"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-3 group">
          <img 
            src="/assets/fortuneoo_logo.png" 
            alt="Fortuneo ChurnScore" 
            className="h-9 w-auto object-contain drop-shadow-md group-hover:drop-shadow-lg transition-all duration-300"
          />
        </NavLink>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) =>
                `relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  isActive
                    ? 'text-inherit active-link font-semibold'
                    : 'text-inherit opacity-60 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5'
                }`
              }
            >
              <Icon size={15} />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-4">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-black/5 dark:bg-white/5 text-inherit opacity-70 hover:opacity-100 transition-all"
            aria-label="Toggle theme"
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {/* Status badge */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-subtle border border-brand/20">
            <div className="w-1.5 h-1.5 rounded-full bg-brand-glow animate-pulse" />
            <span className="text-brand-glow text-xs font-medium">Modèle en ligne</span>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
            aria-controls="mobile-menu"
            className="md:hidden p-2 text-inherit opacity-70 hover:opacity-100 transition-colors"
          >
            {open ? (
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" />
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <rect y="3" width="20" height="2" rx="1" />
                <rect y="9" width="20" height="2" rx="1" />
                <rect y="15" width="20" height="2" rx="1" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {open && (
        <motion.div
          id="mobile-menu"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden mt-2 bg-white dark:bg-slate-900 border-t border-black/5 dark:border-slate-700/20 rounded-b-2xl shadow-xl"
        >
          <div className="px-4 py-4 flex flex-col gap-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <NavLink
                key={path}
                to={path}
                end={path === '/'}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                    isActive ? 'text-inherit bg-black/5 dark:bg-brand-subtle' : 'text-inherit opacity-70 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5'
                  }`
                }
              >
                <Icon size={16} />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        </motion.div>
      )}
    </motion.nav>
  )
}
