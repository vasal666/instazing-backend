from flask import Flask, request, jsonify
from instaloader import Instaloader, Post
import os

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_media():
    try:
        # Get Instagram post URL from frontend
        data = request.get_json()
        post_url = data.get('url')

        # Extract shortcode from URL (e.g., ABC123 from https://www.instagram.com/p/ABC123/)
        shortcode = post_url.split('/')[-2]

        # Initialize Instaloader
        L = Instaloader(download_pictures=True, download_videos=True, download_comments=False, download_geotags=False)

        # Fetch post
        post = Post.from_shortcode(L.context, shortcode)

        # Download media to a temporary folder
        temp_dir = 'downloads'
        os.makedirs(temp_dir, exist_ok=True)
        L.download_post(post, target=temp_dir)

        # Find the downloaded file (image or video)
        for file in os.listdir(temp_dir):
            if file.endswith(('.jpg', '.mp4')):
                file_path = os.path.join(temp_dir, file)
                break
        else:
            return jsonify({'success': False, 'error': 'No media found'}), 400

        # Generate a public URL for the file (Render/Heroku serves static files)
        file_url = f"/static/{file}"
        return jsonify({'success': True, 'downloadUrl': file_url, 'thumbnail': file_url if file.endswith('.jpg') else None})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_file(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
