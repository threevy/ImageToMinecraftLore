import argparse
from pathlib import Path
from PIL import Image, ImageChops


def detect_bg_color(img, sample=6):
    w, h = img.size
    sample = max(1, min(sample, w // 2, h // 2))
    corners = [
        (0, 0, sample, sample),
        (w - sample, 0, w, sample),
        (0, h - sample, sample, h),
        (w - sample, h - sample, w, h),
    ]
    counts = {}
    for box in corners:
        for px in img.crop(box).getdata():
            counts[px] = counts.get(px, 0) + 1
    return max(counts, key=counts.get)


def autocrop_to_subject(img, bg_color, threshold=24, padding_frac=0.06):
    bg_layer = Image.new("RGB", img.size, bg_color)
    diff = ImageChops.difference(img, bg_layer).convert("L")
    mask = diff.point(lambda p: 255 if p > threshold else 0)
    bbox = mask.getbbox()

    if bbox is None:
        return img

    left, top, right, bottom = bbox
    w, h = img.size
    pad_x = int((right - left) * padding_frac)
    pad_y = int((bottom - top) * padding_frac)
    left = max(0, left - pad_x)
    top = max(0, top - pad_y)
    right = min(w, right + pad_x)
    bottom = min(h, bottom + pad_y)
    return img.crop((left, top, right, bottom))


RESAMPLE_METHODS = {
    "nearest": Image.NEAREST,
    "box": Image.BOX,
}


def build_pixel_grid(image_path, cols, char_aspect=1.0, autocrop=True, max_rows=None,
                      resample="nearest"):
    img = Image.open(image_path).convert("RGBA")

    background = Image.new("RGBA", img.size, (255, 255, 255, 255))
    img = Image.alpha_composite(background, img).convert("RGB")

    if autocrop:
        bg_color = detect_bg_color(img)
        img = autocrop_to_subject(img, bg_color)

    w, h = img.size
    rows = max(1, round((h / w) * cols / char_aspect))

    if max_rows and rows > max_rows:
        cols = max(1, round(cols * max_rows / rows))
        rows = max(1, round((h / w) * cols / char_aspect))

    small = img.resize((cols, rows), RESAMPLE_METHODS[resample])

    pixels = small.load()
    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            row.append(pixels[x, y])
        grid.append(row)
    return grid


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def grid_to_text(grid, name=None):
    lines = []
    if name:
        lines.append(name)

    for row in grid:
        cells = []
        for rgb in row:
            hexcolor = rgb_to_hex(rgb)
            cells.append(f"<color:{hexcolor}><shadow:{hexcolor}:1>█</color>")
        line = "<b><u>" + "".join(cells) + "</u></b>"
        lines.append(line)

    return "\n".join(lines)


def convert(image_path, output_path, cols=30, name=None, autocrop=True, max_rows=18,
            resample="nearest"):
    grid = build_pixel_grid(image_path, cols, autocrop=autocrop, max_rows=max_rows,
                             resample=resample)
    text = grid_to_text(grid, name=name)
    Path(output_path).write_text(text, encoding="utf-8")
    print(f"Wrote {len(grid)} rows x {len(grid[0])} cols -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert an image to pixel-art text.")
    parser.add_argument("input", help="Path to the input image")
    parser.add_argument("output", help="Path to the output .txt file")
    parser.add_argument("--cols", type=int, default=30, help="Number of columns (pixel width)")
    parser.add_argument("--name", type=str, default=None, help="Optional name/title as first line")
    parser.add_argument("--no-autocrop", action="store_true",
                         help="Disable auto-cropping/centering the main subject")
    parser.add_argument("--max-rows", type=int, default=18,
                         help="Cap on row count; cols is auto-reduced to stay within it "
                              "(set to 0 to disable the cap)")
    parser.add_argument("--resample", choices=["nearest", "box"], default="nearest",
                         help="nearest = crisp/blocky (best for art that's already pixel-art "
                              "style); box = averaged/smoother (better for detailed photos or "
                              "line art with thin outlines)")
    args = parser.parse_args()

    convert(args.input, args.output, cols=args.cols, name=args.name,
            autocrop=not args.no_autocrop, max_rows=(args.max_rows or None),
            resample=args.resample)


if __name__ == "__main__":
    main()
