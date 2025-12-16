import socket
import struct
import proto_dispositivo_pb2 as pb


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

def enviar_requisicao_tcp(
        ip: str,
        porta: int,
        name_client: str,
        name_device: str,
        operacao: str,
        status: str = None,
        type_device: str = None,
        parametros: dict = None,
        timeout: int = 5
    ):
    """
    operacao: 'LER' ou 'ESCREVER'
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    print(f"Conectando ao dispositivo em {ip}:{porta}...")
    sock.connect((ip, porta))

    req = pb.Requisicao()
    print("Montando requisição para dispositivo...")
    req.name_client = name_client
    print(f"Nome do cliente definido: {name_client}")
    req.name_device = name_device
    print(f"Nome do dispositivo definido: {name_device}")

    if operacao.upper() == "LER":
        print("Operação definida como LER")
        req.ler.operacao.operacao = pb.ComandoOperacao.LER

    elif operacao.upper() == "ESCREVER":
        print("Operação definida como ESCREVER")
        req.escrever.operacao.operacao = pb.ComandoOperacao.ESCREVER

        if status is not None:
            print(f"Definindo status do dispositivo para: {status}")
            req.escrever.info_device.status = status

        if type_device is not None:
            print(f"Definindo tipo do dispositivo para: {type_device}")
            req.escrever.info_device.type_device = type_device

        if parametros:
            print(f"Definindo parâmetros do dispositivo: {parametros}")
            for k, v in parametros.items():
                req.escrever.info_device.parametros[k] = str(v)

    else:
        raise ValueError("Operação inválida: use 'LER' ou 'ESCREVER'")

    # Envia requisição
    print("Enviando requisição ao dispositivo...")
    enviar(sock, req)

    # Recebe resposta
    print("Aguardando resposta do dispositivo...")
    resp = receber(sock, pb.Resposta)

    sock.close()
    print(f"Resposta recebida do dispositivo. {resp}")
    return resp
