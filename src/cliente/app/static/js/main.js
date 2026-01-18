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

    // Adiciona parâmetros se existirem
    if (d.parametros && Object.keys(d.parametros).length > 0) {
      const parametrosDiv = document.createElement("div");
      parametrosDiv.classList.add("parametros");
      const parametrosList = document.createElement("ul");

      if (!String(d.name).toLowerCase().includes("luz")) {
        if (String(d.name).toLowerCase().includes("temperatura")) {
          const paramP = document.createElement("p");
          paramP.textContent = `Temperatura: ${d.parametros.temperatura} °C`;
          parametrosList.appendChild(paramP);
        }else {
          Object.entries(d.parametros).forEach(([key, value]) => {
            const paramP = document.createElement("p");
            paramP.textContent = `${key}: ${value}`;
            parametrosList.appendChild(paramP);
          });
        }

        parametrosDiv.appendChild(parametrosList);
        card.appendChild(parametrosDiv);
      }
    }

    // If device is an actuator, add a control button
    const btn = document.createElement("button");
    if (String(d.status).toLowerCase() === "ativo") {
      btn.textContent = "Desativar";
      btn.classList.add("toggle-button-off");
    } else {
      btn.textContent = "Ativar";
      btn.classList.add("toggle-button-on");
    }
    btn.addEventListener("click", async () => {
      // Simple UI feedback: toggle status text optimistically
      const current = statusP.textContent || "";
      const isOn = /on|ativo|true/i.test(current);
      const newStatus = isOn ? "desativado" : "ativo";
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
    if (String(d.name).toLowerCase().includes("porta")) {
      const btn2 = document.createElement("button");
      btn2.textContent = "Abrir";
      btn2.classList.add("open-button");
      btn2.addEventListener("click", async () => {
        if( String(d.status).toLowerCase() !== "ativo"){
          alert("Ative o atuador antes de abrir a porta!");
          return;
        }
        // Simple UI feedback: toggle status text optimistically
        const currentDoor = d.parametros?.aberto;
        console.log("Current door status:", currentDoor);
        const newParam = (currentDoor === "nao") ? "sim" : "nao";
        if (newParam === "sim") {
          const command = { "parametros": {"aberto": newParam} };
          // statusP.textContent = `Status: ${newStatus}`;
          // Try to send command to backend (best-effort)
          try {
            console.warn("Enviando comando para", d.name, command);
            await sendCommand(d.name, command);
          } catch (err) {
            console.error("Erro ao enviar comando do atuador:", err);
          }
        }else{
          alert("Porta já está aberta!");
        }
      });
      card.appendChild(btn2);
    }

    
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
