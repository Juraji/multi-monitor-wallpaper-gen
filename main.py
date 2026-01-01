from PIL import Image
from PIL.Image import Resampling

from screen import get_xrandr_screens

BG_COLOR = 'black'
IMAGE_SRC = './images.txt'
OUTPUT_IMG = "./wallpaper.jpg"

if __name__ == '__main__':
    # Read and validate image paths from file
    try:
        with open(IMAGE_SRC, 'r') as f:
            images = [line.strip() for line in f.readlines() if line.strip()]
        print(f"Found {len(images)} valid image paths")
    except FileNotFoundError:
        print(f"Error: {IMAGE_SRC} not found.")
        exit(1)
    except Exception as e:
        print(f"Error reading {IMAGE_SRC}: {e}")
        exit(1)

    # Get active screens configuration
    try:
        screens = get_xrandr_screens()
        print(f"Found {len(screens)} active screens: {screens}")
    except RuntimeError as e:
        print(f"Error getting screen information: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error getting screens: {e}")
        exit(1)

    # Check if we have enough images for all screens and vice versa, else print a warning.
    if len(screens) > len(images):
        print(f"Warning: More screens ({len(screens)}) than images. Extra screens will use background color.")
    elif len(images) > len(screens):
        print(f"Info: More images ({len(images)}) than screens ({len(screens)}). Extra images will be ignored.")

    # Calculate total dimensions needed for the combined image
    min_x = min(s.x_pos for s in screens)
    min_y = min(s.y_pos for s in screens)
    max_x = max(s.x_pos + s.width for s in screens)
    max_y = max(s.y_pos + s.height for s in screens)
    total_width = int(max_x - min_x)
    total_height = int(max_y - min_y)

    print(f"Total screen area: {total_width}x{total_height}")

    base_image = Image.new('RGB', (total_width, total_height), color=BG_COLOR)

    for index, screen in enumerate(screens):
        if index >= len(images):
            break  # No more images to use
        image_path = images[index]

        print(f"Processing '{image_path}' for screen {index}...")

        try:
            img = Image.open(image_path)
        except Exception as e:
            print(f"Warning: Could not open {image_path}. Error: {e}")
            continue  # Skip to next screen if image fails to load

        # Calculate position on base image
        left = int(screen.x_pos - min_x)
        top = int(screen.y_pos - min_y)

        img_aspect = img.width / img.height
        screen_aspect = screen.width / screen.height

        # Resize maintaining aspect ratio to fit screen dimensions
        if img_aspect > screen_aspect:
            new_width = int(screen.height * img_aspect)
            new_height = screen.height
        else:
            new_width = screen.width
            new_height = int(screen.width / img_aspect)

            print(f"Resizing image to {new_width}x{new_height}...")
        img = img.resize((new_width, new_height), Resampling.LANCZOS)

        # Center crop the resized image to match screen dimensions
        left_crop = (new_width - screen.width) // 2
        top_crop = (new_height - screen.height) // 2
        right_crop = left_crop + screen.width
        bottom_crop = top_crop + screen.height

        print("Cropping image to cover area...")
        img = img.crop((left_crop, top_crop, right_crop, bottom_crop))

        print("Pasting image...")
        print(f"Pasting image at position ({left}, {top})...")
        base_image.paste(img, (left, top))

        print(f"Image for screen {index} completed.")
        print()

    base_image.save(OUTPUT_IMG)
    print(f"Wallpaper saved to {OUTPUT_IMG}")
