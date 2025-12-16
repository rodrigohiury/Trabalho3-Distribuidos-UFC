const BASE_URL = ""; // IP fixo ou domínio

export async function getSensorData() {
  const response = await fetch(`${BASE_URL}/devices`);
  return await response.json();
}

export async function sendCommand(actuatorName, command) {
  return fetch(`${BASE_URL}/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ actuatorName, command }),
  });
}
