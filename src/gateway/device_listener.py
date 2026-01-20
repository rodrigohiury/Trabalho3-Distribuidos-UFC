import socket
import os
import struct
import json
import device_pb2
import device_pb2_grpc
import time
import grpc
# import proto_dispositivo_pb2

ESTADOS_VALIDOS = ["ativo", "desativado", "ATIVO", "DESATIVADO"]
TIPOS_VALIDOS = ["sensor", "atuador"]
ARQUIVO_DADOS = "dados.json"
PORTA = 58950

def getPayload(mensagem):
    payload = mensagem.SerializeToString()
    return payload

def getProtobuf(payload, classe):
    msg = classe()
    msg.ParseFromString(payload)
    return msg

def recv_all(sock, n):
    dados = b""
    while len(dados) < n:
        pacote = sock.recv(n - len(dados))
        if not pacote:
            raise ConnectionError("Conexão encerrada")
        dados += pacote
    return dados

def carregar_dispositivos():
    if not os.path.exists(ARQUIVO_DADOS):
        return {"dispositivos": []}
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"dispositivos": []}

def salvar_dispositivos(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf8") as f:
        json.dump(dados, f, indent=4)

def validar_readdevice(msg):
    if not msg.name_device:
        return "Faltando campos obrigatórios"
    if not msg.status and not msg.parametros:
        return "Faltando campos obrigatórios"
    if msg.status not in ESTADOS_VALIDOS:
        return "Status do dispositivo inválido"
    return None

def criar_resposta_ok(msg):
    resposta = proto_dispositivo_pb2.Resposta()
    ok = proto_dispositivo_pb2.RespostaOk()
    ok.comando = "save_device"
    ok.dados["name_device"] = msg.name_device
    ok.dados["status"] = msg.status
    ok.dados["type_device"] = msg.type_device
    ok.dados["ip_device"] = msg.ip_device
    ok.dados["port_device"] = str(msg.port_device)
    for k, v in msg.parametros.items():
        ok.dados[k] = v
    ok.device_info.CopyFrom(msg)
    resposta.ok.CopyFrom(ok)
    return resposta

def criar_resposta_erro(comando, mensagem, detalhes=None):
    resposta = proto_dispositivo_pb2.Resposta()
    resposta.erro.comando = comando
    resposta.erro.mensagem = mensagem
    if detalhes:
        for k, v in detalhes.items():
            resposta.erro.detalhes[k] = v
    return resposta

def getDevice(device_name):
    dados = carregar_dispositivos()
    nome_dispositivo = device_name
    pos = -1
    device = None
    for i, d in enumerate(dados.get("dispositivos", [])):
        if d["name_device"] == nome_dispositivo:
            device = d
            pos = i
            break
    return pos, device


def receive_info_device():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('localhost', PORTA))
        print(f"[INPUT DEVICE SERVER ON] Gateway (Python) rodando na porta {PORTA} aguardando Protobuf...")

        while True:
            conn, addr = server_socket.recvfrom(65535)
            print(f"[CONNECTION ESTABLISHED] Conexão de: {addr[0]}")
            
            try:
                # Recebe ReadDevice com prefixo de tamanho
                msg = getProtobuf(conn, device_pb2.DeviceResponse)

                tipo = msg.WhichOneof("tipo")
                print(f"[MSG RECEIVED]: {tipo}")

                if tipo == "state":
                    resposta = saveState(msg.state)
                elif tipo == "info":
                    resposta = saveInfo(msg.info)
                elif tipo == "id":
                    resposta = saveID(msg.id) 
                else:
                    resposta = device_pb2.CommandResponse()
                    resposta.status = "error"
                    resposta.message = "Protobuf inválido: tipo desconhecido"
                    raise ValueError("Tipo de mensagem desconhecido")
                print("Resposta gerada:", resposta)
                response_payload = getPayload(resposta)
                server_socket.sendto(response_payload, addr)
            except ConnectionResetError as e:
                print("[ERROR] Erro de conexão:", e)
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind(('localhost', PORTA))
            except Exception as e:
                print("[ERROR]:", e)
    except KeyboardInterrupt:
        print("\n[SHUTTING DOWN] Desligando Gateway.")
    finally:
        server_socket.close()

def saveState(req: device_pb2.DeviceState) -> device_pb2.CommandResponse:
    device_name = req.device_name
    i, device = getDevice(device_name)

    if device is not None:
        print(f"[STATE] Salvando estado no dispositivo {device_name}...")

        device["status"] = req.status
        device["parametros"] = dict(req.parameters)
        device["last_update"] = str(time.time())

        resposta = saveDevice(i, device)
        if resposta:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "ok"
            msgReply.message = "Estado salvo com sucesso"
            return msgReply
        else:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "error"
            msgReply.message = "Erro no salvamento do estado"
            return msgReply
    else:
        msgReply = device_pb2.CommandResponse()
        msgReply.status = "error"
        msgReply.message = "Dispositivo não encontrado"
        return msgReply

def saveInfo(req: device_pb2.DeviceInfo) -> device_pb2.CommandResponse:
    device_name = req.device_name
    i, device = getDevice(device_name)

    if device is not None:
        print(f"[INFO] Salvando info no dispositivo {device_name}...")

        device["ip_device"] = req.device_ip
        device["port_device"] = req.device_port
        device["type_device"] = req.device_type
        device["name_device"] = req.device_name
        device["status"] = req.status
        device["parametros"] = dict(req.parametros)
        device["last_update"] = str(time.time())

        resposta = saveDevice(i, device)
        if resposta:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "ok"
            msgReply.message = "Info salva com sucesso"
            return msgReply
        else:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "error"
            msgReply.message = "Erro no salvamento da info"
            return msgReply
    else:
        dev = {
            "name_device": req.device_name,
            "ip_device": req.device_ip,
            "port_device": req.device_port,
            "type_device": req.device_type,
            "status": req.status,
            "parametros": dict(req.parametros),
            "last_update": str(time.time())
        }
        resposta = saveNewDevice(dev)
        if resposta:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "ok"
            msgReply.message = "Info salva com sucesso [FIRST_TIME]"
            return msgReply
        else:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "error"
            msgReply.message = "Erro no salvamento da info"
            return msgReply

def saveID(req: device_pb2.DeviceID) -> device_pb2.CommandResponse:
    device_name = req.device_name
    i, device = getDevice(device_name)

    if device is not None:
        print(f"[ID] Salvando id no dispositivo {device_name}...")

        device["ip_device"] = req.device_ip
        device["port_device"] = req.device_port
        device["type_device"] = req.device_type
        device["name_device"] = req.device_name
        device["last_update"] = str(time.time())


        resposta = saveDevice(i, device)
        if resposta:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "ok"
            msgReply.message = "ID salvo com sucesso"
            return msgReply
        else:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "error"
            msgReply.message = "Erro no salvamento do ID"
            return msgReply
    else:
        dev = {
            "name_device": req.device_name,
            "ip_device": req.device_ip,
            "port_device": req.device_port,
            "type_device": req.device_type,
            "last_update": str(time.time())
        }
        resposta = saveNewDevice(dev)
        if resposta:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "ok"
            msgReply.message = "ID salva com sucesso [FIRST_TIME]"
            return msgReply
        else:
            msgReply = device_pb2.CommandResponse()
            msgReply.status = "error"
            msgReply.message = "Erro no salvamento da id"
            return msgReply

def setState(req: device_pb2.DeviceState) -> device_pb2.CommandResponse:
    device_name = req.device_name
    i, device = getDevice(device_name)

    if device is not None:
        print("[WRITE] Enviando requisição de escrita ao dispositivo...")

        target = device.get("ip_device") + ":" + "1" + str(device.get("port_device"))

        channel = grpc.insecure_channel(target)
        stub = device_pb2_grpc.DeviceServiceStub(channel)

        resposta = stub.SetState(req)
        if resposta is not None:
            print("[WRITE] Resposta do dispositivo:", resposta)
            if resposta.response == "ok":
                device["status"] = req.status
                for k, v in req.parameters.items():
                    device["parametros"][k] = v
                device["last_update"] = str(time.time())
                saveDevice(i, device)
    else:
        msgReply = device_pb2.CommandResponse()
        msgReply.response = "error"
        msgReply.message = "Dispositivo não encontrado"
        return msgReply
    return resposta

def getState(device_name) -> device_pb2.DeviceState:
    dados = carregar_dispositivos()
    nome_dispositivo = device_name

    device = buscar_dispositivo(dados, nome_dispositivo)

    if device is not None:

        target = device.get("ip_device") + ":" + str(device.get("port_device"))

        channel = grpc.insecure_channel(target)
        stub = device_pb2_grpc.DeviceServiceStub(channel)

        resposta = stub.GetState()
        print("[GET] Resposta do dispositivo:", resposta)
    else:
        resposta = None
        raise ValueError("Dispositivo não encontrado")

    return resposta

def saveDevice(i, device):
    dados = carregar_dispositivos()
    dispositivos = dados.get("dispositivos", [])
    dispositivos[i] = device
    dados["dispositivos"] = dispositivos
    try:
        salvar_dispositivos(dados)
        print(f"[SAVE] Dispositivo {device['name_device']} salvo no arquivo de dados")
        return True
    except Exception as e:
        print(f"[ERROR] Erro ao salvar dispositivo {device['name_device']}: {e}")
        return False

def saveNewDevice(device):
    dados = carregar_dispositivos()
    dispositivos = dados.get("dispositivos", [])
    dispositivos.append(device)
    dados["dispositivos"] = dispositivos
    try:
        salvar_dispositivos(dados)
        print(f"[SAVE] Dispositivo {device['name_device']} salvo no arquivo de dados")
        return True
    except Exception as e:
        print(f"[ERROR] Erro ao salvar dispositivo {device['name_device']}: {e}")
        return False

if __name__ == "__main__":
    receive_info_device()
