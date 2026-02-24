import pandas as pd

def filter_cars(df, criteria):
    """
    Ajan 2: Araçları kriterlere göre filtreler
    
    Uygulanan filtreler:
    - Minimum ve maksimum fiyat
    - Yakıt tipi
    - Maksimum yakıt tüketimi
    - Gövde tipi
    """
    
    filtered = df.copy()
    
    # ========== FİYAT FİLTRESİ ==========
    if criteria.get('min_price'):
        filtered = filtered[filtered['price'] >= criteria['min_price']]
        print(f"   Minimum fiyat filtresinden sonra: {len(filtered)} araç")
    
    if criteria.get('max_price'):
        filtered = filtered[filtered['price'] <= criteria['max_price']]
        print(f"   Maksimum fiyat filtresinden sonra: {len(filtered)} araç")
    
    # ========== YAKIT TİPİ FİLTRESİ ==========
    if criteria.get('fuel_type'):
        filtered = filtered[filtered['fuel_type'] == criteria['fuel_type']]
        print(f"   Yakıt filtresinden sonra: {len(filtered)} araç")
    
    # ========== YAKIT TÜKETİMİ FİLTRESİ ==========
    if criteria.get('max_fuel_consumption'):
        filtered = filtered[filtered['fuel_consumption'] <= criteria['max_fuel_consumption']]
        print(f"   Yakıt tüketim filtresinden sonra: {len(filtered)} araç")
    
    # ========== GÖVDE TİPİ FİLTRESİ ==========
    if criteria.get('body_type'):
        filtered = filtered[filtered['body_type'] == criteria['body_type']]
        print(f"   Gövde filtresinden sonra: {len(filtered)} araç")
    
    return filtered