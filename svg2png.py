import os
import cairosvg
import random
from tqdm import tqdm

def convert_svg_to_png(source_dir, target_dir, width, height):
    # Create target directory if it does not exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Walk through the source directory
    for root, dirs, files in tqdm(os.walk(source_dir)):
        # Determine the current directory's structure in the target directory
        relative_path = os.path.relpath(root, source_dir)
        target_path = os.path.join(target_dir, relative_path)

        # Create corresponding directory in the target directory structure
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        # Convert each SVG file in the current directory to PNG
        for file in tqdm(files):
            if file.endswith(".svg"):
            #     if random.random() > 0.01:
            #         continue
                svg_file_path = os.path.join(root, file)
                png_file_name = file[:-4] + ".png"  # Change file extension
                png_file_path = os.path.join(target_path, png_file_name)

                # Convert SVG to PNG
                try:
                    cairosvg.svg2png(url=svg_file_path, write_to=png_file_path,background_color="white")
                except Exception as e:
                    pass
            #      output_width=width, output_height=height
                # breakpoint()
# Example usage
source_directory = 'data/svg-gen/sampled_results'  # Update this path
target_directory = 'data/svg-gen/sampled_pngs'  # Update this path
output_width = 1024
output_height = 768

convert_svg_to_png(source_directory, target_directory, output_width, output_height)
