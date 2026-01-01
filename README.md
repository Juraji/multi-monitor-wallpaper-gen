# Multi-Monitor Wallpaper Generator

A Python tool that automatically generates a single combined wallpaper image for multi-monitor setups. It detects your monitor configuration using `xrandr` and maps individual images to each screen, handling different resolutions and positions.

## Features

- Automatic screen detection (width, height, and relative position).
- Resizes and center-crops images to perfectly fit each monitor's aspect ratio.
- Supports arbitrary monitor arrangements (horizontal, vertical, or mixed).
- Fills empty spaces with a customizable background color.

## Requirements

- **Operating System**: Linux (required for `xrandr` support).
- **Python**: 3.x
- **System Tools**: `xrandr` (standard on most Linux distributions with X11).

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

1. **Prepare your images**:
   Create or edit the `images.txt` file in the project root. Add the absolute or relative paths to the images you want to use, one per line. The images will be assigned to monitors based on their position (sorted primarily by vertical position, then horizontal).

   Example `images.txt`:
   ```text
   /path/to/left_monitor_bg.jpg
   /path/to/right_monitor_bg.png
   ```

2. **Generate the wallpaper**:
   Run the main script:
   ```bash
   python main.py
   ```

3. **Set the wallpaper**:
   The script generates a file named `wallpaper.jpg` in the project root. You can then set this image as your wallpaper using your desktop environment's settings (ensure you use the "Span" or "None" tiling mode so it covers all monitors correctly).

## Project Structure

- `main.py`: The entry point of the application. Handles image processing and stitching.
- `screen.py`: Contains logic for detecting screens and their dimensions via `xrandr`.
- `images.txt`: Configuration file where you list the paths to source images.
- `requirements.txt`: Lists the Python dependencies (`Pillow`).
- `wallpaper.jpg`: The default output filename (generated after running).

## Configuration

The following constants can be adjusted directly in `main.py`:

- `BG_COLOR`: The color used for areas not covered by any monitor (default: `'black'`).
- `IMAGE_SRC`: The path to the file containing image paths (default: `'./images.txt'`).
- `OUTPUT_IMG`: The path and name of the generated wallpaper (default: `"./wallpaper.jpg"`).

## Compatibility Disclaimer

"Hey, great script for X11! But what about us poor souls on Wayland? Or those stuck with Windows/MacOS?"

Look, this was built specifically for my X11 setup - I can't guarantee it'll work elsewhere without some tweaking. That said: the code is yours to play with!
Fork it, extend it, and if you manage to make it work on other platforms, I'd be thrilled to see your contributions.