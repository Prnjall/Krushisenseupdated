import { useState } from 'react';
import { Navbar, Footer } from './components/Layout';
import { Home } from './components/Home';
import { PredictCrop } from './components/PredictCrop';
import { HowItWorks } from './components/HowItWorks';
import { AnimatePresence } from 'motion/react';
import { LanguageProvider } from './contexts/LanguageContext';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home onStart={() => setCurrentPage('predict')} />;
      case 'predict':
        return <PredictCrop />;
      case 'how-it-works':
        return <HowItWorks />;
      default:
        return <Home onStart={() => setCurrentPage('predict')} />;
    }
  };

  return (
    <LanguageProvider>
      <div className="min-h-screen flex flex-col">
        <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />
        <main className="flex-grow">
          <AnimatePresence mode="wait">
            {renderPage()}
          </AnimatePresence>
        </main>
        <Footer />
      </div>
    </LanguageProvider>
  );
}
