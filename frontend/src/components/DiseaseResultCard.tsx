import React from 'react';
import { useTranslation } from '../contexts/LanguageContext';
import { AlertTriangle, CheckCircle, Info, XCircle, RefreshCcw } from 'lucide-react';

export interface DiseaseResult {
  success: boolean;
  status: 'HEALTHY' | 'DISEASE_DETECTED' | 'LOW_CONFIDENCE' | 'UNSUPPORTED_CROP' | 'INVALID_IMAGE' | 'ANALYSIS_UNAVAILABLE';
  crop?: string;
  message?: string;
  diagnosis?: {
    disease: string;
    class_name: string;
    confidence: number;
  };
  confidence?: number;
}

interface DiseaseResultCardProps {
  result: DiseaseResult;
  onRetry: () => void;
}

export const DiseaseResultCard: React.FC<DiseaseResultCardProps> = ({ result, onRetry }) => {
  const { t } = useTranslation();

  const formatConfidence = (conf?: number) => {
    if (conf === undefined) return null;
    return `${Math.round(conf * 100)}%`;
  };

  const renderContent = () => {
    switch (result.status) {
      case 'HEALTHY':
        return (
          <div className="flex flex-col items-center text-center p-6 bg-green-500/10 border border-green-500/30 rounded-2xl">
            <CheckCircle className="w-16 h-16 text-green-500 mb-4" />
            <h3 className="font-headline font-black text-2xl text-green-600 dark:text-green-400 mb-2">
              {t('Plant appears healthy')}
            </h3>
            <p className="text-on-surface-variant mb-6 text-sm">
              {t('No common disease was detected by the screening model.')}
            </p>
            
            <div className="flex gap-8 items-center bg-surface-container-lowest py-3 px-6 rounded-xl w-full justify-center">
              <div>
                <p className="text-xs uppercase tracking-wider font-bold text-on-surface-variant">{t('Crop')}</p>
                <p className="font-headline font-bold text-lg capitalize">{t(result.crop || '')}</p>
              </div>
              <div className="w-px h-10 bg-on-surface/10"></div>
              <div>
                <p className="text-xs uppercase tracking-wider font-bold text-on-surface-variant">{t('Confidence')}</p>
                <p className="font-headline font-bold text-lg text-green-600 dark:text-green-400">
                  {formatConfidence(result.diagnosis?.confidence || result.confidence)}
                </p>
              </div>
            </div>
          </div>
        );

      case 'DISEASE_DETECTED':
        return (
          <div className="flex flex-col items-center text-center p-6 bg-orange-500/10 border border-orange-500/30 rounded-2xl">
            <AlertTriangle className="w-16 h-16 text-orange-500 mb-4" />
            <h3 className="font-headline font-black text-2xl text-orange-600 dark:text-orange-400 mb-2">
              {t('Possible disease detected')}
            </h3>
            <p className="text-on-surface-variant mb-6 text-sm">
              {t('AI screening indicates a possible case of')} <span className="font-bold text-on-surface">{t(result.diagnosis?.disease || '')}</span>.
            </p>
            
            <div className="flex gap-4 md:gap-8 items-center bg-surface-container-lowest py-3 px-4 md:px-6 rounded-xl w-full justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider font-bold text-on-surface-variant">{t('Crop')}</p>
                <p className="font-headline font-bold text-lg capitalize">{t(result.crop || '')}</p>
              </div>
              <div className="w-px h-10 bg-on-surface/10"></div>
              <div className="flex-1 text-center">
                <p className="text-xs uppercase tracking-wider font-bold text-on-surface-variant">{t('Disease')}</p>
                <p className="font-headline font-bold text-lg text-orange-600 dark:text-orange-400">
                  {t(result.diagnosis?.disease || '')}
                </p>
              </div>
              <div className="w-px h-10 bg-on-surface/10"></div>
              <div>
                <p className="text-xs uppercase tracking-wider font-bold text-on-surface-variant">{t('Confidence')}</p>
                <p className="font-headline font-bold text-lg text-orange-600 dark:text-orange-400">
                  {formatConfidence(result.diagnosis?.confidence || result.confidence)}
                </p>
              </div>
            </div>
          </div>
        );

      case 'LOW_CONFIDENCE':
        return (
          <div className="flex flex-col items-center text-center p-6 bg-yellow-500/10 border border-yellow-500/30 rounded-2xl">
            <Info className="w-16 h-16 text-yellow-600 dark:text-yellow-400 mb-4" />
            <h3 className="font-headline font-black text-2xl text-yellow-700 dark:text-yellow-400 mb-2">
              {t('Unable to determine reliably')}
            </h3>
            <p className="text-on-surface-variant mb-4 text-sm">
              {t('Please upload a clearer photo showing the affected leaf.')}
            </p>
            <div className="text-left bg-surface-container-lowest p-4 rounded-xl w-full text-sm text-on-surface-variant">
              <p className="font-bold mb-2 uppercase tracking-wide text-xs">{t('Suggestions for better results:')}</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>{t('Ensure good lighting')}</li>
                <li>{t('Leaf should fill most of the frame')}</li>
                <li>{t('Avoid blurry or out-of-focus images')}</li>
                <li>{t('Avoid heavily obstructed leaves')}</li>
              </ul>
            </div>
          </div>
        );

      case 'UNSUPPORTED_CROP':
        return (
          <div className="flex flex-col items-center text-center p-6 bg-surface-container-high rounded-2xl border border-outline-variant/30">
            <Info className="w-16 h-16 text-on-surface-variant mb-4" />
            <h3 className="font-headline font-black text-xl text-on-surface mb-2">
              {t('Screening not available')}
            </h3>
            <p className="text-on-surface-variant text-sm">
              {t('Disease screening is not available for this crop yet.')}
            </p>
          </div>
        );

      case 'INVALID_IMAGE':
        return (
          <div className="flex flex-col items-center text-center p-6 bg-red-500/10 border border-red-500/30 rounded-2xl">
            <XCircle className="w-16 h-16 text-red-500 mb-4" />
            <h3 className="font-headline font-black text-xl text-red-600 dark:text-red-400 mb-2">
              {t('Invalid Image')}
            </h3>
            <p className="text-on-surface-variant text-sm mb-4">
              {t('Please upload a valid crop image.')}
            </p>
            <div className="bg-surface-container-lowest py-2 px-4 rounded-lg inline-block text-xs font-bold text-on-surface-variant">
              {t('JPG, PNG, WebP • Maximum 5 MB')}
            </div>
          </div>
        );

      case 'ANALYSIS_UNAVAILABLE':
      default:
        return (
          <div className="flex flex-col items-center text-center p-6 bg-surface-container-high rounded-2xl border border-outline-variant/30">
            <RefreshCcw className="w-16 h-16 text-on-surface-variant mb-4 opacity-50" />
            <h3 className="font-headline font-black text-xl text-on-surface mb-2">
              {t('Analysis Unavailable')}
            </h3>
            <p className="text-on-surface-variant text-sm mb-6">
              {t('Disease screening is temporarily unavailable.')}
            </p>
            <button 
              onClick={onRetry}
              className="bg-primary text-on-primary px-6 py-2 rounded-full font-bold text-sm hover:opacity-90 active:scale-95 transition-all"
            >
              {t('Try Again')}
            </button>
          </div>
        );
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto" role="alert" aria-live="polite">
      {renderContent()}
      
      <div className="mt-6 text-center text-xs text-on-surface-variant/70 italic px-4">
        {t('AI-assisted screening only. Results are not a confirmed diagnosis. For serious or uncertain cases, consult a local agricultural expert or KVK.')}
      </div>
    </div>
  );
};
