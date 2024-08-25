import logging
from logging.handlers import RotatingFileHandler
from win10toast import ToastNotifier
import os
from flask import Flask, request, Response
import json
import time
import sys
import socket
import importlib
import random
import subprocess
import translators as ts

from package.module.aichat.gemini import AI as gemini
from package.module.aichat.chatgpt import AI as chatgpt
from package.module.playsfx import playsfx

# Status counters
Status = {
    "Succeed": 0,
    "Error": 0,
    "Connect": 0
}

# Constants
shotappname = "GGCAAL"
appname = "Google Gemini & ChatGPT AI API Launcher"
app = Flask(__name__)

# Load the configuration from JSON file
try:
    with open('settings.json') as config_file:
        config = json.load(config_file)
except Exception as e:
    raise FileNotFoundError("Configuration file 'settings.json' not found or invalid.") from e

# Access configuration values
debug_mode = config.get('debug_mode', False)
port = config.get('port', 3000)
skip = config.get('skip', False)

# Configure logging
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
log_file = f'{shotappname}.log'
log_handler = RotatingFileHandler(log_file, encoding='utf-8', maxBytes=1000000, backupCount=1)
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

# Color constants for terminal output
COLORS = {
    "HEADER": "\033[95m",
    "OKBLUE": "\033[94m",
    "OKCYAN": "\033[96m",
    "OKGREEN": "\033[92m",
    "WARNING": "\033[93m",
    "FAIL": "\033[91m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
    "ENDC": "\033[0m"
}

# Notifier class for showing Windows toast notifications
class Notifier:
    def show(self, title="title", message="message", duration=1, icon_path=None):
        try:
            toaster = ToastNotifier()
            toaster.show_toast(title, message, icon_path=icon_path, duration=duration)
        except Exception as e:
            app.logger.error(f"Notifier error: {e}")

def errorsfx():
    sfx_player = playsfx()
    sfx_player.sfxplayer("resource/error.mp3", 999, True)
    for i in range(70001):
        r = f"{i + random.uniform(0, 50) % 2}{i + random.uniform(0, 50) % 2}"
        print(f"error: {r}{r}{r}{r}{r}{r}")
        time.sleep(0)
    time.sleep(10)
    sys.exit()

def cool_loading():
    try:
        if not skip:
            print(f"{COLORS['#800000']}[Python]{COLORS['ENDC']} Loading...", end='', flush=True)
            time.sleep(1)
            for i in range(101):
                print(f"\r{COLORS['#800000']}[Python]{COLORS['ENDC']} {shotappname} Loading: {i}%", end='', flush=True)
                time.sleep(0)
            print(f"\n{COLORS['#800000']}[Python]{COLORS['ENDC']} Imports:", end='', flush=True)

            importline = ["logging", "win10toast", "os", "flask", "json", "time", "sys", "socket", "random", "subprocess"]
            for module_name in importline:
                try:
                    importlib.import_module(module_name)
                    print(f"\n{COLORS['#800000']}[Python]{COLORS['ENDC']} {shotappname}: Imported {module_name.lower()}")
                except ImportError as ie:
                    app.logger.error(f"Failed to import {module_name}: {str(ie)}")
                    print(f"\n{COLORS['#800000']}[Python]{COLORS['ENDC']} {shotappname}: Failed to import {module_name.lower()}")
                except Exception as e:
                    app.logger.error(f"Unexpected error importing {module_name}: {str(e)}")
                    print(f"\n{COLORS['#800000']}[Python]{COLORS['ENDC']} {shotappname}: Unexpected error importing {module_name.lower()}")

                for i in range(101):
                    print(f"\r{COLORS['#800000']}[Python]{COLORS['ENDC']} {shotappname}: Import {module_name.lower()}: {i}%", end='', flush=True)
                    time.sleep(0)
            print(f"\n{COLORS['#800000']}[Python]{COLORS['ENDC']} Boost...")
            time.sleep(2)
    except Exception as e:
        app.logger.error("Error occurred during startup: %s", e)
        raise ValueError("Startup error occurred: %s" % e)

@app.route("/api", methods=['GET', 'POST'])
def home():
    Status["Connect"] += 1
    if 'help' in request.args:
        response_data = {
            "Available Endpoints": {
                "/?GET": "Get information about the server and its status.",
                "/?module=<module>&txt=<query>": "Query the specified AI module with the provided text."
            },

            "Parameters": {
                "module": "Specify the AI module to use (`gemini` or `chatgpt`).",
                "txt": "Provide the text for the AI to process."
            },

            "Response Format": "For successful queries, the response contains the generated text and other relevant information. For errors, the response includes an error message and code.",

            "Error Handling": {
                "400 Bad Request": "The request is invalid or missing required parameters.",
                "500 Internal Server Error": "An unexpected error occurred on the server."
            },

            "Usage Examples": {
                "Query Gemini module": "/?module=gemini&txt=How is the weather today?",
                "Query ChatGPT module": "/?module=chatgpt&txt=Tell me a joke."
            },

            "Tips": {
                "Tip 1": "Provide clear and concise queries to get accurate responses.",
                "Tip 2": "Experiment with different modules and texts to explore the capabilities of the AI.",
                "Tip 3": "Check the server status regularly to ensure smooth operation.",
                "Tip 4": "Ensure that only sticker output is supported.",
                "Tip 5": "The AI can support queries in all languages."
            }
        }
        return Response(json.dumps(response_data, indent=4, ensure_ascii=False), mimetype='application/json')

    if 'GET' in request.args:
        ip_address = get_ip_address()
        user_ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if user_ip_address is not None:
            user_ip_address = user_ip_address.split(',')[0].strip()

        response_data = {
            "status": Status,
            "user_ip_address": user_ip_address,
            "server_ip_address": ip_address
        }
        return Response(json.dumps(response_data, indent=5, ensure_ascii=False), mimetype='application/json')
    
    if 'module' not in request.args:
        response_data = {
            "message": "Please specify a module using the 'module' parameter or refer to the ?help command for assistance.",
            "status": "ERROR",
            "error_code": 400,
            "error_type": "Bad Request"
        }
        return Response(json.dumps(response_data, indent=4, ensure_ascii=False), mimetype='application/json')

    module_name = request.args['module'].lower()
    if module_name == "gemini":
        ai_module = gemini
        module = "gemini"
    elif module_name == "chatgpt":
        ai_module = chatgpt
        module = "chatgpt"
    else:
        response_data = {
            "message": "Invalid module. Use 'gemini' or 'chatgpt'. or refer to the ?help command for assistance.",
            "status": "ERROR",
            "error_code": 400,
            "error_type": "Bad Request"
        }
        return Response(json.dumps(response_data, indent=4, ensure_ascii=False), mimetype='application/json')

    if 'txt' not in request.args:
        response_data = {
            "message": "Please provide a 'txt' parameter.",
            "status": "ERROR",
            "error_code": 400,
            "error_type": "Bad Request"
        }
        return Response(json.dumps(response_data, indent=4, ensure_ascii=False), mimetype='application/json')

    txt = request.args['txt']
    if not txt.strip():
        response_data = {
            "message": "The 'txt' parameter cannot be empty. or refer to the ?help command for assistance.",
            "status": "ERROR",
            "error_code": 400,
            "error_type": "Bad Request"
        }
        return Response(json.dumps(response_data, indent=4, ensure_ascii=False), mimetype='application/json')

    user_id = request.remote_addr
    start_time = time.time()

    try:
        app.logger.info("User query: %s", txt, extra={'user_id': user_id})

        ai_instance = ai_module()
        ai_response = ai_instance.query_generative_api(txt)
        if not ai_response:
            raise ValueError("Generative AI API response is None")

        markdown_text = ai_instance.to_markdown(ai_response)
        token_count = ai_instance.count_tokens(ai_response)

        end_time = time.time()
        time_to_output = end_time - start_time

        generative_time = {
            "hours": int(time_to_output // 3600),
            "minutes": int((time_to_output % 3600) // 60),
            "seconds": int(time_to_output % 60),
            "milliseconds": int((time_to_output % 1) * 1000)
        }

        response_data = {
            "status": "Succeed",
            "module": module,
            "query": txt,
            "text": markdown_text,
            "Token Count": token_count,
            "Generative Time": generative_time
        }
        
        if 'translators' in request.args:
            translators = request.args['translators']
            if not txt.strip():
                translator = ts.translate_html(markdown_text, translator=ts.google, to_language=translators, n_jobs=-1)
                response_data["translator"] = translator

        Status["Succeed"] += 1
        return Response(json.dumps(response_data, indent=4, ensure_ascii=False), mimetype='application/json')

    except Exception as e:
        app.logger.error("Error occurred: %s", str(e), extra={'user_id': user_id})
        error_data = {
            "message": "An error occurred while processing your request. or refer to the ?help command for assistance.",
            "status": "ERROR",
            "error_code": 500,
            "error_type": "Critical Error",
            "text": str(e)
        }
        Status["Error"] += 1
        return Response(json.dumps(error_data, indent=4, ensure_ascii=False), mimetype='application/json')

# Utility function to get IP address
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 1))
        ip_address = s.getsockname()[0]
    except Exception as e:
        app.logger.error(f"{appname} Error {e}")
        raise ValueError(f"{appname} Error {e}")
    finally:
        s.close()
    return ip_address

if __name__ == '__main__':
    os.system("cls")
    try:
        if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
            cool_loading()
            os.system("cls")
            print(f"{COLORS['OKGREEN']}{f'[{shotappname}] ' + appname}{COLORS['ENDC']}")
            print(f"{COLORS['OKBLUE']}Made By Paopun20{COLORS['ENDC']}")
            print("")

            ip_address = get_ip_address()

            print(f"{COLORS['#800000']}WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.{COLORS['ENDC']}")
            print("")
            print(f" * Running on all addresses (0.0.0.0)")
            print(f" * Serving Flask app '{__name__}' ({f'[{shotappname}] ' + appname})")
            print("")
            print(f" * Debug mode: {COLORS['OKGREEN'] if debug_mode else COLORS['FAIL']}{debug_mode and 'on' or 'off'}{COLORS['ENDC']}")
            print(f" * Server is running at{COLORS['#808000']} http://{ip_address}:{port}{COLORS['ENDC']}")
            print("")
            print(f"{COLORS['#808000']}> Press CTRL+C to quit <{COLORS['ENDC']}")
    finally:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

        try:
            app.run(debug=debug_mode, port=port, host='0.0.0.0')
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
