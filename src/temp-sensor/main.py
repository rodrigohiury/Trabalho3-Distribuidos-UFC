from device_receive_multcast_udp import start_udp_listener
from device_receive_protobuf_tcp import socket_tcp_device_receive
from simul import simular_temp_sensor

import threading

if __name__ == "__main__":
    # Cria threads para cada função
    thread_udp = threading.Thread(target=start_udp_listener, name="UDPListener")
    thread_tcp = threading.Thread(target=socket_tcp_device_receive, name="TCPListener")
    thread_simul = threading.Thread(target=simular_temp_sensor, name="SimulTempSensor")

    # Inicia as threads
    thread_udp.start()
    thread_tcp.start()
    thread_simul.start()