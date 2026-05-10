import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Overview from './pages/Overview'
import Prediction from './pages/Prediction'
import Methodology from './pages/Methodology'
import Team from './pages/Team'

function App() {
  return (
    <div className="relative isolate min-h-screen overflow-hidden bg-[var(--bg-primary)] text-[var(--text-primary)] font-dm transition-colors duration-300">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 right-[-8rem] h-[28rem] w-[28rem] rounded-full bg-brand/10 blur-3xl dark:bg-brand/20" />
        <div className="absolute top-[28rem] left-[-10rem] h-[24rem] w-[24rem] rounded-full bg-gold/10 blur-3xl dark:bg-gold/15" />
        <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-black/[0.03] to-transparent dark:from-white/[0.02]" />
      </div>

      <div className="relative z-10">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/overview" element={<Overview />} />
            <Route path="/prediction" element={<Prediction />} />
            <Route path="/methodology" element={<Methodology />} />
            <Route path="/team" element={<Team />} />
          </Routes>
        </main>

        <footer className="mt-20 border-t border-black/5 bg-white/40 py-12 backdrop-blur-md dark:border-white/5 dark:bg-white/[0.02]">
          <div className="mx-auto max-w-7xl px-6 text-center">
            <p className="text-sm font-dm font-medium opacity-50">
              Réalisé dans le cadre du cours de machine learning 2 à l'ENSAE de Dakar.
            </p>
            <div className="mt-4 flex items-center justify-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-brand-glow animate-pulse" />
              <span className="text-[10px] font-bold uppercase tracking-widest opacity-45">Modèle actif · GradientBoosting</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
