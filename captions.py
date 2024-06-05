import queue
import utils
from keys import keys
from openai import AzureOpenAI, OpenAI
import typing
import queue
from io import BytesIO
import base64
import PIL.Image
import os
from tqdm.contrib.concurrent import process_map
import functools
import json
import argparse

available_clients = queue.Queue()

def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    parser.add_argument("--png-path", required=True)
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

def caption_img(path: str):
    buffered = BytesIO()
    with PIL.Image.open(path) as img:
        img.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    messages = [
        {
            "role": "system",
            "content": "Generate a detailed caption for the given image. The reader of your caption should be able to replicate this picture."
        },
        {
            "role": "user",
            "content": [{
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,%s" % image_base64},
                }
            ]
        }
    ]
    return  multi_ask(messages, model="gpt-4v")


def main():
    args = default_argument_parser().parse_args()
    init_client("gpt-4v")
    in_dir = args.png_path
    out_dir = "data/%s-gen/captions.json"%args.format
    file_list = os.listdir(in_dir)
    file_list_complete_path = []
    n = len(file_list)
    for file in file_list:
        file_list_complete_path.append(os.path.join(in_dir, file))
    captions = process_map(caption_img, file_list_complete_path)
    assert(len(captions) == n)
    result = {}
    for i in range(n):
        result[file_list[i]] = captions[i]
    json.dump(result, open("data/%s-gen/captions.json"%args.format, "w"))


if __name__ == '__main__':
    main()
