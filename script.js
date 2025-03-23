async function getWeather() {
    const cityInput = document.getElementById('city-input');
    const weatherInfo = document.getElementById('weather-info');
    const city = cityInput.value.trim();

    if (!city) {
        showError('Please enter a city name');
        return;
    }

    weatherInfo.innerHTML = '<p class="loading">Loading weather data...</p>';
    weatherInfo.classList.add('active');

    try {
        const response = await fetch(`http://localhost:5000/weather?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch weather data');
        }

        displayWeather(data);
    } catch (error) {
        showError(error.message || 'Error fetching weather data. Please try again.');
        console.error('Error:', error);
    }
}

function formatRainData(rainValue) {
    return rainValue === undefined || rainValue === 0 ? 'No data' : `${rainValue} mm`;
}

function displayWeather(data) {
    const weatherInfo = document.getElementById('weather-info');
    weatherInfo.innerHTML = `
        <h2>${data.city}</h2>
        <p class="temperature">${data.temp_celsius}°C / ${data.temp_fahrenheit}°F</p>
        <p class="description">${data.description}</p>
        <div class="weather-details">
            <div class="detail-item">
                <p>Feels like: ${data.feels_like_celsius}°C / ${data.feels_like_fahrenheit}°F</p>
            </div>
            <div class="detail-item">
                <p>Humidity: ${data.humidity}%</p>
            </div>
            <div class="detail-item">
                <p>Wind Speed: ${data.wind_speed} m/s</p>
            </div>
            <div class="detail-item">
                <p>Rain (1h): ${formatRainData(data.rain_1h)}</p>
            </div>
            <div class="detail-item">
                <p>Rain (3h): ${formatRainData(data.rain_3h)}</p>
            </div>
            <div class="detail-item">
                <p>Precipitation Probability: ${data.precipitation_probability}%</p>
            </div>
            <div class="detail-item">
                <p>Sunrise: ${data.sunrise}</p>
            </div>
            <div class="detail-item">
                <p>Sunset: ${data.sunset}</p>
            </div>
        </div>
    `;
    weatherInfo.classList.add('active');
}

function showError(message) {
    const weatherInfo = document.getElementById('weather-info');
    weatherInfo.innerHTML = `<p class="error-message active">${message}</p>`;
    weatherInfo.classList.add('active');
}

document.getElementById('city-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        getWeather();
    }
}); 