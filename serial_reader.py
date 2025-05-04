import serial
import time
from app.database import insert_sensor_data, create_table, get_fan_mode  # Make sure get_fan_mode exists

# Setup Serial Connection
ser = serial.Serial('/dev/cu.usbmodem31101', 9600)
time.sleep(2)

# Setup DB
create_table()

print("Listening for Arduino data...")

last_command_sent = ""

while True:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        print("Received:", line)

        try:
            parts = line.split('|')
            temp = float(parts[0].split(':')[1].replace('°C', '').strip())
            hum = float(parts[1].split(':')[1].replace('%', '').strip())
            soil = int(parts[2].split(':')[1].replace('%', '').strip())

            insert_sensor_data(soil, temp, hum)
            print("Saved to PostgreSQL database.")

        except Exception as e:
            print("Error parsing line:", e)

    # --- Send fan mode command ---
    try:
        fan_mode = get_fan_mode()  # This should return 'AUTO', 'ON', or 'OFF'

        if fan_mode != last_command_sent:
            if fan_mode == "ON":
                ser.write(b"FAN_ON\n")
            elif fan_mode == "OFF":
                ser.write(b"FAN_OFF\n")
            elif fan_mode == "AUTO":
                ser.write(b"FAN_AUTO\n")

            print(f"Sent command to Arduino: FAN_{fan_mode}")
            last_command_sent = fan_mode

    except Exception as e:
        print("Error sending fan command:", e)

    time.sleep(1)
