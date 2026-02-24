import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

def generate_explanation(user_query, criteria, top_cars):
    """
    Ajan 4: Google Gemini API kullanarak Türkçe açıklama oluşturur
    """
    
    # Gemini için prompt oluştur
    prompt = f"""
Sen bir araba tavsiye asistanısın. Kullanıcıya en uygun araçları buldun ve şimdi güzel, anlaşılır bir açıklama yapman gerekiyor.

Kullanıcı şunu sordu:
"{user_query}"

Analiz edilen kriterler:
- Maksimum fiyat: {criteria.get('max_price', 'Belirtilmedi')}
- Yakıt tipi: {criteria.get('fuel_type', 'Belirtilmedi')}
- Gövde tipi: {criteria.get('body_type', 'Belirtilmedi')}
- Yakıt tasarrufu öncelikli: {'Evet' if criteria.get('fuel_priority') else 'Hayır'}
- Güç öncelikli: {'Evet' if criteria.get('power_priority') else 'Hayır'}

Bulunan en iyi araçlar:
"""
    
    for idx, car in top_cars.iterrows():
        prompt += f"""
{car['brand']} {car['model']}
- Fiyat: {int(car['price'])} TL
- Yakıt: {car['fuel_type']}
- Tüketim: {car['fuel_consumption']} L/100km
- Güç: {car['horsepower']} HP
- Gövde: {car['body_type']}
- Skor: {car['utility_score']:.2f}
"""
    
    prompt += """

Her araç için şu formatta yaz:

### ARAÇ: {Marka} {Model}
Fiyat: {fiyat} TL | Yakıt: {tüketim} L/100km
{Kısa açıklama ve yorum, 2-3 cümle}

1. Başta kısa bir giriş yap (1-2 cümle)
2. Sonra her araç için yukarıdaki formatı kullan
3. En sonda kısa bir sonuç ve tavsiye ekle (2-3 cümle)
"""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    
    except Exception as e:
        print(f"❌ Gemini API hatası: {str(e)}")
        return f"""
Sorgunuzu analiz ettik: "{user_query}"

Kriterlerinize göre {len(top_cars)} araç bulduk. En uygun seçenekler:

{chr(10).join([f"• {car['brand']} {car['model']} - {int(car['price'])} TL" for _, car in top_cars.iterrows()])}

Bu araçlar fiyat, yakıt tüketimi ve performans açısından en iyi dengeyi sunuyor.
"""