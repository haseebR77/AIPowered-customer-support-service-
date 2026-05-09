const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const REQUEST_TIMEOUT_MS = 25000;

async function fetchWithTimeout(url, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

async function parseApiError(response, fallbackMessage) {
  try {
    const data = await response.json();
    if (typeof data?.detail === "string") return data.detail;
    if (typeof data?.message === "string") return data.message;
  } catch {
    // Ignore parsing error and return fallback.
  }
  return fallbackMessage;
}

export async function askQuestion(query) {
  const response = await fetchWithTimeout(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const message = await parseApiError(response, "Failed to fetch chatbot response.");
    throw new Error(message);
  }

  return response.json();
}

export async function getLogs() {
  const response = await fetchWithTimeout(`${API_BASE_URL}/logs`);
  if (!response.ok) {
    const message = await parseApiError(response, "Failed to fetch logs.");
    throw new Error(message);
  }
  return response.json();
}

export async function escalateQuery(query, reason) {
  const response = await fetchWithTimeout(`${API_BASE_URL}/escalate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, reason }),
  });

  if (!response.ok) {
    const message = await parseApiError(response, "Failed to escalate query.");
    throw new Error(message);
  }

  return response.json();
}
