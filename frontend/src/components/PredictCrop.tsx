// Crop translations for English, Hindi, Marathi
export const cropTranslations: Record<string, { en: string; hi: string; mr: string }> = {
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
  coffee: { en: "Coffee", hi: "कॉफी", mr: "कॉफी" },
  sugarcane: { en: "Sugarcane", hi: "गन्ना", mr: "ऊस" },
  cucumber: { en: "Cucumber", hi: "खीरा", mr: "काकडी" },
  jowar: { en: "Jowar", hi: "ज्वार", mr: "ज्वारी" },
  tur: { en: "Tur", hi: "अरहर", mr: "तूर" },
  urad: { en: "Urad", hi: "उड़द", mr: "उडीद" },
  moong: { en: "Moong", hi: "मूंग", mr: "मूग" },
  gram: { en: "Gram", hi: "चना", mr: "हरभरा" },
  masoor: { en: "Masoor", hi: "मसूर", mr: "मसूर" },
  ginger: { en: "Ginger", hi: "अदरक", mr: "आले" },
  turmeric: { en: "Turmeric", hi: "हल्दी", mr: "हळद" },
  tobacco: { en: "Tobacco", hi: "तंबाकू", mr: "तंबाखू" },
  groundnut: { en: "Groundnut", hi: "मूंगफली", mr: "भुईमूग" },
  soybean: { en: "Soybean", hi: "सोयाबीन", mr: "सोयाबीन" },
  mustard: { en: "Mustard", hi: "सरसों", mr: "मोहरी" },
  sunflower: { en: "Sunflower", hi: "सूरजमुखी", mr: "सूर्यफूल" },
  tea: { en: "Tea", hi: "चाय", mr: "चहा" },
  rubber: { en: "Rubber", hi: "रबर", mr: "रबर" },
  pulses: { en: "Pulses", hi: "दालें", mr: "डाळी" },
  wheat: { en: "Wheat", hi: "गेहूं", mr: "गहू" }
};
import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { CheckCircle2, Loader2, ArrowRight, MapPin, Layers, Sprout } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
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
  label: string;
  region: string;
  district?: string;
  soil_color?: string;
  fertilizer?: string;
  score?: number;
  confidence?: number;
}

// Simple CSV parser to handle dataset loading
function parseCSV(csvText: string): any[] {
  const lines = csvText.split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1)
    .filter(line => line.trim() !== '')
    .map(line => {
      const values = line.split(',');
      const obj: any = {};
      headers.forEach((header, i) => {
        const val = values[i];
        const trimmedHeader = header.trim();
        if (['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'].includes(trimmedHeader)) {
          obj[trimmedHeader] = parseFloat(val);
        } else {
          obj[trimmedHeader] = val ? val.trim() : val;
        }
      });
      return obj;
    });
}

function calculatePredictCrop(data: SoilData, allRows: any[]): PredictionResult[] {
  const scored = allRows.map(row => {
    const distance =
      Math.abs(row.N - data.n) +
      Math.abs(row.P - data.p) +
      Math.abs(row.K - data.k) +
      Math.abs(row.temperature - data.temp) +
      Math.abs(row.ph - data.ph) +
      Math.abs(row.rainfall - data.rainfall);

    const regionBonus = row.region === 'maharashtra' ? 0.8 : 1.0;
    const finalScore = distance * regionBonus;
    // Map distance to a 0-100% confidence/probability proxy
    const confidence = Math.max(0, Math.min(100, 100 - (finalScore / 10)));
    return { ...row, score: finalScore, confidence };
  });

  scored.sort((a, b) => (a.score || 0) - (b.score || 0));

  const seen = new Set();
  const top3: PredictionResult[] = [];

  for (const row of scored) {
    if (!seen.has(row.label)) {
      seen.add(row.label);
      top3.push(row);
    }
    if (top3.length === 3) break;
  }

  return top3;
}
import { useTranslation } from '../contexts/LanguageContext';

export const PredictCrop: React.FC = () => {
  const { t, language, translateBatch } = useTranslation();
  const [allRows, setAllRows] = useState<any[]>([]);
  const [formData, setFormData] = useState<SoilData>(() => {
    const saved = sessionStorage.getItem('predictFormData');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return {
          n: parsed.n ?? NaN,
          p: parsed.p ?? NaN,
          k: parsed.k ?? NaN,
          ph: parsed.ph ?? NaN,
          temp: parsed.temp ?? NaN,
          humidity: parsed.humidity ?? NaN,
          rainfall: parsed.rainfall ?? NaN,
        };
      } catch (e) {}
    }
    return {
      n: NaN,
      p: NaN,
      k: NaN,
      ph: NaN,
      temp: NaN,
      humidity: NaN,
      rainfall: NaN,
    };
  });

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<PredictionResult[] | null>(() => {
    const saved = sessionStorage.getItem('predictRecommendations');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {}
    }
    return null;
  });

  useEffect(() => {
    const loadDataset = async () => {
      try {
        const response = await fetch('/data/crop_merged.csv');
        const text = await response.text();
        const rows = parseCSV(text);
        setAllRows(rows);
      } catch (e) {
        console.error("Failed to load dataset:", e);
      }
    };
    loadDataset();
  }, []);

  useEffect(() => {
    sessionStorage.setItem('predictFormData', JSON.stringify(formData));
  }, [formData]);

  useEffect(() => {
    if (recommendations) {
      sessionStorage.setItem('predictRecommendations', JSON.stringify(recommendations));
    } else {
      sessionStorage.removeItem('predictRecommendations');
    }
  }, [recommendations]);

  useEffect(() => {
    const clearStorageOnRefresh = () => {
      sessionStorage.removeItem('predictFormData');
      sessionStorage.removeItem('predictRecommendations');
    };
    window.addEventListener('beforeunload', clearStorageOnRefresh);
    return () => window.removeEventListener('beforeunload', clearStorageOnRefresh);
  }, []);

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
        'Please enter all soil data fields before predicting.',
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
    if (errorMsg) setErrorMsg(null);
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

  const isAnyBlank = Object.values(formData).some(v => isNaN(v as number));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isAnyBlank) {
      setErrorMsg(t('Please enter all soil data fields before predicting.'));
      return;
    }
    if (allRows.length === 0) {
      setErrorMsg(t('Dataset still loading, please wait a moment.'));
      return;
    }
    setErrorMsg(null);
    setLoading(true);
    try {
      // Simulate minimal delay for UI feel
      await new Promise(res => setTimeout(res, 600));
      const recs = calculatePredictCrop(formData, allRows);
      setRecommendations(recs);
    } catch (error) {
      setErrorMsg(t('Prediction failed') + ': ' + (error as Error).message);
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
        {errorMsg && (
          <div className="mb-8 p-4 bg-red-500/10 border-l-4 border-red-500 rounded-r-lg flex items-start gap-4 shadow-sm backdrop-blur-sm">
            <div className="bg-red-500/20 p-1 rounded-full text-red-500 flex-shrink-0 mt-0.5">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <p className="font-headline font-bold text-red-600 dark:text-red-400 self-center">{errorMsg}</p>
          </div>
        )}
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
              className="bg-primary text-on-primary px-12 py-5 rounded-full font-headline font-extrabold text-lg tracking-tight uppercase transition-all active:scale-95 shadow-xl shadow-primary/20 flex items-center gap-3 disabled:opacity-50"
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
            {recommendations.map((result, idx) => (
              <ResultCard
                key={`${result.label}-${idx}`}
                result={result}
                label={
                  idx === 0 ? t('Primary Recommendation') :
                  idx === 1 ? t('Secondary Match') :
                  t('Tertiary Alternative')
                }
                name={t(result.label)}
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

const ResultCard: React.FC<{ result: PredictionResult; label: string; name: string; reason: string }> = ({ result, label, name, reason }) => {
  const navigate = useNavigate();
  const { t, translateBatch } = useTranslation();
  const { cropKey } = { cropKey: result.label };
  const slug = (cropKey || '').toLowerCase().replace(/\s+/g, '');
  const translation = cropTranslations[slug];
  const displayName = translation?.en || name;

  // Explanation Mapping Logic
  const getRegionExplanation = (district: string) => {
    const d = (district || '').toLowerCase();
    if (['kolhapur', 'sangli', 'satara', 'pune'].some(dn => d.includes(dn))) 
      return "Moderate to high rainfall region with fertile river basin soil.";
    if (['nagpur', 'wardha', 'amaravati'].some(dn => d.includes(dn)))
      return "Warm climate with moderate rainfall, ideal for citrus and cotton.";
    if (['nashik', 'ahmednagar'].some(dn => d.includes(dn)))
      return "Semi-arid climate with well-developed irrigation systems.";
    if (['ratnagiri', 'sindhudurg', 'raigad'].some(dn => d.includes(dn)))
      return "Coastal tropical climate with very high rainfall.";
    return "Region with similar historical cultivation success and climatic profile.";
  };

  const getSoilExplanation = (soil: string) => {
    const s = (soil || '').toLowerCase();
    if (s.includes('black')) return "High moisture retention capacity, rich in magnesium and iron.";
    if (s.includes('red')) return "Well-drained soil with good aeration, prevents root waterlogging.";
    if (s.includes('alluvial')) return "Extremely fertile and rich in nutrients, supports diverse crop types.";
    if (s.includes('laterite')) return "Rich in iron and aluminum, suitable for plantation crops.";
    return "Provides essential mineral structure required for this crop's growth.";
  };

  const getFertilizerExplanation = (fertilizer: string) => {
    const f = (fertilizer || '').toLowerCase();
    if (f.includes('urea')) return "High nitrogen source to promote fast green vegetative growth.";
    if (f.includes('dap')) return "Provides phosphorus and nitrogen for strong root development.";
    if (f.includes('ssp')) return "Supplies phosphorus and sulfur for better seed and fruit quality.";
    if (f.includes('potash') || f.includes('mop')) return "Enhances potassium levels for disease resistance and water regulation.";
    return "Supplies balanced nutrients to ensure optimal yield and soil health.";
  };

  const regionExplanation = getRegionExplanation(result.district || '');
  const soilExplanation = getSoilExplanation(result.soil_color || '');
  const fertExplanation = getFertilizerExplanation(result.fertilizer || '');

  // Trigger translation for dynamic explanations
  useEffect(() => {
    translateBatch([regionExplanation, soilExplanation, fertExplanation]);
  }, [regionExplanation, soilExplanation, fertExplanation, translateBatch]);

  const handleClick = () => {
    navigate(`/crop/${slug}`);
  };

  return (
    <div
      id={`result-card-${slug}`}
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      className="bg-surface-container-lowest p-6 rounded-2xl group hover:bg-surface-container transition-all duration-500 flex flex-col items-center text-center py-10 cursor-pointer border border-on-surface/5 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 hover:-translate-y-2"
    >
      <p className="font-body text-[10px] uppercase tracking-[0.2em] text-on-surface-variant/70 mb-4 font-bold">{label}</p>
      
      <div className="crop-card mb-4 min-w-[140px]">
        <h3 className="text-2xl font-display font-bold text-primary mb-1">{displayName}</h3>
        {translation?.hi && <p className="text-xs text-on-surface-variant/80 font-medium">{translation.hi}</p>}
        {translation?.mr && <p className="text-xs text-on-surface-variant/80 font-medium">{translation.mr}</p>}
      </div>
      
      {result.region === 'maharashtra' && (
        <div className="w-full space-y-4 my-2 px-2">
          {result.district && (
            <div className="text-left animate-in fade-in slide-in-from-bottom-2 duration-700">
              <p className="font-bold text-xs flex items-center gap-2 text-on-surface/90">
                <MapPin className="size-3.5 text-primary shrink-0" /> {t('Similar Region')}: <span className="text-primary">{result.district}</span>
              </p>
              <p className="text-[10px] leading-relaxed text-on-surface-variant/70 mt-0.5 ml-6 italic">
                ({t(regionExplanation)})
              </p>
            </div>
          )}
          
          {result.soil_color && (
            <div className="text-left animate-in fade-in slide-in-from-bottom-3 duration-700 delay-100">
              <p className="font-bold text-xs flex items-center gap-2 text-on-surface/90">
                <Layers className="size-3.5 text-primary shrink-0" /> {t('Suitable Soil')}: <span className="text-primary">{result.soil_color}</span>
              </p>
              <p className="text-[10px] leading-relaxed text-on-surface-variant/70 mt-0.5 ml-6 italic">
                ({t(soilExplanation)})
              </p>
            </div>
          )}
          
          {result.fertilizer && (
            <div className="text-left animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
              <p className="font-bold text-xs flex items-center gap-2 text-on-surface/90">
                <Sprout className="size-3.5 text-primary shrink-0" /> {t('Recommended Fertilizer')}: <span className="text-primary">{result.fertilizer}</span>
              </p>
              <p className="text-[10px] leading-relaxed text-on-surface-variant/70 mt-0.5 ml-6 italic">
                ({t(fertExplanation)})
              </p>
            </div>
          )}
        </div>
      )}

      <div className="mt-6 flex items-center text-on-surface-variant font-bold text-xs justify-center gap-2 py-2 px-4 bg-surface-container-low rounded-full">
        <CheckCircle2 className="w-3.5 h-3.5 text-primary" />
        {reason} {result.confidence ? `${result.confidence.toFixed(1)}%` : ''}
      </div>

      <div className="mt-4 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 flex items-center gap-1.5 text-[10px] font-bold text-primary uppercase tracking-wider">
        {t('View details')} <ArrowRight className="w-3 h-3" />
      </div>

      <p className="mt-8 text-[9px] text-on-surface-variant/30 font-medium tracking-tight">
        * {t('Based on similar agricultural conditions from real dataset')}
      </p>
    </div>
  );
};
// Add crop-card CSS for multi-language display
const style = document.createElement('style');
style.innerHTML = `
.crop-card {
  padding: 12px;
  border-radius: 10px;
  background: var(--color-surface-container-low);
  border: 1px solid var(--color-on-surface-variant-opacity);
  text-align: center;
  margin-bottom: 10px;
}
.crop-card h3 {
  font-size: 18px;
  font-weight: bold;
}
.crop-card p {
  font-size: 11px;
  opacity: 0.8;
}
`;
if (typeof window !== 'undefined' && !document.getElementById('crop-card-style')) {
  style.id = 'crop-card-style';
  document.head.appendChild(style);
}
