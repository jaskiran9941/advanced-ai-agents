"""Financial analysis tools for receipt and transaction extraction."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import re
from .registry import Tool, ToolRegistry
import structlog

logger = structlog.get_logger()


class FinancialTools:
    """Financial analysis tools for AI agent."""

    def __init__(self, gmail_client):
        """Initialize financial tools with Gmail client."""
        self.gmail = gmail_client

    def extract_receipts(self, days_back: int = 30) -> str:
        """Extract receipts from emails in the last N days.

        Args:
            days_back: Number of days to search back

        Returns:
            Summary of found receipts with amounts and vendors
        """
        try:
            # Search for receipt keywords
            query = (
                f'(receipt OR invoice OR "order confirmation" OR "payment received") '
                f'after:{(datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")}'
            )

            messages = self.gmail.list_messages(query=query, max_results=50)

            if not messages:
                return f"No receipts found in the last {days_back} days."

            receipts = []
            total_amount = 0.0

            for msg in messages[:20]:  # Limit to 20 for performance
                try:
                    full_msg = self.gmail.get_message(msg["id"])

                    # Extract receipt info
                    snippet = full_msg.get("snippet", "")

                    # Get headers
                    headers = full_msg.get("payload", {}).get("headers", [])
                    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
                    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
                    date_str = next((h["value"] for h in headers if h["name"] == "Date"), "")

                    # Extract amount (simple regex - looks for $ or USD amounts)
                    text_to_search = subject + " " + snippet
                    amount_patterns = [
                        r'\$(\d+(?:,\d{3})*\.?\d*)',  # $1,234.56
                        r'(\d+(?:,\d{3})*\.?\d*)\s*USD',  # 1234.56 USD
                        r'Total[:\s]+\$?(\d+(?:,\d{3})*\.?\d*)',  # Total: $1234.56
                    ]

                    amount = 0.0
                    for pattern in amount_patterns:
                        match = re.search(pattern, text_to_search, re.IGNORECASE)
                        if match:
                            amount_str = match.group(1).replace(',', '')
                            try:
                                amount = float(amount_str)
                                break
                            except ValueError:
                                continue

                    # Parse date
                    try:
                        date_obj = datetime.fromtimestamp(int(full_msg.get("internalDate", 0)) / 1000)
                    except:
                        date_obj = datetime.now()

                    # Extract vendor from sender
                    vendor = sender.split('<')[0].strip() if '<' in sender else sender
                    vendor = vendor[:50]  # Limit length

                    receipts.append({
                        "vendor": vendor,
                        "amount": amount,
                        "date": date_obj,
                        "subject": subject[:80]  # Truncate subject
                    })

                    if amount > 0:
                        total_amount += amount

                except Exception as e:
                    logger.debug(f"Error processing message: {e}")
                    continue

            # Format response
            if not receipts:
                return f"Found emails that might be receipts, but couldn't extract amount details."

            result = f"📊 Found {len(receipts)} receipts in the last {days_back} days:\n\n"

            # Show top 10 receipts
            for i, r in enumerate(receipts[:10], 1):
                date_str = r['date'].strftime('%b %d')
                if r['amount'] > 0:
                    result += f"{i}. {r['vendor']}: ${r['amount']:.2f} ({date_str})\n"
                else:
                    result += f"{i}. {r['vendor']}: Amount not detected ({date_str})\n"

            if len(receipts) > 10:
                result += f"\n...and {len(receipts) - 10} more receipts"

            if total_amount > 0:
                result += f"\n\n💰 Total detected spending: ${total_amount:.2f}"

            return result

        except Exception as e:
            logger.error("Failed to extract receipts", error=str(e))
            return f"Error extracting receipts: {str(e)}"

    def analyze_spending_by_vendor(self, days_back: int = 30) -> str:
        """Analyze spending grouped by vendor.

        Args:
            days_back: Number of days to analyze

        Returns:
            Spending breakdown by vendor
        """
        try:
            # Search for receipt keywords
            query = (
                f'(receipt OR invoice OR "order confirmation" OR "payment received") '
                f'after:{(datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")}'
            )

            messages = self.gmail.list_messages(query=query, max_results=50)

            if not messages:
                return f"No spending data found in the last {days_back} days."

            vendor_spending: Dict[str, float] = {}

            for msg in messages[:20]:
                try:
                    full_msg = self.gmail.get_message(msg["id"])
                    snippet = full_msg.get("snippet", "")
                    headers = full_msg.get("payload", {}).get("headers", [])
                    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
                    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")

                    # Extract amount
                    text_to_search = subject + " " + snippet
                    amount_patterns = [
                        r'\$(\d+(?:,\d{3})*\.?\d*)',
                        r'(\d+(?:,\d{3})*\.?\d*)\s*USD',
                        r'Total[:\s]+\$?(\d+(?:,\d{3})*\.?\d*)',
                    ]

                    amount = 0.0
                    for pattern in amount_patterns:
                        match = re.search(pattern, text_to_search, re.IGNORECASE)
                        if match:
                            amount_str = match.group(1).replace(',', '')
                            try:
                                amount = float(amount_str)
                                break
                            except ValueError:
                                continue

                    # Extract vendor
                    vendor = sender.split('<')[0].strip() if '<' in sender else sender
                    vendor = vendor[:50]

                    if amount > 0:
                        if vendor in vendor_spending:
                            vendor_spending[vendor] += amount
                        else:
                            vendor_spending[vendor] = amount

                except Exception as e:
                    logger.debug(f"Error processing message: {e}")
                    continue

            if not vendor_spending:
                return "No spending data could be extracted from receipts."

            # Sort by amount
            sorted_vendors = sorted(vendor_spending.items(), key=lambda x: x[1], reverse=True)

            result = f"📊 Spending by Vendor (last {days_back} days):\n\n"

            for i, (vendor, amount) in enumerate(sorted_vendors[:10], 1):
                result += f"{i}. {vendor}: ${amount:.2f}\n"

            total = sum(vendor_spending.values())
            result += f"\n💰 Total: ${total:.2f}"

            return result

        except Exception as e:
            logger.error("Failed to analyze spending", error=str(e))
            return f"Error analyzing spending: {str(e)}"

    def monthly_spending_report(self) -> str:
        """Generate monthly spending report.

        Returns:
            Monthly spending summary
        """
        try:
            # Get current month
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            query = (
                f'(receipt OR invoice OR "order confirmation" OR "payment received") '
                f'after:{month_start.strftime("%Y/%m/%d")}'
            )

            messages = self.gmail.list_messages(query=query, max_results=100)

            if not messages:
                return f"No spending data found for {month_start.strftime('%B %Y')}."

            total_amount = 0.0
            transaction_count = 0

            for msg in messages[:30]:
                try:
                    full_msg = self.gmail.get_message(msg["id"])
                    snippet = full_msg.get("snippet", "")
                    headers = full_msg.get("payload", {}).get("headers", [])
                    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")

                    # Extract amount
                    text_to_search = subject + " " + snippet
                    amount_patterns = [
                        r'\$(\d+(?:,\d{3})*\.?\d*)',
                        r'(\d+(?:,\d{3})*\.?\d*)\s*USD',
                        r'Total[:\s]+\$?(\d+(?:,\d{3})*\.?\d*)',
                    ]

                    amount = 0.0
                    for pattern in amount_patterns:
                        match = re.search(pattern, text_to_search, re.IGNORECASE)
                        if match:
                            amount_str = match.group(1).replace(',', '')
                            try:
                                amount = float(amount_str)
                                break
                            except ValueError:
                                continue

                    if amount > 0:
                        total_amount += amount
                        transaction_count += 1

                except Exception as e:
                    logger.debug(f"Error processing message: {e}")
                    continue

            result = f"📊 Monthly Spending Report - {month_start.strftime('%B %Y')}\n\n"
            result += f"💰 Total Spending: ${total_amount:.2f}\n"
            result += f"📈 Transactions: {transaction_count}\n"

            if transaction_count > 0:
                avg_transaction = total_amount / transaction_count
                result += f"📊 Average Transaction: ${avg_transaction:.2f}"

            return result

        except Exception as e:
            logger.error("Failed to generate monthly report", error=str(e))
            return f"Error generating report: {str(e)}"


def register_financial_tools(registry: ToolRegistry, gmail_client) -> None:
    """Register financial analysis tools.

    Args:
        registry: Tool registry
        gmail_client: Gmail client for email access
    """
    tools = FinancialTools(gmail_client)

    registry.register(Tool(
        name="extract_receipts",
        description=(
            "Extract receipts from emails to analyze spending. "
            "Finds receipts, invoices, and order confirmations from the last N days. "
            "Extracts vendor names and amounts."
        ),
        parameters={
            "days_back": {
                "type": "integer",
                "description": "Number of days to search (default: 30)",
                "default": 30
            }
        },
        function=tools.extract_receipts
    ))

    registry.register(Tool(
        name="analyze_spending_by_vendor",
        description=(
            "Analyze spending grouped by vendor from email receipts. "
            "Shows total spending per vendor for the specified time period."
        ),
        parameters={
            "days_back": {
                "type": "integer",
                "description": "Number of days to analyze (default: 30)",
                "default": 30
            }
        },
        function=tools.analyze_spending_by_vendor
    ))

    registry.register(Tool(
        name="monthly_spending_report",
        description=(
            "Generate a monthly spending report from email receipts. "
            "Shows total spending, transaction count, and average transaction for current month."
        ),
        parameters={},
        function=tools.monthly_spending_report
    ))

    logger.info("Registered financial tools", count=3)
