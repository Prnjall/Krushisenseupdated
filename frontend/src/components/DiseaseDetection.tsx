import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { UploadCloud, Image as ImageIcon, X, Loader2, Camera, ChevronRight } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';
import { safeFetchJson } from '../lib/api';
import { DiseaseResultCard, DiseaseResult } from './DiseaseResultCard';
import { DiseaseAdvisoryCard, DiseaseAdvisory } from './DiseaseAdvisoryCard';

const SUPPORTED_CROPS = [
  { id: 'apple', label: 'Apple' },
  { id: 'maize', label: 'Maize' },
  { id: 'grapes', label: 'Grapes' },
  { id: 'rice', label: 'Rice' }
];

export const DiseaseDetection: React.FC = () => {
  const { t, language, translateBatch } = useTranslation();
  
  const [selectedCrop, setSelectedCrop] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<DiseaseResult | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  
  const [aiAdvisory, setAiAdvisory] = useState<DiseaseAdvisory | null>(null);
  const [aiAdvisoryLoading, setAiAdvisoryLoading] = useState(false);
  const [aiAdvisoryError, setAiAdvisoryError] = useState<string | null>(null);
  
  const advisoryAbortController = useRef<AbortController | null>(null);
  

  
  const [showMobileUploadMenu, setShowMobileUploadMenu] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const galleryInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (language !== 'en') {
      translateBatch([
        'AI-Assisted Disease Screening',
        'Upload a clear photo of a crop leaf to screen for common diseases.',
        'Select Crop',
        'Upload a leaf image',
        'JPG, PNG or WebP • Maximum 5 MB',
        'Analyze Crop',
        'Analyzing...',
        'Drag & drop image here or click to browse',
        'Take a photo',
        'Remove image',
        'Your image is analyzed for this screening request and is not stored by KrushiSense.',
        'Please select a supported crop first.',
        'File size exceeds 5MB limit.',
        'Invalid file type. Please upload a JPG, PNG or WebP image.',
        'An error occurred during upload. Please try again.',
        'An error occurred during analysis. Please try again.',
        'AI disease advisory is temporarily unavailable.',
        'Apple', 'Maize', 'Grapes', 'Rice',
        'Add Crop Image',
        'Take Photo',
        'Choose from Gallery',
        'Cancel',
        'Healthy',
        'Apple Scab', 'Apple Black Rot',
        'Maize Cercospora Leaf Spot', 'Maize Common Rust', 'Maize Northern Leaf Blight',
        'Grape Black Rot', 'Grape Esca', 'Grape Leaf Blight',
        'Rice Bacterial Leaf Blight', 'Rice Brown Spot', 'Rice Leaf Smut',
        'Updating advice...'
      ]);
    }
  }, [language, translateBatch]);

  // Clean up object URLs to prevent memory leaks
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleCropSelect = (cropId: string) => {
    setSelectedCrop(cropId);
    setResult(null); // Reset result when crop changes
    setAiAdvisory(null);
    setAiAdvisoryError(null);
    setValidationError(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const handleUploadClick = () => {
    // Check if device is mobile width (less than 768px for standard tailwind md breakpoint)
    if (window.innerWidth < 768) {
      setShowMobileUploadMenu(true);
    } else {
      fileInputRef.current?.click();
    }
  };

  const validateAndSetFile = (file: File) => {
    setValidationError(null);
    setResult(null); // Reset result when new image is uploaded
    setAiAdvisory(null);
    setAiAdvisoryError(null);

    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setValidationError(t('Invalid file type. Please upload a JPG, PNG or WebP image.'));
      return;
    }

    // Check file size (5MB = 5 * 1024 * 1024 bytes)
    if (file.size > 5 * 1024 * 1024) {
      setValidationError(t('File size exceeds 5MB limit.'));
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleRemoveImage = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setResult(null);
    setAiAdvisory(null);
    setAiAdvisoryError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    if (!selectedCrop) {
      setValidationError(t('Please select a supported crop first.'));
      return;
    }
    if (!selectedFile) {
      return;
    }

    setIsAnalyzing(true);
    setValidationError(null);
    setResult(null);
    setAiAdvisory(null);
    setAiAdvisoryError(null);

    const formData = new FormData();
    formData.append('crop', selectedCrop);
    formData.append('image', selectedFile);

    try {
      const { success, data, error } = await safeFetchJson('/api/disease-detection', {
        method: 'POST',
        body: formData,
      }, t('An error occurred during analysis. Please try again.'));

      if (!success) {
        setResult({
          success: false,
          status: 'ANALYSIS_UNAVAILABLE',
          message: error
        });
      } else {
        setResult(data);
      }
    } catch (error) {
      setResult({
        success: false,
        status: 'ANALYSIS_UNAVAILABLE',
        message: t('An error occurred during upload. Please try again.')
      });
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => {
        document.getElementById('analysis-result')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    }
  };

  const handleGetAdvisory = async (signal?: AbortSignal) => {
    if (!result || !selectedCrop) return;
    
    setAiAdvisoryLoading(true);
    setAiAdvisoryError(null);
    
    try {
      const payload = {
        language,
        crop: selectedCrop,
        diagnosis: result.diagnosis ? {
          status: result.status,
          disease: result.diagnosis.disease,
          class_name: result.diagnosis.class_name,
          confidence: result.diagnosis.confidence
        } : { status: result.status },
        location: { region: "Unknown Region" }, // Would be dynamic in a full app
        weather_current: { status: "UNAVAILABLE" },
        weather_forecast: { status: "UNAVAILABLE" },
        satellite: { status: "UNAVAILABLE" }
      };

      const { success, data, error, errorType } = await safeFetchJson('/api/disease-advisory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: signal
      }, t('AI disease advisory is temporarily unavailable.'));
      
      if (!success) {
        if (errorType === 'ABORT_ERROR') return;
        if (errorType === 'AI_UNAVAILABLE' || errorType === 'RESOURCE_EXHAUSTED' || error === 'AI advisory is temporarily unavailable.') {
          throw new Error(t('AI disease advisory is temporarily unavailable.'));
        }
        throw new Error(error);
      }
      setAiAdvisory(data.advisory);
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        setAiAdvisoryError((e as Error).message);
      }
    } finally {
      if (!signal?.aborted) {
        setAiAdvisoryLoading(false);
      }
      // Only scroll if we successfully fetched (user clicked it initially, or if they changed language and we successfully updated)
      if (!signal?.aborted && !signal) {
        setTimeout(() => {
          document.getElementById('advisory-result')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
      }
    }
  };

  return (
    <>
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto px-4 sm:px-6 py-24 min-h-screen"
      >
      <header className="mb-12 text-center">
        <h1 className="font-headline font-black text-3xl sm:text-5xl md:text-6xl tracking-tighter mb-4 text-primary">
          {t('AI-Assisted Disease Screening')}
        </h1>
        <p className="font-body text-on-surface-variant max-w-xl mx-auto text-base md:text-lg leading-relaxed">
          {t('Upload a clear photo of a crop leaf to screen for common diseases.')}
        </p>
      </header>

      {/* Crop Selection Section */}
      <section className="mb-10">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-sm">1</div>
          <h2 className="font-headline font-bold text-xl text-on-surface">{t('Select Crop')}</h2>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {SUPPORTED_CROPS.map((crop) => (
            <button
              key={crop.id}
              onClick={() => handleCropSelect(crop.id)}
              className={`p-4 rounded-2xl flex flex-col items-center justify-center gap-3 transition-all active:scale-95 border-2 ${
                selectedCrop === crop.id
                  ? 'bg-primary/10 border-primary text-primary shadow-sm'
                  : 'bg-surface-container-low border-transparent text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
              }`}
            >
              <SproutIcon className={`w-8 h-8 ${selectedCrop === crop.id ? 'text-primary' : 'text-on-surface-variant'}`} />
              <span className="font-headline font-bold">{t(crop.label)}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Image Upload Section */}
      <AnimatePresence>
        {selectedCrop && (
          <motion.section 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-10"
          >
            <div className="flex items-center gap-4 mb-6 mt-12">
              <div className="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-sm">2</div>
              <h2 className="font-headline font-bold text-xl text-on-surface">{t('Upload a leaf image')}</h2>
            </div>

            <div 
              className={`relative border-2 border-dashed rounded-3xl p-6 md:p-12 transition-all text-center flex flex-col items-center justify-center min-h-[300px]
                ${previewUrl ? 'border-primary/30 bg-surface-container-lowest' : 'border-outline-variant hover:border-primary/50 bg-surface-container-low hover:bg-surface-container'}`}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                id="disease-image-upload"
              />
              <input
                type="file"
                ref={cameraInputRef}
                onChange={handleFileChange}
                accept="image/*"
                capture="environment"
                className="hidden"
                id="disease-image-upload-camera"
              />
              <input
                type="file"
                ref={galleryInputRef}
                onChange={handleFileChange}
                accept="image/*"
                className="hidden"
                id="disease-image-upload-gallery"
              />

              {!previewUrl ? (
                <>
                  <div className="bg-surface-container-highest p-4 rounded-full mb-6">
                    <UploadCloud className="w-10 h-10 text-primary" />
                  </div>
                  <h3 className="font-headline font-bold text-lg mb-2 text-on-surface">
                    {t('Drag & drop image here or click to browse')}
                  </h3>
                  <p className="text-sm font-bold text-on-surface-variant uppercase tracking-wider mb-8">
                    {t('JPG, PNG or WebP • Maximum 5 MB')}
                  </p>
                  
                  <div className="flex flex-col sm:flex-row gap-4">
                    <button
                      type="button"
                      onClick={handleUploadClick}
                      className="bg-primary text-on-primary px-8 py-3 rounded-full font-bold shadow-lg shadow-primary/20 hover:opacity-90 transition-opacity active:scale-95"
                    >
                      {t('Upload a leaf image')}
                    </button>
                  </div>
                </>
              ) : (
                <div className="w-full flex flex-col items-center">
                  <div className="relative rounded-2xl overflow-hidden shadow-lg border border-outline-variant/20 mb-6 max-w-sm w-full">
                    <img src={previewUrl} alt="Leaf preview" className="w-full h-auto object-cover max-h-[400px]" />
                    <button
                      onClick={handleRemoveImage}
                      className="absolute top-3 right-3 bg-black/60 hover:bg-black/80 text-white p-2 rounded-full backdrop-blur-md transition-all active:scale-90"
                      aria-label={t('Remove image')}
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-on-surface-variant bg-surface-container-high px-4 py-2 rounded-full">
                    <ImageIcon className="w-4 h-4" />
                    <span className="font-medium truncate max-w-[200px]">{selectedFile?.name}</span>
                    <span>•</span>
                    <span>{(selectedFile!.size / (1024 * 1024)).toFixed(2)} MB</span>
                  </div>
                </div>
              )}
            </div>

            {validationError && (
              <div className="mt-4 p-4 bg-red-500/10 text-red-600 dark:text-red-400 rounded-xl font-medium text-sm flex items-center gap-2">
                <X className="w-5 h-5" />
                {validationError}
              </div>
            )}

            <div className="mt-4 text-center">
              <p className="text-xs text-on-surface-variant flex items-center justify-center gap-1.5 opacity-80">
                <span className="w-2 h-2 rounded-full bg-primary/40 inline-block"></span>
                {t('Your image is analyzed for this screening request and is not stored by KrushiSense.')}
              </p>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Analysis Button */}
      <AnimatePresence>
        {selectedCrop && selectedFile && !result && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex justify-center mt-12 mb-16"
          >
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="bg-primary text-on-primary px-12 py-5 rounded-full font-headline font-extrabold text-lg tracking-tight uppercase transition-all active:scale-95 shadow-xl shadow-primary/30 flex items-center gap-3 disabled:opacity-70 w-full sm:w-auto justify-center"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  {t('Analyzing...')}
                </>
              ) : (
                <>
                  {t('Analyze Crop')}
                  <ChevronRight className="w-6 h-6" />
                </>
              )}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Result Section */}
      <AnimatePresence>
        {result && (
          <motion.section 
            id="analysis-result"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-12 mb-20"
          >
            <div className="flex items-center gap-4 mb-8">
              <div className="h-px flex-grow bg-surface-container-highest"></div>
              <h2 className="font-headline font-black text-xl tracking-wider uppercase text-center text-on-surface-variant">
                {t('Screening Result')}
              </h2>
              <div className="h-px flex-grow bg-surface-container-highest"></div>
            </div>

            <DiseaseResultCard 
              result={result} 
              onRetry={handleRemoveImage} 
            />

            {/* AI Advisory Section */}
            <div className="mt-8 flex flex-col items-center gap-6">
              {!aiAdvisory && (result.status === 'DISEASE_DETECTED' || result.status === 'HEALTHY') && (
                <button
                  onClick={() => handleGetAdvisory()}
                  disabled={aiAdvisoryLoading}
                  className="bg-primary text-on-primary px-8 py-4 rounded-full font-headline font-extrabold tracking-tight transition-all active:scale-95 shadow-xl shadow-primary/20 flex items-center gap-3 disabled:opacity-70"
                >
                  {aiAdvisoryLoading ? (
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      {aiAdvisory ? t("Updating advice...") : t("Generating Advisory...")}
                    </div>
                  ) : (
                    <>
                      <SproutIcon className="w-5 h-5" />
                      {result.status === 'HEALTHY' ? t('Get AI Crop Health Advice') : t('Get AI Disease Advisory')}
                    </>
                  )}
                </button>
              )}

              {result.status === 'LOW_CONFIDENCE' && (
                <p className="text-on-surface-variant font-medium text-center text-sm max-w-md px-4">
                  {t('AI advisory is unavailable because the disease screening result is uncertain.')}
                </p>
              )}

              {aiAdvisoryError && (
                <div className="p-4 bg-error/10 text-error rounded-xl font-medium text-sm flex items-center gap-2 max-w-md w-full justify-center text-center">
                  <X className="w-5 h-5 shrink-0" />
                  {aiAdvisoryError}
                </div>
              )}
            </div>

            {aiAdvisory && (
              <div id="advisory-result">
                <DiseaseAdvisoryCard advisory={aiAdvisory} />
              </div>
            )}
            
            <div className="mt-12 flex justify-center border-t border-surface-container-highest pt-8">
              <button
                onClick={handleRemoveImage}
                className="text-primary font-bold hover:underline py-2 px-4 rounded-lg hover:bg-primary/5 transition-colors"
              >
                {t('Screen another leaf')}
              </button>
            </div>
          </motion.section>
        )}
      </AnimatePresence>
    </motion.div>
      <AnimatePresence>
        {showMobileUploadMenu && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[5000] flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-4"
            onClick={() => setShowMobileUploadMenu(false)}
          >
            <motion.div 
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={e => e.stopPropagation()}
              className="w-full max-w-sm bg-surface-container-lowest rounded-t-3xl sm:rounded-3xl overflow-hidden shadow-2xl flex flex-col"
            >
              <div className="p-6 text-center border-b border-outline-variant/20">
                <h3 className="font-headline font-bold text-xl text-on-surface">
                  {t('Add Crop Image')}
                </h3>
              </div>
              
              <div className="flex flex-col p-4 gap-3">
                <button
                  onClick={() => {
                    setShowMobileUploadMenu(false);
                    cameraInputRef.current?.click();
                  }}
                  className="flex items-center justify-center gap-3 w-full bg-primary text-on-primary py-4 rounded-2xl font-bold font-headline shadow-md active:scale-95 transition-transform"
                >
                  <Camera className="w-5 h-5" />
                  {t('Take Photo')}
                </button>
                
                <button
                  onClick={() => {
                    setShowMobileUploadMenu(false);
                    galleryInputRef.current?.click();
                  }}
                  className="flex items-center justify-center gap-3 w-full bg-surface-container text-on-surface py-4 rounded-2xl font-bold font-headline border border-outline-variant/30 active:scale-95 transition-transform"
                >
                  <ImageIcon className="w-5 h-5" />
                  {t('Choose from Gallery')}
                </button>
              </div>
              
              <div className="p-4 pt-0">
                <button
                  onClick={() => setShowMobileUploadMenu(false)}
                  className="w-full py-4 text-on-surface-variant font-bold font-headline active:opacity-70 transition-opacity"
                >
                  {t('Cancel')}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

// Simple sprout icon for the crop selection buttons
function SproutIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M7 20h10" />
      <path d="M10 20c5.5-2.5.8-6.4 3-10" />
      <path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z" />
      <path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z" />
    </svg>
  );
}
