const WEATHERAPI_KEY = 'c0f4dd8438534ba0b3b184030251504'; 

document.addEventListener('DOMContentLoaded', () => {
    const cityInput = document.getElementById('city-input');
    const searchBtn = document.getElementById('search-btn');
    const errorDiv = document.getElementById('error');
    const weatherCard = document.getElementById('weather-card');
    const cityName = document.getElementById('city-name');
    const weatherInfo = document.getElementById('weather-info');

    const weatherIcons = {
        'Sunny': '☀️',
        'Clear': '🌙',
        'Cloudy': '☁️',
        'Rain': '🌧️',
        'Snow': '❄️'
    };

    async function getWeather(city) {
        try {
            const response = await fetch(
                `https://api.weatherapi.com/v1/current.json?key=${WEATHERAPI_KEY}&q=${city}&lang=ru`
            );
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error?.message || 'Ошибка запроса');
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(error.message);
        }
    }

    function displayWeather(data) {
        const weather = data.current.condition.text;
        
        cityName.textContent = `${data.location.name}, ${data.location.country}`;
        weatherInfo.innerHTML = `
            <div class="weather-icon">${weatherIcons[data.current.condition.text] || '🌈'}</div>
            <div class="weather-item">
                <span>🌡️ Температура:</span>
                <span>${Math.round(data.current.temp_c)}°C</span>
            </div>
            <div class="weather-item">
                <span>💨 Ощущается:</span>
                <span>${Math.round(data.current.feelslike_c)}°C</span>
            </div>
            <div class="weather-item">
                <span>☁️ Погода:</span>
                <span>${weather}</span>
            </div>
            <div class="weather-item">
                <span>💧 Влажность:</span>
                <span>${data.current.humidity}%</span>
            </div>
            <div class="weather-item">
                <span>🌬️ Ветер:</span>
                <span>${data.current.wind_kph} км/ч</span>
            </div>
        `;
        weatherCard.style.display = 'block';
        errorDiv.style.display = 'none';
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        weatherCard.style.display = 'none';
    }

    searchBtn.addEventListener('click', async () => {
        const city = cityInput.value.trim();
        if (!city) {
            showError('Введите название города');
            return;
        }
        
        try {
            const weatherData = await getWeather(city);
            displayWeather(weatherData);
        } catch (error) {
            showError(`Ошибка: ${error.message}`);
        }
    });

    cityInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchBtn.click();
    });
});