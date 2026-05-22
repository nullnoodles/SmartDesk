"""Generate the SmartDesk application icon programmatically.

Creates a modern, aesthetic icon with a gradient background and 'S' lettermark.
Outputs: assets/icon.ico (multi-size) and assets/icon.png (256x256).
"""
import sys
sys.path.insert(0, ".")

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)


def create_icon():
    """Generate a modern gradient icon with an S lettermark."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background with gradient effect
    # Base: deep blue-purple gradient
    for y in range(size):
        ratio = y / size
        r = int(30 + (89 - 30) * ratio)   # 1e → 59
        g = int(30 + (60 - 30) * ratio)    # 1e → 3c
        b = int(46 + (180 - 46) * ratio)   # 2e → b4
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Apply rounded corners mask
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (size - 1, size - 1)], radius=48, fill=255)
    img.putalpha(mask)

    # Draw the "S" lettermark
    # Try to use a bold system font, fallback to default
    font_size = 160
    font = None
    font_paths = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, font_size)
            break
        except (OSError, IOError):
            continue

    if font is None:
        font = ImageFont.load_default()

    # Draw S with a slight glow effect
    letter = "S"
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2 - bbox[0]
    y = (size - text_h) // 2 - bbox[1] - 5

    # Glow layer
    draw.text((x, y), letter, fill=(137, 180, 250, 80), font=font)
    # Main letter - white
    draw.text((x - 1, y - 1), letter, fill=(255, 255, 255, 240), font=font)

    # Small accent dot (bottom-right)
    dot_x, dot_y = size - 55, size - 55
    draw.ellipse([(dot_x, dot_y), (dot_x + 20, dot_y + 20)], fill=(166, 227, 161, 200))

    # Save PNG
    png_path = ASSETS_DIR / "icon.png"
    img.save(str(png_path), "PNG")
    print(f"Saved: {png_path}")

    # Save ICO (multi-size for Windows)
    ico_path = ASSETS_DIR / "icon.ico"
    # Create multiple sizes
    sizes_list = [16, 24, 32, 48, 64, 128, 256]
    icons = []
    for s in sizes_list:
        resized = img.resize((s, s), Image.LANCZOS)
        icons.append(resized)

    icons[0].save(
        str(ico_path),
        format="ICO",
        sizes=[(s, s) for s in sizes_list],
        append_images=icons[1:],
    )
    print(f"Saved: {ico_path}")

    # Also save a splash image (wider)
    splash = Image.new("RGBA", (600, 350), (0, 0, 0, 0))
    splash_draw = ImageDraw.Draw(splash)

    # Gradient background
    for y in range(350):
        ratio = y / 350
        r = int(24 + (30 - 24) * ratio)
        g = int(24 + (30 - 24) * ratio)
        b = int(36 + (50 - 36) * ratio)
        splash_draw.line([(0, y), (600, y)], fill=(r, g, b, 255))

    # Rounded rect mask
    splash_mask = Image.new("L", (600, 350), 0)
    splash_mask_draw = ImageDraw.Draw(splash_mask)
    splash_mask_draw.rounded_rectangle([(0, 0), (599, 349)], radius=20, fill=255)
    splash.putalpha(splash_mask)

    # Paste icon
    icon_small = img.resize((80, 80), Image.LANCZOS)
    splash.paste(icon_small, (260, 80), icon_small)

    # App name
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
        sub_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    splash_draw.text((210, 175), "SmartDesk", fill=(205, 214, 244, 255), font=title_font)
    splash_draw.text((195, 220), "Freelancer Management System", fill=(166, 173, 200, 255), font=sub_font)
    splash_draw.text((245, 290), "Loading...", fill=(137, 180, 250, 200), font=sub_font)

    splash_path = ASSETS_DIR / "splash.png"
    splash.save(str(splash_path), "PNG")
    print(f"Saved: {splash_path}")


if __name__ == "__main__":
    create_icon()
