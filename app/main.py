import os
import threading
from flask import Flask, jsonify, send_file, request, render_template
from flask_cors import CORS
import subprocess

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

BASE_DIR = "/home/sikandar"
MEDIA_DIR = os.path.join(BASE_DIR, "Movies")
HLS_DIR = os.path.join(BASE_DIR, "HLS")
PICTURES_DIR = os.path.join(BASE_DIR, "Pictures")
CLIPS_DIR = os.path.join(BASE_DIR, "Clips")

# Ensure HLS directory exists
os.makedirs(HLS_DIR, exist_ok=True)

# Helper: List directory contents
def list_directory(path):
    files = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        files.append({
            "name": item,
            "is_dir": os.path.isdir(item_path),
            "path": item_path,
        })
    return files

# Route: Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Route: List folders (Movies, Pictures, Clips)
@app.route('/folder/<folder>')
def show_folder(folder):
    folder_map = {"Movies": MEDIA_DIR, "Pictures": PICTURES_DIR, "Clips": CLIPS_DIR}
    if folder not in folder_map:
        return "Folder not found", 404
    files = list_directory(folder_map[folder])
    return render_template('view.html', folder=folder, files=files)

# Route: Stream Video
@app.route('/stream/<filename>')
def stream_video(filename):
    input_path = os.path.join(MEDIA_DIR, filename)
    output_dir = os.path.join(HLS_DIR, filename[:-4])
    os.makedirs(output_dir, exist_ok=True)
    playlist_path = os.path.join(output_dir, "playlist.m3u8")

    # If HLS already exists, stream it
    if not os.path.exists(playlist_path):
        def convert_to_hls():
            cmd = [
                "ffmpeg", "-i", input_path,
                "-codec: copy", "-start_number", "0",
                "-hls_time", "10", "-hls_list_size", "0",
                "-f", "hls", os.path.join(output_dir, "playlist.m3u8")
            ]
            subprocess.run(cmd)
        threading.Thread(target=convert_to_hls).start()

    return jsonify({"stream_url": f"/hls/{filename[:-4]}/playlist.m3u8"})

@app.route('/folder/pictures')
def pictures_album():
    images = [img for img in os.listdir(PICTURES_DIR) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('album.html', images=images)

@app.route('/folder/pictures/<filename>')
def serve_picture(filename):
    file_path = os.path.join(PICTURES_DIR, filename)
    return send_file(file_path)

# Route: Serve HLS segments
@app.route('/hls/<folder>/<filename>')
def serve_hls(folder, filename):
    return send_file(os.path.join(HLS_DIR, folder, filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
