import { getSensorData, sendCommand } from "./api.js";

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

    const title = document.createElement("h3");
    title.textContent = d.name;

    const typeP = document.createElement("p");
    typeP.textContent = `Tipo: ${d.type}`;

    const valueP = document.createElement("p");
    valueP.textContent = `Valor: ${d.value}`;

    const statusP = document.createElement("p");
    statusP.textContent = `Status: ${d.status}`;

    card.appendChild(title);
    // card.appendChild(typeP);
    // card.appendChild(valueP);
    card.appendChild(statusP);

    // If device is an actuator, add a control button
    const btn = document.createElement("button");
    if (String(d.status).toLowerCase() === "ativo"){
      btn.textContent = "Desligar";
      btn.classList.add("toggle-button-off");
    }else{
      btn.textContent = "Ligar";
      btn.classList.add("toggle-button-on");
    }
    btn.addEventListener("click", async () => {
      // Simple UI feedback: toggle status text optimistically
      const current = statusP.textContent || "";
      const isOn = /on|ativo|true/i.test(current);
      const newStatus = isOn ? "desligado" : "ativo";
      const command = { "status": newStatus };
      // statusP.textContent = `Status: ${newStatus}`;
      // Try to send command to backend (best-effort)
      try {
        console.warn("Enviando comando para", d.name, command);
        await sendCommand(d.name, command);
      } catch (err) {
        console.error("Erro ao enviar comando do atuador:", err);
      }
    });

    card.appendChild(btn);
    if (String(d.type).toLowerCase() === "atuador") {
    }

    grid.appendChild(card);
  });
}

async function sendActuatorCommand(device, com) {
  print("Enviando comando para", device.name, com);
  await sendCommand(device.name, com);
}

atualizarLista();
setInterval(atualizarLista, 2000);
