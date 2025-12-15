
import sys
import os

sys.path.append("../")

from func_gateway_request_device import enviar_requisicao_tcp as enviar_req_device
from func_gateway_receive_client import socket_receiv_client_request_device
from func_multcast_udp import multcast_broadcaster_udp
from func_gateway_save_info import receive_info_device

# if __name__ == "__main__":
#     multcast_broadcaster_udp(
#         ip_gateway="localhost",
#         port_gateway="7895"
#     )

#     receive_info_device()
#     socket_receiv_client_request_device()

import threading

def main():
    # Criando threads para cada função
    thread_broadcast = threading.Thread(
        target=multcast_broadcaster_udp, 
        kwargs={"ip_gateway": "localhost", "port_gateway": "7895"}
    )
    
    thread_receive_info = threading.Thread(target=receive_info_device)
    thread_receive_request = threading.Thread(target=socket_receiv_client_request_device)

    # Iniciando todas as threads
    thread_broadcast.start()
    thread_receive_info.start()
    thread_receive_request.start()

    # Se você quiser que o programa espere todas terminarem
    thread_broadcast.join()
    thread_receive_info.join()
    thread_receive_request.join()


if __name__ == "__main__":
    main()

