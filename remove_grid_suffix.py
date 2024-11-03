import os
import json

def remove_grid_suffix(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            # Remove "_grid" from "prompt" and "brief_action" fields
            if "prompt" in data:
                data["prompt"] = data["prompt"].replace("_grid", "")
            if "brief_action" in data:
                data["brief_action"] = data["brief_action"].replace("_grid", "")
            
            # Write the updated data back to the file
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            
            print(f"Updated: {filename}")

if __name__ == "__main__":
    processed_dir = "processed"  # Change this to the actual directory path if different
    remove_grid_suffix(processed_dir)
    print("All .json files have been processed.")