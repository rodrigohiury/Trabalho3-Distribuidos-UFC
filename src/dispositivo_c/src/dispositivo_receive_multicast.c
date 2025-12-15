#define _DEFAULT_SOURCE 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/ip.h> 
#include <sys/socket.h>
#include "dispositivo.pb-c.h"

#define MCAST_GRP  "224.1.1.1"
#define MCAST_PORT 5007

extern int enviar_info(const char *ip_gateway, int port_gateway);

void start_udp_client(void)
{
    int sock;
    struct sockaddr_in local_addr, src_addr;
    socklen_t addrlen = sizeof(src_addr);
    uint8_t buffer[1024];
    
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return;
    }
    
    int reuse = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
    
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_port = htons(MCAST_PORT);
    local_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    
    if (bind(sock, (struct sockaddr *)&local_addr, sizeof(local_addr)) < 0) {
        perror("bind");
        close(sock);
        return;
    }
    
    struct ip_mreq mreq;
    mreq.imr_multiaddr.s_addr = inet_addr(MCAST_GRP);
    mreq.imr_interface.s_addr = htonl(INADDR_ANY);
    
    if (setsockopt(sock, IPPROTO_IP, IP_ADD_MEMBERSHIP,
                   &mreq, sizeof(mreq)) < 0) {
        perror("IP_ADD_MEMBERSHIP");
        close(sock);
        return;
    }
    
    printf("UDP Client listening on 0.0.0.0:%d\n", MCAST_PORT);
    
    while (1) {
        ssize_t n = recvfrom(sock, buffer, sizeof(buffer), 0,
                            (struct sockaddr *)&src_addr, &addrlen);
        if (n < 0)
            continue;
        
        char ip_gateway[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &src_addr.sin_addr,
                 ip_gateway, sizeof(ip_gateway));
        
        Dispositivo__ReadDevice *msg = 
            dispositivo__read_device__unpack(NULL, n, buffer);
        
        if (msg == NULL) {
            fprintf(stderr, "Erro ao desempacotar mensagem protobuf\n");
            continue;
        }
        
        int port_gateway = msg->port_device;
        
        printf("Dados recebidos - Device: %s, Port: %d\n", 
               msg->name_device, port_gateway);
        printf("Vindo de %s:%d\n", ip_gateway, ntohs(src_addr.sin_port));
        
        enviar_info(ip_gateway, port_gateway);
        
        dispositivo__read_device__free_unpacked(msg, NULL);
    }
    
    close(sock);
}