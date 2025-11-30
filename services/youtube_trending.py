import requests
import re
from typing import List, Dict
from .text_handler_adv import classify_by_embedding

API_KEY = os.getenv("YOUTUBE_API_TOKEN")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CATEGORIES_API_URL = "https://www.googleapis.com/youtube/v3/videoCategories"

MUSIC_CATEGORY_ID = "10"


def clean_description(text: str) -> str:
    """Удаляет из текста все URL (http/https/www) и лишние пробелы."""
    if not text:
        return ""
    url_pattern = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
    cleaned = url_pattern.sub("", text)
    return cleaned.strip()


def get_category_name_by_id(category_id: str, region: str = "GB") -> str:
    """
    Возвращает название категории по её ID.
    :param category_id: ID категории YouTube
    :param region: региональный код для фильтрации категорий (ISO 3166‑1 alpha‑2)
    :return: название категории или ID, если не найдено
    """
    params = {"part": "snippet", "regionCode": region, "key": API_KEY}
    resp = requests.get(YOUTUBE_CATEGORIES_API_URL, params=params)
    resp.raise_for_status()
    data = resp.json()

    for item in data.get("items", []):
        if item.get("id") == category_id:
            return item.get("snippet", {}).get("title", category_id)

    return category_id


def get_trending_videos_non_music(
    region: str = "GB", max_results: int = 20
) -> List[Dict]:
    """
    Возвращает список трендовых видео, исключая музыкальную категорию.
    :param region: региональный код (ISO 3166‑1 alpha‑2), например 'US', 'RU'
    :param max_results: сколько видео запрашивать (максимум 50)
    :return: список словарей с данными видео (без музыки)
    """
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "key": API_KEY,
    }
    resp = requests.get(YOUTUBE_API_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("items", [])
    videos: List[Dict] = []

    category_cache = {}

    for item in items:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        category_id = snippet.get("categoryId")

        if category_id == MUSIC_CATEGORY_ID:
            continue

        if category_id not in category_cache:
            category_name = get_category_name_by_id(category_id, region)
            category_cache[category_id] = category_name
        else:
            category_name = category_cache[category_id]

        theme = classify_by_embedding(clean_description(snippet.get("description", "")))

        videos.append(
            {
                "Title": snippet.get("title"),
                "Theme": theme[0],
                "ChannelTitle": snippet.get("channelTitle"),
                "PublishedAt": snippet.get("publishedAt"),
                "ViewCount": int(stats.get("viewCount", 0)),
                "LikeCount": int(stats.get("likeCount", 0))
                if stats.get("likeCount")
                else None,
                "CommentCount": int(stats.get("commentCount", 0))
                if stats.get("commentCount")
                else None,
                "Category": category_name,
            }
        )
    airtable_records = [{"fields": video} for video in videos]
    return airtable_records


if __name__ == "__main__":
    trending = get_trending_videos_non_music(region="GB", max_results=25)
    for video in trending:
        print(video)
