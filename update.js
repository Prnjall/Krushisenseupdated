const fs = require('fs');
const path = require('path');
const userData = require('./user_data.js');

const cropDataPath = path.join(__dirname, 'frontend', 'src', 'data', 'cropData.ts');
let content = fs.readFileSync(cropDataPath, 'utf8');

// Also process sugarcane and cucumber to fill their 'why'
if (!userData.sugarcane) {
    userData.sugarcane = {
        name: "Sugarcane",
        description: "Sugarcane is a tall, perennial grass used primarily for sugar production.",
        season: "Year-Round",
        temperature: "20°C - 35°C",
        soil: "Loamy / Well-drained",
        climate: "Tropical & Subtropical",
        water: "High",
        why: "Requires consistent irrigation throughout its long growing season."
    };
}
if (!userData.cucumber) {
    userData.cucumber = {
        name: "Cucumber",
        description: "Cucumber is a widely-cultivated creeping vine plant that bears usually cylindrical fruits.",
        season: "Zaid (Summer)",
        temperature: "20°C - 30°C",
        soil: "Sandy Loam",
        climate: "Tropical & Warm Temperate",
        water: "Medium",
        why: "Requires moderate, frequent watering. Susceptible to water stress."
    };
}

let resultStr = `export interface CropInfo {
  name: string;
  scientificName: string;
  category: string;
  season: string;
  seasonDescription: string;
  description: string;
  temperature: string;
  soil: string;
  climate: string;
  water: string;
  waterDescription: string;
  why: string;
  image: string;
}

export const cropData: Record<string, CropInfo> = {\n`;

// Parse existing with a basic regex to grab category, scientificName, etc
// We'll just define the dummy fields directly since we don't really want to parse typescript safely in JS without ts-node/acorn.
// Wait, I can just hardcode the ones that matter or use a simple hack.
// Actually, it's easier to just build the object and JSON stringify, then fix formatting.

const existingCrops = [
 "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans", "mungbean", "blackgram", "lentil", "pomegranate", "banana", "mango", "grapes", "watermelon", "muskmelon", "apple", "orange", "papaya", "coconut", "cotton", "jute", "coffee", "sugarcane", "cucumber"
];

const sciNames = {
rice: "Oryza sativa", maize: "Zea mays", chickpea: "Cicer arietinum", kidneybeans: "Phaseolus vulgaris", pigeonpeas: "Cajanus cajan", mothbeans: "Vigna aconitifolia", mungbean: "Vigna radiata", blackgram: "Vigna mungo", lentil: "Lens culinaris", pomegranate: "Punica granatum", banana: "Musa acuminata", mango: "Mangifera indica", grapes: "Vitis vinifera", watermelon: "Citrullus lanatus", muskmelon: "Cucumis melo", apple: "Malus domestica", orange: "Citrus sinensis", papaya: "Carica papaya", coconut: "Cocos nucifera", cotton: "Gossypium hirsutum", jute: "Corchorus capsularis", coffee: "Coffea arabica", sugarcane: "Saccharum officinarum", cucumber: "Cucumis sativus"
};

const cats = {
rice: "Staple Cereal", maize: "Cereal Grain", chickpea: "Pulse / Legume", kidneybeans: "Pulse / Legume", pigeonpeas: "Pulse / Legume", mothbeans: "Pulse / Legume", mungbean: "Pulse / Legume", blackgram: "Pulse / Legume", lentil: "Pulse / Legume", pomegranate: "Fruit", banana: "Fruit", mango: "Fruit", grapes: "Fruit", watermelon: "Fruit", muskmelon: "Fruit", apple: "Fruit", orange: "Fruit", papaya: "Fruit", coconut: "Plantation Crop", cotton: "Fiber Crop", jute: "Fiber Crop", coffee: "Plantation Crop", sugarcane: "Cash Crop", cucumber: "Vegetable"
};

for (const key of existingCrops) {
  const d = userData[key];
  resultStr += `  ${key}: {
    name: ${JSON.stringify(d.name)},
    scientificName: ${JSON.stringify(sciNames[key])},
    category: ${JSON.stringify(cats[key])},
    season: ${JSON.stringify(d.season)},
    seasonDescription: "Typical season requirements.",
    description: ${JSON.stringify(d.description)},
    temperature: ${JSON.stringify(d.temperature)},
    soil: ${JSON.stringify(d.soil)},
    climate: ${JSON.stringify(d.climate)},
    water: ${JSON.stringify(d.water)},
      waterDescription: ${JSON.stringify("Water level is " + d.water)},
    why: ${JSON.stringify(d.why)},
    image: "/images/crops/${key}.jpg",
  },\n`;
}

resultStr += `};

export function getCropBySlug(slug: string): CropInfo | undefined {
  return cropData[slug.toLowerCase()];
}

export function getAllCropSlugs(): string[] {
  return Object.keys(cropData);
}
`;

fs.writeFileSync(cropDataPath, resultStr);
console.log("Updated cropData.ts");
