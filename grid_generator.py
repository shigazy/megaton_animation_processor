from PIL import Image, ImageDraw, ImageFont
import os

def create_8k_grid(frames, output_path):
    # Calculate grid dimensions
    num_frames = len(frames)
    grid_size = int(num_frames ** 0.5) + 1
    
    # Create a new 8K image
    grid_image = Image.new('RGB', (4320, 7680), (255, 255, 255))  # White background
    
    # Calculate thumbnail size
    thumb_width = 4320 // grid_size
    thumb_height = 7680 // grid_size
    
    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 60)  # Increase font size
    except IOError:
        font = ImageFont.load_default()
    
    for i, frame in enumerate(frames):
        img = Image.open(frame)
        # Replace ANTIALIAS with LANCZOS
        img = img.resize((thumb_width, thumb_height), Image.LANCZOS)
        
        # Draw the frame number
        draw = ImageDraw.Draw(img)
        text = str(i + 1)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        text_position = (thumb_width - text_width - 5, 5)  # Top right corner with a small margin
        draw.text(text_position, text, fill="cyan", font=font)  # Change text color to cyan
        
        x = (i % grid_size) * thumb_width
        y = (i // grid_size) * thumb_height
        
        grid_image.paste(img, (x, y))
    
    # Save the grid image as PNG
    grid_image.save(output_path, "PNG")
    
    # Convert the PNG to WebP
    webp_output_path = output_path.replace(".png", ".webp")
    grid_image.save(webp_output_path, "WEBP")
    
    # Delete the PNG and GIF files
    if os.path.exists(output_path):
        os.remove(output_path)
    for frame in frames:
        if frame.endswith(".gif") and os.path.exists(frame):
            os.remove(frame)