import sqlite3

def get_latest_reading():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT soil_moisture, temperature, humidity, timestamp FROM sensor_readings ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    return row
