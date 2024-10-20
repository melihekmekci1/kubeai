import click
import requests

@click.command()
@click.argument('query')
def ask_chatgpt(query):
    """Query ChatGPT using kubeai command."""
    # Make a request to the deployed Kubernetes service
    response = requests.post("http://0.0.0.0:8080/query", json={"query": query})
    click.echo(response.text)

if __name__ == '__main__':
    ask_chatgpt()
