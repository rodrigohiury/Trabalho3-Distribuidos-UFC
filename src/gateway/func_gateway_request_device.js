const net = require("net");
const protobuf = require("protobufjs");

const HOST = "localhost";
const PORT = 5001;
const client = new net.Socket();

async function loadProto() {
  const root = await protobuf.load("dispositivo.proto");
  return {
    Requisicao: root.lookupType("dispositivo.Requisicao"),
    Resposta: root.lookupType("dispositivo.Resposta"),
    ComandoOperacao: root.lookupEnum("dispositivo.ComandoOperacao.TipoOperacao")
  };
}

function enviar(socket, message, Type) {
  const buffer = Type.encode(message).finish();
  const header = Buffer.alloc(4);
  header.writeUInt32BE(buffer.length, 0);

  socket.write(Buffer.concat([header, buffer]));
}

function receber(socket, Type) {
  return new Promise((resolve) => {
    let buffer = Buffer.alloc(0);
    let messageLength = null;

    socket.on("data", (data) => {
      buffer = Buffer.concat([buffer, data]);

      // lê header
      if (messageLength === null && buffer.length >= 4) {
        messageLength = buffer.readUInt32BE(0);
        buffer = buffer.slice(4);
      }

      // lê payload
      if (messageLength !== null && buffer.length >= messageLength) {
        const payload = buffer.slice(0, messageLength);
        const message = Type.decode(payload);
        resolve(message);
      }
    });
  });
}


// MAIN
async function main() {
  const { Requisicao, Resposta, ComandoOperacao } = await loadProto();

  client.connect({ host: HOST, port: PORT }, () => {
    console.log("Conectado ao dispositivo");

    // monta requisição LER
    const message = Requisicao.create({
      name_client: "cliente_javascript",
      name_device: "Sensor de InfraVermelho",
      ler: {
        operacao: {
          operacao: ComandoOperacao.values.LER
        }
      }
    });

    const buffer = Requisicao.encode(message).finish();
    const header = Buffer.alloc(4);
    header.writeUInt32BE(buffer.length, 0);

    client.write(Buffer.concat([header, buffer]));
    // enviar(client, req, Requisicao);
    // client.write(JSON.stringify(dados));


    // function enviar(socket, message, Type) {
    //   const buffer = Type.encode(message).finish();
    //   const header = Buffer.alloc(4);
    //   header.writeUInt32BE(buffer.length, 0);

    //   socket.write(Buffer.concat([header, buffer]));
    // }
  });

  const resposta = await receber(client, Resposta);

  console.log("Resposta recebida:");
  console.log(resposta);

  client.end();
}

main();
