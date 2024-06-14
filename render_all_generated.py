import utils
import json
import os
import argparse
import cairosvg
import PIL.Image
import io
import tqdm

def default_argument_parser():
    parser = argparse.ArgumentParser(description="render generated vector graphics")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    parser.add_argument(
        "--model", choices=["gpt-4", "gpt-35-turbo", "Mixtral-8x7B-Instruct-v0.1"], default="", required=True, help="the model used to generate")
    return parser


def main():
    args = default_argument_parser().parse_args()
    dataset = json.load(open("results_gen/%s/generated_%s.json"%(args.format, args.model)))
    out_dir = "results_gen/%s/generated_pngs/%s"%(args.format, args.model)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    for k, code in tqdm.tqdm(list(dataset.items())):
        out_file_path = os.path.join(out_dir, k)
        if os.path.exists(out_file_path):
            continue
        # print(caption)
        if args.format == "svg":
            try:
                png_bytes = cairosvg.svg2png(code, background_color="white")
                img = PIL.Image.open(io.BytesIO(png_bytes))
            except:
                img = None
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
