import React, { useEffect } from 'react';
import { TrendingUp, Brain, Leaf, Clock, Wallet, MousePointer2 } from 'lucide-react';
import { motion, useMotionValue, useSpring } from 'motion/react';
import { useTranslation } from '../contexts/LanguageContext';

const HeroBackgroundImage = ({ heroRef }: { heroRef: React.RefObject<HTMLElement> }) => {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const smoothX = useSpring(mouseX, { damping: 30, stiffness: 100 });
  const smoothY = useSpring(mouseY, { damping: 30, stiffness: 100 });

  useEffect(() => {
    const hero = heroRef.current;
    if (!hero) return;

    const handleMouseMove = (e: MouseEvent) => {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const hasHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
      
      if (prefersReducedMotion || !hasHover) {
        mouseX.set(0);
        mouseY.set(0);
        return;
      }
      
      const rect = hero.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = ((e.clientY - rect.top) / rect.height) * 2 - 1;
      
      // Target movement: X ±8px, Y ±6px
      mouseX.set(-x * 8); 
      mouseY.set(-y * 6);
    };

    const handleMouseLeave = () => {
      mouseX.set(0);
      mouseY.set(0);
    };

    hero.addEventListener('mousemove', handleMouseMove);
    hero.addEventListener('mouseleave', handleMouseLeave);
    return () => {
      hero.removeEventListener('mousemove', handleMouseMove);
      hero.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [mouseX, mouseY, heroRef]);

  return (
    <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
      <motion.div 
        style={{ x: smoothX, y: smoothY }}
        className="absolute inset-0 w-full h-full lg:inset-[-20px] lg:w-[calc(100%+40px)] lg:h-[calc(100%+40px)]"
      >
        <img 
          src="/images/hero-bg.jpg" 
          alt="" 
          className="w-full h-full object-cover lg:object-center object-bottom"
        />
        {/* Subtle overlay for readability without fading to solid black at the bottom */}
        <div className="absolute inset-0 bg-black/50 lg:bg-black/40" />
        {/* Dark gradient at the very top to ensure Navbar text is visible */}
        <div className="absolute inset-x-0 top-0 h-32 lg:h-40 bg-linear-to-b from-black/70 to-transparent pointer-events-none" />
      </motion.div>
    </div>
  );
};

interface HomeProps {
  onStart: () => void;
}

export const Home: React.FC<HomeProps> = ({ onStart }) => {
  const { t, language, translateBatch } = useTranslation();
  const heroRef = React.useRef<HTMLElement>(null);

  useEffect(() => {
    if (language !== 'en') {
      translateBatch([
        'Smart Crop Recommendation System',
        'KrushiSense is a smart agriculture web application that helps farmers choose the most suitable crop based on soil and environmental conditions. The system uses machine learning to analyze important factors like Nitrogen (N), Phosphorus (P), Potassium (K), pH level, temperature, humidity, and rainfall.',
        'Start Prediction',
        'Agricultural Intelligence',
        'Empowering farmers with data-driven decision making.',
        'Helps farmers choose the right crop',
        'By analyzing multi-layered environmental data points, our ML model identifies the perfect genetic match for your soil.',
        'Improves crop productivity',
        'Maximize your yield by planting what nature intended for your specific geographical and chemical profile.',
        'Saves time and effort',
        'Instant analysis eliminates weeks of manual soil testing and guesswork.',
        'Reduces financial loss',
        'Prevent investment in crops destined to fail due to incompatible soil pH or climatic shifts.',
        'Easy to use for everyone',
        'A minimalist interface designed with accessibility and clarity at its core.',
        'Cultivating the Future',
        'Harnessing the power of precision agriculture to ensure food security through digital curation.'
      ]);
    }
  }, [language, translateBatch]);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Hero Section */}
      <section ref={heroRef} className="relative w-full overflow-hidden flex flex-col items-center justify-center min-h-[100dvh] px-4 sm:px-6 md:px-8 py-24 md:py-32 border-b border-outline-variant/10">
        <HeroBackgroundImage heroRef={heroRef} />
        <div className="relative z-10 w-full max-w-4xl mx-auto flex flex-col items-center text-center mt-8 md:mt-12">
          <h2 className="font-headline font-bold text-white/90 tracking-[0.2em] uppercase text-[10px] sm:text-xs md:text-sm mb-4 md:mb-6 px-2">
            {t('Smart Crop Recommendation System')}
          </h2>
          <h1 className="font-headline font-extrabold text-5xl sm:text-6xl md:text-7xl lg:text-8xl text-white tracking-tighter mb-6 md:mb-8 leading-[1.1] drop-shadow-lg px-2 break-words">
            KrushiSense
          </h1>
          <p className="font-body text-sm sm:text-base md:text-xl text-white/95 leading-relaxed mb-10 md:mb-12 max-w-[90%] sm:max-w-2xl lg:max-w-3xl mx-auto font-medium drop-shadow-md">
            {t('KrushiSense is a smart agriculture web application that helps farmers choose the most suitable crop based on soil and environmental conditions. The system uses machine learning to analyze important factors like Nitrogen (N), Phosphorus (P), Potassium (K), pH level, temperature, humidity, and rainfall.')}
          </p>
          <button 
            onClick={onStart}
            className="w-full sm:w-auto max-w-xs mx-auto bg-primary text-on-primary px-8 md:px-10 py-4 md:py-5 rounded-xl font-headline font-bold text-base md:text-xl transition-all hover:opacity-90 active:scale-95 flex items-center justify-center gap-3 shadow-2xl shadow-primary/30"
          >
            {t('Start Prediction')}
            <TrendingUp className="w-5 h-5 md:w-6 md:h-6" />
          </button>
        </div>
      </section>

      {/* Bento Grid / Benefits Section */}
      <section className="bg-surface-container-low py-16 md:py-32 px-6 md:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12 md:mb-16">
            <h3 className="font-headline text-3xl md:text-4xl font-bold tracking-tight">{t('Agricultural Intelligence')}</h3>
            <p className="font-body text-on-surface-variant mt-2 text-sm md:text-base">{t('Empowering farmers with data-driven decision making.')}</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4 md:gap-6">
            <div className="md:col-span-3 bg-surface-container-lowest p-6 md:p-10 rounded-xl flex flex-col justify-between min-h-[250px] md:min-h-[320px] transition-transform hover:-translate-y-1">
              <div>
                <Brain className="w-8 h-8 md:w-10 md:h-10 mb-6 text-primary" />
                <h4 className="font-headline text-xl md:text-2xl font-bold mb-4">{t('Helps farmers choose the right crop')}</h4>
                <p className="font-body text-sm md:text-base text-on-surface-variant leading-relaxed">
                  {t('By analyzing multi-layered environmental data points, our ML model identifies the perfect genetic match for your soil.')}
                </p>
              </div>
            </div>
            <div className="md:col-span-3 bg-surface-container-lowest p-6 md:p-10 rounded-xl flex flex-col justify-between min-h-[250px] md:min-h-[320px] transition-transform hover:-translate-y-1">
              <div>
                <Leaf className="w-8 h-8 md:w-10 md:h-10 mb-6 text-primary" />
                <h4 className="font-headline text-xl md:text-2xl font-bold mb-4">{t('Improves crop productivity')}</h4>
                <p className="font-body text-sm md:text-base text-on-surface-variant leading-relaxed">
                  {t('Maximize your yield by planting what nature intended for your specific geographical and chemical profile.')}
                </p>
              </div>
            </div>
            <div className="md:col-span-2 bg-surface-container-lowest p-6 md:p-10 rounded-xl flex flex-col justify-between min-h-[250px] md:min-h-[320px] transition-transform hover:-translate-y-1">
              <div>
                <Clock className="w-8 h-8 md:w-10 md:h-10 mb-6 text-primary" />
                <h4 className="font-headline text-lg md:text-xl font-bold mb-4">{t('Saves time and effort')}</h4>
                <p className="font-body text-xs md:text-sm text-on-surface-variant">
                  {t('Instant analysis eliminates weeks of manual soil testing and guesswork.')}
                </p>
              </div>
            </div>
            <div className="md:col-span-2 bg-primary text-on-primary p-6 md:p-10 rounded-xl flex flex-col justify-between min-h-[250px] md:min-h-[320px] transition-transform hover:-translate-y-1">
              <div>
                <Wallet className="w-8 h-8 md:w-10 md:h-10 mb-6 text-on-primary" />
                <h4 className="font-headline text-lg md:text-xl font-bold mb-4">{t('Reduces financial loss')}</h4>
                <p className="font-body text-xs md:text-sm opacity-80">
                  {t('Prevent investment in crops destined to fail due to incompatible soil pH or climatic shifts.')}
                </p>
              </div>
            </div>
            <div className="md:col-span-2 bg-surface-container-lowest p-6 md:p-10 rounded-xl flex flex-col justify-between min-h-[250px] md:min-h-[320px] transition-transform hover:-translate-y-1">
              <div>
                <MousePointer2 className="w-8 h-8 md:w-10 md:h-10 mb-6 text-primary" />
                <h4 className="font-headline text-lg md:text-xl font-bold mb-4">{t('Easy to use for everyone')}</h4>
                <p className="font-body text-xs md:text-sm text-on-surface-variant">
                  {t('A minimalist interface designed with accessibility and clarity at its core.')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Visual Anchor Section */}
      <section className="max-w-7xl mx-auto px-6 md:px-8 py-16 md:py-32">
        <div className="relative w-full h-80 md:h-150 overflow-hidden rounded-xl bg-surface-container">
          <img 
            src="https://images.unsplash.com/photo-1622840951255-d08db152f4ce?q=80&w=1632&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
            alt="Lush green fields" 
            className="w-full h-full object-cover"
            referrerPolicy="no-referrer"
          />
          {/* Overlay to ensure text readability */}
          <div className="absolute inset-0 bg-black/40" />
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 md:p-12 text-center bg-linear-to-t from-background/80 via-transparent to-transparent pointer-events-none">
            <div className="mt-4 relative z-10 pointer-events-auto">
              <h3 className="font-headline text-3xl md:text-5xl font-extrabold text-white drop-shadow-[0_4px_4px_rgba(0,0,0,0.8)] mb-4 md:mb-6 tracking-tighter">{t('Cultivating the Future')}</h3>
              <p className="font-body text-sm md:text-lg text-white/95 drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] max-w-xl mx-auto font-medium">
                {t('Harnessing the power of precision agriculture to ensure food security through digital curation.')}
              </p>
            </div>
          </div>
        </div>
      </section>
    </motion.div>
  );
};
