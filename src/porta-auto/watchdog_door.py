import json
import time


def watchdog_door():
    ARQUIVO_JSON = "dados.json"   # nome do seu arquivo
    INTERVALO = 2                 # tempo entre verificações (segundos)

    while True:
        try:
            # 1. Ler o JSON
            with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 2. Verificar o estado
            estado = data["parametros"][0]["aberto"]

            if estado.lower() == "sim":
                print("Porta aberta detectada. Aguardando 10 segundos...")
                time.sleep(10)

                # 3. Atualizar para "nao"
                data["parametros"][0]["aberto"] = "nao"

                # 4. Gravar novamente no arquivo
                with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                print("Porta fechada automaticamente.")

            # Aguarda antes de verificar novamente
            time.sleep(INTERVALO)

        except Exception as e:
            print("Erro ao monitorar o arquivo:", e)
            time.sleep(INTERVALO)
