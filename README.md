# Aster & Row — AI Support Agent

> Internship assignment implementation for a reliable AI customer-support agent.

A reliable RAG-based customer support agent built with **Gemini, FAISS, Sentence Transformers, and Streamlit**.

The goal is not to answer every question, but to **avoid confidently giving incorrect answers** through deterministic routing, controlled retrieval, tool boundaries, safety checks, and behavioral evaluation.

---

## Key Features

- **Deterministic Routing** — Separates order queries, knowledge queries, unsafe requests, and clarification cases using rules.
- **Authority-Aware RAG** — Prioritizes `current` knowledge over `legacy` and `internal` documents using frontmatter metadata.
- **Conflict Detection** — Flags potential conflicts when multiple current sources provide contradictory information.
- **Secure Order Lookup** — The LLM never receives raw `orders.json`; order information is sanitized before being passed to Gemini.
- **Prompt-Injection Defense** — Retrieved documents are treated as untrusted data rather than instructions.
- **Multi-Turn Memory** — Supports follow-up questions using conversation context.
- **Behavioral Evaluation** — Evaluates routing, retrieval, tool usage, citations, safety, and data leakage.

---

## Architecture

```text
                         User
                           │
                           ▼
                    Streamlit UI
                           │
                           ▼
                   Agent Controller
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       Safety Check             Deterministic Router
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
              Knowledge Query       Order Query         Clarification
                    │                    │
                    ▼                    ▼
                Embeddings          Order Lookup
                    │                    │
                    ▼                    ▼
                FAISS RAG          Data Sanitization
                    │                    │
                    ▼                    │
           Authority + Conflict         │
                Detection               │
                    │                    │
                    └─────────┬──────────┘
                              ▼
                         Gemini LLM
                              │
                              ▼
                     Customer Response
```

The LLM does not directly access `orders.json`. Order information passes through the order lookup and sanitization layer before reaching Gemini.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | User interface |
| Google Gemini | Large Language Model |
| Sentence Transformers | Text embeddings |
| FAISS | Vector similarity search |
| Pytest | Testing |
| python-dotenv | Environment configuration |

---

## Project Structure

```text
ai-agent-intern-test/
│
├── app.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── agent.py
│   ├── router.py
│   ├── conversation.py
│   ├── safety.py
│   ├── prompts.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   └── order_lookup.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── gemini.py
│   │
│   └── observability/
│       ├── __init__.py
│       └── logger.py
│
├── knowledge-base/
│   ├── 01-returns-policy-current.md
│   ├── 02-returns-policy-legacy.md
│   ├── 03-shipping-policy-current.md
│   ├── 04-shipping-policy-legacy.md
│   ├── 05-warranty-policy-current.md
│   ├── 06-warranty-policy-legacy.md
│   ├── 07-membership-benefits-current.md
│   ├── 08-membership-benefits-legacy.md
│   ├── 09-international-shipping.md
│   ├── 10-faq-common-questions.md
│   ├── 11-product-care.md
│   ├── 12-breeze-tumbler-product-card.md
│   ├── 13-gift-cards-policy.md
│   └── 14-internal-content-migration-notes.md
│
├── data/
│   ├── orders.json
│   └── orders-data-dictionary.md
│
├── evaluation/
│   ├── visible-cases.json
│   ├── custom-cases.json
│   └── evaluate.py
│
├── tests/
│   ├── test_retrieval.py
│   ├── test_orders.py
│   ├── test_safety.py
│   ├── test_agent.py
│   └── test_conversation.py
│
└── scripts/
    └── build_index.py
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/bhaktijain09/ai-agent-intern-test.git
cd ai-agent-intern-test
```

### 2. Create a Virtual Environment

#### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from `.env.example`.

#### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

#### macOS/Linux

```bash
cp .env.example .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=gemini-3.6-flash

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
TOP_K=5
SIMILARITY_THRESHOLD=0.35
```

> **Important:** Never commit `.env` or your actual API key to GitHub.

---

## Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will be available at the local Streamlit URL shown in the terminal.

---

## Run Tests

Run the complete test suite:

```bash
python -m pytest tests/ -v
```

The tests cover:

- Order lookup
- Safety checks
- Agent routing
- Conversation memory
- Retrieval
- Authority handling
- Conflict detection

Some retrieval tests use the Sentence Transformer model and may download it from Hugging Face during the first run.

---

## Behavioral Evaluation

The project includes a behavioral evaluation suite designed to test whether the agent behaves reliably under normal and adversarial scenarios.

### Run the Complete Evaluation

```bash
python evaluation/evaluate.py
```

### Run Custom / Adversarial Cases

```bash
python evaluation/evaluate.py --cases custom
```

The evaluation checks system behavior including:

- Correct routing
- Tool usage
- Source citations
- Safety handling
- PII protection
- Conflict handling
- Human hand-off behavior
- Data leakage prevention

A valid `GEMINI_API_KEY` is required for the full LLM evaluation.

---

## Deliberate Conflict Case

The knowledge base contains two **current** documents with intentionally conflicting information.

This case is designed to test whether the retrieval system can detect conflicting authoritative sources instead of silently selecting one.

### Source A

`knowledge-base/11-product-care.md`

States that Aster & Row drinkware, including the Breeze Tumbler, is:

> Hand wash only

### Source B

`knowledge-base/12-breeze-tumbler-product-card.md`

States that the Breeze Tumbler is:

> Dishwasher safe

Both documents contain:

```yaml
status: current
```

Neither filename contains the word `current`.

This is intentional. The retrieval system uses document metadata to determine authority rather than relying only on filenames.

When both sources are relevant, the retriever flags a potential conflict so the agent can avoid silently selecting one source.

---

## Security

The system uses multiple defensive mechanisms to reduce hallucination, prompt injection, and sensitive-data exposure.

### Prompt-Injection Protection

Retrieved documents are treated as **untrusted data**, not system instructions.

The knowledge base includes an internal document containing an embedded prompt-injection attempt to test this behavior.

The agent is designed to prevent retrieved content from overriding the system's instructions or security boundaries.

### Authority Handling

Documents can be classified as:

```text
current
legacy
internal
unclassified
```

Current documents receive higher authority than legacy documents, while internal documents are not treated as customer-facing authoritative sources.

Authority is determined using document metadata rather than relying solely on filenames.

### Order Data Sanitization

The LLM does not receive the raw `orders.json` file.

The order lookup flow is:

```text
User
  ↓
Agent
  ↓
lookup_order()
  ↓
sanitize_order()
  ↓
Customer-safe order data
  ↓
Gemini
```

Sensitive and internal order fields are removed before the data reaches the LLM.

For cancelled or returned orders, stale shipping information can be removed or nullified to prevent incorrect shipping claims.

---

## Reliability Design

The system deliberately avoids relying on the LLM for decisions that can be handled deterministically.

### Deterministic Routing

Queries are classified before the LLM is invoked.

This prevents the model from freely deciding whether a request should access customer order data or the knowledge base.

### Controlled Retrieval

Knowledge queries use semantic retrieval through Sentence Transformers and FAISS.

Retrieved documents are filtered and evaluated based on:

- Similarity
- Document authority
- Source metadata
- Potential conflicts

### Tool Boundaries

Order data is accessed through a dedicated lookup function rather than being exposed directly to the LLM.

This creates a controlled boundary between customer requests and internal order data.

### Safety Checks

Unsafe or disallowed requests can be intercepted before normal knowledge retrieval or tool execution.

---

## Design Trade-Off

The project intentionally uses a lightweight architecture:

- Streamlit instead of React
- In-memory FAISS instead of a hosted vector database
- Local JSON order data instead of a production database
- No microservices

The focus is on **RAG reliability, agent boundaries, safety, and evaluation** rather than unnecessary infrastructure complexity.

For an internship assignment, this keeps the implementation understandable, testable, and easy to run locally while still demonstrating production-relevant design principles.

---

## Future Improvements

Potential improvements for a production deployment include:

- React + FastAPI architecture
- Persistent vector database
- Authentication and role-based access
- Human support escalation
- Cloud deployment
- Production monitoring and tracing
- Advanced semantic conflict detection
- Automated knowledge-base versioning
- Persistent conversation storage
- Rate limiting and abuse prevention

---

## Project Goal

The central design principle of this project is:

> **A support agent should know when not to answer.**

Instead of optimizing only for response generation, the system emphasizes **controlled decision-making, reliable retrieval, safe tool usage, source awareness, and measurable behavior**.

This makes the agent more suitable for customer-support scenarios where an incorrect confident answer can be worse than asking for clarification or escalating to a human.