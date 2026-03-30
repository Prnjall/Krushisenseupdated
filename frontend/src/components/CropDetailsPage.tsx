import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import {
  ArrowLeft,
  Thermometer,
  Layers,
  Cloud,
  Droplets,
  Sun,
  BarChart2,
  FileText,
  Globe,
  ChevronDown,
} from 'lucide-react';
import { getCropBySlug } from '../data/cropData';
import { useTranslation, Language } from '../contexts/LanguageContext';
import { cropTranslations } from './PredictCrop';

// ─── Crop placeholder images (emoji-based SVG data URIs per crop) ───────────
const CROP_EMOJIS: Record<string, string> = {
  rice: '🌾', maize: '🌽', chickpea: '🫘', kidneybeans: '🫘',
  pigeonpeas: '🫘', mothbeans: '🫘', mungbean: '🫛', blackgram: '🫘',
  lentil: '🫘', pomegranate: '🍎', banana: '🍌', mango: '🥭',
  grapes: '🍇', watermelon: '🍉', muskmelon: '🍈', apple: '🍎',
  orange: '🍊', papaya: '🍑', coconut: '🥥', cotton: '🌸',
  jute: '🌿', coffee: '☕', sugarcane: '🎋', cucumber: '🥒',
  jowar: '🌾', tur: '🫘', urad: '🫘', moong: '🫛',
  gram: '🫘', masoor: '🫘', ginger: '🫚', turmeric: '🫚',
  tobacco: '🍂', groundnut: '🥜', soybean: '🫛', mustard: '🌼',
  sunflower: '🌻', tea: '🍵', rubber: '🌳', pulses: '🫘'
};

function getCropImage(slug: string): string {
  const emoji = CROP_EMOJIS[slug] || '🌱';
  return `data:image/svg+xml,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#1a1a1a"/>
          <stop offset="100%" style="stop-color:#333333"/>
        </linearGradient>
      </defs>
      <rect width="600" height="600" fill="url(#bg)"/>
      <text x="300" y="310" font-size="200" text-anchor="middle" dominant-baseline="middle">${emoji}</text>
    </svg>`
  )}`;
}

// ─── Season icon selector ────────────────────────────────────────────────────
const SeasonIcon: React.FC<{ season: string }> = ({ season }) => {
  const s = season.toLowerCase();
  if (s.includes('kharif'))   return <Sun className="w-7 h-7 text-neutral-700" />;
  if (s.includes('rabi'))     return <Cloud className="w-7 h-7 text-neutral-700" />;
  if (s.includes('zaid'))     return <Thermometer className="w-7 h-7 text-neutral-700" />;
  if (s.includes('winter'))   return <Cloud className="w-7 h-7 text-neutral-700" />;
  if (s.includes('summer'))   return <Sun className="w-7 h-7 text-neutral-700" />;
  if (s.includes('autumn'))   return <Layers className="w-7 h-7 text-neutral-700" />;
  return <Sun className="w-7 h-7 text-neutral-700" />;
};

// ════════════════════════════════════════════════════════════════════════════
export const CropDetailsPage: React.FC = () => {
  const { cropName } = useParams<{ cropName: string }>();
  const navigate = useNavigate();
  const { t, language, setLanguage, translateBatch } = useTranslation();
  const [showLangMenu, setShowLangMenu] = React.useState(false);

  const languages: { code: Language; name: string }[] = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi (हिंदी)' },
    { code: 'mr', name: 'Marathi (मराठी)' },
  ];

  const slug = (cropName ?? '').toLowerCase();
  const crop = getCropBySlug(slug);

  React.useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [slug]);

  React.useEffect(() => {
    if (language !== 'en' && crop) {
      translateBatch([
        crop.description,
        crop.season,
        crop.temperature,
        crop.soil,
        crop.climate,
        crop.note,
        crop.why,
        crop.category,
        crop.seasonDescription,
        crop.scientificName,
        "Back to Results",
        "About this Crop",
        "Cultivation Window",
        "Temperature",
        "Soil Type",
        "Climate",
        "Water Requirement",
        "Approx",
        "Why this crop is recommended"
      ]);
    }
  }, [language, crop, translateBatch]);

  // ── Not found ──────────────────────────────────────────────────────────────
  if (!crop) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-6 px-6 bg-white">
        <p className="font-headline font-black text-6xl text-black">404</p>
        <p className="font-body text-neutral-500 text-lg">
          Crop <span className="font-bold text-black">"{cropName}"</span> not found in our database.
        </p>
        <button
          onClick={() => window.history.length > 1 ? navigate(-1) : navigate('/predict')}
          className="flex items-center gap-2 bg-black text-white px-8 py-4 rounded-full font-headline font-extrabold uppercase tracking-tight transition-all active:scale-95 hover:bg-neutral-800"
        >
          <ArrowLeft className="w-5 h-5" /> {t("Back to Results")}
        </button>
      </div>
    );
  }

  const imgSrc = getCropImage(slug);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="min-h-screen bg-white"
    >
      {/* ── Top bar ──────────────────────────────────────────────────────── */}
      <div className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-neutral-100">
        <div className="max-w-6xl mx-auto px-6 py-4 flex flex-row items-center justify-between">
          <div className="flex-1">
            <button
              id="back-to-results-btn"
              onClick={() => navigate('/predict')}
              className="flex items-center gap-2 font-body text-sm text-neutral-600 hover:text-black transition-colors group"
            >
              <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1 duration-200" />
              {t("Back to Results")}
            </button>
          </div>
          
          <div className="flex-shrink-0 flex justify-center">
            <h1 className="font-headline font-bold text-lg tracking-tight text-black flex items-center gap-2">
              {cropTranslations[slug]?.en || crop.name}
              {cropTranslations[slug]?.hi && (
                <span className="hidden sm:inline text-sm text-neutral-500 font-normal">
                  • {cropTranslations[slug].hi} • {cropTranslations[slug].mr}
                </span>
              )}
            </h1>
          </div>

          <div className="flex-1 flex justify-end">
            <div className="relative">
              <div 
                className="flex items-center gap-2 text-black font-headline font-bold text-sm tracking-tight cursor-pointer active:scale-95 duration-150"
                onClick={() => setShowLangMenu(!showLangMenu)}
              >
                <Globe className="w-5 h-5 text-neutral-600" />
                <span className="hidden md:inline">{languages.find(l => l.code === language)?.name.split(' ')[0]}</span>
                <ChevronDown className={`w-4 h-4 text-neutral-400 transition-transform ${showLangMenu ? 'rotate-180' : ''}`} />
              </div>

              {showLangMenu && (
                <div className="absolute right-0 mt-3 w-40 bg-white border border-neutral-200 rounded-lg shadow-xl overflow-hidden z-[60]">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      className={`w-full text-left px-4 py-3 font-headline font-bold text-sm transition-colors ${
                        language === lang.code ? 'bg-primary text-on-primary' : 'hover:bg-neutral-100 text-black'
                      }`}
                      onClick={() => {
                        setLanguage(lang.code);
                        setShowLangMenu(false);
                      }}
                    >
                      {lang.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div className="max-w-6xl mx-auto px-6 py-10 md:py-14">

        {/* === SECTION 1 — Hero grid === */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12"
        >
          {/* Left column: image + cultivation window */}
          <div className="flex flex-col gap-6">
            {/* Crop image card */}
            <div className="relative rounded-3xl overflow-hidden aspect-square shadow-lg">
              <img
                src={imgSrc}
                alt={crop.name}
                className="w-full h-full object-cover grayscale"
              />
              {/* Overlay label at bottom */}
              <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
                <p className="font-body text-[10px] uppercase tracking-[0.25em] text-white/60 mb-1">
                  {t(crop.category)}
                </p>
                <p className="font-headline font-bold text-white text-xl">
                  {t(crop.scientificName)}
                </p>
              </div>
            </div>

            {/* Cultivation window card */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
              className="bg-white rounded-2xl p-6 border border-neutral-200 shadow-sm"
            >
              <p className="font-body text-[10px] uppercase tracking-[0.25em] text-neutral-400 mb-4">
                {t("Cultivation Window")}
              </p>
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-headline font-black text-3xl tracking-tight text-black">
                  {t(crop.season)}
                </h2>
                <div className="bg-neutral-100 p-2.5 rounded-full">
                  <SeasonIcon season={t(crop.season)} />
                </div>
              </div>
              <p className="font-body text-sm text-neutral-500 leading-relaxed">
                {t(crop.seasonDescription)}
              </p>
            </motion.div>
          </div>

          {/* Right column: About + info cards + climate + water */}
          <div className="flex flex-col gap-6">
            {/* About the crop description */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.18, duration: 0.4 }}
            >
              <h2 className="font-headline font-black text-2xl tracking-tighter text-black mb-3">
                {t("About this Crop")}
              </h2>
              <p className="font-body text-neutral-600 leading-relaxed text-[15px]">
                {t(crop.description)}
              </p>
            </motion.div>

            {/* Why recommended */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.4 }}
            >
              <h2 className="font-headline font-black text-3xl md:text-[2.5rem] tracking-tighter text-black mb-5 leading-[1.1]">
                {t("Why this crop is recommended")}
              </h2>
              <div className="border-l-[3px] border-neutral-200 pl-5">
                <p className="font-body text-neutral-500 leading-relaxed text-[15px] italic">
                  {t(crop.why)}
                </p>
              </div>
            </motion.div>

            {/* Info grid: {t("Temperature")} + {t("Soil Type")} */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35, duration: 0.4 }}
              className="grid grid-cols-2 gap-4"
            >
              <div className="bg-white rounded-2xl p-5 border border-neutral-200 group hover:border-neutral-400 transition-colors duration-300">
                <div className="flex items-center gap-2 mb-4">
                  <Thermometer className="w-4 h-4 text-neutral-400" />
                  <p className="font-body text-xs text-neutral-400 tracking-wide">
                    {t("Temperature")}
                  </p>
                </div>
                <p className="font-headline font-black text-xl tracking-tight text-black">
                  {t(crop.temperature)}
                </p>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-neutral-200 group hover:border-neutral-400 transition-colors duration-300">
                <div className="flex items-center gap-2 mb-4">
                  <Layers className="w-4 h-4 text-neutral-400" />
                  <p className="font-body text-xs text-neutral-400 tracking-wide">
                    {t("Soil Type")}
                  </p>
                </div>
                <p className="font-headline font-black text-xl tracking-tight text-black leading-tight">
                  {t(crop.soil)}
                </p>
              </div>
            </motion.div>

            {/* {t("Climate")} card */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.4 }}
              className="bg-white rounded-2xl p-5 border border-neutral-200 group hover:border-neutral-400 transition-colors duration-300"
            >
              <div className="flex items-center gap-2 mb-4">
                <Cloud className="w-4 h-4 text-neutral-400" />
                <p className="font-body text-xs text-neutral-400 tracking-wide">
                  {t("Climate")}
                </p>
              </div>
              <p className="font-headline font-black text-2xl tracking-tight text-black">
                {t(crop.climate)}
              </p>
            </motion.div>
          </div>
        </motion.div>

        {/* === SECTION 2 — {t("Water Requirement")} (dark card) === */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="mt-8"
        >
          <div className="relative rounded-3xl overflow-hidden bg-neutral-900 text-white p-8 md:p-10 shadow-xl max-w-xl">
            {/* Subtle background pattern */}
            <div className="absolute inset-0 opacity-[0.04]">
              <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="water-pattern" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse">
                    <circle cx="30" cy="30" r="20" fill="none" stroke="white" strokeWidth="0.5" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#water-pattern)" />
              </svg>
            </div>

            {/* Background wave decoration */}
            <svg
              className="absolute right-0 bottom-0 opacity-10"
              width="300" height="200" viewBox="0 0 300 200"
              aria-hidden="true"
            >
              <path d="M0 100 Q75 40 150 100 Q225 160 300 100 L300 200 L0 200 Z" fill="white" />
              <path d="M0 130 Q75 70 150 130 Q225 190 300 130 L300 200 L0 200 Z" fill="white" />
            </svg>

            <div className="relative z-10">
              <div className="flex flex-col gap-4 font-body">
                <p className="font-headline font-black text-2xl tracking-tight text-white flex items-center mb-2">
                  <Droplets className="w-6 h-6 mr-3 text-blue-400" /> {t("Water Requirement")}: {crop.water}
                </p>
                <p className="text-xl text-neutral-300 flex items-center">
                  <BarChart2 className="w-5 h-5 mr-3 text-neutral-400" /> {t("Approx")}: {t(crop.water_mm)}
                </p>
                <p className="text-xl text-neutral-300 flex items-center mt-1">
                  <FileText className="w-5 h-5 mr-3 text-neutral-400 flex-shrink-0" /> <span className="leading-snug">{t(crop.note)}</span>
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* ── Minimal footer ────────────────────────────────────────────────── */}
      <footer className="border-t border-neutral-100 mt-12">
        <div className="max-w-6xl mx-auto px-6 py-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <span className="font-headline font-black text-black tracking-tight">KrushiSense</span>
          <div className="flex gap-6 text-[11px] text-neutral-400 uppercase tracking-widest font-body">
            <a href="#" className="hover:text-black transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-black transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-black transition-colors">Contact Support</a>
          </div>
          <span className="text-[11px] text-neutral-400 font-body">
            © 2024 KrushiSense. The Digital Curator.
          </span>
        </div>
      </footer>
    </motion.div>
  );
};
