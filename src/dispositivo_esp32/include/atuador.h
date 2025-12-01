#ifndef DISP_ESP32_ATUADOR
#define DISP_ESP32_ATUADOR

#include "driver/gpio.h"

#define LED_PIN 4

void configurar_atuador();
uint16_t escrever_atuador();

#endif // DISP_ESP32_ATUADOR