const Net = require('net');
const port = 7895;
const server_tcp = new Net.Server();
const fs = require("fs");




function buscarDadosJSON(dados, name_device) {
    return dados.dispositivos.find(p => p.name_device === name_device) || null;
}


function enviarOrdemDevice(port, host, name_device, action, value=null)  {
    const client = new Net.Socket();

    client.connect({ port: port, host: host }, function() {

        let arquivo = fs.readFileSync("dados.json", "utf8");
        
        let json_arq = JSON.parse(arquivo);

        const resultado = buscarDadosJSON(json_arq, name_device);

        // resultado = resultado.dispositivos.find(p => p.name_device === name_device) || null;
        const dados = {
            name_device: resultado.name_device,
            porta: resultado.port_device,
            action: action,
            value: value
        };
            // "ip_device": "localhost",
            // "port_device": 5001,
            // "action": "save_device",
            // "name_device": "Sensor de InfraVermelho",
            // "status_device": "ativo",
            // "type_device": "sensor",
            // "value_device": null

        client.write(JSON.stringify(dados));
    });


    client.on("data", (data) => {
        try {
            const resposta = JSON.parse(data.toString());
            
            console.log("Resposta do servidor:", resposta);
        } catch (err) {
            console.log("Erro ao ler JSON:", err);
        }
    });

    client.on("close", () => {
        console.log("Conexão encerrada");
    });
}


// const resultado = buscarDadosJSON(json_arq, "Sensor de Temperatura");

enviarOrdemDevice(5001, "localhost", "Sensor de InfraVermelho", "set_value", value=123)


