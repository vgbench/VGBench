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

device = "cuda" if torch.cuda.is_available() else "cpu"
# model, preprocess = clip.load('ViT-B/32', download_root="/staging/bzou24/checkpoints", device=device)
model, preprocess = longclip.load("/staging/bzou24/checkpoints/longclip-L.pt", device=device)

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
    # svg_path = "data/svg-gen/generated_svgs.json"
    png_path = "data/tikz-gen/sampled_pngs"
    caption_path = "data/tikz-gen/captions.json"
    # svg_data = json.load(open(svg_path))
    caption_data = json.load(open(caption_path))
    clip_score = 0
    for key in tqdm.tqdm(caption_data.keys()):
        # png_bytes = cairosvg.svg2png(bytestring=svg_data[key], background_color="white")
        # image = Image.open(io.BytesIO(png_bytes))
        image = Image.open(os.path.join(png_path, key))
        caption = caption_data[key]
        clip_score += evaluate_sim_img_text(image, caption)
    print(clip_score/len(caption_data.keys()))


if __name__ == '__main__':
    main()
