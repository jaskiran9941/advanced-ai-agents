#!/usr/bin/env python3
"""
Test script to verify multi-agent workflow works end-to-end.
"""

import os
import sys
from dotenv import load_dotenv
from orchestrator.orchestrator_agent import OrchestratorAgent

def test_workflow():
    """Test the full multi-agent workflow."""

    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment or use test key
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        # For testing code structure only - will fail on actual API call
        print("⚠️  No API key found - using test mode (will fail on API calls)")
        print("   To test with real API: export OPENAI_API_KEY='your-key-here'\n")
        api_key = "test-key-for-structural-testing"

    print("✅ API Key found")
    print("\n" + "="*60)
    print("Testing Multi-Agent Podcast System")
    print("="*60 + "\n")

    try:
        # Initialize orchestrator
        print("1️⃣ Initializing Orchestrator Agent...")
        orchestrator = OrchestratorAgent(api_key)
        print("   ✅ Orchestrator initialized\n")

        # Test workflow
        user_id = "test_user"
        user_goal = "Find me AI and technology podcasts"

        print(f"2️⃣ Executing workflow for: '{user_goal}'")
        print(f"   User ID: {user_id}\n")

        result = orchestrator.execute(user_id, user_goal)

        print("\n" + "="*60)
        print("WORKFLOW RESULT")
        print("="*60 + "\n")

        if result.get("success"):
            print("✅ SUCCESS! Workflow completed\n")

            # Show agent sequence
            agent_seq = result.get("agent_sequence", [])
            print(f"🔄 Agent Sequence: {' → '.join([a.title() for a in agent_seq])}\n")

            # Show each agent's output
            agent_outputs = result.get("agent_outputs", {})
            for agent_name in agent_seq:
                print(f"\n📦 {agent_name.upper()} AGENT OUTPUT:")
                print("-" * 40)
                output = agent_outputs.get(agent_name, {})
                for key, value in output.items():
                    print(f"  {key}: {value}")

            # Final result
            print("\n🎯 FINAL RESULT:")
            print("-" * 40)
            final = result.get("final_result", {})
            for key, value in final.items():
                print(f"  {key}: {value}")

            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED!")
            print("="*60)
            return True

        else:
            print(f"❌ WORKFLOW FAILED: {result.get('error', 'Unknown error')}")
            print(f"\n📋 Agent outputs so far:")
            agent_outputs = result.get("agent_outputs", {})
            for agent_name, output in agent_outputs.items():
                print(f"  - {agent_name}: {output}")
            return False

    except Exception as e:
        print(f"\n❌ ERROR during workflow execution:")
        print(f"   {str(e)}\n")

        import traceback
        print("Full traceback:")
        print("-" * 60)
        traceback.print_exc()
        print("-" * 60)

        return False

if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)
