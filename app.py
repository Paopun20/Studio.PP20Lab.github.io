from flask import Flask, request, jsonify, render_template, Response
import json
import textwrap
import google.generativeai as genai
import nltk

nltk.data.path.append('./nltk_data')
nltk.download('punkt')  # Download necessary resource for tokenization

# Load API keys from JSON file
try:
    with open('settings.json') as config_file:
        api_keys = json.load(config_file)
except Exception as e:
    raise FileNotFoundError("Configuration file 'settings.json' not found or invalid.") from e

# Extract Generative AI SDK API key
gemini_api_key = "AIzaSyAR_N9oCnRcJqr9EYtzjkDG-jhuTiJwjeg"

if not gemini_api_key:
    raise ValueError("Generative AI SDK API key not found in JSON file")

# Configure Google Generative AI SDK
genai.configure(api_key=gemini_api_key)

geminiconfig = {
    "generation_config": {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    },
    "safety_settings": [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ],
}

class AI:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        safety_settings=geminiconfig["safety_settings"],
        generation_config=geminiconfig["generation_config"],
    )
    
    @staticmethod
    def to_markdown(text):
        text = text.replace('•', '  *')
        return textwrap.indent(text, '> ', predicate=lambda _: True)
    
    @staticmethod
    def query_generative_api(query):
        try:
            chat_session = AI.model.start_chat()
            response = chat_session.send_message(query)
            return response.text
        except Exception as e:
            raise ValueError("Failed to retrieve data from the Generative AI API: %s" % str(e))
    
    @staticmethod
    def count_tokens(text):
        tokens = nltk.word_tokenize(text)  # Tokenize the text
        return len(tokens)
    
    @staticmethod
    def calculate_auto_indent(data):
        if isinstance(data, dict):
            return max([AI.calculate_auto_indent(value) for value in data.values()] + [0]) + 1
        elif isinstance(data, list):
            return max([AI.calculate_auto_indent(item) for item in data] + [0]) + 1
        else:
            return 0

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("indexPY.html")  # Ensure this file exists in the /templates directory

@app.route("/api", methods=['GET', 'POST'])
def API():
    if request.method == 'POST':
        data = request.get_json()
        txt = data.get('txt')
        if not txt:
            return jsonify({"error": "No text provided"}), 400
        
        try:
            response_text = AI.query_generative_api(txt)
            markdown_text = AI.to_markdown(response_text)
            return jsonify({"output": markdown_text, "token_count": AI.count_tokens(response_text)})
        except ValueError as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid request method"}), 405

if __name__ == "__main__":
    app.run(debug=True, port=4949)
