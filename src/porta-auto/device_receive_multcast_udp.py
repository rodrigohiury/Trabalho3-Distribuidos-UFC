import socket
import struct
import json
import os
# import proto_endereco_gateway_pb2 as pb
# from device_request_info_tcp import enviar_dispositivo


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

        msg = json.loads(data)

        print(
            f"Recebido de {addr[0]}:"
            f"\ngateway=   >{msg["ip_gateway"]}:{msg["port_gateway"]}<   \n "
            f"broker=    >{msg["broker_ip"]}:{msg["broker_port"]}<     \n"
            f"exchange=    >{msg["exchange_name"]}<     "
        )

        dados_device = carregar_json("dados.json")
        # print(dados_device["port_device"])
        dados_device["port_device"] = int(dados_device["port_device"])

        msgSend = {
            "name_device": dados_device["name_device"],
            "ip_device": dados_device["ip_device"],
            "port_device": dados_device["port_device"],
            "type_device": dados_device["type_device"]
        }

        ttl = 128

        # Cria socket UDP
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # TTL multicast
        sock2.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_MULTICAST_TTL,
            ttl.to_bytes(1, byteorder="big")
        )

        payload = json.dumps(msgSend).encode("utf-8")
        print("Enviando para o gateway:")
        print(msgSend)
        sock2.sendto(payload, (msg["ip_gateway"], msg["port_gateway"]))
        sock2.close()
        # enviar_dispositivo(msg.id_gateway_for_save_info, int(msg.port_gateway_for_save_info), dados_device)

if __name__ == "__main__":
    start_udp_listener()
