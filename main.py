import datetime as dt
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from requests.exceptions import RequestException

app = Flask(__name__)
CORS(app)

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = open('api_key.txt', 'r').read().strip()

def kelvin_to_celsius_fahrenheit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius, fahrenheit

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

if __name__ == '__main__':
    app.run(debug=True)
