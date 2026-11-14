import requests
import time
import serial
import serial.tools.list_ports

# Function to automatically find the ESP32-S3 COM port
def find_esp32_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Check description for standard USB Serial devices
        if "USB" in port.description or "Serial" in port.description:
            return port.device
    return None

def get_max_telemetry():
    url = "http://localhost:8085/data.json"
    
    # Locate and connect to the ESP32-S3 via Serial (USB)
    esp_port = find_esp32_port()
    if not esp_port:
        print("Error: Could not find ESP32-S3. Please check the USB connection.")
        return

    try:
        # Open serial connection matching the C firmware baud rate (115200)
        ser = serial.Serial(esp_port, 115200, timeout=1)
        print(f"Connected to ESP32 on {esp_port}")
        print("--- Starting ULTIMATE hardware telemetry (Press Ctrl+C to stop) ---")
    except Exception as e:
        print(f"Failed to open Serial port: {e}")
        return
    
    while True:
        try:
            # Fetch data from LibreHardwareMonitor local server
            response = requests.get(url, timeout=2)
            data = response.json()
            
            # Dictionary to store the latest metrics
            metrics = {
                "cpu_temp": "N/A", "cpu_power": "N/A", "cpu_load": "N/A", "cpu_clock": "N/A",
                "gpu_temp": "N/A", "gpu_power": "N/A", "gpu_load": "N/A", "gpu_clock": "N/A",
                "gpu_vram": "N/A", "ram_used": "N/A",
                "fps": "N/A", "fps_low": "N/A", "frametime": "N/A"
            }
            
            # Recursive function to parse the JSON tree
            def parse_node(node, current_hw=""):
                text = node.get("Text", "").lower()
                value = node.get("Value", "")
                val_lower = value.lower()
                
                # Identify hardware category
                if any(k in text for k in ["gpu", "radeon", "nvidia", "geforce", "rtx", "gtx"]):
                    current_hw = "gpu"
                elif any(k in text for k in ["cpu", "ryzen", "intel", "core"]):
                    current_hw = "cpu"
                elif "rtss" in text or "rivatuner" in text:
                    current_hw = "fps"
                elif "memory" in text and current_hw == "":
                    current_hw = "ram"
                    
                # Extract numeric value only
                val_num = ''.join(c for c in value if c.isdigit() or c == '.')

                # Temperature parsing
                if "\u00b0c" in val_lower or " c" in val_lower or value.endswith("C"):
                    if current_hw == "cpu" and metrics["cpu_temp"] == "N/A" and val_num:
                        metrics["cpu_temp"] = val_num
                    elif current_hw == "gpu" and metrics["gpu_temp"] == "N/A" and val_num:
                        metrics["gpu_temp"] = val_num
                        
                # Power consumption parsing (Watts)
                elif " w" in val_lower:
                    if current_hw == "cpu" and ("package" in text or metrics["cpu_power"] == "N/A") and val_num:
                        metrics["cpu_power"] = val_num
                    elif current_hw == "gpu" and (any(k in text for k in ["total", "package", "gpu power"]) or metrics["gpu_power"] == "N/A") and val_num:
                        metrics["gpu_power"] = val_num

                # Load percentage parsing
                elif "%" in value:
                    if current_hw == "cpu" and ("total" in text or metrics["cpu_load"] == "N/A") and val_num:
                        metrics["cpu_load"] = val_num
                    elif current_hw == "gpu" and ("core" in text or metrics["gpu_load"] == "N/A") and val_num:
                        metrics["gpu_load"] = val_num
                        
                # Clock speed parsing (MHz)
                elif "mhz" in val_lower:
                    if current_hw == "cpu" and ("core" in text or metrics["cpu_clock"] == "N/A") and val_num:
                        metrics["cpu_clock"] = val_num
                    elif current_hw == "gpu" and ("core" in text or metrics["gpu_clock"] == "N/A") and val_num:
                        metrics["gpu_clock"] = val_num

                # Memory usage parsing (convert MB to GB dynamically)
                elif "gb" in val_lower or "mb" in val_lower:
                    is_gb = "gb" in val_lower
                    num_val = float(val_num) if val_num else 0
                    display_val = f"{num_val:.1f}GB" if is_gb else f"{(num_val/1024):.1f}GB"
                    
                    if current_hw == "gpu" and "used" in text and metrics["gpu_vram"] == "N/A" and val_num:
                        metrics["gpu_vram"] = display_val
                    elif current_hw == "ram" and "used" in text and metrics["ram_used"] == "N/A" and val_num:
                        metrics["ram_used"] = display_val

                # FPS and Frametime parsing
                if current_hw == "fps":
                    if "0.1%" in text or "low" in text:
                        if val_num and metrics["fps_low"] == "N/A": metrics["fps_low"] = val_num
                    elif "frametime" in text or "ms" in val_lower:
                        if val_num and metrics["frametime"] == "N/A": metrics["frametime"] = val_num
                    elif "fps" in val_lower or "framerate" in text:
                        if val_num and metrics["fps"] == "N/A": metrics["fps"] = val_num

                # Traverse child nodes
                for child in node.get("Children", []):
                    parse_node(child, current_hw)

            # Start JSON parsing
            parse_node(data)
            
            # Format lines exactly as the C firmware expects them
            cpu_line = f"CPU: {metrics['cpu_temp']}C | {metrics['cpu_power']}W | {metrics['cpu_load']}%\n"
            gpu_line = f"GPU: {metrics['gpu_temp']}C | {metrics['gpu_power']}W | {metrics['gpu_load']}% | VRAM: {metrics['gpu_vram']}\n"
            ram_line = f"RAM: {metrics['ram_used']} | CPU CLK: {metrics['cpu_clock']}MHz\n"
            fps_line = f"FPS: {metrics['fps']} | 0.1%: {metrics['fps_low']} | {metrics['frametime']}ms\n"
            
            # Send lines to ESP32 over Serial
            ser.write(cpu_line.encode('utf-8'))
            ser.write(gpu_line.encode('utf-8'))
            ser.write(ram_line.encode('utf-8'))
            ser.write(fps_line.encode('utf-8')) # This last line triggers the OLED to refresh
            
            # Also print to console for debugging
            print(f"{cpu_line.strip()} || {gpu_line.strip()} || {fps_line.strip()}")
            time.sleep(1)
            
        except Exception as e:
            print(f"Data Error: Make sure LibreHardwareMonitor is running! {e}")
            time.sleep(2)

if __name__ == "__main__":
    get_max_telemetry()
