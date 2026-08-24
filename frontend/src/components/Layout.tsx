import React, { useState, useEffect } from 'react';
import { Globe, ChevronDown, Sun, Moon, Menu, X } from 'lucide-react';
import { useTranslation, Language } from '../contexts/LanguageContext';
import { useTheme } from '../contexts/ThemeContext';

interface NavbarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
}

import GooeyNav from './ui/GooeyNav';
import StaggeredMenu from './StaggeredMenu';

export const Navbar: React.FC<NavbarProps> = ({ currentPage, setCurrentPage }) => {
  const { language, setLanguage, t, loading } = useTranslation();
  const { theme, toggleTheme } = useTheme();
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    // Initialize
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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

  const isHome = currentPage === 'home';
  // On home page, use white text only if we haven't scrolled. Otherwise, use theme text.
  const isTransparent = isHome && !isScrolled;
  
  const textColor = isTransparent ? 'text-white drop-shadow-md' : 'text-on-surface';
  const textVariantColor = isTransparent ? 'text-white/80 hover:text-white drop-shadow-md' : 'text-on-surface-variant hover:text-on-surface';

  const navPages = ['home', 'predict', 'disease-detection', 'how-it-works', 'nearby-kendras'];
  const gooeyItems = navPages.map(page => ({
    id: page,
    label: t(page === 'home' ? 'Home' : page === 'predict' ? 'Predict Crop' : page === 'disease-detection' ? 'Disease Detection' : page === 'how-it-works' ? 'How It Works' : 'Nearby Kendras'),
    href: page === 'home' ? '/' : `/${page}`
  }));
  const activeGooeyIndex = navPages.indexOf(currentPage) !== -1 ? navPages.indexOf(currentPage) : 0;
  
  // Use hex colors matching the theme or white for the home page when at top
  const gooeyTextColor = isTransparent ? 'white' : (theme === 'dark' ? '#e2e2e9' : '#1a1c1e');
  
  const staggeredMenuColors = theme === 'dark' ? ['#1a1c1e', '#2f3136'] : ['#f0f2f5', '#e1e3e8'];
  const staggeredMenuBtnColor = isTransparent ? '#ffffff' : (theme === 'dark' ? '#ffffff' : '#000000');
  
  const staggeredMenuItems = navPages.map(page => ({
    label: t(page === 'home' ? 'Home' : page === 'predict' ? 'Predict Crop' : page === 'disease-detection' ? 'Disease Detection' : page === 'how-it-works' ? 'How It Works' : 'Nearby Kendras'),
    ariaLabel: `Navigate to ${page}`,
    link: '#',
    onClick: () => handlePageChange(page)
  }));

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-[1000] transition-all duration-300 ${
        isTransparent 
          ? 'bg-transparent border-transparent py-4' 
          : 'bg-background/90 backdrop-blur-md border-b border-on-surface/5 py-2 shadow-sm'
      }`}>
        <div className="flex justify-between items-center w-full px-4 md:px-8 max-w-7xl mx-auto">
          <div 
            className={`text-xl md:text-2xl font-black tracking-tighter cursor-pointer font-headline shrink-0 ${textColor}`}
            onClick={() => handlePageChange('home')}
          >
            KrushiSense
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-2">
            <GooeyNav 
              items={gooeyItems}
              initialActiveIndex={activeGooeyIndex}
              onSelect={handlePageChange}
              textColor={gooeyTextColor}
              activeTextColor="#1a1c1e" // Black/dark text when pill is active
            />
          </div>
          
          <div className="hidden lg:flex items-center gap-3 md:gap-6">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-full transition-colors ${textVariantColor} ${isTransparent ? 'hover:bg-white/20' : 'hover:bg-surface-container-high'}`}
              aria-label="Toggle theme"
            >
              {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
            </button>

            {/* Language Selector (Now visible on mobile too, but compact) */}
            <div className="relative">
              <div 
                className={`flex items-center gap-1 md:gap-2 font-headline font-bold text-base md:text-lg uppercase tracking-tight cursor-pointer active:scale-95 duration-150 ${textColor}`}
                onClick={() => setShowLangMenu(!showLangMenu)}
              >
                <Globe className="w-5 h-5" />
                <span className="hidden sm:inline">{languages.find(l => l.code === language)?.name.split(' ')[0]}</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${showLangMenu ? 'rotate-180' : ''}`} />
              </div>

              {showLangMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-xl overflow-hidden z-[110]">
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

            {/* Mobile Menu Toggle is now handled by StaggeredMenu */}
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[1010] lg:hidden transition-opacity duration-300"
          aria-hidden="true"
        />
      )}
      
      <div className="lg:hidden">
        <StaggeredMenu 
          isFixed={true}
          position="right"
          colors={staggeredMenuColors}
          items={staggeredMenuItems}
          displaySocials={false}
          logoUrl="" // Do not show ReactBits logo
          menuButtonColor={staggeredMenuBtnColor}
          openMenuButtonColor="#000000" // Always dark because menu panel is white
          accentColor="#006b5f" // KrushiSense primary color
          onMenuOpen={() => setIsMobileMenuOpen(true)}
          onMenuClose={() => setIsMobileMenuOpen(false)}
        >
          {/* Mobile Theme and Language Controls */}
          <div className="flex flex-col gap-4 mt-2">
            <div className="flex items-center justify-between">
              <span className="font-headline font-bold text-on-surface uppercase tracking-tight text-lg">Theme</span>
              <button
                onClick={toggleTheme}
                className={`p-3 rounded-full transition-colors bg-surface-container-low hover:bg-surface-container-high text-on-surface`}
                aria-label="Toggle theme"
              >
                {theme === 'light' ? <Moon className="w-6 h-6" /> : <Sun className="w-6 h-6" />}
              </button>
            </div>
            
            <div className="flex flex-col gap-2">
              <span className="font-headline font-bold text-on-surface uppercase tracking-tight text-lg">Language</span>
              <div className="flex flex-col gap-2 bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    className={`w-full text-left px-4 py-3 font-headline font-bold text-base transition-colors ${
                      language === lang.code ? 'bg-primary text-on-primary' : 'hover:bg-surface-container-low text-on-surface'
                    } ${loading ? 'opacity-60 cursor-not-allowed' : ''}`}
                    onClick={() => {
                      if (!loading) {
                        setLanguage(lang.code);
                      }
                    }}
                    disabled={loading}
                  >
                    {lang.name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </StaggeredMenu>
      </div>
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
