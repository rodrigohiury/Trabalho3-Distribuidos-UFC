const Net = require('net');
var readline = require('readline');
const port = 6789;
const host = 'localhost';

// Sensor de temperatura

const device_conect_gateway = new Net.Socket();

//
device_conect_gateway.connect({ port: port, host: host }, function() {
    var input = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const dados = {
        
        "ip_device": "localhost",
        "port_device": 5001,
        "action": "save_device",
        "name_device": "Sensor de Temperatura",
        "status_device": "ativo",
        "type_device": "sensor",

    
    };
    device_conect_gateway.write(JSON.stringify(dados));
});


device_conect_gateway.on("data", (data) => {
    try {
        const resposta = JSON.parse(data.toString());
        console.log("Resposta do servidor:", resposta);
    } catch (err) {
        console.log("Erro ao ler JSON:", err);
    }
});

device_conect_gateway.on("close", () => {
    console.log("Conexão encerrada");
});


