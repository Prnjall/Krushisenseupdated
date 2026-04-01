import React, { useEffect } from 'react';
import { TrendingUp, Brain, Leaf, Clock, Wallet, MousePointer2 } from 'lucide-react';
import { motion } from 'motion/react';
import { useTranslation } from '../contexts/LanguageContext';

interface HomeProps {
  onStart: () => void;
}

export const Home: React.FC<HomeProps> = ({ onStart }) => {
  const { t, language, translateBatch } = useTranslation();

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
      <section className="max-w-7xl mx-auto px-6 md:px-8 pt-12 md:pt-24 pb-16 md:pb-32">
        <div className="flex flex-col md:flex-row items-center gap-10 md:gap-16">
          <div className="md:w-1/2 text-left">
            <h2 className="font-headline font-medium text-on-surface-variant tracking-widest uppercase text-xs md:text-sm mb-4 md:mb-6">
              {t('Smart Crop Recommendation System')}
            </h2>
            <h1 className="font-headline font-extrabold text-5xl sm:text-7xl md:text-8xl text-primary tracking-tighter mb-6 md:mb-8 leading-none">
              KrushiSense
            </h1>
            <p className="font-body text-base md:text-xl text-on-surface-variant leading-relaxed mb-8 md:mb-12">
              {t('KrushiSense is a smart agriculture web application that helps farmers choose the most suitable crop based on soil and environmental conditions. The system uses machine learning to analyze important factors like Nitrogen (N), Phosphorus (P), Potassium (K), pH level, temperature, humidity, and rainfall.')}
            </p>
            <button 
              onClick={onStart}
              className="w-full sm:w-auto bg-primary text-on-primary px-8 md:px-10 py-4 md:py-5 rounded-lg font-headline font-bold text-lg md:text-xl transition-all hover:opacity-90 active:scale-95 flex items-center justify-center gap-3 shadow-2xl shadow-primary/10"
            >
              {t('Start Prediction')}
              <TrendingUp className="w-5 h-5 md:w-6 md:h-6" />
            </button>
          </div>
          <div className="md:w-1/2 w-full aspect-square rounded-2xl overflow-hidden shadow-2xl">
            <img 
              src="https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&q=80&w=1200" 
              alt="Sustainable farming" 
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          </div>
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
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 md:p-12 text-center bg-linear-to-t from-background via-transparent to-transparent">
            <div className="mt-4">
              <h3 className="font-headline text-3xl md:text-5xl font-extrabold text-primary mb-4 md:mb-6 tracking-tighter">{t('Cultivating the Future')}</h3>
              <p className="font-body text-sm md:text-lg text-on-surface max-w-xl">
                {t('Harnessing the power of precision agriculture to ensure food security through digital curation.')}
              </p>
            </div>
          </div>
        </div>
      </section>
    </motion.div>
  );
};
