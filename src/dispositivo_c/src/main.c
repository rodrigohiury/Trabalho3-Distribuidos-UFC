#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include "dispositivo_info.h"
#include "dispositivo_receive_multicast.h"
#include "dispositivo_receive_protobuf.h"

#define IP "localhost"
#define PORT 5001

void *udp_thread(void *arg) {
    (void)arg;  // unused
    start_udp_client();
    return NULL;
}

void *tcp_thread(void *arg) {
    (void)arg;  // unused
    escutar_comandos_tcp(IP, PORT);
    return NULL;
}

int main(void) {
    pthread_t t_udp;
    pthread_t t_tcp;

    if (pthread_create(&t_udp, NULL, udp_thread, NULL) != 0) {
        perror("pthread_create udp");
        exit(EXIT_FAILURE);
    }

    if (pthread_create(&t_tcp, NULL, tcp_thread, NULL) != 0) {
        perror("pthread_create tcp");
        exit(EXIT_FAILURE);
    }

    /* Wait forever (or until threads exit) */
    pthread_join(t_udp, NULL);
    pthread_join(t_tcp, NULL);

    return 0;
}
