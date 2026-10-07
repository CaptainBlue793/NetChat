---
title: NetChat
emoji: 🐦
colorFrom: pink
colorTo: blue
sdk: streamlit
sdk_version: 1.65.0
python_version: 3.11
app_file: app.py
pinned: false
license: mit
short_description: Chat with Website using RAG
---

# NetChat

Load a public HTML webpage and ask questions grounded in its content. Answers include numbered source passages, and follow-up questions retain conversation history.

## Run locally (PowerShell)

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m streamlit run app.py
```

Enter your Hugging Face token in the sidebar, or configure `HF_TOKEN` in an untracked `.env` file using `.env.example`. The token needs Inference Providers permission. `HF_MODEL` optionally overrides the default `meta-llama/Llama-3.1-8B-Instruct`. A supported provider and available account quota are required; model availability can change.

On Hugging Face Spaces, configure `HF_TOKEN` as a Space secret, not a repository file. Native Streamlit Spaces are legacy deployments; new Spaces may require Docker. This checkout preserves the existing Space metadata.

## How it works

The loader extracts readable text, splits it into overlapping passages, and ranks passages using TF-IDF. The most relevant passages and recent conversation are sent to Hugging Face's `InferenceClient.chat_completion`. This replaces the original deprecated LangChain inference wrapper and local embedding/Chroma stack. Retrieval is lexical: paraphrases may match less well than semantic embeddings.

Loading a new page resets conversation history. Failed loads retain the previous page and show its active URL. Model failures leave the conversation unchanged so the question can be retried.

## Scope and limitations

- Single-page HTML only; no whole-site crawling, PDFs, login pages, or JavaScript rendering.
- Read timeout, redirect limit, public-host validation, and a 2 MB page limit.
- No persistence across browser sessions.
- Model answers and citations need review; grounding prompts do not guarantee accuracy.
- Public-host DNS validation is basic defense, not a hardened network boundary for hostile multi-user deployments.

## Verify

```powershell
.venv/Scripts/python -m unittest -v
.venv/Scripts/python -m pip check
```

Tests cover retrieval, follow-ups, webpage extraction, invalid/private URLs, empty model responses, startup, and switching pages. Model calls in automated tests are mocked; hosted generation requires a separate live check.
