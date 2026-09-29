import { motion, AnimatePresence } from "motion/react";
import React, { useState, useEffect, useMemo } from "react";
import {
  Map,
  MapMarker,
  MarkerPopup,
} from "@/src/components/ui/map";
import { Button } from "@/src/components/ui/button";
import { Navigation, ExternalLink, Search, X, CheckCircle2, AlertCircle, MapPin, Globe, Phone, Mail, Building, Info, Loader2 } from "lucide-react";
import { useTranslation } from "../contexts/LanguageContext";
import { safeFetchJson } from "@/src/lib/api";

const STATE_LIST = [
  "All of India",
  "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
  "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", 
  "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", 
  "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
  "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
  "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
];

function LocationStatusBadge({ kvk }: { kvk: any }) {
  const { t } = useTranslation();
  if (kvk.latitude && kvk.longitude) {
    return (
      <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md border border-emerald-100">
        <CheckCircle2 className="size-3.5" />
        {t("Exact location verified")}
      </div>
    );
  }
  if (kvk.address) {
    return (
      <div className="flex items-center gap-1.5 text-[11px] font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-md border border-amber-100">
        <MapPin className="size-3.5" />
        {t("Official address available")}
      </div>
    );
  }
  return (
    <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-500 bg-slate-50 px-2 py-1 rounded-md border border-slate-200">
      <AlertCircle className="size-3.5" />
      {t("Location mapping pending")}
    </div>
  );
}

export const NearbyKendras = () => {
  const { t, translateBatch, language } = useTranslation();
  
  const [kvks, setKvks] = useState<any[]>([]);
  const [activeState, setActiveState] = useState("Maharashtra");
  const [activeDistrict, setActiveDistrict] = useState("All Districts");
  const [searchQuery, setSearchQuery] = useState("");
  
  const [mapCenter, setMapCenter] = useState<[number, number]>([76.5, 19.2]);
  const [mapZoom, setMapZoom] = useState(6.2);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [selectedKvk, setSelectedKvk] = useState<any>(null);

  // Fetch KVKs from API when state changes
  useEffect(() => {
    async function fetchKvks() {
      setLoading(true);
      setError(false);
      
      const baseUrl = "/api/v1/kvks/?limit=100";
      const filterUrl = activeState !== "All of India" ? `&state=${encodeURIComponent(activeState)}` : "";
      
      let allRecords: any[] = [];
      let currentPage = 1;
      let totalPages = 1;

      try {
        do {
          const res = await safeFetchJson(`${baseUrl}${filterUrl}&page=${currentPage}`);
          if (res.success && res.data) {
            const payload = res.data;
            if (payload.data && Array.isArray(payload.data)) {
              allRecords = [...allRecords, ...payload.data];
            }
            totalPages = payload.pagination?.total_pages || 1;
            currentPage++;
          } else {
            break;
          }
        } while (currentPage <= totalPages);
        
        const uniqueIds = new Set();
        const uniqueRecords = [];
        for (const record of allRecords) {
          if (!uniqueIds.has(record.id)) {
            uniqueIds.add(record.id);
            uniqueRecords.push(record);
          }
        }
        setKvks(uniqueRecords);
        setActiveDistrict("All Districts");
      } catch (err) {
        console.error("Failed to fetch KVKs:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    }
    
    fetchKvks();
  }, [activeState]);

  // Derived state
  const availableDistricts = useMemo(() => {
    const dists = new Set<string>();
    kvks.forEach(k => {
      if (k.district) dists.add(k.district);
    });
    return ["All Districts", ...Array.from(dists).sort()];
  }, [kvks]);

  const filteredKvks = useMemo(() => {
    let result = kvks;
    
    // District filter
    if (activeDistrict !== "All Districts") {
      result = result.filter(k => k.district === activeDistrict);
    }
    
    // Search filter
    if (searchQuery.trim() !== "") {
      const q = searchQuery.toLowerCase();
      result = result.filter(k => 
        (k.name && k.name.toLowerCase().includes(q)) ||
        (k.district && k.district.toLowerCase().includes(q)) ||
        (k.state && k.state.toLowerCase().includes(q)) ||
        (k.address && k.address.toLowerCase().includes(q)) ||
        (k.host_org && k.host_org.toLowerCase().includes(q))
      );
    }
    
    return result;
  }, [kvks, activeDistrict, searchQuery]);

  // Network Summary Stats
  const stats = useMemo(() => {
    const states = new Set<string>();
    const districts = new Set<string>();
    let exactLocations = 0;
    
    kvks.forEach(k => {
      if (k.state) states.add(k.state);
      if (k.district) districts.add(k.district);
      if (k.latitude && k.longitude) exactLocations++;
    });
    
    return {
      total: kvks.length,
      states: states.size,
      districts: districts.size,
      mapped: exactLocations
    };
  }, [kvks]);

  // Translation hook
  useEffect(() => {
    if (language === 'en' || kvks.length === 0) return;
    
    const stringsToTranslate = new Set<string>();
    kvks.forEach(kvk => {
      stringsToTranslate.add(kvk.name);
      if (kvk.district) stringsToTranslate.add(kvk.district);
      if (kvk.state) stringsToTranslate.add(kvk.state);
    });
    STATE_LIST.forEach(s => stringsToTranslate.add(s));
    availableDistricts.forEach(d => stringsToTranslate.add(d));
    
    translateBatch(Array.from(stringsToTranslate));
  }, [language, translateBatch, kvks, availableDistricts]);

  function handleStateChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const newState = e.target.value;
    setActiveState(newState);
    if (newState === "All of India") {
      setMapCenter([78.9629, 20.5937]);
      setMapZoom(4.5);
    } else if (newState === "Maharashtra") {
      setMapCenter([76.5, 19.2]);
      setMapZoom(6.2);
    } else {
      setMapCenter([78.9629, 20.5937]);
      setMapZoom(5.5);
    }
  }
  
  const mapKVKs = filteredKvks.filter(k => k.latitude != null && k.longitude != null);
  
  const getDirectionsLink = (kvk: any) => {
    if (kvk.latitude && kvk.longitude) {
      return `https://www.google.com/maps/dir/?api=1&destination=${kvk.latitude},${kvk.longitude}`;
    }
    return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(kvk.name + ' ' + (kvk.address || `${kvk.district} ${kvk.state}`))}`;
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-[1400px] mx-auto px-4 md:px-8 py-12 md:py-20"
    >
      <header className="mb-12 text-center">
        <h2 className="font-headline font-medium text-primary tracking-widest uppercase text-sm mb-4">
          {t("KVK Explorer")}
        </h2>
        <h1 className="font-headline font-black text-4xl md:text-6xl tracking-tighter mb-4 text-on-surface">
          {t("KVK Network")}
        </h1>
        <p className="font-body text-on-surface-variant max-w-2xl mx-auto text-lg leading-relaxed mb-10">
          {t("Find agricultural support centres")}
        </p>
        
        {/* Network Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
           <div className="bg-surface-container-lowest border border-on-surface/5 p-4 rounded-2xl flex flex-col items-center">
             <span className="font-black text-3xl text-primary">{stats.total}</span>
             <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant mt-1">{t("KVKs found")}</span>
           </div>
           <div className="bg-surface-container-lowest border border-on-surface/5 p-4 rounded-2xl flex flex-col items-center">
             <span className="font-black text-3xl text-primary">{stats.states}</span>
             <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant mt-1">{t("States / UTs")}</span>
           </div>
           <div className="bg-surface-container-lowest border border-on-surface/5 p-4 rounded-2xl flex flex-col items-center">
             <span className="font-black text-3xl text-primary">{stats.districts}</span>
             <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant mt-1">{t("Districts identified")}</span>
           </div>
           <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-2xl flex flex-col items-center">
             <span className="font-black text-3xl text-emerald-600">{stats.mapped}</span>
             <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 mt-1 text-center leading-tight">{t("Exact locations mapped")}</span>
           </div>
        </div>
      </header>

      {/* Filters */}
      <div className="bg-surface-container-lowest p-4 md:p-6 rounded-3xl border border-on-surface/5 shadow-sm mb-8 flex flex-col md:flex-row gap-4 items-center">
        <div className="w-full md:w-1/3 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 size-5 text-on-surface-variant/50" />
          <input 
            type="text" 
            placeholder={t("Search KVK by name, district or address")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-12 bg-surface-container text-on-surface rounded-xl pl-12 pr-4 font-body focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>
        
        <div className="w-full md:w-1/3">
          <select 
            value={activeState} 
            onChange={handleStateChange}
            className="w-full h-12 bg-surface-container text-on-surface rounded-xl px-4 font-body focus:outline-none focus:ring-2 focus:ring-primary/20 cursor-pointer"
          >
            {STATE_LIST.map((stateName) => (
              <option key={stateName} value={stateName}>
                {t(stateName)}
              </option>
            ))}
          </select>
        </div>

        <div className="w-full md:w-1/3">
          <select 
            value={activeDistrict} 
            onChange={(e) => setActiveDistrict(e.target.value)}
            disabled={activeState === "All of India"}
            className="w-full h-12 bg-surface-container text-on-surface rounded-xl px-4 font-body focus:outline-none focus:ring-2 focus:ring-primary/20 cursor-pointer disabled:opacity-50"
          >
            {availableDistricts.map((distName) => (
              <option key={distName} value={distName}>
                {t(distName)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex flex-col lg:grid lg:grid-cols-[1fr_400px] xl:grid-cols-[1fr_450px] gap-8 h-[800px]">
        {/* Map Column */}
        <div className="bg-surface-container-lowest rounded-3xl overflow-hidden border border-on-surface/5 shadow-xl relative order-2 lg:order-1 h-[500px] lg:h-full flex flex-col">
          <div className="flex-1 relative">
            <Map center={mapCenter} zoom={mapZoom}>
              {mapKVKs.map((kvk) => (
                <MapMarker key={kvk.id} longitude={kvk.longitude} latitude={kvk.latitude}>
                  <MarkerPopup className="p-0 overflow-hidden min-w-[280px]">
                    <div className="p-4 space-y-3 font-body">
                        <span className="text-[10px] font-black uppercase tracking-[0.1em] text-primary block mb-1">
                          {t("ICAR · Krishi Vigyan Kendra")}
                        </span>
                        <h3 className="font-headline font-black text-base leading-tight text-on-surface">{t(kvk.name)}</h3>
                        <div className="flex items-center gap-1.5 text-xs font-medium text-on-surface-variant">
                          <Navigation className="size-3 text-primary" />
                          {t(kvk.district)}, {t(kvk.state)}
                        </div>
                        <Button 
                          onClick={() => setSelectedKvk(kvk)} 
                          size="sm" 
                          className="w-full bg-surface-container-low text-on-surface hover:bg-surface-container"
                        >
                          {t("View Details")}
                        </Button>
                    </div>
                  </MarkerPopup>
                </MapMarker>
              ))}
            </Map>
            <div className="absolute bottom-4 left-4 right-4 bg-background/95 backdrop-blur border border-on-surface/10 p-3 rounded-xl shadow-lg flex gap-3 items-start">
               <Info className="size-5 text-primary shrink-0 mt-0.5" />
               <p className="text-xs font-medium text-on-surface leading-relaxed">
                 {t("Map markers show KVKs with verified exact locations.")} {t("Other KVKs remain searchable using their official address.")}
               </p>
            </div>
          </div>
        </div>

        {/* Results Column */}
        <div className="bg-surface-container-lowest rounded-3xl overflow-hidden border border-on-surface/5 shadow-xl flex flex-col order-1 lg:order-2 h-[600px] lg:h-full">
           <div className="p-5 border-b border-on-surface/5 flex justify-between items-center bg-surface-container-lowest z-10 shrink-0">
              <h3 className="font-headline font-bold text-lg text-on-surface">
                {filteredKvks.length} {t("KVKs found")}
              </h3>
              {loading && <Loader2 className="size-5 animate-spin text-primary" />}
           </div>
           
           <div className="flex-1 overflow-y-auto p-4 space-y-4">
             {error ? (
               <div className="text-center p-8 text-on-surface-variant">
                 <AlertCircle className="size-8 mx-auto mb-3 opacity-50" />
                 <p>{t("We couldn't load KVK information right now")}</p>
               </div>
             ) : loading && kvks.length === 0 ? (
               <div className="text-center p-8 text-on-surface-variant">
                 <Loader2 className="size-8 mx-auto mb-3 animate-spin text-primary" />
                 <p>{t("Finding Krishi Vigyan Kendras...")}</p>
               </div>
             ) : filteredKvks.length === 0 ? (
               <div className="text-center p-8 text-on-surface-variant">
                 <Search className="size-8 mx-auto mb-3 opacity-30" />
                 <p>{t("No KVKs found")}</p>
               </div>
             ) : (
               filteredKvks.map(kvk => (
                 <div key={kvk.id} className="p-5 rounded-2xl border border-on-surface/5 bg-background hover:border-primary/20 transition-all flex flex-col gap-4">
                    <div>
                      <div className="flex justify-between items-start mb-2 gap-3">
                        <h4 className="font-headline font-bold text-base leading-tight text-on-surface">
                          {t(kvk.name)}
                        </h4>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-on-surface-variant font-medium">
                        <MapPin className="size-3.5" />
                        {t(kvk.district)}, {t(kvk.state)}
                      </div>
                    </div>
                    
                    <LocationStatusBadge kvk={kvk} />
                    
                    <div className="text-xs text-on-surface-variant line-clamp-2 leading-relaxed">
                      {kvk.address}
                    </div>

                    <div className="flex gap-2 mt-2">
                       <Button 
                         variant="outline" 
                         size="sm" 
                         className="flex-1 text-xs font-bold"
                         onClick={() => setSelectedKvk(kvk)}
                       >
                         {t("View Details")}
                       </Button>
                       <a
                          href={getDirectionsLink(kvk)}
                          target="_blank"
                          rel="noreferrer"
                          className="flex-1"
                        >
                          <Button size="sm" className="w-full bg-primary text-on-primary font-bold text-xs gap-1.5">
                            <Navigation className="size-3.5" />
                            {t("Get Directions")}
                          </Button>
                        </a>
                    </div>
                 </div>
               ))
             )}
           </div>
        </div>
      </div>

      {/* Details Modal */}
      <AnimatePresence>
        {selectedKvk && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedKvk(null)}
              className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative bg-surface-container-lowest w-full max-w-2xl rounded-3xl shadow-2xl border border-on-surface/10 overflow-hidden flex flex-col max-h-[90vh]"
            >
              <div className="p-6 border-b border-on-surface/5 flex justify-between items-start bg-surface-container-low">
                <div>
                  <h2 className="font-headline font-black text-2xl text-on-surface mb-2">{t(selectedKvk.name)}</h2>
                  <div className="flex items-center gap-2 text-sm text-on-surface-variant font-medium">
                    <MapPin className="size-4" />
                    {t(selectedKvk.district)}, {t(selectedKvk.state)}
                  </div>
                </div>
                <button onClick={() => setSelectedKvk(null)} className="p-2 bg-background rounded-full hover:bg-surface-container transition-colors">
                  <X className="size-5 text-on-surface-variant" />
                </button>
              </div>
              
              <div className="p-6 overflow-y-auto font-body space-y-6">
                <LocationStatusBadge kvk={selectedKvk} />
                
                {selectedKvk.address && (
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2 flex items-center gap-2"><MapPin className="size-4"/> {t("Address")}</h4>
                    <p className="text-on-surface bg-surface-container-low p-4 rounded-xl leading-relaxed">{selectedKvk.address}</p>
                  </div>
                )}
                
                {selectedKvk.host_org && (
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-2 flex items-center gap-2"><Building className="size-4"/> {t("Host organization")}</h4>
                    <div className="bg-surface-container-low p-4 rounded-xl">
                      <p className="text-on-surface font-medium">{selectedKvk.host_org}</p>
                      {selectedKvk.host_type && (
                        <p className="text-xs text-on-surface-variant mt-1">{t("Host type")}: {selectedKvk.host_type}</p>
                      )}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedKvk.phone && (
                    <div className="flex items-center gap-3 p-4 bg-surface-container-low rounded-xl">
                      <Phone className="size-5 text-primary" />
                      <div>
                        <span className="text-xs text-on-surface-variant block mb-0.5">Phone</span>
                        <a href={`tel:${selectedKvk.phone}`} className="font-medium hover:text-primary transition-colors">{selectedKvk.phone}</a>
                      </div>
                    </div>
                  )}
                  {selectedKvk.email && (
                    <div className="flex items-center gap-3 p-4 bg-surface-container-low rounded-xl">
                      <Mail className="size-5 text-primary" />
                      <div>
                        <span className="text-xs text-on-surface-variant block mb-0.5">Email</span>
                        <a href={`mailto:${selectedKvk.email}`} className="font-medium hover:text-primary transition-colors">{selectedKvk.email}</a>
                      </div>
                    </div>
                  )}
                  {selectedKvk.year_established && (
                    <div className="flex items-center gap-3 p-4 bg-surface-container-low rounded-xl">
                      <Info className="size-5 text-primary" />
                      <div>
                        <span className="text-xs text-on-surface-variant block mb-0.5">{t("Year established")}</span>
                        <span className="font-medium">{selectedKvk.year_established}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="p-6 border-t border-on-surface/5 bg-surface-container-low flex flex-wrap gap-3">
                {selectedKvk.latitude && selectedKvk.longitude && (
                  <Button 
                    onClick={() => {
                      setMapCenter([selectedKvk.longitude, selectedKvk.latitude]);
                      setMapZoom(13);
                      setSelectedKvk(null);
                    }}
                    className="bg-primary text-on-primary"
                  >
                    <MapPin className="size-4 mr-2" />
                    {t("Show on Map")}
                  </Button>
                )}
                
                <a href={getDirectionsLink(selectedKvk)} target="_blank" rel="noreferrer">
                  <Button variant="outline" className="bg-background border-on-surface/10 hover:bg-surface-container">
                    <Navigation className="size-4 mr-2" />
                    {t("Get Directions")}
                  </Button>
                </a>
                
                {selectedKvk.url && (
                  <a href={selectedKvk.url} target="_blank" rel="noreferrer" className="ml-auto">
                    <Button variant="ghost" className="text-primary hover:bg-primary/10">
                      <Globe className="size-4 mr-2" />
                      {t("Official Website")}
                    </Button>
                  </a>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
