import socket
import struct
import proto_endereco_gateway_pb2 as pb
from device_request_info_tcp import enviar_dispositivo
import json


def carregar_json(caminho_arquivo):
    """
    Lê um arquivo JSON e retorna os dados carregados como dicionário ou lista.

    :param caminho_arquivo: Caminho do arquivo JSON.
    :return: Dados do JSON (dict ou list).
    """
    import os
    
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

def start_udp_listener(
    multicast_ip="224.1.1.1",
    multicast_port=5007
):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", multicast_port))

    mreq = struct.pack(
        "4sl",
        socket.inet_aton(multicast_ip),
        socket.INADDR_ANY
    )
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Escutando multicast {multicast_ip}:{multicast_port}")

    while True:
        data, addr = sock.recvfrom(1024)

        msg = pb.EnderecoInfo()
        msg.ParseFromString(data)

        print(
            f"Recebido de {addr[0]}:"
            f"\ngateway=   >{msg.id_gateway_for_save_info}<   \n "
            f"porta=    >{msg.port_gateway_for_save_info}<     "
        )

        dados_device = carregar_json("dados.json")
        # print(dados_device["port_device"])
        dados_device["port_device"] = int(dados_device["port_device"])
        print(dados_device["port_device"])

        # print(dados_device)
        dispositivo_exemplo = {
            "name_device": "Porta Automatica",
            "ip_device": "localhost",
            "port_device": 5003,
            "status": "ativo",
            "type_device": "atuador",
            "parametros": [
                {}
            ]
        }

        print(type(dispositivo_exemplo))
        enviar_dispositivo(msg.id_gateway_for_save_info, int(msg.port_gateway_for_save_info), dados_device)

if __name__ == "__main__":
    start_udp_listener()
