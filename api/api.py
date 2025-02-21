from flask import Flask, request, jsonify
import re
import requests

app = Flask(__name__)

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

@app.route('/convert', methods=['GET'])
def convert_reel():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "Instagram Reels URL is required"}), 400


    match = re.search(r'/(reel|tv|p)/([^/?]+)', url)

    
    if not match:
        return jsonify({"error": "Invalid Instagram Reels URL format"}), 400

    reel_id = match.group(1)
    modified_url = f"https://www.ddinstagram.com/grid/{reel_id}"

    # Get the final redirected URL (direct video link)
    video_url = get_redirected_url(modified_url)

    if not video_url:
        return jsonify({"error": "Failed to fetch video link"}), 500

    return jsonify({        
        "dwn_url": video_url
    })

