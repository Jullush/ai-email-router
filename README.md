# AI Email Router PoC

A production-grade Proof of Concept (PoC) that serves as an intelligent email router. The system processes non-deterministic user queries, 
evaluates sender intent using a locally hosted Large Language Model (LLM via Ollama), 
and autonomously dispatches tickets to the appropriate department using AI Agent Tool Calling mechanisms.

---

## Architecture Overview

The system is designed as a containerized microservice architecture ensuring operational isolation, determinism, and data privacy by hosting the LLM locally.

```
+------------------+      POST /api/v1/messages       +----------------------+
|   HTTP Client    | -------------------------------> |   FastAPI Gateway    |
+------------------+                                  +----------------------+
                                                                 |
                                                                 v
                                                      +----------------------+
                                                      |   LangChain Agent    |
                                                      |  (Ollama: llama3.2)  |
                                                      +----------------------+
                                                                 |
                                                                 v (Tool Calling)
+------------------+         SMTP (Port 1025)         +----------------------+
| MailHog Server   | <------------------------------- |   send_email Tool    |
| (Web UI: :8025)  |                                  +----------------------+
+------------------+
```

### Core Components

1. **API Layer (FastAPI & Pydantic):** Ingests incoming HTTP requests (`POST /api/v1/messages`), validates payload schema (`email`, `message`), and hosts interactive OpenAPI/Swagger documentation.
2. **AI Agent Core (LangChain & Ollama):**
   - Utilizes `llama3.2:3b` executing inside a dedicated container.
   - Evaluates message semantics against departmental guidelines.
   - Executes autonomous function calling (`send_email` tool) with deterministic argument binding.
   - Validates execution results via `RoutingResult` to prevent false-positive acknowledgments.
3. **Mail Dispatcher & Testing Server (SMTP & MailHog):** Sends routed messages over standard SMTP while preserving the original sender address in the `Reply-To` header, captured by the MailHog test mailbox.

---

## Department Routing Matrix

| Department | Target Recipient | Scope & Responsibility |
| :--- | :--- | :--- |
| **IT Support** | `it@example.com` | Hardware failures, network infrastructure, software provisioning |
| **Help Desk** | `help-desk@example.com` | Account management, system credentials, password resets, access grants |
| **Human Resources** | `human-resources@example.com` | Recruitment, leave requests, employee relations, company benefits |
| **Payroll & Personnel** | `kadry@example.com` | Salaries, contracts, tax declarations, employment certificates |
| **Fallback (Other)** | `other@example.com` | Uncategorized inquiries, cross-functional topics, ambiguous requests |

---

## Quickstart Guide

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v24.0+)
- [Docker Compose](https://docs.docker.com/compose/) (v2.20+)

### 1. Launch Environment

Execute the following command in the project root directory:

```bash
docker compose up -d
```

The orchestration setup automatically:
- Starts the **Ollama** engine service.
- Initializes model provisioning (`llama3.2:3b`) via `ollama-init`.
- Starts the **MailHog** SMTP server and Web UI.
- Builds and runs the **FastAPI** application container.

---

## Service Endpoints & Interfaces

| Interface | URL | Description |
| :--- | :--- | :--- |
| **Swagger UI** | [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs) | Interactive API exploration and test client |
| **OpenAPI Specification** | [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json) | Raw OpenAPI schema JSON |
| **MailHog Web UI** | [http://localhost:8025](http://localhost:8025) | Webmail console for inspecting routed emails |
| **Health Check** | [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) | Service operational status endpoint |

---

## Usage Examples

### 1. Hardware Issue (Routed to IT)

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@company.com",
    "message": "My primary workstation monitor has failed and does not turn on."
  }'
```

**Response:**
```json
{
  "status": "success"
}
```

### 2. Authentication Problem (Routed to Help Desk)

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice.smith@company.com",
    "message": "I entered an incorrect password multiple times and my ERP account is locked. Please unlock it."
  }'
```

### 3. Vacation Policy Inquiry (Routed to Human Resources)

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "email": "robert.johnson@company.com",
    "message": "Could you please clarify the remaining annual leave allowance for this calendar year?"
  }'
```

### 4. Payroll Certificate Request (Routed to Kadry)

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "email": "emily.davis@company.com",
    "message": "Please generate and issue an official earnings certificate for my bank mortgage application."
  }'
```

---

## Inspecting Dispatched Emails

1. Navigate to **[http://localhost:8025](http://localhost:8025)** in your browser.
2. Select any newly arrived email to inspect delivery details:
   - **Recipient (`To`):** Assigned department address (e.g., `it@example.com`).
   - **Sender (`From`):** `routing-agent@example.com`.
   - **Reply-To:** Original request sender address (e.g., `john.doe@company.com`).
   - **Content:** Exact user message payload.

---

## Local Development (Without Full Dockerization)

To run the API locally with hot-reloading for rapid iteration:

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Start auxiliary services:**
   ```bash
   docker compose up -d ollama ollama-init mailhog
   ```

3. **Run development server:**
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```
