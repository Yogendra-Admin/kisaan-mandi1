import os
import urllib.request

crops = {
    "onion": "onion,field",
    "spinach": "spinach,field",
    "coconut": "coconut,tree,farm",
    "cabbage": "cabbage,field",
    "carrot": "carrot,field",
    "radish": "radish,field",
    "eggplant": "eggplant,field",
    "okra": "okra,field",
    "chilli": "chilli,field",
    "pea": "pea,field",
    "mango": "mango,tree",
    "banana": "banana,plantation",
    "apple": "apple,tree,orchard",
    "orange": "orange,tree,orchard",
    "grapes": "grapes,vineyard",
    "pomegranate": "pomegranate,tree",
    "papaya": "papaya,tree",
    "guava": "guava,tree",
    "pineapple": "pineapple,field",
    "watermelon": "watermelon,field",
    "lemon": "lemon,tree",
    "strawberry": "strawberry,field",
    "turmeric": "turmeric,plant",
    "cumin": "cumin,field",
    "cardamom": "cardamom,plant",
    "chickpea": "chickpea,field",
    "soybean": "soybean,field",
    "sunflower": "sunflower,field",
    "barley": "barley,field",
    "millet": "millet,field",
    "maize": "corn,field",
    "oats": "oats,field",
    "ginger": "ginger,plant",
    "rice": "rice,field"
}

dest_dir = "static/images/products"
os.makedirs(dest_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("Starting to download field-growing crop photos from LoremFlickr...")

for crop_name, tag in crops.items():
    filepath = os.path.join(dest_dir, f"{crop_name}.png")
    
    # Check if the file already exists and is valid
    if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
        print(f"File for {crop_name} already exists. Skipping.")
        continue

    url = f"https://loremflickr.com/600/400/{tag}"
    print(f"Downloading {crop_name} from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            with open(filepath, 'wb') as f:
                f.write(data)
        print(f"  Successfully downloaded {crop_name}.png")
    except Exception as e:
        print(f"  Error downloading {crop_name}: {e}")

print("Finished downloading crop field photos.")
