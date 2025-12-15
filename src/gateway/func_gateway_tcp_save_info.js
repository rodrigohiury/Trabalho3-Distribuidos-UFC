const Net = require("net");
const fs = require("fs");

const ESTADOS_VALIDOS = ["ativo", "desligado", "ATIVO", "DESLIGADO"];
const TIPOS_VALIDOS = ["sensor", "atuador"];
const ARQUIVO_DADOS = "dados.json";


// Lê o arquivo JSON
function carregarDispositivos() {
  const arquivo = fs.readFileSync(ARQUIVO_DADOS, "utf8");
  return JSON.parse(arquivo);
}

// Salva no arquivo JSON
function salvarDispositivos(dados) {
  fs.writeFileSync(ARQUIVO_DADOS, JSON.stringify(dados, null, 4));
}

// Envia resposta padronizada
function responder(socket, status, message) {
  socket.write(JSON.stringify({ status, message }) + "\n");
}

// Valida dados do dispositivo
function validarDispositivo(json) {
  if (!json.name_device || !json.status_device || !json.type_device) {
    return "Faltando campos obrigatórios";
  }

  if (!ESTADOS_VALIDOS.includes(json.status_device)) {
    return "Status do dispositivo inválido";
  }

  if (!TIPOS_VALIDOS.includes(json.type_device)) {
    return "Tipo do dispositivo inválido";
  }

  return null; // válido
}

function tratarAcao(socket, json, dados) {
  switch (json.action) {
    case "save_device": {
      const erro = validarDispositivo(json);
      if (erro) {
        responder(socket, "error", erro);
        return;
      }

      const dispositivo = {
        ip_device: socket.remoteAddress,
        port_device: json.port_device,
        name_device: json.name_device,
        status_device: json.status_device,
        type_device: json.type_device
      };

      dados.dispositivos.push(dispositivo);
      salvarDispositivos(dados);

      console.log("Dispositivo salvo:", dispositivo);

      responder(
        socket,
        "ok",
        `Dispositivo salvo com sucesso: ${json.name_device}`
      );
      break;
    }

    default:
      responder(socket, "error", "Ação desconhecida");
  }
}

function iniciarServidorTCPSaveInfo(port = 7895) {
  const server = new Net.Server();

  server.on("connection", (socket) => {
    console.log("Cliente conectado:", socket.remoteAddress);

    let dados = carregarDispositivos();

    socket.on("data", (buffer) => {
      try {
        const json = JSON.parse(buffer.toString());
        console.log("JSON recebido:", json);

        tratarAcao(socket, json, dados);

      } catch (err) {
        responder(socket, "error", "JSON inválido");
      }
    });

    socket.on("end", () => {
      console.log("Cliente desconectado:", socket.remoteAddress);
    });
  });

  server.listen(port, () => {
    console.log(`Servidor TCP rodando na porta ${port}`);
  });

  return server;
}

iniciarServidorTCPSaveInfo(7895);
