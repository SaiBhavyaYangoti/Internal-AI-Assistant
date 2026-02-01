import json
import re
from llm import call_llm
from search import web_search

# -----------------------------
# Action Keywords (Guardrail Layer)
# -----------------------------
ACTION_KEYWORDS = [
    "notify", "remind", "send reminder",
    "send notification", "alert", "follow up"
]

# -----------------------------
# Intent Detection (Rule-based + LLM Backup)
# -----------------------------
def detect_intent(user_query: str):

    query_lower = user_query.lower()

    # Fast rule-based check for action-style requests
    if any(k in query_lower for k in ACTION_KEYWORDS):
        return "ACTION"

    # LLM fallback for ambiguous cases
    prompt = f"""
Return ONLY valid JSON.

User query:
"{user_query}"

Format:
{{"intent":"QUERY"}} OR {{"intent":"ACTION"}}
"""

    raw = call_llm(prompt)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            return parsed.get("intent", "QUERY")
        except:
            return "QUERY"

    return "QUERY"

# -----------------------------
# Action Extraction (Structured JSON)
# -----------------------------
def extract_action(user_query: str):

    prompt = f"""
Return ONLY valid JSON.

User query:
"{user_query}"

Extract:
- action_type: send_reminder OR notify_team
- target: short team/entity name

Format:
{{
  "action_type": "...",
  "target": "..."
}}
"""

    raw = call_llm(prompt)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            return parsed.get("action_type", "notify_team"), parsed.get("target", "team")
        except:
            return "notify_team", "team"

    return "notify_team", "team"

# -----------------------------
# Selective Retrieval Router (LLM-based)
# -----------------------------
def needs_retrieval(user_query: str):

    prompt = f"""
Return ONLY JSON.

User request:
"{user_query}"

Does this require external information retrieval before executing the action?

Rules:
- Pure operational action (send reminder to HR) → false
- Policy/news/compliance context required → true

Format:
{{"needs_retrieval": true}} OR {{"needs_retrieval": false}}
"""

    raw = call_llm(prompt)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            return parsed.get("needs_retrieval", True)
        except:
            return True

    return True

# -----------------------------
# Web-Grounded Question Answering
# -----------------------------
def answer_query(user_query: str):

    sources = web_search(user_query)
    top = sources[:5]

    context = "\n".join(
        f"{i+1}. {s['title']} ({s['link']}): {s['snippet']}"
        for i, s in enumerate(top)
    )

    prompt = f"""
You are an Internal AI Assistant (not an email writer).

User question:
"{user_query}"

Web snippets:
{context}

Instructions:
- Do not respond with greetings or email format
- Use clean Markdown structure
- Use bullet points for key details
- Only use information from the retrieved snippets

Return EXACTLY in this format:

### Summary
(3–5 lines)

### Key Points
- Point 1
- Point 2
- Point 3
- Point 4

### Confidence
High / Medium / Low  
Reason: (start on new line)

### Suggested Next Step
One helpful follow-up question the user can ask next.
"""

    answer = call_llm(prompt)

    # Post-processing: enforce consistent heading formatting
    answer = answer.replace("### Summary ", "### Summary\n\n")
    answer = answer.replace("### Key Points ", "### Key Points\n\n")
    answer = answer.replace("### Confidence ", "### Confidence\n\n")

    return answer, sources

# -----------------------------
# Main Assistant Orchestration Pipeline
# -----------------------------
def run_assistant(user_query: str):

    intent = detect_intent(user_query)

    # Standard query flow: always grounded in retrieval
    if intent == "QUERY":
        answer, sources = answer_query(user_query)
        return {
            "intent": "QUERY",
            "answer": answer,
            "sources": sources
        }

    # Action flow: extract tool intent first
    action_type, target = extract_action(user_query)

    # Decide whether retrieval context is required
    retrieval_required = needs_retrieval(user_query)

    # Pure internal operational action (no retrieval needed)
    if not retrieval_required:
        return {
            "intent": "ACTION",
            "answer": "Action request detected. Confirmation required.",
            "sources": [],
            "proposed_action": {
                "action_type": action_type,
                "target": target
            }
        }

    # Contextual action: retrieve evidence + then propose action
    answer, sources = answer_query(user_query)

    return {
        "intent": "ACTION",
        "answer": answer,
        "sources": sources,
        "proposed_action": {
            "action_type": action_type,
            "target": target
        }
    }
