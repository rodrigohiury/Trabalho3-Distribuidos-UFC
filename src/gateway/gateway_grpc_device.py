import grpc

import device_pb2
import device_pb2_grpc

def main():
    channel = grpc.insecure_channel("localhost:50051")
    stub = device_pb2_grpc.DeviceServiceStub(channel)

    # Info do dispositivo
    info = stub.GetInfo(device_pb2.Empty())
    print("Dispositivo:", info.device_id, info.device_type)

    # Estado atual
    state = stub.GetState(device_pb2.Empty())
    print("Estado atual:", state.state)

    # Enviar comando
    response = stub.SetState(
        device_pb2.DeviceCommand(
            command="open",
            parameters={"duration": "5"}
        )
    )
    print("Resposta:", response.status)

    # Estado depois
    state = stub.GetState(device_pb2.Empty())
    print("Estado final:", state.state)

if __name__ == "__main__":
    main()

def sendComand(device_name, command):
    