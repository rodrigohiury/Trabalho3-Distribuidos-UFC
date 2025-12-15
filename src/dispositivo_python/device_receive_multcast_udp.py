import socket
import struct
import proto_endereco_gateway_pb2 as pb


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
            f"Recebido de {addr[0]} → "
            f"gateway={msg.id_gateway_for_save_info} "
            f"porta={msg.port_gateway_for_save_info}"
        )


if __name__ == "__main__":
    start_udp_listener()
