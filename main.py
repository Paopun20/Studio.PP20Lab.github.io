from package.module.AI_module.google_gemini import GoogleGemini as Gemini
from flask import Flask, request, jsonify
import os

# Load API key from environment variable
API_KEY = "AIzaSyAR_N9oCnRcJqr9EYtzjkDG-jhuTiJwjeg"

# Enable debug mode
DEBUG_MODE = True

# Create an instance of Gemini with debug mode enabled
gemini = Gemini(debug=DEBUG_MODE)

# Set the API key and configure the model
try:
    if not API_KEY:
        raise ValueError("API key is not set")
    gemini.set_api_key(API_KEY)

    gemini.configure_model(
        model_name="gemini-1.5-flash",
        gconfig={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        },
        safety=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    )
except Exception as e:
    print(f"Error during setup: {e}")

app = Flask(__name__)

@app.route('/<id_value>/Gemini/<chatname>/', methods=['GET'])
def handle_request(id_value, chatname):
    text_received = request.args.get('txt')

    if not text_received:
        return jsonify({"status": "error", "message": "No text provided in 'txt' parameter"}), 400

    chat_log_path = f"DBChatlog/{id_value}.json"
    if os.path.exists(chat_log_path):
        try:
            gemini.load_chats(chat_log_path)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error loading chat history: {e}"}), 500

    try:
        output = gemini.send_query(text_received, chatname)
        gemini.save_chats(chat_log_path)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    response_data = {
        "status": "Succeed",
        "query": text_received,
        "text": output,
    }

    return jsonify(response_data)

if __name__ == '__main__':
    # Run the Flask server
    app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE)
