#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include "dispositivo.pb-c.h"

#define BUF_SIZE 4096

/* ============================================================
   Funções auxiliares de comunicação
   ============================================================ */

// Receber exatamente 'len' bytes
int recv_all(int sock, void *buf, size_t len) {
    size_t total = 0;
    while (total < len) {
        ssize_t r = recv(sock, (char *)buf + total, len - total, 0);
        if (r <= 0) {
            if (r == 0) {
                fprintf(stderr, "Conexão encerrada pelo servidor\n");
            } else {
                perror("recv");
            }
            return -1;
        }
        total += r;
    }
    return 0;
}

// Enviar mensagem protobuf com prefixo de tamanho (big-endian)
int enviar(int sock, ProtobufCMessage *msg) {
    uint32_t len = protobuf_c_message_get_packed_size(msg);
    uint32_t net_len = htonl(len);  // Converte para big-endian (network byte order)

    uint8_t *buf = malloc(len);
    if (!buf) {
        perror("malloc");
        return -1;
    }
    
    protobuf_c_message_pack(msg, buf);

    // Envia tamanho (4 bytes)
    if (send(sock, &net_len, 4, 0) != 4) {
        perror("send header");
        free(buf);
        return -1;
    }
    
    // Envia dados
    if (send(sock, buf, len, 0) != (ssize_t)len) {
        perror("send data");
        free(buf);
        return -1;
    }

    free(buf);
    return 0;
}

// Receber mensagem protobuf Resposta
Dispositivo__Resposta *receber(int sock) {
    uint32_t net_len;
    
    // Recebe tamanho (4 bytes)
    if (recv_all(sock, &net_len, 4) < 0) {
        fprintf(stderr, "Erro ao receber header\n");
        return NULL;
    }

    uint32_t len = ntohl(net_len);  // Converte de big-endian
    
    if (len > BUF_SIZE) {
        fprintf(stderr, "Mensagem muito grande: %u bytes\n", len);
        return NULL;
    }

    // Recebe dados
    uint8_t *buf = malloc(len);
    if (!buf) {
        perror("malloc");
        return NULL;
    }
    
    if (recv_all(sock, buf, len) < 0) {
        fprintf(stderr, "Erro ao receber dados\n");
        free(buf);
        return NULL;
    }

    // Desempacota protobuf
    Dispositivo__Resposta *resp =
        dispositivo__resposta__unpack(NULL, len, buf);

    free(buf);
    return resp;
}

/* ============================================================
   Criar requisição de ESCREVER com parâmetros
   ============================================================ */

Dispositivo__Requisicao *criar_requisicao_escrever_teste(void) {
    // Alocar requisição
    Dispositivo__Requisicao *req = 
        malloc(sizeof(Dispositivo__Requisicao));
    dispositivo__requisicao__init(req);

    req->name_client = strdup("cliente_teste");
    req->name_device = strdup("Sensor de InfraVermelho");

    // Configurar tipo ESCREVER
    req->tipo_case = DISPOSITIVO__REQUISICAO__TIPO_ESCREVER;

    // Alocar RequisicaoEscrever
    Dispositivo__RequisicaoEscrever *escrever = 
        malloc(sizeof(Dispositivo__RequisicaoEscrever));
    dispositivo__requisicao_escrever__init(escrever);

    // Comando de operação
    Dispositivo__ComandoOperacao *cmd = 
        malloc(sizeof(Dispositivo__ComandoOperacao));
    dispositivo__comando_operacao__init(cmd);
    cmd->operacao = DISPOSITIVO__COMANDO_OPERACAO__TIPO_OPERACAO__ESCREVER;
    escrever->operacao = cmd;

    // InfoDeviceClient
    Dispositivo__InfoDeviceClient *info = 
        malloc(sizeof(Dispositivo__InfoDeviceClient));
    dispositivo__info_device_client__init(info);

    info->status = strdup("ligado-");
    info->type_device = strdup("sensor");

    // Criar parâmetros (map<string, string>)
    // Em protobuf-c, maps são arrays de entries
    info->n_parametros = 2;
    info->parametros = malloc(sizeof(Dispositivo__InfoDeviceClient__ParametrosEntry*) * 2);

    // Parâmetro 1: temperatura
    Dispositivo__InfoDeviceClient__ParametrosEntry *param1 = 
        malloc(sizeof(Dispositivo__InfoDeviceClient__ParametrosEntry));
    dispositivo__info_device_client__parametros_entry__init(param1);
    param1->key = strdup("temperatura");
    param1->value = strdup("1000°");
    info->parametros[0] = param1;

    // Parâmetro 2: movimentacao
    Dispositivo__InfoDeviceClient__ParametrosEntry *param2 = 
        malloc(sizeof(Dispositivo__InfoDeviceClient__ParametrosEntry));
    dispositivo__info_device_client__parametros_entry__init(param2);
    param2->key = strdup("movimentacao");
    param2->value = strdup("nao");
    info->parametros[1] = param2;

    escrever->info_device = info;
    req->escrever = escrever;

    return req;
}

/* ============================================================
   Criar requisição de LEITURA
   ============================================================ */

Dispositivo__Requisicao *criar_requisicao_ler_teste(void) {
    Dispositivo__Requisicao *req = 
        malloc(sizeof(Dispositivo__Requisicao));
    dispositivo__requisicao__init(req);

    req->name_client = strdup("cliente_teste");
    req->name_device = strdup("Sensor de InfraVermelho");

    req->tipo_case = DISPOSITIVO__REQUISICAO__TIPO_LER;

    Dispositivo__RequisicaoLer *ler = 
        malloc(sizeof(Dispositivo__RequisicaoLer));
    dispositivo__requisicao_ler__init(ler);

    Dispositivo__ComandoOperacao *cmd = 
        malloc(sizeof(Dispositivo__ComandoOperacao));
    dispositivo__comando_operacao__init(cmd);
    cmd->operacao = DISPOSITIVO__COMANDO_OPERACAO__TIPO_OPERACAO__LER;
    
    ler->operacao = cmd;
    req->ler = ler;

    return req;
}

/* ============================================================
   Imprimir requisição (similar ao print(req) do Python)
   ============================================================ */

void imprimir_requisicao(Dispositivo__Requisicao *req) {
    printf("════════════════════════════════════════\n");
    printf("REQUISIÇÃO:\n");
    printf("  Cliente: %s\n", req->name_client);
    printf("  Dispositivo: %s\n", req->name_device);

    switch (req->tipo_case) {
        case DISPOSITIVO__REQUISICAO__TIPO_LER:
            printf("  Tipo: LER\n");
            printf("  Operação: %d\n", req->ler->operacao->operacao);
            break;

        case DISPOSITIVO__REQUISICAO__TIPO_ESCREVER:
            printf("  Tipo: ESCREVER\n");
            printf("  Operação: %d\n", req->escrever->operacao->operacao);
            printf("  Status: %s\n", req->escrever->info_device->status);
            printf("  Tipo Device: %s\n", req->escrever->info_device->type_device);
            
            if (req->escrever->info_device->n_parametros > 0) {
                printf("  Parâmetros:\n");
                for (size_t i = 0; i < req->escrever->info_device->n_parametros; i++) {
                    Dispositivo__InfoDeviceClient__ParametrosEntry *p = 
                        req->escrever->info_device->parametros[i];
                    printf("    %s = %s\n", p->key, p->value);
                }
            }
            break;

        default:
            printf("  Tipo: DESCONHECIDO\n");
    }
    printf("════════════════════════════════════════\n");
}

/* ============================================================
   Imprimir resposta (similar ao print(resp) do Python)
   ============================================================ */

void imprimir_resposta(Dispositivo__Resposta *resp) {
    printf("\n════════════════════════════════════════\n");
    printf("RESPOSTA:\n");

    switch (resp->tipo_case) {
        case DISPOSITIVO__RESPOSTA__TIPO_OK:
            printf("  Status: OK ✓\n");
            printf("  Comando: %s\n", resp->ok->comando);
            
            if (resp->ok->n_dados > 0) {
                printf("  Dados:\n");
                for (size_t i = 0; i < resp->ok->n_dados; i++) {
                    Dispositivo__RespostaOk__DadosEntry *d = resp->ok->dados[i];
                    printf("    %s = %s\n", d->key, d->value);
                }
            }

            if (resp->ok->device_info) {
                Dispositivo__ReadDevice *dev = resp->ok->device_info;
                printf("  Device Info:\n");
                printf("    Nome: %s\n", dev->name_device);
                printf("    IP: %s\n", dev->ip_device);
                printf("    Porta: %u\n", dev->port_device);
                printf("    Status: %s\n", dev->status);
                printf("    Tipo: %s\n", dev->type_device);
                
                if (dev->n_parametros > 0) {
                    printf("    Parâmetros:\n");
                    for (size_t i = 0; i < dev->n_parametros; i++) {
                        Dispositivo__ReadDevice__ParametrosEntry *p = dev->parametros[i];
                        printf("      %s = %s\n", p->key, p->value);
                    }
                }
            }
            break;

        case DISPOSITIVO__RESPOSTA__TIPO_ERRO:
            printf("  Status: ERRO ✗\n");
            printf("  Comando: %s\n", resp->erro->comando);
            printf("  Mensagem: %s\n", resp->erro->mensagem);
            
            if (resp->erro->n_detalhes > 0) {
                printf("  Detalhes:\n");
                for (size_t i = 0; i < resp->erro->n_detalhes; i++) {
                    Dispositivo__RespostaErro__DetalhesEntry *d = resp->erro->detalhes[i];
                    printf("    %s = %s\n", d->key, d->value);
                }
            }
            break;

        default:
            printf("  Status: DESCONHECIDO\n");
    }
    printf("════════════════════════════════════════\n\n");
}

/* ============================================================
   MAIN - Equivalente ao código Python
   ============================================================ */

int main(void) {
    // Criar socket TCP
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        return 1;
    }

    // Conectar ao servidor
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(5001),
    };
    
    if (inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr) <= 0) {
        fprintf(stderr, "IP inválido\n");
        close(sock);
        return 1;
    }

    printf("Conectando a localhost:5001...\n");
    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect");
        close(sock);
        return 1;
    }
    printf("✓ Conectado!\n\n");

    // Criar requisição (ESCREVER com parâmetros)
    Dispositivo__Requisicao *req = criar_requisicao_escrever_teste();
    
    // Para testar LER, descomente a linha abaixo:
    // Dispositivo__Requisicao *req = criar_requisicao_ler_teste();

    // Imprimir requisição
    printf("Enum ESCREVER = %d\n\n", 
           DISPOSITIVO__COMANDO_OPERACAO__TIPO_OPERACAO__ESCREVER);
    imprimir_requisicao(req);

    // Enviar requisição
    printf("\nEnviando requisição...\n");
    if (enviar(sock, (ProtobufCMessage *)req) < 0) {
        fprintf(stderr, "Erro ao enviar requisição\n");
        dispositivo__requisicao__free_unpacked(req, NULL);
        close(sock);
        return 1;
    }
    printf("✓ Requisição enviada!\n");

    // Receber resposta
    printf("\nAguardando resposta...\n");
    Dispositivo__Resposta *resp = receber(sock);
    if (!resp) {
        fprintf(stderr, "Erro ao receber resposta\n");
        dispositivo__requisicao__free_unpacked(req, NULL);
        close(sock);
        return 1;
    }
    printf("✓ Resposta recebida!\n");

    // Imprimir resposta
    imprimir_resposta(resp);

    // Limpar e fechar
    dispositivo__requisicao__free_unpacked(req, NULL);
    dispositivo__resposta__free_unpacked(resp, NULL);
    close(sock);

    printf("Conexão encerrada.\n");
    return 0;
}