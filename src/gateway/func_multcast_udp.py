import socket
import time
import json


def multcast_broadcaster_udp(
    ip_gateway="localhost",
    port_gateway="7895",
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

    print("Broadcaster UDP iniciado")
    print(f"Multicast: {multicast_ip}:{multicast_port}")
    print(f"Intervalo: {interval_sec}s | TTL: {ttl}")

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

            payload = json.dumps(msg).encode("utf-8")

            sock.sendto(payload, (multicast_ip, multicast_port))

            print(
                f"Enviado → gateway={ip_gateway}:{port_gateway} broker={broker_ip}:{broker_port} exchange={exchange_name}"
            )

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\nBroadcaster encerrado")
    finally:
        sock.close()


if __name__ == "__main__":
    multcast_broadcaster_udp()
