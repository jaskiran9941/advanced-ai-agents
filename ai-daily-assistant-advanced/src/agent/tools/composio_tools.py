"""Composio integration for third-party tools."""

from typing import List, Any, Optional
from src.config.settings import settings
import structlog

logger = structlog.get_logger()


def get_composio_toolset() -> Optional[Any]:
    """Initialize Composio toolset if enabled."""
    if not settings.composio.enabled:
        logger.info("Composio integration disabled")
        return None

    if not settings.composio.api_key:
        logger.warning("Composio API key not configured")
        return None

    try:
        from composio_langchain import ComposioToolSet

        toolset = ComposioToolSet(api_key=settings.composio.api_key)
        logger.info("Initialized Composio toolset")
        return toolset
    except ImportError:
        logger.warning("composio-langchain not installed. Install with: pip install composio-langchain")
        return None
    except Exception as e:
        logger.error("Failed to initialize Composio", error=str(e))
        return None


def get_composio_tools(
    entity_id: Optional[str] = None,
    apps: Optional[List[str]] = None
) -> List[Any]:
    """Get Composio tools for specified apps.

    Args:
        entity_id: User entity ID for OAuth (default from settings)
        apps: List of app names (default from settings)

    Returns:
        List of LangChain-compatible tools
    """
    toolset = get_composio_toolset()
    if not toolset:
        return []

    entity_id = entity_id or settings.composio.entity_id
    app_names = apps or settings.composio.apps

    try:
        from composio_langchain import App

        # Convert app names to App enum
        app_enums = []
        for app_name in app_names:
            try:
                app_enums.append(App[app_name])
            except KeyError:
                logger.warning(f"Unknown Composio app: {app_name}")
                continue

        if not app_enums:
            logger.warning("No valid Composio apps configured")
            return []

        # Get tools from Composio
        tools = toolset.get_tools(apps=app_enums, entity_id=entity_id)

        logger.info(
            "Retrieved Composio tools",
            count=len(tools),
            apps=app_names,
            entity_id=entity_id
        )

        return tools

    except Exception as e:
        logger.error("Failed to get Composio tools", error=str(e))
        return []


def initiate_composio_connection(
    app_name: str,
    entity_id: str,
    redirect_url: str = "http://localhost:8501/oauth/callback"
) -> Optional[str]:
    """Initiate OAuth connection for a Composio app.

    Args:
        app_name: Name of the app (e.g., "GOOGLECALENDAR")
        entity_id: User entity ID
        redirect_url: OAuth callback URL

    Returns:
        Authorization URL for user to visit, or None if failed
    """
    toolset = get_composio_toolset()
    if not toolset:
        return None

    try:
        from composio_langchain import App

        app = App[app_name]
        connection_request = toolset.initiate_connection(
            redirect_url=redirect_url,
            entity_id=entity_id,
            app=app
        )

        logger.info(
            "Initiated Composio connection",
            app=app_name,
            entity_id=entity_id,
            auth_url=connection_request.redirectUrl
        )

        return connection_request.redirectUrl

    except Exception as e:
        logger.error("Failed to initiate connection", error=str(e))
        return None
