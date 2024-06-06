import queue
import utils
from keys import keys
from openai import AzureOpenAI, OpenAI
import typing
import multiprocessing
from io import BytesIO
import base64
import PIL.Image
import os
from tqdm.contrib.concurrent import process_map
import functools
import json
import argparse

available_keys = multiprocessing.Queue()


def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    parser.add_argument("--png-path", required=True)
    return parser


def init_client(model: typing.Literal["gpt-4", "gpt-4v"]):
    for key in keys[model]:
        available_keys.put(key)


def caption_img(path: str) -> str:
    buffered = BytesIO()
    with PIL.Image.open(path) as img:
        if img.size[0] > 1024 or img.size[1] > 1024:
            img = img.copy()
            img = utils.scale_image(img, 1024)

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
    return utils.multi_ask(available_keys, messages, model="gpt-4v")


def main():
    args = default_argument_parser().parse_args()
    init_client("gpt-4v")
    in_dir = args.png_path
    out_file = "data/%s-gen/captions.json" % args.format
    file_list = os.listdir(in_dir)[:200]
    file_list_complete_path = []
    n = len(file_list)
    for file in file_list:
        file_list_complete_path.append(os.path.join(in_dir, file))
    captions = []
    # for file in file_list_complete_path:
    #     captions.append(caption_img(file))
    captions = process_map(caption_img, file_list_complete_path, max_workers = 8)
    assert (len(captions) == n)
    result = {}
    for i in range(n):
        if captions[i] is not None:
            result[file_list[i]] = captions[i]
    json.dump(result, open(out_file, "w"))


if __name__ == '__main__':
    main()
