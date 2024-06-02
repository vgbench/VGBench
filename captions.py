import queue
import utils
from keys import keys
from openai import AzureOpenAI, OpenAI
import typing
import queue

available_clients = queue.Queue()


def multi_ask(messages, model="gpt-4"):
    success = False
    while not success:
        client = available_clients.get()
        try:
            response = utils.ask_gpt(client, messages, model=model)
            success = True
        except Exception as e:
            print(e)
            continue
        available_clients.put(client)
        break
    return response


def init_client(model: typing.Literal["gpt-4", "gpt-4v"]):
    for key in keys[model]:
        available_clients.put(AzureOpenAI(
            api_version="2024-02-01",
            azure_endpoint=key["GPT_ENDPOINT"],
            api_key=key["GPT_KEY"]
        ))

def main():
    init_client("gpt-4")
    generate("svg")


if __name__ == '__main__':
    main()
