const Net = require("net");
const fs = require("fs");
const { enviarOrdemDevice } = require("./func_gateway_request_device");

const ARQUIVO_DADOS = "dados.json";
const CLIENTES_VALIDOS = ["123321", "112233", "000077"];

/* ===================== UTIL ===================== */

function carregarDados() {
  return JSON.parse(fs.readFileSync(ARQUIVO_DADOS, "utf8"));
}

function buscarDispositivo(dados, nome) {
  return dados.dispositivos.find(
    d => d.name_device.toLowerCase() === nome.toLowerCase()
  ) || null;
}

/* ===================== PROTO BUILDERS ===================== */

// Cria mensagem Protobuf → Requisicao { operacao }
function criarRequisicaoOperacao(tipoOperacao, parametros = {}) {
  return {
    operacao: {
      operacao: tipoOperacao, // "LER" | "ESCREVER"
      parametros
    }
  };
}

/* ===================== HANDLERS ===================== */

function tratarLeitura(dados, payload) {
  const dispositivo = buscarDispositivo(dados, payload.name_device);

  if (!dispositivo) {
    return { status: "error", message: "Dispositivo não encontrado" };
  }

  const msg = criarRequisicaoOperacao("LER", payload.parametros || {});

  enviarOrdemDevice(
    dispositivo.ip_device,
    dispositivo.port_device,
    msg
  );

  return {
    status: "ok",
    enviado_para: dispositivo.name_device,
    requisicao: msg
  };
}

function tratarEscrita(dados, payload) {
  const dispositivo = buscarDispositivo(dados, payload.name_device);

  if (!dispositivo) {
    return { status: "error", message: "Dispositivo não encontrado" };
  }

  if (dispositivo.type_device !== "atuador") {
    return {
      status: "error",
      message: "Somente atuadores aceitam escrita"
    };
  }

  if (!payload.parametros || Object.keys(payload.parametros).length === 0) {
    return {
      status: "error",
      message: "Parâmetros obrigatórios para escrita"
    };
  }

  const msg = criarRequisicaoOperacao("ESCREVER", payload.parametros);

  enviarOrdemDevice(
    dispositivo.ip_device,
    dispositivo.port_device,
    msg
  );

  return {
    status: "ok",
    enviado_para: dispositivo.name_device,
    requisicao: msg
  };
}

/* ===================== DISPATCH ===================== */

function processarRequisicao(payload) {
  if (!CLIENTES_VALIDOS.includes(payload.id_client)) {
    return { status: "error", message: "Cliente não autorizado" };
  }

  const dados = carregarDados();

  switch (payload.action) {
    case "ler":
      return tratarLeitura(dados, payload);

    case "escrever":
      return tratarEscrita(dados, payload);

    default:
      return {
        status: "error",
        message: "Ação inválida (use ler ou escrever)"
      };
  }
}

/* ===================== TCP SERVER ===================== */

function iniciarServidorTCP_ReceiveClient(port = 7890) {
  const server = new Net.Server();

  server.on("connection", socket => {
    console.log("Cliente conectado:", socket.remoteAddress);

    socket.on("data", buffer => {
      try {
        const payload = JSON.parse(buffer.toString());
        console.log("Requisição recebida:", payload);

        const resposta = processarRequisicao(payload);

        socket.write(JSON.stringify(resposta) + "\n");

      } catch (err) {
        socket.write(JSON.stringify({
          status: "error",
          message: "JSON inválido"
        }) + "\n");
      }
    });

    socket.on("end", () => {
      console.log("Cliente desconectado:", socket.remoteAddress);
    });
  });

  server.listen(port, () => {
    console.log(`Gateway TCP rodando na porta ${port}`);
  });

  return server;
}

module.exports = { iniciarServidorTCP_ReceiveClient };

// старт 🚀
iniciarServidorTCP_ReceiveClient(7890);
