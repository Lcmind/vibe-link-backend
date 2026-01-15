"""Brand overlay service using Pillow - Professional Grade."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os


def analyze_image_colors(img: Image.Image) -> dict:
    """Analyze the top portion of image to determine best text color."""
    # Crop top 20% of image where text will be placed
    top_region = img.crop((0, 0, img.width, int(img.height * 0.2)))
    
    # Resize for faster processing
    small = top_region.resize((50, 10))
    
    # Get average color
    pixels = list(small.getdata())
    avg_r = sum(p[0] for p in pixels) // len(pixels)
    avg_g = sum(p[1] for p in pixels) // len(pixels)
    avg_b = sum(p[2] for p in pixels) // len(pixels)
    
    avg_luminance = (0.299 * avg_r + 0.587 * avg_g + 0.114 * avg_b) / 255
    
    return {
        'avg_color': (avg_r, avg_g, avg_b),
        'luminance': avg_luminance,
        'is_dark': avg_luminance < 0.5
    }


def add_brand_overlay(image_path: str, brand_name: str, primary_color: str = "#FFFFFF", mood: str = "professional") -> str:
    """
    Add brand name text overlay with professional styling that matches the image.
    
    Args:
        image_path: Path to the generated poster image
        brand_name: Brand name to overlay (in ENGLISH)
        primary_color: Hex color for the text (brand color)
        mood: The mood/style of the poster
        
    Returns:
        str: Path to the image with overlay
    """
    img = Image.open(image_path).convert('RGBA')
    
    # Analyze image to determine best text approach
    color_analysis = analyze_image_colors(img)
    
    # Create overlay layer
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Determine text color based on image analysis
    if color_analysis['is_dark']:
        text_color = (255, 255, 255)  # White text on dark
        shadow_color = (0, 0, 0, 200)
        glass_fill = (0, 0, 0, 80)
    else:
        text_color = (20, 20, 30)  # Dark text on light
        shadow_color = (255, 255, 255, 200)
        glass_fill = (255, 255, 255, 120)
    
    # Font sizing - responsive to image width
    font_size = int(img.width * 0.08)  # 8% of width (more elegant)
    font = None
    
    # Try to load professional fonts
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
    
    if font is None:
        font = ImageFont.load_default()
        font_size = 20
    
    # Calculate text position
    text = brand_name.upper()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (img.width - text_width) // 2
    y = int(img.height * 0.05)  # 5% from top
    
    # Create frosted glass background for text
    glass_padding_x = int(text_width * 0.12)
    glass_padding_y = int(text_height * 0.4)
    
    glass_left = x - glass_padding_x
    glass_top = y - glass_padding_y
    glass_right = x + text_width + glass_padding_x
    glass_bottom = y + text_height + glass_padding_y
    
    # Draw rounded rectangle background
    draw.rounded_rectangle(
        [glass_left, glass_top, glass_right, glass_bottom],
        radius=10,
        fill=glass_fill
    )
    
    # Subtle border
    draw.rounded_rectangle(
        [glass_left, glass_top, glass_right, glass_bottom],
        radius=10,
        outline=(*text_color[:3], 40),
        width=1
    )
    
    # Draw text shadow
    shadow_offset = max(1, font_size // 50)
    draw.text(
        (x + shadow_offset, y + shadow_offset), 
        text, 
        font=font, 
        fill=shadow_color
    )
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=(*text_color, 255))
    
    # Composite overlay onto original image
    result = Image.alpha_composite(img, overlay)
    
    # Convert back to RGB for saving
    result = result.convert('RGB')
    
    output_path = '/tmp/poster_final.png'
    result.save(output_path, quality=95)
    
    return output_path
