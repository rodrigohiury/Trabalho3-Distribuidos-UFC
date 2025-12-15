from device_receive_multcast_udp import start_udp_listener
from device_receive_protobuf_tcp import socket_tcp_device_receive

if __name__ == "__main__":
    start_udp_listener()
    socket_tcp_device_receive()