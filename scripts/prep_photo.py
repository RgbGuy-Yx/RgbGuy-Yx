#!/usr/bin/env python3
"""
Pre-processes an input photo for terminal ASCII art rendering.
1. Removes background using rembg.
2. Composites subject over pure-white (#FFFFFF) background.
3. Applies CLAHE (Contrast-Limited Adaptive Histogram Equalization) via OpenCV to sharpen facial mid-tones and highlights.
4. Outputs data/source-prepped.png.
"""

import argparse
import os
import sys
import numpy as np
from PIL import Image
import cv2
import rembg


def parse_arguments():
    parser = argparse.ArgumentParser(description="Pre-process photo for ASCII art generator.")
    parser.add_argument(
        "--input",
        default="data/source-photo.jpg",
        help="Path to source input photo (default: data/source-photo.jpg)"
    )
    parser.add_argument(
        "--output",
        default="data/source-prepped.png",
        help="Path to save prepped image (default: data/source-prepped.png)"
    )
    parser.add_argument(
        "--model",
        default="u2netp",
        help="rembg model name (default: u2netp for lightweight fast processing)"
    )
    return parser.parse_args()


def process_photo(input_path: str, output_path: str, model_name: str = "u2netp"):
    if not os.path.exists(input_path):
        # Check fallback to source-photo.jpg in root
        if os.path.exists("source-photo.jpg"):
            input_path = "source-photo.jpg"
        else:
            raise FileNotFoundError(f"Source photo not found at: {input_path}")

    print(f"[*] Opening source photo: {input_path}")
    img = Image.open(input_path)

    # Convert to RGBA
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    print(f"[*] Removing background using rembg (model: {model_name})...")
    session = rembg.new_session(model_name)
    no_bg = rembg.remove(img, session=session)

    print("[*] Compositing subject over pure-white (#FFFFFF) background...")
    white_bg = Image.new("RGBA", no_bg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, no_bg).convert("RGB")

    print("[*] Applying CLAHE via OpenCV to sharpen facial mid-tones & highlights...")
    rgb_arr = np.array(composited)
    
    # Convert to LAB color space
    lab = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.8, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    # Merge channels and convert back to RGB
    enhanced_lab = cv2.merge((cl, a_channel, b_channel))
    final_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    out_img = Image.fromarray(final_rgb)
    out_img.save(output_path, "PNG")
    print(f"[+] Preprocessed image saved to: {output_path} (size: {out_img.size})")


def main():
    args = parse_arguments()
    process_photo(args.input, args.output, args.model)


if __name__ == "__main__":
    main()
