import React, { useState } from 'react';
import { Globe, ChevronDown } from 'lucide-react';
import { useTranslation, Language } from '../contexts/LanguageContext';

interface NavbarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPage, setCurrentPage }) => {
  const { language, setLanguage, t } = useTranslation();
  const [showLangMenu, setShowLangMenu] = useState(false);

  const languages: { code: Language; name: string }[] = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi (हिंदी)' },
    { code: 'mr', name: 'Marathi (मराठी)' },
  ];

  return (
    <nav className="bg-background/80 backdrop-blur-md sticky top-0 z-50 transition-all duration-200">
      <div className="flex justify-between items-center w-full px-8 py-4 max-w-7xl mx-auto">
        <div 
          className="text-2xl font-black text-black tracking-tighter cursor-pointer font-headline"
          onClick={() => setCurrentPage('home')}
        >
          KrushiSense
        </div>
        <div className="hidden md:flex items-center space-x-8">
          <button 
            className={`font-headline font-bold text-lg uppercase tracking-tight transition-colors duration-200 ${
              currentPage === 'home' ? 'text-black border-b-2 border-black pb-1' : 'text-neutral-500 hover:text-black'
            }`}
            onClick={() => setCurrentPage('home')}
          >
            {t('Home')}
          </button>
          <button 
            className={`font-headline font-bold text-lg uppercase tracking-tight transition-colors duration-200 ${
              currentPage === 'predict' ? 'text-black border-b-2 border-black pb-1' : 'text-neutral-500 hover:text-black'
            }`}
            onClick={() => setCurrentPage('predict')}
          >
            {t('Predict Crop')}
          </button>
          <button 
            className={`font-headline font-bold text-lg uppercase tracking-tight transition-colors duration-200 ${
              currentPage === 'how-it-works' ? 'text-black border-b-2 border-black pb-1' : 'text-neutral-500 hover:text-black'
            }`}
            onClick={() => setCurrentPage('how-it-works')}
          >
            {t('How It Works')}
          </button>
        </div>
        
        <div className="relative">
          <div 
            className="flex items-center gap-2 text-black font-headline font-bold text-lg uppercase tracking-tight cursor-pointer active:scale-95 duration-150"
            onClick={() => setShowLangMenu(!showLangMenu)}
          >
            <Globe className="w-5 h-5" />
            <span>{languages.find(l => l.code === language)?.name.split(' ')[0]}</span>
            <ChevronDown className={`w-4 h-4 transition-transform ${showLangMenu ? 'rotate-180' : ''}`} />
          </div>

          {showLangMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white border border-neutral-200 rounded-lg shadow-xl overflow-hidden z-[60]">
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
    </nav>
  );
};

export const Footer: React.FC = () => {
  const { t } = useTranslation();
  return (
    <footer className="bg-surface-container-low w-full py-12 px-8 mt-20">
      <div className="flex flex-col md:flex-row justify-between items-center max-w-7xl mx-auto gap-8">
        <div className="text-center md:text-left">
          <div className="font-headline font-bold text-black text-xl">KrushiSense</div>
          <p className="font-body text-sm text-neutral-600 mt-2">
            © 2024 KrushiSense. {t('The Digital Curator for Agriculture.')}
          </p>
        </div>
        <div className="flex gap-8">
          <a className="text-neutral-500 hover:text-black transition-opacity text-sm" href="#">{t('Privacy Policy')}</a>
          <a className="text-neutral-500 hover:text-black transition-opacity text-sm" href="#">{t('Terms of Service')}</a>
          <a className="text-neutral-500 hover:text-black transition-opacity text-sm" href="#">{t('Contact Support')}</a>
        </div>
      </div>
    </footer>
  );
};
