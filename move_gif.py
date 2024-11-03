import os
import shutil

def move_gifs_to_subfolder(source_dir, gif_subfolder="GIF"):
    # Create the GIF subfolder if it doesn't exist
    gif_dir = os.path.join(source_dir, gif_subfolder)
    os.makedirs(gif_dir, exist_ok=True)

    # Iterate through files in the source directory
    for filename in os.listdir(source_dir):
        if filename.lower().endswith('.gif'):
            source_path = os.path.join(source_dir, filename)
            destination_path = os.path.join(gif_dir, filename)
            
            # Move the GIF file
            shutil.move(source_path, destination_path)
            print(f"Moved: {filename} to {gif_subfolder}/")

def main():
    output_dir = r"C:/Users/higaz/OneDrive/Desktop/Animation Package/gif/"
    move_gifs_to_subfolder(output_dir)
    print("All GIF files have been moved to the GIF subfolder.")

if __name__ == "__main__":
    main()