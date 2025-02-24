from flask import Flask, request, jsonify
from instagrapi import Client as InstaClient
import os
import pymongo
import json
import re

app = Flask(__name__)

# MongoDB setup
MONGO_URI = "mongodb+srv://Ansh089:Ansh089@cluster0.y8tpouc.mongodb.net/?retryWrites=true&w=majority"  # Change this to your MongoDB URI
DB_NAME = "instagram_db"
COLLECTION_NAME = "sessions"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Initialize Instagram Client
insta_client = InstaClient()

# Load session from MongoDB if available
saved_session = collection.find_one({"_id": "insta_session"})
if saved_session and "session_data" in saved_session:
    insta_client.set_settings(saved_session["session_data"])  # ✅ Correct way to load session
else:
    insta_client.login("loveis8507", "Ansh12345@23")
    session_data = insta_client.get_settings()
    collection.update_one({"_id": "insta_session"}, {"$set": {"session_data": session_data}}, upsert=True)



@app.route("/profile", methods=["GET"])
def get_profile():
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "⚠️ Please provide a username"}), 400

    try:
        user_info = insta_client.user_info_by_username_v1(username)  # ✅ Using v1 method
        full_name = user_info.full_name or "No name available."  # ✅ Full name added
        profile_pic = str(user_info.profile_pic_url_hd)  # ✅ High-quality profile pic
        bio = user_info.biography or "No bio available."
        followers = user_info.follower_count
        following = user_info.following_count

        response_data = {
            "username": username,
            "name": full_name,  # ✅ Full name added in response
            "bio": bio,
            "followers": followers,
            "following": following,
            "profile_pic": profile_pic
        }

        return app.response_class(
            response=json.dumps(response_data, ensure_ascii=False),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/save_session", methods=["POST"])
def save_session():
    """Session.json ko MongoDB me save karega"""
    try:
        session_data = insta_client.get_settings()
        collection.update_one({"_id": "insta_session"}, {"$set": {"session_data": session_data}}, upsert=True)
        return jsonify({"message": "Session saved to MongoDB"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/fetch_session", methods=["GET"])
def fetch_session():
    """MongoDB se session fetch karke return karega"""
    try:
        saved_session = collection.find_one({"_id": "insta_session"})
        if saved_session:
            return jsonify({"session_data": saved_session["session_data"]}), 200
        else:
            return jsonify({"error": "No session found in MongoDB"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/post", methods=["GET"])
def download_post():
    post_url = request.args.get("url")

    if not post_url:
        return jsonify({"error": "⚠️ Please provide a post URL"}), 400

    try:
        # Get media ID from URL
        media_id = insta_client.media_pk_from_url(post_url)
        
        # Fetch post info
        post_info = insta_client.media_info(media_id)

        # Check if it's a carousel (multiple images/videos)
        if post_info.resources:
            media_list = []
            for resource in post_info.resources:
                media_url = resource.video_url if resource.video_url else resource.thumbnail_url
                media_list.append(str(media_url))  # ✅ Convert to string

            response_data = {"media": media_list}

        else:
            # Single image/video post
            media_url = post_info.video_url if post_info.video_url else post_info.thumbnail_url
            response_data = {"media": [str(media_url)]}  # ✅ Convert to string

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/story", methods=["GET"])
def download_story():
    story_url = request.args.get("url")

    if not story_url:
        return jsonify({"error": "⚠️ Please provide a story URL"}), 400

    try:
        # Extract story ID from the URL (last part of the URL)
        match = re.search(r"/stories/[^/]+/(\d+)", story_url)
        if not match:
            return jsonify({"error": "❌ Invalid story URL format"}), 400

        story_id = match.group(1)  # Extracted story ID

        # Fetch story info using story ID
        story_info = insta_client.media_info(story_id)

        # Get video or image URL
        media_url = story_info.video_url if story_info.video_url else story_info.thumbnail_url

        return jsonify({"story_url": str(media_url)})  # ✅ Convert to string

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/reel", methods=["GET"])
def download_reel():
    reel_url = request.args.get("url")

    if not reel_url:
        return jsonify({"error": "⚠️ Please provide a reel URL"}), 400

    try:
        # Get media ID from URL
        media_id = insta_client.media_pk_from_url(reel_url)
        
        # Fetch reel info
        reel_info = insta_client.media_info(media_id)

        response_data = {
            "video_url": str(reel_info.video_url)
        }

        return app.response_class(
            response=json.dumps(response_data, ensure_ascii=False),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/caption", methods=["GET"])
def download_caption():
    reel_url = request.args.get("url")

    if not reel_url:
        return jsonify({"error": "⚠️ Please provide a reel URL"}), 400

    try:
        # Get media ID from URL
        media_id = insta_client.media_pk_from_url(reel_url)
        
        # Fetch reel info
        reel_info = insta_client.media_info(media_id)

        response_data = {
            "caption": reel_info.caption_text or "No caption"
        }

        return app.response_class(
            response=json.dumps(response_data, ensure_ascii=False),
            status=200,
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        

if __name__ == "__main__":
    app.run(debug=True)
