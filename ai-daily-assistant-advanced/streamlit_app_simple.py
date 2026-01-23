"""Simplified Streamlit UI for Email Analysis Bot.

Uses .env credentials for easy configuration.
"""

import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def initialize_bot():
    """Initialize the bot components."""
    import sys
    from pathlib import Path

    # Add src to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    try:
        # Check for required API key
        ai_provider = os.getenv('DEFAULT_AI_PROVIDER', 'anthropic')

        if ai_provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key or api_key == 'your-anthropic-key-here':
                return {'error': 'missing_ai_key', 'provider': 'Anthropic'}
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key or api_key == 'your-openai-key-here':
                return {'error': 'missing_ai_key', 'provider': 'OpenAI'}

        # Check for Gmail credentials
        gmail_client_id = os.getenv('GMAIL_CLIENT_ID')
        if not gmail_client_id:
            return {'error': 'missing_gmail', 'ai_provider': ai_provider}

        # Initialize components
        from src.gmail.simple_client import SimpleGmailClient
        from src.agent import AIProvider, AIProviderFactory, AgentRunner, SessionManager
        from src.agent.tools import (
            ToolRegistry,
            register_email_tools,
            register_financial_tools,
            register_calendar_helpers,
            get_composio_tools
        )
        from src.config.settings import settings
        import structlog

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

        # Initialize Gmail client
        gmail_client = SimpleGmailClient()

        # Initialize AI provider
        provider_factory = AIProviderFactory(default_provider=ai_provider)

        if ai_provider == 'anthropic':
            anthropic_provider = AIProvider(
                provider="anthropic",
                api_key=api_key,
                model="claude-opus-4-5-20251101",
                max_tokens=4096,
            )
            provider_factory.register_provider(anthropic_provider)
        else:
            openai_provider = AIProvider(
                provider="openai",
                api_key=api_key,
                model="gpt-4-turbo",
                max_tokens=4096,
            )
            provider_factory.register_provider(openai_provider)

        llm = provider_factory.get_llm()

        # Initialize tool registry
        tool_registry = ToolRegistry(allowlist=[], blocklist=[])
        register_email_tools(tool_registry, gmail_client)
        register_financial_tools(tool_registry, gmail_client)
        register_calendar_helpers(tool_registry, settings.composio.entity_id)

        # Get Composio tools count (for display)
        composio_tools = get_composio_tools() if settings.composio.enabled else []
        composio_count = len(composio_tools)

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
            'ai_provider': ai_provider,
            'composio_count': composio_count,
        }

    except Exception as e:
        return {'error': 'init_failed', 'message': str(e)}


def show_setup_instructions(error_type, **kwargs):
    """Show setup instructions based on error type."""
    if error_type == 'missing_ai_key':
        st.error(f"❌ {kwargs['provider']} API key not configured")
        st.info(f"""
        **Setup Required:**

        1. Get your {kwargs['provider']} API key:
           - Anthropic: https://console.anthropic.com/
           - OpenAI: https://platform.openai.com/api-keys

        2. Open `.env` file in the project root

        3. Add your API key:
           ```
           ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
           ```

        4. Restart Streamlit
        """)

    elif error_type == 'missing_gmail':
        st.warning("⚠️ Gmail OAuth not configured")
        st.info("""
        **Gmail Setup (3 steps):**

        **Step 1:** Create Google Cloud OAuth Credentials
        1. Go to https://console.cloud.google.com/
        2. Create a new project (or select existing)
        3. Enable "Gmail API" (APIs & Services → Library)
        4. Create OAuth credentials (APIs & Services → Credentials)
           - Type: Desktop app
        5. Download the JSON file as `credentials.json`
        6. Save in project root: `email-slack-bot/credentials.json`

        **Step 2:** Run the setup script
        ```bash
        python3 scripts/setup_gmail_simple.py
        ```

        This will:
        - Open your browser for OAuth authorization
        - Automatically save credentials to `.env`

        **Step 3:** Restart Streamlit
        """)

    elif error_type == 'init_failed':
        st.error(f"❌ Initialization failed: {kwargs['message']}")
        st.info("""
        **Troubleshooting:**
        - Check that all required packages are installed
        - Verify `.env` file exists and has correct values
        - Check the terminal for detailed error messages
        """)


def main():
    """Main Streamlit app."""

    # Title and header
    st.title("📧 Email Analysis Bot")
    st.markdown("Ask questions about your Gmail emails using natural language")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Initialize bot
        bot_components = initialize_bot()

        if 'error' in bot_components:
            show_setup_instructions(bot_components['error'], **bot_components)
            return
        else:
            st.success("✅ Bot initialized successfully!")

            # Show configuration
            with st.expander("Configuration Details"):
                st.write(f"**AI Provider:** {bot_components['ai_provider']}")
                custom_tool_count = len(bot_components['tool_registry'].get_filtered_tools())
                composio_count = bot_components.get('composio_count', 0)
                total_tools = custom_tool_count + composio_count
                st.write(f"**Custom Tools:** {custom_tool_count}")
                st.write(f"**Composio Tools:** {composio_count}")
                st.write(f"**Total Tools:** {total_tools}")

            # Show Composio status
            if bot_components.get('composio_count', 0) > 0:
                st.info(f"✅ Composio tools loaded: {bot_components['composio_count']}")

            # Show available tools
            with st.expander("Available Custom Tools"):
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

        # Session controls
        st.divider()
        st.header("💬 Session")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            bot_components['session_manager'].clear_session("streamlit_session")
            st.rerun()

    # Main chat interface
    if 'error' not in bot_components:
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
        <p style='font-size: 0.8em;'>All credentials stored in .env file</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
