import os
import shutil
import re

def move_unique_assets(source_dir, dest_dir, max_assets=None):
    print(f"Source directory: {source_dir}")
    print(f"Destination directory: {dest_dir}")
    print(f"Max assets to move: {max_assets}")

    if not os.path.exists(dest_dir):
        print(f"Destination directory does not exist. Creating: {dest_dir}")
        os.makedirs(dest_dir)
    
    # Dictionary to keep track of moved assets
    moved_assets = {}
    moved_count = 0

    # Regular expression to match FBX filenames with optional numbers in parentheses
    pattern = re.compile(r'^(.*?)( \(\d+\))?\.fbx$', re.IGNORECASE)

    print(f"Listing files in source directory: {source_dir}")
    for filename in sorted(os.listdir(source_dir)):
        print(f"Checking file: {filename}")
        if max_assets is not None and moved_count >= max_assets:
            print(f"Reached max assets limit: {max_assets}")
            break

        match = pattern.match(filename)
        if match:
            base_name = match.group(1)
            
            # Use base_name as key, ignoring numbers in parentheses
            asset_key = base_name.lower()

            if asset_key not in moved_assets:
                source_path = os.path.join(source_dir, filename)
                new_filename = f"{base_name}.fbx"
                dest_path = os.path.join(dest_dir, new_filename)
                print(f"Moving {source_path} to {dest_path}")
                shutil.move(source_path, dest_path)
                moved_assets[asset_key] = True
                moved_count += 1
                print(f"Moved: {filename} to {new_filename}")
            else:
                print(f"Asset {base_name} already moved. Skipping.")
        else:
            print(f"Filename {filename} is not an FBX file or doesn't match pattern. Skipping.")

    print(f"Total assets moved: {moved_count}")

if __name__ == "__main__":
    source_directory = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\Animations"
    destination_directory = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\processed"
    move_unique_assets(source_directory, destination_directory, max_assets=10000)