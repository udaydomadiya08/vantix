from flask import Flask, request, jsonify, send_file, render_template
import os
import subprocess
import google.generativeai as genai
from flask import session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "123"  # Required for using session
CORS(app)
# 🔐 Gemini setup
GEMINI_API_KEY = "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name='models/gemini-2.5-flash-preview-04-17')
conversation = []

from flask import jsonify, url_for
import subprocess
import os

import os
conversation=[]
@app.route("/generate", methods=["POST"])
def generate():
    print(">>> /generate endpoint called <<<") 
    user_input = request.json.get("message", "")
    print(f"Received message: {user_input}")

    # Always define base_prompt first
    base_prompt = {
        "role": "model",
        "parts": [
            "You are Clara, a friendly, helpful, and empathetic assistant. "
           
            "dont use emojis and just respond in plain text, not any bold text and not any hyphen or astreik mark use or nay symbols like that only plain text"
            "respond directly to task without teliing anyhting just give ouptu that is of use and nothing else just ouput that is essential and nothing else text jus tmain contextual text"
        ]
    }

    if not session.get("intro_shown"):
        intro_message = {
            "role": "model",
            "parts": [
                "Hi there! I'm Clara, your helpful assistant. 😊\n\n"
                "Here's a quick intro video about how I can support you:\n\n"
                '<video controls autoplay muted>'
                '<source src="/static/videos/intro.mp4" type="video/mp4">'
                "Your browser does not support the video tag."
                '</video>\n\n'
                "How can I support you today?"
            ]
        }
        conversation.append(intro_message)
        session["intro_shown"] = True
        return jsonify({"reply": intro_message["parts"][0]})

    # Add base prompt only if this is a fresh conversation
    if not conversation:
        conversation.append(base_prompt)


    print(f"Received message: {user_input}")  # Debug input

    conversation.append({"role": "user", "parts": [user_input]})

    # Generate AI response
    response = gemini_model.generate_content(conversation)
    ai_reply = response.text.strip()

    conversation.append({"role": "model", "parts": [ai_reply]})


    print("Clara says:", ai_reply)

    # Save response text to input.txt
    input_txt_path = "/Users/uday/Downloads/VIDEOYT/input.txt"
    with open(input_txt_path, "w") as f:
        f.write(ai_reply)
    print(f"Saved script to {input_txt_path}")

    # Run video generation script
    video_script_path = "/Users/uday/Downloads/VIDEOYT/video.py"
    print(f"Running video generation script: {video_script_path}")
    result = subprocess.run(["python3", video_script_path], capture_output=True, text=True)

    print("Video script stdout:", result.stdout)
    print("Video script stderr:", result.stderr)

    # Check if video file exists
    video_path = "/Users/uday/Downloads/VIDEOYT/static/videos/myfinal.mp4"
    if os.path.exists(video_path):
        print(f"Video created successfully: {video_path}")
    else:
        print("Video file not found!")

    # Return URL relative to your Flask static folder (make sure your Flask app serves it)
    video_url = "/static/videos/myfinal.mp4"  # Or whatever URL you want to serve it at

    return jsonify({"video": video_url})



# @app.route("/video")
# def get_video():
#     return send_file("/Users/uday/Downloads/VIDEOYT/final_video/myfinal.mp4", mimetype="video/mp4")



@app.route('/')
def index():
    video_path = 'static/videos/myfinal.mp4'
    video_exists = os.path.exists(video_path)
    return render_template('index.html', video_exists=video_exists)


from flask import send_file

@app.route('/videos/myfinal.mp4')
def serve_video():
    return send_file('static/videos/myfinal.mp4', mimetype='video/mp4')



if __name__ == "__main__":
    app.run(debug=True)
