import utils
import json
import os

def main():
    dataset = json.load(open("/home/zbc/research/datasets/datikz.json"))
    for i, sample in enumerate(dataset):
        print(i)
        code = sample['code']
        caption = sample['caption']
        out_file_path = os.path.join("pngs", "%d.png"%i)
        if os.path.exists(out_file_path):
            continue
        # print(caption)
        img = utils.render_tikz(code)
        if img == None:
            continue
        img.save(out_file_path)
        


if __name__ == '__main__':
    main()
