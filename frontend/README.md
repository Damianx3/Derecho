# DERECHO Frontend

React/Vite frontend prototype based on the team mockup.

## Run it

```bash
npm install
npm run dev
```

Then open the Vite local URL.

## Backend contract

The UI expects two Python backend endpoints:

### `POST /api/translate`

Request:

```json
{
  "sourceLanguage": "English",
  "targetLanguage": "Spanish",
  "text": "Hello, how are you?"
}
```

Response:

```json
{
  "translation": "Hola, ¿cómo estás?",
  "audioUrl": null,
  "sources": []
}
```

### `POST /api/legal-rights`

Request:

```json
{
  "language": "English",
  "question": "What are my rights if an immigration officer asks questions?"
}
```

Response:

```json
{
  "answer": "Your approved knowledge base response goes here.",
  "sources": [
    {
      "title": "Source title",
      "organization": "Organization",
      "url": "https://example.org/source"
    }
  ]
}
```

## Important architecture note

Keep the legal knowledge base and source retrieval on the Python/backend side.
The React app should display the answer and citations it receives; it should not
invent legal sources or make legal claims itself.

For an offline Raspberry Pi deployment, serve the built React files locally and
have the Python API listen on localhost, for example:

- React/Vite static files -> browser
- Python API -> `127.0.0.1:<port>`
- local speech/translation/legal model -> Python process
- approved local source documents -> backend knowledge base
