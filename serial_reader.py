import serial
import sqlite3
import time

# Setup Serial Connection
ser = serial.Serial('/dev/cu.usbmodem11101', 9600)
time.sleep(2)  # Allow Arduino reset

# Setup SQLite Database
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        soil_moisture INTEGER,
        temperature REAL,
        humidity REAL
    )
''')
conn.commit()

print("Listening for Arduino data...")

# Main loop
while True:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        print("Received:", line)

        try:
            parts = line.split('|')
            soil = int(parts[0].split(':')[1].replace('%', '').strip())
            temp = float(parts[1].split(':')[1].replace('°C', '').strip())
            hum = float(parts[2].split(':')[1].replace('%', '').strip())

            cursor.execute('''
                INSERT INTO sensor_readings (soil_moisture, temperature, humidity)
                VALUES (?, ?, ?)
            ''', (soil, temp, hum))
            conn.commit()

            print("Saved to database.")

        except Exception as e:
            print("Error parsing line:", e)