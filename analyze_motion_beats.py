import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_motion_beats(client, animation_name, frame_count, grid_image_path):
    base64_image = encode_image(grid_image_path)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": f"""For the animation '{animation_name}' with {frame_count} frames, analyze the key motion beats.
                        Return a clean JSON object with frame numbers and descriptions.
                        Format: {{"beats": [{{"frame": 1, "description": "start"}}, {{"frame": N, "description": "end"}}]}}"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/webp;base64,{base64_image}"}
                    }
                ]
            }],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        # Remove any markdown formatting if present
        content = content.replace('```json\n', '').replace('\n```', '')
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error for {animation_name}: {e}")
        print(f"Raw response: {content}")
        return None
    except Exception as e:
        print(f"Error analyzing {animation_name}: {e}")
        return None

def update_animation_json(json_path):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        with open(json_path, 'r') as f:
            animation_data = json.load(f)
            
        if 'motion_beats' in animation_data:
            print(f"Skipping {json_path} - already has motion beats")
            return
            
        base_name = os.path.splitext(json_path)[0]
        grid_image_path = f"{base_name}_grid.webp"
        
        if not os.path.exists(grid_image_path):
            print(f"Missing grid image for {json_path}")
            return
            
        print(f"Sending prompt to OpenAI for animation '{animation_data['name']}' with {animation_data['length']['frame_count']} frames.")
        
        beats = analyze_motion_beats(
            client,
            animation_data['name'],
            int(animation_data['length']['frame_count']),
            grid_image_path
        )
        
        if beats:
            animation_data['motion_beats'] = beats['beats']
            with open(json_path, 'w') as f:
                json.dump(animation_data, f, indent=4)
            print(f"Successfully added motion beats to: {animation_data['name']}")
            
    except Exception as e:
        print(f"Error processing {json_path}: {e}")

def process_directory(directory_path):
    try:
        for file in os.listdir(directory_path):
            if file.endswith('.json') and not file.endswith('_grid.json'):
                json_path = os.path.join(directory_path, file)
                try:
                    update_animation_json(json_path)
                except Exception as e:
                    print(f"Error processing {file}: {e}")
                    continue
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        print(f"Directory processing error: {e}")

if __name__ == "__main__":
    processed_dir = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\processed"
    process_directory(processed_dir)