
import socket, json
import struct
from datetime import datetime
from google.protobuf import json_format
# from proto_dispositivo_pb2 import Requisicao, Resposta, RespostaOk, RespostaErro
import sys
import os

# sys.path.append("../")
from proto.proto_dispositivo_pb2 import proto_dispositivo_pb2 as proto_dispositivo_pb2
from proto.proto_endereco_gateway_pb2 import proto_gateway_pb2 as proto_gateway_pb2
from google.protobuf.json_format import MessageToJson

from func_gateway_request_device import enviar_requisicao_tcp as enviar_req_device


IP_DEVICE = "localhost"
PORT_DEVICE = 5001


def carregar_json():
    with open("dados.json", "r", encoding="utf-8") as f:
        return json.load(f)
    
def buscar_ip_porta_dispositivo(dados, nome_disopsitivo):
    
    for d in dados.get("dispositivos", []):
        if d.get("name_device") == nome_disopsitivo:
            return d["ip_device"], d["port_device"]

    return None, None


def recv_all(sock, n):
    dados = b""
    while len(dados) < n:
        pacote = sock.recv(n - len(dados))
        if not pacote:
            raise ConnectionError("Conexão encerrada")
        dados += pacote
    return dados


def enviar_protobuf(sock, mensagem):
    """Serializa a mensagem protobuf e envia com prefixo de tamanho."""
    try:
        payload = mensagem.SerializeToString()
        header = struct.pack(">I", len(payload))
        sock.sendall(header + payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)
        raise

def receber_protobuf(sock, classe):
    """Recebe resposta prefixada e converte para objeto protobuf."""
    try:
        header = recv_all(sock, 4)
        if not header:
            return None

        tamanho = struct.unpack(">I", header)[0]
        payload = recv_all(sock, tamanho)

        msg = classe()
        msg.ParseFromString(payload)
        print(f"msg {msg}")
        return msg

    except Exception as e:
        print("Erro ao receber resposta:", e)
        raise




def tratar_escrita(req: proto_dispositivo_pb2.Requisicao) -> proto_dispositivo_pb2.Resposta:
    dados = carregar_json()
    nome_dispositivo = req.name_device

    ip_d, port_d = buscar_ip_porta_dispositivo(dados, nome_dispositivo)

    if ip_d and port_d:
        resposta = enviar_req_device(
            ip_d,
            port_d,
            req.name_client,
            req.name_device,
            req.operacao,
            req.status,
            req.type_device,
            req.parametros)
    else:
        resposta = None
        raise ValueError("IP ou porta do dispositivo não informados")
        

    return resposta

def tratar_leitura(req: proto_dispositivo_pb2.Requisicao) -> proto_dispositivo_pb2.Resposta:
    dados = carregar_json()
    nome_dispositivo = req.name_device

    ip_d, port_d = buscar_ip_porta_dispositivo(dados, nome_dispositivo)

    if ip_d and port_d:
        resposta = enviar_req_device(
            ip_d,
            port_d,
            req.name_client,
            req.name_device,
            req.operacao,
            req.type_device,
        )
    else:
        resposta = None
        raise ValueError("IP ou porta do dispositivo não informados")
        

def tratar_listagem(req: proto_gateway_pb2.Requisicao) -> proto_gateway_pb2.Resposta:
    dados = carregar_json()

    # Cria a mensagem Protobuf
    resposta = proto_gateway_pb2.RespostaOkLista()
    resposta.comando = "LISTAR"

    # (opcional) dados extras
    resposta.dados["total"] = str(len(dados["dispositivos"]))

    # Preenche a lista de devices
    for item in dados.get("dispositivos", []):
        device = resposta.devices.add()
        device.name_device = item.get("name_device", "")
        device.ip_device = item.get("ip_device", "")
        device.port_device = int(item.get("port_device", 0))
        device.type_device = item.get("type_device", "")

    return resposta


def tratar_requisicao(req: proto_gateway_pb2.Requisicao) -> proto_gateway_pb2.Resposta:
    tipo = req.WhichOneof("tipo")

    if tipo == "ler":
        return tratar_leitura(req)

    elif tipo == "escrever":
        return tratar_escrita(req)
    elif tipo == "listar":
        return tratar_listagem(req)

    else:
        return erro("REQUISICAO_INVALIDA", "Tipo de requisição não reconhecido")
    



def erro(comando, mensagem):
    resposta = proto_dispositivo_pb2.Resposta()
    resposta.erro.comando = comando
    resposta.erro.mensagem = mensagem
    resposta.erro.detalhes["timestamp"] = datetime.now().isoformat()
    return resposta

def socket_receiv_client_request_device():
    socket_device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_device.bind((IP_DEVICE, 5012))
    socket_device.listen(1)

    print(f"Dispositivo escutando em {IP_DEVICE}:{PORT_DEVICE}")

    while True:
        conn, addr = socket_device.accept()
        print("Conexão recebida de:", addr)

        try:
            req = receber_protobuf(conn, proto_gateway_pb2.Requisicao)
            print("Requisição recebida:")
            print(MessageToJson(req))

            resp = tratar_requisicao(req)
            enviar_protobuf(conn, resp)

        except Exception as e:
            print("Erro:", e)

        finally:
            conn.close()

 
if __name__ == "__main__":
    socket_receiv_client_request_device()
     