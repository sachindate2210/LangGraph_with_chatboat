import uuid
import streamlit as st

from agent.multi_graph_builder import multi_agent_graph
from database.save_step import save_step
from database.save_session import save_session
from database.create_tables import create_tables
create_tables()
from memory.session_memory import add_session_memory



st.set_page_config(
    page_title="AI Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Agent")

# CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# DISPLAY CHAT HISTORY
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

query = st.chat_input("Type your message...")


if query:

    # SHOW USER MESSAGE
    with st.chat_message("user"):
        st.markdown(query)
    # SAVE USER MESSAGE
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    session_id = uuid.uuid4()

    try:

        with st.spinner("Agent Thinking..."):

            # =================================================
            # STEP 1 — USER INPUT
            # =================================================

            save_step(session_id, 1, "User Input", query)

            add_session_memory(f"User: {query}")

            # =================================================
            # STEPS 2–9 — LANGGRAPH
            # =================================================

            result = multi_agent_graph.invoke(
                {
                    "query":              query,
                    "session_id":         str(session_id),
                    "memory":             "",
                    "task_queue":         [],
                    "current_task":       "",
                    "research_result":    "",
                    "calculation_result": "",
                    "weather_result":     "",
                    "database_result":    "",
                    "file_result":        "",
                    "email_result":       "",
                    "final_answer":       ""
                },
                {"recursion_limit": 25}
            )

            final_answer = result["final_answer"]

            # SAVE AI RESPONSE
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": final_answer
                }
            )

            # =================================================
            # SAVE SESSION
            # =================================================

            save_session(session_id, query, final_answer)

            # =================================================
            # UI OUTPUT
            # =================================================
            
            with st.chat_message("assistant"):
                st.markdown(final_answer)

            # PDF DOWNLOAD
            if "output.pdf" in final_answer:
                with open("output.pdf", "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=f,
                        file_name="result.pdf",
                        mime="application/pdf"
                    )

            # DATABASE RESULT DOWNLOAD (large results)
            if "[DOWNLOAD_FILE:db_result.txt]" in final_answer:
                with open("db_result.txt", "rb") as f:
                    st.download_button(
                        label="⬇️ Download Full DB Result",
                        data=f,
                        file_name="db_result.txt",
                        mime="text/plain"
                    )

    except Exception as e:

        import traceback
        st.error(f"Error: {str(e)}")
        st.code(traceback.format_exc())