# Project assessment

The original checkout contained a complete single-page UI and a basic RAG pipeline, but it was an unverified prototype rather than a reliable application.

## Original gaps found

- The same vector store stayed in session state after changing the website URL.
- A large frozen 2024 environment included unrelated packages and legacy inference dependencies.
- The configured model ID had no version suffix; model availability needed verification.
- Page loading, token errors, and provider failures had no user-facing recovery.
- No tests, setup instructions, source passages, or conversation reset controls.
- `.env` was tracked. This change stops tracking it, but does not remove it from Git history or revoke any old credential.

## Repair scope

Single public webpage loading, conversation reset on page change, passage retrieval, history-aware questions, current Hugging Face hosted chat API, source display, error recovery, a local virtual environment, and tests.

Retrieval now uses TF-IDF instead of local transformer embeddings and Chroma. It is cheaper to run locally, but semantic matching quality can be lower. This is an explicit tradeoff, not equivalent retrieval behavior.

## Remaining scope

Live hosted inference must pass before calling the app end-to-end working. Whole-site crawling, JavaScript pages, persistent storage, and production deployment hardening are outside the existing single-page MVP. Changes are local; the remote Space has not been updated.

## Verification results

- Seven automated tests passed: startup, page switching, failure/retry behavior, passage ranking and follow-ups, extraction, invalid/private URL rejection, and empty model response handling.
- Dependency consistency check passed.
- Live HTML load from example.com passed.
- The original `mistralai/Mistral-7B-Instruct` model lookup returned HTTP 404.
- Initial replacement `Qwen/Qwen2.5-7B-Instruct` was rejected because none of the account's enabled providers supported it.
- Final default `meta-llama/Llama-3.1-8B-Instruct` returned a grounded answer with a source citation using the locally authenticated account.
- Local Streamlit health endpoint returned `ok` on port 8501.

The core single-page MVP works in the tested flow. This is not a production readiness claim or a guarantee for every website/model/provider. The repaired app is running locally; Hugging Face still contains the original code until these changes are pushed.
