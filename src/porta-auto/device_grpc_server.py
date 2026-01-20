import device_pb2
import device_pb2_grpc
import json

class DeviceServiceServicer(device_pb2_grpc.DeviceServiceServicer):

    def __init__(self):
        # Estado interno do dispositivo
        self.estado = {
            "status": "",
            "parametros": {}
        }

    def carregar_json(self):
        with open("dados.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    def salvar_json(self, dados):
        with open("dados.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def refreshState(self):
        data = self.carregar_json()
        self.estado["status"] = data["status"]
        for k, v in data["parametros"].items():
            self.estado["parametros"][k] = v
    
    def saveState(self):
        data = self.carregar_json()
        data["status"] = self.estado["status"]
        for k, v in self.estado["parametros"].items():
            data["parametros"][k] = v
        self.salvar_json(data)

    def SetState(self, request, context):
        """
        request é um DeviceState enviado pelo Gateway
        """

        print(f"[gRPC] SetState recebido: {request}")

        try:
            # Atualiza estado interno do dispositivo
            self.estado["status"] = request.status
            for k, v in request.parameters.items():
                self.estado["parametros"][k] = v
            
            self.saveState()

            response = device_pb2.CommandResponse()
            response.response = "ok"
            response.message = "Estado aplicado com sucesso"
            response.status = self.estado["status"]
            for k, v in self.estado["parametros"].items():
                response.parameters[k] = v
            return response

        except Exception as e:
            response = device_pb2.CommandResponse()
            response.response = "error"
            response.message = str(e)
            response.status = self.estado["status"]
            for k, v in self.estado["parametros"].items():
                response.parameters[k] = v
            return response
        
        def getStateMessage(self):
            device = self.carregar_json()
            msg = device_pb2.DeviceState()
            msg.device_name = device["name_device"]
            msg.status = device["status"]
            for k, v in device["parametros"].items():
                msg.parameters[k] = v
            return msg