"""Streamlit chat UI for the research assistant."""
import os
import json
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://localhost:8000")
STREAM_TIMEOUT = 300  # 5 minutes — allows for slow local models

# Page config
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔍",
    layout="centered"
)

# Title
st.title("🔍 Multi-Agent Research Assistant")
st.markdown("Ask me anything and I'll research it for you!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show agent steps if available
        if message["role"] == "assistant" and "steps" in message:
            with st.expander("Agent Steps"):
                st.markdown(f"**Plan:** {message['steps']['plan']}")
                st.markdown(f"**Search Results:** {message['steps']['search_results']}")

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        final_data = None
        error_msg = None

        try:
            with st.status("Researching your question...", expanded=True) as status_widget:
                response = requests.post(
                    f"{DJANGO_API_URL}/api/ask/stream/",
                    json={"question": prompt},
                    stream=True,
                    timeout=STREAM_TIMEOUT
                )
                response.raise_for_status()

                for raw_line in response.iter_lines():
                    if not raw_line:
                        continue
                    event = json.loads(raw_line)
                    etype = event.get("type")

                    if etype == "status":
                        st.write(f"⏳ {event['message']}")

                    elif etype == "update":
                        st.write(f"✅ {event['message']}")
                        if event.get("plan"):
                            st.caption(f"**Plan:** {event['plan']}")
                        if event.get("search_results"):
                            preview = event["search_results"][:120]
                            if len(event["search_results"]) > 120:
                                preview += "..."
                            st.caption(f"**Found:** {preview}")

                    elif etype == "error":
                        st.write(f"❌ {event['message']}")
                        error_msg = event["message"]

                    elif etype == "result":
                        final_data = event["data"]
                        status_widget.update(
                            label="✅ Research complete!",
                            state="complete",
                            expanded=False
                        )
                        break

                response.close()

            # Render the answer outside the status widget
            if final_data:
                answer = final_data.get("answer", "No answer received")
                st.markdown(answer)

                if final_data.get("error"):
                    st.warning(f"Note: {final_data['error']}")

                with st.expander("Agent Steps"):
                    st.markdown(f"**Plan:** {final_data.get('plan', 'N/A')}")
                    st.markdown(f"**Search Results:** {final_data.get('search_results', 'N/A')}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "steps": {
                        "plan": final_data.get("plan", "N/A"),
                        "search_results": final_data.get("search_results", "N/A")
                    }
                })

            elif error_msg:
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {error_msg}"
                })

        except requests.exceptions.Timeout:
            error_msg = "Request timed out. The model is too slow — try a shorter question or switch to a faster model."
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        except requests.exceptions.ConnectionError:
            error_msg = f"Could not connect to the API at {DJANGO_API_URL}. Make sure the backend is running."
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with info
with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    This is a multi-agent research assistant powered by:
    - LangGraph for agent orchestration
    - Django REST API backend
    - Streamlit for the UI

    The system uses a Planner agent and a Researcher agent to answer your questions.
    """)

    st.markdown("### Status")
    st.markdown(f"API URL: `{DJANGO_API_URL}`")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
