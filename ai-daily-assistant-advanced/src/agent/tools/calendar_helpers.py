"""Custom calendar helper tools that use Composio's managed auth."""

from typing import Optional
from datetime import datetime, timedelta
from .registry import Tool, ToolRegistry
from .composio_tools import get_composio_toolset
import structlog

logger = structlog.get_logger()


class CalendarHelpers:
    """Custom calendar tools using Composio's authentication."""

    def __init__(self, entity_id: str = "default"):
        """Initialize with Composio toolset."""
        self.toolset = get_composio_toolset()
        self.entity_id = entity_id

    def find_next_free_slot(self, duration_minutes: int = 30) -> str:
        """Find the next available time slot in calendar.

        Args:
            duration_minutes: Desired meeting duration

        Returns:
            Next available time slot
        """
        if not self.toolset:
            return "Calendar integration not configured. Enable Composio integration in settings."

        try:
            # Use Composio's GOOGLECALENDAR_FIND_FREE_SLOTS action
            result = self.toolset.execute_action(
                action="GOOGLECALENDAR_FIND_FREE_SLOTS",
                params={
                    "time_min": datetime.now().isoformat(),
                    "time_max": (datetime.now() + timedelta(days=7)).isoformat(),
                    "duration": duration_minutes
                },
                entity_id=self.entity_id
            )

            logger.info("Found free calendar slots", result=result)
            return f"Next available slot: {result}"

        except Exception as e:
            logger.error("Failed to find free slot", error=str(e))
            return f"Error finding free slot: {str(e)}\n\nMake sure you've connected your Google Calendar via Composio."

    def summarize_todays_meetings(self) -> str:
        """Get summary of today's meetings.

        Returns:
            Summary of today's calendar
        """
        if not self.toolset:
            return "Calendar integration not configured. Enable Composio integration in settings."

        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0)
            today_end = today_start + timedelta(days=1)

            result = self.toolset.execute_action(
                action="GOOGLECALENDAR_LIST_EVENTS",
                params={
                    "calendar_id": "primary",
                    "time_min": today_start.isoformat(),
                    "time_max": today_end.isoformat(),
                    "order_by": "startTime"
                },
                entity_id=self.entity_id
            )

            logger.info("Retrieved today's meetings", result=result)

            # Format the result
            if isinstance(result, dict) and "items" in result:
                events = result["items"]
                if not events:
                    return "📅 No meetings scheduled for today."

                summary = f"📅 Today's Meetings ({len(events)} total):\n\n"
                for i, event in enumerate(events[:10], 1):  # Limit to 10
                    title = event.get("summary", "Untitled")
                    start = event.get("start", {}).get("dateTime", "")
                    try:
                        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        time_str = start_time.strftime("%I:%M %p")
                    except:
                        time_str = "Time TBD"

                    summary += f"{i}. {time_str}: {title}\n"

                return summary
            else:
                return f"Today's calendar: {result}"

        except Exception as e:
            logger.error("Failed to get today's meetings", error=str(e))
            return f"Error retrieving meetings: {str(e)}\n\nMake sure you've connected your Google Calendar via Composio."


def register_calendar_helpers(registry: ToolRegistry, entity_id: str = "default") -> None:
    """Register custom calendar helper tools.

    Args:
        registry: Tool registry
        entity_id: Composio entity ID for OAuth
    """
    helpers = CalendarHelpers(entity_id)

    registry.register(Tool(
        name="find_next_free_slot",
        description=(
            "Find the next available time slot in your Google Calendar. "
            "Searches the next 7 days for free time slots of specified duration. "
            "Requires Composio Google Calendar integration."
        ),
        parameters={
            "duration_minutes": {
                "type": "integer",
                "description": "Meeting duration in minutes (default: 30)",
                "default": 30
            }
        },
        function=helpers.find_next_free_slot
    ))

    registry.register(Tool(
        name="summarize_todays_meetings",
        description=(
            "Get a summary of today's meetings and schedule from Google Calendar. "
            "Shows all meetings scheduled for today with times and titles. "
            "Requires Composio Google Calendar integration."
        ),
        parameters={},
        function=helpers.summarize_todays_meetings
    ))

    logger.info("Registered calendar helper tools", count=2)
