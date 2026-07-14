# main.py

Converts an image into a "pixel art" text file, where each pixel becomes a
colored block character in a markup format like:

```
<b><u><color:#RRGGBB><shadow:#RRGGBB:1>█</color>...</u></b>
```

Each line of the output represents one row of the downsampled image. Handy
for editors/games that accept this kind of colored-block markup for custom
item art.

## Requirements

- Python 3
- [Pillow](https://pypi.org/project/Pillow/)

Install Pillow if you don't have it:

```
pip install Pillow
```

(If `pip` isn't recognized, try `python -m pip install Pillow`.)

## Usage

Open a command prompt in the directory of the main.py file, and your image. Then, use the following command with your own flags.

```
python3 main.py INPUT_IMAGE OUTPUT_TXT [--cols N] [--name NAME] [--max-rows N] [--resample {nearest,box}] [--no-autocrop]
```

### Example

```
python3 main.py flareon.png output.txt --cols 30 --name Flareon
```

### See all options

```
python3 main.py --help
```

## Options

| Flag | Default | Description |
|---|---|---|
| `input` | — | Path to the source image (required) |
| `output` | — | Path to write the `.txt` result to (required) |
| `--cols` | `30` | Width of the pixel grid, in characters. Row count is calculated automatically to preserve the subject's proportions. |
| `--name` | *(none)* | Optional title written as the first line of the output file (e.g. `Flareon`) |
| `--max-rows` | `18` | Caps how tall the grid can get. If the natural row count would exceed this, `--cols` is automatically reduced to compensate. Raise or lower this to match the preview box size of whatever editor you're pasting into. Set to `0` to disable the cap entirely. |
| `--resample` | `nearest` | `nearest` picks one crisp color per cell, best for art that's already pixel-art style. `box` averages colors together which is smoother, but can blur blocky source art. Use `box` for detailed/photographic art or line art with thin outlines, where `nearest` can look speckly. |
| `--no-autocrop` | off | Disables auto-cropping to the main subject. By default, the script detects the background color, crops tightly around whatever isn't background, and centers that in the output. Use this flag if you want the literal, uncropped image instead. |

## How it works

1. **Loads the image** and composites any transparency onto a white
   background (so transparent PNG areas turn white, not black).
2. **Auto-crops** to the main subject by detecting the background color from
   the image corners and cropping to the bounding box of everything that
   differs from it — this keeps the subject centered and filling the frame
   instead of floating off to one side.
3. **Downsamples** using either nearest-neighbor or box/area averaging
   (`--resample`), depending on whether the source is already blocky pixel
   art or a more detailed/anti-aliased image.
4. **Caps row count** (via `--max-rows`) by shrinking `--cols` if needed, so
   the result fits within a fixed-size preview box rather than getting cut
   off or requiring scrolling.
5. **Writes each pixel** as a `<color>`/`<shadow>` wrapped block character,
   one row per line, optionally prefixed with a `--name` title line.

## Tips

- If your output still looks clipped in your editor's preview, try lowering
  `--max-rows` (e.g. `--max-rows 14`) until it fits.
- If colors look blurry/muddy, try `--resample nearest` (the default). If
  colors look noisy/speckled instead (common with detailed line art), try
  `--resample box`.
- If a subject isn't being detected/cropped correctly (e.g. very low-contrast
  edges against the background), try `--no-autocrop` to fall back to using
  the whole image.
