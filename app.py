from flask import Flask, render_template, request, jsonify
import os
import yt_dlp
import subprocess
import re
from datetime import datetime
import os
import platform

app = Flask(__name__, template_folder=".")
def get_download_folder():
    system_name = platform.system()
    
    if system_name == "Windows":
        return os.path.join(os.getenv("USERPROFILE"), "Downloads")
    elif system_name == "Darwin":  # macOS
        return os.path.join(os.path.expanduser("~"), "Downloads")
    elif system_name == "Linux":
        return os.path.join(os.path.expanduser("~"), "Downloads")
    elif system_name == "Android":  # Android
        return "/storage/emulated/0/Download"
    elif system_name == "iOS":  # iOS
        return os.path.join(os.path.expanduser("~"), "Documents")
    else:
        return os.path.expanduser("~")  # Fallback to home directory if unknown OS

output_folder = get_download_folder()
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*\']', '', filename)

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data['videoUrl']
    
    title = sanitize_filename(video_url.split('=')[-1])  # Extract title from URL
    video_file = os.path.join(output_folder, f"{title}.mp4")
    audio_file = os.path.join(output_folder, f"{title}.m4a")
    
    # Add a timestamp to the final output filename
    title  = "Downloadedfile"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output = os.path.join(output_folder, f"{title}_{timestamp}.mp4")  # Final output file name with timestamp

    ydl_opts_video = {
        'format': 'bestvideo',
        'outtmpl': video_file,
        'noplaylist': True,
    }

    ydl_opts_audio = {
        'format': 'bestaudio',
        'outtmpl': audio_file,
        'noplaylist': True,
    }

    try:
        # Download video
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([video_url])

        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([video_url])

        # Merge video and audio files
        command = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            final_output
        ]
        subprocess.run(command, check=True)

        # Clean up by removing separate audio and video files
        os.remove(video_file)
        os.remove(audio_file)

        return jsonify({'status': 'success', 'message': 'Your video has been downloaded successfully!', 'file': final_output})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
