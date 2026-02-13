
# Hardcoded data for the crop dictionary (Presentation Version)

crops_data = [
    {
        "id": 1,
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Wheat",
        "overview": "Wheat is the second most important cereal crop in India after rice. It is the main food staple in north and north-western India. India is the second-largest producer of wheat globally.",
        "header_image": "dictionary/crop_headers/wheat-cultivation-india.webp",
        "family": "Poaceae (Gramineae)",
        "varieties": "HD 2967, PBW 343, DBW 17, WH 542. Durum wheat (macaroni wheat) is also grown in some parts.",
        "growth_habit": "Annual grass, 0.6 to 1.5 meters tall",
        "pollination": "Self-pollinated",
        
        "soil_ph": "6.0 - 7.5",
        "soil_type": "Well-drained clay loam or loam texture",
        "climatic_req": "Cool and moist climate during growth (10-15°C) and warm dry climate during grain formation (21-26°C). Rainfall: 750-1000mm.",
        "sowing_window": "Rabi Season: Nov 1 - Nov 15 (Timely), up to Dec 15 (Late)",
        "seed_rate_spacing": "100 kg/ha (Timely), 125 kg/ha (Late). Spacing: 22.5 cm between rows.",
        "water_req": "4-6 irrigations at critical stages: CRI (21 DAS), Tillering, Jointing, Flowering, Milking, Dough.",
        
        "fertilizer_schedule": "NPK 120:60:40 kg/ha. Apply half N and full P & K as basal. Remaining N at 1st irrigation.",
        "micronutrients": "Zinc deficiency is common (Khaira disease). Apply 25 kg/ha Zinc Sulphate.",
        "crop_rotation": "Rice-Wheat, Cotton-Wheat, Maize-Wheat, Sorghum-Wheat",
        
        "major_pests": "Termites, Aphids, Armyworm, Brown Mite",
        "weed_control": "Phalaris minor (Gulli danda) is major weed. Use Sulfosulfuron or Clodinafop 30-35 DAS.",
        "ipm_practices": "Use varying sowing dates, resistant varieties, and biological control agents like Ladybird beetles for aphids.",
        
        "maturity_signs": "Straw turns yellow and becomes brittle. Grain becomes hard and contains 20-25% moisture.",
        "harvesting_method": "Manual using sickles or mechanical using Combine Harvesters.",
        "yield_expectations": "3.5 - 5.5 tonnes/ha",
        "storage_req": "Store in metallic bins or gunny bags. Grain moisture should be < 12%. maintain < 25°C.",
        "processing_value": "Flour (Atta), Maida, Semolina (Suji), Bakery products, Pasta.",
        
        "sowing_season": "Rabi (Winter)",
        "harvesting_season": "March - April",
        "growth_duration": "120 - 140 days",
        "average_price": "₹2125 - ₹2400 / quintal",
        "diseases": [
            {
                "name": "Brown Rust (Leaf Rust)",
                "symptoms": "Small, round to oval brown pustules on leaf blades. Pustules burst to release reddish-brown spores.",
                "medicine_protection": "Grow resistant varieties like HD 2967.",
                "medicine_cure": "Spray Propiconazole (Tilt) 25 EC @ 0.1%.",
                "image":"dictionary/disease_images/brown-rust-wheat-a1-cl-lib.webp"
            },
            {
                "name": "Yellow Rust (Stripe Rust)",
                "symptoms": "Yellow pustules arranged in linear stripes on leaves. Severe in NW India.",
                "medicine_protection": "Monitor crop regularly.",
                "medicine_cure": "Spray Tebuconazole or Triadimefon @ 0.1%."
            }
        ]
    },
    {
        "id": 2,
        "name": "Rice (Paddy)",
        "scientific_name": "Oryza sativa",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Rice",
        "overview": "Rice is the staple food for more than 60% of the world's population. It is a semi-aquatic plant and thrives in high humidity and water.",
        "header_image": "dictionary/crop_headers/paddy.jpg",
        "family": "Poaceae",
        "varieties": "Basmati (Pusa Basmati 1121, 1509), Non-Basmati (IR 64, Swarna, MTU 7029).",
        "growth_habit": "Annual grass, semi-aquatic",
        "pollination": "Self-pollinated",
        
        "soil_ph": "5.5 - 6.5 (slightly acidic)",
        "soil_type": "Clay or clay-loam offering low permeability and water retention.",
        "climatic_req": "Hot and humid. Temp: 20-37°C. Rainfall: > 1000mm.",
        "sowing_window": "Kharif: June-July (Transplanting), Rabi: Dec-Jan",
        "seed_rate_spacing": "Transplanting: 20-30 kg/ha (Nursery). Spacing: 20x10 cm or 20x15 cm.",
        "water_req": "Needs standing water (2-5 cm) from transplanting to dough stage. Highly water-intensive.",
        
        "fertilizer_schedule": "NPK 100:50:50 kg/ha. N in 3 splits (Basal, Tillering, Panicle Initiation).",
        "micronutrients": "Zinc deficiency causes 'Khaira' disease (rusty brown spots). Apply Zinc Sulphate.",
        "crop_rotation": "Rice-Wheat, Rice-Pulses, Rice-Mustard",
        
        "major_pests": "Stem Borer, Brown Plant Hopper (BPH), Leaf Folder, Gundhi Bug",
        "weed_control": "Pre-emergence: Pretilachlor or Butachlor within 3 days of transplanting.",
        "ipm_practices": "Light traps for stem borer. Alleyways (skipping rows) for BPH management.",
        
        "maturity_signs": "80% of panicles turn straw-colored. Grain is hard and clear.",
        "harvesting_method": "Manual cutting near base or Combined Harvester.",
        "yield_expectations": "3 - 6 tonnes/ha (highly variable by variety)",
        "storage_req": "Dry to 14% moisture. Protected from rodents and moisture in silos.",
        "processing_value": "Milled rice, Rice bran oil, Flaked rice (Poha), Puffed rice.",
        
        "sowing_season": "Kharif (Monsoon)",
        "harvesting_season": "Oct - Nov",
        "growth_duration": "100 - 150 days",
        "average_price": "₹2183 - ₹4000 (Basmati higher) / quintal",
        "diseases": [
            {
                "name": "Blast",
                "symptoms": "Spindle-shaped spots with white centre and brown margin. Can break neck of panicle.",
                "medicine_protection": "Avoid excess Nitrogen.",
                "medicine_cure": "Spray Tricyclazole 75 WP @ 0.6 g/L."
            },
                {
                "name": "Bacterial Leaf Blight",
                "symptoms": "Streaming yellow/white lesions along leaf margins. Bacterial ooze seen in morning.",
                "medicine_protection": "Use resistant varieties.",
                "medicine_cure": "Spray Streptocycline 15g + Copper Oxychloride 500g per ha."
            }
        ]
    },
    {
        "id": 3,
        "name": "Cotton",
        "scientific_name": "Gossypium hirsutum",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Cotton",
        "overview": "Cotton is the most important fibre crop of India ('White Gold'). It accounts for 65% of raw material for the textile industry.",
        "header_image": "dictionary/crop_headers/Cotton-plants-in-a-field.webp",
        "family": "Malvaceae",
        "varieties": "Bt Cotton hybrids (Bollgard II), H-4, MCU-5, Suvin.",
        "growth_habit": "Perennial shrub grown as an annual. 1-2m tall.",
        "pollination": "Often cross-pollinated",
        
        "soil_ph": "6.0 - 8.0",
        "soil_type": "Black cotton soils (Vertisols), Alluvial soils with good drainage.",
        "climatic_req": "Tropical/Sub-tropical. Min 16°C for germination. Frost-free season is essential.",
        "sowing_window": "North: April-May, Central: June-July (Monsoon onset)",
        "seed_rate_spacing": "Bt Cotton: 1.5 - 2.5 kg/ha. Spacing: 90x60 cm or wider.",
        "water_req": "Requires 700-1200mm water. Irrigation essential at flowering and boll development if no rain.",
        
        "fertilizer_schedule": "NPK 100:50:50 kg/ha. Foliar spray of MgSO4 and KNO3 benefits boll retention.",
        "micronutrients": "Magnesium deficiency causes reddening of leaves (Lalya). Boron helps boll set.",
        "crop_rotation": "Cotton-Sorghum, Cotton-Wheat, Cotton-Pulses",
        
        "major_pests": "Pink Bollworm, American Bollworm, Whitefly, Jassids, Thrips",
        "weed_control": "Inter-cultivation (hoeing). Pendimethalin pre-emergence.",
        "ipm_practices": "Pheromone traps for Bollworms. Yellow sticky traps for Whitefly. Refugial non-Bt crop.",
        
        "maturity_signs": "Bolls burst fully, lint is fluffy and dry. Leaves turn reddish/dry.",
        "harvesting_method": "Hand picking (multiple pickings as bolls burst).",
        "yield_expectations": "20 - 30 quintals/ha (Seed Cotton)",
        "storage_req": "Store in dry, clean godowns. Moisture < 8-9%.",
        "processing_value": "Lint for textiles, Cottonseed oil, Oil cake (cattle feed).",
        
        "sowing_season": "Kharif",
        "harvesting_season": "Oct - Feb",
        "growth_duration": "150 - 180 days",
        "average_price": "₹6620 - ₹7500 / quintal",
        "diseases": [
            {
                "name": "Fusarium Wilt",
                "symptoms": "Yellowing and drying of leaves. Vascular browning inside stem.",
                "medicine_protection": "Seed treatment with Trichoderma.",
                "medicine_cure": "Drenching with Carbendazim 2g/L.",
                "image": "dictionary/disease_images/fusarium_wilt_LJJFd17.webp"
            }
        ]
    },
    {
        "id": 4,
        "name": "Sugarcane",
        "scientific_name": "Saccharum officinarum",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Sugarcane",
        "overview": "Sugarcane is a long-duration tropical grass rich in sucrose. It is the primary source of sugar in India.",
        "header_image": "dictionary/crop_headers/sugar.webp",
        "family": "Poaceae",
        "varieties": "Co 0238, Co 86032, Co 11015.",
        "growth_habit": "Perennial grass, 2-6 meters tall, clump forming.",
        "pollination": "Cross-pollinated (rarely flowers in cultivation)",
        
        "soil_ph": "6.5 - 7.5",
        "soil_type": "Deep, well-drained loams or clay loams.",
        "climatic_req": "Hot and humid. 26-32°C. High rainfall or irrigation required.",
        "sowing_window": "Spring (Feb-Mar), Autumn (Oct), Adsali (July in Maharashtra).",
        "seed_rate_spacing": "3-bud setts: 35,000-40,000/ha. Spacing: 90-120 cm ridges.",
        "water_req": "1500-2500 mm. Frequent irrigation (every 10-15 days in summer).",
        
        "fertilizer_schedule": "NPK 250:100:100 kg/ha. Heavy N feeder. Apply 1/3 at planting, 1/3 at 45 days, 1/3 at 90 days.",
        "micronutrients": "Iron chlorosis (yellowing) in calcareous soils. Spray FeSO4.",
        "crop_rotation": "Sugarcane-Ratoon-Wheat, Sugarcane-Vegetables",
        
        "major_pests": "Early Shoot Borer, Top Borer, Pyrilla, White Grub",
        "weed_control": "Atrazine pre-emergence. Earthing up controls weeds.",
        "ipm_practices": "Release Trichogramma chilonis (egg parasitoid) for borer control.",
        
        "maturity_signs": "Leaves turn yellow. Cane produces metallic sound when tapped. Brix reading > 18%.",
        "harvesting_method": "Manual cutting with knives/machetes close to ground.",
        "yield_expectations": "70 - 100 tonnes/ha",
        "storage_req": "Crush within 24 hours of harvest to prevent sucrose inversion.",
        "processing_value": "Sugar, Jaggery (Gur), Molasses (Alcohol), Bagasse (Paper/Power).",
        
        "sowing_season": "Spring/Autumn",
        "harvesting_season": "Dec - March",
        "growth_duration": "10 - 14 months",
        "average_price": "₹315 - ₹340 / quintal (FRP)",
        "diseases": [
            {
                "name": "Red Rot",
                "symptoms": "Reddening of internal pith with white cross-bands. Alcoholic smell.",
                "medicine_protection": "Key threat. Use healthy setts/resistant varieties.",
                "medicine_cure": "No specific cure in standing crop. Remove clamps."
            }
        ]
    },
    {
        "id": 5,
        "name": "Maize (Corn)",
        "scientific_name": "Zea mays",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Maize",
        "overview": "Maize is widely cultivated throughout the world, and a greater weight of maize is produced each year than any other grain.",
        "header_image": "dictionary/crop_headers/sweetcorn.webp",
        "family": "Poaceae",
        "varieties": "Ganga Safed-2, Deccan-103, HQPM-1 (High Protein).",
        "growth_habit": "Annual grass, stout, erect, solid stem.",
        "pollination": "Cross-pollinated (Wind)",
        
        "soil_ph": "5.5 - 7.5",
        "soil_type": "Well-drained sandy loam to silty loam. Intolerant to waterlogging.",
        "climatic_req": "Warm weather. 21-27°C. Frost damages the crop.",
        "sowing_window": "Kharif: June-July, Rabi: Oct-Nov, Spring: Feb",
        "seed_rate_spacing": "15-20 kg/ha. Spacing: 60x20 cm. ",
        "water_req": "500-600mm. Critical stages: Tasseling and Silking. Avoid water stress.",
        
        "fertilizer_schedule": "NPK 120:60:40 kg/ha. Responsive to high N.",
        "micronutrients": "Zinc deficiency causes 'White Bud'. Apply ZnSO4.",
        "crop_rotation": "Maize-Mustard, Maize-Chickpea, Maize-Wheat",
        
        "major_pests": "Stem Borer (Chilo partellus), Fall Armyworm (FAW - major recent threat).",
        "weed_control": "Atrazine 1-2 days after sowing.",
        "ipm_practices": "For FAW: Pheromone traps, parasitic wasps, Neem oil spray.",
        
        "maturity_signs": "Husk turns yellow/dry. Grain is hard. Black layer forms at grain base.",
        "harvesting_method": "Manual picking of cobs or Mechanical Corn Picker.",
        "yield_expectations": "3 - 5 tonnes/ha",
        "storage_req": "Dry to 10-12% moisture to prevent aflatoxin.",
        "processing_value": "Corn starch, Corn oil, Ethanol, Animal feed, Popcorn.",
        
        "sowing_season": "Kharif/Rabi",
        "harvesting_season": "Sep-Oct / Mar-Apr",
        "growth_duration": "90 - 110 days",
        "average_price": "₹2090 - ₹2250 / quintal",
        "diseases": [
            {
                "name": "Turcicum Leaf Blight",
                "symptoms": "Long, elliptical, greyish-green lesions on leaves.",
                "medicine_protection": "Resistant hybrids.",
                "medicine_cure": "Spray Mancozeb 75 WP @ 2g/L."
            }
        ]
    },
    {
        "id": 6,
        "name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Potato",
        "overview": "Potato is the world's fourth-largest food crop. It is a tuber crop rich in starch.",
        "header_image": "dictionary/crop_headers/potato.webp",
        "family": "Solanaceae",
        "varieties": "Kufri Jyoti, Kufri Chandramukhi, Kufri Lauvkar.",
        "growth_habit": "Herbaceous perennial grown as annual.",
        "pollination": "Self-pollinated (mostly propagated vegetatively)",
        
        "soil_ph": "5.0 - 6.5 (Slightly acidic prevents scab)",
        "soil_type": "Sandy loam rich in organic matter. Loose soil needed for tuber expansion.",
        "climatic_req": "Cool season crop. Tuberization best at 20°C day / 14°C night.",
        "sowing_window": "Plains: Oct-Nov. Hills: Mar-Apr.",
        "seed_rate_spacing": "15-20 quintals/ha (tubers). Spacing: 60x20 cm.",
        "water_req": "Frequent light irrigations. Dry period required before harvest for skin hardening.",
        
        "fertilizer_schedule": "NPK 150:80:100 kg/ha. High Potash requirement.",
        "micronutrients": "Boron helps in tuber quality.",
        "crop_rotation": "Maize-Potato-Wheat, Green manure-Potato",
        
        "major_pests": "Aphids (virus vector), Potato Tuber Moth, Cutworms.",
        "weed_control": "Metribuzin pre-emergence. Earthing up controls weeds.",
        "ipm_practices": "Yellow sticky traps for Aphids. Dehaulming (cutting tops) to stop virus reach tubers.",
        
        "maturity_signs": "Vines turn yellow and dry up. Skin of tuber doesn't peel on rubbing.",
        "harvesting_method": "Digging with fork or Potato Digger machine. Care to avoid cuts.",
        "yield_expectations": "20 - 30 tonnes/ha",
        "storage_req": "Cold storage (2-4°C) for long term. Dark, ventilated for short term.",
        "processing_value": "Chips, Fries, Starch, Vodka/Alcohol.",
        
        "sowing_season": "Rabi (Winter)",
        "harvesting_season": "Jan - March",
        "growth_duration": "90 - 120 days",
        "average_price": "₹800 - ₹1500 / quintal",
        "diseases": [
            {
                "name": "Late Blight",
                "symptoms": "Water-soaked spots on leaves turning black. Decay of tubers. Historic famine cause.",
                "medicine_protection": "Prophylactic Mancozeb.",
                "medicine_cure": "Cymoxanil + Mancozeb spray."
            }
        ]
    },
    {
        "id": 7,
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Tomato",
        "overview": "Tomato is the major dietary source of the antioxidant lycopene, which has been linked to many health benefits.",
        "header_image": "dictionary/crop_headers/Tomato_je.jpg",
        "family": "Solanaceae",
        "varieties": "Pusa Ruby, Arka Vikas, Roma (for processing). Hybrids: Abhinav, US-440.",
        "growth_habit": "Determinate (Bush) or Indeterminate (Vine/Climber).",
        "pollination": "Self-pollinated",
        
        "soil_ph": "6.0 - 7.0",
        "soil_type": "Well-drained sandy loam. Avoid heavy clay.",
        "climatic_req": "Warm season. 20-30°C. Blossom drop occurs >35°C or <13°C.",
        "sowing_window": "Aug-Sep, Dec-Jan, May-June (Year round possible).",
        "seed_rate_spacing": "400-500g/ha (Open pollinated), 100-150g/ha (Hybrid). Spacing: 60x45cm.",
        "water_req": "Regular irrigation to maintain uniform moisture. Fluctuations cause fruit cracking.",
        
        "fertilizer_schedule": "NPK 100:60:60 kg/ha. Calcium sprays prevent Blossom End Rot.",
        "micronutrients": "Boron and Calcium are critical.",
        "crop_rotation": "Non-Solanaceous crops (avoid growing after potato/brinjal/chilli).",
        
        "major_pests": "Fruit Borer (Helicoverpa), Whitefly, Leaf Miner.",
        "weed_control": "Pendimethalin pre-transplant. Mulching is highly effective.",
        "ipm_practices": "Trap crop: Marigold (for borer). Pheromone traps.",
        
        "maturity_signs": "Color change from Green -> Breaker -> Pink -> Red.",
        "harvesting_method": "Hand picking with calyx attached.",
        "yield_expectations": "20 t/ha (Variety) to 60-80 t/ha (Hybrids).",
        "storage_req": "12-15°C. Do not refrigerate below 10°C (chilling injury).",
        "processing_value": "Ketchup, Puree, Sauce, Juice.",
        
        "sowing_season": "Year-round",
        "harvesting_season": "Two months after planting",
        "growth_duration": "110 - 140 days",
        "average_price": "₹1500 - ₹3000 / quintal",
        "diseases": [
            {
                "name": "Early Blight",
                "symptoms": "Concentric rings ('Target board') on lower leaves. Defoliation.",
                "medicine_protection": "Clean cultivation.",
                "medicine_cure": "Spray Chlorothalonil or Mancozeb."
            },
            {
                "name": "Tomato Leaf Curl Virus",
                "symptoms": "Leaves curl, become small and puckered. Stunted growth.",
                "medicine_protection": "Control Whitefly vector.",
                "medicine_cure": "Remove infected plants. Spray Imidacloprid."
            }
        ]
    },
    {
        "id": 8,
        "name": "Mustard",
        "scientific_name": "Brassica juncea",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Brassica_juncea",
        "overview": "Indian Mustard (Raya) is a major oilseed crop. It produces edible oil and is used as a spice.",
        "header_image": "dictionary/crop_headers/mustard.jpg",
        "family": "Brassicaceae",
        "varieties": "Pusa Jaikisan, Varuna, RH-30, Pusa Bold.",
        "growth_habit": "Annual herb, 1-2m tall, yellow flowers.",
        "pollination": "Cross-pollinated (Insects/Bees)",
        
        "soil_ph": "6.0 - 7.5",
        "soil_type": "Light to heavy loam soils. Thrives in sandy loam.",
        "climatic_req": "Cool and dry growing season. 15-25°C. Frost is harmful.",
        "sowing_window": "Rabi: Sep end to Oct middle (North India).",
        "seed_rate_spacing": "4-5 kg/ha. Spacing: 30x10 cm.",
        "water_req": "2-3 irrigations. Flowering and Pod formation stages are critical.",
        
        "fertilizer_schedule": "NPK 80:40:40 kg/ha. Sulphur (20-40 kg) increases oil content.",
        "micronutrients": "Sulphur is key.",
        "crop_rotation": "Maize-Mustard, Pearl Millet-Mustard, Fallow-Mustard",
        
        "major_pests": "Mustard Aphid (Lipaphis erysimi), Painted Bug, Sawfly.",
        "weed_control": "Oxadiargyl or Pendimethalin.",
        "ipm_practices": "Early sowing avoids severe aphid attack. Yellow sticky traps.",
        
        "maturity_signs": "Leaves turn yellow and drop. Siliquae (pods) turn straw yellow. Seeds become darker.",
        "harvesting_method": "Sickle harvesting of whole plants. Threshing after drying.",
        "yield_expectations": "1.5 - 2.5 tonnes/ha",
        "storage_req": "Seed moisture < 8%.",
        "processing_value": "Mustard Oil, Mustard Cake (Manure/Feed).",
        
        "sowing_season": "Rabi",
        "harvesting_season": "Feb - March",
        "growth_duration": "100 - 135 days",
        "average_price": "₹5050 - ₹5450 / quintal (MSP: ₹5650)",
        "diseases": [
            {
                "name": "White Rust",
                "symptoms": "White creamy pustules on leaves and floral parts (staghead formation).",
                "medicine_protection": "Resistant varieties.",
                "medicine_cure": "Spray Metalaxyl (Ridomil MZ).",
                "image":"dictionary/disease_images/mustard_d1.jpg"
            }
        ]
    },
    {
        "id": 9,
        "name": "Soybean",
        "scientific_name": "Glycine max",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Soybean",
        "overview": "Soybean is the world’s largest source of animal protein feed and the second largest source of vegetable oil.",
        "header_image": "dictionary/crop_headers/Soybean.USDA.jpg",
        "family": "Fabaceae (Legumes)",
        "varieties": "JS 335, JS 93-05, NRC 37 (Ahilya 4).",
        "growth_habit": "Bushy, erect annual herb.",
        "pollination": "Self-pollinated",
        
        "soil_ph": "6.0 - 7.5",
        "soil_type": "Well-drained fertile loam. Sensitive to salt.",
        "climatic_req": "Warm temperate/Tropical. 20-30°C.",
        "sowing_window": "Kharif: June end to July 1st fortnight.",
        "seed_rate_spacing": "65-75 kg/ha. Spacing: 45x5 cm.",
        "water_req": "Critical stages: Pod initiation and Grain filling. Waterlogging is harmful.",
        
        "fertilizer_schedule": "NPK 20:60:40 kg/ha. Needs less N (fixes own N). Sulphur is beneficial.",
        "micronutrients": "Molybdenum (for N-fixation), Zinc.",
        "crop_rotation": "Soybean-Wheat, Soybean-Chickpea",
        
        "major_pests": "Girdle Beetle, Tobacco Caterpillar, Stem Fly.",
        "weed_control": "Imazethapyr post-emergence.",
        "ipm_practices": "Use Pheromone traps for Spodoptera. Bird perches.",
        
        "maturity_signs": "Leaves lose green color and fall off. Pods turn brown/yellow.",
        "harvesting_method": "Threshing floor or Combine Harvester.",
        "yield_expectations": "2 - 3 tonnes/ha",
        "storage_req": "Moisture < 10%. Very hygroscopic (absorbs moisture).",
        "processing_value": "Soy milk, Tofu, Soy chunks, Oil, Soya sauce.",
        
        "sowing_season": "Kharif",
        "harvesting_season": "Sep - Oct",
        "growth_duration": "90 - 105 days",
        "average_price": "₹4600 - ₹4800 / quintal",
        "diseases": [
            {
                "name": "Yellow Mosaic Virus",
                "symptoms": "Bright yellow patches on leaves. Transmitted by Whitefly.",
                "medicine_protection": "Resistant varieties.",
                "medicine_cure": "Control vector with Thiamethoxam.",
                "image": "dictionary/disease_images/soyabean_d1.png"
            }
        ]
    },
    {
        "id": 10,
        "name": "Chickpea (Gram)",
        "scientific_name": "Cicer arietinum",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Chickpea",
        "overview": "Chickpea (Chana) is the most important pulse crop of India. It is a rich source of protein.",
        "header_image": "dictionary/crop_headers/chickpeas.webp",
        "family": "Fabaceae",
        "varieties": "Desi (Bengal Gram) and Kabuli types. GPF 2, JG 11.",
        "growth_habit": "Annual semi-erect or spreading herb.",
        "pollination": "Self-pollinated",
        
        "soil_ph": "6.0 - 7.5",
        "soil_type": "Sandy loam to clay loam. Rough seedbed is fine.",
        "climatic_req": "Cool and dry climate. 15-25°C.",
        "sowing_window": "Rabi: Oct-Nov.",
        "seed_rate_spacing": "Desi: 60-80 kg/ha, Kabuli: 100 kg/ha. Spacing: 30x10 cm.",
        "water_req": "Rainfed usually. 1-2 irrigations improve yield (Branching, Pod filling).",
        
        "fertilizer_schedule": "NPK 20:40:0 kg/ha. Biofertilizer (Rhizobium + PSB) recommended.",
        "micronutrients": "Iron deficiency in calcareous soils.",
        "crop_rotation": "Rice-Chickpea, Maize-Chickpea, Bajra-Chickpea",
        
        "major_pests": "Gram Pod Borer (Helicoverpa armigera) - Major pest.",
        "weed_control": "Pendimethalin pre-emergence.",
        "ipm_practices": "Nipping (plucking apical buds) to encourage branching. Pheromone traps for borer.",
        
        "maturity_signs": "Leaves turn reddish-brown and fall. Pods turn yellow/brown.",
        "harvesting_method": "Pulling out whole plants or cutting with sickle.",
        "yield_expectations": "1.5 - 2.5 tonnes/ha",
        "storage_req": "Moisture < 10%. Protection from Pulse Beetle.",
        "processing_value": "Besan (flour), Dal, Roasted Chana.",
        
        "sowing_season": "Rabi",
        "harvesting_season": "March - April",
        "growth_duration": "130 - 150 days",
        "average_price": "₹5335 (MSP) - ₹6000 / quintal",
        "diseases": [
            {
                "name": "Fusarium Wilt",
                "symptoms": "Drooping of leaves and drying of entire plant. Roots turn black.",
                "medicine_protection": "Deep summer ploughing. Wilt resistant varieties (JG 315).",
                "medicine_cure": "Seed treatment with Trichoderma + Carboxin.",
                "image": "dictionary/disease_images/fusarium_wilt_LJJFd17.webp"
            }
        ]
    }
]
