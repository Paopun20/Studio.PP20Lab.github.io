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
gemini_api_key = api_keys.get('gemini_api_key')

if not gemini_api_key:
    raise ValueError("Generative AI SDK API key not found in JSON file")

# Configure Google Generative AI SDK
genai.configure(api_key=gemini_api_key)

geminiconfig = {}
geminiconfig["generation_config"] = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

geminiconfig["safety_settings"] = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

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