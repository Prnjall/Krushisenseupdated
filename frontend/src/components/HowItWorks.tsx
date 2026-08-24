import React, { useEffect } from 'react';
import { motion } from 'motion/react';
import { Info, Microscope, Landmark, RadioReceiver, Sprout, CloudRain, Satellite, Bug, BrainCircuit, Network } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';

export const HowItWorks: React.FC = () => {
  const { t, language, translateBatch } = useTranslation();

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
        'Real-time smart devices can be installed in your fields for continuous monitoring of moisture and nutrients.'
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            <WorkflowStep 
              num="01" 
              icon={<Sprout className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Predict the Best Crop')} 
              desc={t('Our pre-trained ML model cross-references your soil profile against thousands of successful harvest data points to find the optimal match with top-3 recommendations.')} 
            />
            <WorkflowStep 
              num="02" 
              icon={<CloudRain className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Monitor Weather')} 
              desc={t('Access current weather and a 7-day forecast with deterministic agricultural risk signals based on real-time temperature and precipitation trends.')} 
            />
            <WorkflowStep 
              num="03" 
              icon={<Satellite className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Observe Vegetation')} 
              desc={t('Leverage Sentinel-2 L2A satellite imagery to calculate NDVI, giving you observation freshness and vegetation insight without leaving your field.')} 
            />
            <WorkflowStep 
              num="04" 
              icon={<Bug className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Screen Crop Diseases')} 
              desc={t('Upload an image or use your camera to let our MobileNetV3 ONNX model detect diseases in supported crops with strict status-based safety handling.')} 
            />
            <WorkflowStep 
              num="05" 
              icon={<BrainCircuit className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Get AI Agricultural Advice')} 
              desc={t('Our Gemini-powered engine combines your available agricultural context, weather, and satellite data to provide safe, sustainable recommendations and disease management advice.')} 
            />
            <WorkflowStep 
              num="06" 
              icon={<Network className="w-8 h-8 md:w-10 md:h-10" />} 
              title={t('Interoperate With Systems')} 
              desc={t('Designed for the BRICS AgriN initiative, external agricultural systems can securely provide context to our advisory engine via a canonical observation schema.')} 
            />
          </div>
          <div className="mt-8 md:mt-12 bg-surface-dim p-5 md:p-6 rounded-xl border-l-4 border-primary flex flex-col md:flex-row items-center gap-4 md:gap-6">
            <Info className="w-6 h-6 md:w-8 md:h-8 text-primary shrink-0" />
            <p className="font-body text-on-surface text-sm md:text-base font-semibold italic text-center md:text-left">
              {t('Important Note: The accuracy of the recommendation depends on correct input values. Precision in soil testing leads to precision in results.')}
            </p>
          </div>
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

const WorkflowStep: React.FC<{ num: string; icon: React.ReactNode; title: string; desc: string }> = ({ num, icon, title, desc }) => (
  <div className="bg-surface-container-lowest p-6 md:p-8 rounded-xl flex flex-col justify-between min-h-[250px] md:min-h-[320px]">
    <div>
      <span className="text-on-surface-variant font-headline font-bold text-3xl md:text-4xl opacity-20 block mb-3 md:mb-4">{num}</span>
      <div className="mb-4 md:mb-6 text-primary">{icon}</div>
      <h3 className="font-headline text-xl md:text-2xl font-bold mb-2 md:mb-3">{title}</h3>
      <p className="text-on-surface-variant text-xs md:text-sm leading-relaxed">{desc}</p>
    </div>
  </div>
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
