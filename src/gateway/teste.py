import socket
import struct
import gateway_pb2 as gateway_pb2


def enviar_protobuf(sock, msg):
    payload = msg.SerializeToString()
    sock.sendall(struct.pack(">I", len(payload)) + payload)


def recv_all(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Conexão encerrada")
        data += packet
    return data


def receber_protobuf(sock, cls):
    header = recv_all(sock, 4)
    size = struct.unpack(">I", header)[0]
    payload = recv_all(sock, size)
    msg = cls()
    msg.ParseFromString(payload)
    return msg


# =========================
# TESTE LISTAR
# =========================

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 5012))

req = gateway_pb2.Requisicao()
req.name_client = "cliente_teste"
req.name_device = "Sensor de InfraVermelho"
req.escrever.info_device.status = "ligado-"
req.escrever.info_device.type_device = "sensor"
req.escrever.info_device.parametros["temperatura"] = "1000°"
req.escrever.info_device.parametros["movimentacao"] = "nao"
# ONEOF: LISTAR
req.listar.operacao.operacao = gateway_pb2.ComandoOperacao.LER

print("Enviando requisição LISTAR...")
enviar_protobuf(sock, req)

resp = receber_protobuf(sock, gateway_pb2.RespostaOk)

print("\nResposta recebida:")
# print("Comando:", resp.comando)
# print("Dados:", dict(resp.dados))

print("\nDispositivos:")
print(resp)
# for d in resp.devices:
#     print(
#         f"- {d.name_device} | {d.ip_device}:{d.port_device} | {d.type_device}"
#     )

sock.close()
