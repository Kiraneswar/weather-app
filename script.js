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
        <div class="datetime-info">
            <p class="date">${data.current_date}</p>
            <p class="time">${data.current_time}</p>
        </div>
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

let timeoutId = null;

document.getElementById('city-input').addEventListener('input', function(e) {
    const query = e.target.value.trim();
    const suggestionsList = document.getElementById('city-suggestions');
    
    // Clear previous timeout to prevent multiple requests
    if (timeoutId) {
        clearTimeout(timeoutId);
    }
    
    // Clear suggestions if input is empty
    if (!query) {
        suggestionsList.innerHTML = '';
        suggestionsList.style.display = 'none';
        return;
    }
    
    // Reduce timeout delay to 150ms for faster response
    timeoutId = setTimeout(async () => {
        if (query.length >= 1) { // Reduced to 1 character to show results faster
            try {
                const response = await fetch(`http://localhost:5000/cities/search?q=${encodeURIComponent(query)}`);
                if (!response.ok) throw new Error('Network response was not ok');
                const cities = await response.json();
                
                // Enhanced display of city suggestions
                if (cities.length > 0) {
                    suggestionsList.innerHTML = cities.map(city => `
                        <li onclick="selectCity('${city.name}, ${city.state || 'India'}')" 
                            class="city-suggestion-item">
                            <div class="city-info">
                                <span class="city-name">${highlightMatch(city.name, query)}</span>
                                ${city.state ? `<span class="city-state">${city.state}</span>` : ''}
                            </div>
                        </li>
                    `).join('');
                    suggestionsList.style.display = 'block';
                } else {
                    suggestionsList.innerHTML = '<li class="no-results">No cities found</li>';
                    suggestionsList.style.display = 'block';
                }
            } catch (error) {
                console.error('Error fetching city suggestions:', error);
                suggestionsList.innerHTML = '<li class="error">Error fetching cities</li>';
                suggestionsList.style.display = 'block';
            }
        }
    }, 150); // Reduced delay
});

// Function to highlight the matched text
function highlightMatch(cityName, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return cityName.replace(regex, '<strong>$1</strong>');
}

// Add keyboard navigation
document.getElementById('city-input').addEventListener('keydown', function(e) {
    const suggestionsList = document.getElementById('city-suggestions');
    const suggestions = suggestionsList.getElementsByTagName('li');
    let currentFocus = -1;

    if (suggestions.length > 0) {
        if (e.key === 'ArrowDown') {
            currentFocus++;
            addActive(suggestions, currentFocus);
            e.preventDefault();
        } else if (e.key === 'ArrowUp') {
            currentFocus--;
            addActive(suggestions, currentFocus);
            e.preventDefault();
        } else if (e.key === 'Enter') {
            if (currentFocus > -1) {
                suggestions[currentFocus].click();
            }
        }
    }
});

function addActive(suggestions, currentFocus) {
    if (!suggestions) return;
    removeActive(suggestions);
    if (currentFocus >= suggestions.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = suggestions.length - 1;
    suggestions[currentFocus].classList.add('active');
}

function removeActive(suggestions) {
    for (let i = 0; i < suggestions.length; i++) {
        suggestions[i].classList.remove('active');
    }
}

function selectCity(cityName) {
    document.getElementById('city-input').value = cityName;
    document.getElementById('city-suggestions').style.display = 'none';
    getWeather();
}

// Close suggestions when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.closest('.autocomplete-wrapper')) {
        document.getElementById('city-suggestions').style.display = 'none';
    }
}); 