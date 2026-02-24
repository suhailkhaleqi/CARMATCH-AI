from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv

# Ajanlari içe aktar
from agents.query_analyzer import analyze_query
from agents.filter_agent import filter_cars
from agents.ranking_agent import rank_cars
from agents.llm_agent import generate_explanation

load_dotenv()

app = Flask(__name__)
CORS(app)  # GitHub Pages'ten gelen isteklere izin ver

# Araç veritabanını yükle
df = pd.read_csv('cars_database.csv')

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Araba Tavsiye Asistanı API çalışıyor!",
        "agents": ["Query Analyzer", "Filter", "Ranking", "LLM Explanation"]
    })

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        # Kullanıcı sorgusunu al
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"error": "Sorgu boş olamaz!"}), 400
        
        print(f"📥 Kullanıcı sorgusu: {user_query}")
        
        # ========== AJAN 1: Sorgu Analizi ==========
        print("🔍 Ajan 1: Sorgu analiz ediliyor...")
        criteria = analyze_query(user_query)
        print(f"✅ Kriterler: {criteria}")
        
        # ========== AJAN 2: Filtreleme ==========
        print("🎯 Ajan 2: Araçlar filtreleniyor...")
        filtered_cars = filter_cars(df, criteria)
        print(f"✅ {len(filtered_cars)} araç bulundu")
        
        if filtered_cars.empty:
            return jsonify({
                "explanation": "Üzgünüm, kriterlere uygun araç bulunamadı. Lütfen farklı kriterler deneyin.",
                "cars": []
            })
        
        # ========== AJAN 3: Skorlama ==========
        print("📊 Ajan 3: Skorlar hesaplanıyor...")
        ranked_cars = rank_cars(filtered_cars, criteria)
        print(f"✅ En iyi araçlar sıralandı")
        
        # İlk 5'i al
        top_cars = ranked_cars.head(5)
        
        # ========== AJAN 4: Gemini ile açıklama ==========
        print("✨ Ajan 4: AI açıklama oluşturuluyor...")
        explanation = generate_explanation(user_query, criteria, top_cars)
        print(f"✅ Açıklama hazır")
        
        # Sonucu oluştur
        result = {
            "explanation": explanation,
            "cars": top_cars.to_dict('records')
        }
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)