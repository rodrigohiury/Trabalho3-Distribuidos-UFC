const Net = require('net');
const port = 7890;
const server_tcp = new Net.Server();
const fs = require("fs");
const { json } = require('stream/consumers');

function buscarInfoDispositivo(data_json,nome){
    // Procura o item na lista
    const dispositivo = data_json.dispositivos.find(
        item => item.name_device === nome
    );

    return dispositivo || null;
}


function lerDados(data_json){
    const matriculas = ["123321", "112233", "000077"]
    
    // const json = JSON.parse(data.toString());
    console.log("JSON recebido:", json);
    console.log("Ação recebida:", json.action);
    
    if (matriculas.includes(data_json.id_client)){
        if (data_json.name_device == null) {
            console.log("erro com nome do dispositivo")
            return
        }
        else if(buscarInfoDispositivo(data_json,nome) == null){
            console.log("nome do disṕsitivo não consta na lista")
            return
        }

        switch (data_json.action_client){
            case "lista":
                console.log("Função Listar dispositivos")
                return listarDispositivos()
                // chamar função listagem
                // retorno de função

            case "ler":
                console.log("Função Ler sensor ou status atuador")
                return lerDispositivo(data_json.name_device)
                // chamar função de leitura
                // retorno de função


            case "escrever":
                console.log("Função Escrever em atuador")

                return escreverDispositivo(deviceName, actionData)
                // chamar função de escrita
                // retorno de função
        }

    }else{
        console.log("Erro")
    }

}

function listarDispositivos() {
    try {
        // Lê o arquivo dados.json
        const conteudo = fs.readFileSync("dados.json", "utf8");

        // Converte para objeto
        const json = JSON.parse(conteudo);

        // Verifica se existe a chave dispositivos
        if (!Array.isArray(json.dispositivos)) {
            console.log("Nenhum dispositivo encontrado.");
            return json; // retorna mesmo assim
        }

        console.log("Lista de dispositivos:\n");

        // Lista cada dispositivo
        json.dispositivos.forEach((d, index) => {
            console.log(`Dispositivo ${index + 1}:`);
            console.log(`  Porta:    ${d.port_device}`);
            console.log(`  Nome:     ${d.name_device}`);
            console.log(`  Status:   ${d.status_device}`);
            console.log(`  Valor atual:     ${d.type_device}`);
            console.log("-----------------------------------");
        });

        // Retorna o JSON completo
        return json;

    } catch (erro) {
        console.error("Erro ao ler dados.json:", erro.message);
        return null;
    }
}

function escreverDispositivo(deviceName, actionData) {
    try {
        // Lê JSON
        const conteudo = fs.readFileSync("dados.json", "utf8");
        const json = JSON.parse(conteudo);

        const dispositivos = json.dispositivos;
        if (!Array.isArray(dispositivos)) {
            console.log("Lista de dispositivos inválida.");
            return null;
        }

        // Busca pelo nome
        const dispositivo = dispositivos.find(d =>
            d.name_device.toLowerCase() === deviceName.toLowerCase()
        );

        if (!dispositivo) {
            console.log(`Dispositivo '${deviceName}' não encontrado.`);
            return null;
        }

        console.log("\nDispositivo encontrado:", dispositivo);

        if (dispositivo.type_device === "sensor") {
            console.log("\n Tipo: Sensor");

            // Aqui você coloca a lógica do sensor (ex: leitura)
            console.log(`→ Sensor '${deviceName}' está realizando leitura...`);
            return { status: "ok", message: "Leitura realizada no sensor." };
        }

        if (dispositivo.type_device === "atuador") {
            console.log("\nTipo: Atuador");

            const { action, value_device } = actionData;

            switch (action) {
                case "turn_on":
                    console.log(`→ Atuador '${deviceName}' ligado.`);
                    break;

                case "turn_off":
                    console.log(`→ Atuador '${deviceName}' desligado.`);
                    break;

                case "set_value":
                    // Verifica se o valor existe
                    if (value_device === null || value_device === undefined) {
                        console.log("ERRO: 'value_device' não pode ser nulo em 'set_value'.");
                        return { status: "error", message: "value_device é obrigatório." };
                    }

                    console.log(`→ Atuador '${deviceName}' definido para valor: ${value_device}`);
                    break;

                case "read_value":
                    console.log(`→ Lendo valor atual do atuador '${deviceName}'...`);
                    break;

                default:
                    console.log(`Ação '${action}' desconhecida.`);
                    return { status: "error", message: "Ação inválida." };
            }

            return { status: "ok", message: `Ação '${action}' executada com sucesso.` };
        }

        
        // Se o type não for reconhecido
        console.log(`Tipo de dispositivo '${dispositivo.type_device}' não é reconhecido.`);
        return { status: "error", message: "Tipo inválido." };

    } catch (erro) {
        console.error("Erro ao processar ação:", erro.message);
        return null;
    }
}

function lerDispositivo(nome) {
    try {
        // Lê o arquivo dados.json
        const conteudo = fs.readFileSync("dados.json", "utf8");

        // Converte para objeto
        const json = JSON.parse(conteudo);

        const dispositivos = json.dispositivos;

        if (!Array.isArray(dispositivos)) {
            console.log("Arquivo não contém lista de dispositivos.");
            return null;
        }

        // Procura pelo nome exato (case insensitive)
        const dispositivo = dispositivos.find(d =>
            d.name_device.toLowerCase() === nome.toLowerCase()
        );

        if (!dispositivo) {
            console.log(`Dispositivo '${nome}' não encontrado.`);
            return null;
        }

        console.log("Dispositivo encontrado:");
        console.log(dispositivo);

        return dispositivo;

    } catch (erro) {
        console.error("Erro ao ler dados.json:", erro.message);
        return null;
    }
}



server_tcp.listen(port, () => console.log(`Servidor na porta ${port}`));

// função para receber dados iniciais do dispositivo
server_tcp.on('connection', (socket) => {
    console.log("Cliente conectado");

    let arquivo = fs.readFileSync("dados.json", "utf8");
    // 2. Converte de texto → JSON
    let json_arq = JSON.parse(arquivo);
    console.log("Conteúdo do arquivo:", json_arq);
    
    
    name_device = null;
    status_device = null;
    type_device = null;


    const estados = ["ativo", "desligado", "ATIVO", "DESLIGADO"];
    // function enviarOrdemDevice(port, host, name_device, action, value=null)
    

    // salvar informações do dispositivo  
    socket.on('data', (data) => {
        try {
            const json = JSON.parse(data.toString());

            lerDados(data_json)
            console.log("JSON recebido:", json);
            console.log("Ação recebida:", json.action);
            socket.write()

            
            
        } catch (e) {
            socket.write(JSON.stringify({
                status: "error",
                message: "JSON inválido"
            }) + "\n");
        }
    });

    socket.on('end', () => console.log("Dispositivo ", json.name_device," desconectado"));
});
