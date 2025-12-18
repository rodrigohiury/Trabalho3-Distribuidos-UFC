import socket
import struct
import proto_dispositivo_pb2

def recv_all(sock, n):
    """Recebe exatamente n bytes do socket."""
    dados = b""
    while len(dados) < n:
        pacote = sock.recv(n - len(dados))
        if not pacote:
            raise ConnectionError("Conexão encerrada")
        dados += pacote
    return dados

def enviar_protobuf(sock, mensagem):
    """Serializa a mensagem protobuf e envia com prefixo de tamanho (4 bytes)."""
    payload = mensagem.SerializeToString()
    header = struct.pack(">I", len(payload))
    sock.sendall(header + payload)

def receber_protobuf(sock, classe):
    """Recebe mensagem Protobuf prefixada por 4 bytes de tamanho e retorna o objeto."""
    header = recv_all(sock, 4)
    tamanho = struct.unpack(">I", header)[0]
    payload = recv_all(sock, tamanho)
    msg = classe()
    msg.ParseFromString(payload)
    return msg

def enviar_dispositivo(ip_servidor, porta_servidor, dispositivo_json):
    """
    Envia um dispositivo via socket para o servidor Protobuf usando protocolo com prefixo de tamanho.
    """
    # Cria a mensagem ReadDevice
    msg = proto_dispositivo_pb2.ReadDevice()
    msg.name_device = dispositivo_json.get("name_device", "")
    msg.ip_device = dispositivo_json.get("ip_device", "")
    msg.port_device = dispositivo_json.get("port_device", 0)
    msg.status = dispositivo_json.get("status", "")
    msg.type_device = dispositivo_json.get("type_device", "")

    # Converte lista de dicts em um único map
    parametros_lista = dispositivo_json.get("parametros", [])
    parametros_map = {}
    for d in parametros_lista:
        parametros_map.update(d)
    if "value_device" in dispositivo_json:
        parametros_map["value_device"] = str(dispositivo_json["value_device"])
    msg.parametros.update(parametros_map)

    # Conecta, envia e recebe resposta
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_servidor, porta_servidor))
            enviar_protobuf(s, msg)

            # Recebe resposta como Protobuf Resposta
            resposta = receber_protobuf(s, proto_dispositivo_pb2.Resposta)
            if resposta.HasField("ok"):
                print("Resposta OK:")
                print("Comando:", resposta.ok.comando)
                print("Dados:", dict(resposta.ok.dados))
                print("Device Info:", dict(resposta.ok.device_info.parametros))
            elif resposta.HasField("erro"):
                print("Resposta ERRO:")
                print("Comando:", resposta.erro.comando)
                print("Mensagem:", resposta.erro.mensagem)
                print("Detalhes:", dict(resposta.erro.detalhes))

    except Exception as e:
        print("Erro ao enviar dispositivo:", e)


if __name__ == "__main__":
    dispositivo_exemplo = {
        "name_device": "Luz Quarto",
        "ip_device": "localhost",
        "port_device": 5003,
        "status": "ativo",
        "type_device": "atuador",
        "parametros": [
            {}
        ]
    }

    enviar_dispositivo("127.0.0.1", 7895, dispositivo_exemplo)
