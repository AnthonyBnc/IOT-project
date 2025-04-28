from flask import Blueprint, render_template, jsonify
from .database import get_latest_reading

main = Blueprint('main', __name__)

@main.route('/')
def dashboard():
    reading = get_latest_reading()

    if reading:
        soil_moisture, temperature, humidity, timestamp = reading
        return render_template('dashboard.html',
                               soil=soil_moisture,
                               temp=temperature,
                               hum=humidity,
                               time=timestamp)
    else:
        return "No data yet."

# New route: API to get live sensor data
@main.route('/api/sensor')
def sensor_api():
    reading = get_latest_reading()

    if reading:
        soil_moisture, temperature, humidity, timestamp = reading
        return jsonify({
            'soil_moisture': soil_moisture,
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': timestamp
        })
    else:
        return jsonify({
            'error': 'No data available'
        }), 404
