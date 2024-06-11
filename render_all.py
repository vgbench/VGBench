import utils
import json
import os
import argparse
import cairosvg
import PIL.Image
import io

def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    parser.add_argument("--dataset-path", required=True)
    return parser


def main():
    args = default_argument_parser().parse_args()
    dataset = json.load(open(args.dataset_path))
    for idx in range(491, len(dataset)):
        print(idx)
        sample = dataset[idx]
        code = sample['code']
        caption = sample['caption']
        out_file_path = os.path.join("pngs/%s"%args.format, "%d.png"%idx)
        if os.path.exists(out_file_path):
            continue
        # print(caption)
        if args.format == "svg":
            png_bytes = cairosvg.svg2png(code, background_color="white")
            img = PIL.Image.open(io.BytesIO(png_bytes))
        elif args.format == "tikz":
            img = utils.render_tikz(code)
        elif args.format =="graphviz":
            img = utils.render_graphviz(code)
        else:
            raise "Unknown format"
        if img == None:
            continue
        img.save(out_file_path)
        

if __name__ == '__main__':
    main()
