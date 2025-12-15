const net = require("net");
const protobuf = require("protobufjs");

const HOST = "localhost";
const PORT = 5001;
// const client = new net.Socket();

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



function enviarProtobuf({ host, port, mensagem, TipoMensagem, TipoResposta }) {

    const client = new net.Socket();

    let buffer = Buffer.alloc(0);
    let messageLength = null;

    client.connect(port, host, () => {
      console.log("Conectado ao servidor");
      // const payload = mensagem;
      // const header = Buffer.alloc(4);
      // header.writeUInt32BE(payload.length, 0);

      // client.write(Buffer.concat([header, payload]));


      const sizeBuffer = Buffer.alloc(4);
      sizeBuffer.writeUInt32BE(mensagem.length);

      client.write(sizeBuffer);
      client.write(buffer);
    });

    client.on("data", (data) => {
      console.log("Resposta bruta:", data);

      // (opcional) decodificar Resposta
      const Resposta = root.lookupType("dispositivo.Resposta");
      const resposta = Resposta.decode(data);
      console.log("Resposta decodificada:", resposta);

      client.destroy();
    });

    client.on("error", console.error);
  
}


module.exports = {
 enviarProtobuf 
};
