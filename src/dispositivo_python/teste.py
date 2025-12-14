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
print(pb.ComandoOperacao.ESCREVER)
req.escrever.operacao.operacao = pb.ComandoOperacao.ESCREVER
req.escrever.info_device.status = "ligado-"
req.escrever.info_device.type_device = "sensor"
req.escrever.info_device.parametros["temperatura"] = "1000°"
req.escrever.info_device.parametros["movimentacao"] = "nao"

print(req)

#   string status = 1;
#   string type_device = 2;
#   map<string, string> parametros = 3;

# req.ler.operacao.operacao = pb.ComandoOperacao.LER

enviar(sock, req)
resp = receber(sock, pb.Resposta)

print("Resposta:")
print(resp)

sock.close()


import socket
import struct
import dispositivo_pb2 as pb


def enviar(sock, msg):
    payload = msg.SerializeToString()
    sock.sendall(struct.pack(">I", len(payload)) + payload)


def receber(sock, classe):
    header = sock.recv(4)
    if not header:
        raise ConnectionError("Conexão encerrada")

    tamanho = struct.unpack(">I", header)[0]

    dados = b""
    while len(dados) < tamanho:
        chunk = sock.recv(tamanho - len(dados))
        if not chunk:
            raise ConnectionError("Conexão encerrada")
        dados += chunk

    msg = classe()
    msg.ParseFromString(dados)
    return msg


# ------------------------
