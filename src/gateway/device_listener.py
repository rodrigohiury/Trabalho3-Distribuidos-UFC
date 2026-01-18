import socket
import os
import struct
import json
# import proto_dispositivo_pb2

ESTADOS_VALIDOS = ["ativo", "desativado", "ATIVO", "DESATIVADO"]
TIPOS_VALIDOS = ["sensor", "atuador"]
ARQUIVO_DADOS = "dados.json"
PORTA = 78950

def receber_protobuf(sock, classe):
    header = recv_all(sock, 4)
    tamanho = struct.unpack(">I", header)[0]
    payload = recv_all(sock, tamanho)
    msg = classe()
    msg.ParseFromString(payload)
    return msg

def enviar_protobuf(sock, mensagem):
    payload = mensagem.SerializeToString()
    header = struct.pack(">I", len(payload))
    sock.sendall(header + payload)

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
        return "Faltando campos obrigatórios":
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
    dados = carregar_json()
    print("Dados carregados para leitura:", dados)
    nome_dispositivo = device_name

    print("Buscando dispositivo:", nome_dispositivo)
    for i, d in enumerate(dados.get("dispositivos", [])):
        if d["name_device"] == nome_dispositivo:
            device = d
            break
    return i, device


def receive_info_device():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('localhost', PORTA))
        server_socket.listen(5)
        print(f"Gateway (Python) rodando na porta {PORTA} aguardando Protobuf...")

        while True:
            conn, addr = server_socket.accept()
            print(f"Conexão de: {addr[0]}")
            
            try:
                # Recebe ReadDevice com prefixo de tamanho
                msg = receber_protobuf(conn, device_pb2.DeviceStateUpdateUpdate)
                print(f"Recebido: {msg.device_name}")

                # Validação
                erro = validar_readdevice(msg)
                if erro:
                    print("Erro de validação:", erro)
                    continue

                # Carrega dados existentes
                dados = carregar_dispositivos()
                dispositivos = dados.get("dispositivos", [])

                # Cria novo dispositivo a partir do ReadDevice

                # Substitui o dispositivo existente ou adiciona se não existir
                atualizado = False
                i, d = getDevice(msg.name_device)
                if d is not None:
                    if d.["status"] != msg.status:
                        d["status"] = msg.status
                    if d.parametros != dict(msg.parametros):
                        d["parametros"] = dict(msg.parametros)
                    atualizado = True
                    print(f"Dispositivo {msg.name_device} atualizado")
                if atualizado:
                    # Salva dados completos (mantendo todos os outros intactos)
                    dispositivos[i] = d
                    dados["dispositivos"] = dispositivos
                    salvar_dispositivos(dados)
                    print(f"Dispositivo {msg.name_device} atualizado no arquivo de dados")
                else:
                    print(f"Dispositivo {msg.name_device} não encontrado para atualização")
            except Exception as e:
                print("Erro:", e)
                resposta_erro = criar_resposta_erro("save_device", str(e))
                try:
                    enviar_protobuf(conn, resposta_erro)
                except:
                    pass
            finally:
                conn.close()

    except KeyboardInterrupt:
        print("\nDesligando Gateway.")
    finally:
        server_socket.close()

def setState(device_name, req: device_pb2.DeviceState) -> device_pb2.CommandResponse:
    i, device = getDevice(device_name)
    print(f"Dispositivo encontrado: {device}")

    if device is not None:
        print("Enviando requisição de escrita ao dispositivo...")

        target = device.get("ip_device") + ":" + str(device.get("port_device"))

        channel = grpc.insecure_channel(target)
        stub = device_pb2_grpc.DeviceServiceStub(channel)

        resposta = stub.SetState(req)
        print("Resposta do dispositivo:", resposta)
    else:
        resposta = None
        raise ValueError("IP ou porta do dispositivo não informados")

    return resposta

def getState(device_name) -> device_pb2.DeviceState:
    dados = carregar_json()
    print("Dados carregados para leitura:", dados)
    nome_dispositivo = device_name

    print("Buscando dispositivo:", nome_dispositivo)
    device = buscar_dispositivo(dados, nome_dispositivo)
    print(f"Dispositivo encontrado: {device}")

    if device is not None:
        print("Enviando requisição de leitura ao dispositivo...")

        target = device.get("ip_device") + ":" + str(device.get("port_device"))

        channel = grpc.insecure_channel(target)
        stub = device_pb2_grpc.DeviceServiceStub(channel)

        resposta = stub.GetState()
        print("Resposta do dispositivo:", resposta)
    else:
        resposta = None
        raise ValueError("IP ou porta do dispositivo não informados")

    return resposta

if __name__ == "__main__":
    receive_info_device()
