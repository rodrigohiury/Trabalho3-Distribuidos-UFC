from device_receive_multcast_udp import start_udp_listener
from device_receive_protobuf_tcp import socket_tcp_device_receive
from watchdog_door import WatchdogDoor
from device_grpc_server import DeviceServiceServicer
from concurrent import futures

import threading
import device_pb2
import device_pb2_grpc
import grpc

if __name__ == "__main__":
    whatchdog = WatchdogDoor()
    # Cria threads para cada função
    thread_udp = threading.Thread(target=start_udp_listener, name="UDPListener", args=(whatchdog ,))
    # thread_tcp = threading.Thread(target=socket_tcp_device_receive, name="TCPListener")
    thread_watchdog = threading.Thread(target=whatchdog.watchdog_door, name="WatchdogDoor")

    # Inicia as threads
    thread_udp.start()
    # thread_tcp.start()
    thread_watchdog.start()

    grpc_serv = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    device_pb2_grpc.add_DeviceServiceServicer_to_server(
        DeviceServiceServicer(),
        grpc_serv
    )

    grpc_serv.add_insecure_port("[::]:15033")
    grpc_serv.start()
    print("Dispositivo gRPC rodando na porta 15033")
    grpc_serv.wait_for_termination()
