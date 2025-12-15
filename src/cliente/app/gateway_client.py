import grpc
from app.proto import gateway_pb2, gateway_pb2_grpc
import socket
import struct


class GatewayClient:
    def __init__(self, host="localhost", port=5012):
        channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = gateway_pb2_grpc.GatewayServiceStub(channel)

    def enviar_protobuf(self, sock, msg):
        payload = msg.SerializeToString()
        sock.sendall(struct.pack(">I", len(payload)) + payload)
    
    def receber_protobuf(self, sock, cls):
        header = recv_all(sock, 4)
        size = struct.unpack(">I", header)[0]
        payload = recv_all(sock, size)
        msg = cls()
        msg.ParseFromString(payload)
        return msg

    # ==============================
    # LISTAR DISPOSITIVOS
    # ==============================
    def get_devices(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 5012))

        req = gateway_pb2.Requisicao(
            name_client="web-client",
            name_device="",
            listar=gateway_pb2.RequisicaoListar(
                operacao=gateway_pb2.ComandoOperacao(
                    operacao=gateway_pb2.ComandoOperacao.LISTAR
                )
            )
        )


        print("Enviando requisição LISTAR...")
        self.enviar_protobuf(sock, req)

        resp = self.receber_protobuf(sock, gateway_pb2.RespostaOkLista)

        print("\nResposta recebida:")

        print("\nDispositivos:")


        sock.close()

        # requisicao = gateway_pb2.Requisicao(
        #     name_client="web-client",
        #     name_device="",
        #     listar=gateway_pb2.RequisicaoListar(
        #         operacao=gateway_pb2.ComandoOperacao(
        #             operacao=gateway_pb2.ComandoOperacao.LISTAR
        #         )
        #     )
        # )

        # resposta = self.stub.EnviarRequisicao(requisicao)

        # if resposta.HasField("erro"):
        #     raise Exception(resposta.erro.mensagem)

        # # resposta do tipo lista
        return [
            {
                "name": d.name_device,
                "ip": d.ip_device,
                "port": d.port_device,
                "type": d.type_device
            }
            for d in resp.devices
        ]

    # ==============================
    # ENVIAR COMANDO (ESCREVER)
    # ==============================
    def send_command(self, device_name, parametros: dict):
        requisicao = gateway_pb2.Requisicao(
            name_client="web-client",
            name_device=device_name,
            escrever=gateway_pb2.RequisicaoEscrever(
                operacao=gateway_pb2.ComandoOperacao(
                    operacao=gateway_pb2.ComandoOperacao.ESCREVER
                ),
                info_device=gateway_pb2.InfoDeviceClient(
                    parametros=parametros
                )
            )
        )

        resposta = self.stub.EnviarRequisicao(requisicao)

        if resposta.HasField("erro"):
            return {
                "status": "error",
                "message": resposta.erro.mensagem
            }

        return {
            "status": "ok",
            "dados": dict(resposta.ok.dados)
        }
    
    
    


gateway = GatewayClient()






def recv_all(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Conexão encerrada")
        data += packet
    return data


