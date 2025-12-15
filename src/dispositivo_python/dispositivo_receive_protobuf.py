import socket
import time
from dispositivo_pb2 import Requisicao, Resposta, RespostaOk, RespostaErro

IP_DEVICE = "localhost"
PORT_DEVICE = 5001


# ===================== LÓGICA DO DISPOSITIVO =====================

ESTADO_ATUAL = {
    "status": "desligado",
    "valor": "0"
}


def executar_operacao(req: Requisicao) -> Resposta:
    resposta = Resposta()

    try:
        operacao = req.operacao.operacao

        # ---------- LER ----------
        if operacao == req.operacao.LER:
            resposta.ok.comando = "LER"
            resposta.ok.dados["status"] = ESTADO_ATUAL["status"]
            resposta.ok.dados["valor"] = ESTADO_ATUAL["valor"]
            resposta.ok.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            return resposta

        # ---------- ESCREVER ----------
        elif operacao == req.operacao.ESCREVER:
            for chave, valor in req.operacao.parametros.items():
                ESTADO_ATUAL[chave] = valor

            resposta.ok.comando = "ESCREVER"
            resposta.ok.dados.update(ESTADO_ATUAL)
            resposta.ok.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            return resposta

        else:
            raise ValueError("Operação desconhecida")

    except Exception as e:
        resposta.erro.comando = "ERRO"
        resposta.erro.mensagem = str(e)
        resposta.erro.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return resposta


# ===================== TCP SERVER =====================

def receber_acoes_protobuf():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((IP_DEVICE, PORT_DEVICE))
    servidor.listen(1)

    print(f"Dispositivo escutando em {IP_DEVICE}:{PORT_DEVICE}")

    while True:
        conn, addr = servidor.accept()
        print("Conexão recebida de:", addr)

        try:
            data = conn.recv(4096)
            if not data:
                conn.close()
                continue

            # ---------- DECODIFICA PROTOBUF ----------
            requisicao = Requisicao()
            requisicao.ParseFromString(data)

            print("Requisição recebida (PROTOBUF):")
            print(requisicao)

            # ---------- EXECUTA ----------
            resposta = executar_operacao(requisicao)

            # ---------- ENVIA ----------
            conn.sendall(resposta.SerializeToString())

        except Exception as e:
            print("Erro:", e)

        finally:
            conn.close()


if __name__ == "__main__":
    receber_acoes_protobuf()
    
