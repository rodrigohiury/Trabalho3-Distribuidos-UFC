#ifndef DISPOSITIVO_RECEIVE_PROTOBUF
#define DISPOSITIVO_RECEIVE_PROTOBUF

#include <stdlib.h>
#include "dispositivo.pb-c.h"

int recv_all(int sock, void *buf, size_t len);
char *timestamp_iso8601(void);
int enviar_protobuf(int sock, ProtobufCMessage *msg);
Dispositivo__Requisicao *receber_requisicao(int sock);
Dispositivo__Resposta *criar_erro(const char *comando,
                                        const char *mensagem);
Dispositivo__Resposta *tratar_leitura(void);
Dispositivo__Resposta *tratar_escrita(void);
Dispositivo__Resposta *tratar_requisicao(Dispositivo__Requisicao *req);
void escutar_comandos_tcp(const char *ip, int port);

#endif