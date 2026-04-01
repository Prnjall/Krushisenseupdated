import React, { useEffect } from 'react';
import { motion } from 'motion/react';
import { ShieldCheck, Lock, Eye, Users, FileText, Calendar } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';

export const PrivacyPolicy: React.FC = () => {
  const { t, translateBatch, language } = useTranslation();

  const content = [
    "Privacy Policy",
    "Last updated: January 2025",
    "KrushiSense is committed to protecting your privacy. This policy explains what data we collect, how we use it, and what we never do with it.",
    "1. What Data We Collect",
    "KrushiSense collects only the minimum data needed to provide crop recommendations. This includes:",
    "Soil input values — Nitrogen (N), Phosphorus (P), Potassium (K), pH, temperature, humidity, and rainfall values that you enter manually into the prediction form.",
    "Location data — Only when you click \"Find Nearest KVK\". Your GPS coordinates are used in that moment to calculate distances. They are not stored, saved, or transmitted to any server.",
    "No account data — KrushiSense does not require you to create an account. We do not collect your name, email, phone number, or any personal identifying information.",
    "2. How We Use Your Data",
    "Soil input values are sent to our AI model to generate crop recommendations. These values are processed in real time and are not stored after the session ends.",
    "Location data is used only on your device to calculate the distance between you and nearby Krishi Vigyan Kendras. It is never sent to our servers.",
    "We do not use your data for advertising, profiling, or any commercial purpose.",
    "3. What We Never Do",
    "We never sell your data to any third party.",
    "We never share your data with advertisers.",
    "We never store your location after you close the page.",
    "We never track your activity across other websites.",
    "4. Third-Party Services",
    "KrushiSense uses the following third-party services to function:",
    "Anthropic Claude API — Used to power the crop prediction feature. Soil input values are sent to Anthropic's servers for processing. Anthropic's privacy policy applies to this data.",
    "CARTO / MapLibre (via mapcn) — Used to display the Krishi Kendra map. Map tile requests are made to CARTO's servers. No personal data is included in these requests.",
    "Google Maps — When you click \"Directions\" on a KVK, you are redirected to Google Maps. Google's privacy policy applies from that point.",
    "5. Cookies",
    "KrushiSense does not use tracking cookies. We may use minimal session storage to remember your language preference (English / मराठी / हिंदी) during your visit. This is cleared when you close your browser.",
    "6. Children's Privacy",
    "KrushiSense is intended for farmers and agricultural professionals. We do not knowingly collect data from children under 13 years of age.",
    "7. Changes to This Policy",
    "We may update this Privacy Policy as the app grows. Any significant changes will be noted at the top of this page with a new \"Last updated\" date. Continued use of KrushiSense after changes means you accept the updated policy.",
    "8. Contact",
    "If you have any questions about this Privacy Policy, please reach out via our Contact Support page."
  ];

  useEffect(() => {
    translateBatch(content);
  }, [language]);

  return (
    <div className="max-w-4xl mx-auto px-6 py-20 md:py-32">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-16"
      >
        {/* Header */}
        <header className="border-b border-on-surface/10 pb-12">
          <div className="flex items-center gap-3 text-primary font-headline font-black uppercase tracking-widest text-xs mb-6">
            <ShieldCheck className="size-5" />
            <span>{t("Legal & Security")}</span>
          </div>
          <h1 className="font-headline font-black text-5xl md:text-7xl tracking-tighter text-on-surface mb-8">
            {t("Privacy Policy")}
          </h1>
          <div className="flex items-center gap-2 text-on-surface-variant font-body text-sm bg-surface-container-low w-fit px-4 py-2 rounded-full border border-on-surface/5">
            <Calendar className="size-4" />
            <span>{t("Last updated: January 2025")}</span>
          </div>
        </header>

        {/* Intro */}
        <section className="bg-primary/5 p-8 md:p-12 rounded-[2.5rem] border border-primary/10">
          <p className="font-body text-on-surface text-lg md:text-xl leading-relaxed italic">
            "{t("KrushiSense is committed to protecting your privacy. This policy explains what data we collect, how we use it, and what we never do with it.")}"
          </p>
        </section>

        {/* Content Sections */}
        <div className="space-y-12">
          {[
            { id: 1, title: "1. What Data We Collect", icon: <Eye className="size-6" /> },
            { id: 2, title: "2. How We Use Your Data", icon: <Users className="size-6" /> },
            { id: 3, title: "3. What We Never Do", icon: <Lock className="size-6" /> },
            { id: 4, title: "4. Third-Party Services", icon: <FileText className="size-6" /> },
            { id: 5, title: "5. Cookies", icon: <ShieldCheck className="size-6" /> },
            { id: 6, title: "6. Children's Privacy", icon: <Users className="size-6" /> },
            { id: 7, title: "7. Changes to This Policy", icon: <ShieldCheck className="size-6" /> },
            { id: 8, title: "8. Contact", icon: <ShieldCheck className="size-6" /> }
          ].map((section, idx) => (
            <div key={idx} className="group">
              <h2 className="font-headline font-black text-2xl md:text-3xl text-on-surface mb-6 flex items-center gap-4">
                <span className="text-primary/20 group-hover:text-primary transition-colors">{section.icon}</span>
                {t(section.title)}
              </h2>
              <div className="space-y-4 pl-10">
                {idx === 0 && (
                  <>
                    <p className="font-body text-on-surface-variant leading-relaxed text-lg">
                      {t("KrushiSense collects only the minimum data needed to provide crop recommendations. This includes:")}
                    </p>
                    <ul className="space-y-6 mt-4">
                      {[
                        "Soil input values — Nitrogen (N), Phosphorus (P), Potassium (K), pH, temperature, humidity, and rainfall values that you enter manually into the prediction form.",
                        "Location data — Only when you click \"Find Nearest KVK\". Your GPS coordinates are used in that moment to calculate distances. They are not stored, saved, or transmitted to any server.",
                        "No account data — KrushiSense does not require you to create an account. We do not collect your name, email, phone number, or any personal identifying information."
                      ].map((item, i) => (
                        <li key={i} className="flex gap-4 p-5 rounded-2xl bg-surface-container-low/50 border border-on-surface/5">
                          <div className="size-2 rounded-full bg-primary mt-2.5 shrink-0" />
                          <span className="font-body text-on-surface-variant text-base md:text-lg">{t(item)}</span>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
                {idx === 1 && (
                  <ul className="space-y-4">
                    {[
                      "Soil input values are sent to our AI model to generate crop recommendations. These values are processed in real time and are not stored after the session ends.",
                      "Location data is used only on your device to calculate the distance between you and nearby Krishi Vigyan Kendras. It is never sent to our servers.",
                      "We do not use your data for advertising, profiling, or any commercial purpose."
                    ].map((item, i) => (
                      <p key={i} className="font-body text-on-surface-variant leading-relaxed text-lg">{t(item)}</p>
                    ))}
                  </ul>
                )}
                {idx === 2 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      "We never sell your data to any third party.",
                      "We never share your data with advertisers.",
                      "We never store your location after you close the page.",
                      "We never track your activity across other websites."
                    ].map((item, i) => (
                      <div key={i} className="p-4 rounded-xl bg-red-500/5 text-red-600 dark:text-red-400 font-headline font-bold text-sm border border-red-500/10 flex items-center gap-3">
                        <div className="size-1.5 rounded-full bg-current" />
                        {t(item)}
                      </div>
                    ))}
                  </div>
                )}
                {idx === 3 && (
                   <ul className="space-y-6">
                   {[
                     "Anthropic Claude API — Used to power the crop prediction feature. Soil input values are sent to Anthropic's servers for processing. Anthropic's privacy policy applies to this data.",
                     "CARTO / MapLibre (via mapcn) — Used to display the Krishi Kendra map. Map tile requests are made to CARTO's servers. No personal data is included in these requests.",
                     "Google Maps — When you click \"Directions\" on a KVK, you are redirected to Google Maps. Google's privacy policy applies from that point."
                   ].map((item, i) => (
                     <li key={i} className="font-body text-on-surface-variant leading-relaxed text-lg border-l-2 border-primary/10 pl-6 py-2">{t(item)}</li>
                   ))}
                 </ul>
                )}
                {idx === 4 && <p className="font-body text-on-surface-variant leading-relaxed text-lg">{t("KrushiSense does not use tracking cookies. We may use minimal session storage to remember your language preference (English / मराठी / हिंदी) during your visit. This is cleared when you close your browser.")}</p>}
                {idx === 5 && <p className="font-body text-on-surface-variant leading-relaxed text-lg">{t("KrushiSense is intended for farmers and agricultural professionals. We do not knowingly collect data from children under 13 years of age.")}</p>}
                {idx === 6 && <p className="font-body text-on-surface-variant leading-relaxed text-lg">{t("We may update this Privacy Policy as the app grows. Any significant changes will be noted at the top of this page with a new \"Last updated\" date. Continued use of KrushiSense after changes means you accept the updated policy.")}</p>}
                {idx === 7 && (
                  <p className="font-body text-on-surface-variant leading-relaxed text-lg">
                    {t("If you have any questions about this Privacy Policy, please reach out via our Contact Support page.")}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};
