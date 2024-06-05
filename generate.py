import queue
import utils
from keys import keys
from openai import AzureOpenAI, OpenAI
import typing
import queue
import json
from tqdm.contrib.concurrent import process_map
import functools
import argparse

available_clients = queue.Queue()

def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    return parser


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


def generate(caption: str, g_type: typing.Literal["svg"]):
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
        lines = response.split("\n")
        if lines[0].strip() == "```svg":
            lines = lines[1:]
            lines = lines[:-1]
        return "\n".join(lines)


def main():
    args = default_argument_parser().parse_args()
    init_client("gpt-4")
    caption_data = json.load(open("data/%s-gen/captions.json"%args.format))
    list_of_keys = []
    list_of_captions = []
    for k, v in caption_data.items():
        list_of_keys.append(k)
        list_of_captions.append(v)
    n = len(list_of_keys)
    svgs = process_map(functools.partial(generate, g_type=args.format), list_of_captions)
    result = {}
    for i in range(n):
        result[list_of_keys[i]] = svgs[i]

    json.dump(result, open("data/svg-gen/generated_svgs.json", "w"))


if __name__ == '__main__':
    main()
