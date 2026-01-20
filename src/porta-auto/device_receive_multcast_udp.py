import socket
import struct
import json
import os
import device_pb2
import device_pb2_grpc
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

def getPayload(mensagem):
    payload = mensagem.SerializeToString()
    return payload

def getProtobuf(payload, classe):
    msg = classe()
    msg.ParseFromString(payload)
    return msg

def getState():
    data = carregar_json("dados.json")
    msg = device_pb2.DeviceResponse()
    msg.state.device_name = data["name_device"]
    msg.state.status = data["status"]
    for k, v in data["parametros"].items():
        msg.state.parameters[k] = v
    return msg


def start_udp_listener(
    whatchdog=None,
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

        msg = getProtobuf(data, device_pb2.Multicast)

        print(
            f"Recebido de {addr[0]}:"
            f"\ngateway=   >{msg.ip_gateway}:{str(msg.port_gateway)}<   \n "
            f"broker=    >{msg.broker_ip}:{msg.broker_port}<     \n"
            f"exchange=    >{msg.exchange_name}<     "
        )

        dados_device = carregar_json("dados.json")
        # print(dados_device["port_device"])
        dados_device["port_device"] = int(dados_device["port_device"])

        msgSend = device_pb2.DeviceResponse()
        msgSend.id.device_name = dados_device["name_device"]
        msgSend.id.device_ip = dados_device["ip_device"]
        msgSend.id.device_port = str(dados_device["port_device"])
        msgSend.id.device_type = dados_device["type_device"]


        ttl = 128

        # Cria socket UDP
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # TTL multicast
        sock2.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_MULTICAST_TTL,
            ttl.to_bytes(1, byteorder="big")
        )

        print("Enviando para o gateway:")
        print(msgSend)
        payload = getPayload(msgSend)
        sock2.settimeout(3.0)
        sock2.sendto(payload, (msg.ip_gateway, int(msg.port_gateway)))
        try:
            data, addr = sock2.recvfrom(1024)
            resposta = getProtobuf(data, device_pb2.CommandResponse)
            print(f"Resposta do gateway: {resposta.message}")
            if "[FIRST_TIME]" in resposta.message:
                print("Enviando estado inicial do dispositivo...")
                state_msg = getState()
                payload_state = getPayload(state_msg)
                sock2.sendto(payload_state, (msg.ip_gateway, int(msg.port_gateway)))
                try:
                    data, addr = sock2.recvfrom(1024)
                    resposta_state = getProtobuf(data, device_pb2.CommandResponse)
                    print(f"Resposta do gateway ao estado inicial: {resposta_state.message}")
                except socket.timeout:
                    print("Timeout esperando resposta do gateway ao estado inicial.")
                except Exception as e:
                    print("Erro ao receber resposta do gateway ao estado inicial:", e)
        except ConnectionResetError as e:
            print("Erro de conexão:", e)       
        except socket.timeout:
            print("Timeout esperando resposta do gateway.")
        except Exception as e:
            print("Erro ao receber resposta do gateway:", e)
        whatchdog.set_gateway(msg.ip_gateway, int(msg.port_gateway))
        sock2.close()
        # enviar_dispositivo(msg.id_gateway_for_save_info, int(msg.port_gateway_for_save_info), dados_device)
    sock.close()

if __name__ == "__main__":
    start_udp_listener()
