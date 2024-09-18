from package.module.AI_module.google_gemini import GoogleGemini as Gemini
from flask import Flask, request, jsonify

# Enable debug mode
debug_mode = True

# Create an instance of Gemini with debug mode enabled
gemini = Gemini(debug=debug_mode)

# Set the API key and configure the model
try:
    # Set API key
    gemini.set_api_key("AIzaSyAR_N9oCnRcJqr9EYtzjkDG-jhuTiJwjeg")

    # Configure the model
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

# Define a route to handle GET requests to /<id>/Gemini/<chatname>/
@app.route('/<id_value>/Gemini/<chatname>/', methods=['GET'])
def handle_request(id_value, chatname):
    # Get the 'txt' parameter from the URL
    text_received = request.args.get('txt')

    # Return a JSON response with the received data
    response_data = {
        'id': id_value,
        'chatname': chatname,
        'text': text_received,
        'message': 'Request was successful!'
    }
    return jsonify(response_data)

# Run the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
