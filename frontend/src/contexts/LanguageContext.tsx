import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export type Language = 'en' | 'hi' | 'mr';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (text: string) => string;
  translateBatch: (texts: string[]) => Promise<void>;
  loading: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);


// Static translation dictionary for instant language switching
const staticTranslations: Record<Language, Record<string, string>> = {
  en: {},
  hi: {
    "Home": "होम",
    "Predict Crop": "फसल भविष्यवाणी",
    "How It Works": "यह कैसे काम करता है",
    "The Digital Curator for Agriculture.": "कृषि के लिए डिजिटल क्यूरेटर।",
    "Privacy Policy": "गोपनीयता नीति",
    "Terms of Service": "सेवा की शर्तें",
    "Contact Support": "सहायता से संपर्क करें",
    "Smart Crop Recommendation System": "स्मार्ट फसल अनुशंसा प्रणाली",
    "KrushiSense is a smart agriculture web application that helps farmers choose the most suitable crop based on soil and environmental conditions. The system uses machine learning to analyze important factors like Nitrogen (N), Phosphorus (P), Potassium (K), pH level, temperature, humidity, and rainfall.": "कृषिसेन्स एक स्मार्ट कृषि वेब अनुप्रयोग है जो किसानों को मिट्टी और पर्यावरणीय स्थितियों के आधार पर सबसे उपयुक्त फसल चुनने में मदद करता है। सिस्टम नाइट्रोजन (एन), फास्फोरस (पी), पोटेशियम (के), पीएच स्तर, तापमान, आर्द्रता और वर्षा जैसे महत्वपूर्ण कारकों का विश्लेषण करने के लिए मशीन लर्निंग का उपयोग करता है।",
    "Start Prediction": "शुरू करें",
    "Agricultural Intelligence": "कृषि बुद्धिमत्ता",
    "Empowering farmers with data-driven decision making.": "डेटा-संचालित निर्णय लेने के साथ किसानों को सशक्त बनाना।",
    "Helps farmers choose the right crop": "किसानों को सही फसल चुनने में मदद करता है",
    "By analyzing multi-layered environmental data points, our ML model identifies the perfect genetic match for your soil.": "बहु-स्तरीय पर्यावरणीय डेटा बिंदुओं का विश्लेषण करके, हमारा एमएल मॉडल आपकी मिट्टी के लिए सही आनुवंशिक मिलान की पहचान करता है।",
    "Improves crop productivity": "फसल उत्पादकता में सुधार करता है",
    "Maximize your yield by planting what nature intended for your specific geographical and chemical profile.": "प्रकृति ने आपकी विशिष्ट भौगोलिक और रासायनिक प्रोफ़ाइल के लिए जो इरादा किया है उसे लगाकर अपनी उपज को अधिकतम करें।",
    "Saves time and effort": "समय और प्रयास बचाता है",
    "Instant analysis eliminates weeks of manual soil testing and guesswork.": "त्वरित विश्लेषण हफ्तों के मैनुअल मिट्टी परीक्षण और अनुमान को समाप्त करता है।",
    "Reduces financial loss": "वित्तीय नुकसान को कम करता है",
    "Prevent investment in crops destined to fail due to incompatible soil pH or climatic shifts.": "असंगत मिट्टी के पीएच या जलवायु परिवर्तनों के कारण विफल होने वाली फसलों में निवेश को रोकें।",
    "Easy to use for everyone": "सभी के लिए उपयोग में आसान",
    "A minimalist interface designed with accessibility and clarity at its core.": "पहुंच और स्पष्टता को ध्यान में रखकर बनाया गया एक न्यूनतम इंटरफ़ेस।",
    "Cultivating the Future": "भविष्य की खेती",
    "Harnessing the power of precision agriculture to ensure food security through digital curation.": "डिजिटल क्यूरेशन के माध्यम से खाद्य सुरक्षा सुनिश्चित करने के लिए सटीक कृषि की शक्ति का उपयोग करना।",
    "The Science Behind The Harvest.": "कटाई के पीछे का विज्ञान।",
    "KrushiSense bridges traditional wisdom and modern data science to deliver precision crop recommendations.": "कृषिसेन्स सटीक फसल अनुशंसाएं देने के लिए पारंपरिक ज्ञान और आधुनिक डेटा विज्ञान को जोड़ता है।",
    "The Workflow": "कार्यप्रवाह",
    "Input Data": "इनपुट डेटा",
    "Enter your specific soil metrics: Nitrogen (N), Phosphorus (P), Potassium (K), pH levels, and environmental factors like Temperature, Humidity, and Rainfall.": "अपने विशिष्ट मिट्टी के मेट्रिक्स दर्ज करें: नाइट्रोजन (एन), फास्फोरस (पी), पोटेशियम (के), पीएच स्तर, और तापमान, आर्द्रता और वर्षा जैसे पर्यावरणीय कारक।",
    "Data Processing": "डेटा प्रोसेसिंग",
    "Your information is securely transmitted to our backend API where it is normalized and prepared for analysis using specialized agricultural algorithms.": "आपकी जानकारी सुरक्षित रूप से हमारे बैकएंड एपीआई को प्रेषित की जाती है जहां इसे विशेष कृषि एल्गोरिदम का उपयोग करके विश्लेषण के लिए सामान्यीकृत और तैयार किया जाता है।",
    "Machine Learning": "मशीन लर्निंग",
    "Our pre-trained ML model cross-references your soil profile against thousands of successful harvest data points to find the optimal match.": "हमारा पूर्व-प्रशिक्षित एमएल मॉडल इष्टतम मिलान खोजने के लिए हजारों सफल फसल डेटा बिंदुओं के साथ आपकी मिट्टी की प्रोफाइल का मिलान करता है।",
    "Recommendation": "अनुशंसा",
    "Receive a ranked list of the top 3 crops most likely to thrive in your current environment, ensuring maximum yield and resource efficiency.": "शीर्ष 3 फसलों की एक रैंक वाली सूची प्राप्त करें जो आपके वर्तमान वातावरण में पनपने की सबसे अधिक संभावना है, जिससे अधिकतम उपज और संसाधन दक्षता सुनिश्चित होती है।",
    "Important Note: The accuracy of the recommendation depends on correct input values. Precision in soil testing leads to precision in results.": "महत्वपूर्ण नोट: अनुशंसा की सटीकता सही इनपुट मानों पर निर्भर करती है। मिट्टी के परीक्षण में सटीकता परिणामों में सटीकता की ओर ले जाती है।",
    "Resources": "संसाधन",
    "Where to get your data.": "अपना डेटा कहां से प्राप्त करें।",
    "Access reliable testing facilities to ensure your input data is scientifically verified.": "यह सुनिश्चित करने के लिए विश्वसनीय परीक्षण सुविधाओं तक पहुंचें कि आपका इनपुट डेटा वैज्ञानिक रूप से सत्यापित है।",
    "Soil Testing Laboratories": "मिट्टी परीक्षण प्रयोगशालाएं",
    "Professional labs provide detailed chemical analysis of N, P, K levels and pH concentration.": "पेशेवर प्रयोगशालाएं एन, पी, के स्तर और पीएच एकाग्रता का विस्तृत रासायनिक विश्लेषण प्रदान करती हैं।",
    "Agriculture Centers": "कृषि केंद्र",
    "Government-led centers often provide subsidized or free basic soil testing kits and reports.": "सरकारी नेतृत्व वाले केंद्र अक्सर रियायती या मुफ्त बुनियादी मिट्टी परीक्षण किट और रिपोर्ट प्रदान करते हैं।",
    "IoT Soil Sensors": "IoT मिट्टी सेंसर",
    "Real-time smart devices can be installed in your fields for continuous monitoring of moisture and nutrients.": "नमी और पोषक तत्वों की निरंतर निगरानी के लिए आपके खेतों में रीयल-टाइम स्मार्ट डिवाइस स्थापित किए जा सकते हैं।",
    "Predictive Cultivation.": "भविष्य कहनेवाला खेती।",
    "Input your soil and environmental parameters to identify the most suitable crops for your specific terrain.": "अपने विशिष्ट इलाके के लिए सबसे उपयुक्त फसलों की पहचान करने के लिए अपनी मिट्टी और पर्यावरणीय मापदंडों को इनपुट करें।",
    "Nitrogen (N)": "नाइट्रोजन (एन)",
    "Enter N ratio": "एन अनुपात दर्ज करें",
    "mg/kg": "मिलीग्राम/किग्रा",
    "Phosphorus (P)": "फास्फोरस (पी)",
    "Enter P ratio": "पी अनुपात दर्ज करें",
    "Potassium (K)": "पोटेशियम (के)",
    "Enter K ratio": "के अनुपात दर्ज करें",
    "Soil pH": "मिट्टी का पीएच",
    "Enter pH level": "पीएच स्तर दर्ज करें",
    "pH scale (0-14)": "पीएच स्केल (0-14)",
    "Temperature": "तापमान",
    "Enter degrees": "डिग्री दर्ज करें",
    "°C": "°C",
    "Humidity": "आर्द्रता",
    "Enter humidity": "आर्द्रता दर्ज करें",
    "Rainfall": "वर्षा",
    "Annual average": "वार्षिक औसत",
    "Top 3 Recommended Crops": "शीर्ष 3 अनुशंसित फसलें",
    "Primary Recommendation": "प्राथमिक अनुशंसा",
    "Secondary Match": "माध्यमिक मिलान",
    "Tertiary Alternative": "तृतीयक विकल्प",
    "Rice": "चावल",
    "Wheat": "गेहूं",
    "Cotton": "कपास",
    "Maize": "मक्का",
    "Jute": "जूट",
    "Coffee": "कॉफी",
    "Tea": "चाय",
    "Rubber": "रबर",
    "Coconut": "नारियल",
    "Sugarcane": "गन्ना",
    "Tobacco": "तंबाकू",
    "Groundnut": "मूंगफली",
    "Soybean": "सोयाबीन",
    "Mustard": "सरसों",
    "Sunflower": "सूरजमुखी",
    "Optimal Match": "इष्टतम मिलान",
    "High Viability": "उच्च व्यवहार्यता",
    "Strong Potential": "मजबूत क्षमता",
    "Suitable": "उपयुक्त",
    "Recommended": "अनुशंसित",
    "Similar Region": "समान क्षेत्र",
    "Suitable Soil": "उपयुक्त मिट्टी",
    "Recommended Fertilizer": "अनुशंसित उर्वरक",
    "Based on similar agricultural conditions from real dataset": "वास्तविक डेटासेट से समान कृषि स्थितियों पर आधारित",
    "Nearby Kendras": "नजदीकी केंद्र",
    "Find Nearby Agriculture Kendras": "नजदीकी कृषि केंद्र खोजें",
    "Locate government centers and resources near you": "अपने पास के सरकारी केंद्रों और संसाधनों का पता लगाएं",
    "Maharashtra · ICAR Official Network": "महाराष्ट्र · आईसीएआर आधिकारिक नेटवर्क",
    "Krishi Vigyan Kendras": "कृषि विज्ञान केंद्र",
    "Find official government agricultural centres near you. Every KVK provides soil testing, expert guidance, and free farmer consultation.": "अपने पास के आधिकारिक सरकारी कृषि केंद्र खोजें। प्रत्येक केवीके मिट्टी परीक्षण, विशेषज्ञ मार्गदर्शन और मुफ्त किसान परामर्श प्रदान करता है।",
    "🏛️ 49 KVKs across Maharashtra": "🏛️ महाराष्ट्र भर में 49 केवीके",
    "🧪 Soil Testing at every KVK": "🧪 प्रत्येक केवीके में मिट्टी परीक्षण",
    "💰 ₹100–₹200 per sample": "💰 ₹100–₹200 प्रति नमूना",
    "🆓 Free expert consultation": "🆓 मुफ्त विशेषज्ञ परामर्श",
    "Soil Testing Available at Every KVK — ₹100 to ₹200 per sample": "प्रत्येक केवीके में मिट्टी परीक्षण उपलब्ध — ₹100 से ₹200 प्रति नमूना",
    "Tests: pH · Nitrogen · Phosphorus · Potassium · Organic Carbon · Micronutrients · Results in 3–7 days": "परीक्षण: पीएच · नाइट्रोजन · फास्फोरस · पोटेशियम · जैविक कार्बन · सूक्ष्म पोषक तत्व · परिणाम 3-7 दिनों में",
    "Filter:": "फिल्टर:",
    "All Regions": "सभी क्षेत्र",
    "Western MH": "पश्चिमी महाराष्ट्र",
    "Marathwada": "मराठवाड़ा",
    "Vidarbha": "विदर्भ",
    "Konkan": "कोंकण",
    "North MH": "उत्तरी महाराष्ट्र",
    "Find Nearest KVK": "नजदीकी केवीके खोजें",
    "Locating...": "खोज रहे हैं...",
    "Showing": "दिखा रहा है",
    "Kendras": "केंद्र",
    "KVK": "केवीके",
    " District": " जिला",
    "🧪 Soil Testing": "🧪 मिट्टी परीक्षण",
    "Mobile Lab": "मोबाइल लैब",
    "💬 Free Consultation": "💬 मुफ्त परामर्श",
    "Maps": "मैप्स",
    "You": "आप",
    "ICAR · Krishi Vigyan Kendra": "आईसीएआर · कृषि विज्ञान केंद्र",
    "📍": "📍",
    "Soil Testing Available": "मिट्टी परीक्षण उपलब्ध",
    "Cost:": "लागत:",
    " per sample": " प्रति नमूना",
    "Tests:": "परीक्षण:",
    "Mobile Lab — visits your farm": "मोबाइल लैब — आपके खेत का दौरा करती है",
    "from your location": "आपके स्थान से",
    "Directions": "दिशानिर्देश",
    "KVK (Official ICAR)": "केवीके (आधिकारिक आईसीएआर)",
    "KVK with Mobile Soil Lab": "मोबाइल मिट्टी लैब के साथ केवीके",
    "Your Location": "आपका स्थान"
  },
  mr: {
    "Home": "होम",
    "Predict Crop": "पीक भविष्यवाणी",
    "How It Works": "हे कसे कार्य करते",
    "The Digital Curator for Agriculture.": "शेतीसाठी डिजिटल क्युरेटर.",
    "Privacy Policy": "गोपनीयता धोरण",
    "Terms of Service": "सेवा अटी",
    "Contact Support": "संपर्क साधा",
    "Smart Crop Recommendation System": "स्मार्ट पीक शिफारस प्रणाली",
    "KrushiSense is a smart agriculture web application that helps farmers choose the most suitable crop based on soil and environmental conditions. The system uses machine learning to analyze important factors like Nitrogen (N), Phosphorus (P), Potassium (K), pH level, temperature, humidity, and rainfall.": "कृषीसेन्स हे एक स्मार्ट कृषी वेब अनुप्रयोग आहे जे शेतकऱ्यांना माती आणि पर्यावरणीय परिस्थितीच्या आधारावर सर्वात योग्य पीक निवडण्यास मदत करते. सिस्टम नायट्रोजन (एन), फॉस्फरस (पी), पोटॅशियम (के), पीएच पातळी, तापमान, आद्रता आणि पाऊस यांसारख्या महत्त्वाच्या घटकांचे विश्लेषण करण्यासाठी मशीन लर्निंगचा वापर करते.",
    "Start Prediction": "सुरू करा",
    "Agricultural Intelligence": "कृषी बुद्धिमत्ता",
    "Empowering farmers with data-driven decision making.": "डेटा-आधारित निर्णय घेण्यासह शेतकऱ्यांना सक्षम करणे.",
    "Helps farmers choose the right crop": "शेतकऱ्यांना योग्य पीक निवडण्यास मदत करते",
    "By analyzing multi-layered environmental data points, our ML model identifies the perfect genetic match for your soil.": "बहु-स्तरीय पर्यावरणीय डेटा पॉइंट्सचे विश्लेषण करून, आमचे एमएल मॉडेल तुमच्या मातीसाठी योग्य अनुवांशिक जुळणी ओळखते.",
    "Improves crop productivity": "पीक उत्पादकता सुधारते",
    "Maximize your yield by planting what nature intended for your specific geographical and chemical profile.": "निसर्गाने तुमच्या विशिष्ट भौगोलिक आणि रासायनिक प्रोफाइलसाठी जे नियोजित केले आहे ते लावून तुमचे उत्पन्न वाढवा.",
    "Saves time and effort": "वेळ आणि श्रम वाचवते",
    "Instant analysis eliminates weeks of manual soil testing and guesswork.": "झटपट विश्लेषण आठवड्यांचे मॅन्युअल माती परीक्षण आणि अंदाज काढून टाकते.",
    "Reduces financial loss": "आर्थिक नुकसान कमी करते",
    "Prevent investment in crops destined to fail due to incompatible soil pH or climatic shifts.": "विसंगत माती पीएच किंवा हवामानातील बदलांमुळे अपयशी ठरणाऱ्या पिकांमधील गुंतवणूक टाळा.",
    "Easy to use for everyone": "सर्वांसाठी वापरण्यास सोपे",
    "A minimalist interface designed with accessibility and clarity at its core.": "प्रवेशयोग्यता आणि स्पष्टता लक्षात घेऊन डिझाइन केलेले एक किमान इंटरफेस.",
    "Cultivating the Future": "भविष्यातील शेती",
    "Harnessing the power of precision agriculture to ensure food security through digital curation.": "डिजिटल क्युरेशनद्वारे अन्न सुरक्षा सुनिश्चित करण्यासाठी अचूक शेतीची शक्ती वापरणे.",
    "The Science Behind The Harvest.": "कापणीमागील विज्ञान.",
    "KrushiSense bridges traditional wisdom and modern data science to deliver precision crop recommendations.": "कृषीसेन्स अचूक पीक शिफारसी देण्यासाठी पारंपारिक शहाणपण आणि आधुनिक डेटा सायन्स जोडते.",
    "The Workflow": "कार्यप्रवाह",
    "Input Data": "इनपुट डेटा",
    "Enter your specific soil metrics: Nitrogen (N), Phosphorus (P), Potassium (K), pH levels, and environmental factors like Temperature, Humidity, and Rainfall.": "तुमचे विशिष्ट मातीचे मेट्रिक्स प्रविष्ट करा: नायट्रोजन (एन), फॉस्फरस (पी), पोटॅशियम (के), पीएच पातळी आणि तापमान, आद्रता आणि पाऊस यांसारखे पर्यावरणीय घटक.",
    "Data Processing": "डेटा प्रोसेसिंग",
    "Your information is securely transmitted to our backend API where it is normalized and prepared for analysis using specialized agricultural algorithms.": "तुमची माहिती सुरक्षितपणे आमच्या बॅकएंड एपीआय कडे पाठवली जाते जिथे ती विशेष कृषी अल्गोरिदम वापरून विश्लेषणासाठी तयार केली जाते.",
    "Machine Learning": "मशीन लर्निंग",
    "Our pre-trained ML model cross-references your soil profile against thousands of successful harvest data points to find the optimal match.": "आमचे पूर्व-प्रशिक्षित एमएल मॉडेल इष्टतम जुळणी शोधण्यासाठी हजारो यशस्वी पीक डेटा पॉइंट्ससह तुमच्या माती प्रोफाइलचा संदर्भ घेते.",
    "Recommendation": "शिफारस",
    "Receive a ranked list of the top 3 crops most likely to thrive in your current environment, ensuring maximum yield and resource efficiency.": "तुमच्या सध्याच्या वातावरणात वाढण्याची सर्वाधिक शक्यता असलेल्या टॉप 3 पिकांची रँक केलेली यादी मिळवा, ज्यामुळे जास्तीत जास्त उत्पन्न आणि संसाधन कार्यक्षमता सुनिश्चित होईल.",
    "Important Note: The accuracy of the recommendation depends on correct input values. Precision in soil testing leads to precision in results.": "महत्वाची टीप: शिफारसीची अचूकता योग्य इनपुट मूल्यांवर अवलंबून असते. माती परीक्षणातील अचूकता निकालांमध्ये अचूकता आणते.",
    "Resources": "संसाधन",
    "Where to get your data.": "तुमचा डेटा कोठून मिळवायचा.",
    "Access reliable testing facilities to ensure your input data is scientifically verified.": "तुमचा इनपुट डेटा वैज्ञानिकदृष्ट्या सत्यापित आहे याची खात्री करण्यासाठी विश्वसनीय चाचणी सुविधांमध्ये प्रवेश करा.",
    "Soil Testing Laboratories": "माती परीक्षण प्रयोगशाळा",
    "Professional labs provide detailed chemical analysis of N, P, K levels and pH concentration.": "व्यावसायिक प्रयोगशाळा एन, पी, के पातळी आणि पीएच एकाग्रतेचे तपशीलवार रासायनिक विश्लेषण प्रदान करतात.",
    "Agriculture Centers": "कृषी केंद्रे",
    "Government-led centers often provide subsidized or free basic soil testing kits and reports.": "शासकीय नेतृत्वाखालील केंद्रे अनेकदा अनुदानित किंवा विनामूल्य मूलभूत माती परीक्षण किट आणि अहवाल प्रदान करतात.",
    "IoT Soil Sensors": "IoT माती सेन्सर्स",
    "Real-time smart devices can be installed in your fields for continuous monitoring of moisture and nutrients.": "ओलावा आणि पोषक तत्वांच्या सतत निरीक्षणासाठी तुमच्या शेतात रीयल-टाइम स्मार्ट उपकरणे बसवता येतात.",
    "Predictive Cultivation.": "भविष्यसूचक लागवड.",
    "Input your soil and environmental parameters to identify the most suitable crops for your specific terrain.": "तुमच्या विशिष्ट भूप्रदेशासाठी सर्वात योग्य पिके ओळखण्यासाठी तुमची माती आणि पर्यावरणीय मापदंड प्रविष्ट करा.",
    "Nitrogen (N)": "नायट्रोजन (एन)",
    "Enter N ratio": "एन प्रमाण प्रविष्ट करा",
    "mg/kg": "मिलीग्राम/किलो",
    "Phosphorus (P)": "फॉस्फरस (पी)",
    "Enter P ratio": "पी प्रमाण प्रविष्ट करा",
    "Potassium (K)": "पोटॅशियम (के)",
    "Enter K ratio": "के प्रमाण प्रविष्ट करा",
    "Soil pH": "मातीचा पीएच",
    "Enter pH level": "पीएच पातळी प्रविष्ट करा",
    "pH scale (0-14)": "पीएच स्केल (0-14)",
    "Temperature": "तापमान",
    "Enter degrees": "डिग्री प्रविष्ट करा",
    "°C": "°C",
    "Humidity": "आद्रता",
    "Enter humidity": "आद्रता प्रविष्ट करा",
    "Rainfall": "पाऊस",
    "Annual average": "वार्षिक सरासरी",
    "Top 3 Recommended Crops": "शिफारस केलेली टॉप 3 पिके",
    "Primary Recommendation": "प्राथमिक शिफारस",
    "Secondary Match": "दुय्यम जुळणी",
    "Tertiary Alternative": "तृतीयक पर्याय",
    "Rice": "तांदूळ",
    "Wheat": "गहू",
    "Cotton": "कापूस",
    "Maize": "मका",
    "Jute": "जूट",
    "Coffee": "कॉफी",
    "Tea": "चहा",
    "Rubber": "रबर",
    "Coconut": "नारळ",
    "Sugarcane": "ऊस",
    "Tobacco": "तंबाखू",
    "Groundnut": "भुईमूग",
    "Soybean": "सोयाबीन",
    "Mustard": "मोहरी",
    "Sunflower": "सूर्यफूल",
    "Optimal Match": "इष्टतम जुळणी",
    "High Viability": "उच्च व्यवहार्यता",
    "Strong Potential": "मजबूत क्षमता",
    "Suitable": "योग्य",
    "Recommended": "शिफारस केलेले",
    "Similar Region": "समान क्षेत्र",
    "Suitable Soil": "उपयुक्त माती",
    "Recommended Fertilizer": "शिफारस केलेले खत",
    "Based on similar agricultural conditions from real dataset": "वास्तविक डेटासेटमधील समान कृषी स्थितींवर आधारित",
    "Nearby Kendras": "नजीकची केंद्रे",
    "Find Nearby Agriculture Kendras": "नजीकची कृषी केंद्रे शोधा",
    "Locate government centers and resources near you": "तुमच्या जवळील सरकारी केंद्रे आणि संसाधने शोधा",
    "Maharashtra · ICAR Official Network": "महाराष्ट्र · आयसीएआर अधिकृत नेटवर्क",
    "Krishi Vigyan Kendras": "कृषि विज्ञान केंद्रे",
    "Find official government agricultural centres near you. Every KVK provides soil testing, expert guidance, and free farmer consultation.": "तुमच्या जवळील अधिकृत सरकारी कृषी केंद्रे शोधा. प्रत्येक केव्हीके माती परीक्षण, तज्ञ मार्गदर्शन आणि विनामूल्य शेतकरी सल्ला प्रदान करते.",
    "🏛️ 49 KVKs across Maharashtra": "🏛️ महाराष्ट्रभर ४९ केव्हीके",
    "🧪 Soil Testing at every KVK": "🧪 प्रत्येक केव्हीकेमध्ये माती परीक्षण",
    "💰 ₹100–₹200 per sample": "💰 ₹१००–₹२०० प्रति नमुना",
    "🆓 Free expert consultation": "🆓 विनामूल्य तज्ञ सल्ला",
    "Soil Testing Available at Every KVK — ₹100 to ₹200 per sample": "प्रत्येक केव्हीकेमध्ये माती परीक्षण उपलब्ध — ₹१०० ते ₹२०० प्रति नमुना",
    "Tests: pH · Nitrogen · Phosphorus · Potassium · Organic Carbon · Micronutrients · Results in 3–7 days": "चाचण्या: पीएच · नायट्रोजन · फॉस्फरस · पोटॅशियम · सेंद्रिय कार्बन · सूक्ष्म पोषक घटक · निकाल ३-७ दिवसांत",
    "Filter:": "फिल्टर:",
    "All Regions": "सर्व क्षेत्रे",
    "Western MH": "पश्चिम महाराष्ट्र",
    "Marathwada": "मराठवाडा",
    "Vidarbha": "विदर्भ",
    "Konkan": "कोकण",
    "North MH": "उत्तर महाराष्ट्र",
    "Find Nearest KVK": "नजीकचे केव्हीके शोधा",
    "Locating...": "शोधत आहे...",
    "Showing": "दाखवत आहे",
    "Kendras": "केंद्रे",
    "KVK": "केव्हीके",
    " District": " जिल्हा",
    "🧪 Soil Testing": "🧪 माती परीक्षण",
    "Mobile Lab": "मोबाईल लॅब",
    "💬 Free Consultation": "💬 विनामूल्य सल्ला",
    "Maps": "नकाशे",
    "You": "तुम्ही",
    "ICAR · Krishi Vigyan Kendra": "आयसीएआर · कृषि विज्ञान केंद्र",
    "📍": "📍",
    "Soil Testing Available": "माती परीक्षण उपलब्ध",
    "Cost:": "किंमत:",
    " per sample": " प्रति नमुना",
    "Tests:": "चाचण्या:",
    "Mobile Lab — visits your farm": "मोबाईल लॅब — तुमच्या शेताला भेट देते",
    "from your location": "तुमच्या स्थानापासून",
    "Directions": "दिशा",
    "KVK (Official ICAR)": "केव्हीके (अधिकृत आयसीएआर)",
    "KVK with Mobile Soil Lab": "मोबाईल सॉईल लॅबसह केव्हीके",
    "Your Location": "तुमचे स्थान"
  }
};

// Cache to store dynamic translations and avoid redundant API calls
const dynamicTranslationCache: Record<string, Record<string, string>> = {
  en: {},
  hi: {},
  mr: {},
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    return (localStorage.getItem('app-language') as Language) || 'en';
  });
  const [loading, setLoading] = useState(false);
  const [dynamicTranslations, setDynamicTranslations] = useState<Record<string, string>>({});

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('app-language', lang);
  };

  const t = useCallback((text: string) => {
    if (language === 'en') return text;
    // Check static dictionary first (instant)
    if (staticTranslations[language][text]) return staticTranslations[language][text];
    // Check dynamic cache second
    return dynamicTranslations[text] || dynamicTranslationCache[language][text] || text;
  }, [language, dynamicTranslations]);

  useEffect(() => {
    if (language === 'en') {
      setDynamicTranslations({});
      return;
    }
    setDynamicTranslations({ ...dynamicTranslationCache[language] });
  }, [language]);

  // Helper to translate a single string
  const translateText = async (text: string, targetLanguage: string): Promise<string | null> => {
    const tl = targetLanguage === 'hi' ? 'hi' : 'mr';
    // Supported approach: Proxy through backend or use official GCP API.
    // For now, keeping the current provider but wrapping it for reliability.
    try {
      const res = await fetch(
        `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=${tl}&dt=t&q=${encodeURIComponent(text)}`
      );
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      if (data && data[0]) {
        return data[0].map((item: any) => item[0]).join("");
      }
    } catch (e) {
      console.error(`Translation error for "${text.substring(0, 20)}...":`, e);
    }
    return null;
  };

  const translateBatch = async (texts: string[]) => {
    if (language === 'en' || texts.length === 0) return;

    const missingTexts = texts.filter(t => 
      !staticTranslations[language][t] && !dynamicTranslationCache[language][t]
    );
    
    if (missingTexts.length === 0) return;

    setLoading(true);
    try {
      const result: Record<string, string> = {};
      
      // Concurrency limiting: process in batches of 5
      const BATCH_SIZE = 5;
      for (let i = 0; i < missingTexts.length; i += BATCH_SIZE) {
        const batch = missingTexts.slice(i, i + BATCH_SIZE);
        await Promise.all(
          batch.map(async (textToTranslate) => {
            const translated = await translateText(textToTranslate, language);
            if (translated) {
              result[textToTranslate] = translated;
            }
          })
        );
      }

      Object.assign(dynamicTranslationCache[language], result);
      setDynamicTranslations(prev => ({ ...prev, ...result }));
    } catch (error) {
      console.error("Batch translation error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, translateBatch, loading }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useTranslation = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};
