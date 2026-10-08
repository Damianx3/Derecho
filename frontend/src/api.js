/*
  Frontend/backend boundary.

  Replace these endpoints with your Python backend when it is ready.

  Expected:
    POST /api/translate
      body: {
        sourceLanguage: "English",
        targetLanguage: "Spanish",
        text: "..."
      }
      response: {
        translation: "...",
        audioUrl?: "...",
        sources?: [{ title, url, organization }]
      }

    POST /api/legal-rights
      body: {
        language: "English",
        question: "..."
      }
      response: {
        answer: "...",
        sources: [{ title, url, organization }]
      }
*/

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function post(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

export function translateText(payload) {
  return post("/api/translate", payload);
}

export function askLegalRights(payload) {
  return post("/api/legal-rights", payload);
}
