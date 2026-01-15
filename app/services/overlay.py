"""Brand overlay service using Pillow."""

from PIL import Image, ImageDraw, ImageFont
import os


def add_brand_overlay(image_path: str, brand_name: str, primary_color: str = "#FFFFFF") -> str:
    """
    Add brand name text overlay to the generated poster image.
    
    Args:
        image_path: Path to the generated poster image
        brand_name: Brand name to overlay (in ENGLISH)
        primary_color: Hex color for the text
        
    Returns:
        str: Path to the image with overlay
    """
    img = Image.open(image_path).convert('RGBA')
    
    # Create overlay layer
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Convert hex to RGB
    hex_color = primary_color.lstrip('#')
    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Try to load a nice font, fallback to default
    font_size = int(img.width * 0.12)  # 12% of image width
    font = None
    
    # Try common font paths
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
    
    if font is None:
        # Use default font with larger size workaround
        font = ImageFont.load_default()
        font_size = 20  # Default font is small
    
    # Calculate text position (center-top)
    text_bbox = draw.textbbox((0, 0), brand_name.upper(), font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (img.width - text_width) // 2
    y = int(img.height * 0.08)  # 8% from top
    
    # Draw shadow/outline for better visibility
    shadow_offset = max(3, font_size // 25)
    for offset_x in range(-shadow_offset, shadow_offset + 1):
        for offset_y in range(-shadow_offset, shadow_offset + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text(
                    (x + offset_x, y + offset_y), 
                    brand_name.upper(), 
                    font=font, 
                    fill=(0, 0, 0, 180)
                )
    
    # Draw main text
    draw.text((x, y), brand_name.upper(), font=font, fill=(*rgb_color, 255))
    
    # Add subtle tagline area (optional gradient bar)
    bar_height = int(img.height * 0.02)
    bar_y = y + text_height + int(img.height * 0.03)
    bar_width = int(text_width * 0.6)
    bar_x = (img.width - bar_width) // 2
    
    for i in range(bar_width):
        alpha = int(255 * (1 - abs(i - bar_width/2) / (bar_width/2)))
        draw.rectangle(
            [bar_x + i, bar_y, bar_x + i + 1, bar_y + bar_height],
            fill=(*rgb_color, alpha)
        )
    
    # Composite overlay onto original image
    result = Image.alpha_composite(img, overlay)
    
    # Convert back to RGB for saving as PNG/JPEG
    result = result.convert('RGB')
    
    output_path = '/tmp/poster_final.png'
    result.save(output_path, quality=95)
    
    return output_path
