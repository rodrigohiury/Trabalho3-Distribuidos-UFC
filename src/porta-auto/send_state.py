import socket
import json


def carregar_json(caminho_arquivo):
    """
    Lê um arquivo JSON e retorna os dados carregados como dicionário ou lista.

    :param caminho_arquivo: Caminho do arquivo JSON.
    :return: Dados do JSON (dict ou list).
    """
    
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

def enviar_estado_atual():
    dados_device = carregar_json("dados.json")
    msg = {
        "name_device": dados_device["name_device"],
        "status": dados_device["status"],
        "parametros": dados_device["parametros"]
    }
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_servidor, porta_servidor))
        sock.sendall(json.dumps(msg).encode("utf-8"))
        sock.close()
    except Exception as e:
        print(f"Erro ao enviar estado atual: {str(e)}")
