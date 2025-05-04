import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    # Create sensor_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id SERIAL PRIMARY KEY,
            soil_moisture INT,
            temperature FLOAT,
            humidity FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create fan_control table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fan_control (
            id SERIAL PRIMARY KEY,
            mode VARCHAR(10) NOT NULL DEFAULT 'AUTO',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Ensure at least one fan control row exists
    cursor.execute("SELECT COUNT(*) FROM fan_control;")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("INSERT INTO fan_control (mode) VALUES ('AUTO');")

    conn.commit()
    cursor.close()
    conn.close()

def insert_sensor_data(soil, temp, hum):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sensor_data (soil_moisture, temperature, humidity)
        VALUES (%s, %s, %s);
    """, (soil, temp, hum))
    conn.commit()
    cursor.close()
    conn.close()

def get_latest_reading():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT soil_moisture, temperature, humidity, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 1;
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def get_fan_mode():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mode FROM fan_control
        ORDER BY updated_at DESC
        LIMIT 1;
    """)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else "AUTO"

def set_fan_mode(mode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fan_control (mode, updated_at)
        VALUES (%s, CURRENT_TIMESTAMP);
    """, (mode,))
    conn.commit()
    cursor.close()
    conn.close()
