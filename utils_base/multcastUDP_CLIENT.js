// Source - https://stackoverflow.com/a
// Posted by dirkk0
// Retrieved 2025-12-05, License - CC BY-SA 4.0


// obs:
// sudo ufw allow from 192.168.1.0/24 to any port 5007 proto udp

// ufw: É o Uncomplicated Firewall, uma interface simples para o iptables.
// allow: Significa permitir tráfego que corresponde à regra. Se fosse deny, bloquearia.
// from 192.168.1.0/24: Especifica de onde o tráfego é permitido.
//     Isso significa:
//         Qualquer IP entre 192.168.1.1 e 192.168.1.254. Que é sua rede Wi-Fi local (classe C /24)
//         Nenhum outro IP fora da sua casa poderá acessar essa porta. É uma sub-rede privada, não pública.
//
// to any: Significa permitir o tráfego para qualquer IP da máquina local.
//         Ou seja, vale para:
//              192.168.1.111 (seu IP Wi-Fi)
//              127.0.0.1 (loopback)
//              Outras interfaces (Docker, VMs), se existirem
//
// port 5007: Porta que será liberada. A regra só afeta tráfego UDP nessa porta.
// proto udp: Força que somente o protocolo UDP seja liberado

var PORT = 5007;
var dgram = require('dgram');
var client = dgram.createSocket({ type: 'udp4', reuseAddr: true })

IP_Gateway = ""
PORT_Gateway = 7895

client.on('listening', function () {
    var address = client.address();
    console.log('UDP Client listening on ' + address.address + ":" + address.port);
    client.setBroadcast(true)
    client.setMulticastTTL(128);
    client.addMembership('224.1.1.1');
});

client.on('message', function (message, remote) {
    console.log('Dados recevidos de um servidor: ' + message + '\n');
    console.log('Messagem: ', message); 
    console.log('Vinda de ' +remote.address + ':' + remote.port + ' - ' + message);
    IP_Gateway = remote.address
    PORT_Gateway = Number(message)
    console.log('C: Gateway set to -> ' + IP_Gateway + ':' + PORT_Gateway);

});

client.bind(PORT);
