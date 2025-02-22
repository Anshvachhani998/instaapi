from flask import Flask, request, jsonify
import re
import requests
from instagrapi import Client as InstaClient
import os

app = Flask(__name__)

INSTAGRAM_SESSION_FILE = "session.json"
insta_client = InstaClient()

def get_redirected_url(ddinstagram_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(ddinstagram_url, headers=headers, allow_redirects=True)

        
        final_url = response.url

        if "scontent.cdninstagram.com" in final_url:
            return final_url
        return None

    except Exception as e:
        return None


@app.route('/api', methods=['GET'])
def convert_reel():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "Instagram Reels, TV, or Post URL is required"}), 400

    match = re.search(r'/(reel|tv|p)/([^/?]+)', url)
    
    if not match:
        return jsonify({"error": "Invalid Instagram URL format"}), 400

    content_id = match.group(2)  # Extract only the ID
    modified_url = f"https://www.ddinstagram.com/grid/{content_id}"  # Corrected format

    # Get the final redirected URL (direct video link)
    video_url = get_redirected_url(modified_url)

    if not video_url:
        return jsonify({"error": "Failed to fetch video link"}), 500

    return jsonify({
        "dwn_url": video_url
    })




# Load session if exists
if os.path.exists(INSTAGRAM_SESSION_FILE):
    insta_client.load_settings(INSTAGRAM_SESSION_FILE)
else:
    insta_client.login("loveis8507", "Ansh12345@23")
    insta_client.dump_settings(INSTAGRAM_SESSION_FILE)


@app.route("/profile", methods=["GET"])
def get_profile():
    username = request.args.get("username")
    
    if not username:
        return jsonify({"error": "⚠️ Please provide a username"}), 400
    
    try:
        user_info = insta_client.user_info_by_username(username)
        profile_pic = user_info.profile_pic_url
        bio = user_info.biography or "No bio available."
        followers = user_info.follower_count
        following = user_info.following_count

        response_data = {
            "username": username,
            "bio": bio,
            "followers": followers,
            "following": following,
            "profile_pic": profile_pic
        }

        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
