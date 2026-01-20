from device_receive_multcast_udp import start_udp_listener
from device_send_state_mq import SendState
from simul import simular_temp_sensor
from device_grpc_server import DeviceServiceServicer
from concurrent import futures

import threading
import device_pb2
import device_pb2_grpc
import grpc

if __name__ == "__main__":
    # Cria threads para cada função
    SendStateInstance = SendState()
    thread_udp = threading.Thread(target=start_udp_listener, name="UDPListener", args=(SendStateInstance,))
    thread_simul = threading.Thread(target=simular_temp_sensor, name="SimulTempSensor")
    thread_send_data = threading.Thread(target=SendStateInstance.start_sending, name="SendStateMQ")

    # Inicia as threads
    thread_udp.start()
    thread_simul.start()
    thread_send_data.start()

    grpc_serv = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    device_pb2_grpc.add_DeviceServiceServicer_to_server(
        DeviceServiceServicer(),
        grpc_serv
    )

    grpc_serv.add_insecure_port("[::]:13830")
    grpc_serv.start()
    print("Dispositivo gRPC rodando na porta 13830")
    grpc_serv.wait_for_termination()
