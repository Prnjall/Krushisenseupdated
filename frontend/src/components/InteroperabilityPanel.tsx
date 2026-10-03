import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Network, Database, Share2, Server, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';
import { safeFetchJson } from '../lib/api';

interface InteroperabilityPanelProps {
  language: string;
  locationQuery: string;
  formData: any;
  weatherData: any;
  weatherForecast: any;
  satelliteData: any;
  recommendations: any[];
}

export const InteroperabilityPanel: React.FC<InteroperabilityPanelProps> = ({
  language,
  locationQuery,
  formData,
  weatherData,
  weatherForecast,
  satelliteData,
  recommendations,
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [advisory, setAdvisory] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Build the canonical payload expected by /api/v1/interop/advisory/
  const canonicalPayload = {
    schema_version: "1.0",
    context: {
      region: locationQuery || "Unknown region",
      country: "India",
      language: language,
    },
    soil: {
      nitrogen: isNaN(formData.n) ? null : { value: formData.n, unit: "mg/kg", source: "farmer_input" },
      phosphorus: isNaN(formData.p) ? null : { value: formData.p, unit: "mg/kg", source: "farmer_input" },
      potassium: isNaN(formData.k) ? null : { value: formData.k, unit: "mg/kg", source: "farmer_input" },
      ph: isNaN(formData.ph) ? null : { value: formData.ph, unit: "pH", source: "farmer_input" }
    },
    environment: {
      temperature_c: isNaN(formData.temp) ? null : { value: formData.temp, unit: "C", source: "farmer_input" },
      humidity_percent: isNaN(formData.humidity) ? null : { value: formData.humidity, unit: "%", source: "farmer_input" },
      precipitation_mm: isNaN(formData.rainfall) ? null : { value: formData.rainfall, unit: "mm", source: "farmer_input" }
    },
    forecast: weatherForecast ? {
      horizon_days: weatherForecast?.length || 7,
      daily_forecasts: weatherForecast?.map((f: any) => ({
        date: f.date,
        temperature_max_c: f.temperature_max,
        temperature_min_c: f.temperature_min,
        precipitation_mm: f.precipitation_sum,
        precipitation_probability_percent: f.precipitation_probability,
        weather_code: f.weather_code
      })) || [],
      risk_signals: []
    } : null,
    satellite: satelliteData ? {
      indicator: "NDVI",
      value: satelliteData.ndvi,
      unit: "unitless",
      observed_at: satelliteData.date_acquired || new Date().toISOString(),
      cloud_cover_percent: satelliteData.cloud_cover,
      source: satelliteData.source || "Sentinel-2",
      days_since_observation: satelliteData.days_since || 0
    } : null,
    crop_prediction: recommendations?.[0] ? {
      crop_canonical: recommendations[0].label,
      confidence: (recommendations[0].confidence || 0) / 100, // expecting 0-1
      prediction_status: "high_confidence",
      data_familiarity: "high",
      estimated_yield: recommendations[0].estimated_yield,
      regenerative_signals: recommendations[0].regenerative_reasons || []
    } : null,
    provenance: [
      {
        source_id: "ks_farmer_01",
        provider: "KrushiSense",
        freshness_category: "CURRENT"
      }
    ]
  };

  const handleShare = async () => {
    setLoading(true);
    setErrorMsg(null);
    setAdvisory(null);
    try {
      const { success, data, error, errorType } = await safeFetchJson('/api/v1/interop/advisory/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(canonicalPayload),
      });

      if (!success) {
        if (errorType === 'AI_UNAVAILABLE' || errorType === 'RESOURCE_EXHAUSTED' || error === 'AI advisory is temporarily unavailable.') {
          setErrorMsg(t("Canonical data prepared successfully. AI advisory is temporarily unavailable."));
        } else {
          setErrorMsg(t("Failed to generate interoperable advisory") + ": " + (error || "Unknown error"));
        }
      } else {
        setAdvisory(data.advisory);
      }
    } catch (e) {
      setErrorMsg(t("Network error connecting to interoperability endpoint."));
    } finally {
      setLoading(false);
    }
  };

  const hasSoil = !isNaN(formData.n) || !isNaN(formData.p) || !isNaN(formData.k) || !isNaN(formData.ph);
  const hasEnv = !isNaN(formData.temp) || !isNaN(formData.humidity) || !isNaN(formData.rainfall);
  
  return (
    <div className="mt-16 max-w-5xl mx-auto border-2 border-primary/20 bg-surface-container-lowest rounded-3xl overflow-hidden shadow-xl">
      <div className="bg-primary/5 p-6 md:p-8 flex items-center justify-between border-b border-primary/10">
        <div>
          <h3 className="font-headline font-black text-2xl text-primary flex items-center gap-3">
            <Network className="w-7 h-7" />
            {t("Interoperable Agricultural Intelligence")}
          </h3>
          <p className="font-body text-sm text-on-surface-variant mt-2 max-w-2xl">
            {t("Designed for integration across state and national agricultural platforms. KrushiSense converts heterogeneous agricultural signals into a common schema so compatible agricultural platforms can exchange context consistently.")}
          </p>
          <div className="mt-4 flex flex-col items-start gap-1">
            <span className="inline-block bg-secondary/10 text-secondary border border-secondary/20 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest">
              {t("Cross-System Agriculture")}
            </span>
            <p className="font-body text-xs text-on-surface-variant/80">
              {t("BRICS-ready interoperability architecture. Designed to support future BRICS agricultural data exchange through a canonical schema.")}
            </p>
          </div>
        </div>
      </div>

      <div className="p-6 md:p-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Column 1: Local Data */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2 mb-2 border-b border-surface-container-highest pb-2">
              <Database className="w-5 h-5 text-secondary" />
              <h4 className="font-headline font-bold text-lg text-secondary uppercase tracking-tight">{t("Local Farm Data")}</h4>
            </div>
            
            <div className="space-y-4">
              <div className="bg-surface-container-low p-3 rounded-lg text-sm">
                <span className="font-bold block mb-1 text-on-surface-variant">{t("Soil")}</span>
                {hasSoil ? (
                  <div className="grid grid-cols-2 gap-1 text-xs">
                    <span>N: {isNaN(formData.n) ? '-' : formData.n}</span>
                    <span>P: {isNaN(formData.p) ? '-' : formData.p}</span>
                    <span>K: {isNaN(formData.k) ? '-' : formData.k}</span>
                    <span>pH: {isNaN(formData.ph) ? '-' : formData.ph}</span>
                  </div>
                ) : <span className="text-xs italic text-on-surface-variant/50">{t("Unavailable")}</span>}
              </div>

              <div className="bg-surface-container-low p-3 rounded-lg text-sm">
                <span className="font-bold block mb-1 text-on-surface-variant">{t("Environment")}</span>
                {hasEnv ? (
                  <div className="grid grid-cols-2 gap-1 text-xs">
                    <span>{t("Temp")}: {isNaN(formData.temp) ? '-' : `${formData.temp}°C`}</span>
                    <span>{t("Hum")}: {isNaN(formData.humidity) ? '-' : `${formData.humidity}%`}</span>
                    <span>{t("Rain")}: {isNaN(formData.rainfall) ? '-' : `${formData.rainfall}mm`}</span>
                  </div>
                ) : <span className="text-xs italic text-on-surface-variant/50">{t("Unavailable")}</span>}
              </div>
            </div>
          </div>

          {/* Column 2: Canonical Context */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2 mb-2 border-b border-surface-container-highest pb-2">
              <Share2 className="w-5 h-5 text-tertiary" />
              <h4 className="font-headline font-bold text-lg text-tertiary uppercase tracking-tight">{t("Canonical Context")}</h4>
            </div>

            <div className="space-y-4">
              <div className="bg-surface-container-low p-3 rounded-lg text-sm">
                <span className="font-bold block mb-1 text-on-surface-variant">{t("Data Sources")}</span>
                <ul className="text-xs space-y-1">
                  {hasSoil && <li className="flex gap-1 items-center"><CheckCircle2 className="w-3 h-3 text-green-500"/> {t("Farmer-entered")}</li>}
                  {weatherData && <li className="flex gap-1 items-center"><CheckCircle2 className="w-3 h-3 text-green-500"/> {t("Open-Meteo")}</li>}
                  {satelliteData && <li className="flex gap-1 items-center"><CheckCircle2 className="w-3 h-3 text-green-500"/> {t("Sentinel")}</li>}
                  {recommendations?.[0] && <li className="flex gap-1 items-center"><CheckCircle2 className="w-3 h-3 text-green-500"/> {t("KrushiSense ML")}</li>}
                </ul>
              </div>

              <div className="bg-surface-container-low p-3 rounded-lg text-sm">
                <span className="font-bold block mb-1 text-on-surface-variant">{t("Crop Intelligence")}</span>
                {recommendations?.[0] ? (
                  <div className="text-xs space-y-1">
                    <div><span className="font-semibold">{t("Crop")}:</span> {t(recommendations[0].label)} ({(recommendations[0].confidence || 0).toFixed(1)}%)</div>
                    {recommendations[0].estimated_yield !== undefined && <div><span className="font-semibold">{t("Yield Index")}:</span> {recommendations[0].estimated_yield.toFixed(2)}</div>}
                    {recommendations[0].regenerative_reasons?.length > 0 && (
                      <div className="text-primary font-medium mt-1 truncate" title={recommendations[0].regenerative_reasons.map((t_str: string) => t(t_str)).join(', ')}>
                        + {recommendations[0].regenerative_reasons.length} {t("Regenerative Signals")}
                      </div>
                    )}
                  </div>
                ) : <span className="text-xs italic text-on-surface-variant/50">{t("Unavailable")}</span>}
              </div>
            </div>
          </div>

          {/* Column 3: Partner System */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2 mb-2 border-b border-surface-container-highest pb-2">
              <Server className="w-5 h-5 text-primary" />
              <h4 className="font-headline font-bold text-lg text-primary uppercase tracking-tight">{t("Example Partner System")}</h4>
            </div>
            
            <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-4 flex flex-col h-full items-center justify-center text-center gap-4">
              <button 
                onClick={handleShare}
                disabled={loading}
                className="bg-primary/10 text-primary hover:bg-primary/20 px-6 py-3 rounded-full font-bold text-sm tracking-wide uppercase transition-all disabled:opacity-50 flex items-center gap-2 w-full justify-center"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Share2 className="w-4 h-4" />}
                {t("Preview Interoperable Data")}
              </button>

              <p className="text-[10px] text-on-surface-variant/60 leading-tight">
                {t("Canonical schemas allow participating systems to map their local agricultural data into a shared representation.")}
              </p>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {errorMsg && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="mt-6 p-4 bg-orange-500/10 border-l-4 border-orange-500 rounded-r-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-orange-500 mt-0.5 shrink-0" />
            <p className="text-sm font-medium text-orange-700 dark:text-orange-400">{errorMsg}</p>
          </motion.div>
        )}

        {advisory && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="mt-6 border border-primary/20 rounded-xl p-5 bg-primary/5 text-left">
            <h5 className="font-headline font-bold text-primary mb-3 uppercase tracking-tight text-sm">
              {t("Partner AI Response")}
            </h5>
            <div className="space-y-4 text-sm font-body">
              <p><strong>{t("Summary")}:</strong> {advisory.summary}</p>
              {advisory.next_steps && advisory.next_steps.length > 0 && (
                <div>
                  <p className="mb-2"><strong>{t("Next Steps")}:</strong></p>
                  <ul className="list-disc pl-5 space-y-1 text-on-surface-variant">
                    {advisory.next_steps.map((step: string, i: number) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};
