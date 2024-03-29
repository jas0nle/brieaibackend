from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import cv2
import base64
import os
load_dotenv()
app = Flask(__name__)
CORS(app)
# Members API Route
#to get it running locally, change _app and cta to have localhost:5000/members, etc
#to get it running online, deploy backend separately, then front end
@app.route("/members")
def members():
    return{"members":["Member1","Member2","Member3",]}

@app.route("/upload-video", methods=["POST"])
def upload_video():
    apiKey = os.getenv("OPENAI_API_KEY")
    if not apiKey:
        return jsonify({"error": "OpenAI API key not found"}), 500
    client = OpenAI(api_key=apiKey)
    uploaded_file = request.files["video"]
    uploaded_file_path = os.path.join("uploaded_videos", uploaded_file.filename)
    uploaded_file.save(uploaded_file_path)
    # Process the uploaded video file here
    # For example, save it to disk
    video = cv2.VideoCapture(uploaded_file_path)
    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        
    video.release()
    PROMPT_MESSAGES = [
    {
        "role": "user",
        "content": [
            "These are frames from a video of me on an indoor rowing machine. Generate a compelling description on how I can improve my form to become a better rower.",
            *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
        ],
    },
]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 2000,
    }

    result = client.chat.completions.create(**params)
    os.remove(uploaded_file_path)
    return jsonify({"frame_count": result.choices[0].message.content}), 200



if __name__ == "__main__":
    app.run(debug=True)