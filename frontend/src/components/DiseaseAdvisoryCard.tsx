import React from 'react';
import { motion } from 'motion/react';
import { Sprout, AlertTriangle, ShieldCheck, Sun, Info } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';

export interface DiseaseAdvisory {
  summary: string;
  what_it_means: string;
  symptoms: string[];
  immediate_actions: string[];
  sustainable_practices: string[];
  prevention: string[];
  weather_considerations: string[];
  when_to_seek_help: string[];
  cautions: string[];
}

export const DiseaseAdvisoryCard: React.FC<{ advisory: DiseaseAdvisory }> = ({ advisory }) => {
  const { t } = useTranslation();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-8 bg-surface-container-lowest border border-primary/20 rounded-3xl p-6 md:p-10 max-w-4xl w-full text-left"
    >
      <h3 className="font-headline font-black text-2xl md:text-3xl text-primary mb-6 flex items-center gap-3">
        <Sprout className="w-8 h-8" />
        {t("AI Disease Advisory")}
      </h3>
      
      <div className="space-y-6">
        <div className="bg-primary/5 p-4 rounded-2xl">
          <h4 className="font-headline font-bold text-lg mb-2 text-primary">{t("Summary")}</h4>
          <p className="font-body text-on-surface-variant leading-relaxed">{advisory.summary}</p>
        </div>

        <div>
          <h4 className="font-headline font-bold text-lg mb-2 text-on-surface">{t("What This Means")}</h4>
          <p className="font-body text-on-surface-variant leading-relaxed">{advisory.what_it_means}</p>
        </div>

        {advisory.symptoms && advisory.symptoms.length > 0 && (
          <div className="bg-surface-container-low p-4 rounded-2xl">
            <h4 className="font-headline font-bold text-lg mb-2 text-on-surface flex items-center gap-2">
              <Info className="w-5 h-5 text-primary" />
              {t("Symptoms")}
            </h4>
            <ul className="list-disc pl-5 font-body text-on-surface-variant space-y-1">
              {advisory.symptoms.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-surface-container p-4 rounded-2xl">
            <h4 className="font-headline font-bold text-lg mb-2 text-on-surface">{t("Immediate Actions")}</h4>
            <ul className="list-disc pl-5 font-body text-on-surface-variant space-y-1">
              {advisory.immediate_actions?.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
          
          <div className="bg-surface-container p-4 rounded-2xl">
            <h4 className="font-headline font-bold text-lg mb-2 text-on-surface flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-primary" />
              {t("Prevention")}
            </h4>
            <ul className="list-disc pl-5 font-body text-on-surface-variant space-y-1">
              {advisory.prevention?.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {advisory.sustainable_practices && advisory.sustainable_practices.length > 0 && (
            <div className="bg-surface-container-high p-4 rounded-2xl">
              <h4 className="font-headline font-bold text-lg mb-2 text-on-surface flex items-center gap-2">
                <Sprout className="w-5 h-5 text-primary" />
                {t("Sustainable Practices")}
              </h4>
              <ul className="list-disc pl-5 font-body text-on-surface-variant space-y-1">
                {advisory.sustainable_practices.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {advisory.weather_considerations && advisory.weather_considerations.length > 0 && (
            <div className="bg-surface-container-high p-4 rounded-2xl">
              <h4 className="font-headline font-bold text-lg mb-2 text-on-surface flex items-center gap-2">
                <Sun className="w-5 h-5 text-primary" />
                {t("Weather Considerations")}
              </h4>
              <ul className="list-disc pl-5 font-body text-on-surface-variant space-y-1">
                {advisory.weather_considerations.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {advisory.when_to_seek_help && advisory.when_to_seek_help.length > 0 && (
          <div className="bg-surface-container-highest p-4 rounded-2xl">
            <h4 className="font-headline font-bold text-lg mb-2 text-on-surface">{t("When to Seek Expert Help")}</h4>
            <ul className="list-disc pl-5 font-body text-on-surface-variant space-y-1">
              {advisory.when_to_seek_help.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {advisory.cautions && advisory.cautions.length > 0 && (
          <div className="bg-error/10 border border-error/20 p-4 rounded-2xl">
            <h4 className="font-headline font-bold text-lg mb-2 text-error flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-error" />
              {t("Important Cautions")}
            </h4>
            <ul className="list-disc pl-5 font-body text-error space-y-1">
              {advisory.cautions.map((caution, i) => (
                <li key={i}>{caution}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </motion.div>
  );
};
