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
import os

available_keys = multiprocessing.Queue()


def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    parser.add_argument(
        "--model", choices=["gpt-4", "gpt-35-turbo", "Mixtral-8x7B-Instruct-v0.1"], default="", required=True, help="the model used to generate")

    return parser


def init_client(model: typing.Literal["gpt-4", "gpt-35-turbo", "Mixtral-8x7B-Instruct-v0.1"]):
    for key in keys[model]:
        available_keys.put(key)


def generate(caption: str, g_type: typing.Literal["svg", "tikz", "graphviz"], model: typing.Literal["gpt-4", "gpt-35-turbo", "Mixtral-8x7B-Instruct-v0.1"]):
    messages = [
        {
            "role": "system",
            "content": "Generate a %s based on the caption below. You should output the compilable code without any additional information." % g_type
        }, {
            "role": "user",
            "content": caption
        }]
    response = utils.multi_ask(available_keys, messages, model=model)
    if response == None:
        return ""
    lines = response.split("\n")
    if lines[0].strip().startswith("```"):
        lines = lines[1:]
        lines = lines[:-1]
    result =  "\n".join(lines)
    
    return result

def generate_wrapper(args: typing.Tuple[str, str], g_type: typing.Literal["svg", "tikz", "graphviz"], model: typing.Literal["gpt-4", "gpt-35-turbo", "Mixtral-8x7B-Instruct-v0.1"]) -> str:
    caption, filename = args
    target_file = os.path.join("results_gen/%s/tmp_generated/%s"%(g_type, model), filename)+".txt"
    if os.path.exists(target_file):
        with open(target_file) as file:
            result = file.read()
    else:
        result = generate(caption, g_type, model=model)
        with open(target_file, "w") as file:
            file.write(result)
        print(target_file)

    return result


def main():
    args = default_argument_parser().parse_args()
    init_client(args.model)
    caption_data = json.load(open("data/%s/captions.json" % args.format))
    list_of_keys = []
    list_of_captions = []
    for k, v in caption_data.items():
        list_of_keys.append(k)
        list_of_captions.append(v)
    n = len(list_of_keys)
    svgs = process_map(functools.partial(
        generate_wrapper, g_type=args.format, model=args.model), list(zip(list_of_captions, list_of_keys)), chunksize=1, max_workers=8)
    result = {}
    for i in range(n):
        result[list_of_keys[i]] = svgs[i]

    json.dump(result, open("results_gen/%s/generated_%s.json"%(args.format, args.model), "w"))


if __name__ == '__main__':
    main()
