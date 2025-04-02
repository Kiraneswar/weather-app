import datetime as dt
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from requests.exceptions import RequestException

app = Flask(__name__)
CORS(app)

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct?"
API_KEY = open('api_key.txt', 'r').read().strip()

@app.route('/cities/search')
def search_cities():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    try:
        # List of major cities in Andhra Pradesh and Telangana
        indian_cities = [
            # Andhra Pradesh Cities
            {"name": "Visakhapatnam", "state": "Andhra Pradesh"},
            {"name": "Vijayawada", "state": "Andhra Pradesh"},
            {"name": "Guntur", "state": "Andhra Pradesh"},
            {"name": "Nellore", "state": "Andhra Pradesh"},
            {"name": "Kurnool", "state": "Andhra Pradesh"},
            {"name": "Kakinada", "state": "Andhra Pradesh"},
            {"name": "Tirupati", "state": "Andhra Pradesh"},
            {"name": "Anantapur", "state": "Andhra Pradesh"},
            {"name": "Kadapa", "state": "Andhra Pradesh"},
            {"name": "Rajahmundry", "state": "Andhra Pradesh"},
            {"name": "Eluru", "state": "Andhra Pradesh"},
            {"name": "Ongole", "state": "Andhra Pradesh"},
            {"name": "Nandyal", "state": "Andhra Pradesh"},
            {"name": "Machilipatnam", "state": "Andhra Pradesh"},
            {"name": "Adoni", "state": "Andhra Pradesh"},
            {"name": "Chittor", "state": "Andhra Pradesh"},
            {"name": "Srikakulam", "state": "Andhra Pradesh"},
            {"name": "Bhimavaram", "state": "Andhra Pradesh"},
            {"name": "Hindupur", "state": "Andhra Pradesh"},
            {"name": "Madanapalle", "state": "Andhra Pradesh"},
            {"name": "Guntakal", "state": "Andhra Pradesh"},
            {"name": "Dharmavaram", "state": "Andhra Pradesh"},
            {"name": "Gudivada", "state": "Andhra Pradesh"},
            {"name": "Narasaraopet", "state": "Andhra Pradesh"},
            {"name": "Proddatur", "state": "Andhra Pradesh"},
            {"name": "Tadepalligudem", "state": "Andhra Pradesh"},
            
            # Telangana Cities
            {"name": "Hyderabad", "state": "Telangana"},
            {"name": "Warangal", "state": "Telangana"},
            {"name": "Nizamabad", "state": "Telangana"},
            {"name": "Karimnagar", "state": "Telangana"},
            {"name": "Khammam", "state": "Telangana"},
            {"name": "Ramagundam", "state": "Telangana"},
            {"name": "Secunderabad", "state": "Telangana"},
            {"name": "Mahbubnagar", "state": "Telangana"},
            {"name": "Nalgonda", "state": "Telangana"},
            {"name": "Adilabad", "state": "Telangana"},
            {"name": "Suryapet", "state": "Telangana"},
            {"name": "Miryalaguda", "state": "Telangana"},
            {"name": "Siddipet", "state": "Telangana"},
            {"name": "Kamareddy", "state": "Telangana"},
            {"name": "Mancherial", "state": "Telangana"},
            {"name": "Bodhan", "state": "Telangana"},
            {"name": "Jagitial", "state": "Telangana"},
            {"name": "Sangareddy", "state": "Telangana"},
            {"name": "Bhongir", "state": "Telangana"},
            {"name": "Medak", "state": "Telangana"},
            {"name": "Wanaparthy", "state": "Telangana"},
            {"name": "Kothagudem", "state": "Telangana"},
            {"name": "Tandur", "state": "Telangana"},
            {"name": "Vikarabad", "state": "Telangana"},
            {"name": "Nirmal", "state": "Telangana"}
        ]
        
        # Filter cities based on substring match
        matching_cities = [
            city for city in indian_cities
            if query in city['name'].lower()
        ]
        
        # Sort cities by name
        matching_cities.sort(key=lambda x: x['name'])
        
        return jsonify(matching_cities)
    except Exception as e:
        print(f"Error in city search: {str(e)}")
        return jsonify([])

@app.route('/weather')
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City name is required'}), 400

    url = BASE_URL + "appid=" + API_KEY + "&q=" + city
    
    try:
        response = requests.get(url, timeout=10, verify=True)
        response.raise_for_status()  
        data = response.json()

        if 'main' in data:
            # Get local time for the city using timezone offset
            timezone_offset = data['timezone']
            local_time = dt.datetime.utcnow() + dt.timedelta(seconds=timezone_offset)
            
            # Format date and time
            current_date = local_time.strftime('%B %d, %Y')
            current_time = local_time.strftime('%I:%M %p')

            temp_kelvin = data['main']['temp']
            temp_celsius, temp_fahrenheit = kelvin_to_celsius_fahrenheit(temp_kelvin)
            feels_like_kelvin = data['main']['feels_like']
            feels_like_celsius, feels_like_fahrenheit = kelvin_to_celsius_fahrenheit(feels_like_kelvin)
            wind_speed = data['wind']['speed']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            sunrise = dt.datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone']).strftime('%H:%M')
            sunset = dt.datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone']).strftime('%H:%M')
            
            rain_data = data.get('rain', {})
            rain_1h = rain_data.get('1h', None) 
            rain_3h = rain_data.get('3h', None)  
            
            precipitation_prob = 0
            if 'rain' in description.lower():
                precipitation_prob = 100
            elif 'cloud' in description.lower():
                precipitation_prob = 50
            elif 'clear' in description.lower():
                precipitation_prob = 0
            else:
                precipitation_prob = 25

            return jsonify({
                'city': city,
                'current_date': current_date,
                'current_time': current_time,
                'temp_celsius': round(temp_celsius, 2),
                'temp_fahrenheit': round(temp_fahrenheit, 2),
                'feels_like_celsius': round(feels_like_celsius, 2),
                'feels_like_fahrenheit': round(feels_like_fahrenheit, 2),
                'humidity': humidity,
                'wind_speed': wind_speed,
                'description': description,
                'sunrise': sunrise,
                'sunset': sunset,
                'rain_1h': round(rain_1h, 2) if rain_1h is not None else None,
                'rain_3h': round(rain_3h, 2) if rain_3h is not None else None,
                'precipitation_probability': precipitation_prob
            })
        else:
            return jsonify({'error': f"Error fetching weather data for {city}"}), 404

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error. Please check your internet connection.'}), 503
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching weather data: {str(e)}'}), 500

def kelvin_to_celsius_fahrenheit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius, fahrenheit

if __name__ == '__main__':
    app.run(debug=True)
