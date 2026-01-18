import pika
import json

def carregar_json():
    with open("dados.json", "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dispositivos(dados):
    with open("dados,json", "w", encoding="utf8") as f:
        json.dump(dados, f, indent=4)


def atualizar_sensor(ch, method, properties, body):
    print("Recebido:", body)
    data = json.loads(body)
    dados_gateway = carregar_json()
    devices = dados_gateway.get("dispositivos", [])
    atualizado = False
    for i, device in enumerate(devices):
        if device["name_device"] == data.get("name_device"):
            devices[i].update(data)
            atualizado = True
            break
    if not atualizado:
        devices.append(data)
    dados_gateway["dispositivos"] = devices
    salvar_dispositivos(dados_gateway)
        


def consume_data(broker_ip, broker_port, queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=broker_ip,
            port=broker_port,
            credentials=pika.PlainCredentials(
                username='guest',
                password='guest'
                )
            )
    )
    channel = connection.channel()

    channel.queue_bind(
        queue=queue_name,
        routing_key=''
    )


    channel.basic_consume(
        queue=queue_name,
        on_message_callback=atualizar_sensor,
        auto_ack=True
    )

    print("Gateway aguardando dados...")
    channel.start_consuming()
