import utils
import json
import os

def main():
    dataset = json.load(open("/home/zbc/research/datasets/datikz.json"))
    sample = dataset[110]
    img = utils.render_tikz(sample['code'])
    print(img)


if __name__ == '__main__':
    main()
