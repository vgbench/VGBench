import queue
import utils
from keys import keys
from openai import AzureOpenAI, OpenAI
import typing
import queue
import json

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


def generate(g_type: typing.Literal["svg"], caption: str):
    if g_type == "svg":
        messages = [
            {
                "role": "system",
                "content": "Generate a %s based on the caption below. You should output the compilable code without any additional information."%g_type
            },{
                "role": "user",
                "content": caption
            }]
        response = multi_ask(messages)
        return response


def main():
    init_client("gpt-4")
    caption_data = json.load(open("data/svg-gen/captions.json"))
    test_key = list(caption_data.keys())[0]
    test_caption = caption_data[test_key]
    print(generate("svg", test_caption))


if __name__ == '__main__':
    main()
