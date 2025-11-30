from flask import Flask, jsonify
from config import Config
import tables as tb  # t-bank)
import services.reddit as rt
import os
import services.youtube as yt
import services.youtube as yttrend


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Routes
    @app.route("/ping")
    def ping():
        return jsonify({"status": True, "message": "Pong"}), 200

    @app.route("/update_main")
    def update():
        user = os.environ.get("REDDIT_TARGET_USER", "Thanatofobia")
        posts = rt.get_posts(user, 50)
        print(posts)
        return tb.write_table("dst2JVDFbeSpy5ENyB", posts, "viww0JqwoFahw", "name")

    @app.route("/update_youtube")
    def update_youtube():
        channel = os.environ.get(
            "YOUTUBE_TARGET_CHANNEL_ID", "UCuAXFkgsw1L7xaCfnd5JJOw"
        )
        videos = yttrend.fetch_all_channel_videos(channel)
        print(videos)
        return tb.write_table("dstJUo2aE5o0MHAi9e", videos, "viwwBFXJ296gZ")

    @app.route("/update_youtube_trending")
    def update_youtube_trending():
        videos = yt.get_trending_videos_non_music("GB", 20)
        print(videos)
        return tb.write_table("dstVA5ezf9rtAZBl64", videos, "viw4leoS9FWR5")

    @app.errorhandler(404)
    def not_found():
        return jsonify({"status": False, "message": "Error"}), 404

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=8000)
