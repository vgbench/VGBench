import queue
import utils
from keys import keys
from openai import AzureOpenAI, OpenAI
import typing
import multiprocessing
import json
from tqdm.contrib.concurrent import process_map
import functools
import argparse

available_keys = multiprocessing.Queue()


def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    return parser


def init_client(model: typing.Literal["gpt-4", "gpt-4v"]):
    for key in keys[model]:
        available_keys.put(key)


def generate(caption: str, g_type: typing.Literal["svg"]):
    messages = [
        {
            "role": "system",
            "content": "Generate a %s based on the caption below. You should output the compilable code without any additional information." % g_type
        }, {
            "role": "user",
            "content": caption
        }]
    response = utils.multi_ask(available_keys, messages)
    lines = response.split("\n")
    if lines[0].strip().startswith() == "```":
        lines = lines[1:]
        lines = lines[:-1]
    return "\n".join(lines)


def main():
    args = default_argument_parser().parse_args()
    init_client("gpt-4")
    caption_data = json.load(open("data/%s-gen/captions.json" % args.format))
    list_of_keys = []
    list_of_captions = []
    for k, v in caption_data.items():
        list_of_keys.append(k)
        list_of_captions.append(v)
    n = len(list_of_keys)
    svgs = process_map(functools.partial(
        generate, g_type=args.format), list_of_captions)
    result = {}
    for i in range(n):
        result[list_of_keys[i]] = svgs[i]

    json.dump(result, open("data/%s-gen/generated.json"%args.format, "w"))


if __name__ == '__main__':
    main()
