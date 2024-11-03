import os
import json
import re
import base64
import subprocess
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def describe_animation(grid_image_path):
    # Open the grid image
    grid_image = Image.open(grid_image_path)
    
    # Extract the base name from the file path
    base_name = os.path.basename(grid_image_path)
    base_name = os.path.splitext(base_name)[0]
    
    # Encode the image as a base64 string
    base64_image = encode_image(grid_image_path)
    
    # Generate a prompt based on the file name
    prompt = f"The image '{base_name}' is a numbered grid of images representing the action happening within an FBX animation file, frame by frame. "
    prompt += "Please describe the action happening in the animation based on the grid image and the file name. Do not reference the grid image or file name. Just respond with the description concisely. Do not return the context of the prompt. Just return the description of what's happening in the fbx file. Just describe the action."

    # Send the prompt and image to ChatGPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ],
            }
        ],
        max_tokens=300
    )

    # Extract the description from the response
    description = response.choices[0].message.content.strip()

    # Extract action words from the file name
    action_words = re.findall(r'\b\w+\b', base_name)
    action_prompt = " ".join(action_words)
    
    # Generate a brief action word(s) to describe what's happening
    brief_action = action_words[-1] if action_words else "action"
    
    return base_name, description, action_prompt, brief_action

def get_animation_length(fbx_file_path):
    script_path = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\blender_fbx_test.py"
    blender_executable = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"  # Adjust the path to your Blender executable

    command = [
        blender_executable,
        "--background",
        "--python", script_path,
        "--", fbx_file_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout

    # Extract frame count, duration, and frame rate from the output
    frame_count = None
    duration_seconds = None
    frame_rate = None

    for line in output.splitlines():
        if "Frame Count:" in line:
            frame_count = float(line.split(":")[1].strip())
        elif "Duration (seconds):" in line:
            duration_seconds = float(line.split(":")[1].strip())
        elif "Frame Rate:" in line:
            frame_rate = float(line.split(":")[1].strip())

    if frame_count is None or duration_seconds is None or frame_rate is None:
        raise ValueError("Failed to extract animation length from Blender output")

    return frame_count, duration_seconds, frame_rate

def create_json_file(base_name, description, action_prompt, brief_action, length, output_dir):
    # Remove '_grid' from the base name for the JSON file
    base_name = base_name.replace("_grid", "")
    
    data = {
        "name": base_name,
        "description": description,
        "prompt": action_prompt,
        "brief_action": brief_action,
        "length": length
    }
    
    json_file_path = os.path.join(output_dir, f"{base_name}.json")
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Created JSON file: {json_file_path}")

if __name__ == "__main__":
    processed_dir = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\Animations3"
    
    # Iterate over all grid image files in the processed directory
    for grid_image_file in os.listdir(processed_dir):
        if grid_image_file.endswith("_grid.webp"):
            grid_image_path = os.path.join(processed_dir, grid_image_file)
            
            # Get the corresponding .fbx file path
            base_name = os.path.splitext(grid_image_file)[0].replace("_grid", "")
            fbx_file_path = os.path.join(processed_dir, f"{base_name}.fbx")
            
            # Get the animation length and print the result
            print(f"Analyzing FBX file: {fbx_file_path}")
            frame_count, duration_seconds, frame_rate = get_animation_length(fbx_file_path)
            print(f"Animation Length Results:")
            print(f"  Frame Count: {frame_count}")
            print(f"  Duration (seconds): {duration_seconds:.2f}")
            print(f"  Frame Rate: {frame_rate:.2f}")
            
            # Describe the animation
            base_name, description, action_prompt, brief_action = describe_animation(grid_image_path)
            
            # Create the JSON file
            create_json_file(base_name, description, action_prompt, brief_action, 
                             {"frame_count": frame_count, "duration_seconds": duration_seconds, "frame_rate": frame_rate}, 
                             processed_dir)