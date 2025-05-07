from database import get_connection, get_historical_data

def analyze_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get total number of readings
    cursor.execute('SELECT COUNT(*) FROM sensor_data')
    total_readings = cursor.fetchone()[0]
    print(f'Total sensor readings: {total_readings}')
    
    # Get time range
    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM sensor_data')
    min_time, max_time = cursor.fetchone()
    print(f'Data range: {min_time} to {max_time}')
    
    # Get basic statistics
    cursor.execute('''
        SELECT 
            AVG(temperature), MIN(temperature), MAX(temperature),
            AVG(humidity), MIN(humidity), MAX(humidity),
            AVG(soil_moisture), MIN(soil_moisture), MAX(soil_moisture)
        FROM sensor_data
    ''')
    stats = cursor.fetchone()
    print(f'Temperature: avg={stats[0]:.2f}°C, min={stats[1]:.2f}°C, max={stats[2]:.2f}°C')
    print(f'Humidity: avg={stats[3]:.2f}%, min={stats[4]:.2f}%, max={stats[5]:.2f}%')
    print(f'Soil Moisture: avg={stats[6]:.2f}%, min={stats[7]}%, max={stats[8]}%')
    
    # Get critical conditions frequency
    cursor.execute('''
        SELECT COUNT(*) FROM sensor_data 
        WHERE temperature > 35.0 AND humidity < 30.0
    ''')
    extreme_heat_dry = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM sensor_data 
        WHERE humidity > 60.0 OR temperature > 30.0
    ''')
    high_humid_temp = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM sensor_data 
        WHERE soil_moisture <= 5
    ''')
    low_soil = cursor.fetchone()[0]
    
    print('\nCondition Analysis:')
    print(f'- Extreme Heat and Dryness (Fan ON): {extreme_heat_dry} readings ({extreme_heat_dry/total_readings*100:.2f}%)')
    print(f'- High Humidity or Temperature (Fan ON): {high_humid_temp} readings ({high_humid_temp/total_readings*100:.2f}%)')
    print(f'- Low Soil Moisture (Buzzer Alert): {low_soil} readings ({low_soil/total_readings*100:.2f}%)')
    print(f'- Normal Conditions (Fan OFF): {total_readings - extreme_heat_dry - high_humid_temp - low_soil} readings ({(total_readings - extreme_heat_dry - high_humid_temp - low_soil)/total_readings*100:.2f}%)')
    
    # Get fan mode stats
    try:
        cursor.execute('''
            SELECT mode, COUNT(*) 
            FROM fan_control 
            GROUP BY mode 
            ORDER BY COUNT(*) DESC
        ''')
        fan_modes = cursor.fetchall()
        print('\nFan Mode Usage:')
        for mode, count in fan_modes:
            print(f'- {mode}: {count} times')
    except Exception as e:
        print(f'Error getting fan modes: {e}')
    
    # Recent readings
    cursor.execute('''
        SELECT soil_moisture, temperature, humidity, timestamp 
        FROM sensor_data 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''')
    recent = cursor.fetchall()
    print('\nMost Recent Readings:')
    for soil, temp, humid, time in recent:
        print(f'Time: {time}, Temp: {temp:.2f}°C, Humidity: {humid:.2f}%, Soil: {soil}%')
    
    cursor.close()
    conn.close()
    
    # Test historical data
    hist_data = get_historical_data(24)
    records = len(hist_data['timestamps'])
    print(f'\nHistorical Data: Retrieved {records} records for the last 24 hours')
    if records > 0:
        print(f'First timestamp: {hist_data["timestamps"][0]}')
        print(f'Last timestamp: {hist_data["timestamps"][-1]}')

if __name__ == "__main__":
    analyze_data() 