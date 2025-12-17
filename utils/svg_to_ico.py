#!/usr/bin/env python3
"""
Convert SVG favicons to ICO format for browser compatibility.
"""
import os
import sys
from PIL import Image
import cairosvg
import tempfile

def svg_to_ico(svg_path, ico_path, sizes=(16, 32, 48, 64)):
    """Convert SVG file to ICO with multiple sizes."""
    print(f"Converting {svg_path} to {ico_path}...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Convert SVG to PNG for each size
        png_files = []
        for size in sizes:
            png_path = os.path.join(tmpdir, f"temp_{size}x{size}.png")
            cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)
            png_files.append((png_path, size))
        
        # Open PNG files and create ICO
        images = [Image.open(png_path).convert('RGBA') for png_path, size in png_files]
        
        # Save as ICO
        images[0].save(ico_path, format='ICO', append_images=images[1:], sizes=[(size, size) for _, size in png_files])
        
    print(f"Successfully created {ico_path}")

if __name__ == "__main__":
    # Convert all favicon SVG files to ICO
    image_dir = "content/image"
    svg_files = [f for f in os.listdir(image_dir) if f.startswith('favicon-') and f.endswith('.svg')]
    
    if not svg_files:
        print("No favicon SVG files found in content/image/")
        sys.exit(0)
    
    for svg_file in svg_files:
        svg_path = os.path.join(image_dir, svg_file)
        ico_file = svg_file.replace('.svg', '.ico')
        ico_path = os.path.join(image_dir, ico_file)
        svg_to_ico(svg_path, ico_path)
    
    print("\nAll conversions completed!")