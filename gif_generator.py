import subprocess
from PIL import Image

def create_gif(frames, output_path, duration=100):
    images = []
    for frame in frames:
        img = Image.open(frame)
        # Replace ANTIALIAS with LANCZOS
        img = img.resize((360, 640), Image.LANCZOS)
        images.append(img)
    
    images[0].save(output_path, save_all=True, append_images=images[1:], duration=duration, loop=0)

def convert_to_webp(gif_path, webp_path):
    subprocess.run([
        "ffmpeg", "-i", gif_path, 
        "-vcodec", "libwebp", "-lossless", "0", "-compression_level", "6",
        "-q:v", "90", "-loop", "0", "-preset", "picture", "-an", "-vsync", "0",
        webp_path
    ])