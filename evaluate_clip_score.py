import sys
# sys.path.insert(0, '/home/bzou24/Long-CLIP')
sys.path.insert(0, 'Long-CLIP')
from model import longclip
import json
import cairosvg
from PIL import Image
import io
import torch
import tqdm
import os
import argparse

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = longclip.load("longclip-L.pt", device=device)

def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    parser.add_argument("--png-path", required=True)
    return parser

def evaluate_sim_img_text(img: Image, caption: str):
    image_processed = preprocess(img).unsqueeze(0).to(device)
    text_input = longclip.tokenize([caption], truncate=True).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image_processed)
        text_features = model.encode_text(text_input)
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    clip_score = torch.matmul(image_features, text_features.T).item()
    return clip_score


def main():
    args = default_argument_parser().parse_args()
    # svg_path = "results_gen/svg/generated_svgs.json"
    caption_path = "data/%s/captions.json"%args.format
    # svg_data = json.load(open(svg_path))
    caption_data = json.load(open(caption_path))
    clip_score = 0
    cnt = 0
    for key in tqdm.tqdm(caption_data.keys()):
        img_path = os.path.join(args.png_path, key)
        if not os.path.exists(img_path):
            print("[WARNING] %s not found"%img_path)
            continue
        image = Image.open(img_path)
        caption = caption_data[key]
        clip_score += evaluate_sim_img_text(image, caption)
        cnt += 1
    print(clip_score/cnt)


if __name__ == '__main__':
    main()

