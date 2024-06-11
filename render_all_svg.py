import utils
import json
import os
import cairosvg
import PIL.Image
import io

def main():
    dataset = json.load(open("/home/zbc/research/datasets/svg.json"))
    
    for idx in range(0, len(dataset)):
        sample = dataset[idx]
        code = sample['code']
        caption = sample['caption']
        out_file_path = os.path.join("pngs/svg", "%d.png"%idx)
        if os.path.exists(out_file_path):
            continue
        # print(caption)
        png_bytes = cairosvg.svg2png(code, background_color="white")
        img = PIL.Image.open(io.BytesIO(png_bytes))
        if img == None:
            continue
        img.save(out_file_path)
        


if __name__ == '__main__':
    main()
