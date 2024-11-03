import json
import os

def add_type_to_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            # Add the "type": "rpm" field if it doesn't exist
            if 'type' not in data:
                data['type'] = "rpm"
            
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            
            print(f"Updated {filename}")

# Specify the directory containing the JSON files
directory = "processed"

add_type_to_json_files(directory)
print("All JSON files have been updated.")