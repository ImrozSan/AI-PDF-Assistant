# 📄 AI PDF Assistant

An advanced, Streamlit-powered document intelligence and interactive Q&A application designed to transform static PDF files into dynamic, conversational knowledge bases. Built as a professional internship project, this tool utilizes state-of-the-art language models and document-parsing pipelines to provide precise, context-grounded answers directly from uploaded files.

---

## 🚀 Key Features

* **Intelligent Document Parsing:** Seamlessly upload and process PDF documents with automated text extraction and clean data chunking.
* **Context-Grounded Q&A:** Query documents using natural language to get accurate answers grounded directly in the text.
* **Zero-Hallucination Guardrails:** Explicitly communicates when information is missing from the uploaded text rather than generating false data.
* **Responsive Web Interface:** Built with Streamlit to deliver a clean, modern, and interactive user experience.

---

## 🛠️ Tech Stack

* **Frontend & UI:** Streamlit
* **AI & LLM Orchestration:** Python, Groq API, Qwen Models, LangChain / Custom Text Splitters
* **Document Processing:** PyPDF / PDF Text Extraction Libraries
* **Configuration:** Python-dotenv (`.env`), TOML (`.streamlit/config.toml`)

---

## 📁 Project Structure

```text
AI PDF Assistant/
│
├── .streamlit/
│   └── config.toml        # Streamlit theme and server configurations
├── .env                   # Local environment variables & API keys
├── ai.py                  # Core AI pipeline and LLM utilities
├── app.py                 # Main Streamlit application entry point
├── presentation.html      # Project presentation overview
└── requirements.txt       # Project dependencies
