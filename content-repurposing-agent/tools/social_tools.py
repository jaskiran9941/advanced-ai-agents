"""
Social media platform API integration tools.

✅ REAL MULTI-AGENT VALUE: Each platform has different APIs, auth, and posting requirements.
This is genuine infrastructure that LLMs alone cannot handle.
"""
import requests
from typing import Dict, Any, Optional, List
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("social_tools")

# =============================================================================
# TWITTER / X POSTING
# =============================================================================

def post_to_twitter(text: str, media_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Post a tweet to Twitter/X.

    Args:
        text: Tweet text (max 280 chars)
        media_ids: Optional list of uploaded media IDs

    Returns:
        Response with tweet ID and URL
    """
    # Try OAuth 2.0 first (from account linking)
    from auth.oauth_manager import oauth_manager

    if oauth_manager.is_linked('twitter'):
        logger.info("Using OAuth 2.0 linked account for Twitter")
        try:
            import tweepy

            # Get OAuth 2.0 access token
            token_data = oauth_manager.get_token('twitter')
            if not token_data:
                logger.error("Twitter account linked but no valid token")
                return {"success": False, "error": "No valid Twitter token"}

            access_token = token_data['access_token']

            # Authenticate with OAuth 2.0
            client = tweepy.Client(bearer_token=access_token)

            # Ensure text is a string, not an array
            if isinstance(text, list):
                logger.warning(f"Tweet text is a list, converting to string: {text}")
                text = text[0] if text else ""

            # Convert to string if needed
            text = str(text)

            logger.info(f"Posting tweet with text (length={len(text)}): {text[:100]}...")

            # Post tweet
            response = client.create_tweet(
                text=text,
                user_auth=False  # Using app-only auth with OAuth 2.0 bearer token
            )

            tweet_id = response.data['id']
            logger.info(f"Posted tweet successfully: {tweet_id}")

            return {
                "success": True,
                "tweet_id": tweet_id,
                "url": f"https://twitter.com/user/status/{tweet_id}",
                "text": text
            }

        except Exception as e:
            logger.error(f"Twitter OAuth 2.0 posting failed: {str(e)}")
            return {"success": False, "error": str(e)}

    # Fallback to old API v1.1 credentials
    if not settings.twitter.bearer_token:
        logger.warning("Twitter API not configured, using mock")
        return _mock_twitter_post(text)

    try:
        import tweepy

        # Authenticate with old credentials
        client = tweepy.Client(
            bearer_token=settings.twitter.bearer_token,
            consumer_key=settings.twitter.api_key,
            consumer_secret=settings.twitter.api_secret,
            access_token=settings.twitter.access_token,
            access_token_secret=settings.twitter.access_secret
        )

        # Post tweet
        response = client.create_tweet(
            text=text,
            media_ids=media_ids
        )

        tweet_id = response.data['id']
        logger.info(f"Posted tweet: {tweet_id}")

        return {
            "success": True,
            "tweet_id": tweet_id,
            "url": f"https://twitter.com/user/status/{tweet_id}",
            "text": text
        }

    except Exception as e:
        logger.error(f"Twitter posting failed: {str(e)}")
        return {"success": False, "error": str(e)}

def post_twitter_thread(tweets: List[str]) -> Dict[str, Any]:
    """
    Post a thread of tweets.

    Args:
        tweets: List of tweet texts

    Returns:
        Response with thread details
    """
    # Try OAuth 2.0 first (from account linking)
    from auth.oauth_manager import oauth_manager

    if oauth_manager.is_linked('twitter'):
        logger.info("Using OAuth 2.0 linked account for Twitter thread")
        try:
            import tweepy

            # Get OAuth 2.0 access token
            token_data = oauth_manager.get_token('twitter')
            if not token_data:
                logger.error("Twitter account linked but no valid token")
                return {"success": False, "error": "No valid Twitter token"}

            access_token = token_data['access_token']

            # Authenticate with OAuth 2.0
            client = tweepy.Client(bearer_token=access_token)

            tweet_ids = []
            previous_id = None

            for i, text in enumerate(tweets):
                response = client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=previous_id,
                    user_auth=False
                )

                tweet_id = response.data['id']
                tweet_ids.append(tweet_id)
                previous_id = tweet_id

                logger.info(f"Posted tweet {i+1}/{len(tweets)}: {tweet_id}")

            return {
                "success": True,
                "thread_length": len(tweets),
                "tweet_ids": tweet_ids,
                "thread_url": f"https://twitter.com/user/status/{tweet_ids[0]}"
            }

        except Exception as e:
            logger.error(f"Twitter OAuth 2.0 thread posting failed: {str(e)}")
            return {"success": False, "error": str(e)}

    # Fallback to old API v1.1 credentials
    if not settings.twitter.bearer_token:
        logger.warning("Twitter API not configured, using mock")
        return _mock_twitter_thread(tweets)

    try:
        import tweepy

        client = tweepy.Client(
            bearer_token=settings.twitter.bearer_token,
            consumer_key=settings.twitter.api_key,
            consumer_secret=settings.twitter.api_secret,
            access_token=settings.twitter.access_token,
            access_token_secret=settings.twitter.access_secret
        )

        tweet_ids = []
        previous_id = None

        for i, text in enumerate(tweets):
            response = client.create_tweet(
                text=text,
                in_reply_to_tweet_id=previous_id
            )

            tweet_id = response.data['id']
            tweet_ids.append(tweet_id)
            previous_id = tweet_id

            logger.info(f"Posted tweet {i+1}/{len(tweets)}: {tweet_id}")

        return {
            "success": True,
            "thread_length": len(tweets),
            "tweet_ids": tweet_ids,
            "thread_url": f"https://twitter.com/user/status/{tweet_ids[0]}"
        }

    except Exception as e:
        logger.error(f"Twitter thread posting failed: {str(e)}")
        return {"success": False, "error": str(e)}

# =============================================================================
# LINKEDIN POSTING
# =============================================================================

def post_to_linkedin(text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Post to LinkedIn.

    Args:
        text: Post text
        image_url: Optional image URL

    Returns:
        Response with post ID and URL
    """
    # Try OAuth 2.0 first (from account linking)
    from auth.oauth_manager import oauth_manager

    if oauth_manager.is_linked('linkedin'):
        logger.info("Using OAuth 2.0 linked account for LinkedIn")
        try:
            # Get OAuth 2.0 access token
            token_data = oauth_manager.get_token('linkedin')
            if not token_data:
                logger.error("LinkedIn account linked but no valid token")
                return {"success": False, "error": "No valid LinkedIn token"}

            access_token = token_data['access_token']

            # Headers with OAuth token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Get user profile (using userinfo endpoint for OpenID Connect)
            profile_response = requests.get(
                "https://api.linkedin.com/v2/userinfo",
                headers=headers
            )
            profile_response.raise_for_status()
            user_data = profile_response.json()
            user_sub = user_data.get("sub")  # User ID from OpenID Connect

            logger.info(f"LinkedIn user sub: {user_sub}")

            # Create post using LinkedIn Share API
            post_data = {
                "author": f"urn:li:person:{user_sub}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # Add image if provided
            if image_url:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "originalUrl": image_url
                }]

            post_response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers=headers,
                json=post_data
            )
            post_response.raise_for_status()

            post_id = post_response.json()["id"]
            logger.info(f"Posted to LinkedIn: {post_id}")

            return {
                "success": True,
                "post_id": post_id,
                "url": f"https://www.linkedin.com/feed/update/{post_id}",
                "text": text
            }

        except Exception as e:
            logger.error(f"LinkedIn OAuth 2.0 posting failed: {str(e)}")
            return {"success": False, "error": str(e)}

    # Fallback to old API credentials
    if not settings.linkedin.access_token:
        logger.warning("LinkedIn API not configured, using mock")
        return _mock_linkedin_post(text)

    try:
        # Get user URN
        headers = {
            "Authorization": f"Bearer {settings.linkedin.access_token}",
            "Content-Type": "application/json"
        }

        # Get user profile
        profile_response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers=headers
        )
        profile_response.raise_for_status()
        user_urn = profile_response.json()["id"]

        # Create post
        post_data = {
            "author": f"urn:li:person:{user_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # Add image if provided
        if image_url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                "status": "READY",
                "originalUrl": image_url
            }]

        post_response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=post_data
        )
        post_response.raise_for_status()

        post_id = post_response.json()["id"]
        logger.info(f"Posted to LinkedIn: {post_id}")

        return {
            "success": True,
            "post_id": post_id,
            "url": f"https://www.linkedin.com/feed/update/{post_id}",
            "text": text
        }

    except Exception as e:
        logger.error(f"LinkedIn posting failed: {str(e)}")
        return {"success": False, "error": str(e)}

# =============================================================================
# INSTAGRAM POSTING
# =============================================================================

def post_to_instagram(caption: str, image_path: str) -> Dict[str, Any]:
    """
    Post to Instagram.

    Args:
        caption: Post caption
        image_path: Path to image file

    Returns:
        Response with post details
    """
    if not settings.instagram.username:
        logger.warning("Instagram API not configured, using mock")
        return _mock_instagram_post(caption)

    try:
        from instagrapi import Client

        client = Client()
        client.login(settings.instagram.username, settings.instagram.password)

        # Upload photo
        media = client.photo_upload(
            image_path,
            caption=caption
        )

        logger.info(f"Posted to Instagram: {media.pk}")

        return {
            "success": True,
            "media_id": media.pk,
            "url": f"https://www.instagram.com/p/{media.code}/",
            "caption": caption
        }

    except Exception as e:
        logger.error(f"Instagram posting failed: {str(e)}")
        return {"success": False, "error": str(e)}

# =============================================================================
# SUBSTACK PUBLISHING
# =============================================================================

def publish_to_substack(title: str, content: str, subtitle: Optional[str] = None) -> Dict[str, Any]:
    """
    Publish article to Substack.

    Args:
        title: Article title
        content: Article content (HTML or markdown)
        subtitle: Optional subtitle

    Returns:
        Response with publication details
    """
    if not settings.substack.api_key:
        logger.warning("Substack API not configured, using mock")
        return _mock_substack_publish(title, content)

    try:
        headers = {
            "Authorization": f"Bearer {settings.substack.api_key}",
            "Content-Type": "application/json"
        }

        post_data = {
            "title": title,
            "subtitle": subtitle or "",
            "body": content,
            "publication_id": settings.substack.publication_id,
            "type": "newsletter"
        }

        response = requests.post(
            "https://substack.com/api/v1/posts",
            headers=headers,
            json=post_data
        )
        response.raise_for_status()

        data = response.json()
        post_id = data.get("id")

        logger.info(f"Published to Substack: {post_id}")

        return {
            "success": True,
            "post_id": post_id,
            "url": data.get("canonical_url", ""),
            "title": title
        }

    except Exception as e:
        logger.error(f"Substack publishing failed: {str(e)}")
        return {"success": False, "error": str(e)}

# =============================================================================
# MOCK FUNCTIONS (for testing without API keys)
# =============================================================================

def _mock_twitter_post(text: str) -> Dict[str, Any]:
    """Mock Twitter posting for testing."""
    logger.info(f"[MOCK] Would post tweet: {text[:50]}...")
    return {
        "success": True,
        "tweet_id": "mock_12345",
        "url": "https://twitter.com/user/status/mock_12345",
        "text": text,
        "mock": True
    }

def _mock_twitter_thread(tweets: List[str]) -> Dict[str, Any]:
    """Mock Twitter thread for testing."""
    logger.info(f"[MOCK] Would post thread with {len(tweets)} tweets")
    return {
        "success": True,
        "thread_length": len(tweets),
        "tweet_ids": [f"mock_{i}" for i in range(len(tweets))],
        "thread_url": "https://twitter.com/user/status/mock_0",
        "mock": True
    }

def _mock_linkedin_post(text: str) -> Dict[str, Any]:
    """Mock LinkedIn posting for testing."""
    logger.info(f"[MOCK] Would post to LinkedIn: {text[:50]}...")
    return {
        "success": True,
        "post_id": "mock_linkedin_123",
        "url": "https://www.linkedin.com/feed/update/mock_linkedin_123",
        "text": text,
        "mock": True
    }

def _mock_instagram_post(caption: str) -> Dict[str, Any]:
    """Mock Instagram posting for testing."""
    logger.info(f"[MOCK] Would post to Instagram: {caption[:50]}...")
    return {
        "success": True,
        "media_id": "mock_ig_123",
        "url": "https://www.instagram.com/p/mock_code/",
        "caption": caption,
        "mock": True
    }

def _mock_substack_publish(title: str, content: str) -> Dict[str, Any]:
    """Mock Substack publishing for testing."""
    logger.info(f"[MOCK] Would publish to Substack: {title}")
    return {
        "success": True,
        "post_id": "mock_substack_123",
        "url": "https://yoursubstack.substack.com/p/mock-post",
        "title": title,
        "mock": True
    }
