import React, { useState, useEffect } from 'react';
import { Globe, ChevronDown, Sun, Moon, Menu, X } from 'lucide-react';
import { useTranslation, Language } from '../contexts/LanguageContext';
import { useTheme } from '../contexts/ThemeContext';

interface NavbarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPage, setCurrentPage }) => {
  const { language, setLanguage, t, loading } = useTranslation();
  const { theme, toggleTheme } = useTheme();
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Close mobile menu on direct interaction with links
  const handlePageChange = (page: string) => {
    setCurrentPage(page);
    setIsMobileMenuOpen(false);
  };

  // Prevent scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = 'unset';
    return () => { document.body.style.overflow = 'unset'; };
  }, [isMobileMenuOpen]);

  const languages: { code: Language; name: string }[] = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi (हिंदी)' },
    { code: 'mr', name: 'Marathi (मराठी)' },
  ];

  return (
    <>
      <nav className="bg-background/80 backdrop-blur-md sticky top-0 z-1000 transition-all duration-200 border-b border-on-surface/5">
        <div className="flex justify-between items-center w-full px-4 md:px-8 py-4 max-w-7xl mx-auto">
          <div 
            className="text-xl md:text-2xl font-black text-on-surface tracking-tighter cursor-pointer font-headline shrink-0"
            onClick={() => handlePageChange('home')}
          >
            KrushiSense
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-8">
            {['home', 'predict', 'how-it-works', 'nearby-kendras'].map((page) => (
              <button 
                key={page}
                className={`font-headline font-bold text-lg uppercase tracking-tight transition-colors duration-200 whitespace-nowrap ${
                  currentPage === page ? 'text-on-surface border-b-2 border-on-surface pb-1' : 'text-on-surface-variant hover:text-on-surface'
                }`}
                onClick={() => handlePageChange(page)}
              >
                {t(page === 'home' ? 'Home' : page === 'predict' ? 'Predict Crop' : page === 'how-it-works' ? 'How It Works' : 'Nearby Kendras')}
              </button>
            ))}
          </div>
          
          <div className="flex items-center gap-3 md:gap-6">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-surface-container-high transition-colors text-on-surface-variant hover:text-on-surface"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
            </button>

            {/* Desktop Language Selector */}
            <div className="hidden md:block relative">
              <div 
                className="flex items-center gap-2 text-on-surface font-headline font-bold text-lg uppercase tracking-tight cursor-pointer active:scale-95 duration-150"
                onClick={() => setShowLangMenu(!showLangMenu)}
              >
                <Globe className="w-5 h-5" />
                <span>{languages.find(l => l.code === language)?.name.split(' ')[0]}</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${showLangMenu ? 'rotate-180' : ''}`} />
              </div>

              {showLangMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-xl overflow-hidden z-110">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      className={`w-full text-left px-4 py-3 font-headline font-bold text-sm transition-colors ${
                        language === lang.code ? 'bg-primary text-on-primary' : 'hover:bg-surface-container-low text-on-surface'
                      } ${loading ? 'opacity-60 cursor-not-allowed' : ''}`}
                      onClick={() => {
                        if (!loading) {
                          setLanguage(lang.code);
                          setShowLangMenu(false);
                        }
                      }}
                      disabled={loading}
                    >
                      {lang.name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Mobile Menu Toggle */}
            <button 
              className="lg:hidden p-2 text-on-surface-variant hover:text-on-surface transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay - Moved OUTSIDE the nav to ensure it covers the screen */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 top-15 bg-background z-2000 p-6 lg:hidden flex flex-col overflow-y-auto shadow-2xl">
          <div className="flex flex-col space-y-6 pt-4 mb-8">
            {['home', 'predict', 'how-it-works', 'nearby-kendras'].map((page) => (
              <button 
                key={page}
                className={`text-left font-headline font-black text-3xl uppercase tracking-tighter transition-colors active:scale-95 ${
                  currentPage === page ? 'text-primary' : 'text-on-surface'
                }`}
                onClick={() => handlePageChange(page)}
              >
                {t(page === 'home' ? 'Home' : page === 'predict' ? 'Predict Crop' : page === 'how-it-works' ? 'How It Works' : 'Nearby Kendras')}
              </button>
            ))}
          </div>

          <div className="mt-auto pt-8 border-t border-on-surface/10 pb-8">
            <h4 className="text-xs font-headline font-bold uppercase tracking-widest text-on-surface-variant mb-6">
              {t('Select Language')}
            </h4>
            <div className="grid grid-cols-1 gap-3">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  className={`w-full text-left p-5 rounded-2xl font-headline font-bold text-lg transition-all active:scale-95 ${
                    language === lang.code 
                      ? 'bg-primary text-on-primary shadow-lg shadow-primary/20' 
                      : 'bg-surface-container-low text-on-surface border border-on-surface/5'
                  }`}
                  onClick={() => {
                    setLanguage(lang.code);
                    setIsMobileMenuOpen(false);
                  }}
                >
                  {lang.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

import { useNavigate } from 'react-router-dom';

export const Footer: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  return (
    <footer className="bg-surface-container-low w-full py-12 px-8 mt-20 border-t border-on-surface/5">
      <div className="flex flex-col md:flex-row justify-between items-center max-w-7xl mx-auto gap-8">
        <div className="text-center md:text-left">
          <div className="font-headline font-bold text-on-surface text-xl">KrushiSense</div>
          <p className="font-body text-sm text-on-surface-variant mt-2">
            © 2024 KrushiSense. {t('The Digital Curator for Agriculture.')}
          </p>
        </div>
        <div className="flex gap-8">
          <button
            className="text-on-surface-variant hover:text-on-surface transition-colors text-sm bg-transparent border-none outline-none cursor-pointer"
            onClick={() => navigate('/privacy-policy')}
            type="button"
          >
            {t('Privacy Policy')}
          </button>
          <button
            className="text-on-surface-variant hover:text-on-surface transition-colors text-sm bg-transparent border-none outline-none cursor-pointer"
            onClick={() => navigate('/terms-of-service')}
            type="button"
          >
            {t('Terms of Service')}
          </button>
          <button
            className="text-on-surface-variant hover:text-on-surface transition-colors text-sm bg-transparent border-none outline-none cursor-pointer"
            onClick={() => navigate('/contact-support')}
            type="button"
          >
            {t('Contact Support')}
          </button>
        </div>
      </div>
    </footer>
  );
};
