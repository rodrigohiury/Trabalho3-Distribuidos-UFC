import socket
import os
import struct
import json
# import proto_dispositivo_pb2

ESTADOS_VALIDOS = ["ativo", "desligado", "ATIVO", "DESLIGADO"]
TIPOS_VALIDOS = ["sensor", "atuador"]
ARQUIVO_DADOS = "dados.json"
PORTA = 78950

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

def validar_readdevice(read_msg):
    if not read_msg.name_device or not read_msg.status or not read_msg.type_device:
        return "Faltando campos obrigatórios"
    if read_msg.status not in ESTADOS_VALIDOS:
        return "Status do dispositivo inválido"
    if read_msg.type_device not in TIPOS_VALIDOS:
        return "Tipo do dispositivo inválido"
    return None

def criar_resposta_ok(read_msg):
    resposta = proto_dispositivo_pb2.Resposta()
    ok = proto_dispositivo_pb2.RespostaOk()
    ok.comando = "save_device"
    ok.dados["name_device"] = read_msg.name_device
    ok.dados["status"] = read_msg.status
    ok.dados["type_device"] = read_msg.type_device
    ok.dados["ip_device"] = read_msg.ip_device
    ok.dados["port_device"] = str(read_msg.port_device)
    for k, v in read_msg.parametros.items():
        ok.dados[k] = v
    ok.device_info.CopyFrom(read_msg)
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

def recv_all(sock, n):
    dados = b""
    while len(dados) < n:
        pacote = sock.recv(n - len(dados))
        if not pacote:
            raise ConnectionError("Conexão encerrada")
        dados += pacote
    return dados

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
                read_msg = receber_protobuf(conn, proto_dispositivo_pb2.ReadDevice)
                print(f"Recebido: {read_msg.name_device} ({read_msg.type_device})")

                # Validação
                erro = validar_readdevice(read_msg)
                if erro:
                    resposta_erro = criar_resposta_erro("save_device", erro)
                    enviar_protobuf(conn, resposta_erro)
                    continue

                # Carrega dados existentes
                dados = carregar_dispositivos()
                dispositivos = dados.get("dispositivos", [])

                # Cria novo dispositivo a partir do ReadDevice
                novo_disp = {
                    "name_device": read_msg.name_device,
                    "ip_device": read_msg.ip_device,
                    "port_device": read_msg.port_device,
                    "status": read_msg.status,
                    "type_device": read_msg.type_device,
                    "parametros": [dict(read_msg.parametros)]
                }

                # Substitui o dispositivo existente ou adiciona se não existir
                atualizado = False
                for i, d in enumerate(dispositivos):
                    if d.get("name_device") == read_msg.name_device:
                        dispositivos[i] = novo_disp
                        atualizado = True
                        print(f"Dispositivo {read_msg.name_device} atualizado")
                        break
                if not atualizado:
                    dispositivos.append(novo_disp)
                    print(f"Dispositivo {read_msg.name_device} adicionado")

                # Salva dados completos (mantendo todos os outros intactos)
                dados["dispositivos"] = dispositivos
                salvar_dispositivos(dados)

                # Retorna RespostaOk via Protobuf
                resposta_ok = criar_resposta_ok(read_msg)
                enviar_protobuf(conn, resposta_ok)

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

if __name__ == "__main__":
    receive_info_device()
