import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv
from glob import glob

# Load environment variables from .env file
load_dotenv()

def encode_image(image_path):
    """Encode image as base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_motion_beats(client, animation_name, frame_count, grid_image_path):
    """Get motion beat analysis using both metadata and grid image"""
    
    # Encode the grid image
    base64_image = encode_image(grid_image_path)
    
    prompt = f"""Analyze the key motion beats for the animation '{animation_name}' with {frame_count} frames.
    The grid image shows numbered frames of the animation sequence.
    Return a JSON array of frame numbers and descriptions of key poses.
    Focus on major pose changes and key moments in the animation.
    Format as: {{"beats": [
        {{"frame": 1, "description": "starting pose"}},
        {{"frame": N, "description": "key pose"}}
    ]}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/webp;base64,{base64_image}"}
                    }
                ]
            }],
            max_tokens=500
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error analyzing motion beats: {e}")
        return None

def update_animation_json(json_path):
    """Update existing JSON file with motion beat annotations"""
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        # Read existing JSON
        with open(json_path, 'r') as f:
            animation_data = json.load(f)
            
        # Skip if already has motion beats
        if 'motion_beats' in animation_data:
            print(f"Skipping {json_path} - already has motion beats")
            return
            
        # Get corresponding grid image path
        base_name = os.path.splitext(json_path)[0]
        grid_image_path = f"{base_name}_grid.webp"
        
        if not os.path.exists(grid_image_path):
            print(f"Missing grid image for {json_path}")
            return
            
        # Get motion beat analysis
        beats = analyze_motion_beats(
            client,
            animation_data['name'],
            int(animation_data['length']['frame_count']),
            grid_image_path
        )
        
        if beats:
            # Add motion beats to the JSON
            animation_data['motion_beats'] = beats['beats']
            
            # Write updated JSON back to file
            with open(json_path, 'w') as f:
                json.dump(animation_data, f, indent=4)
                
            print(f"Successfully added motion beats to: {animation_data['name']}")
            
    except Exception as e:
        print(f"Error processing {json_path}: {e}")

def process_directory(directory_path):
    """Process all JSON files in the given directory"""
    
    # Find all JSON files
    for file in os.listdir(directory_path):
        if file.endswith('.json') and not file.endswith('_grid.json'):
            json_path = os.path.join(directory_path, file)
            update_animation_json(json_path)

if __name__ == "__main__":
    processed_dir = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\processed"
    process_directory(processed_dir)