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
# model, preprocess = clip.load('ViT-B/32', download_root="/staging/bzou24/checkpoints", device=device)
model, preprocess = longclip.load("/staging/bzou24/checkpoints/longclip-L.pt", device=device)

def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--format", choices=["svg", "tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")
    parser.add_argument("--png-path", required=True)

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
    # svg_path = "data/svg-gen/generated_svgs.json"
    caption_path = "data/%s-gen/captions.json"%args.format
    # svg_data = json.load(open(svg_path))
    caption_data = json.load(open(caption_path))
    clip_score = 0
    for key in tqdm.tqdm(caption_data.keys()):
        image = Image.open(os.path.join(args.png_path, key))
        caption = caption_data[key]
        clip_score += evaluate_sim_img_text(image, caption)
    print(clip_score/len(caption_data.keys()))


if __name__ == '__main__':
    main()
