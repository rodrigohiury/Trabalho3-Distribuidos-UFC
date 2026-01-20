
import socket, json
import struct
from datetime import datetime
from google.protobuf import json_format
# from proto_dispositivo_pb2 import Requisicao, Resposta, RespostaOk, RespostaErro
import sys
import os

sys.path.append("../")
# import proto_dispositivo_pb2 as proto_dispositivo_pb2
import proto_gateway_pb2 as proto_gateway_pb2
from google.protobuf.json_format import MessageToJson

# from func_gateway_request_device import enviar_requisicao_tcp as enviar_req_device
import device_pb2
import device_pb2_grpc
from device_listener import setState, getState


IP_DEVICE = "localhost"
PORT_DEVICE = 5001


def carregar_json():
    with open("dados.json", "r", encoding="utf-8") as f:
        return json.load(f)
    
def buscar_dispositivo(dados, nome_disopsitivo):
    for d in dados.get("dispositivos", []):
        if d.get("name_device") == nome_disopsitivo:
            return d

    return None


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
        print("[ERROR] Erro ao enviar mensagem:", e)
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
        return msg

    except Exception as e:
        print("[ERROR] Erro ao receber resposta:", e)
        raise




def tratar_escrita(req: proto_gateway_pb2.Requisicao):

    d = buscar_dispositivo(carregar_json(), req.name_device)
    newReq = device_pb2.DeviceState()
    newReq.device_name = req.name_device
    if req.escrever.info_device.status != "":
        newReq.status = req.escrever.info_device.status
    else:
        newReq.status = d["status"]
    if req.escrever.info_device.parametros is not None:
        for k, v in req.escrever.info_device.parametros.items():
            newReq.parameters[k] = v
    else: 
        for k, v in d["parametros"].items():
            newReq.parameters[k] = v
    resposta = setState(newReq)

    return resposta

def tratar_leitura(req):
    dados = carregar_json()
    nome_dispositivo = req.name_device

    device = buscar_dispositivo(dados, nome_dispositivo)

    if device is not None:
        target = device.get("ip_device") + ":" + str(device.get("port_device"))
        channel = grpc.insecure_channel(target)
        stub = device_pb2_grpc.DeviceServiceStub(channel)

        resposta = stub.GetState()
    else:
        resposta = None
        raise ValueError("IP ou porta do dispositivo não informados")
    return resposta
        

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
        device.status = item.get("status", "")
        # parametros pode ser uma lista com dict ou um dict direto
        params = item.get("parametros", {})
        if isinstance(params, list) and len(params) > 0:
            # Se for lista, pega o primeiro dict e mescla todos
            merged_params = {}
            for p in params:
                if isinstance(p, dict):
                    merged_params.update(p)
            device.parametros.update(merged_params)
        elif isinstance(params, dict):
            # Se for dict direto, usa como está
            device.parametros.update(params)
    
    return resposta



def tratar_requisicao(req: proto_gateway_pb2.Requisicao) -> proto_gateway_pb2.Resposta:
    tipo = req.WhichOneof("tipo")

    if tipo == "ler":
        print("[READ REQ] Requisição de leitura recebida")
        return tratar_leitura(req)
    elif tipo == "escrever":
        print("[WRITE REQ] Requisição de escrita recebida")
        return tratar_escrita(req)
    elif tipo == "listar":
        print("[LIST REQ] Requisição de listagem recebida")
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

    print(f"[LISTENING] Dispositivo escutando em {IP_DEVICE}:{PORT_DEVICE}")

    while True:
        conn, addr = socket_device.accept()
        print("[CONNECTION ESTABLISHED] Conexão recebida de:", addr)

        try:
            req = receber_protobuf(conn, proto_gateway_pb2.Requisicao)

            resp = tratar_requisicao(req)
            enviar_protobuf(conn, resp)

        except Exception as e:
            print("[ERROR]:", e)

        finally:
            conn.close()

 
if __name__ == "__main__":
    socket_receiv_client_request_device()
     