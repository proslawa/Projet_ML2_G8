import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

function AnimatedHeadline({ text }) {
  const words = text.split(' ')
  return (
    <h1 className="font-syne font-extrabold text-4xl sm:text-5xl md:text-6xl lg:text-7xl leading-tight tracking-tight">
      {words.map((word, wi) => (
        <span key={wi} className="inline-block mr-[0.3em]">
          {word.split('').map((char, ci) => (
            <motion.span
              key={`${wi}-${ci}`}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.4,
                delay: wi * 0.1 + ci * 0.02 + 0.2,
                ease: [0.22, 1, 0.36, 1]
              }}
              className="inline-block"
            >
              {char}
            </motion.span>
          ))}
        </span>
      ))}
    </h1>
  )
}

export default function Hero() {
  return (
    <section className="relative z-30 min-h-[94vh] flex items-center overflow-hidden">
      {/* Background image */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1556761175-b413da4baf72?w=1920"
          alt="Professional business environment"
          className="w-full h-full object-cover"
        />
        {/* Overlay adaptive to theme */}
        <div className="absolute inset-0 bg-white/70 dark:bg-black/85 transition-colors duration-300" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-current text-white dark:text-slate-950 opacity-20" />
      </div>

      {/* Subtle ambient glow */}
      <div className="mesh-gradient pointer-events-none opacity-30" />

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-36 pb-28 w-full text-center flex flex-col items-center">

        {/* Main headline */}
        <div className="max-w-4xl">
          <AnimatedHeadline text="Prédire. Retenir. Rentabiliser." />

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.6 }}
            className="mt-8 text-lg md:text-xl lg:text-[1.15rem] opacity-70 leading-7 md:leading-8 max-w-3xl mx-auto font-dm"
          >
            Fortuneo est une banque 100% digitale — sans agence, sans conseiller en face-à-face. Quand un client décide de partir, il ne le dit pas. Il se déconnecte, réduit ses transactions, et un jour, ferme son compte.
            Nous avons construit un système de machine learning capable de détecter ces signaux avant qu'il soit trop tard — analyser le comportement, calculer le risque, et permettre aux équipes Fortuneo d'agir au bon moment.
          </motion.p>

          {/* CTA buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2, duration: 0.5 }}
            className="relative z-50 flex flex-wrap justify-center gap-5 mt-12"
          >
            <Link
              to="/prediction"
              className="inline-flex items-center gap-2 px-10 py-4 rounded-xl
                         bg-brand text-white font-bold text-base
                         shadow-xl shadow-brand/20
                         hover:bg-brand-light hover:scale-[1.03]
                         transition-all duration-300 cursor-pointer"
            >
              Lancer le Scoring
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>
            <Link
              to="/methodology"
              className="inline-flex items-center gap-2 px-10 py-4 rounded-xl
                         border border-black/10 dark:border-white/10
                         hover:bg-black/5 dark:hover:bg-white/5
                         font-bold text-base transition-all duration-300 cursor-pointer"
            >
              Voir la Méthode
            </Link>
          </motion.div>
        </div>
      </div>

      {/* Bottom fade adaptive */}
      <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-current to-transparent opacity-10 z-10 pointer-events-none" />
    </section>
  )
}
