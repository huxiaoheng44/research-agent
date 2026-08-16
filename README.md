## Run with Docker

1. Create `backend/.env` from `backend/.env.example` and set a real
   `OPENAI_API_KEY`.
2. Start the application:

   ```sh
   docker compose up --build
   ```

3. Open `http://localhost:5173`. The API is available at
   `http://localhost:8787`.

Uploaded files are stored in the `research_uploads` Docker volume. The vector index is intentionally in memory, so upload sources again after a backend container restart.

## Run without Docker

In one terminal:

```sh
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8787
```

In another terminal:

```sh
cd frontend
npm install
npm run dev
```

## Architecture

`POST /api/sources` accepts `.txt`, `.md`, and `.html` files. The backend extracts text, chunks it, embeds it with `all-MiniLM-L6-v2`, and stores the vectors in an in-memory store.

`POST /api/research` returns a streaming Markdown response. For each question, `LocalEvidenceJudge` retrieves the five nearest chunks and asks a small model to return the indices that are genuinely useful. Only selected chunks are sent to the main research agent. The main agent has an optional OpenAI `web_search` tool: it should use it when local evidence is missing or insufficient, or when the question needs current external information.

## Example queries

- Upload `test.md`, then ask: `What is You don't need RAG project?`
  - Expected: an answer grounded in the selected uploaded-file chunks followed by a server-generated `Source: test.md` line.
- Ask: `What are the latest developments in RAG evaluation?`
  - Expected: the main agent may invoke web search and return a current, sourced response.

## Evaluation

For this project, I would evaluate the agent with a small set of questions whose answers are known to exist in uploaded documents. For each question, I would check:

- whether the agent selects relevant uploaded-file chunks and answer is supported by those chunks;
- whether the agent avoids unnecessary web search;
- whether it uses web search when the local documents do not contain the necessary information.

This evaluation is important because a model may prefer web search even when the answer is already available in a private uploaded document. To address this, the application uses a local evidence judge. It reviews the top five similarity-search results and selects only the chunks that are useful before they are passed to the main agent. This reduces irrelevant context while preserving useful information from uploaded files also reduces the token costs on the other hand.

## Future improvements

Persist the vector store across backend restarts, add upload queuing for files, and add unit/integration tests in CI, improve retrieval approach
