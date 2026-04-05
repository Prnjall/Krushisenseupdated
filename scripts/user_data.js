const cropData = {
rice: {
name: "Rice",
description: "Rice is a staple cereal crop grown in warm and humid regions. It requires standing water during most of its growth period and is widely cultivated during monsoon season.",
season: "Kharif",
temperature: "20°C - 35°C",
soil: "Clayey / Loamy",
climate: "Tropical, Humid",
water: "High",
why: "Suitable for high humidity, high rainfall and water-retentive soil"
},
maize: {
name: "Maize",
description: "Maize is a versatile cereal crop grown in warm climates. It grows rapidly and adapts well to different soil conditions with proper nutrients.",
season: "Kharif / Rabi",
temperature: "18°C - 30°C",
soil: "Well-drained Loamy",
climate: "Subtropical / Warm",
water: "Medium",
why: "Performs well in moderate rainfall and warm conditions"
},
chickpea: {
name: "Chickpea",
description: "Chickpea is a protein-rich pulse crop grown in dry and cool climates. It requires less water and grows well in winter season.",
season: "Rabi",
temperature: "20°C - 25°C",
soil: "Sandy Loam / Loam",
climate: "Cool and Dry",
water: "Low",
why: "Best for low moisture and cooler conditions"
},
kidneybeans: {
name: "Kidney Beans",
description: "Kidney beans are leguminous crops that grow well in moderate climates with well-drained soil.",
season: "Rabi",
temperature: "15°C - 25°C",
soil: "Loamy",
climate: "Mild / Cool",
water: "Medium",
why: "Requires moderate temperature and soil moisture"
},
pigeonpeas: {
name: "Pigeon Peas",
description: "Pigeon peas are drought-resistant legumes grown in tropical regions with moderate rainfall.",
season: "Kharif",
temperature: "25°C - 35°C",
soil: "Sandy Loam",
climate: "Tropical",
water: "Low",
why: "Suitable for dry regions and low rainfall"
},
mothbeans: {
name: "Moth Beans",
description: "Moth beans are hardy pulse crops that can survive in arid and semi-arid climates.",
season: "Kharif",
temperature: "25°C - 35°C",
soil: "Sandy",
climate: "Arid / Semi-arid",
water: "Low",
why: "Thrives in dry and drought-prone areas"
},
mungbean: {
name: "Mung Bean",
description: "Mung bean is a short-duration pulse crop grown in warm climates with moderate rainfall.",
season: "Kharif / Zaid",
temperature: "25°C - 35°C",
soil: "Loamy",
climate: "Warm",
water: "Low",
why: "Suitable for warm climate with low water requirement"
},
blackgram: {
name: "Blackgram",
description: "Blackgram is a pulse crop grown in hot and humid climates and is widely used in Indian agriculture.",
season: "Kharif",
temperature: "25°C - 35°C",
soil: "Clay Loam",
climate: "Hot and Humid",
water: "Low",
why: "Performs well in humid climate with moderate soil fertility"
},
lentil: {
name: "Lentil",
description: "Lentil is a winter pulse crop grown in cool and dry climates with minimal water requirement.",
season: "Rabi",
temperature: "18°C - 25°C",
soil: "Loamy",
climate: "Cool",
water: "Low",
why: "Suitable for cold climate and low moisture soil"
},
pomegranate: {
name: "Pomegranate",
description: "Pomegranate is a fruit crop grown in dry climates and requires well-drained soil.",
season: "Perennial",
temperature: "25°C - 35°C",
soil: "Loamy / Sandy",
climate: "Dry / Semi-arid",
water: "Low",
why: "Thrives in dry conditions with low humidity"
},
banana: {
name: "Banana",
description: "Banana is a tropical fruit crop that requires high temperature and high humidity.",
season: "Year-round",
temperature: "25°C - 35°C",
soil: "Loamy",
climate: "Tropical",
water: "High",
why: "Requires continuous moisture and warm climate"
},
mango: {
name: "Mango",
description: "Mango is a tropical fruit crop grown in warm regions with moderate rainfall.",
season: "Perennial",
temperature: "24°C - 30°C",
soil: "Well-drained Loamy",
climate: "Tropical",
water: "Medium",
why: "Needs warm climate with seasonal rainfall"
},
grapes: {
name: "Grapes",
description: "Grapes are fruit crops grown in warm climates with dry conditions during ripening.",
season: "Perennial",
temperature: "15°C - 30°C",
soil: "Sandy Loam",
climate: "Temperate",
water: "Medium",
why: "Requires controlled irrigation and dry climate"
},
watermelon: {
name: "Watermelon",
description: "Watermelon is a summer fruit crop that grows well in hot climates with sandy soil.",
season: "Zaid",
temperature: "25°C - 35°C",
soil: "Sandy",
climate: "Warm",
water: "Medium",
why: "Requires warm temperature and moderate irrigation"
},
muskmelon: {
name: "Muskmelon",
description: "Muskmelon is a summer fruit crop that requires warm temperature and low humidity.",
season: "Zaid",
temperature: "25°C - 35°C",
soil: "Sandy Loam",
climate: "Warm",
water: "Medium",
why: "Best for warm climate with low humidity"
},
apple: {
name: "Apple",
description: "Apple is a temperate fruit crop grown in cool climates and requires chilling conditions.",
season: "Perennial",
temperature: "10°C - 25°C",
soil: "Loamy",
climate: "Temperate",
water: "Medium",
why: "Needs cold climate for proper growth"
},
orange: {
name: "Orange",
description: "Orange is a citrus fruit crop grown in subtropical climates with moderate rainfall.",
season: "Perennial",
temperature: "20°C - 30°C",
soil: "Sandy Loam",
climate: "Subtropical",
water: "Medium",
why: "Performs well in moderate temperature and rainfall"
},
papaya: {
name: "Papaya",
description: "Papaya is a tropical fruit crop that grows quickly in warm climates.",
season: "Year-round",
temperature: "25°C - 35°C",
soil: "Loamy",
climate: "Tropical",
water: "Medium",
why: "Needs warm climate with good drainage"
},
coconut: {
name: "Coconut",
description: "Coconut is a tropical crop grown in coastal regions with high humidity.",
season: "Perennial",
temperature: "25°C - 35°C",
soil: "Sandy / Coastal",
climate: "Tropical Humid",
water: "High",
why: "Requires high humidity and rainfall"
},
cotton: {
name: "Cotton",
description: "Cotton is a fiber crop grown in warm climates with moderate rainfall.",
season: "Kharif",
temperature: "21°C - 30°C",
soil: "Black Soil",
climate: "Warm",
water: "Medium",
why: "Requires warm climate and moderate irrigation"
},
jute: {
name: "Jute",
description: "Jute is a fiber crop grown in warm and humid climates with high rainfall.",
season: "Kharif",
temperature: "24°C - 35°C",
soil: "Alluvial",
climate: "Humid",
water: "High",
why: "Needs heavy rainfall and humidity"
},
coffee: {
name: "Coffee",
description: "Coffee is a plantation crop grown in tropical highland climates with shade.",
season: "Perennial",
temperature: "18°C - 28°C",
soil: "Loamy",
climate: "Tropical Highland",
water: "Medium",
why: "Requires moderate rainfall and shaded conditions"
}
};

module.exports = cropData;
