from flask import Blueprint, render_template, jsonify, request
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

fan_state = False

@main.route('/api/fan', methods=['POST'])
def toggle_fan():
    global fan_state
    action = request.json.get('action')

    if action == 'on':
        fan_state = True
    elif action == 'off':
        fan_state = False

    return jsonify({'fan_state': fan_state})

@main.route('/api/fan', methods=['GET'])
def get_fan_state():
    global fan_state
    return jsonify({'fan_state': fan_state})
    