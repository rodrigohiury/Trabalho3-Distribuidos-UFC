import pika
import json
import threading
import device_pb2
import device_pb2_grpc


class ConsumeData():
    def __init__(self, broker_ip="", broker_port=0, queue_name=""):
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.queue_name = queue_name
    
    def carregar_json(self):
        with open("dados.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def salvar_dispositivos(self, dados):
        with open("dados.json", "w", encoding="utf8") as f:
            json.dump(dados, f, indent=4)

    def getProtobuf(self, payload, classe):
        msg = classe()
        msg.ParseFromString(payload)
        return msg

    def atualizar_sensor(self, ch, method, properties, body):
        print("Recebido:", body)
        data = self.getProtobuf(body, device_pb2.DeviceState)
        dados_gateway = self.carregar_json()
        devices = dados_gateway.get("dispositivos", [])
        atualizado = False
        for i, device in enumerate(devices):
            if device["name_device"] == data.device_name:
                device["status"] = data.status
                if "parametros" not in device:
                    device["parametros"] = {}
                for k, v in data.parameters.items():
                    device["parametros"][k] = v
                atualizado = True
                break
        if atualizado:
            devices[i] = device
            print(f"[RABBITMQ] Sensor {data.device_name} atualizado.")
            dados_gateway["dispositivos"] = devices
            self.salvar_dispositivos(dados_gateway)
            


    def consume_data(self):
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

     #   channel.queue_bind(
     #       queue=self.queue_name,
     #       routing_key=''
     #   )


        channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.atualizar_sensor,
            auto_ack=True
        )

        print("Gateway aguardando dados...")
        channel.start_consuming()
