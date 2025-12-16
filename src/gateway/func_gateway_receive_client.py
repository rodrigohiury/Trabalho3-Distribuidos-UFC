
import socket, json
import struct
from datetime import datetime
from google.protobuf import json_format
# from proto_dispositivo_pb2 import Requisicao, Resposta, RespostaOk, RespostaErro
import sys
import os

sys.path.append("../")
import proto_dispositivo_pb2 as proto_dispositivo_pb2
import proto_gateway_pb2 as proto_gateway_pb2
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
        print(f"Payload a ser enviado: {payload}")
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




def tratar_escrita(req: proto_gateway_pb2.Requisicao) -> proto_dispositivo_pb2.Resposta:
    dados = carregar_json()
    print("Dados carregados para escrita:", dados)
    nome_dispositivo = req.name_device

    print("Buscando IP e porta do dispositivo:", nome_dispositivo)
    ip_d, port_d = buscar_ip_porta_dispositivo(dados, nome_dispositivo)
    print(f"IP e porta encontrados: {ip_d}:{port_d}")

    if ip_d and port_d is not None:
        print("Enviando requisição de escrita ao dispositivo...")

        # extrai subcampos da mensagem 'escrever'
        info = None
        try:
            info = req.escrever.info_device
        except Exception:
            info = None

        status = info.status if info and hasattr(info, 'status') else None
        type_device = info.type_device if info and hasattr(info, 'type_device') else None
        parametros = dict(info.parametros) if info and hasattr(info, 'parametros') else None

        operacao = "ESCREVER"

        resposta = enviar_req_device(
            ip_d,
            port_d,
            req.name_client,
            req.name_device,
            operacao,
            status,
            type_device,
            parametros)
    else:
        resposta = None
        raise ValueError("IP ou porta do dispositivo não informados")

    return resposta

def tratar_leitura(req: proto_dispositivo_pb2.Requisicao) -> proto_dispositivo_pb2.Resposta:
    dados = carregar_json()
    print("Dados carregados para leitura:", dados)
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
    print("Dados carregados para listagem:", dados)

    # Cria a mensagem Protobuf
    resposta = proto_gateway_pb2.RespostaOkLista()
    resposta.comando = "LISTAR"

    # (opcional) dados extras
    resposta.dados["total"] = str(len(dados["dispositivos"]))

    print("Preenchendo dispositivos na resposta...")
    # Preenche a lista de devices
    for item in dados.get("dispositivos", []):
        print("---------------------------------------------------------------------")
        print("Item:", item)
        print("add")
        device = resposta.devices.add()
        print("name")
        device.name_device = item.get("name_device", "")
        print(device.name_device)
        print("ip")
        device.ip_device = item.get("ip_device", "")
        print(device.ip_device)
        print("port")
        device.port_device = int(item.get("port_device", 0))
        print(device.port_device)
        print("type")
        device.type_device = item.get("type_device", "")
        print(device.type_device)
        print("status")
        device.status = item.get("status", "")
        print(device.status)
        print("parametros")
        device.parametros.update(item.get("parametros", {}))
        print(device.parametros)
    
    print("Resposta de listagem criada:", resposta)
    return resposta



def tratar_requisicao(req: proto_gateway_pb2.Requisicao) -> proto_gateway_pb2.Resposta:
    print("Tratando requisição...")
    tipo = req.WhichOneof("tipo")
    print(f"Tipo de requisição: {tipo}")

    if tipo == "ler":
        print("Req de leitura")
        return tratar_leitura(req)
    elif tipo == "escrever":
        print("Req de escrita")
        return tratar_escrita(req)
    elif tipo == "listar":
        print("Req de listagem")
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
            print("----------------------------------------------------")
            print("Enviando resposta:")
            print(resp)
            enviar_protobuf(conn, resp)

        except Exception as e:
            print("Erro:", e)

        finally:
            conn.close()

 
if __name__ == "__main__":
    socket_receiv_client_request_device()
     