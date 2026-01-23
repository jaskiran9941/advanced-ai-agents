"""Streamlit UI for Email Analysis Bot.

A web-based interface for testing and using the email analysis bot
without needing Slack.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.gmail import GmailClient
from src.agent import AIProvider, AIProviderFactory, AgentRunner, SessionManager
from src.agent.tools import ToolRegistry, register_email_tools
import structlog


# Page configuration
st.set_page_config(
    page_title="Email Analysis Bot",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def initialize_bot():
    """Initialize the bot components (cached for performance)."""

    # Setup logging
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(structlog.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    try:
        # Initialize Gmail client
        gmail_client = GmailClient(
            credentials_file=settings.gmail.credentials_file,
            token_file=settings.gmail.token_file,
            scopes=settings.gmail.scopes,
        )

        # Initialize AI provider
        provider_factory = AIProviderFactory(default_provider=settings.ai.default_provider)

        # Register Anthropic provider if available
        try:
            anthropic_provider = AIProvider(
                provider="anthropic",
                api_key=settings.anthropic.api_key,
                model=settings.anthropic.model,
                max_tokens=settings.anthropic.max_tokens,
            )
            provider_factory.register_provider(anthropic_provider)
        except Exception:
            pass

        # Register OpenAI provider if available
        try:
            openai_provider = AIProvider(
                provider="openai",
                api_key=settings.openai.api_key,
                model=settings.openai.model,
                max_tokens=settings.openai.max_tokens,
            )
            provider_factory.register_provider(openai_provider)
        except Exception:
            pass

        llm = provider_factory.get_llm()

        # Initialize tool registry
        tool_registry = ToolRegistry(
            allowlist=settings.tools.allowlist,
            blocklist=settings.tools.blocklist,
        )
        register_email_tools(tool_registry, gmail_client)

        # Initialize agent runner
        agent_runner = AgentRunner(
            llm=llm,
            tool_registry=tool_registry,
            max_iterations=10,
            verbose=False,
        )

        # Initialize session manager
        session_manager = SessionManager()

        return {
            'agent': agent_runner,
            'session_manager': session_manager,
            'gmail_client': gmail_client,
            'tool_registry': tool_registry,
            'provider_factory': provider_factory,
        }

    except Exception as e:
        st.error(f"Failed to initialize bot: {str(e)}")
        st.info("Please make sure you've run `python scripts/setup_gmail.py` and configured your .env file")
        return None


def main():
    """Main Streamlit app."""

    # Title and header
    st.title("📧 Email Analysis Bot")
    st.markdown("Ask questions about your Gmail emails using natural language")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Try to initialize bot
        bot_components = initialize_bot()

        if bot_components:
            st.success("✅ Bot initialized successfully!")

            # Show configuration
            with st.expander("Configuration Details"):
                st.write(f"**AI Provider:** {settings.ai.default_provider}")
                st.write(f"**Gmail Scopes:** {', '.join(settings.gmail.scopes)}")
                st.write(f"**Available Tools:** {len(bot_components['tool_registry'].get_filtered_tools())}")

            # Show available tools
            with st.expander("Available Tools"):
                tools = bot_components['tool_registry'].get_filtered_tools()
                for tool in tools:
                    st.write(f"**{tool.name}**")
                    st.caption(tool.description)
                    st.divider()

            # Quick stats
            try:
                gmail_client = bot_components['gmail_client']
                unread_count = gmail_client.get_unread_count()
                st.metric("Unread Emails", unread_count)
            except Exception as e:
                st.warning(f"Could not fetch email stats: {str(e)}")

        else:
            st.error("❌ Bot not initialized")
            st.info("""
            **Setup Required:**
            1. Run: `python scripts/setup_gmail.py`
            2. Configure your `.env` file with:
               - SLACK_BOT_TOKEN (optional for Streamlit)
               - ANTHROPIC_API_KEY or OPENAI_API_KEY
            3. Restart Streamlit
            """)
            return

        # Session controls
        st.divider()
        st.header("💬 Session")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            bot_components['session_manager'].clear_session("streamlit_session")
            st.rerun()

    # Main chat interface
    if bot_components:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "timestamp" in message:
                    st.caption(message["timestamp"])

        # Example queries
        if not st.session_state.messages:
            st.markdown("### 💡 Try these example queries:")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📬 Unread emails"):
                    example_query = "What are my unread emails?"
                    st.session_state.example_query = example_query
                    st.rerun()

            with col2:
                if st.button("🔍 Recent emails"):
                    example_query = "Show me emails from the last 3 days"
                    st.session_state.example_query = example_query
                    st.rerun()

            with col3:
                if st.button("👥 Email summary"):
                    example_query = "Who has emailed me the most recently?"
                    st.session_state.example_query = example_query
                    st.rerun()

        # Chat input
        default_value = ""
        if "example_query" in st.session_state:
            default_value = st.session_state.example_query
            del st.session_state.example_query

        if prompt := st.chat_input("Ask about your emails...", value=default_value):
            # Add user message to chat
            timestamp = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": timestamp
            })

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption(timestamp)

            # Display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                with st.spinner("🤔 Thinking..."):
                    try:
                        # Get chat history for context
                        chat_history = bot_components['session_manager'].get_history("streamlit_session")

                        # Run agent
                        response = bot_components['agent'].run(
                            query=prompt,
                            chat_history=chat_history if chat_history else None
                        )

                        # Update session history
                        bot_components['session_manager'].add_message("streamlit_session", "human", prompt)
                        bot_components['session_manager'].add_message("streamlit_session", "ai", response)

                        # Display response
                        message_placeholder.markdown(response)
                        timestamp = datetime.now().strftime("%I:%M %p")
                        st.caption(timestamp)

                        # Add assistant response to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": timestamp
                        })

                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        message_placeholder.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Email Analysis Bot powered by AI • Built with Streamlit</p>
        <p style='font-size: 0.8em;'>Your emails are processed securely and never stored by this app</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
