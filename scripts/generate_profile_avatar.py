from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = 640
OUT = Path(__file__).resolve().parents[1] / "images" / "profile-avatar.png"


def load_font(size):
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    image = Image.new("RGB", (SIZE, SIZE), (247, 248, 244))
    draw = ImageDraw.Draw(image)

    draw.ellipse((28, 28, SIZE - 28, SIZE - 28), fill=(31, 63, 53))
    draw.ellipse((68, 68, SIZE - 68, SIZE - 68), outline=(91, 135, 118), width=3)

    for offset in (-150, -75, 0, 75, 150):
        draw.line((SIZE // 2 + offset, 105, SIZE // 2 + offset, 535), fill=(48, 82, 70), width=2)
        draw.line((105, SIZE // 2 + offset, 535, SIZE // 2 + offset), fill=(48, 82, 70), width=2)

    font = load_font(190)
    text = "WH"
    box = draw.textbbox((0, 0), text, font=font)
    x = (SIZE - (box[2] - box[0])) / 2
    y = (SIZE - (box[3] - box[1])) / 2 - box[1]
    draw.text((x, y), text, font=font, fill=(244, 247, 242))

    image.save(OUT, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
