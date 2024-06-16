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
import seaborn as sns
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches

def default_argument_parser():
    parser = argparse.ArgumentParser(description="render the original vector graphics in the dataset")
    parser.add_argument("--dataset-path", required=True)
    parser.add_argument("--format", required=True)
    return parser


def main():
    args = default_argument_parser().parse_args()
    dataset = json.load(open(args.dataset_path))[0:2000]
    sizes = []
    # plt.figure(figsize=(12,6))
    for idx, sample in enumerate(dataset):
        sizes.append(len(sample['code']))
    # print(np.quantile(sizes, 0))
    # print(np.quantile(sizes, 0.1))
    # print(np.quantile(sizes, 0.2))
    # print(np.quantile(sizes, 0.3))
    # print(np.quantile(sizes, 0.4))
    # print(np.quantile(sizes, 0.5))
    # print(np.quantile(sizes, 0.6))
    # print(np.quantile(sizes, 0.7))
    # print(np.quantile(sizes, 0.8))
    # print(np.quantile(sizes, 0.9))
    # print(np.quantile(sizes, 1))
    colors = sns.color_palette()
    handles = []
    handles.append(mpatches.Patch(color=colors[0], label="All types"))
    sns.histplot(sizes, alpha=0, log_scale=True, kde=True, element='step', fill=False, color=colors[0])
    data_dir = "data/%s/"%args.format
    cnt = 0
    for file in os.listdir(data_dir):
        if not file.startswith("final_dataset_") or not file.endswith(".json"):
            continue
        qtype = file.split(".")[0].split("_")[2]
        print(qtype)
        sizes = []
        with open(os.path.join(data_dir, file)) as f:
            data = json.load(f)
            for sample in data:
                sizes.append(len(sample['data']['code']))
        cnt += 1
        handles.append(mpatches.Patch(color=colors[cnt], label=qtype.capitalize()))
        sns.histplot(sizes, alpha=0, log_scale=True, kde=True, element='step', fill=False, color=colors[cnt])
    # plt.legend()
    # plt.xlabel("The number of characters in the vector graphics code")
    plt.ylabel("The number of samples")
    plt.legend(handles=handles)
    plt.savefig("%s_dis.pdf"%args.format)
    plt.show()

if __name__ == '__main__':
    main()
