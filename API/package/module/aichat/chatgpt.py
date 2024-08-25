import json
import textwrap
import openai
import nltk

# Set NLTK data path and download necessary resource
nltk.data.path.append('./nltk_data')
nltk.download('punkt')

# Load API keys from JSON file
try:
    with open('settings.json') as config_file:
        api_keys = json.load(config_file)
except FileNotFoundError:
    raise FileNotFoundError("Configuration file 'settings.json' not found or invalid.")
except json.JSONDecodeError:
    raise ValueError("Configuration file 'settings.json' is not a valid JSON.")

# Extract Generative AI SDK API key
chatgpt_api_key = api_keys.get('chatgpt_api_key')

if not chatgpt_api_key:
    raise ValueError("ChatGPT SDK API key not found in JSON file")

# Configure OpenAI API
openai.api_key = chatgpt_api_key

chatgptconfig = {
    "generation_config": {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_tokens": 8192,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "logprobs": 0
    }
}

class AI:
    @staticmethod
    def to_markdown(text):
        """
        Convert bullet points in the text to markdown format.
        """
        text = text.replace('•', '  *')
        return textwrap.indent(text, '> ', predicate=lambda _: True)
    
    @staticmethod
    def query_generative_api(query):
        """
        Query the OpenAI Generative API and return the response text.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[{"role": "user", "content": query}],
                temperature=chatgptconfig["generation_config"]["temperature"],
                max_tokens=256,
                top_p=chatgptconfig["generation_config"]["top_p"],
                frequency_penalty=chatgptconfig["generation_config"]["frequency_penalty"],
                presence_penalty=chatgptconfig["generation_config"]["presence_penalty"]
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            raise ValueError("Failed to retrieve data from the Generative AI API: %s" % str(e))
    
    @staticmethod
    def count_tokens(text):
        """
        Count the number of tokens in the given text using NLTK tokenizer.
        """
        tokens = nltk.word_tokenize(text)
        return len(tokens)
    
    @staticmethod
    def calculate_auto_indent(data):
        """
        Calculate the auto indentation level for a given JSON-like data structure.
        """
        if isinstance(data, dict):
            return max([AI.calculate_auto_indent(value) for value in data.values()] + [0]) + 1
        elif isinstance(data, list):
            return max([AI.calculate_auto_indent(item) for item in data] + [0]) + 1
        else:
            return 0