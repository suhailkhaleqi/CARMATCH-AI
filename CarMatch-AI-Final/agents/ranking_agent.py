import pandas as pd
import numpy as np

def rank_cars(df, criteria):
    """
    Ajan 3: Her araç için utility score hesaplar
    
    Dikkate alınanlar:
    - Fiyat (düşük olanlar daha iyi)
    - Yakıt tüketimi (düşük olanlar daha iyi)
    - Güç (yüksek olanlar daha iyi)
    - Kullanıcı öncelikleri
    """
    
    df = df.copy()
    
    # ========== NORMALİZASYON ==========
    # Tüm değerleri [0, 1] aralığına getir
    
    # Fiyat (tersine çevir: düşük olanlar daha iyi)
    if df['price'].max() != df['price'].min():
        df['price_score'] = 1 - (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min())
    else:
        df['price_score'] = 1.0
    
    # Yakıt tüketimi (tersine çevir: düşük olanlar daha iyi)
    if df['fuel_consumption'].max() != df['fuel_consumption'].min():
        df['fuel_score'] = 1 - (df['fuel_consumption'] - df['fuel_consumption'].min()) / (df['fuel_consumption'].max() - df['fuel_consumption'].min())
    else:
        df['fuel_score'] = 1.0
    
    # Güç (yüksek olanlar daha iyi)
    if df['horsepower'].max() != df['horsepower'].min():
        df['power_score'] = (df['horsepower'] - df['horsepower'].min()) / (df['horsepower'].max() - df['horsepower'].min())
    else:
        df['power_score'] = 1.0
    
    # ========== AĞIRLIKLAR ==========
    # Varsayılan
    weight_price = 0.4
    weight_fuel = 0.3
    weight_power = 0.3
    
    # Önceliklere göre ağırlıkları ayarla
    if criteria['fuel_priority']:
        weight_fuel = 0.5
        weight_price = 0.3
        weight_power = 0.2
    
    if criteria['power_priority']:
        weight_power = 0.5
        weight_price = 0.3
        weight_fuel = 0.2
    
    # ========== TOPLAM SKOR ==========
    df['utility_score'] = (
        weight_price * df['price_score'] +
        weight_fuel * df['fuel_score'] +
        weight_power * df['power_score']
    )
    
    # Skora göre sırala (azalan)
    df = df.sort_values('utility_score', ascending=False)
    
    return df