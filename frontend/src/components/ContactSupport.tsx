import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { 
  CheckCircle2, 
  Send, 
  Mail, 
  Github, 
  HelpCircle, 
  Bug, 
  MapPin, 
  MessageSquare,
  ArrowRight,
  Phone
} from 'lucide-react';
import { Button } from './ui/button';
import { useTranslation } from '../contexts/LanguageContext';

export const ContactSupport: React.FC = () => {
  const { t, translateBatch, language } = useTranslation();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Content for translation
  const stringsToTranslate = [
    "Contact Support",
    "Have a question, found a bug, or want to suggest a feature? We read every message and typically respond within 1–2 working days.",
    "Crop Prediction",
    "Questions about how predictions work",
    "KVK Locations",
    "Wrong address or missing Kendra",
    "Report a Bug",
    "Something not working as expected",
    "Your Name",
    "Email Address",
    "Category",
    "Select a category",
    "Message",
    "Describe your question or issue in detail...",
    "Send Message",
    "Submitting...",
    "Success!",
    "Thank you for reaching out. We will get back to you soon.",
    "We respond within 1–2 working days. For urgent issues related to KVK locations, you can directly call the KVK using numbers on the Agri Kendras page.",
    "Or reach us directly",
    "Open an issue on GitHub",
    "General Inquiry",
    "Bug Report",
    "Feature Request",
    "Missing KVK Data"
  ];

  useEffect(() => {
    translateBatch(stringsToTranslate);
  }, [language]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    
    try {
      const formspreeId = import.meta.env.VITE_FORMSPREE_ID;
      const response = await fetch(`https://formspree.io/f/${formspreeId}`, {
        method: "POST",
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      });

      if (response.ok) {
        setIsSubmitted(true);
      } else {
        const data = await response.json();
        setError(data.error || "Something went wrong. Please try again later.");
      }
    } catch (err) {
      setError("Network error. Please check your connection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center p-6">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-surface-container-lowest p-12 rounded-[2.5rem] border border-on-surface/5 shadow-2xl text-center max-w-md w-full"
        >
          <div className="bg-primary/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-8">
            <CheckCircle2 className="size-10 text-primary" />
          </div>
          <h2 className="font-headline font-black text-4xl tracking-tighter mb-4 text-on-surface">
            {t("Success!")}
          </h2>
          <p className="font-body text-on-surface-variant text-lg leading-relaxed mb-10">
            {t("Thank you for reaching out. We will get back to you soon.")}
          </p>
          <Button 
            onClick={() => setIsSubmitted(false)}
            className="w-full h-14 rounded-2xl bg-primary text-on-primary font-headline font-black uppercase tracking-widest text-sm"
          >
            {t("Send Another Message")}
          </Button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-16 md:py-24">
      <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_1fr] gap-16 lg:gap-24 items-start">
        
        {/* Left Column: Info & Content */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <header className="mb-12">
            <h2 className="font-headline font-black text-primary uppercase tracking-[0.2em] text-sm mb-4">
              {t("Support")}
            </h2>
            <h1 className="font-headline font-black text-5xl md:text-7xl tracking-tighter text-on-surface mb-8">
              {t("Contact Support")}
            </h1>
            <p className="font-body text-on-surface-variant text-lg md:text-xl leading-relaxed">
              {t("Have a question, found a bug, or want to suggest a feature? We read every message and typically respond within 1–2 working days.")}
            </p>
          </header>

          <div className="grid grid-cols-1 gap-6 mb-12">
            {[
              { icon: <HelpCircle className="size-6" />, title: "Crop Prediction", desc: "Questions about how predictions work", color: "bg-blue-500/10 text-blue-500" },
              { icon: <MapPin className="size-6" />, title: "KVK Locations", desc: "Wrong address or missing Kendra", color: "bg-green-500/10 text-green-500" },
              { icon: <Bug className="size-6" />, title: "Report a Bug", desc: "Something not working as expected", color: "bg-red-500/10 text-red-500" }
            ].map((item, idx) => (
              <div key={idx} className="flex gap-5 p-6 rounded-3xl bg-surface-container-low border border-on-surface/5 hover:border-primary/20 transition-all group">
                <div className={`${item.color} p-4 rounded-2xl`}>
                  {item.icon}
                </div>
                <div>
                  <h3 className="font-headline font-bold text-lg text-on-surface group-hover:text-primary transition-colors">
                    {t(item.title)}
                  </h3>
                  <p className="font-body text-on-surface-variant text-sm mt-1">
                    {t(item.desc)}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-8 border-t border-on-surface/10">
            <h3 className="font-headline font-bold text-on-surface mb-6 uppercase tracking-widest text-xs">
              {t("Or reach us directly")}
            </h3>
            <div className="space-y-4">
              <a href="mailto:krushisense@gmail.com" className="flex items-center gap-4 text-on-surface-variant hover:text-primary transition-colors group">
                <div className="bg-surface-container-high p-3 rounded-xl group-hover:bg-primary/10 transition-colors">
                  <Mail className="size-5" />
                </div>
                <span className="font-headline font-bold tracking-tight">krushisense@gmail.com</span>
              </a>
              <a href="https://github.com/Prnjall" target="_blank" rel="noreferrer" className="flex items-center gap-4 text-on-surface-variant hover:text-primary transition-colors group">
                <div className="bg-surface-container-high p-3 rounded-xl group-hover:bg-primary/10 transition-colors">
                  <Github className="size-5" />
                </div>
                <span className="font-headline font-bold tracking-tight">{t("Open an issue on GitHub")}</span>
              </a>
            </div>
          </div>
        </motion.div>

        {/* Right Column: Form */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-surface-container-lowest p-8 md:p-12 rounded-[2.5rem] border border-on-surface/5 shadow-2xl sticky top-32"
        >
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="space-y-2">
              <label htmlFor="full-name" className="font-headline font-black uppercase tracking-widest text-[10px] text-on-surface-variant ml-1">
                {t("Your Name")}
              </label>
              <input 
                required
                id="full-name"
                name="name"
                type="text"
                placeholder="Ramesh Patil"
                className="w-full h-14 bg-surface-container-low border border-on-surface/5 rounded-2xl px-6 font-body text-on-surface placeholder:text-on-surface-variant/30 focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="font-headline font-black uppercase tracking-widest text-[10px] text-on-surface-variant ml-1">
                {t("Email Address")}
              </label>
              <input 
                required
                id="email"
                name="email"
                type="email"
                placeholder="ramesh@example.com"
                className="w-full h-14 bg-surface-container-low border border-on-surface/5 rounded-2xl px-6 font-body text-on-surface placeholder:text-on-surface-variant/30 focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="category" className="font-headline font-black uppercase tracking-widest text-[10px] text-on-surface-variant ml-1">
                {t("Category")}
              </label>
              <select 
                required
                id="category"
                name="category"
                className="w-full h-14 bg-surface-container-low border border-on-surface/5 rounded-2xl px-6 font-body text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all appearance-none cursor-pointer"
              >
                <option value="" disabled selected>{t("Select a category")}</option>
                <option value="General Inquiry">{t("General Inquiry")}</option>
                <option value="Bug Report">{t("Bug Report")}</option>
                <option value="Feature Request">{t("Feature Request")}</option>
                <option value="Missing KVK Data">{t("Missing KVK Data")}</option>
              </select>
            </div>

            <div className="space-y-2">
              <label htmlFor="message" className="font-headline font-black uppercase tracking-widest text-[10px] text-on-surface-variant ml-1">
                {t("Message")}
              </label>
              <textarea 
                required
                id="message"
                name="message"
                rows={5}
                placeholder={t("Describe your question or issue in detail...")}
                className="w-full bg-surface-container-low border border-on-surface/5 rounded-3xl p-6 font-body text-on-surface placeholder:text-on-surface-variant/30 focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all resize-none"
              />
            </div>

            {error && (
              <div className="bg-red-500/10 text-red-500 p-4 rounded-xl text-sm font-bold flex gap-3 items-center border border-red-500/20">
                <Bug className="size-4 shrink-0" />
                {error}
              </div>
            )}

            <Button 
              type="submit" 
              disabled={isSubmitting}
              className="w-full h-16 rounded-2xl bg-primary text-on-primary font-headline font-black uppercase tracking-widest text-sm flex items-center justify-center gap-3 active:scale-[0.98] transition-transform disabled:opacity-50"
            >
              <Send className="size-5" />
              {isSubmitting ? t("Submitting...") : t("Send Message")}
            </Button>
            
            <p className="text-center text-[11px] font-body text-on-surface-variant leading-relaxed px-4">
              {t("We respond within 1–2 working days. For urgent issues related to KVK locations, you can directly call the KVK using numbers on the Agri Kendras page.")}
            </p>
          </form>
        </motion.div>

      </div>
    </div>
  );
};
