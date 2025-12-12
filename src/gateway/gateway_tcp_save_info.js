const Net = require('net');
const port = 7895;
const server_tcp = new Net.Server();
const fs = require("fs");
const { json } = require('stream/consumers');

server_tcp.listen(port, () => console.log(`Servidor na porta ${port}`));

// função para receber dados iniciais do dispositivo
server_tcp.on('connection', (socket) => {
    console.log("Cliente conectado");

    // ler dado do arquivo JSON dados.json
    let arquivo = fs.readFileSync("dados.json", "utf8");
    
    // Convertendo para objeto JSON
    let json_arq = JSON.parse(arquivo);
    console.log("Conteúdo do arquivo:", json_arq);
    
    
    name_device = null;
    status_device = null;
    type_device = null;

    const estados = ["ativo", "desligado", "ATIVO", "DESLIGADO"];

    // salvar informações do dispositivo
    socket.on('data', (data) => {
        try {
            const json = JSON.parse(data.toString());
            console.log("JSON recebido:", json);
            console.log("Ação recebida:", json.action);

            switch (json.action) {
                case "save_device":
                    console.log("Salvando nome do dispositivo...");
                    if (!json.name_device || !json.status_device || !json.type_device) {
                        console.log("Faltando campos obrigatórios");
                        socket.write(JSON.stringify({
                            status: "error",
                            message: "Faltando campos obrigatórios"
                        }) + "\n");
                        return
                    }
                    if (!estados.includes(json.status_device)) {
                        console.log("Status do dispositivo inválido");
                        socket.write(JSON.stringify({
                            status: "error",
                            message: "Status do dispositivo inválido"
                        }) + "\n");
                        return
                    }
                    if (!json.type_device === "sensor" || !json.type_device === "atuador") {
                        console.log("Tipo do dispositivo inválido");
                        socket.write(JSON.stringify({
                            status: "error",
                            message: "Tipo do dispositivo inválido"
                        }) + "\n");
                        return
                    }
                    json_received = {
                        ip_device: socket.remoteAddress,
                        port_device: json.port_device,
                        name_device: json.name_device,
                        status_device: json.status_device,
                        type_device: json.type_device
                    };
                    console.log("Dados do dispositivo:", json_received);


                    json_arq.dispositivos.push(json_received);
                    fs.writeFileSync("dados.json", JSON.stringify(json_arq, null, 4));

                    console.log("Dados do dispositivo:", json_received);
                    name_device = json.name_device;
                    socket.write(JSON.stringify({
                        status: "ok",
                        message: `Dispositivo salvo com sucesso registrado: ${json.name}`
                    }) + "\n");
                    break;
                default:
                    socket.write(JSON.stringify({
                        status: "error",
                        message: "Ação desconhecida"
                    }) + "\n");
            }
            
        } catch (e) {
            socket.write(JSON.stringify({
                status: "error",
                message: "JSON inválido"
            }) + "\n");
        }
    });

    socket.on('end', () => console.log("Dispositivo ", json.name_device," desconectado"));
});
