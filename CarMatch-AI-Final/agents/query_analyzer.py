import re
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

def analyze_query(query):
    """
    Ajan 1: Kullanıcı sorgusunu AI ile analiz eder
    
    Gemini kullanarak doğal dildeki her türlü sorguyu anlar
    """
    
    # Önce basit regex ile dene (hızlı)
    criteria = extract_with_regex(query)
    
    # Eğer belirsizlik varsa veya karmaşık sorgu ise AI kullan
    if needs_ai_analysis(query, criteria):
        criteria = extract_with_ai(query)
    
    return criteria


def extract_with_regex(query):
    """Hızlı regex tabanlı çıkarma"""
    
    query_lower = query.lower()
    
    criteria = {
        'max_price': None,
        'fuel_type': None,
        'body_type': None,
        'fuel_priority': False,
        'power_priority': False
    }
    
    # FİYAT
    price_patterns = [
        r'(\d+)\.(\d+)\s*(?:tl|lira)',
        r'(\d+)\s*(?:bin|k)\s*(?:tl|lira)',
        r'(\d+)\s*(?:tl|lira)',
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, query_lower)
        if match:
            if 'bin' in pattern or 'k' in pattern:
                criteria['max_price'] = int(match.group(1)) * 1000
            else:
                price_str = match.group(1)
                if len(match.groups()) > 1:
                    price_str += match.group(2)
                criteria['max_price'] = int(price_str)
            break
    
    # YAKIT TİPİ
    fuel_keywords = {
        'benzin': 'Benzin',
        'dizel': 'Dizel',
        'diesel': 'Dizel',
        'hibrit': 'Hibrit',
        'hybrid': 'Hibrit',
        'elektrik': 'Elektrik',
        'electric': 'Elektrik'
    }
    
    for keyword, fuel_type in fuel_keywords.items():
        if keyword in query_lower:
            criteria['fuel_type'] = fuel_type
            break
    
    # GÖVDE TİPİ
    body_keywords = {
        'suv': 'SUV',
        'sedan': 'Sedan',
        'hatchback': 'Hatchback',
        'coupe': 'Coupe'
    }
    
    for keyword, body_type in body_keywords.items():
        if keyword in query_lower:
            criteria['body_type'] = body_type
            break
    
    # ÖNCELİKLER
    fuel_saving_keywords = ['az yakan', 'yakıt tasarrufu', 'ekonomik']
    if any(keyword in query_lower for keyword in fuel_saving_keywords):
        criteria['fuel_priority'] = True
    
    power_keywords = ['güçlü', 'hızlı', 'sportif']
    if any(keyword in query_lower for keyword in power_keywords):
        criteria['power_priority'] = True
    
    return criteria


def needs_ai_analysis(query, criteria):
    """AI analizine ihtiyaç var mı kontrol et"""
    
    query_lower = query.lower()
    
    # Karmaşık ifadeler
    complex_keywords = [
        'aileme', 'aile', 'şehir içi', 'lüks', 'güvenli', 
        'offroad', 'ikinci el gibi', 'ilk arabam', 'öğrenci',
        'rahat', 'konforlu', 'modern', 'şık'
    ]
    
    # Eğer karmaşık kelime varsa AI kullan
    if any(keyword in query_lower for keyword in complex_keywords):
        return True
    
    # Eğer hiçbir kriter bulunamadıysa AI kullan
    if not any([criteria['max_price'], criteria['fuel_type'], criteria['body_type']]):
        return True
    
    return False


def extract_with_ai(query):
    """Gemini ile doğal dil analizi"""
    
    prompt = f"""
Kullanıcının araba araması sorgusunu analiz et ve JSON formatında kriterleri çıkar.

Kullanıcı sorgusu: "{query}"

Şu kriterleri bul:

1. FIYAT KRİTERLERİ:
- min_price: Minimum fiyat (sayı veya null)
- max_price: Maksimum fiyat (sayı veya null)

KURALLAR:
* Eğer SAYISAL fiyat belirtilmişse (örn: "800000 TL altı"):
  → max_price = o sayı, min_price = null
  
* "ucuz", "uygun fiyatlı":
  → max_price = 600000, min_price = null
  
* "orta", "normal", "orta segment":
  → min_price = 600000, max_price = 1900000
  
* "lüks", "pahalı", "premium":
  → min_price = 1900000, max_price = null

* ÇELİŞKİ DURUMU (örn: "ucuz lüks"):
  → min_price = 600000, max_price = 1500000 (orta segment)

* Hiç fiyat kelimesi YOK:
  → min_price = null, max_price = null

* ÖNEMLİ: "aile" kelimesi fiyatı ETKİLEMEZ!

2. YAKIT KRİTERLERİ:
- fuel_type: "Benzin", "Dizel", "Hibrit", "Elektrik" veya null
- max_fuel_consumption: Maksimum tüketim (sayı veya null)

KURALLAR:
* "az yakan", "ekonomik", "yakıt tasarrufu":
  → max_fuel_consumption = 6.5
  
* Belirtilmemişse:
  → max_fuel_consumption = null

3. GÖVDE TİPİ:
- body_type: "SUV", "Sedan", "Hatchback", "Coupe" veya null

KURALLAR:
* "aile", "aileme uygun": → null (fiyata göre karar)
* "şehir içi", "küçük", "park": → "Hatchback"
* "spor", "şık": → "Coupe"
* "SUV", "arazi", "offroad": → "SUV"
* "sedan": → "Sedan"

4. ÖNCELİKLER:
- fuel_priority: Yakıt tasarrufu önemli mi? (true/false)
  * "az yakan", "ekonomik" → true
  
- power_priority: Güç önemli mi? (true/false)
  * "güçlü", "hızlı", "sportif", "performans" → true

SADECE JSON döndür (markdown yok, açıklama yok):
{{
  "min_price": null veya sayı,
  "max_price": null veya sayı,
  "fuel_type": null veya string,
  "max_fuel_consumption": null veya sayı,
  "body_type": null veya string,
  "fuel_priority": true/false,
  "power_priority": true/false
}}
"""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # JSON'ı parse et
        import json
        result_text = response.text.strip()
        
        # Markdown kod bloklarını temizle
        if '```' in result_text:
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        criteria = json.loads(result_text.strip())
        print(f"   AI analizi: {criteria}")
        return criteria
        
    except Exception as e:
        print(f"   AI analiz hatası: {e}, regex kullanılıyor")
        return extract_with_regex(query)