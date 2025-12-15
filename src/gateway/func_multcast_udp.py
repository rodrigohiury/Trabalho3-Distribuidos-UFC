import socket
import time
import proto_endereco_gateway_pb2 as pb


def multcast_broadcaster_udp(
    ip_gateway="localhost",
    port_gateway="7895",
    multicast_ip="224.1.1.1",
    multicast_port=5007,
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
            msg = pb.EnderecoInfo()
            msg.id_gateway_for_save_info = ip_gateway
            msg.port_gateway_for_save_info = port_gateway

            payload = msg.SerializeToString()

            sock.sendto(payload, (multicast_ip, multicast_port))

            print(
                f"Enviado → gateway={ip_gateway} porta={port_gateway}"
            )

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\nBroadcaster encerrado")
    finally:
        sock.close()


if __name__ == "__main__":
    multcast_broadcaster_udp(
        ip_gateway="localhost do gostosim",
        port_gateway="7895"
    )
