"""
Simple test to demonstrate mock data working without API keys.
"""
from agents.seo_agent import SEOResearchAgent
from agents.writer_agent import ContentWriterAgent

def main():
    print("="*80)
    print("TESTING MOCK DATA (No API Keys Required)")
    print("="*80)
    print()

    # Test SEO Agent
    print("1. Testing SEO Research Agent with Mock Data...")
    print("-"*80)
    seo_agent = SEOResearchAgent(llm_provider="claude")
    seo_results = seo_agent.research_topic("The Future of AI in Climate Change Solutions")

    print("Primary Keywords:", seo_results.get("primary_keywords", []))
    print("Hashtags:", seo_results.get("hashtags", []))
    print()

    # Test Content Writer
    print("2. Testing Content Writer Agent with Mock Data...")
    print("-"*80)
    writer_agent = ContentWriterAgent(llm_provider="claude")

    # Test LinkedIn content
    linkedin_content = writer_agent.write_linkedin_post(
        topic="The Future of AI in Climate Change Solutions",
        keywords=seo_results.get("primary_keywords", [])
    )

    print("LinkedIn Content Preview:")
    print(linkedin_content[:300] + "...")
    print()

    # Test Twitter content
    twitter_content = writer_agent.write_twitter_thread(
        topic="The Future of AI in Climate Change Solutions",
        keywords=seo_results.get("primary_keywords", [])
    )

    print("Twitter Thread Preview:")
    if isinstance(twitter_content, list) and len(twitter_content) > 0:
        print(f"Tweet 1: {twitter_content[0][:100]}...")
    elif isinstance(twitter_content, str):
        preview = twitter_content[:200]
        print(preview + "..." if len(twitter_content) > 200 else preview)
    else:
        print(f"Type: {type(twitter_content)}, Value: {str(twitter_content)[:100]}")
    print()

    print("="*80)
    print("✅ Mock data is working! All agents can run without API keys.")
    print("   Add real API keys to .env file to get actual AI-generated content.")
    print("="*80)

if __name__ == "__main__":
    main()
