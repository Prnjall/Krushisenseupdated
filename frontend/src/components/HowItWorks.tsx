import React, { useEffect } from 'react';
import { motion } from 'motion/react';
import { Database, RefreshCw, Cpu, BadgeCheck, Info, Microscope, Landmark, RadioReceiver } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';

export const HowItWorks: React.FC = () => {
  const { t, language, translateBatch } = useTranslation();

  useEffect(() => {
    if (language !== 'en') {
      translateBatch([
        'The Science Behind The Harvest.',
        'KrushiSense bridges traditional wisdom and modern data science to deliver precision crop recommendations.',
        'The Workflow',
        'Input Data',
        'Enter your specific soil metrics: Nitrogen (N), Phosphorus (P), Potassium (K), pH levels, and environmental factors like Temperature, Humidity, and Rainfall.',
        'Data Processing',
        'Your information is securely transmitted to our backend API where it is normalized and prepared for analysis using specialized agricultural algorithms.',
        'Machine Learning',
        'Our pre-trained ML model cross-references your soil profile against thousands of successful harvest data points to find the optimal match.',
        'Recommendation',
        'Receive a ranked list of the top 3 crops most likely to thrive in your current environment, ensuring maximum yield and resource efficiency.',
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
      className="max-w-7xl mx-auto px-8 py-20"
    >
      <section className="mb-32">
        <div className="flex flex-col md:flex-row gap-16 items-center">
          <div className="md:w-1/2">
            <h1 className="font-headline text-6xl md:text-7xl font-extrabold tracking-tighter text-primary mb-6">
              {t('The Science Behind The Harvest.')}
            </h1>
            <p className="text-on-surface-variant text-xl leading-relaxed max-w-md">
              {t('KrushiSense bridges traditional wisdom and modern data science to deliver precision crop recommendations.')}
            </p>
          </div>
          <div className="md:w-1/2 w-full h-80 rounded-xl overflow-hidden bg-surface-container-low relative">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent"></div>
            <img 
              alt="Agricultural technology" 
              className="w-full h-full object-cover grayscale opacity-60 mix-blend-multiply" 
              src="https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&q=80&w=1920" 
              referrerPolicy="no-referrer"
            />
          </div>
        </div>
      </section>

      <section className="bg-surface-container-low -mx-8 px-8 py-24">
        <div className="max-w-7xl mx-auto">
          <div className="mb-16">
            <h2 className="font-headline text-4xl font-extrabold tracking-tight text-primary">{t('The Workflow')}</h2>
            <div className="w-16 h-1 bg-primary mt-4"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <WorkflowStep 
              num="01" 
              icon={<Database className="w-10 h-10" />} 
              title={t('Input Data')} 
              desc={t('Enter your specific soil metrics: Nitrogen (N), Phosphorus (P), Potassium (K), pH levels, and environmental factors like Temperature, Humidity, and Rainfall.')} 
            />
            <WorkflowStep 
              num="02" 
              icon={<RefreshCw className="w-10 h-10" />} 
              title={t('Data Processing')} 
              desc={t('Your information is securely transmitted to our backend API where it is normalized and prepared for analysis using specialized agricultural algorithms.')} 
            />
            <WorkflowStep 
              num="03" 
              icon={<Cpu className="w-10 h-10" />} 
              title={t('Machine Learning')} 
              desc={t('Our pre-trained ML model cross-references your soil profile against thousands of successful harvest data points to find the optimal match.')} 
            />
            <WorkflowStep 
              num="04" 
              icon={<BadgeCheck className="w-10 h-10" />} 
              title={t('Recommendation')} 
              desc={t('Receive a ranked list of the top 3 crops most likely to thrive in your current environment, ensuring maximum yield and resource efficiency.')} 
            />
          </div>
          <div className="mt-12 bg-surface-dim p-6 rounded-xl border-l-4 border-primary flex items-center gap-6">
            <Info className="w-8 h-8 text-primary" />
            <p className="font-body text-on-surface font-semibold italic">
              {t('Important Note: The accuracy of the recommendation depends on correct input values. Precision in soil testing leads to precision in results.')}
            </p>
          </div>
        </div>
      </section>

      <section className="py-24">
        <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-8">
          <div className="max-w-xl">
            <span className="text-on-surface-variant font-headline font-bold uppercase tracking-widest text-xs mb-4 block">{t('Resources')}</span>
            <h2 className="font-headline text-5xl font-extrabold tracking-tight text-primary">{t('Where to get your data.')}</h2>
          </div>
          <p className="text-on-surface-variant max-w-xs text-right hidden md:block">
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
  <div className="bg-surface-container-lowest p-8 rounded-xl flex flex-col justify-between min-h-[320px]">
    <div>
      <span className="text-on-surface-variant font-headline font-bold text-4xl opacity-20 block mb-4">{num}</span>
      <div className="mb-6 text-primary">{icon}</div>
      <h3 className="font-headline text-2xl font-bold mb-3">{title}</h3>
      <p className="text-on-surface-variant text-sm leading-relaxed">{desc}</p>
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
