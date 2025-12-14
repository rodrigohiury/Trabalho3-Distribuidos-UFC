const BASE_URL = "http://127.0.0.1:8000"; // IP fixo ou domínio

export async function getSensorData() {
  const response = await fetch(`${BASE_URL}/devices`);
  return await response.json();
}

export async function sendCommand(actuatorId, command) {
  return fetch(`${BASE_URL}/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actuatorId, command }),
  });
}
