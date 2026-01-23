"""AI agent execution runner with tool calling support."""

from typing import Optional, Dict, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseLanguageModel
from .tools.registry import ToolRegistry
import structlog

logger = structlog.get_logger()


class AgentRunner:
    """Agent execution runner with LangChain."""

    def __init__(
        self,
        llm: BaseLanguageModel,
        tool_registry: ToolRegistry,
        max_iterations: int = 10,
        verbose: bool = False,
    ):
        """Initialize agent runner.

        Args:
            llm: Language model instance
            tool_registry: Tool registry with registered tools
            max_iterations: Maximum agent iterations
            verbose: Enable verbose logging
        """
        self.llm = llm
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """Create LangChain agent with tools.

        Returns:
            Agent executor instance
        """
        # Get tools from registry
        tools = self.tool_registry.to_langchain_tools()

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)

        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            max_iterations=self.max_iterations,
            verbose=self.verbose,
            handle_parsing_errors=True,
            return_intermediate_steps=False,
        )

        logger.info("Created agent executor", tool_count=len(tools))
        return agent_executor

    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent.

        Returns:
            System prompt string
        """
        return """You are an AI assistant that helps users analyze and manage their Gmail emails.

You have access to several tools to search, retrieve, and analyze emails. Use these tools to answer the user's questions accurately.

Guidelines:
- When users ask about unread emails, use the list_unread tool
- When users ask "what is X saying?" or want emails from a specific person, use get_sender_emails tool
- When users ask about spending or transactions, search for relevant emails with keywords like "receipt", "invoice", "payment"
- Always provide concise, helpful summaries
- If you can't find information, let the user know clearly
- Format dates and times in a user-friendly way
- When searching, use appropriate Gmail query operators (from:, subject:, has:attachment, etc.)

Be helpful, accurate, and conversational in your responses."""

    def run(
        self,
        query: str,
        chat_history: Optional[list] = None
    ) -> str:
        """Run the agent with a query.

        Args:
            query: User query
            chat_history: Optional chat history for context

        Returns:
            Agent response
        """
        try:
            logger.info("Running agent", query=query)

            inputs = {"input": query}
            if chat_history:
                inputs["chat_history"] = chat_history

            result = self.agent_executor.invoke(inputs)
            response = result.get("output", "I couldn't process that request.")

            logger.info("Agent execution completed", response_length=len(response))
            return response

        except Exception as e:
            logger.error("Agent execution failed", error=str(e))
            return f"I encountered an error: {str(e)}"

    async def arun(
        self,
        query: str,
        chat_history: Optional[list] = None
    ) -> str:
        """Run the agent asynchronously.

        Args:
            query: User query
            chat_history: Optional chat history for context

        Returns:
            Agent response
        """
        try:
            logger.info("Running agent asynchronously", query=query)

            inputs = {"input": query}
            if chat_history:
                inputs["chat_history"] = chat_history

            result = await self.agent_executor.ainvoke(inputs)
            response = result.get("output", "I couldn't process that request.")

            logger.info("Async agent execution completed", response_length=len(response))
            return response

        except Exception as e:
            logger.error("Async agent execution failed", error=str(e))
            return f"I encountered an error: {str(e)}"


class SessionManager:
    """Manage agent sessions per conversation thread."""

    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, list] = {}

    def get_history(self, session_id: str) -> list:
        """Get chat history for a session.

        Args:
            session_id: Session identifier

        Returns:
            Chat history list
        """
        return self.sessions.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add message to session history.

        Args:
            session_id: Session identifier
            role: Message role (human/ai)
            content: Message content
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        from langchain.schema import HumanMessage, AIMessage

        message = HumanMessage(content=content) if role == "human" else AIMessage(content=content)
        self.sessions[session_id].append(message)

        logger.debug("Added message to session", session_id=session_id, role=role)

    def clear_session(self, session_id: str) -> None:
        """Clear session history.

        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info("Cleared session", session_id=session_id)

    def clear_all_sessions(self) -> None:
        """Clear all sessions."""
        self.sessions.clear()
        logger.info("Cleared all sessions")
