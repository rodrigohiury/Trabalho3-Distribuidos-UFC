#ifndef DISP_ESP32_SENSOR_LUMINOSIDADE
#define DISP_ESP32_SENSOR_LUMINOSIDADE

#include "driver/gpio.h"

#define LUM_PIN 35

void configurar_sensor_luminosidade();
uint16_t ler_luminosidade();

#endif // DISP_ESP32_SENSOR_LUMINOSIDADE