import serial
import time
from app.database import insert_sensor_data, create_table

# Setup Serial Connection
ser = serial.Serial('/dev/cu.usbmodem31101', 9600)
time.sleep(2)  # Allow Arduino reset

# Setup PostgreSQL Table (optional)
create_table()

print("Listening for Arduino data...")

# Main loop
while True:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        print("Received:", line)

        try:
            parts = line.split('|')
            temp = float(parts[0].split(':')[1].replace('°C', '').strip())
            hum = float(parts[1].split(':')[1].replace('%', '').strip())
            soil = int(parts[2].split(':')[1].replace('%', '').strip())

            print(f"Trying to insert: Soil={soil}%, Temp={temp}°C, Hum={hum}%")

            # Insert into PostgreSQL database
            insert_sensor_data(soil, temp, hum)
            print("Saved to PostgreSQL database.")

        except Exception as e:
            print("Error parsing line:", e)

    time.sleep(1)  # Small delay to avoid overwhelming the serial port
