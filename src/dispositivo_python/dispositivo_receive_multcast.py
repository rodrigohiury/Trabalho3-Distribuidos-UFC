import socket
import struct

from dispositivo_info import enviar_info

IP_Gateway = ""
PORT_Gateway = 7895

def start_udp_client():
    PORT = 5007
    MCAST_GRP = "224.1.1.1"
    
    global IP_Gateway, PORT_Gateway

    # Cria socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Permite reutilizar porta (necessário para multicast)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Liga na porta
    sock.bind(("", PORT))

    # Entra no grupo multicast
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"UDP Client listening on 0.0.0.0:{PORT}")

    while True:
        message, addr = sock.recvfrom(1024)
        message = message.decode("utf-8")

        print("Dados recebidos:", message)
        print(f"Vindo de {addr[0]}:{addr[1]} - {message}")

        IP_Gateway = addr[0]
        PORT_Gateway = int(message)

        enviar_info( IP_Gateway, PORT_Gateway)  # no caso isso iria enviar assim que 
                                               # recebesse o ip e porta do gateway via multcast
        
