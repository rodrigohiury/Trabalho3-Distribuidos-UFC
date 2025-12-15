// Source - https://stackoverflow.com/a
// Posted by dirkk0
// Retrieved 2025-12-05, License - CC BY-SA 4.0

const const_port_for_tcp = "7895"

var dgram = require('dgram');
var server = dgram.createSocket("udp4");
server.bind(function () {
    server.setBroadcast(true) // Isso habilita o socket para enviar pacotes broadcast.
    
    server.setMulticastTTL(128); // Define o Time-To-Live (TTL) para pacotes multicast. 
                                 // O pacote pode viajar por até 128 roteadores

    setInterval(broadcastNew, 3000); // Isso faz com que a função broadcastNew seja chamada a cada 3 segundos.
});

function broadcastNew() {
    var message = new Buffer.from(const_port_for_tcp);
    server.send(message, 0, message.length, 5007, "224.1.1.1");
    console.log("Enviando porta " + message + " para dispositivos na rede enviarem info...");
}


// module.exports = { startTCPServer };
