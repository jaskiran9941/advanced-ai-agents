#!/usr/bin/env python3
"""Verification script for WhatsApp Fix + Hybrid Tool implementation."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_settings_import():
    """Test that settings can be imported without requiring all credentials."""
    print("✓ Testing settings import...")
    try:
        from src.config.settings import settings
        print(f"  ✅ Settings imported successfully")
        print(f"  - Slack bot_token: {'SET' if settings.slack.bot_token else 'NOT SET (OK)'}")
        print(f"  - Composio enabled: {settings.composio.enabled}")
        print(f"  - Composio apps: {settings.composio.apps}")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_tools_import():
    """Test that all new tools can be imported."""
    print("\n✓ Testing tools import...")
    try:
        from src.agent.tools import (
            ToolRegistry,
            register_email_tools,
            register_financial_tools,
            register_calendar_helpers,
            get_composio_tools,
            initiate_composio_connection
        )
        print(f"  ✅ All tools imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_tool_registration():
    """Test tool registration without Gmail client."""
    print("\n✓ Testing tool registration...")
    try:
        from src.agent.tools import ToolRegistry
        
        registry = ToolRegistry()
        initial_count = len(registry.get_all_tools())
        print(f"  ✅ ToolRegistry created (initial tools: {initial_count})")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_composio_tools():
    """Test Composio tools loading."""
    print("\n✓ Testing Composio tools...")
    try:
        from src.agent.tools import get_composio_tools
        from src.config.settings import settings
        
        if not settings.composio.enabled:
            print(f"  ℹ️  Composio disabled (expected - set COMPOSIO_ENABLED=true to enable)")
            tools = get_composio_tools()
            print(f"  ✅ get_composio_tools() returns empty list: {len(tools) == 0}")
        else:
            tools = get_composio_tools()
            print(f"  ✅ Composio tools loaded: {len(tools)}")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_session_manager():
    """Test SessionManager with cleanup."""
    print("\n✓ Testing SessionManager...")
    try:
        from src.agent.runner import SessionManager
        
        sm = SessionManager(session_ttl_hours=24, max_sessions=1000)
        sm.add_message("test_session", "human", "Hello")
        sm.add_message("test_session", "ai", "Hi there!")
        
        history = sm.get_history("test_session")
        print(f"  ✅ SessionManager created with cleanup")
        print(f"  - Messages in session: {len(history)}")
        print(f"  - TTL: 24 hours, Max sessions: 1000")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def test_message_splitting():
    """Test WhatsApp message splitting."""
    print("\n✓ Testing message splitting...")
    try:
        from src.whatsapp.webhook import _split_message
        
        # Test short message
        short = "Hello world"
        chunks = _split_message(short, max_length=1600)
        assert len(chunks) == 1, "Short message should be 1 chunk"
        
        # Test long message
        long = "Paragraph 1\n\n" * 100  # ~1300 chars
        chunks = _split_message(long, max_length=100)
        assert len(chunks) > 1, "Long message should be split"
        
        print(f"  ✅ Message splitting works correctly")
        print(f"  - Short message: 1 chunk")
        print(f"  - Long message: {len(chunks)} chunks")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("WhatsApp Fix + Hybrid Tool Implementation Verification")
    print("=" * 60)
    
    tests = [
        test_settings_import,
        test_tools_import,
        test_tool_registration,
        test_composio_tools,
        test_session_manager,
        test_message_splitting,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✅ All verification tests passed!")
        print("\nNext steps:")
        print("1. Update .env with your credentials")
        print("2. Test WhatsApp: python run_whatsapp.py")
        print("3. Test Streamlit: streamlit run streamlit_app_simple.py")
        print("4. (Optional) Enable Composio integration")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
