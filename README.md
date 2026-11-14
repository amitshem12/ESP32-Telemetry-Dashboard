# ESP32 PC Telemetry Dashboard

A standalone, plug-and-play hardware telemetry dashboard for monitoring real-time PC performance metrics, built with an ESP32-S3 and a 1.5" OLED display.

## Features
* **Real-Time Monitoring:** Tracks CPU & GPU (Temperature, Power, Load, Clock speeds), RAM usage, VRAM, and Gaming FPS (including 0.1% lows and frametimes).
* **Hardware-Agnostic:** Python data-extraction service utilizes LibreHardwareMonitor's local JSON server, supporting universal Intel/AMD/NVIDIA hardware setups.
* **Native USB & Mass Storage:** The ESP32-S3 utilizes custom flash memory partitioning (32MB) to act as a native USB flash drive. It hosts the portable Python `.exe` natively, requiring no prior software installation on the host PC.
* **Custom Enclosure:** Designed and integrated a 3D-printed enclosure to manage physical constraints and hardware assembly.

## Tech Stack & Hardware
* **Microcontroller:** ESP32-S3 (32MB Flash)
* **Display:** 1.5" OLED (SSD1327) via Hardware SPI
* **Firmware:** C/C++ (Arduino IDE 2), U8g2 graphics library, USBMSC
* **PC Host Script:** Python, PySerial, Requests

## Project Structure
* `/Python_Host` - The data extraction script and executable.
* `/ESP32_Firmware` - The C++ source code for the microcontroller.
