import json
import time
import random


def simular_temp_sensor():
    ARQUIVO_JSON = "dados.json"
    INTERVALO = 2          # segundos
    DESVIO = 0.2           # intensidade do ruído (±)
    LIMITE_MIN = 15.0
    LIMITE_MAX = 40.0

    try:
        # Lê o JSON
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        temp = 25
        status = data["status"].lower()

        # Arredonda para simular sensor real
        data["parametros"][0]["temperatura"] = f"{temp:.2f}"

        # Grava o JSON
        with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Erro no sensor de temperatura:", e)
        time.sleep(INTERVALO)

    while True:
        try:
            # Lê o JSON
            with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            temp_atual = data["parametros"][0]["temperatura"]
            status = data["status"].lower()
            if status == "ativo":

                # Gera ruído com média zero
                ruido = random.gauss(0, DESVIO)

                nova_temp = float(temp_atual) + ruido

                # Evita valores absurdos
                nova_temp = max(LIMITE_MIN, min(LIMITE_MAX, nova_temp))

                # Arredonda para simular sensor real
                data["parametros"][0]["temperatura"] = f"{nova_temp:.2f}"

                # Grava o JSON
                with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                time.sleep(INTERVALO)

        except Exception as e:
            print("Erro no sensor de temperatura:", e)
            time.sleep(INTERVALO)
