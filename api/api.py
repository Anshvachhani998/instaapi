from flask import Flask, request, jsonify
from instagrapi import Client
import requests
import os

app = Flask(__name__)

# Instagram Credentials
INSTAGRAM_USERNAME = "harshvi_039"
INSTAGRAM_PASSWORD = "Ansh123@123"
SESSION_FILE = "session.json"

# Initialize Instagram Client
cl = Client()

# Try loading session to avoid frequent logins
if os.path.exists(SESSION_FILE):
    cl.load_settings(SESSION_FILE)
else:
    cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    cl.dump_settings(SESSION_FILE)  # Save session

def clean_instagram_url(url: str) -> str:
    """Cleans Instagram URL by removing tracking parameters and replacing 'reel' with 'p'."""
    url = url.split("?")[0]  # Remove URL parameters
    url = url.replace("/reel/", "/p/")  # Convert Reel to Post URL
    return url

@app.route("/get_instagram_video", methods=["GET"])
def get_instagram_video():
    """Fetches the Instagram video URL, title, and size."""
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

        clean_url = clean_instagram_url(url)
        shortcode = clean_url.split("/")[-2]

        # Fetch post details
        media_info = cl.media_info_from_shortcode(shortcode)

        if media_info.video_url:
            video_url = media_info.video_url
            title = media_info.caption if media_info.caption else "No Title"

            # Get video file size
            response = requests.head(video_url)
            size_bytes = int(response.headers.get("content-length", 0))
            size_mb = size_bytes / (1024 * 1024)

            return jsonify({
                "status": "success",
                "video_url": video_url,
                "title": title,
                "video_size_MB": round(size_mb, 2)
            })
        else:
            return jsonify({"status": "error", "message": "This post does not contain a video."}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

