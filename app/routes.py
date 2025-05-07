from flask import Blueprint, render_template, jsonify, request
from .database import get_latest_reading, get_historical_data, get_all_historical_data

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

@main.route('/api/history')
def history_api():
    hours = request.args.get('hours', default=24, type=int)
    data = get_historical_data(hours)
    
    if data and len(data['timestamps']) > 0:
        # Format timestamps for better handling in JavaScript
        formatted_data = {
            'timestamps': data['timestamps'],
            'temperature': data['temperature'],
            'humidity': data['humidity'],
            'soil_moisture': data['soil_moisture']
        }
        return jsonify(formatted_data)
    else:
        return jsonify({
            'error': 'No historical data available'
        }), 404

@main.route('/api/all-history')
def all_history_api():
    """Return all historical data without time restriction."""
    data = get_all_historical_data()
    
    if data and len(data['timestamps']) > 0:
        # Format timestamps for better handling in JavaScript
        formatted_data = {
            'timestamps': data['timestamps'],
            'temperature': data['temperature'],
            'humidity': data['humidity'],
            'soil_moisture': data['soil_moisture'],
            'total_count': data.get('total_count', len(data['timestamps'])),
            'displayed_count': data.get('displayed_count', len(data['timestamps']))
        }
        return jsonify(formatted_data)
    else:
        return jsonify({
            'error': 'No historical data available'
        }), 404

@main.route('/visualization')
def visualization():
    """Display a dedicated page with comprehensive data visualization."""
    # Get the latest reading for current stats
    reading = get_latest_reading()
    
    # Get all historical data for initial loading
    data = get_all_historical_data()
    data_count = len(data['timestamps']) if data and 'timestamps' in data else 0
    
    if reading:
        soil_moisture, temperature, humidity, timestamp = reading
        return render_template('visualization.html',
                              soil=soil_moisture,
                              temp=temperature,
                              hum=humidity,
                              time=timestamp,
                              data_count=data_count,
                              show_all_data=True)
    else:
        return render_template('visualization.html',
                              data_count=data_count,
                              show_all_data=True)
    