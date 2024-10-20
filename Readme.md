Documentation for kubeai Kubernetes Assistant
Overview
kubeai is a command-line tool that interacts with a Flask-based API to assist Kubernetes users by executing kubectl commands or providing manual steps for Kubernetes operations. The tool integrates with OpenAI's GPT models to interpret user queries, suggest commands, and handle errors. If a command cannot be executed, it returns detailed steps to perform the task manually.

Features
Accepts user queries related to Kubernetes operations.
Suggests and runs kubectl commands in a Kubernetes cluster based on user input.
Provides manual steps for performing tasks when kubectl commands cannot be applied.
Logs errors and issues for troubleshooting.
Components
1. kubeai.py
The kubeai.py script is the client CLI tool that interacts with the Flask API running in a Kubernetes cluster. It sends queries from the user to the Flask API, which then processes them and returns the result.

2. Flask API (kubeai_server.py)
The Flask-based API receives requests from the CLI, processes the input with the help of ChatGPT, executes kubectl commands, and sends back the results.

3. ChatGPT API Integration
The API integrates with OpenAI's GPT models (e.g., gpt-3.5-turbo) to interpret user queries and suggest Kubernetes commands. If a kubectl command cannot be executed, the model provides detailed manual steps.

Installation
Prerequisites
Python 3.x
pip for installing required packages
kubectl installed and configured for your Kubernetes cluster
OpenAI API key (set as an environment variable CHATGPT_API_KEY)
Step 1: Setup the CLI Tool
Modify setup.py
Ensure that your setup.py file is configured as follows:

python
Copy code
from setuptools import setup, find_packages

setup(
    name='kubeai',
    version='1.0',
    py_modules=['kubeai'],
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        kubeai=kubeai:ask_chatgpt
    ''',
)
This allows the script kubeai.py to be installed as a system-wide executable that you can invoke using the kubeai command.

Installation
Build the package by running:

bash
Copy code
python3 setup.py sdist bdist_wheel
Install the package:

bash
Copy code
pip install .
This will install the kubeai command globally, and you can run it from any location in your terminal.

Step 2: Set Up Flask API Server (kubeai_server.py)
Install Dependencies
Install the required Python dependencies:

bash
Copy code
pip install flask requests
Set Up Environment Variables
Ensure the environment variable CHATGPT_API_KEY is set with your OpenAI API key:

bash
Copy code
export CHATGPT_API_KEY="your-openai-api-key"
Running the Flask Server
Run the Flask API server with:

bash
Copy code
python kubeai_server.py
This will start the server on http://0.0.0.0:80.

You can test the API locally by sending POST requests to http://localhost/query with the query payload.

Step 3: Deploy Flask API Server on Kubernetes
Create a Dockerfile for containerizing the Flask API server:

Dockerfile
Copy code
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV CHATGPT_API_KEY="your-openai-api-key"

CMD ["python", "kubeai_server.py"]
Build and push the Docker image:

bash
Copy code
docker build -t your-docker-repo/kubeai-server .
docker push your-docker-repo/kubeai-server
Create a Kubernetes deployment YAML file:

yaml
Copy code
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubeai-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kubeai-server
  template:
    metadata:
      labels:
        app: kubeai-server
    spec:
      containers:
      - name: kubeai-server
        image: your-docker-repo/kubeai-server
        ports:
        - containerPort: 80
        env:
        - name: CHATGPT_API_KEY
          valueFrom:
            secretKeyRef:
              name: chatgpt-api-secret
              key: api_key
Apply the deployment:

bash
Copy code
kubectl apply -f kubeai-server-deployment.yaml
Usage
CLI Usage
Once the kubeai command-line tool is installed, you can use it to query Kubernetes via ChatGPT:

bash
Copy code
kubeai "what are pods in default namespace"
The CLI tool will send the query to the deployed Flask API, which will then query ChatGPT, execute the suggested kubectl command, and return the output.

API Usage
The Flask API exposes a /query endpoint that accepts POST requests. You can send a JSON payload with a query field, and the API will respond with either the kubectl command output or manual steps.

Example request:

bash
Copy code
curl -X POST http://localhost/query -H "Content-Type: application/json" -d '{"query": "List all pods in default namespace"}'
Example response:

sql
Copy code
$ kubectl get pods --namespace=default
NAME           READY   STATUS    RESTARTS   AGE
example-pod1   1/1     Running   0          1d
example-pod2   1/1     Running   0          2d
If the kubectl command fails or cannot be executed, the API will provide manual steps.

Logging
The Flask API logs all errors to help with debugging. You can find the logs in your Kubernetes cluster or container logs. It is set to ERROR level by default to minimize noise.

To enable more detailed logging, you can set the log level to DEBUG in the kubeai_server.py file:

python
Copy code
logging.basicConfig(level=logging.DEBUG)
Error Handling
If ChatGPT does not suggest a valid kubectl command, the API will return a response with manual steps to follow.
If kubectl commands fail, detailed manual steps will be returned to the user.
Conclusion
kubeai provides a powerful interface for Kubernetes users by combining the functionality of kubectl with the intelligence of OpenAI’s GPT models. This allows users to seamlessly manage their Kubernetes clusters or receive guidance when commands fail.