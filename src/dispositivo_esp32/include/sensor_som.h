#ifndef DISP_ESP32_SENSOR_SOM
#define DISP_ESP32_SENSOR_SOM

#include "driver/gpio.h"
#include <stdint.h>

#define LUM_PIN 34

void configurar_sensor_som();
uint16_t ler_som();

#endif // DISP_ESP32_SENSOR_SOM