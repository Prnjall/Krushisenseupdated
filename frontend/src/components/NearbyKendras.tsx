import { motion } from "motion/react";
import { useState, useEffect } from "react";
import {
  Map,
  MapMarker,
  MarkerContent,
  MarkerLabel,
  MarkerPopup,
} from "@/src/components/ui/map";
import { Button } from "@/src/components/ui/button";
import { Navigation, ExternalLink, FlaskConical, Truck, Phone } from "lucide-react";
import { useTranslation } from "../contexts/LanguageContext";

// ── Complete Maharashtra KVK Dataset ─────────────────────────────────────────
const kvks = [
  // WESTERN MAHARASHTRA
  { id: 1,  name: "KVK Baramati",    district: "Pune",       region: "western",    phone: "02112-255207", lat: 18.1522, lng: 74.5815, mobileLab: true,  soilCost: "₹100–₹150", tests: "pH, N, P, K, OC, Micronutrients" },
  { id: 2,  name: "KVK Narayangaon", district: "Pune",       region: "western",    phone: "02132-242216", lat: 19.1007, lng: 73.9894, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 3,  name: "KVK Kolhapur",    district: "Kolhapur",   region: "western",    phone: "0231-2651420", lat: 16.7050, lng: 74.2433, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 4,  name: "KVK Satara",      district: "Satara",     region: "western",    phone: "02162-220013", lat: 17.6805, lng: 74.0183, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 5,  name: "KVK Sangli",      district: "Sangli",     region: "western",    phone: "0233-2226789", lat: 16.8524, lng: 74.5815, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 6,  name: "KVK Solapur",     district: "Solapur",    region: "western",    phone: "02189-233001", lat: 17.6599, lng: 75.9064, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },

  // NORTH MAHARASHTRA
  { id: 7,  name: "KVK Nashik",      district: "Nashik",     region: "north",      phone: "0253-2231473", lat: 20.0059, lng: 73.7897, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC, Micronutrients" },
  { id: 8,  name: "KVK Ahmednagar",  district: "Ahmednagar", region: "north",      phone: "02422-252414", lat: 19.6586, lng: 74.7239, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 9,  name: "KVK Dhule",       district: "Dhule",      region: "north",      phone: "02562-232095", lat: 20.9013, lng: 74.7749, mobileLab: false, soilCost: "₹100–₹150", tests: "pH, N, P, K, OC" },
  { id: 10, name: "KVK Jalgaon",     district: "Jalgaon",    region: "north",      phone: "0257-2226833", lat: 21.0077, lng: 75.5626, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 11, name: "KVK Nandurbar",   district: "Nandurbar",  region: "north",      phone: "02564-220012", lat: 21.3683, lng: 74.2437, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },

  // MARATHWADA
  { id: 12, name: "KVK Aurangabad",  district: "Aurangabad", region: "marathwada", phone: "0240-2376558", lat: 19.8762, lng: 75.3433, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC, Micronutrients" },
  { id: 13, name: "KVK Latur",       district: "Latur",      region: "marathwada", phone: "02382-257766", lat: 18.4088, lng: 76.5604, mobileLab: false, soilCost: "₹100–₹150", tests: "pH, N, P, K, OC" },
  { id: 14, name: "KVK Nanded",      district: "Nanded",     region: "marathwada", phone: "02465-227848", lat: 18.9068, lng: 77.2976, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 15, name: "KVK Osmanabad",   district: "Osmanabad",  region: "marathwada", phone: "02471-224011", lat: 18.1862, lng: 76.0404, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 16, name: "KVK Hingoli",     district: "Hingoli",    region: "marathwada", phone: "07246-222134", lat: 19.7176, lng: 77.1496, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 17, name: "KVK Beed",        district: "Beed",       region: "marathwada", phone: "02442-222011", lat: 18.9891, lng: 75.7601, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },

  // VIDARBHA
  { id: 18, name: "KVK Nagpur",      district: "Nagpur",     region: "vidarbha",   phone: "0712-2500477", lat: 21.1458, lng: 79.0882, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC, Micronutrients" },
  { id: 19, name: "KVK Amravati",    district: "Amravati",   region: "vidarbha",   phone: "0721-2580606", lat: 20.9374, lng: 77.7796, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 20, name: "KVK Washim",      district: "Washim",     region: "vidarbha",   phone: "07251-222462", lat: 20.1119, lng: 77.1332, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC, Micronutrients" },
  { id: 21, name: "KVK Yavatmal",    district: "Yavatmal",   region: "vidarbha",   phone: "07232-248235", lat: 20.3888, lng: 78.1204, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 22, name: "KVK Akola",       district: "Akola",      region: "vidarbha",   phone: "0724-2258271", lat: 20.7002, lng: 77.0082, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC, Micronutrients" },
  { id: 23, name: "KVK Buldhana",    district: "Buldhana",   region: "vidarbha",   phone: "07262-242011", lat: 20.5292, lng: 76.1842, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 24, name: "KVK Wardha",      district: "Wardha",     region: "vidarbha",   phone: "07152-240011", lat: 20.7453, lng: 78.6022, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 25, name: "KVK Chandrapur",  district: "Chandrapur", region: "vidarbha",   phone: "07176-222134", lat: 19.9615, lng: 79.2961, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 26, name: "KVK Gadchiroli",  district: "Gadchiroli", region: "vidarbha",   phone: "07132-222011", lat: 20.1809, lng: 80.0016, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 27, name: "KVK Gondia",      district: "Gondia",     region: "vidarbha",   phone: "07182-222011", lat: 21.4624, lng: 80.1967, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 28, name: "KVK Bhandara",    district: "Bhandara",   region: "vidarbha",   phone: "07184-222011", lat: 21.1662, lng: 79.6471, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },

  // KONKAN
  { id: 29, name: "KVK Raigad",      district: "Raigad",     region: "konkan",     phone: "02148-222248", lat: 18.9107, lng: 73.3213, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 30, name: "KVK Ratnagiri",   district: "Ratnagiri",  region: "konkan",     phone: "02352-232095", lat: 16.8972, lng: 73.5131, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 31, name: "KVK Sindhudurg",  district: "Sindhudurg", region: "konkan",     phone: "02362-222011", lat: 16.2670, lng: 73.7015, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 32, name: "KVK Thane",       district: "Thane",      region: "konkan",     phone: "02528-241439", lat: 19.9975, lng: 72.7178, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
  { id: 33, name: "KVK Palghar",     district: "Palghar",    region: "konkan",     phone: "02525-222011", lat: 19.6967, lng: 72.7697, mobileLab: false, soilCost: "₹100–₹200", tests: "pH, N, P, K, OC" },
];

const REGIONS = [
  { key: "all",        label: "All Regions" },
  { key: "western",    label: "Western MH"  },
  { key: "marathwada", label: "Marathwada"  },
  { key: "vidarbha",   label: "Vidarbha"    },
  { key: "konkan",     label: "Konkan"      },
  { key: "north",      label: "North MH"    },
];

const REGION_VIEWS: Record<string, { center: [number, number], zoom: number }> = {
  all:        { center: [76.5, 19.2], zoom: 6.2 },
  western:    { center: [74.8, 17.5], zoom: 7.5 },
  marathwada: { center: [76.5, 19.0], zoom: 7.5 },
  vidarbha:   { center: [78.8, 20.5], zoom: 7.2 },
  konkan:     { center: [73.3, 17.8], zoom: 7.5 },
  north:      { center: [74.8, 20.5], zoom: 7.5 },
};

function getDistanceKm(lat1: number, lng1: number, lat2: number, lng2: number) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export const NearbyKendras = () => {
  const { t } = useTranslation();
  const [activeRegion, setActiveRegion] = useState("all");
  const [mapCenter, setMapCenter]       = useState<[number, number]>([76.5, 19.2]);
  const [mapZoom, setMapZoom]           = useState(6.2);
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);
  const [distances, setDistances]       = useState<Record<number, number>>({});
  const [locating, setLocating]         = useState(false);

  const visibleKVKs =
    activeRegion === "all" ? kvks : kvks.filter((k) => k.region === activeRegion);

  const { translateBatch, language } = useTranslation();

  // Dynamic translation for all KVK data
  useEffect(() => {
    if (language === 'en') return;
    
    const stringsToTranslate = new Set<string>();
    kvks.forEach(kvk => {
      stringsToTranslate.add(kvk.name);
      stringsToTranslate.add(kvk.district);
      stringsToTranslate.add(kvk.tests);
      if (kvk.soilCost) stringsToTranslate.add(kvk.soilCost);
    });
    
    // Also include region labels
    REGIONS.forEach(r => stringsToTranslate.add(r.label));
    
    translateBatch(Array.from(stringsToTranslate));
  }, [language, translateBatch]);

  function handleRegionChange(regionKey: string) {
    setActiveRegion(regionKey);
    const view = REGION_VIEWS[regionKey];
    setMapCenter(view.center);
    setMapZoom(view.zoom);
  }

  function handleLocate() {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude: lat, longitude: lng } = pos.coords;
        setUserLocation({ lat, lng });
        const dist: Record<number, number> = {};
        kvks.forEach((k) => { dist[k.id] = getDistanceKm(lat, lng, k.lat, k.lng); });
        setDistances(dist);
        const nearest = kvks.reduce((a, b) => (dist[a.id] < dist[b.id] ? a : b));
        setMapCenter([nearest.lng, nearest.lat]);
        setMapZoom(11);
        setActiveRegion("all");
        setLocating(false);
      },
      () => {
        alert("Could not get your location. Please allow location access.");
        setLocating(false);
      }
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-7xl mx-auto px-6 py-20"
    >
      {/* Header */}
      <header className="mb-16 text-center">
        <h2 className="font-headline font-medium text-on-surface-variant tracking-widest uppercase text-sm mb-4">
          {t("Maharashtra · ICAR Official Network")}
        </h2>
        <h1 className="font-headline font-black text-5xl md:text-7xl tracking-tighter mb-6 text-primary">
          {t("Nearby Kendras")}
        </h1>
        <p className="font-body text-on-surface-variant max-w-2xl mx-auto text-lg leading-relaxed mb-8">
          {t("Find official government agricultural centres near you. Every KVK provides soil testing, expert guidance, and free farmer consultation.")}
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          {[
            t("49 KVKs across Maharashtra"), 
            t("Soil Testing available"), 
            t("Free expert consultation")
          ].map((s) => (
            <span key={s} className="text-xs font-bold uppercase tracking-wider px-4 py-2 rounded-full bg-surface-container-low text-on-surface-variant border border-on-surface/5">
              {s}
            </span>
          ))}
        </div>
      </header>

      {/* Soil Testing Summary Banner */}
      <section className="bg-surface-container-low p-6 md:p-8 rounded-2xl mb-12 flex flex-col md:flex-row items-center gap-6 border border-on-surface/5 hover:border-primary/10 transition-colors">
        <div className="bg-primary/10 p-4 rounded-xl text-primary">
          <FlaskConical className="size-8" />
        </div>
        <div className="flex-1 text-center md:text-left">
          <h3 className="font-headline font-bold text-xl mb-1 text-primary">
            {t("Soil Testing Available")}
          </h3>
          <p className="font-body text-on-surface-variant text-sm">
            {t("Tests: pH · NPK · Organic Carbon · Micronutrients · Results in 3–7 days")}
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-2">
           <span className="text-xs font-bold px-3 py-1.5 rounded-lg bg-surface-container-lowest text-primary border border-primary/20">₹100–₹200 {t("per sample")}</span>
        </div>
      </section>

      <div className="mb-10 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-6">
        <div className="overflow-x-auto pb-2 -mx-6 px-6 no-scrollbar flex-grow">
          <div className="flex flex-nowrap lg:flex-wrap items-center gap-3 min-w-max lg:min-w-0">
            {REGIONS.map((r) => (
              <button
                key={r.key}
                onClick={() => handleRegionChange(r.key)}
                className={`text-xs font-bold px-5 py-2.5 rounded-full transition-all duration-300 border whitespace-nowrap ${
                  activeRegion === r.key
                    ? "bg-primary text-on-primary border-primary shadow-lg shadow-primary/20"
                    : "bg-surface-container-lowest text-on-surface-variant border-on-surface/10 hover:border-primary/30"
                }`}
              >
                {t(r.label)}
              </button>
            ))}
          </div>
        </div>

        <Button
          onClick={handleLocate}
          disabled={locating}
          className="bg-primary text-on-primary hover:opacity-90 rounded-full px-8 h-11 shadow-xl shadow-primary/10 gap-3 w-full sm:w-auto shrink-0 font-headline font-bold uppercase tracking-tight text-xs"
        >
          <Navigation className={`size-4 ${locating ? 'animate-pulse' : ''}`} />
          {locating ? t("Locating...") : t("Find Nearest KVK")}
        </Button>
      </div>

      <div className="flex flex-col lg:grid lg:grid-cols-[380px_1fr] bg-surface-container-lowest rounded-3xl overflow-hidden border border-on-surface/5 shadow-2xl h-[800px] md:h-[700px] lg:h-[800px]">
        <div className="flex flex-col h-1/2 lg:h-full border-b lg:border-b-0 lg:border-r border-on-surface/5 bg-surface-container-lowest overflow-hidden order-2 lg:order-1">
          <div className="p-6 border-b border-on-surface/5">
            <h3 className="font-headline font-black text-xl flex items-center gap-2">
              <span className="text-primary">{visibleKVKs.length}</span> {t("Kendras")} {t("found")}
            </h3>
          </div>
          <div className="flex-grow overflow-y-auto p-4 space-y-4 no-scrollbar">
            {visibleKVKs.map((kvk) => (
              <div
                key={kvk.id}
                onClick={() => { setMapCenter([kvk.lng, kvk.lat]); setMapZoom(11); }}
                className="group p-5 rounded-2xl border bg-surface-container-lowest border-on-surface/5 hover:border-primary/30 transition-all duration-300 cursor-pointer"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-headline font-bold text-lg leading-tight group-hover:text-primary transition-colors pr-4">
                    {t(kvk.name)}
                  </h3>
                  <span className="text-[9px] font-black uppercase tracking-widest px-2 py-1 rounded bg-primary/5 text-primary">
                    {t("KVK")}
                  </span>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-on-surface-variant font-medium mb-4">
                  <div className="p-1 rounded-md bg-surface-container-low">
                    <Navigation className="size-3" />
                  </div>
                  <span>{t(kvk.district)} {t("District")}</span>
                  {distances[kvk.id] && (
                    <span className="ml-auto font-bold text-primary">
                      {distances[kvk.id].toFixed(1)} km
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-on-surface/5">
                  <div className="flex items-center gap-2 text-[11px] font-mono font-bold text-on-surface-variant/80">
                    <Phone className="size-3" />
                    {kvk.phone}
                  </div>
                  <a
                    href={`https://maps.google.com/?q=${kvk.lat},${kvk.lng}`}
                    target="_blank"
                    rel="noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-wider text-primary hover:underline"
                  >
                    {t("Directions")}
                    <ExternalLink className="size-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative h-1/2 lg:h-full order-1 lg:order-2">
          <Map center={mapCenter} zoom={mapZoom}>
            {userLocation && (
              <MapMarker longitude={userLocation.lng} latitude={userLocation.lat}>
                <MarkerPopup className="p-0 overflow-hidden">
                   <div className="bg-primary text-on-primary p-2 px-4 font-headline font-bold text-xs uppercase tracking-widest text-center">
                    {t("You")}
                  </div>
                </MarkerPopup>
              </MapMarker>
            )}

            {visibleKVKs.map((kvk) => (
              <MapMarker key={kvk.id} longitude={kvk.lng} latitude={kvk.lat}>
                <MarkerPopup className="p-0 overflow-hidden min-w-[280px]">
                  <div className="p-5 space-y-4 font-body">
                    <div>
                      <span className="text-[9px] font-black uppercase tracking-[0.2em] text-primary/70 block mb-1">
                        {t("ICAR · Krishi Vigyan Kendra")}
                      </span>
                      <h3 className="font-headline font-black text-lg leading-tight text-on-surface">{t(kvk.name)}</h3>
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-on-surface-variant mt-1">
                        <Navigation className="size-3 text-primary" />
                        {t(kvk.district)} {t("District")}
                      </div>
                    </div>

                    <div className="p-3 bg-surface-container-low rounded-xl border border-on-surface/5 space-y-2">
                       <p className="text-[11px] font-bold text-primary flex items-center gap-2">
                        <FlaskConical className="size-3.5" />
                        {t("Soil Testing Available")}
                      </p>
                      <div className="grid grid-cols-2 gap-2 mt-2">
                         <div className="bg-background p-2 rounded-lg text-center">
                            <span className="text-[9px] block uppercase tracking-widest opacity-50 mb-0.5">{t("Cost")}</span>
                            <span className="text-xs font-bold text-primary">{t(kvk.soilCost)}</span>
                         </div>
                         <div className="bg-background p-2 rounded-lg text-center">
                            <span className="text-[9px] block uppercase tracking-widest opacity-50 mb-0.5">{t("Time")}</span>
                            <span className="text-xs font-bold text-primary">3-7 {t("Days")}</span>
                         </div>
                      </div>
                    </div>

                    {kvk.mobileLab && (
                      <div className="flex items-center gap-2 p-2 px-3 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-amber-500/20">
                        <Truck className="size-4" />
                        {t("Mobile Lab Services")}
                      </div>
                    )}

                    <div className="pt-4 flex items-center gap-3">
                      <a
                        href={`https://maps.google.com/?q=${kvk.lat},${kvk.lng}`}
                        target="_blank"
                        rel="noreferrer"
                        className="flex-1"
                      >
                        <Button size="sm" className="w-full bg-primary text-on-primary font-headline font-bold uppercase tracking-tighter text-xs h-10 rounded-full gap-2">
                          <Navigation className="size-3" />
                          {t("Directions")}
                        </Button>
                      </a>
                      <a href={`tel:${kvk.phone}`} className="h-10 w-10 flex items-center justify-center rounded-full border border-on-surface/10 hover:bg-surface-container transition-colors text-on-surface-variant">
                         <Phone className="size-4" />
                      </a>
                    </div>
                  </div>
                </MarkerPopup>
              </MapMarker>
            ))}
          </Map>
        </div>
      </div>

    </motion.div>
  );
};
