import pika
import json
import time
import random
import os
import threading

class SendState():
    def __init__(
        self,
        broker_ip="",
        broker_port=0,
        exchange_name="",
        interval_sec=15
    ):
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.exchange_name = exchange_name
        self.interval_sec = interval_sec
        self.ready_event = threading.Event()
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def setParams(self, broker_ip, broker_port, exchange_name):
        with self.lock:
            self.broker_ip = broker_ip
            self.broker_port = broker_port
            self.exchange_name = exchange_name
        
        self.ready_event.set()


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


    def publish_state(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.broker_ip,
                port=self.broker_port,
                credentials=pika.PlainCredentials(
                    username='guest',
                    password='guest'
                    )
                )
        )
        channel = connection.channel()

        """ channel.exchange_declare(
            exchange='tr3-sd-e',
            exchange_type='direct'
        ) """

        while True:
            data_device = carregar_json("dados.json")

            channel.basic_publish(
                exchange=exchange_name,
                routing_key='',
                body=json.dumps(data_device)
            )

            print("Publicado:", data_device)
            time.sleep(15)
    

    def start_sending(self):
        print("Aguardando parâmetros para iniciar o envio...")
        self.ready_event.wait()
        print("Iniciando envio de estado para o broker...")
        self.publish_state()
