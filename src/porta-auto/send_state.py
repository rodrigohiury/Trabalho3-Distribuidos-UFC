import socket
import json
import device_pb2
import device_pb2_grpc


def carregar_json(caminho_arquivo):
    """
    Lê um arquivo JSON e retorna os dados carregados como dicionário ou lista.

    :param caminho_arquivo: Caminho do arquivo JSON.
    :return: Dados do JSON (dict ou list).
    """
    
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho_arquivo}")
    except json.JSONDecodeError:
        print("Erro ao decodificar o JSON. Verifique se o arquivo está válido.")
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")

def enviar_estado_atual(gateway_ip, gateway_port):
    dados_device = carregar_json("dados.json")
    msg = device_pb2.DeviceResponse()
    msg.state.device_name = dados_device["name_device"]
    msg.state.status = dados_device["status"]
    for k, v in dados_device["parametros"].items():
        msg.state.parameters[k] = v
    payload = msg.SerializeToString()
    try:

        ttl = 128

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # TTL multicast
        sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_MULTICAST_TTL,
            ttl.to_bytes(1, byteorder="big")
        )
        sock.sendto(payload, (gateway_ip, gateway_port))
        conn, addr = sock.recvfrom(1024)
        print("[AUTO CHANGE] Estado atual enviado ao gateway com sucesso.")
        sock.close()
    except Exception as e:
        print(f"Erro ao enviar estado atual: {str(e)}")
