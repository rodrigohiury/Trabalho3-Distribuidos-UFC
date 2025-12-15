import socket
import json

IP_DEVICE = "localhost"
PORT_DEVICE = 5001

def carregar_json(caminho_arquivo):
    """
    Lê um arquivo JSON e retorna os dados carregados como dicionário ou lista.

    :param caminho_arquivo: Caminho do arquivo JSON.
    :return: Dados do JSON (dict ou list).
    """
    import os
    
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

def salvar_json(caminho_arquivo, dados):
    """
    Salva um dicionário Python em um arquivo JSON.

    :param caminho_arquivo: caminho onde o arquivo será salvo (ex: 'dados.json')
    :param dados: dicionário Python a ser salvo
    """
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)
        print(f"Arquivo salvo em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")

def enviar_mensagem(sock, mensagem: str):
    """Envia mensagem JSON codificada em UTF-8."""
    try:
        sock.sendall(mensagem.encode("utf-8"))
    except Exception as e:
        print("Erro ao enviar mensagem:", e)
        raise

def identificar_acao(data):
    # data = json.loads(data.decode("utf-8"))
    print("Dados recebidos do gateway:", data)
 
    action = data["action"]

    data_current = carregar_json("Trabalho_2/Trabalho2-Distribuidos-UFC/src/dispositivo_python/dados.json")
    
    if data["name_device"] == data_current["name_device"]:

        if action == "turn_on":
            status = "ativo"
            data_current["status_device"] = status
            return data_current
        
        elif action == "turn_off":
            status = "inativo"
            data_current["status_device"] = status

            return data_current
        
        elif action == "set_value":
            value = data["value"]
            data_current["value_device"] = value

            return data_current
        
        elif action == "read_value":
            value = data_current["value"]
            return data_current
        
    return None

def receber_resposta(sock):
    """Recebe JSON do servidor."""
    try:
        data = sock.recv(4096)
        resposta_str = data.decode("utf-8").strip()
        resposta_json = json.loads(resposta_str)
        return resposta_json
    except Exception as e:
        print("Erro ao receber resposta:", e)
        raise

def receber_acao():
    servico_device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servico_device.bind((IP_DEVICE, PORT_DEVICE))
    servico_device.listen(1)

    while True:
        print("Aguardando conexão de um cliente...")

        conn, addr = servico_device.accept()

        # Recebe até 1024 bytes enviados pelo cliente
        data = receber_resposta(conn)

        # Se não recebeu nada, encerra a conexão
        if not data: 
            break

        data_current = identificar_acao(data)
        if data_current != None:
            salvar_json("Trabalho_2/Trabalho2-Distribuidos-UFC/src/dispositivo_python/dados.json", data_current)

            data_current = json.dumps(data_current)

            conn.sendall(data_current.encode("utf-8"))
            # enviar_mensagem(servico_device, data_current)
        else:   
            data_current = {
                "response": "name device invalido"
            }
            data_current = json.dumps(data_current)


            conn.sendall(data_current.encode("utf-8")  )

        conn.close()


receber_acao()

