import socket
import time
import json
import device_pb2
import device_pb2_grpc
from device_listener import carregar_dispositivos, salvar_dispositivos


def multcast_broadcaster_udp(
    ip_gateway="localhost",
    port_gateway="58950",
    multicast_ip="224.1.1.1",
    multicast_port=5007,
    broker_ip="localhost",
    broker_port=5672,
    exchange_name="tr3-sd-e",
    interval_sec=3,
    ttl=128
):
    # Cria socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # TTL multicast
    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_MULTICAST_TTL,
        ttl.to_bytes(1, byteorder="big")
    )

    print("---------------------------------------------------------")
    print("[MULTICAST ON] Broadcaster UDP iniciado")
    print(f"Multicast: {multicast_ip}:{multicast_port}")
    print(f"Intervalo: {interval_sec}s | TTL: {ttl}")
    print("---------------------------------------------------------")

    try:
        while True:
            # Cria mensagem protobuf
            msg = {
                "ip_gateway": ip_gateway,
                "port_gateway": int(port_gateway),
                "broker_ip": broker_ip,
                "broker_port": int(broker_port),
                "exchange_name": exchange_name
            }

            msg = device_pb2.Multicast()
            msg.ip_gateway = ip_gateway
            msg.port_gateway = str(port_gateway)
            msg.broker_ip = broker_ip
            msg.broker_port = str(broker_port)
            msg.exchange_name = exchange_name

            payload = getPayload(msg)

            sock.sendto(payload, (multicast_ip, multicast_port))

            print(
                f"[BROADCASTING] Enviado → gateway={ip_gateway}:{port_gateway} broker={broker_ip}:{broker_port} exchange={exchange_name}"
            )

            time.sleep(interval_sec)

            findLazyDevices()

    except KeyboardInterrupt:
        print("\n[MULTICAST OFF] Broadcaster encerrado")
    finally:
        sock.close()

def getPayload(mensagem):
    payload = mensagem.SerializeToString()
    return payload

def getProtobuf(payload, classe):
    msg = classe()
    msg.ParseFromString(payload)
    return msg

def findLazyDevices():
    data = carregar_dispositivos()
    dispositivos = data.get("dispositivos", [])
    alterado = False
    for i, disp in enumerate(dispositivos):
        if time.time() - float(disp["last_update"]) >= 10:
            print(f"[DELETE] Dispositivo {disp['name_device']} está offline. Deletando.")
            dispositivos.pop(i)
            alterado = True
    if alterado:
        data["dispositivos"] = dispositivos
        salvar_dispositivos(data)

if __name__ == "__main__":
    multcast_broadcaster_udp()
