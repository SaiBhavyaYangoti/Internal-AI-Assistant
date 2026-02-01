import streamlit as st
import streamlit_antd_components as sac

from agent import run_assistant
from actions import execute_action

# ---------------------------------
# Page Configuration
# ---------------------------------
st.set_page_config(page_title="Internal AI Assistant", layout="wide")

# ---------------------------------
# UI Styling (Chat Bubble Design)
# ---------------------------------
st.markdown("""
<style>
.center-box {
    text-align:center;
    padding:25px;
}
.card-box {
    background:white;
    padding:22px;
    border-radius:18px;
    box-shadow:0px 6px 25px rgba(0,0,0,0.08);
    margin-bottom:18px;
}
.small-note {
    color:gray;
    font-size:15px;
}

/* Chat bubble layout (no avatars) */
.user-bubble {
    background:#dbeafe;
    padding:12px;
    border-radius:14px;
    margin:8px;
    text-align:right;
    max-width:70%;
    margin-left:auto;
}

.ai-bubble {
    background:#f3f4f6;
    padding:14px;
    border-radius:14px;
    margin:8px;
    text-align:left;
    max-width:70%;
    margin-right:auto;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# Session State Initialization
# ---------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

if "action_log" not in st.session_state:
    st.session_state.action_log = []

# ---------------------------------
# Sidebar Navigation Menu
# ---------------------------------
with st.sidebar:
    menu = sac.menu([
        sac.MenuItem("Home", icon="house-fill"),
        sac.MenuItem("AI Assistant", icon="robot"),
        sac.MenuItem("Action Center", icon="activity")
    ], open_all=True)

# =================================
# Home Page
# =================================
if menu == "Home":

    st.markdown("""
    <div class="card-box center-box">
        <h1>🤖 Internal AI Assistant</h1>
        <p class="small-note">
        A web-grounded enterprise assistant that answers questions  
        and performs actions only after confirmation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card-box">
        <h3>How it works:</h3>
        ● Ask an internal query<br>
        ● Assistant retrieves reliable web evidence<br>
        ● Suggests actions (reminders/notifications)<br>
        ● Executes only after confirmation<br>
        ● Logs actions transparently<br>
    </div>
    """, unsafe_allow_html=True)

    st.info("➡️ Select **AI Assistant** from the sidebar to begin chatting.")

# =================================
# AI Assistant Chat Page
# =================================
elif menu == "AI Assistant":

    st.markdown("""
    <div class="card-box">
        <h2>🤖 AI Assistant Chat</h2>
        <p class="small-note">
        Ask policy/workflow questions. If an action is needed,  
        the assistant will request confirmation before execution.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Display full chat conversation history
    for role, msg in st.session_state.chat_history:

        if role == "User":
            st.markdown(
                f"""
                <div class='user-bubble'>
                {msg}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            # Render assistant response inside styled bubble
            st.markdown("<div class='ai-bubble'>", unsafe_allow_html=True)
            st.markdown(msg)
            st.markdown("</div>", unsafe_allow_html=True)

    # User input box (ChatGPT-style)
    user_text = st.chat_input("Type your request...")

    if user_text:

        # Store user message
        st.session_state.chat_history.append(("User", user_text))

        # Run assistant pipeline
        result = run_assistant(user_text)

        # Build assistant response message
        assistant_text = result["answer"]

        # Attach references if retrieval was used
        if result["sources"]:
            refs = "\n".join(
                [f"- [{s['title']}]({s['link']})"
                 for s in result["sources"][:5]]
            )

            assistant_text += f"""

---

### 🔗 Top References
{refs}
"""

        # Attach proposed action request if detected
        if result["intent"] == "ACTION":

            action = result["proposed_action"]
            st.session_state.pending_action = action

            assistant_text += f"""

---

### ⚠️ Proposed Action
- Action: **{action['action_type'].replace('_',' ')}**
- Target: **{action['target']}**

Please confirm below to execute, or cancel safely.
"""

        # Store assistant response
        st.session_state.chat_history.append(("AI", assistant_text))

        st.rerun()

    # Action confirmation workflow
    if st.session_state.pending_action:

        st.divider()
        st.subheader("Action Confirmation")

        colA, colB = st.columns(2)
        action = st.session_state.pending_action

        with colA:
            if st.button("✅ Confirm Execution"):

                outcome = execute_action(
                    action_type=action["action_type"],
                    target=action["target"]
                )

                # Log executed action
                st.session_state.action_log.append(outcome)
                st.session_state.pending_action = None

                # Append confirmation message in chat
                st.session_state.chat_history.append(
                    ("AI", f"""
✅ **Action Completed Successfully**

- Status: `{outcome['status']}`
- Target: **{outcome['target']}**
- Message: {outcome['message']}
""")
                )

                st.rerun()

        with colB:
            if st.button("❌ Cancel Action"):

                st.session_state.pending_action = None
                st.session_state.chat_history.append(
                    ("AI", "❌ Action cancelled. No execution was performed.")
                )

                st.rerun()

# =================================
# Action Center Page (Audit Trail)
# =================================
elif menu == "Action Center":

    import json

    st.markdown("""
    <div class="card-box">
        <h2>📌 Action Center</h2>
        <p class="small-note">
        Transparent audit trail of all executed actions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Show executed actions if available
    if st.session_state.action_log:

        # Allow downloading full audit log as JSON
        st.download_button(
            "⬇️ Download Action Audit Log (JSON)",
            data=json.dumps(st.session_state.action_log, indent=2),
            file_name="action_audit_log.json",
            mime="application/json"
        )

        st.markdown("### Executed Actions")

        # Display latest actions first
        for a in reversed(st.session_state.action_log):
            st.markdown(f"""
            <div class="card-box">
                <b>{a['action_type']}</b> → {a['target']} <br>
                Status: <code>{a['status']}</code> <br>
                Message: {a['message']}
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("No actions executed yet.")
