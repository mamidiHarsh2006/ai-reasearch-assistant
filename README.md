# ResearchAI

ResearchAI is a full-stack MVP for scientific literature discovery. The React dashboard calls a FastAPI backend that searches OpenAlex and arXiv, and searches IEEE Xplore when a server-side API key is configured. Returned records are normalized, deduplicated, ranked, and limited to five results by default.

## Requirements

- Python 3.10+
- Node.js 18+
- Optional: an IEEE Xplore API key for IEEE search results

## Run the backend

From the project root, in PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `IEEE_API_KEY` in `backend\.env` if you have an IEEE key. `OPENALEX_MAILTO` is optional and can contain a contact email for the OpenAlex polite pool. Keep credentials in the backend environment only.

```powershell
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`, and interactive API documentation is at `http://127.0.0.1:8000/docs`.

To run the backend unit checks from the `backend` directory:

```powershell
python -m unittest discover -s tests
```

## Run the frontend

In a second PowerShell window, from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (by default `http://127.0.0.1:5173`).

## Notes

- IEEE reports an unavailable source when `IEEE_API_KEY` is not set; the other sources continue to be queried.
- Sentence Transformers uses `all-MiniLM-L6-v2` for semantic relevance when installed and its model is available. If model loading is unavailable, the ranking service falls back to query-term matching; the application continues to work.
- The response and results view identify whether semantic embeddings or the keyword fallback supplied the relevance scores.
- The planner provides deterministic keyword and query expansion; it does not call an external generative AI service.
- Research history and saved-paper navigation are clearly marked as unavailable placeholders. No searches are persisted.
- Use `POST /api/research` with `{"query":"...", "limit":5}`. `limit` is configurable from 1 to 25.
