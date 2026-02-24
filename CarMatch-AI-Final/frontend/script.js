// Backend API URL (change for production deployment)
const BACKEND_URL = 'http://localhost:5001/api/recommend';

// DOM Elements
const searchBtn = document.getElementById('searchBtn');
const userQuery = document.getElementById('userQuery');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const error = document.getElementById('error');
const explanation = document.getElementById('explanation');

// Search button handler
searchBtn.addEventListener('click', handleSearch);

// Enter key handler
userQuery.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        handleSearch();
    }
});

async function handleSearch() {
    const query = userQuery.value.trim();
    
    if (!query) {
        showError('Lütfen bir sorgu girin!');
        return;
    }
    
    hideError();
    hideResults();
    
    // Change button to loading animation
    const btnText = document.getElementById('btnText');
    const originalText = btnText.innerHTML;
    btnText.innerHTML = '<div class="thinking-animation"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
    searchBtn.disabled = true;
    
    try {
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`Sunucu hatası: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayResults(data);
        
        // Smooth scroll to results
        setTimeout(() => {
            document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
        
    } catch (err) {
        console.error('Hata:', err);
        showError(`Bir hata oluştu: ${err.message}`);
    } finally {
        // Restore button
        btnText.innerHTML = originalText;
        searchBtn.disabled = false;
    }
}

function displayResults(data) {
    // Display Gemini explanation
    explanation.innerHTML = formatExplanation(data.explanation, data.cars);
    
    // Show results section
    showResults();
}

function createCarCard(car) {
    const card = document.createElement('div');
    card.className = 'car-card';
    
    // Image (if URL exists in data)
    const imageUrl = car.image_url || getDefaultCarImage(car.brand);
    
    card.innerHTML = `
        <img src="${imageUrl}" alt="${car.brand} ${car.model}" class="car-image" 
             onerror="this.src='https://via.placeholder.com/400x200/667eea/ffffff?text=Araba+Resmi+Yok'">
        <div class="car-info">
            <div class="car-name">${car.brand} ${car.model}</div>
            <div class="car-score">Skor: ${car.utility_score.toFixed(2)}</div>
            <div class="car-details">
                <div class="car-detail">
                    <span class="detail-label">💰 Fiyat</span>
                    <span class="detail-value">${formatPrice(car.price)} TL</span>
                </div>
                <div class="car-detail">
                    <span class="detail-label">⛽ Yakıt</span>
                    <span class="detail-value">${car.fuel_type}</span>
                </div>
                <div class="car-detail">
                    <span class="detail-label">📊 Tüketim</span>
                    <span class="detail-value">${car.fuel_consumption} L/100km</span>
                </div>
                <div class="car-detail">
                    <span class="detail-label">⚡ Güç</span>
                    <span class="detail-value">${car.horsepower} HP</span>
                </div>
                <div class="car-detail">
                    <span class="detail-label">🚗 Gövde</span>
                    <span class="detail-value">${car.body_type}</span>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

function formatExplanation(text, cars) {

    text = text.replace(/\*\*/g, '');
    const sections = text.split('### ARAÇ:');
    let html = '';
    
    sections.forEach((section, index) => {
        if (index === 0) {
            // Intro text
            html += `<p style="margin-bottom: 30px; line-height: 1.8;">${section.trim()}</p>`;
        } else {
            // Car block
            const lines = section.trim().split('\n');
            const carName = lines[0].trim();
            const carText = lines.slice(1).join(' ').trim();
            
            // Find car in data
            const car = cars.find(c => `${c.brand} ${c.model}` === carName);
            const imageUrl = car && car.image ? `images/${car.image}` : 'https://via.placeholder.com/300x200/667eea/ffffff?text=No+Image';
            
            // Получаем имя файла без расширения для ссылки (например: fiat-egea)
            const carSlug = car && car.image ? car.image.replace('.jpg', '').replace('.png', '') : '';
            const sahibindenUrl = `https://www.sahibinden.com/${carSlug}`;
            
            html += `
                <div style="background: white; border-radius: 16px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <img src="${imageUrl}" style="width: 300px; height: 200px; object-fit: cover; border-radius: 12px; margin-bottom: 16px;" alt="${carName}">
                    <h3 style="color: #6366f1; margin-bottom: 12px; font-size: 1.5rem;">${carName}</h3>
                    <p style="line-height: 1.8; color: #4b5563; margin-bottom: 16px;">${carText}</p>
                    <a href="${sahibindenUrl}" target="_blank" class="sahibinden-btn">
                        <div class="sahibinden-logo">S</div>
                        <span>Sahibinden</span>
                    </a>
                </div>
            `;
        }
    });
    
    return html;
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('tr-TR').format(price);
}

// Default car image placeholder (can be replaced with API search)
function getDefaultCarImage(brand) {
    // Future: can use API for image search
    const brandLogos = {
        'Toyota': 'https://www.carlogos.org/car-logos/toyota-logo.png',
        'BMW': 'https://www.carlogos.org/car-logos/bmw-logo.png',
        'Mercedes': 'https://www.carlogos.org/car-logos/mercedes-benz-logo.png',
        'Volkswagen': 'https://www.carlogos.org/car-logos/volkswagen-logo.png',
        'Renault': 'https://www.carlogos.org/car-logos/renault-logo.png',
        'Fiat': 'https://www.carlogos.org/car-logos/fiat-logo.png'
    };
    
    return brandLogos[brand] || 'https://via.placeholder.com/400x200/667eea/ffffff?text=Araba';
}

// UI utility functions
function showLoading() {
    loading.classList.remove('hidden');
}

function hideLoading() {
    loading.classList.add('hidden');
}

function showResults() {
    results.classList.remove('hidden');
}

function hideResults() {
    results.classList.add('hidden');
}

function showError(message) {
    error.textContent = message;
    error.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    error.classList.add('hidden');
}

function insertQuickFilter(text) {
    const currentQuery = userQuery.value.trim();
    if (currentQuery) {
        userQuery.value = currentQuery + ' ' + text;
    } else {
        userQuery.value = text;
    }
    userQuery.focus();
}