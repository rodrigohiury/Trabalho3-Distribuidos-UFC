// Source - https://stackoverflow.com/a
// Posted by dirkk0
// Retrieved 2025-12-05, License - CC BY-SA 4.0

const dgram = require("dgram");

function criarBroadcasterUDP({
  ip_server="localhost",
  tcpPort = "7895",
  multicastIP = "224.1.1.1",
  multicastPort = 5007,
  intervalMs = 3000,
  ttl = 128
} = {}) {

  const server = dgram.createSocket("udp4");

  function broadcastNew() {
    const message = Buffer.from(ip_server+tcpPort);

    server.send(
      message,
      0,
      message.length,
      multicastPort,
      multicastIP,
      (err) => {
        if (err) {
          console.error("Erro ao enviar broadcast:", err);
        } else {
          console.log(
            `Enviando porta TCP ${ip_server+tcpPort} para ${multicastIP}:${multicastPort}`
          );
        }
      }
    );
  }

  server.bind(() => {
    server.setBroadcast(true);        // Habilita broadcast
    server.setMulticastTTL(ttl);      // TTL multicast

    console.log("Servidor UDP pronto para broadcast");
    console.log(`TTL: ${ttl} | Intervalo: ${intervalMs}ms`);

    setInterval(broadcastNew, intervalMs);
  });

  return {
    socket: server,
    stop: () => server.close(),
    broadcastNow: broadcastNew
  };
}

criarBroadcasterUDP({
  tcpPort: "7895"
});

// module.exports = { criarBroadcasterUDP };
