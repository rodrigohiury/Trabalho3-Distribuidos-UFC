import { getSensorData } from "./api.js";

async function atualizarLista() {
  const data = await getSensorData();
  renderDevices(data.devices);
}

function renderDevices(devices) {
  const grid = document.getElementById("devices");
  grid.innerHTML = "";

  devices.forEach((d) => {
    const card = document.createElement("div");
    card.classList.add("device-card");
    card.innerHTML = `
            <h3>${d.name}</h3>
            <p>Tipo: ${d.type}</p>
            <p>Valor: ${d.value}</p>
            <p>Status: ${d.status}</p>
        `;
    grid.appendChild(card);
  });
}

atualizarLista();
// setInterval(atualizarLista, 2000);
