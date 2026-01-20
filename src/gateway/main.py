import sys
import os
import threading
import json

sys.path.append("../")

# from func_gateway_request_device import enviar_requisicao_tcp as enviar_req_device
from func_gateway_receive_client import socket_receiv_client_request_device
from func_multcast_udp import multcast_broadcaster_udp
from device_listener import receive_info_device
from consumer_sensor_data_mq import ConsumeData



def main():
    with open("dados.json", "w", encoding="utf-8") as f:
        json.dump({}, f)

    # Criando threads para cada função
    thread_broadcast = threading.Thread(
        target=multcast_broadcaster_udp, 
        kwargs={"ip_gateway": "localhost", "port_gateway": "58950"}
    )
    
    consumer = ConsumeData("localhost", 5672, "tr3-sd-q")

    thread_receive_info = threading.Thread(target=receive_info_device)
    thread_receive_request = threading.Thread(target=socket_receiv_client_request_device)
    thread_consume_mq = threading.Thread(target=consumer.consume_data)

    # Iniciando todas as threads
    thread_broadcast.start()
    thread_receive_info.start()
    thread_receive_request.start()
    thread_consume_mq.start()

    # Se você quiser que o programa espere todas terminarem
    thread_broadcast.join()
    thread_receive_info.join()
    thread_receive_request.join()


if __name__ == "__main__":
    main()

