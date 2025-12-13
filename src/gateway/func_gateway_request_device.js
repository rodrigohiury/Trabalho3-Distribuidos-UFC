const Net = require("net");
const protobuf = require("protobufjs");

let root;
let Requisicao;
let Resposta;

// Carrega .proto uma vez
async function carregarProto() {
  if (!root) {
    root = await protobuf.load("dispositivo.proto");
    Requisicao = root.lookupType("dispositivo.Requisicao");
    Resposta = root.lookupType("dispositivo.Resposta");
  }
}

// =====================================
// ENVIO REAL PROTOBUF
// =====================================
async function enviarOrdemDevice(ip, port, msgProto) {
  await carregarProto();

  return new Promise((resolve, reject) => {
    const client = new Net.Socket();

    client.connect({ host: ip, port }, () => {
      console.log(`📡 Conectado ao dispositivo ${ip}:${port}`);

      const buffer = Requisicao.encode(msgProto).finish();
      client.write(buffer);
    });

    client.on("data", (data) => {
      try {
        const resposta = Resposta.decode(data);
        resolve(resposta);
      } catch (err) {
        reject(err);
      } finally {
        client.end();
      }
    });

    client.on("error", reject);
  });
}

module.exports = { enviarOrdemDevice };
