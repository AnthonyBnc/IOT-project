import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id SERIAL PRIMARY KEY,
            soil_moisture INT,
            temperature FLOAT,
            humidity FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
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
