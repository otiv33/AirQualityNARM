#include <Arduino.h>
#include <SensirionI2CSen5x.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>

SensirionI2CSen5x sen5x;
HTTPClient http;
const String reqUrl = "http://20.222.149.200:8080/airQuality/";
const char* ssid = "NSM_Student";
const char* wifiPassword = "Radstudiram!";
const String apiToken = "sjurzbfg7qlopdz5";
const int repeatInterval = 10000; // 10s

void setUpAirSensor(){
  Wire.begin();

  uint16_t error;
  char errorMessage[256];

  sen5x.begin(Wire);

  error = sen5x.deviceReset();
  if (error) {
    Serial.print("Error trying to execute deviceReset(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
  }

  Serial.println("Starting measurements ...");
  error = sen5x.startMeasurement();

  if (error) {
    Serial.print("Error trying to execute startMeasurement(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
  }
}

void printIP(){
  Serial.print("Device IP: ");
  Serial.println(WiFi.localIP());
}

void reconnectWifi(){
  Serial.println("Reconnecting to WiFi...");
  WiFi.disconnect();
  WiFi.reconnect();
  printIP();
}

void setUpWifi(){
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, wifiPassword);
  Serial.println("\nConnecting");
  while(WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(100);
  }
  Serial.println("\nConnected to the WiFi network");
  Serial.print(ssid);
  printIP();
}

void postAirQualityData(){
  if(WiFi.status()== WL_CONNECTED){
    String body = getAirQuality();
    if(body != ""){
      Serial.println("\nStarting request ...");
      http.begin(reqUrl);
      http.addHeader("Content-Type", "application/json");
      http.addHeader("Authorization", apiToken);
      int httpResponseCode = http.POST(body);
    
      if (httpResponseCode > 0 && httpResponseCode == HTTP_CODE_OK) {
        Serial.printf("POST request successful : %s, Message --> ", String(httpResponseCode));
        String payload = http.getString();
        Serial.print(payload);
      }
      else {
        Serial.printf("POST request failed : %s\n", http.errorToString(httpResponseCode).c_str());
      }
      http.end();
    }
  }
  else {
    reconnectWifi();
  }
}

String getAirQuality(){
  uint16_t error;
  char errorMessage[256];
  
  delay(1000);

  float pm1;
  float pm25;
  float pm4;
  float pm10;
  float h;
  float t;
  float voc;
  float nox;

  error = sen5x.readMeasuredValues(pm1, pm25, pm4, pm10, h, t, voc,nox);

  if (error) {
    Serial.print("Error trying to execute "
                  "readMeasuredValues(): ");
    errorToString(error, errorMessage, 256);
    Serial.println(errorMessage);
    return "";
  } else {
    if (isnan(nox)) {
      nox = 0.0;
    }
    int dec = 2;
    String res = "{\"pm1\":\""+String(pm1, dec)+"\",\"pm25\":\""+String(pm25, dec)+"\",\"pm4\":\""+String(pm4, dec)+"\",\"pm10\":\""+String(pm10, dec)+"\",\"h\":\""+String(h, dec)+"\",\"t\":\""+String(t, dec)+"\",\"voc\":\""+String(voc, dec)+"\",\"nox\":\""+String(nox, dec)+"\"}";
    // Serial.println(res);
    return res;
  }
}

// SETUP
void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(100);
  }
  setUpWifi();
  setUpAirSensor();
}

// LOOP
void loop() {
  postAirQualityData();
  delay(repeatInterval);
}
