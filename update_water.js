const cropWaterData = {
rice: { water: "High", water_mm: "1200 - 2500 mm per season", note: "Needs standing water in fields" },
maize: { water: "Medium", water_mm: "500 - 800 mm per season", note: "Needs more water during flowering stage" },
chickpea: { water: "Low", water_mm: "300 - 500 mm per season", note: "Grows well with low rainfall" },
kidneybeans: { water: "Medium", water_mm: "400 - 700 mm per season", note: "Needs moderate irrigation" },
pigeonpeas: { water: "Low", water_mm: "600 - 1000 mm per season", note: "Drought tolerant crop" },
mothbeans: { water: "Low", water_mm: "200 - 400 mm per season", note: "Best for dry regions" },
mungbean: { water: "Low", water_mm: "300 - 500 mm per season", note: "Short duration crop" },
blackgram: { water: "Low", water_mm: "300 - 500 mm per season", note: "Needs less irrigation" },
lentil: { water: "Low", water_mm: "250 - 450 mm per season", note: "Grows in dry winter" },
pomegranate: { water: "Low", water_mm: "400 - 700 mm per season", note: "Tolerates dry climate" },
banana: { water: "High", water_mm: "1200 - 2200 mm per season", note: "Needs continuous irrigation" },
mango: { water: "Medium", water_mm: "750 - 1200 mm per season", note: "Needs water during flowering" },
grapes: { water: "Medium", water_mm: "500 - 900 mm per season", note: "Requires controlled irrigation" },
watermelon: { water: "Medium", water_mm: "400 - 600 mm per season", note: "Needs water during fruit stage" },
muskmelon: { water: "Medium", water_mm: "350 - 600 mm per season", note: "Sensitive to overwatering" },
apple: { water: "Medium", water_mm: "800 - 1200 mm per season", note: "Requires seasonal irrigation" },
orange: { water: "Medium", water_mm: "900 - 1200 mm per season", note: "Needs irrigation in dry periods" },
papaya: { water: "Medium", water_mm: "1000 - 1500 mm per season", note: "Needs consistent moisture" },
coconut: { water: "High", water_mm: "1500 - 2500 mm per season", note: "Needs high rainfall or irrigation" },
cotton: { water: "Medium", water_mm: "700 - 1300 mm per season", note: "Sensitive to excess water" },
jute: { water: "High", water_mm: "1500 - 2000 mm per season", note: "Needs heavy rainfall" },
coffee: { water: "Medium", water_mm: "1200 - 1800 mm per season", note: "Needs rainfall + shade" }
};

const fs = require('fs');
const path = require('path');

const cropDataPath = path.join(__dirname, 'frontend', 'src', 'data', 'cropData.ts');
let content = fs.readFileSync(cropDataPath, 'utf8');

let newContent = content.replace(/export interface CropInfo \{([\s\S]*?)\}/, (match, body) => {
    if (!body.includes('water_mm')) {
        body = body.replace(/  why: string;/g, "  water_mm: string;\n  note: string;\n  why: string;");
    }
    return 'export interface CropInfo {' + body + '}';
});

for (const [key, data] of Object.entries(cropWaterData)) {
    const regex = new RegExp("  " + key + ": \\{[\\s\\S]*?\\n  \\},", "g");
    newContent = newContent.replace(regex, (block) => {
        let res = block.replace(/water: ".*?",/g, 'water: "' + data.water + '",');
        if (!res.includes('water_mm')) {
            res = res.replace(/why:/, 'water_mm: "' + data.water_mm + '",\n    note: "' + data.note + '",\n    why:');
        }
        return res;
    });
}

newContent = newContent.replace(/  sugarcane: \{([\s\S]*?)\n  \},/g, (match, block) => {
    if (!block.includes('water_mm')) {
        block = block.replace(/why:/, 'water_mm: "1500 - 2000 mm per season",\n    note: "Needs regular watering.",\n    why:');
    }
    return "  sugarcane: {" + block + "\n  },";
});

newContent = newContent.replace(/  cucumber: \{([\s\S]*?)\n  \},/g, (match, block) => {
    if (!block.includes('water_mm')) {
        block = block.replace(/why:/, 'water_mm: "400 - 600 mm per season",\n    note: "Consistent moisture required.",\n    why:');
    }
    return "  cucumber: {" + block + "\n  },";
});

fs.writeFileSync(cropDataPath, newContent);
console.log("Updated water fields in cropData.ts!");
