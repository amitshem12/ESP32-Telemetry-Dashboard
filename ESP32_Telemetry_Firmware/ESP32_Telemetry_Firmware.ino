#include <U8g2lib.h>
#include <SPI.h>

// Initialize the 1.5" OLED display (SSD1327) via Hardware SPI
U8G2_SSD1327_MIDAS_128X128_F_4W_HW_SPI u8g2(U8G2_R0, /* cs=*/ 10, /* dc=*/ 9, /* reset=*/ 8);

unsigned long lastDataTime = 0;
const unsigned long TIMEOUT_MS = 2000;
String incomingData = "";
bool isReceiving = false;

void setup() {
  Serial.begin(115200);
  u8g2.begin();
  
  displayDisconnectedState();
}

void loop() {
  // Read incoming serial data with framing (<start_marker, end_marker>)
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    if (c == '<') {
      isReceiving = true;
      incomingData = "";
    } 
    else if (c == '>' && isReceiving) {
      isReceiving = false;
      updateOLED(incomingData);
      lastDataTime = millis();
    } 
    else if (isReceiving) {
      incomingData += c;
    }
  }

  // Check for timeout if data flow stops
  if (millis() - lastDataTime > TIMEOUT_MS) {
    displayDisconnectedState();
  }
}

void updateOLED(String data) {
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  
  u8g2.setCursor(0, 15);
  u8g2.print("Telemetry Active");
  
  u8g2.setCursor(0, 40);
  u8g2.print("Data: ");
  u8g2.print(data);
  
  u8g2.sendBuffer();
}

void displayDisconnectedState() {
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB10_tr);
  
  u8g2.setCursor(10, 50);
  u8g2.print("Disconnected");
  
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.setCursor(10, 70);
  u8g2.print("Waiting for PC...");
  
  u8g2.sendBuffer();
}