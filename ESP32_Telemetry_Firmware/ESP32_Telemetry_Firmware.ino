#include <Arduino.h>
#include <U8g2lib.h>
#include <SPI.h>
#include "USB.h"
#include "USBMSC.h"

/* Define SPI pins for the 1.5" OLED SSD1327 */
/* Pins can be easily modified once you wire the physical board */
#define OLED_CS   10
#define OLED_DC   9
#define OLED_RES  8

/* Initialize OLED object using hardware SPI */
U8G2_SSD1327_MIDAS_128X128_F_4W_HW_SPI u8g2(U8G2_R0, OLED_CS, OLED_DC, OLED_RES);

/* Initialize USB Mass Storage object */
USBMSC MSC;

void setup() {
    /* Initialize Serial communication with the PC python script */
    Serial.begin(115200);

    /* Configure Native USB Mass Storage (Drive Mode) */
    MSC.vendorID("ESP32-S3");
    MSC.productID("TelemetryBox");
    MSC.productRevision("1.0");
    MSC.mediaPresent(true);
    MSC.begin(1, 512); /* Block count and size, to be mapped to FAT partition */
    USB.begin();

    /* Initialize and clear the OLED display */
    u8g2.begin();
    u8g2.clearBuffer();
    
    /* Set font and display startup message */
    u8g2.setFont(u8g2_font_ncenB08_tr); 
    u8g2.drawStr(15, 64, "Waiting for PC...");
    u8g2.sendBuffer();
}

void loop() {
    /* Read incoming telemetry data line by line */
    if (Serial.available()) {
        String incomingData = Serial.readStringUntil('\n');
        incomingData.trim();

        /* Parse the prefix and draw to the specific Y coordinate */
        if (incomingData.startsWith("CPU:")) {
            u8g2.clearBuffer(); /* Clear before starting a new frame */
            u8g2.setCursor(0, 20);
            u8g2.print(incomingData);
        } 
        else if (incomingData.startsWith("GPU:")) {
            u8g2.setCursor(0, 50);
            u8g2.print(incomingData);
        } 
        else if (incomingData.startsWith("RAM:")) {
            u8g2.setCursor(0, 80);
            u8g2.print(incomingData);
        } 
        else if (incomingData.startsWith("FPS:")) {
            u8g2.setCursor(0, 110);
            u8g2.print(incomingData);
            
            /* Push the complete frame to the OLED display */
            u8g2.sendBuffer(); 
        }
    }
}