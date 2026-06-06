import urllib.request
import urllib.parse
import json

CROP_DICTIONARY_HI = {
    'apple': 'सेब',
    'banana': 'केला',
    'tomato': 'टमाटर',
    'potato': 'आलू',
    'wheat': 'गेहूं',
    'rice': 'चावल',
    'garlic': 'लहसुन',
    'onion': 'प्याज',
    'mustard': 'सरसों',
    'milk': 'दूध',
    'carrot': 'गाजर',
    'cabbage': 'पत्तागोभी',
    'cauliflower': 'फूलगोभी',
    'cucumber': 'खीरा',
    'maize': 'मक्का',
    'corn': 'मक्का',
    'ginger': 'अदरक',
    'peas': 'मटर',
    'soybean': 'सोयाबीन',
    'orange': 'संतरा',
    'grapes': 'अंगूर',
    'pomegranate': 'अनार',
    'papaya': 'पपीता',
    'guava': 'अमरूद',
    'pineapple': 'अनानास',
    'watermelon': 'तरबूज',
    'lemon': 'नींबू',
    'coconut': 'नारियल',
    'peach': 'आडू',
}

CROP_DICTIONARY_NE = {
    'apple': 'स्याउ',
    'banana': 'केरा',
    'tomato': 'टमाटर',
    'potato': 'आलु',
    'wheat': 'गहुँ',
    'rice': 'चामल',
    'garlic': 'लसुन',
    'onion': 'प्याज',
    'mustard': 'तोरी',
    'milk': 'दूध',
    'carrot': 'गाजर',
    'cabbage': 'बन्दाकोभी',
    'cauliflower': 'काउली',
    'cucumber': 'काँक्रो',
    'maize': 'मकै',
    'corn': 'मकै',
    'ginger': 'अदुवा',
    'peas': 'मटर',
    'soybean': 'भटमास',
    'orange': 'सुन्तला',
    'grapes': 'अङ्गुर',
    'pomegranate': 'अनार',
    'papaya': 'मेवा',
    'guava': 'अम्बा',
    'pineapple': 'भुइँकटहर',
    'watermelon': 'खर्बुजा',
    'lemon': 'कागती',
    'coconut': 'नारियल',
    'peach': 'आरु',
}

def google_translate(text, target_lang):
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=" + target_lang + "&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([part[0] for part in data[0] if part[0]])
    except Exception:
        return ""

def translate_text(text, target_lang):
    if not text:
        return ""
    text_lower = text.strip().lower()
    
    # Try dictionary fallback first
    if target_lang == 'hi' and text_lower in CROP_DICTIONARY_HI:
        return CROP_DICTIONARY_HI[text_lower]
    if target_lang == 'ne' and text_lower in CROP_DICTIONARY_NE:
        return CROP_DICTIONARY_NE[text_lower]
        
    # Try Google Translate API
    translated = google_translate(text, target_lang)
    if translated:
        return translated.strip()
        
    return text
