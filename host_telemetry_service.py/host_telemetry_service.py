import serial
import time
import requests
import json
import sys

# הגדרת פורט ה-USB של ה-ESP32 (יש לשנות לפורט הנכון במחשב שלך)
SERIAL_PORT = 'COM3' 
BAUD_RATE = 115200

def get_telemetry_data():
    try:
        # פנייה לשרת המקומי של LibreHardwareMonitor
        response = requests.get('http://localhost:8085/data.json')
        if response.status_code == 200:
            data = response.json()
            return parse_hardware_data(data)
        else:
            print(f"Error fetching data: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error to LibreHardwareMonitor: {e}")
        return None

def parse_hardware_data(data):
    # הפונקציה הזו תשתנה בהתאם למבנה ה-JSON הספציפי של המחשב שלך
    # כרגע נשתמש בנתוני דמה לצורך הבדיקה
    cpu_temp = 45.2
    gpu_temp = 52.1
    return f"{cpu_temp},{gpu_temp}"

def main():
    try:
        print(f"Connecting to {SERIAL_PORT}...")
        serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected successfully.")
        
        while True:
            hardware_metrics = get_telemetry_data()
            if hardware_metrics:
                # עטיפת הנתונים בסימנים מוסכמים למניעת קריסות (Data Framing)
                payload = f"<{hardware_metrics}>"
                
                # שליחת הנתונים ל-ESP32
                serial_port.write(payload.encode('utf-8'))
                print(f"Sent: {payload}")
                
            time.sleep(1) # קצב רענון של פעם בשנייה
            
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping telemetry service.")
        if 'serial_port' in locals() and serial_port.is_open:
            serial_port.close()
        sys.exit(0)

if __name__ == "__main__":
    main()