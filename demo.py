import streamlit as st
import yt_dlp
import subprocess
import os
import re
from datetime import datetime
import platform

# Hide Streamlit's default menu, footer, and header
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Function to get the download folder path
def get_download_folder():
    system_name = platform.system()
    if system_name == "Windows":
        return os.path.join(os.getenv("USERPROFILE"), "Downloads")
    else:
        return os.path.expanduser("~")

output_folder = get_download_folder()

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*\']', '', filename)

def download_video(video_url, download_type="mp4"):
    title = "DownloadedFile"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if download_type == "mp4":
        video_file = os.path.join(output_folder, f"{title}.mp4")
        audio_file = os.path.join(output_folder, f"{title}.m4a")
        final_output = os.path.join(output_folder, f"{title}_{timestamp}.mp4")

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
            # Download video and audio
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                ydl.download([video_url])
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([video_url])

            # Merge video and audio
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

            os.remove(video_file)
            os.remove(audio_file)
            return final_output

        except Exception as e:
            return None

    elif download_type == "mp3":
        audio_file = os.path.join(output_folder, f"{title}_{timestamp}.mp3")
        
        ydl_opts_audio = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'keepvideo': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([video_url])
            return audio_file

        except Exception as e:
            return None

# Initialize Streamlit design
st.markdown("""
<style>
    .main{
        width: 100%;
        height: 100%;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        gap: 10px;
        --color: rgba(114, 114, 114, 0.3);
        background-color: #191a1a;
        background-image: linear-gradient(0deg, transparent 24%, var(--color) 25%, var(--color) 26%, transparent 27%,transparent 74%, var(--color) 75%, var(--color) 76%, transparent 77%,transparent),
            linear-gradient(90deg, transparent 24%, var(--color) 25%, var(--color) 26%, transparent 27%,transparent 74%, var(--color) 75%, var(--color) 76%, transparent 77%,transparent);
        background-size: 55px 55px;
        }
body {
    background-color: #121212;
    color: white;
    font-family: Arial, sans-serif;
}
.stTitle-typing {
    font-family: 'Courier New', Courier, monospace;
    font-size: 40px;
    color: white;
    display: inline-block;
    white-space: nowrap;
    overflow: hidden;
    border-right: 4px solid transparent;
    animation: typing 5s steps(30) 1s forwards, blink 0.75s step-end infinite;
}
@keyframes typing {
    from { width: 0; }
    to { width: 100%; }
}
@keyframes blink {
    50% { border-color: transparent; }
    100% { border-color: white; }
}
.stTextInput {
    background-color: #1a1a1a;
    border: none;
    padding: 10px;
    border-radius: 10px;
    outline: none;
    color: white;
    animation: rotateShadow 2s infinite linear;
}
.stTextInput:focus {
    animation: rotateShadow 3s infinite linear;
}            
@keyframes rotateShadow {
    0% { box-shadow: -2px -2px 8px 1px #aa00ff, 2px 2px 8px 1px #3700ff; }
    25% { box-shadow: -2px 2px 8px 1px #aa00ff, 2px -2px 8px 1px #3700ff; }
    50% { box-shadow: 2px 2px 8px 1px #aa00ff, -2px -2px 8px 1px #3700ff; }
    75% { box-shadow: 2px -2px 8px 1px #aa00ff, -2px 2px 8px 1px #3700ff; }
    100% { box-shadow: -2px -2px 8px 1px #aa00ff, 2px 2px 8px 1px #3700ff; }
}
.stButton>button {
    display: inline-block;
    border-radius: 8px;
    border: none;
    background: #1875FF;
    color: white;
    font-family: inherit;
    text-align: center;
    font-size: 14px;
    box-shadow: 0px 8px 24px -4px rgba(24, 117, 255, 0.6);
    width: 12em;
    padding: 0.8em 1.2em;
    transition: all 0.3s ease;
    cursor: pointer;
}
.stButton>button:hover {
    background: #0c5fd6;
    color: white;
    box-shadow: 0px 10px 30px -6px rgba(12, 95, 214, 0.7);
}
.stButton>button:active {
    background-color: #28a745;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("YouTube Video Downloader")

video_url = st.text_input("Enter the YouTube Video URL", placeholder="https://youtube.com/...")

col1, col2 = st.columns(2)
with col1:
    if st.button("Download Video"):
        if video_url:
            with st.spinner("Downloading..."):
                output_file = download_video(video_url)
                if output_file:
                    st.success("Video downloaded successfully!")
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Click here to download",
                            data=file,
                            file_name=os.path.basename(output_file),
                            mime="video/mp4"
                        )
                else:
                    st.error("An error occurred during the video download.")
        else:
            st.error("Please enter a valid URL.")

with col2:
    if st.button("Download Audio"):
        if video_url:
            result = download_video(video_url, download_type="mp3")
            if result:
                st.success("Audio downloaded successfully!")
                with open(result, "rb") as file:
                    st.download_button(
                        label="Click here to download",
                        data=file,
                        file_name=os.path.basename(result),
                        mime="audio/mp3"
                    )
            else:
                st.error("An error occurred during the audio download.")
        else:
            st.error("Please enter a valid URL.")
