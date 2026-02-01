# Internal AI Assistant (Take-Home Assignment)

A lightweight enterprise-style AI assistant that answers internal user queries using real web-grounded information and can safely execute internal actions (reminders/notifications) only after explicit user confirmation.

This project was built as part of an advanced take-home assignment to demonstrate:

- Retrieval-Augmented Generation (RAG)
- Action execution with guardrails
- Confirmation-based safety
- Transparent audit logging
- Clean enterprise UI

## Key Features

### Web-Grounded Question Answering (RAG)

The assistant retrieves relevant real-world policy/regulatory information from the web. Responses are generated only from retrieved snippets. Top references are shown for transparency and verification.

### Safe Internal Action Execution

The assistant can propose internal actions such as:

- Notify a team
- Send a reminder

Actions are executed only after:

1. Detection
2. User confirmation
3. Execution logging

This prevents unsafe or accidental automation.

### Selective Retrieval (Efficiency + Relevance)

Not every action requires external retrieval.

**Example:**

- "Send a reminder to HR" → no retrieval needed  
- "Notify compliance about EU AI Act updates" → retrieval required  

The system routes requests accordingly using a lightweight retrieval router.

### Action Audit Trail

All executed actions are logged and visible in the Action Center.

Additional enterprise capability:
- Downloadable Action Audit Log (JSON)

## Design Decisions & Trade-offs

### Why Web Retrieval Instead of Static Knowledge?

Enterprise assistants must stay grounded in up-to-date regulations and policies. Using live retrieval ensures the assistant provides verifiable responses rather than hallucinated facts.

**Trade-off:** Web snippets may sometimes be incomplete, so the assistant reports confidence accordingly.

### Why Confirmation Before Actions?

Action execution is treated as a high-trust operation. The assistant never executes actions automatically. This matches real-world internal tooling standards.

**Trade-off:** Adds an extra click, but ensures safety.

### Why Simulated Internal Actions Instead of Real Email?

In production, actions would integrate with internal systems (Slack, Jira, Email, etc.). For reliability in take-home evaluation, actions are logged internally with full transparency. Optional email utilities can be integrated later without breaking deployment.

**Trade-off:** Avoids fragile SMTP dependencies during review.

### Why Streamlit?

Streamlit provides rapid development of a professional UI with minimal overhead, ideal for demonstrating workflow and interaction design within limited implementation time.

## Installation (Local Run)

### 1. Clone Repository
```bash
git clone https://github.com/SaiBhavyaYangoti/internal-ai-assistant.git
cd internal-ai-assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Groq API Key

Create a `.env` file:
```bash
GROQ_API_KEY=your_key_here
```

### 4. Run App
```bash
streamlit run app.py
```

## Example Queries

### Retrieval Queries

- "What is the government policy on delayed vendor payments in India?"
- "What are the latest AI regulations introduced by the European Union?"

### Action Requests

- "Send a reminder to HR team to complete onboarding."
- "Notify the finance team about delayed vendor payments."

### Mixed Retrieval + Action

- "Alert compliance team about new EU AI regulations."

## Future Extensions

- Slack or MS Teams integration for real notifications
- Role-based access control for sensitive actions
- Persistent database-backed audit storage
- Internal knowledge base ingestion (PDF + company docs)

## Summary

This assistant demonstrates an enterprise-ready architecture combining:

- Real web-grounded responses
- Safe action execution with confirmation
- Transparent auditability
- Clean UI and modular design
