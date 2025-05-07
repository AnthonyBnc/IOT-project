import psycopg2
import os
from dotenv import load_dotenv
import datetime

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

def get_historical_data(hours=24):
    """Get sensor data from the last specified hours for analysis and charting."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT soil_moisture, temperature, humidity, timestamp
            FROM sensor_data
            WHERE timestamp > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp ASC;
        """, (hours,))
        rows = cursor.fetchall()
        
        # Format the data for charts
        timestamps = []
        soil_data = []
        temp_data = []
        humidity_data = []
        
        for row in rows:
            soil, temp, hum, time = row
            timestamps.append(time.strftime('%Y-%m-%d %H:%M:%S'))
            soil_data.append(soil)
            temp_data.append(float(temp))
            humidity_data.append(float(hum))
        
        return {
            'timestamps': timestamps,
            'soil_moisture': soil_data,
            'temperature': temp_data,
            'humidity': humidity_data
        }
    except Exception as e:
        print(f"Error retrieving historical data: {e}")
        return {
            'timestamps': [],
            'soil_moisture': [],
            'temperature': [],
            'humidity': []
        }
    finally:
        cursor.close()
        conn.close()

def get_all_historical_data():
    """Get all sensor data from database without time restriction, optimized for large datasets."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # First check the total count of records for optimization decisions
        cursor.execute("SELECT COUNT(*) FROM sensor_data")
        total_count = cursor.fetchone()[0]
        
        # If there are too many records, consider downsampling
        if total_count > 1000:
            # Use a downsampling strategy - take every Nth record
            sampling_rate = max(1, total_count // 1000)
            
            cursor.execute("""
                SELECT soil_moisture, temperature, humidity, timestamp
                FROM (
                    SELECT soil_moisture, temperature, humidity, timestamp, 
                           ROW_NUMBER() OVER (ORDER BY timestamp) as row_num
                    FROM sensor_data
                ) as numbered
                WHERE row_num % %s = 0
                ORDER BY timestamp ASC;
            """, (sampling_rate,))
        else:
            # Get all data if the dataset is not too large
            cursor.execute("""
                SELECT soil_moisture, temperature, humidity, timestamp
                FROM sensor_data
                ORDER BY timestamp ASC;
            """)
        
        rows = cursor.fetchall()
        
        # Format the data for charts
        timestamps = []
        soil_data = []
        temp_data = []
        humidity_data = []
        
        for row in rows:
            soil, temp, hum, time = row
            timestamps.append(time.strftime('%Y-%m-%d %H:%M:%S'))
            soil_data.append(soil)
            temp_data.append(float(temp))
            humidity_data.append(float(hum))
        
        return {
            'timestamps': timestamps,
            'soil_moisture': soil_data,
            'temperature': temp_data,
            'humidity': humidity_data,
            'total_count': total_count,
            'displayed_count': len(rows)
        }
    except Exception as e:
        print(f"Error retrieving all historical data: {e}")
        return {
            'timestamps': [],
            'soil_moisture': [],
            'temperature': [],
            'humidity': [],
            'total_count': 0,
            'displayed_count': 0
        }
    finally:
        cursor.close()
        conn.close()
