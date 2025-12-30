"""
Example script showing how to use the Content Repurposing Agent System.

This demonstrates the multi-agent architecture in action.
"""
from agents.orchestrator import ContentOrchestrator
import json

def main():
    print("=" * 80)
    print("CONTENT REPURPOSING AGENT SYSTEM - Example")
    print("=" * 80)
    print()

    # Initialize orchestrator
    print("Initializing orchestrator with 9 specialized agents...")
    orchestrator = ContentOrchestrator()
    print("✅ Orchestrator ready\n")

    # Check agent status
    print("Agent Status:")
    status = orchestrator.get_agent_status()
    for agent_name, agent_info in status["agents"].items():
        print(f"  - {agent_name}: {agent_info['model_id']}")
    print()

    # Example topic
    topic = "The Future of AI in Climate Change Solutions"
    platforms = ["linkedin", "twitter"]

    print(f"Topic: {topic}")
    print(f"Target Platforms: {', '.join(platforms)}")
    print()

    # Option 1: Generate content only (for preview)
    print("-" * 80)
    print("Option 1: GENERATE CONTENT ONLY (Preview Mode)")
    print("-" * 80)
    print()

    results = orchestrator.generate_content_only(
        topic=topic,
        platforms=platforms,
        include_seo=True
    )

    print("✅ Content generated!")
    print()
    print("SEO Keywords:", results.get("seo", {}).get("primary_keywords", []))
    print()

    for platform in platforms:
        content = results["content"].get(platform, "")
        print(f"--- {platform.upper()} ---")
        print(content[:200] + "..." if len(content) > 200 else content)
        print()

    # Option 2: Full pipeline with publishing
    print("-" * 80)
    print("Option 2: FULL PIPELINE (Generate + Publish)")
    print("-" * 80)
    print()
    print("NOTE: Running in DRY RUN mode (won't actually post)")
    print()

    full_results = orchestrator.run_full_pipeline(
        topic=topic,
        platforms=platforms,
        enable_editing=False,  # Skip editing for faster demo
        enable_images=True,
        dry_run=True  # Don't actually post to platforms
    )

    print(f"✅ Pipeline completed in {full_results['duration_seconds']:.2f} seconds")
    print()

    # Show publishing results
    if "publishing" in full_results.get("steps", {}):
        print("Publishing Results:")
        for platform, result in full_results["steps"]["publishing"].items():
            if result.get("success"):
                print(f"  ✅ {platform}: {result.get('url', 'Posted (mock)')}")
            else:
                print(f"  ❌ {platform}: {result.get('error', 'Failed')}")
    print()

    # Save full results to file
    output_file = "example_results.json"
    with open(output_file, 'w') as f:
        json.dump(full_results, f, indent=2)

    print(f"📄 Full results saved to: {output_file}")
    print()

    print("=" * 80)
    print("AGENT ARCHITECTURE SUMMARY")
    print("=" * 80)
    print("""
✅ REAL MULTI-AGENT VALUE:
   - SEO Research Agent: Calls external SEO APIs for real-time data
   - Image Generator Agent: Calls DALL-E/SD APIs (LLMs can't generate images)
   - Platform Agents (4x): Each handles different API + formatting
   - Orchestrator: Manages workflow, parallelization, error handling

🔄 SEMI-REAL VALUE:
   - Editor Agent: Iterative refinement improves quality

⚠️ EDUCATIONAL SEPARATION:
   - Content Writer Agent: Could be done in one LLM call, separated for learning

This demonstrates WHEN multi-agent adds real value vs when it's educational!
    """)

if __name__ == "__main__":
    main()
