import os
import sys
import random
import django

# Setup django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kisaan_mandi.settings')
django.setup()

from marketplace.models import Product, Category
from accounts.models import CustomUser

def seed_extra_products():
    print("Fixing existing Product #8 (Groundnut) Nepali name...")
    try:
        groundnut = Product.objects.get(name="Groundnut")
        groundnut.name_ne = "बदाम"
        groundnut.save()
        print("Product #8 updated successfully.")
    except Product.DoesNotExist:
        print("Product #8 (Groundnut) not found in DB.")

    # Get farmers
    farmers_usernames = ['ramu_farmer', 'priya_kisan', 'suresh_farm', 'ram_bahadur']
    farmers = []
    for username in farmers_usernames:
        try:
            user = CustomUser.objects.get(username=username)
            farmers.append(user)
        except CustomUser.DoesNotExist:
            print(f"Farmer '{username}' does not exist. Please run seed_data command first.")
            return

    # Get categories
    categories = {cat.slug: cat for cat in Category.objects.all()}
    required_slugs = ['grains', 'vegetables', 'fruits', 'spices', 'pulses', 'dairy', 'oilseeds']
    for slug in required_slugs:
        if slug not in categories:
            print(f"Category '{slug}' does not exist. Please run seed_data command first.")
            return

    # List of product templates (name, name_hi, name_ne, unit, base_price, category_slug)
    product_templates = [
        # Grains
        ("Barley", "जौ", "जौ", "quintal", 1800, "grains"),
        ("Millet", "बाजरा", "कोदो", "quintal", 2100, "grains"),
        ("Maize", "मक्का", "मकै", "quintal", 1950, "grains"),
        ("Oats", "जई", "जेई", "quintal", 2500, "grains"),
        ("Sorghum", "ज्वार", "जुनेलो", "quintal", 2200, "grains"),
        ("Finger Millet", "रागी", "कोदो", "quintal", 2300, "grains"),
        ("Brown Rice", "भूरा चावल", "खैरो चामल", "quintal", 3800, "grains"),
        ("Black Rice", "काला चावल", "कालो चामल", "quintal", 6500, "grains"),
        ("Semolina", "सूजी", "सुजी", "kg", 45, "grains"),
        ("Wheat Flour", "गेहूँ का आटा", "गहुँको पीठो", "kg", 35, "grains"),
        
        # Vegetables
        ("Cauliflower", "फूलगोभी", "काउली", "kg", 40, "vegetables"),
        ("Cabbage", "पत्तागोभी", "बन्दाकोभी", "kg", 30, "vegetables"),
        ("Spinach", "पालक", "पालुङ्गो", "kg", 25, "vegetables"),
        ("Carrot", "गाजर", "गाजर", "kg", 45, "vegetables"),
        ("Radish", "मूली", "मुला", "kg", 20, "vegetables"),
        ("Green Peas", "हरी मटर", "केराउ", "kg", 60, "vegetables"),
        ("Eggplant", "बैंगन", "भण्टा", "kg", 35, "vegetables"),
        ("Okra", "भिंडी", "रामतोरियाँ", "kg", 50, "vegetables"),
        ("Cucumber", "खीरा", "काँक्रो", "kg", 30, "vegetables"),
        ("Bitter Gourd", "करेला", "करेला", "kg", 55, "vegetables"),
        ("Bottle Gourd", "लौकी", "लौका", "kg", 25, "vegetables"),
        ("Pumpkin", "कद्दू", "फर्सी", "kg", 20, "vegetables"),
        ("Ginger", "अदरक", "अदुवा", "kg", 120, "vegetables"),
        ("Coriander Leaves", "धनिया पत्ता", "धनियाँ", "kg", 60, "vegetables"),
        ("Green Chilli", "हरी मिर्च", "हरियो खुर्सानी", "kg", 70, "vegetables"),
        ("Capsicum", "शिमला मिर्च", "भेडे खुर्सानी", "kg", 80, "vegetables"),
        ("Sweet Potato", "शकरकंद", "सखरखण्ड", "kg", 40, "vegetables"),
        ("Beetroot", "चुकंदर", "चुकन्दर", "kg", 35, "vegetables"),
        ("Green Onion", "हरा प्याज", "हरियो प्याज", "kg", 40, "vegetables"),
        
        # Fruits
        ("Mango", "आम", "आँप", "kg", 100, "fruits"),
        ("Banana", "केला", "केरा", "dozen", 60, "fruits"),
        ("Apple", "सेब", "स्याउ", "kg", 150, "fruits"),
        ("Orange", "संतरा", "सुन्तला", "kg", 120, "fruits"),
        ("Grapes", "अंगूर", "अंगूर", "kg", 90, "fruits"),
        ("Pomegranate", "अनार", "अनार", "kg", 140, "fruits"),
        ("Papaya", "पपीता", "मेवा", "kg", 50, "fruits"),
        ("Guava", "अमरूद", "अम्बा", "kg", 60, "fruits"),
        ("Pineapple", "अनानस", "भुईँकटर", "piece", 70, "fruits"),
        ("Watermelon", "तरबूज", "खरबुजा", "kg", 25, "fruits"),
        ("Lemon", "नींबू", "कागती", "kg", 120, "fruits"),
        ("Coconut", "नारियल", "नरिवल", "piece", 35, "fruits"),
        ("Peach", "आडू", "आरु", "kg", 160, "fruits"),
        ("Plum", "आलूबुखारा", "आलुबखडा", "kg", 180, "fruits"),
        ("Pear", "नाशपाती", "नासपाती", "kg", 90, "fruits"),
        ("Strawberry", "स्ट्रॉबेरी", "स्ट्रबेरी", "kg", 250, "fruits"),
        ("Sweet Lime", "मौसमी", "मौसम", "kg", 80, "fruits"),
        
        # Spices
        ("Black Pepper", "काली मिर्च", "मरिच", "kg", 600, "spices"),
        ("Cumin Seeds", "जीरा", "जिरा", "kg", 250, "spices"),
        ("Cardamom", "इलायची", "अलैंची", "kg", 1200, "spices"),
        ("Cloves", "लौंग", "ल्वाङ", "kg", 800, "spices"),
        ("Cinnamon", "दालचीनी", "दालचिनी", "kg", 350, "spices"),
        ("Fenugreek", "मेथी", "मेथी", "kg", 110, "spices"),
        ("Fennel", "सौंफ", "सौँफ", "kg", 150, "spices"),
        ("Coriander Powder", "धनिया पाउडर", "धनियाँ धुलो", "kg", 160, "spices"),
        ("Asafoetida", "हींग", "हिङ", "kg", 2500, "spices"),
        ("Red Chilli Powder", "लाल मिर्च पाउडर", "रातो खुर्सानी धुलो", "kg", 220, "spices"),
        
        # Pulses
        ("Chickpeas", "चना", "चना", "kg", 90, "pulses"),
        ("Red Lentils", "मसूर दाल", "मुसुरो दाल", "kg", 85, "pulses"),
        ("Black Gram", "उड़द दाल", "मासको दाल", "kg", 110, "pulses"),
        ("Pigeon Peas", "अरहर दाल", "रहरको दाल", "kg", 130, "pulses"),
        ("Green Gram", "मूंग दाल", "मुङको दाल", "kg", 100, "pulses"),
        ("Kidney Beans", "राजमा", "राजमा", "kg", 120, "pulses"),
        ("Black-eyed Peas", "लोबिया", "बोडी", "kg", 95, "pulses"),
        ("Horse Gram", "कुलथी दाल", "गहत", "kg", 80, "pulses"),
        
        # Dairy
        ("Cow Milk", "गाय का दूध", "गाईको दूध", "kg", 60, "dairy"),
        ("Buffalo Milk", "भैंस का दूध", "भैँसीको दूध", "kg", 75, "dairy"),
        ("Paneer", "पनीर", "पनीर", "kg", 380, "dairy"),
        ("Ghee", "घी", "घिउ", "kg", 650, "dairy"),
        ("Curd", "दही", "दही", "kg", 80, "dairy"),
        ("Butter", "मक्खन", "नौनी घिउ", "kg", 450, "dairy"),
        ("Butter Milk", "छाछ", "मही", "kg", 30, "dairy"),
        
        # Oilseeds
        ("Sesame Seeds", "तिल", "तिल", "kg", 180, "oilseeds"),
        ("Sunflower Seeds", "सूरजमुखी के बीज", "सूर्यमुखीको दाना", "kg", 120, "oilseeds"),
        ("Flax Seeds", "अलसी के बीज", "आल्स", "kg", 90, "oilseeds"),
        ("Soybean", "सोयाबीन", "भटमास", "kg", 75, "oilseeds"),
    ]

    prefixes = ["Fresh", "Organic", "Local", "Premium", "Selection of", "Deals on", "High Quality", "Pure", "Farm Fresh", "Traditional"]
    prefixes_hi = ["ताजा", "जैविक", "स्थानीय", "प्रीमियम", "उत्कृष्ट", "सस्ता", "उच्च गुणवत्ता", "शुद्ध", "सीधे खेत से", "पारंपरिक"]
    prefixes_ne = ["ताजा", "जैविक", "स्थानीय", "प्रिमियम", "उत्कृष्ट", "सस्तो", "उच्च गुणस्तर", "शुद्ध", "खेतबाट सिधै", "पारम्परिक"]

    locations_states = [
        ("Nashik", "Maharashtra"),
        ("Anand", "Gujarat"),
        ("Ludhiana", "Punjab"),
        ("Kathmandu", "Bagmati"),
        ("Pune", "Maharashtra"),
        ("Surat", "Gujarat"),
        ("Amritsar", "Punjab"),
        ("Lalitpur", "Bagmati"),
        ("Nagpur", "Maharashtra"),
        ("Rajkot", "Gujarat"),
        ("Jalandhar", "Punjab"),
        ("Bhaktapur", "Bagmati"),
        ("Mumbai Mandi", "Maharashtra"),
        ("Ahmedabad Mandi", "Gujarat"),
        ("Patiala Mandi", "Punjab"),
        ("Pokhara Bazar", "Gandaki"),
    ]

    total_added = 0
    # Generate 100 products
    for i in range(100):
        # Choose a template
        tmpl = random.choice(product_templates)
        name_base, name_hi_base, name_ne_base, unit, base_price, category_slug = tmpl
        
        # Choose random prefix
        pref_idx = random.randint(0, len(prefixes) - 1)
        p_en = prefixes[pref_idx]
        p_hi = prefixes_hi[pref_idx]
        p_ne = prefixes_ne[pref_idx]
        
        # Combine
        full_name_en = f"{p_en} {name_base}"
        full_name_hi = f"{p_hi} {name_hi_base}"
        full_name_ne = f"{p_ne} {name_ne_base}"
        
        # Add random variation to prices and quantities
        price = round(base_price * random.uniform(0.85, 1.25), 2)
        qty = round(random.uniform(10, 500), 2)
        
        # Select farmer and location matching state
        farmer = random.choice(farmers)
        
        # Location logic: match farmer's actual state/location context or random location
        # Let's map it contextually:
        if farmer.username == 'ramu_farmer':
            loc, state = random.choice([x for x in locations_states if x[1] == "Maharashtra"])
        elif farmer.username == 'priya_kisan':
            loc, state = random.choice([x for x in locations_states if x[1] == "Gujarat"])
        elif farmer.username == 'suresh_farm':
            loc, state = random.choice([x for x in locations_states if x[1] == "Punjab"])
        else: # ram_bahadur
            loc, state = random.choice([x for x in locations_states if x[1] in ["Bagmati", "Gandaki"]])
            
        description = f"{full_name_en} direct from the farms of {loc}, {state}."
        is_organic = "Organic" in p_en or random.choice([True, False, False])
        
        category = categories[category_slug]
        
        # Create product in DB
        Product.objects.create(
            farmer=farmer,
            category=category,
            name=full_name_en,
            name_hi=full_name_hi,
            name_ne=full_name_ne,
            description=description,
            price_per_unit=price,
            unit=unit,
            quantity_available=qty,
            location=loc,
            state=state,
            is_organic=is_organic,
            status='active'
        )
        total_added += 1

    print(f"Successfully generated and added {total_added} products to the database!")

if __name__ == "__main__":
    seed_extra_products()
