# Multi-Monitor Wallpaper Generator

A Python tool that generates combined wallpaper images for multi-monitor setups. It detects your monitor configuration
using `xrandr` and maps individual images to each screen, handling different resolutions, positions, and color profiles.

## Features

- Automatic screen detection (width, height, and relative position) via `xrandr`.
- Manual monitor specification for custom layouts.
- Batch processing - generate multiple wallpaper sets from a single image list.
- Resizes and center-crops images to perfectly fit each monitor's aspect ratio.
- Supports arbitrary monitor arrangements (horizontal, vertical, or mixed).
- Fills empty spaces with a customizable background color.
- **ICC profile conversion** - converts embedded color profiles to target profile or sRGB (essential for GNOME users).
- Multi-threaded rendering for fast batch processing.

## Requirements

- **Operating System**: Linux with X11 (required for `xrandr` support).
- **Python**: 3.x
- **System Tools**: `xrandr` (standard on most Linux distributions with X11).
- **Python Dependencies**: `Pillow` (see `requirements.txt`).

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd multi-monitor-wallpaper-gen
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Prepare your images

Create or edit the `images.txt` file in the project root. Use `# [title]` to define wallpaper sets. Each set contains
one image path per monitor (in order of screen position).

Example `images.txt`:

```text
# Wallpaper Set 1
/path/to/left_monitor.jpg
/path/to/right_monitor.png

# Wallpaper Set 2
/path/to/alternate_left.jpg
/path/to/alternate_right.png
```

The `%d` placeholder in titles auto-increments:

```text
# Wallpaper %d
/path/to/image1.jpg
/path/to/image2.png
# Wallpaper %d
/path/to/image3.jpg
/path/to/image4.png
```

### 2. Generate the wallpapers

Run the main script with auto-detected monitors:

```bash
python main.py
```

### 3. Set the wallpaper

The script generates images in the `generated/` directory (default). Set these as your wallpaper using your desktop
environment's "Span" or "Tiled" mode.

---

## Command-Line Options

| Option             | Description                                                                    | Default                |
|--------------------|--------------------------------------------------------------------------------|------------------------|
| `-i, --images`     | Path to the images config file                                                 | `./images.txt`         |
| `-o, --output-dir` | Directory for generated wallpapers                                             | `./generated`          |
| `-m, --monitor`    | Monitor specs (WxH+X+Y). Can be used multiple times. Auto-detected if omitted. | Auto-detect via xrandr |
| `-b, --background` | Background color for areas without images                                      | `black`                |
| `-t, --type`       | Output image format (`jpg` or `png`)                                           | `jpg`                  |
| `-r, --replace`    | Overwrite existing files in output directory                                   | `false`                |
| `-c, --target-icc` | ICC profile to convert images to                                               | Standard sRGB          |

### Examples

**Use custom monitor layout:**

```bash
python main.py -m 1920x1080+0+0 -m 1920x1080+1920+0
```

**Output as PNG with white background:**

```bash
 python main.py -t png -b white
```

**Use custom ICC profile:**

```bash
python main.py -c /path/to/profile.icc
```

**Force overwrite existing outputs:**

```bash
python main.py -r
```

---

## ICC Profile Handling (Important for GNOME Users)

This tool converts embedded ICC profiles in source images to the target profile (specified via `--target-icc`) or
standard sRGB if omitted.

**Why this matters:**

- GNOME does not perform color management on wallpapers - it displays them as-is
- Source images with embedded profiles (especially wide-gamut profiles) may appear washed out or incorrect on GNOME
- Pre-converting to sRGB ensures wallpapers look correct on GNOME

**Note:** Converted images may appear incorrect in some image viewers that don't handle ICC conversion properly. This is
expected - the images will display correctly as desktop wallpaper on GNOME.

---

## Project Structure

- `main.py` - CLI entry point with argparse.
- `screen.py` - Monitor detection and layout handling via `xrandr`.
- `images.txt` - Configuration file for image sets.
- `requirements.txt` - Python dependencies (`Pillow`).
- `generated/` - Default output directory for generated wallpapers.

---

## Compatibility Disclaimer

This tool was built for Linux with X11/`xrandr`. It may work on other platforms with adjustments - contributions are
welcome!
