
import socket, json
import struct
from datetime import datetime
from google.protobuf import json_format
# from proto_dispositivo_pb2 import Requisicao, Resposta, RespostaOk, RespostaErro
import proto_dispositivo_pb2 as proto_dispositivo_pb2
from google.protobuf.json_format import MessageToJson


IP_DEVICE = "localhost"
PORT_DEVICE = 5003


def carregar_json():
    with open("dados.json", "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(dados):
    with open("dados.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


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
    info = req.escrever.info_device

    # valida tipo do dispositivo
    if not(dados["type_device"] == "sensor"):
        # atualiza parâmetros
        for k, v in info.parametros.items():
            dados["parametros"][0][k] = v


        # return erro("ESCREVER", "Sensores não aceitam escrita")

    # atualiza status
    if info.status:
        dados["status"] = info.status

    # atualiza parâmetros
    # for k, v in info.parametros.items():
    #     dados["parametros"][0][k] = v

    salvar_json(dados)

    resposta = proto_dispositivo_pb2.Resposta()
    ok = resposta.ok
    ok.comando = "ESCREVER"
    ok.dados["resultado"] = "Dispositivo atualizado com sucesso"
    ok.dados["timestamp"] = datetime.now().isoformat()

    return resposta



def tratar_requisicao(req: proto_dispositivo_pb2.Requisicao) -> proto_dispositivo_pb2.Resposta:
    tipo = req.WhichOneof("tipo")

    if tipo == "ler":
        return tratar_leitura(req)

    elif tipo == "escrever":
        return tratar_escrita(req)

    else:
        return erro("REQUISICAO_INVALIDA", "Tipo de requisição não reconhecido")
    


def tratar_leitura(req: proto_dispositivo_pb2.Requisicao) -> proto_dispositivo_pb2.Resposta:
    dados = carregar_json()

    resposta = proto_dispositivo_pb2.Resposta()
    ok = resposta.ok

    ok.comando = "LER"
    ok.dados["timestamp"] = datetime.now().isoformat()

    device = ok.device_info
    device.name_device = dados["name_device"]
    device.ip_device = dados["ip_device"]
    device.port_device = dados["port_device"]
    device.status = dados["status"]
    device.type_device = dados["type_device"]

    for k, v in dados["parametros"][0].items():
        device.parametros[k] = v

    return resposta


def erro(comando, mensagem):
    resposta = proto_dispositivo_pb2.Resposta()
    resposta.erro.comando = comando
    resposta.erro.mensagem = mensagem
    resposta.erro.detalhes["timestamp"] = datetime.now().isoformat()
    return resposta

def socket_tcp_device_receive():
    socket_device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_device.bind((IP_DEVICE, PORT_DEVICE))
    socket_device.listen(1)

    print(f"Dispositivo escutando em {IP_DEVICE}:{PORT_DEVICE}")

    while True:
        conn, addr = socket_device.accept()
        print("Conexão recebida de:", addr)

        try:
            req = receber_protobuf(conn, proto_dispositivo_pb2.Requisicao)
            print("Requisição recebida:")
            print(MessageToJson(req))

            resp = tratar_requisicao(req)
            enviar_protobuf(conn, resp)

        except Exception as e:
            print("Erro:", e)

        finally:
            conn.close()

 
if __name__ == "__main__":
    socket_tcp_device_receive()
     