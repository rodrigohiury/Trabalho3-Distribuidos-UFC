import socket
import json

HOST = "localhost"
PORT = 7890

mensagem = {
    "id_client": "123321",
    "action": "ler",
    "name_device": "Sensor de InfraVermelho",
    "parametros": {
        "status": "ligado"
    }
}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.sendall(json.dumps(mensagem).encode("utf-8"))

resposta = sock.recv(4096)
print("Resposta do gateway:", resposta.decode())

sock.close()
