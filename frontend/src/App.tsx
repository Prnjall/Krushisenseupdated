import { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Navbar, Footer } from './components/Layout';
import ScrollToTop from './components/ScrollToTop';
import { Home } from './components/Home';
import { PredictCrop } from './components/PredictCrop';
import { HowItWorks } from './components/HowItWorks';
import { CropDetailsPage } from './components/CropDetailsPage';
import { AnimatePresence } from 'motion/react';
import { LanguageProvider, useTranslation } from './contexts/LanguageContext';
import { NearbyKendras } from './components/NearbyKendras';

import { TermsOfService } from './components/TermsOfService';
import { PrivacyPolicy } from './components/PrivacyPolicy';
import { ContactSupport } from './components/ContactSupport';

// ── Pages that use the shared Navbar + Footer layout ────────────────────────
function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  // Derive currentPage from URL for Navbar active state
  const pathToPage = (path: string) => {
    if (path === '/' || path === '') return 'home';
    if (path.startsWith('/predict')) return 'predict';
    if (path.startsWith('/how-it-works')) return 'how-it-works';
    if (path.startsWith('/nearby-kendras')) return 'nearby-kendras';
    if (path.startsWith('/privacy-policy')) return 'privacy-policy';
    if (path.startsWith('/terms-of-service')) return 'terms-of-service';
    if (path.startsWith('/contact-support')) return 'contact-support';
    return 'home';
  };

  const currentPage = pathToPage(location.pathname);

  const setCurrentPage = (page: string) => {
    if (page === 'home') navigate('/');
    else if (page === 'predict') navigate('/predict');
    else if (page === 'how-it-works') navigate('/how-it-works');
    else if (page === 'nearby-kendras') navigate('/nearby-kendras');
    else if (page === 'privacy-policy') navigate('/privacy-policy');
    else if (page === 'terms-of-service') navigate('/terms-of-service');
    else if (page === 'contact-support') navigate('/contact-support');
  };

  const { loading } = useTranslation();
  return (
    <div className="min-h-screen flex flex-col relative">
      <ScrollToTop />
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="flex-grow">
        <AnimatePresence mode="wait">
          <Routes location={location}>
            <Route path="/" element={<Home onStart={() => setCurrentPage('predict')} />} />
            <Route path="/predict" element={<PredictCrop />} />
            <Route path="/how-it-works" element={<HowItWorks />} />
            <Route path="/nearby-kendras" element={<NearbyKendras />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/terms-of-service" element={<TermsOfService />} />
            <Route path="/contact-support" element={<ContactSupport />} />
          </Routes>
        </AnimatePresence>
      </main>
      <Footer />
      {loading && (
        <div className="fixed inset-0 z-[3000] flex items-center justify-center bg-black/20 backdrop-blur-sm">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}

// ── Root App — crop detail gets its own full-page layout ────────────────────
import { ThemeProvider } from './contexts/ThemeContext';

export default function App() {
  return (
    <LanguageProvider>
      <ThemeProvider>
        <Routes>
          {/* Crop detail: no shared footer/navbar, uses its own top bar */}
          <Route path="/crop/:cropName" element={<CropDetailsPage />} />
          {/* All other pages: shared Navbar + Footer */}
          <Route path="/*" element={<MainLayout />} />
        </Routes>
      </ThemeProvider>
    </LanguageProvider>
  );
}
