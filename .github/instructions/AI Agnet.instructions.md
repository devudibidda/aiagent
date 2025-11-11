---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.
Role

You are an expert AI engineering assistant.
Your goal is to build a Python-based AI agent that:

Fetches PDF files from an external API using OAuth 2.0 authentication.

Processes and embeds PDF content using LangChain, LlamaIndex, and FAISS.

Runs Retrieval-Augmented Generation (RAG) with a local LLM such as Mistral, Llama 3, or Granite through Ollama.

Compares and analyzes the fetched document for compliance against a selected knowledge base of standards or policies.

Provides a simple Gradio UI for user interaction.

All operations must be performed locally (no cloud API calls) except for the authenticated PDF fetch.

Functional Requirements

Authentication

Use OAuth 2.0 client credentials flow.

Fetch access token and include Authorization: Bearer <token> header when calling the PDF API.

Allow environment-based configuration via .env.

PDF Processing

Read and extract text from each page using PyPDF2 or pypdf.

Split text into overlapping chunks using RecursiveCharacterTextSplitter.

Vectorization

Generate sentence embeddings with sentence-transformers/all-MiniLM-L6-v2.

Store vectors locally using FAISS.

Allow re-use of pre-built knowledge-base embeddings stored under knowledge_base/embeddings/.

RAG and Compliance Analysis

Build a RetrievalQA chain using LangChain.

Instantiate a local model with Ollama(model="mistral") or an equivalent Llama/Granite model.

Query: “Analyse this document for compliance gaps against the provided standards.”

Return structured text summarizing alignment and non-compliance areas.

User Interface

Expose a gradio.Blocks() app with inputs for:

PDF file ID (fetched from API)

Knowledge base path

Display compliance analysis output in a textbox.

Run locally on port 7860.

Structure

ai_compliance_agent/
    app.py
    config.py
    api_client.py
    pdf_processor.py
    vector_store.py
    agent_pipeline.py
    ui_gradio.py
    requirements.txt
    knowledge_base/
        standard_1.pdf
        embeddings/


Environment Configuration

Store credentials and URLs in .env

API_BASE_URL=
TOKEN_URL=
CLIENT_ID=
CLIENT_SECRET=


Load using dotenv.

Optional Enhancements

Batch mode for multiple PDFs.

Compliance score output (0–100).

Save results to JSON or CSV.

Dataverse or SQLite storage for reports.

Implementation Guidance

Use requests for OAuth2 token and file retrieval.

Use HuggingFaceEmbeddings from LangChain for vector creation.

Keep components modular: one Python file per subsystem.

Ensure FAISS index is stored locally for quick reuse.

For interactive testing, run:

python ui_gradio.py


then open http://localhost:7860.

Expected Behavior

When the agent runs:

It authenticates and downloads a specified PDF from the API.

Extracts and embeds its text.

Retrieves relevant context from the selected knowledge base.

Uses the local LLM to generate a compliance analysis.

Displays the result interactively through Gradio.