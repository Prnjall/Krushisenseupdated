// Crop translations for English, Hindi, Marathi
const cropTranslations: Record<string, { en: string; hi: string; mr: string }> = {
  rice: { en: "Rice", hi: "चावल", mr: "तांदूळ" },
  maize: { en: "Maize", hi: "मक्का", mr: "मका" },
  chickpea: { en: "Chickpea", hi: "चना", mr: "हरभरा" },
  kidneybeans: { en: "Kidney Beans", hi: "राजमा", mr: "राजमा" },
  pigeonpeas: { en: "Pigeon Peas", hi: "अरहर", mr: "तूर" },
  mothbeans: { en: "Moth Beans", hi: "मोठ", mr: "मटकी" },
  mungbean: { en: "Mung Bean", hi: "मूंग", mr: "मूग" },
  blackgram: { en: "Black Gram", hi: "उड़द", mr: "उडीद" },
  lentil: { en: "Lentil", hi: "मसूर", mr: "मसूर" },
  pomegranate: { en: "Pomegranate", hi: "अनार", mr: "डाळिंब" },
  banana: { en: "Banana", hi: "केला", mr: "केळी" },
  mango: { en: "Mango", hi: "आम", mr: "आंबा" },
  grapes: { en: "Grapes", hi: "अंगूर", mr: "द्राक्षे" },
  watermelon: { en: "Watermelon", hi: "तरबूज", mr: "कलिंगड" },
  muskmelon: { en: "Muskmelon", hi: "खरबूजा", mr: "खरबूज" },
  apple: { en: "Apple", hi: "सेब", mr: "सफरचंद" },
  orange: { en: "Orange", hi: "संतरा", mr: "संत्रे" },
  papaya: { en: "Papaya", hi: "पपीता", mr: "पपई" },
  coconut: { en: "Coconut", hi: "नारियल", mr: "नारळ" },
  cotton: { en: "Cotton", hi: "कपास", mr: "कापूस" },
  jute: { en: "Jute", hi: "जूट", mr: "पाट" },
  coffee: { en: "Coffee", hi: "कॉफी", mr: "कॉफी" }
};
import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { CheckCircle2, Loader2 } from 'lucide-react';
// Prediction types and local API call
export interface SoilData {
  n: number;
  p: number;
  k: number;
  ph: number;
  temp: number;
  humidity: number;
  rainfall: number;
}

export interface PredictionResult {
  primary: {
    name: string;
    reason: string;
  };
  secondary: {
    name: string;
    reason: string;
  };
  tertiary: {
    name: string;
    reason: string;
  };
}

async function predictCrop(data: SoilData, language: string = 'en'): Promise<string[]> {
  const payload = {
    nitrogen: data.n,
    phosphorus: data.p,
    potassium: data.k,
    temperature: data.temp,
    humidity: data.humidity,
    ph: data.ph,
    rainfall: data.rainfall
  };
  const response = await fetch('/api/predict-crop', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const result = await response.json();
  if (result.success && Array.isArray(result.recommendations)) {
    return result.recommendations;
  } else {
    throw new Error(result.error || 'Prediction failed');
  }
}
import { useTranslation } from '../contexts/LanguageContext';

export const PredictCrop: React.FC = () => {
  const { t, language, translateBatch } = useTranslation();
  const [formData, setFormData] = useState<SoilData>({
    n: NaN,
    p: NaN,
    k: NaN,
    ph: NaN,
    temp: NaN,
    humidity: NaN,
    rainfall: NaN,
  });

  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<string[] | null>(null);

  useEffect(() => {
    if (language !== 'en') {
      translateBatch([
        'Predictive Cultivation.',
        'Input your soil and environmental parameters to identify the most suitable crops for your specific terrain.',
        'Nitrogen (N)',
        'Enter N ratio',
        'mg/kg',
        'Phosphorus (P)',
        'Enter P ratio',
        'Potassium (K)',
        'Enter K ratio',
        'Soil pH',
        'Enter pH level',
        'pH scale (0-14)',
        'Temperature',
        'Enter degrees',
        '°C',
        'Humidity',
        'Enter humidity',
        '%',
        'Rainfall',
        'Annual average',
        'mm',
        'Predict Crop',
        'Top 3 Recommended Crops',
        'Primary Recommendation',
        'Secondary Match',
        'Tertiary Alternative',
        'Rice', 'Wheat', 'Cotton', 'Optimal Match', 'High Viability', 'Strong Potential'
      ]);
    }
  }, [language, translateBatch]);

  const inputOrder = ["n", "p", "k", "ph", "temp", "humidity", "rainfall"];
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value === '' ? NaN : parseFloat(value) }));
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const form = e.currentTarget.form;
      if (!form) return;
      const idx = inputOrder.indexOf(e.currentTarget.name);
      if (idx !== -1 && idx < inputOrder.length - 1) {
        const next = form.elements.namedItem(inputOrder[idx + 1]);
        if (next && (next as HTMLElement).focus) {
          (next as HTMLElement).focus();
        }
      }
    }
  };

  const isAnyBlank = Object.values(formData).some(v => isNaN(v));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isAnyBlank) {
      alert('Please fill in all fields with valid numbers before predicting.');
      return;
    }
    setLoading(true);
    try {
      const recs = await predictCrop(formData, language);
      setRecommendations(recs);
    } catch (error) {
      alert('Prediction failed: ' + (error as Error).message);
      setRecommendations(null);
    }
    setLoading(false);
    setTimeout(() => {
      document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto px-6 py-20"
    >
      <header className="mb-16 text-center">
        <h1 className="font-headline font-black text-5xl md:text-7xl tracking-tighter mb-4 text-primary">
          {t('Predictive Cultivation.')}
        </h1>
        <p className="font-body text-on-surface-variant max-w-xl mx-auto text-lg leading-relaxed">
          {t('Input your soil and environmental parameters to identify the most suitable crops for your specific terrain.')}
        </p>
      </header>

      <section className="bg-surface-container-low p-8 md:p-12 rounded-xl mb-12">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="flex flex-col gap-2">
            <label className="font-headline font-bold text-sm tracking-wide text-primary uppercase">{t('Nitrogen (N)')}</label>
            <input 
              name="n"
              value={isNaN(formData.n) ? '' : formData.n}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              className="w-full bg-surface-container-lowest border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all text-on-surface placeholder:text-outline-variant" 
              placeholder={t('Enter N ratio')} 
              type="number" 
            />
            <span className="text-xs font-label text-on-surface-variant tracking-tight italic">{t('mg/kg')}</span>
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-headline font-bold text-sm tracking-wide text-primary uppercase">{t('Phosphorus (P)')}</label>
            <input 
              name="p"
              value={isNaN(formData.p) ? '' : formData.p}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              className="w-full bg-surface-container-lowest border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all text-on-surface placeholder:text-outline-variant" 
              placeholder={t('Enter P ratio')} 
              type="number" 
            />
            <span className="text-xs font-label text-on-surface-variant tracking-tight italic">{t('mg/kg')}</span>
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-headline font-bold text-sm tracking-wide text-primary uppercase">{t('Potassium (K)')}</label>
            <input 
              name="k"
              value={isNaN(formData.k) ? '' : formData.k}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              className="w-full bg-surface-container-lowest border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all text-on-surface placeholder:text-outline-variant" 
              placeholder={t('Enter K ratio')} 
              type="number" 
            />
            <span className="text-xs font-label text-on-surface-variant tracking-tight italic">{t('mg/kg')}</span>
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-headline font-bold text-sm tracking-wide text-primary uppercase">{t('Soil pH')}</label>
            <input 
              name="ph"
              value={isNaN(formData.ph) ? '' : formData.ph}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              className="w-full bg-surface-container-lowest border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all text-on-surface placeholder:text-outline-variant" 
              placeholder={t('Enter pH level')} 
              step="0.1" 
              type="number" 
            />
            <span className="text-xs font-label text-on-surface-variant tracking-tight italic">{t('pH scale (0-14)')}</span>
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-headline font-bold text-sm tracking-wide text-primary uppercase">{t('Temperature')}</label>
            <input 
              name="temp"
              value={isNaN(formData.temp) ? '' : formData.temp}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              className="w-full bg-surface-container-lowest border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all text-on-surface placeholder:text-outline-variant" 
              placeholder={t('Enter degrees')} 
              type="number" 
            />
            <span className="text-xs font-label text-on-surface-variant tracking-tight italic">{t('°C')}</span>
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-headline font-bold text-sm tracking-wide text-primary uppercase">{t('Humidity')}</label>
            <input 
              name="humidity"
              value={isNaN(formData.humidity) ? '' : formData.humidity}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              className="w-full bg-surface-container-lowest border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all text-on-surface placeholder:text-outline-variant" 
              placeholder={t('Enter humidity')} 
              type="number" 
            />
            <span className="text-xs font-label text-on-surface-variant tracking-tight italic">%</span>
          </div>

          <div className="flex flex-col gap-2 md:col-span-2 lg:col-span-1">
            <label className="font-headline font-bold text-sm tracking-wide text-primary uppercase">{t('Rainfall')}</label>
            <input 
              name="rainfall"
              value={isNaN(formData.rainfall) ? '' : formData.rainfall}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              className="w-full bg-surface-container-lowest border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all text-on-surface placeholder:text-outline-variant" 
              placeholder={t('Annual average')} 
              type="number" 
            />
            <span className="text-xs font-label text-on-surface-variant tracking-tight italic">mm</span>
          </div>

          <div className="mt-12 flex justify-center md:col-span-2 lg:col-span-3">
            <button 
              type="submit"
              disabled={loading}
              className="bg-primary text-on-primary px-12 py-5 rounded-full font-headline font-extrabold text-lg tracking-tight uppercase transition-all active:scale-95 shadow-xl shadow-black/5 flex items-center gap-3 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : t('Predict Crop')}
            </button>
          </div>
        </form>
      </section>

      {recommendations && (
        <section id="results" className="mt-24">
          <div className="flex items-center gap-4 mb-8">
            <div className="h-px flex-grow bg-surface-container-highest"></div>
            <h2 className="font-headline font-black text-2xl tracking-tighter uppercase">{t('Top 3 Recommended Crops')}</h2>
            <div className="h-px flex-grow bg-surface-container-highest"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommendations.map((crop, idx) => (
              <ResultCard
                key={crop}
                label={
                  idx === 0 ? t('Primary Recommendation') :
                  idx === 1 ? t('Secondary Match') :
                  t('Tertiary Alternative')
                }
                name={t(crop)}
                reason={
                  idx === 0 ? t('Optimal Match') :
                  idx === 1 ? t('High Viability') :
                  t('Strong Potential')
                }
              />
            ))}
          </div>
        </section>
      )}
    </motion.div>
  );
};

const ResultCard: React.FC<{ label: string; name: string; reason: string }> = ({ label, name, reason }) => {
  // Use the original crop name (lowercase, no spaces) to look up translations
  const cropKey = (name || '').toLowerCase().replace(/\s+/g, '');
  const translation = cropTranslations[cropKey];
  return (
    <div className="bg-surface-container-lowest p-6 rounded-xl group hover:bg-surface-container transition-colors duration-300 flex flex-col items-center text-center py-12">
      <p className="font-body text-xs uppercase tracking-widest text-on-surface-variant mb-1 font-bold">{label}</p>
      <div className="crop-card">
        <h3>{translation?.en || name}</h3>
        <p>{translation?.hi}</p>
        <p>{translation?.mr}</p>
      </div>
      <div className="mt-4 flex items-center text-on-surface-variant font-bold text-sm justify-center">
        <CheckCircle2 className="w-4 h-4 mr-2 text-primary" />
        {reason}
      </div>
    </div>
  );
};
// Add crop-card CSS for multi-language display
const style = document.createElement('style');
style.innerHTML = `
.crop-card {
  padding: 12px;
  border-radius: 10px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(5px);
  text-align: center;
  margin-bottom: 10px;
}
.crop-card h3 {
  font-size: 18px;
  font-weight: bold;
}
.crop-card p {
  font-size: 14px;
  opacity: 0.8;
}
`;
if (typeof window !== 'undefined' && !document.getElementById('crop-card-style')) {
  style.id = 'crop-card-style';
  document.head.appendChild(style);
}
