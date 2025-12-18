from device_receive_multcast_udp import start_udp_listener
from device_receive_protobuf_tcp import socket_tcp_device_receive
from watchdog_door import watchdog_door

import threading

if __name__ == "__main__":
    # Cria threads para cada função
    thread_udp = threading.Thread(target=start_udp_listener, name="UDPListener")
    thread_tcp = threading.Thread(target=socket_tcp_device_receive, name="TCPListener")
    thread_watchdog = threading.Thread(target=watchdog_door, name="WatchdogDoor")

    # Inicia as threads
    thread_udp.start()
    thread_tcp.start()
    thread_watchdog.start()