import requests
import os
from typing import List, Dict
from .text_handler import get_top_keyword


def get_posts(username: str, limit: int = 200) -> List[Dict]:
    """
    Get information about posts from a specific Reddit user.

    Args:
        username (str): The Reddit username to fetch posts from
        limit (int): Number of posts to retrieve (default: 10)

    Returns:
        List[Dict]: List of dictionaries containing post information in the format:
        {
            'title': post title,
            'platform': 'reddit',
            'keywords': extracted keywords from title and text,
            'likes': number of upvotes,
            'comments': number of comments
        }
    """
    # Validate input
    if not username:
        print("Error: username cannot be empty")
        return []

    url = f"https://www.reddit.com/user/{username}/submitted/.json"
    params = {"limit": limit}

    headers = {"User-Agent": os.environ.get("REDDIT_USER_AGENT", "rakuzan:1.0")}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()

        if "data" not in data or "children" not in data["data"]:
            print(f"Error: Unexpected response structure for user {username}")
            return []

        posts = []
        for post in data["data"]["children"]:
            submission = post["data"]

            text_content = (
                submission.get("title", "") + " " + submission.get("selftext", "")
            )
            if False:
                from .text_handler_adv import classify_by_embedding

                top_keyword = classify_by_embedding(text_content)
            else:
                top_keyword = get_top_keyword(text_content)

            post_data = {
                "Title": submission["title"],
                "Platform": "reddit",
                "Theme": top_keyword[0],
                "Likes": submission["score"],
                "Comments": submission["num_comments"],
            }
            posts.append(post_data)

        airtable_records = [{"fields": post} for post in posts]
        return airtable_records

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(f"Error: User {username} not found")
        else:
            print(f"HTTP Error fetching posts for user {username}: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching posts for user {username}: {e}")
        return []
    except KeyError as e:
        print(f"Error parsing response for user {username}: missing key {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching posts for user {username}: {e}")
        return []
