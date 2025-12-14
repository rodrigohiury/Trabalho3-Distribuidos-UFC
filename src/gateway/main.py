from func.func_gateway_receive_client import socket_receiv_client_request_device
from func.func_multcast_udp import criar_multcast_broadcaster_udp
    
# def enviar_requisicao_tcp(
#     ip: str,
#     porta: int,
#     name_client: str,
#     name_device: str,
#     operacao: str,
#     status: str = None,
#     type_device: str = None,
#     parametros: dict = None,
#     timeout: int = 5
# )
if __name__ == "__main__":
    criar_multcast_broadcaster_udp(
        ip_gateway="localhost",
        port_gateway="7895"
    )


    socket_receiv_client_request_device()
