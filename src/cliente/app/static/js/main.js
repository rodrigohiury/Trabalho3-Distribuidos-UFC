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

    const title = document.createElement("h3");
    title.textContent = d.name;

    const typeP = document.createElement("p");
    typeP.textContent = `Tipo: ${d.type}`;

    const valueP = document.createElement("p");
    valueP.textContent = `Valor: ${d.value}`;

    const statusP = document.createElement("p");
    statusP.textContent = `Status: ${d.status}`;

    card.appendChild(title);
    card.appendChild(typeP);
    card.appendChild(valueP);
    card.appendChild(statusP);

    // If device is an actuator, add a control button
    if (String(d.type).toLowerCase() === "atuador") {
      const btn = document.createElement("button");
      btn.textContent = "On/Off";
      btn.addEventListener("click", async () => {
        // Simple UI feedback: toggle status text optimistically
        const current = statusP.textContent || "";
        const isOn = /on|ativado|true/i.test(current);
        const newStatus = isOn ? "OFF" : "ON";
        // statusP.textContent = `Status: ${newStatus}`;
        // Try to send command to backend (best-effort)
        try {
          await sendActuatorCommand(d, newStatus);
        } catch (err) {
          console.error("Erro ao enviar comando do atuador:", err);
        }
      });

      card.appendChild(btn);
    }

    grid.appendChild(card);
  });
}

async function sendActuatorCommand(device, status) {
  // Best-effort POST to server; adjust endpoint as your backend expects.
  // If you have an API helper in `api.js`, prefer using it instead.
  const id = device.id ?? device.name;
  const endpoint = `/actuators/${encodeURIComponent(id)}`;
  await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

atualizarLista();
// setInterval(atualizarLista, 2000);
