from flask import Flask, jsonify, request
import random
import time
import logging
import RPi.GPIO as gpio  # Import GPIO library for Raspberry Pi
from flask_cors import CORS

# Set up logging to console
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing to allow communication with React

# GPIO setup for the relay
RELAY_PIN = 36
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)
gpio.setup(RELAY_PIN, gpio.OUT)

# Normal and high ranges for weather parameters
normal_ranges = {
    "temperature": (60, 85),  # Fahrenheit
    "humidity": (30, 60),  # Percentage
    "wind_speed": (0, 15),  # mph
    "wind_degree": (0, 360),  # Degrees
}

high_ranges = {
    "temperature": (85, 110),  # Fahrenheit
    "humidity": (60, 100),  # Percentage
    "wind_speed": (15, 30),  # mph
    "wind_degree": (0, 360),  # Degrees
}

# Possible weather conditions
weather_conditions = [
    "Clear", "Cloudy", "Rainy", "Stormy", "Snowy", "Foggy", "Windy"
]

def generate_weather_readings(range_type='normal'):
    """Generate random weather readings based on a specified range (normal or high)."""
    def get_reading(parameter, range_type):
        if range_type == 'high':
            return random.randint(*high_ranges[parameter])
        else:
            return random.randint(*normal_ranges[parameter])

    # Generate weather readings
    weather_data = {
        "temperature": get_reading("temperature", range_type),
        "humidity": get_reading("humidity", range_type),
        "wind_speed": random.randint(0, 30),  # Wind speed can vary
        "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
        "wind_degree": random.randint(0, 360),  # Wind degrees
        "weather_description": random.choice(weather_conditions),  # Weather condition
        "soil_moisture": random.randint(300, 700)  # Soil moisture range
    }

    # Add soil moisture classification
    weather_data["soil_status"] = "Wet" if weather_data["soil_moisture"] < 500 else "Dry"

    # Log the generated weather data
    logging.debug("Weather Data:")
    logging.debug(f"Temperature: {weather_data['temperature']}°F")
    logging.debug(f"Humidity: {weather_data['humidity']}%")
    logging.debug(f"Wind Speed: {weather_data['wind_speed']} mph")
    logging.debug(f"Wind Direction: {weather_data['wind_direction']}")
    logging.debug(f"Wind Degree: {weather_data['wind_degree']}°")
    logging.debug(f"Weather Condition: {weather_data['weather_description']}")
    logging.debug(f"Soil Moisture: {weather_data['soil_moisture']} (Status: {weather_data['soil_status']})")
    logging.debug("-" * 40)  # Separator line

    return weather_data

def control_relay(soil_status):
    """Control relay based on soil status."""
    if soil_status == "Dry":
        gpio.output(RELAY_PIN, 1)  # Turn relay ON
        logging.debug("Relay ON - Soil is Dry")
    else:
        gpio.output(RELAY_PIN, 0)  # Turn relay OFF
        logging.debug("Relay OFF - Soil is Wet")

@app.route('/weather-data', methods=['GET'])
def weather_data():
    """Endpoint to return simulated weather data."""
    range_type = request.args.get('range', 'normal')  # Allow user to specify 'normal' or 'high' range
    data = generate_weather_readings(range_type)

    # Control relay based on soil status
    control_relay(data["soil_status"])

    time.sleep(10)  # Simulate delay
    return jsonify(data)

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        gpio.cleanup()
