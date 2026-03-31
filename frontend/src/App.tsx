import { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Navbar, Footer } from './components/Layout';
import { Home } from './components/Home';
import { PredictCrop } from './components/PredictCrop';
import { HowItWorks } from './components/HowItWorks';
import { CropDetailsPage } from './components/CropDetailsPage';
import { AnimatePresence } from 'motion/react';
import { LanguageProvider } from './contexts/LanguageContext';
import { NearbyKendras } from './components/NearbyKendras';

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
    return 'home';
  };

  const currentPage = pathToPage(location.pathname);

  const setCurrentPage = (page: string) => {
    if (page === 'home') navigate('/');
    else if (page === 'predict') navigate('/predict');
    else if (page === 'how-it-works') navigate('/how-it-works');
    else if (page === 'nearby-kendras') navigate('/nearby-kendras');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="flex-grow">
        <AnimatePresence mode="wait">
          <Routes location={location}>
            <Route path="/" element={<Home onStart={() => setCurrentPage('predict')} />} />
            <Route path="/predict" element={<PredictCrop />} />
            <Route path="/how-it-works" element={<HowItWorks />} />
            <Route path="/nearby-kendras" element={<NearbyKendras />} />
          </Routes>
        </AnimatePresence>
      </main>
      <Footer />
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
