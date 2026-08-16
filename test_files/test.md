![You Don't Need RAG](readme-imgs/title.png)

---

## Why This Exists

### The RAG Problem

Retrieval-Augmented Generation has become the default answer to almost every question involving an LLM and external data. Need to query your docs? RAG. Need to answer questions about a website? RAG. Need to give context to a chatbot? RAG.

The pattern has real merits — but it comes with a long tail of real costs:

- **Chunking is lossy.** Splitting documents into fixed-size chunks destroys context that spans paragraphs. The model only sees fragments, not the full picture.
- **Retrieval is imperfect.** Embedding similarity does not equal semantic relevance. Keyword-heavy or highly technical queries often surface the wrong chunks, and the model confidently answers from them anyway.
- **It's operationally heavy.** You need an embedding model, a vector database, an ingestion pipeline, a retrieval layer, and glue code to hold it all together. Every one of these components can fail or drift silently.
- **Evaluation is hard.** Unlike a traditional search index, a RAG pipeline has no single obvious quality metric. Hallucinations can trace back to any layer — embedding quality, chunking strategy, retrieval parameters, or the model itself.
- **Latency adds up.** Every query now requires an embedding round-trip plus a vector search before the LLM even sees a token.

### The Real Problem: Complexity as a Default

The engineering tendency is to reach for the most sophisticated tool available. RAG pipelines get built for 50-page documentation sets that would fit comfortably in a single context window. Embedding databases get deployed for knowledge bases that could be a well-structured text file. Teams spend weeks tuning chunk sizes and overlap parameters for datasets that a simple paste into Claude would handle in seconds.

The results are often disappointing: the pipeline is slow to build, fragile to maintain, and the retrieval quality never quite matches what you'd get from just giving the model the full document. The complexity was the overhead, not the solution.

Modern LLMs — GPT-4o, Claude 3.5/3.7, Gemini 1.5 Pro — now support context windows of 128K to 1M+ tokens. A 300 KB text file is roughly 75K tokens. For a large fraction of real-world knowledge bases, the entire dataset fits. No chunking. No retrieval. No pipeline. Just paste.

### The Project

**You Don't Need RAG** is a tool for the cases where the simpler path is the right one.

It scrapes a list of URLs, extracts clean readable content, and packages everything into one of two formats:

- **Plain Text** — a single `knowledge_base.txt` file. Paste it directly into ChatGPT, Claude, or any LLM with a large context window. No setup, no infrastructure, no latency.
- **RAG ZIP** — a structured archive with one JSON file per page plus a manifest, ready to feed into an embedding pipeline if you do determine that RAG is the right tool for your scale.

The tool recommends which format to use based on the actual size of the scraped content. If it fits in a context window, it tells you to just paste it.

---

## Features

- Paste a block of text containing URLs — any format, email, markdown, plain list — every URL is extracted automatically
- Upload local files: **PDF, TXT, Markdown, JSON, CSV** (up to 20 MB each)
- Async scraping with a live progress view
- Two output formats with a size-based recommendation
- RAG ZIP includes `manifest.json` (lightweight index) + `pages/<id>.json` (full content per page)
- Clean content extraction: removes nav, footer, scripts, cookie banners, and other noise

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Python packages: `requests`, `beautifulsoup4`, `lxml`, `markdownify`, `pdfplumber`

```bash
pip install requests beautifulsoup4 lxml markdownify pdfplumber
```

### Install & Run

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## How It Works

### Step 1 — Add Sources

Paste any text that contains URLs (a list, an email, a markdown doc — anything). Every URL is extracted automatically. You can also upload local files directly: PDF, TXT, Markdown, JSON, or CSV.

![Add sources](readme-imgs/add%20source.png)

### Step 2 — Review

Remove any sources you don't want before scraping begins. URLs and uploaded files are listed separately.

![Review sources](readme-imgs/review.png)

### Step 3 — Scraping

Scraping runs in the background. A progress bar shows how many sources have been processed.

![Scraping in progress](readme-imgs/scrape.png)

### Step 4 — Download

Once done, choose your format. The recommended option is highlighted based on the actual size of the scraped content.

![Download](readme-imgs/download.png)

---

## Output Formats

### Plain Text (`knowledge_base.txt`)

```
=== Page Title ===
URL: https://example.com
Scraped: 2024-01-01T00:00:00Z

Full page content here...

---

=== Next Page ===
...
```

### RAG ZIP (`knowledge_base.zip`)

```
knowledge_base.zip
├── manifest.json          # Lightweight index: id, url, title, char_count, status
└── pages/
    ├── example-com-abc123.json
    ├── example-com-docs-def456.json
    └── ...
```

Each `pages/*.json` contains the full document: `id`, `url`, `type`, `detected_title`, `content_plain`, `content_markdown`, `char_count`, `scraped_at`, `status`.

---

## When You Actually Do Need RAG

This tool isn't anti-RAG. It's pro-pragmatism. RAG is the right call when:

- Your knowledge base is genuinely large (millions of tokens, not thousands)
- You need sub-second retrieval over a live-updating corpus
- You want to retrieve across many different users' private datasets
- Your queries are specific enough that full-document context would mostly be noise

For everything else — try the plain text file first.

---

## Tech Stack

- **Frontend**: Next.js 15 (App Router), React 19
- **Scraping**: Python (`requests`, `BeautifulSoup`, `markdownify`, `pdfplumber`)
- **Jobs**: File-based async jobs in `data/jobs/<uuid>/`
- **Output**: Plain text concatenation or ZIP with `zipfile`
