#include <Adafruit_NeoPixel.h>
#include <stdlib.h>

#define PIN 4
#define LED_COUNT 87
#define BRIGHT 255


Adafruit_NeoPixel leds = Adafruit_NeoPixel(LED_COUNT, PIN, NEO_GRB + NEO_KHZ800);

void clearLEDs() {
  for (int i = 0; i < LED_COUNT; i++) {
    leds.setPixelColor(i, 0x000000);
  }
}

/*
* Pseudo random number generator
* that returns 0 or 1
*/
unsigned rand2() {
  static unsigned state = 1;  
  if (state & 1) {
    state >>= 1;
    state ^= 0x8100;
  } else {
    state >>= 1;
  }
  return state & 1;
}

void randomLight() {
  uint8_t red;
  uint8_t blue;
  uint8_t green;

  for (int i = 0; i < LED_COUNT; i++){
    if (rand2() && rand2() && rand2()){
      red = 0xff;
    } else {
      red = 0x0;
    }

    if (rand2() && rand2() && rand2()){
      green = 0xff;
    } else {
      green = 0x0;
    }

    if (rand2() && rand2() && rand2()){
      blue = 0xff;
    } else {
      blue = 0x0;
    }
 
    leds.setPixelColor(i, red, green, blue);
    
  }
}

/*
* Clear all LEDs and set brightness
*/

void setup(){
  leds.begin();
  leds.setBrightness(BRIGHT);
  clearLEDs();
  leds.show();
}

/*
* Enter Loop
*/
void loop() {
  randomLight();
  leds.show(); 
  delay(20); 
}



