import os
from googleapiclient.discovery import build
from typing import List, Dict
import re
from .text_handler_adv import classify_by_embedding

API_KEY = os.getenv("YOUTUBE_API_TOKEN")
YOUTUBE = build("youtube", "v3", developerKey=API_KEY)


def clean_description(text: str) -> str:
    """
    Убирает из текста все URL (http://…, https://…, www.…).
    """
    if not text:
        return text
    url_pattern = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
    return url_pattern.sub("", text).strip()


def get_video_ids_for_channel(channel_id: str) -> List[str]:
    channel_resp = (
        YOUTUBE.channels().list(part="contentDetails", id=channel_id).execute()
    )
    items = channel_resp.get("items", [])
    if not items:
        return []
    uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    video_ids: List[str] = []
    next_page_token = None
    while True:
        playlist_resp = (
            YOUTUBE.playlistItems()
            .list(
                part="contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=20,
                pageToken=next_page_token,
            )
            .execute()
        )

        for item in playlist_resp.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = playlist_resp.get("nextPageToken")
        if not next_page_token:
            break
    return video_ids


def get_video_stats(video_ids: List[str]) -> List[Dict]:
    videos: List[Dict] = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = (
            YOUTUBE.videos()
            .list(part="snippet,statistics", id=",".join(batch))
            .execute()
        )
        for item in resp.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            raw_desc = snippet.get("description", "")
            clean_desc = clean_description(raw_desc)

            theme = classify_by_embedding(clean_desc)

            videos.append(
                {
                    "Title": snippet.get("title"),
                    "Platform": "youtube",
                    "Theme": theme[0],
                    "LikeCount": int(stats.get("likeCount", 0))
                    if stats.get("likeCount") is not None
                    else None,
                    "CommentCount": int(stats.get("commentCount", 0))
                    if stats.get("commentCount") is not None
                    else None,
                }
            )
    return videos


def fetch_all_channel_videos(channel_id: str) -> List[Dict]:
    video_ids = get_video_ids_for_channel(channel_id)
    if not video_ids:
        print(f"No videos found for channel {channel_id}")
        return []
    videos = get_video_stats(video_ids)
    airtable_records = [{"fields": video} for video in videos]
    return airtable_records


if __name__ == "__main__":
    cid = os.environ.get("YOUTUBE_TARGET_CHANNEL_ID", "UCgv3xMy6kECn0boYP9d2o-g")
    videos = fetch_all_channel_videos(cid)
    for v in videos:
        print(v)
