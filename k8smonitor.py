import subprocess
import requests
import json
import os
import logging
import warnings
from flask import Flask, request, Response


# Set up logging
logging.basicConfig(level=logging.ERROR)  # Set logging level to ERROR to avoid seeing warnings in the logs

# Set up your ChatGPT API URL and key
CHATGPT_API_URL = "https://api.openai.com/v1/chat/completions"
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY", "CHATGPT_API_KEY")

app = Flask(__name__)

def run_kubectl_command(command):
    """
    Function to run a kubectl command passed as a string.
    """
    # Strip code block formatting if it exists
    command = command.replace("```bash", "").replace("```", "").strip()

    # Validate the command starts with 'kubectl'
    if not command.startswith("kubectl"):
        logging.error(f"Invalid command received: {command}")
        return None

    try:
        logging.debug(f"Running command: {command}")
        result = subprocess.check_output(command.split(), stderr=subprocess.STDOUT, universal_newlines=True)
        logging.debug(f"Command output: {result}")
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running kubectl command: {e.output}")
        return None

def send_to_chatgpt(prompt):
    """
    Function to send a user query or command to ChatGPT and get a response.
    """
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an assistant who helps execute Kubernetes commands. If a kubectl command cannot be applied, please provide detailed steps for how to manually do the task."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200
    }

    logging.debug(f"Sending request to ChatGPT with prompt: {prompt}")

    response = requests.post(CHATGPT_API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        chatgpt_response = response.json()
        logging.debug(f"ChatGPT response: {chatgpt_response}")
        return chatgpt_response['choices'][0]['message']['content']
    else:
        logging.error(f"Failed to send data to ChatGPT: {response.status_code}, {response.text}")
        return f"Failed to send data to ChatGPT: {response.status_code}, {response.text}"

def get_manual_steps(query):
    """
    Get detailed manual steps from ChatGPT if kubectl command cannot be applied.
    """
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant who provides manual steps for Kubernetes users when kubectl commands fail."},
            {"role": "user", "content": query}
        ],
        "max_tokens": 300
    }

    response = requests.post(CHATGPT_API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        chatgpt_response = response.json()
        return chatgpt_response['choices'][0]['message']['content']
    else:
        return f"Failed to get manual steps from ChatGPT: {response.status_code}, {response.text}"

def prettify_output(command, command_output):
    """
    Function to format the output of kubectl command to make it more readable.
    """
    # Format output to show kubectl command followed by the output, with proper line breaks
    formatted_output = f"$ {command}\n" + command_output
    return formatted_output

@app.route('/query', methods=['POST'])
def handle_query():
    """
    API endpoint to handle queries from kubeai CLI.
    """
    request_data = request.get_json()
    user_query = request_data.get("query", "")

    logging.debug(f"Received query: {user_query}")

    # Step 1: Ask ChatGPT what kubectl command should be executed
    prompt = f"Based on the following query, what kubectl command should be run in a Kubernetes cluster? Query: {user_query}"
    chatgpt_command_suggestion = send_to_chatgpt(prompt)

    logging.debug(f"ChatGPT suggested command: {chatgpt_command_suggestion}")

    if "kubectl" in chatgpt_command_suggestion:
        # Step 2: Execute the command suggested by ChatGPT
        kubectl_command = chatgpt_command_suggestion.strip()
        command_output = run_kubectl_command(kubectl_command)

        if command_output:
            # Step 3: Prettify the output
            pretty_output = prettify_output(kubectl_command, command_output)

            # Return plain text output (no jsonify)
            return Response(pretty_output, mimetype="text/plain")
        else:
            logging.error("Failed to execute the kubectl command")
            
            # Step 4: Provide detailed manual steps as a fallback
            manual_steps = get_manual_steps(user_query)
            return Response(f"Automatic kubectl command can't be provided.\nManual steps to perform the task:\n{manual_steps}", mimetype="text/plain"), 500

    else:
        # If ChatGPT did not suggest a valid kubectl command, ask for manual steps
        logging.error("ChatGPT did not suggest a valid kubectl command. Fetching manual steps instead.")
        manual_steps = get_manual_steps(user_query)
        return Response(f"ChatGPT did not suggest a valid kubectl command.\nManual steps to perform the task:\n{manual_steps}", mimetype="text/plain"), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
