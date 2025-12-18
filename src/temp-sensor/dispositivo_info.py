import socket
import json

"""
    Esse módulo é responsável por enviar as informações do dispositivo para o gateway.
    Após receber dados de Multcast UDP
"""

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

def enviar_mensagem(sock, mensagem: str):
    """Envia mensagem JSON codificada em UTF-8."""
    try:
        sock.sendall(mensagem.encode("utf-8"))
    except Exception as e:
        print("Erro ao enviar mensagem:", e)
        raise

def receber_resposta(sock):
    """Recebe JSON do servidor."""
    try:
        data = sock.recv(2048)
        resposta_str = data.decode("utf-8").strip()
        resposta_json = json.loads(resposta_str)
        return resposta_json
    except Exception as e:
        print("Erro ao receber resposta:", e)
        raise

def enviar_info( ip: str, port: int,):
    servico_device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servico_device.connect(("localhost", 7895))

    data = carregar_json("Trabalho_2/Trabalho2-Distribuidos-UFC/src/dispositivo_python/dados.json")

    # // DADOS DE LEITURA
    # message ReadDevice {
    #   string name_device = 1;
    #   string ip_device = 2;
    #   uint32 port_device = 3;
    #   string status = 4;
    #   string type_device = 5;
    #   map<string, string> parametros = 6;
    # }


    data = json.dumps(data)
    enviar_mensagem(servico_device, data)
    receber_resposta(servico_device)

enviar_info( "localhost", 7895)