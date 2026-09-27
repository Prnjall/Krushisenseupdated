import React, { useEffect } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { Info, Microscope, Landmark, RadioReceiver, Sprout, CloudRain, Satellite, Bug, BrainCircuit, Network } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';
import SpotlightCard from './ui/SpotlightCard';

export const HowItWorks: React.FC = () => {
  const { t, language, translateBatch } = useTranslation();
  const shouldReduceMotion = useReducedMotion();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : 0.07
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: shouldReduceMotion ? 0 : 12 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { duration: 0.5, ease: "easeOut" } 
    }
  };

  useEffect(() => {
    if (language !== 'en') {
      translateBatch([
        'The Science Behind The Harvest.',
        'KrushiSense bridges traditional wisdom and modern data science to deliver precision crop recommendations.',
        'Platform Capabilities',
        'Predict the Best Crop',
        'Our pre-trained ML model cross-references your soil profile against thousands of successful harvest data points to find the optimal match with top-3 recommendations.',
        'Monitor Weather',
        'Access current weather and a 7-day forecast with deterministic agricultural risk signals based on real-time temperature and precipitation trends.',
        'Observe Vegetation',
        'Leverage Sentinel-2 L2A satellite imagery to calculate NDVI, giving you observation freshness and vegetation insight without leaving your field.',
        'Screen Crop Diseases',
        'Upload an image or use your camera to let our MobileNetV3 ONNX model detect diseases in supported crops with strict status-based safety handling.',
        'Get AI Agricultural Advice',
        'Our Gemini-powered engine combines your available agricultural context, weather, and satellite data to provide safe, sustainable recommendations and disease management advice.',
        'Interoperate With Systems',
        'Designed for the BRICS AgriN initiative, external agricultural systems can securely provide context to our advisory engine via a canonical observation schema.',
        'Important Note: The accuracy of the recommendation depends on correct input values. Precision in soil testing leads to precision in results.',
        'Resources',
        'Where to get your data.',
        'Access reliable testing facilities to ensure your input data is scientifically verified.',
        'Soil Testing Laboratories',
        'Professional labs provide detailed chemical analysis of N, P, K levels and pH concentration.',
        'Agriculture Centers',
        'Government-led centers often provide subsidized or free basic soil testing kits and reports.',
        'IoT Soil Sensors',
        'Real-time smart devices can be installed in your fields for continuous monitoring of moisture and nutrients.',
        'BUILT FOR COOPERATION',
        'Why KrushiSense?',
        'KrushiSense combines agricultural intelligence, real-world data, and interoperable digital infrastructure to make better farming decisions more accessible.',
        'Farmer-First',
        'Designed around the needs of farmers, KrushiSense turns complex agricultural data into clear, practical guidance in English, Hindi, and Marathi.',
        'Evidence-Driven',
        'KrushiSense combines soil information, weather conditions, satellite vegetation insights, and machine learning to support data-driven agricultural decisions.',
        'Interoperable',
        'KrushiSense uses a standardized agricultural data structure so different agricultural platforms and digital systems can exchange agricultural context with its advisory engine.',
        'Built for Cooperation',
        'From local farm insights to cross-system collaboration, KrushiSense is designed to connect agricultural intelligence across regions and digital platforms.'
      ]);
    }
  }, [language, translateBatch]);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-7xl mx-auto px-6 md:px-8 py-12 md:py-20"
    >
      <section className="mb-16 md:mb-32">
        <div className="flex flex-col md:flex-row gap-10 md:gap-16 items-center">
          <div className="md:w-1/2">
            <h1 className="font-headline text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tighter text-primary mb-6">
              {t('The Science Behind The Harvest.')}
            </h1>
            <p className="text-on-surface-variant text-base md:text-xl leading-relaxed max-w-md">
              {t('KrushiSense bridges traditional wisdom and modern data science to deliver precision crop recommendations.')}
            </p>
          </div>
          <div className="md:w-1/2 w-full h-64 md:h-80 rounded-xl overflow-hidden bg-surface-container-low relative border border-on-surface/5">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-transparent z-10"></div>
            <img 
              alt="Agricultural technology" 
              className="w-full h-full object-cover grayscale opacity-40 mix-blend-luminosity" 
              src="https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1920" 
              referrerPolicy="no-referrer"
            />
          </div>
        </div>
      </section>

      <section className="bg-surface-container-low -mx-6 md:-mx-8 px-6 md:px-8 py-16 md:py-24">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12 md:mb-16">
            <h2 className="font-headline text-3xl md:text-4xl font-extrabold tracking-tight text-primary">{t('Platform Capabilities')}</h2>
            <div className="w-12 md:w-16 h-1 bg-primary mt-4"></div>
          </div>
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
          >
            <WorkflowStep 
              num="01" 
              icon={<Sprout className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Predict the Best Crop')} 
              desc={t('Our pre-trained ML model cross-references your soil profile against thousands of successful harvest data points to find the optimal match with top-3 recommendations.')}
              variants={itemVariants}
              shouldReduceMotion={shouldReduceMotion}
            />
            <WorkflowStep 
              num="02" 
              icon={<CloudRain className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Monitor Weather')} 
              desc={t('Access current weather and a 7-day forecast with deterministic agricultural risk signals based on real-time temperature and precipitation trends.')}
              variants={itemVariants}
              shouldReduceMotion={shouldReduceMotion}
            />
            <WorkflowStep 
              num="03" 
              icon={<Satellite className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Observe Vegetation')} 
              desc={t('Leverage Sentinel-2 L2A satellite imagery to calculate NDVI, giving you observation freshness and vegetation insight without leaving your field.')}
              variants={itemVariants}
              shouldReduceMotion={shouldReduceMotion}
            />
            <WorkflowStep 
              num="04" 
              icon={<Bug className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Screen Crop Diseases')} 
              desc={t('Upload an image or use your camera to let our MobileNetV3 ONNX model detect diseases in supported crops with strict status-based safety handling.')}
              variants={itemVariants}
              shouldReduceMotion={shouldReduceMotion}
            />
            <WorkflowStep 
              num="05" 
              icon={<BrainCircuit className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Get AI Agricultural Advice')} 
              desc={t('Our Gemini-powered engine combines your available agricultural context, weather, and satellite data to provide safe, sustainable recommendations and disease management advice.')}
              variants={itemVariants}
              shouldReduceMotion={shouldReduceMotion}
            />
            <WorkflowStep 
              num="06" 
              icon={<Network className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Interoperate With Systems')} 
              desc={t('Designed for the BRICS AgriN initiative, external agricultural systems can securely provide context to our advisory engine via a canonical observation schema.')}
              variants={itemVariants}
              shouldReduceMotion={shouldReduceMotion}
            />
          </motion.div>
          <div className="mt-8 md:mt-12 bg-surface-dim p-5 md:p-6 rounded-xl border-l-4 border-primary flex flex-col md:flex-row items-center gap-4 md:gap-6">
            <Info className="w-6 h-6 md:w-8 md:h-8 text-primary shrink-0" />
            <p className="font-body text-on-surface text-sm md:text-base font-semibold italic text-center md:text-left">
              {t('Important Note: The accuracy of the recommendation depends on correct input values. Precision in soil testing leads to precision in results.')}
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="text-center mb-16 md:mb-20">
          <span className="text-on-surface-variant font-headline font-bold uppercase tracking-widest text-[10px] md:text-xs mb-3 block">
            {t('BUILT FOR COOPERATION')}
          </span>
          <h2 className="font-headline text-4xl md:text-5xl font-extrabold tracking-tight text-primary mb-6">
            {t('Why KrushiSense?')}
          </h2>
          <p className="text-on-surface-variant text-base md:text-lg max-w-2xl mx-auto leading-relaxed px-4">
            {t('KrushiSense combines agricultural intelligence, real-world data, and interoperable digital infrastructure to make better farming decisions more accessible.')}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8 lg:gap-10 px-4 md:px-0">
          <SpotlightCard className="flex flex-col h-full min-h-[320px]">
            <div className="mb-6 md:mb-8 text-primary">
              <Sprout className="w-10 h-10 md:w-12 md:h-12" />
            </div>
            <h3 className="font-headline text-2xl font-bold mb-3 md:mb-4">{t('Farmer-First')}</h3>
            <p className="text-on-surface-variant text-sm md:text-base leading-relaxed">
              {t('Designed around the needs of farmers, KrushiSense turns complex agricultural data into clear, practical guidance in English, Hindi, and Marathi.')}
            </p>
          </SpotlightCard>
          
          <SpotlightCard className="flex flex-col h-full min-h-[320px]">
            <div className="mb-6 md:mb-8 text-primary">
              <Satellite className="w-10 h-10 md:w-12 md:h-12" />
            </div>
            <h3 className="font-headline text-2xl font-bold mb-3 md:mb-4">{t('Evidence-Driven')}</h3>
            <p className="text-on-surface-variant text-sm md:text-base leading-relaxed">
              {t('KrushiSense combines soil information, weather conditions, satellite vegetation insights, and machine learning to support data-driven agricultural decisions.')}
            </p>
          </SpotlightCard>
          
          <SpotlightCard className="flex flex-col h-full min-h-[320px] border-primary/30 relative shadow-xl shadow-primary/5">
            <div className="absolute top-6 right-6 md:top-8 md:right-8 bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
              {t('Built for Cooperation')}
            </div>
            <div className="mb-6 md:mb-8 text-primary mt-8 md:mt-0">
              <Network className="w-10 h-10 md:w-12 md:h-12" />
            </div>
            <h3 className="font-headline text-2xl font-bold mb-3 md:mb-4">{t('Interoperable')}</h3>
            <p className="text-on-surface-variant text-sm md:text-base leading-relaxed">
              {t('KrushiSense uses a standardized agricultural data structure so different agricultural platforms and digital systems can exchange agricultural context with its advisory engine.')}
            </p>
          </SpotlightCard>
        </div>

        <div className="mt-16 md:mt-24 max-w-4xl mx-auto text-center px-6">
          <p className="font-body text-on-surface-variant text-lg md:text-xl lg:text-2xl font-medium italic leading-relaxed">
            "{t('From local farm insights to cross-system collaboration, KrushiSense is designed to connect agricultural intelligence across regions and digital platforms.')}"
          </p>
        </div>
      </section>

      <section className="py-16 md:py-24">
        <div className="flex flex-col md:flex-row justify-between md:items-end mb-12 md:mb-16 gap-4 md:gap-8 text-center md:text-left">
          <div className="max-w-xl mx-auto md:mx-0">
            <span className="text-on-surface-variant font-headline font-bold uppercase tracking-widest text-[10px] md:text-xs mb-2 md:mb-4 block">{t('Resources')}</span>
            <h2 className="font-headline text-3xl md:text-5xl font-extrabold tracking-tight text-primary">{t('Where to get your data.')}</h2>
          </div>
          <p className="text-on-surface-variant max-w-xs md:text-right hidden md:block">
            {t('Access reliable testing facilities to ensure your input data is scientifically verified.')}
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <ResourceCard 
            icon={<Microscope className="w-8 h-8" />}
            title={t('Soil Testing Laboratories')}
            desc={t('Professional labs provide detailed chemical analysis of N, P, K levels and pH concentration.')}
          />
          <ResourceCard 
            icon={<Landmark className="w-8 h-8" />}
            title={t('Agriculture Centers')}
            desc={t('Government-led centers often provide subsidized or free basic soil testing kits and reports.')}
          />
          <ResourceCard 
            icon={<RadioReceiver className="w-8 h-8" />}
            title={t('IoT Soil Sensors')}
            desc={t('Real-time smart devices can be installed in your fields for continuous monitoring of moisture and nutrients.')}
          />
        </div>
      </section>
    </motion.div>
  );
};

const WorkflowStep: React.FC<{ num: string; icon: React.ReactNode; title: string; desc: string; variants?: any; shouldReduceMotion?: boolean | null }> = ({ num, icon, title, desc, variants, shouldReduceMotion }) => (
  <motion.div 
    variants={variants}
    className={`bg-surface-container-lowest p-6 md:p-8 rounded-xl flex flex-col justify-between min-h-[250px] md:min-h-[320px] group ${shouldReduceMotion ? '' : 'transition-transform duration-300 md:hover:-translate-y-1 md:hover:scale-[1.005]'}`}
  >
    <div>
      <motion.span 
        variants={{ hidden: { opacity: 0 }, visible: { opacity: 0.2, transition: { duration: 0.8 } } }}
        className="text-on-surface-variant font-headline font-bold text-3xl md:text-4xl block mb-3 md:mb-4"
      >
        {num}
      </motion.span>
      <div className={`mb-4 md:mb-6 text-primary ${shouldReduceMotion ? '' : 'transition-transform duration-300 md:group-hover:-translate-y-1'}`}>{icon}</div>
      <h3 className="font-headline text-xl md:text-2xl font-bold mb-2 md:mb-3">{title}</h3>
      <p className="text-on-surface-variant text-xs md:text-sm leading-relaxed">{desc}</p>
    </div>
  </motion.div>
);

const ResourceCard: React.FC<{ icon: React.ReactNode; title: string; desc: string }> = ({ icon, title, desc }) => (
  <div className="bg-surface-container-lowest p-8 rounded-xl border border-surface-variant/10 transition-all hover:shadow-lg">
    <div className="flex gap-4">
      <div className="text-primary shrink-0">{icon}</div>
      <div>
        <h4 className="font-headline font-bold text-xl mb-2">{title}</h4>
        <p className="text-on-surface-variant text-sm leading-relaxed">{desc}</p>
      </div>
    </div>
  </div>
);
