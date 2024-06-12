import utils
import json
import os
import argparse
import cairosvg
import PIL.Image
import io
import tqdm

def default_argument_parser():
    parser = argparse.ArgumentParser(description="render the original vector graphics in the dataset")
    parser.add_argument("--dataset-path", required=True)
    parser.add_argument("--idx", type=int, required=True)
    return parser


def main():
    args = default_argument_parser().parse_args()
    dataset = json.load(open(args.dataset_path))
    print(dataset[args.idx]['code'])

if __name__ == '__main__':
    main()
