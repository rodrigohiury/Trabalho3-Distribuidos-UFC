const dgram = require('node:dgram');
const client = dgram.createSocket('udp4');

client.send("Olá servidor", 8000, "localhost", () => {
  client.close();
});
