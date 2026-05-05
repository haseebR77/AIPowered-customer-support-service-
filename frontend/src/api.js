const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function askQuestion(query) {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch chatbot response.");
  }

  return response.json();
}

export async function getLogs() {
  const response = await fetch(`${API_BASE_URL}/logs`);
  if (!response.ok) {
    throw new Error("Failed to fetch logs.");
  }
  return response.json();
}

export async function escalateQuery(query, reason) {
  const response = await fetch(`${API_BASE_URL}/escalate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, reason }),
  });

  if (!response.ok) {
    throw new Error("Failed to escalate query.");
  }

  return response.json();
}
