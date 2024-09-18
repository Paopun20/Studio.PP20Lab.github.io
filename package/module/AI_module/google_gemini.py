import google.generativeai as genai
import json
import os

class GoogleGemini:
    def __init__(self, api_key=None, model_name="gemini-1.5-flash", gconfig=None, safety=None, debug=False):
        """
        Initializes the GoogleGemini object with optional API key and model configuration.

        Args:
            api_key (str): API key for Google Generative AI API (optional).
            model_name (str): Name of the generative model to use (default: "gemini-1.5-flash").
            gconfig (dict): Configuration settings for the model generation (optional).
            safety (list): Safety settings for the model (optional).
            debug (bool): Enables debug mode for additional logging (default: False).
        """
        self.model = None
        self.chats = {}  # To store chat history
        self.debug = debug  # Debug mode flag

        if self.debug:
            print("[DEBUG] GoogleGemini initialized.")

        # Configure API key and model if provided
        if api_key:
            self.set_api_key(api_key)
        if api_key and model_name:
            self.configure_model(model_name, gconfig, safety)

    def set_api_key(self, api_key):
        """Sets the API key for Google Generative AI API."""
        try:
            if self.debug:
                print(f"[DEBUG] Setting API key: {api_key}")
            genai.configure(api_key=api_key)
            print("API key successfully set.")
        except Exception as e:
            raise ValueError(f"Failed to set API key: {e}")

    def configure_model(self, model_name="gemini-1.5-flash", gconfig=None, safety=None):
        """
        Configures the generative model with the given model name and settings.

        Args:
            model_name (str): Name of the model to configure (default: "gemini-1.5-flash").
            gconfig (dict): Model configuration settings (optional).
            safety (list): Safety settings (optional).
        """
        try:
            if self.debug:
                print(f"[DEBUG] Configuring model: {model_name} with settings: {gconfig} and safety: {safety}")
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=gconfig or {},
                safety_settings=safety or []
            )
            print(f"Model '{model_name}' configured successfully.")
        except Exception as e:
            raise ValueError(f"Error configuring model: {e}")

    def send_query(self, query, chat_name="default_chat"):
        """
        Sends a query to the generative model and stores the conversation.

        Args:
            query (str): The user query to send to the model.
            chat_name (str): The name of the chat session (default: "default_chat").

        Returns:
            str: The model's response.
        """
        if not self.model:
            raise RuntimeError("Model is not configured. Please configure the model first.")
        
        try:
            if self.debug:
                print(f"[DEBUG] Sending query: '{query}' to chat session: '{chat_name}'")

            chat_session = self.model.start_chat()
            response = chat_session.send_message(query).text

            if self.debug:
                print(f"[DEBUG] Response received: {response}")

            # Store chat in history
            self._store_chat(chat_name, query, response)

            return response
        except Exception as e:
            raise RuntimeError(f"Error querying the model: {e}")

    def _store_chat(self, chat_name, user_query, model_response):
        """Private method to store a chat conversation."""
        if self.debug:
            print(f"[DEBUG] Storing chat in session '{chat_name}': User: {user_query}, Response: {model_response}")
        
        if chat_name not in self.chats:
            self.chats[chat_name] = []
        
        self.chats[chat_name].append({'user': user_query, 'response': model_response})

    def get_chat_history(self, chat_name="default_chat"):
        """
        Retrieves the chat history for a specific session.

        Args:
            chat_name (str): The name of the chat session (default: "default_chat").

        Returns:
            list: List of chat entries.
        """
        if self.debug:
            print(f"[DEBUG] Retrieving chat history for session '{chat_name}'")

        if chat_name in self.chats:
            return self.chats[chat_name]
        raise ValueError(f"No chat history found for session '{chat_name}'.")

    def save_chats(self, file_path="chat_history.json"):
        """
        Saves all chat histories to a file.

        Args:
            file_path (str): Path to the file (default: "chat_history.json").
        """
        try:
            if self.debug:
                print(f"[DEBUG] Saving chat history to file: {file_path}")
            
            with open(file_path, 'w') as file:
                json.dump(self.chats, file, indent=4)
            print(f"Chat history saved to {file_path}")
        except Exception as e:
            raise IOError(f"Failed to save chat history: {e}")

    def load_chats(self, file_path="chat_history.json"):
        """
        Loads chat histories from a file.

        Args:
            file_path (str): Path to the file (default: "chat_history.json").
        """
        if os.path.exists(file_path):
            try:
                if self.debug:
                    print(f"[DEBUG] Loading chat history from file: {file_path}")
                
                with open(file_path, 'r') as file:
                    self.chats = json.load(file)
                print(f"Chat history loaded from {file_path}")
            except Exception as e:
                raise IOError(f"Failed to load chat history: {e}")
        else:
            raise FileNotFoundError(f"No such file: {file_path}")
