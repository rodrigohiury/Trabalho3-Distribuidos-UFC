import socket
import struct
import dispositivo_pb2 as pb

def enviar(sock, msg):
    payload = msg.SerializeToString()
    sock.sendall(struct.pack(">I", len(payload)) + payload)

def receber(sock, classe):
    header = sock.recv(4)
    tamanho = struct.unpack(">I", header)[0]
    dados = sock.recv(tamanho)
    msg = classe()
    msg.ParseFromString(dados)
    return msg

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 5001))

req = pb.Requisicao()
req.name_client = "cliente_teste"
req.name_device = "Sensor de InfraVermelho"
req.ler.operacao.operacao = pb.ComandoOperacao.LER

enviar(sock, req)
resp = receber(sock, pb.Resposta)

print("Resposta:")
print(resp)

sock.close()
