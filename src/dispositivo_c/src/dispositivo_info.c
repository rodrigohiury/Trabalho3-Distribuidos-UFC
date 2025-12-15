#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "dispositivo.pb-c.h"

int enviar_info(const char *ip_gateway, int port_gateway)
{
    int sock;
    struct sockaddr_in addr;

    /* ---------- SOCKET ---------- */
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return -1;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port_gateway);
    inet_pton(AF_INET, ip_gateway, &addr.sin_addr);

    /* ---------- PROTOBUF ---------- */
    Dispositivo__ComandoOperacao operacao = DISPOSITIVO__COMANDO_OPERACAO__INIT;
    operacao.operacao = DISPOSITIVO__COMANDO_OPERACAO__TIPO_OPERACAO__ESCREVER;

    Dispositivo__InfoDeviceClient info = DISPOSITIVO__INFO_DEVICE_CLIENT__INIT;
    info.status = "online";
    info.type_device = "sensor";

    Dispositivo__RequisicaoEscrever escrever =
        DISPOSITIVO__REQUISICAO_ESCREVER__INIT;
    escrever.operacao = &operacao;
    escrever.info_device = &info;

    Dispositivo__Requisicao req = DISPOSITIVO__REQUISICAO__INIT;
    req.name_client = "device_client";
    req.name_device = "device_01";
    req.tipo_case = DISPOSITIVO__REQUISICAO__TIPO_ESCREVER;
    req.escrever = &escrever;

    size_t len = dispositivo__requisicao__get_packed_size(&req);
    uint8_t *buffer = malloc(len);
    if (!buffer) {
        close(sock);
        return -1;
    }

    dispositivo__requisicao__pack(&req, buffer);

    sendto(sock, buffer, len, 0,
           (struct sockaddr *)&addr, sizeof(addr));

    free(buffer);
    close(sock);

    return 0;
}
