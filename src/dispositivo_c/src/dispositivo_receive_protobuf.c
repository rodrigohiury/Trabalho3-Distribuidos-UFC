#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>

#include "dispositivo.pb-c.h"

static int recv_all(int sock, void *buf, size_t len)
{
    size_t total = 0;
    while (total < len) {
        ssize_t n = recv(sock, (char *)buf + total, len - total, 0);
        if (n <= 0)
            return -1;
        total += n;
    }
    return 0;
}

static char *timestamp_iso8601(void)
{
    time_t now = time(NULL);
    struct tm tm;
    localtime_r(&now, &tm);

    char *buf = malloc(32);
    strftime(buf, 32, "%Y-%m-%dT%H:%M:%S", &tm);
    return buf;
}

int enviar_protobuf(int sock, ProtobufCMessage *msg)
{
    uint32_t size = protobuf_c_message_get_packed_size(msg);
    uint32_t header = htonl(size);

    uint8_t *payload = malloc(size);
    if (!payload)
        return -1;

    protobuf_c_message_pack(msg, payload);

    if (send(sock, &header, 4, 0) != 4 ||
        send(sock, payload, size, 0) != (ssize_t)size) {
        free(payload);
        return -1;
    }

    free(payload);
    return 0;
}

Dispositivo__Requisicao *receber_requisicao(int sock)
{
    uint32_t header;
    if (recv_all(sock, &header, 4) < 0)
        return NULL;

    uint32_t size = ntohl(header);
    uint8_t *payload = malloc(size);
    if (!payload)
        return NULL;

    if (recv_all(sock, payload, size) < 0) {
        free(payload);
        return NULL;
    }

    Dispositivo__Requisicao *req =
        dispositivo__requisicao__unpack(NULL, size, payload);

    free(payload);
    return req;
}

static Dispositivo__Resposta *criar_erro(const char *comando,
                                        const char *mensagem)
{
    Dispositivo__Resposta *resp = malloc(sizeof(*resp));
    dispositivo__resposta__init(resp);

    resp->tipo_case = DISPOSITIVO__RESPOSTA__TIPO_ERRO;
    resp->erro = malloc(sizeof(Dispositivo__RespostaErro));
    dispositivo__resposta_erro__init(resp->erro);

    resp->erro->comando = strdup(comando);
    resp->erro->mensagem = strdup(mensagem);

    resp->erro->n_detalhes = 1;
    resp->erro->detalhes =
        malloc(sizeof(Dispositivo__RespostaErro__DetalhesEntry *));

    Dispositivo__RespostaErro__DetalhesEntry *e =
        malloc(sizeof(*e));
    dispositivo__resposta_erro__detalhes_entry__init(e);

    e->key = strdup("timestamp");
    e->value = timestamp_iso8601();

    resp->erro->detalhes[0] = e;

    return resp;
}

static Dispositivo__Resposta *tratar_leitura(void)
{
    return criar_erro("LER", "LER ainda não implementado");
}

static Dispositivo__Resposta *tratar_escrita(void)
{
    return criar_erro("ESCREVER", "ESCREVER ainda não implementado");
}

Dispositivo__Resposta *tratar_requisicao(Dispositivo__Requisicao *req)
{
    switch (req->tipo_case) {

    case DISPOSITIVO__REQUISICAO__TIPO_LER:
        return tratar_leitura();

    case DISPOSITIVO__REQUISICAO__TIPO_ESCREVER:
        return tratar_escrita();

    default:
        return criar_erro("REQUISICAO", "Tipo inválido");
    }
}

void escutar_comandos_tcp(const char *ip, int port)
{
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0)
        return;

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));

    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &addr.sin_addr);

    bind(server_fd, (struct sockaddr *)&addr, sizeof(addr));
    listen(server_fd, 1);

    printf("Dispositivo escutando em %s:%d\n", ip, port);

    while (1) {
        int client = accept(server_fd, NULL, NULL);
        if (client < 0)
            continue;

        Dispositivo__Requisicao *req = receber_requisicao(client);
        if (!req) {
            close(client);
            continue;
        }

        Dispositivo__Resposta *resp = tratar_requisicao(req);
        enviar_protobuf(client, &resp->base);

        dispositivo__requisicao__free_unpacked(req, NULL);
        dispositivo__resposta__free_unpacked(resp, NULL);

        close(client);
    }
}
