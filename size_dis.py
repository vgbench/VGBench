import utils
import json
import os
import argparse
import cairosvg
import PIL.Image
import io
import tqdm
import matplotlib.pyplot as plt
import numpy as np

def default_argument_parser():
    parser = argparse.ArgumentParser(description="render the original vector graphics in the dataset")
    parser.add_argument("--dataset-path", required=True)
    return parser


def main():
    args = default_argument_parser().parse_args()
    dataset = json.load(open(args.dataset_path))
    sizes = []
    for sample in dataset:
        sizes.append(len(sample['code']))
    print(np.quantile(sizes, 0))
    print(np.quantile(sizes, 0.1))
    print(np.quantile(sizes, 0.2))
    print(np.quantile(sizes, 0.3))
    print(np.quantile(sizes, 0.4))
    print(np.quantile(sizes, 0.5))
    print(np.quantile(sizes, 0.6))
    print(np.quantile(sizes, 0.7))
    print(np.quantile(sizes, 0.8))
    print(np.quantile(sizes, 0.9))
    print(np.quantile(sizes, 1))

if __name__ == '__main__':
    main()
