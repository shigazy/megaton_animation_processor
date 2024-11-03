import subprocess
import os

def run_blender_script(script_path, fbx_file_path):
    blender_executable = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"  # Adjust the path to your Blender executable
    command = [
        blender_executable,
        "--background",  # Run Blender in the background
        "--python", script_path,  # Specify the Python script to run
        "--", fbx_file_path  # Pass additional arguments to the script
    ]
    subprocess.run(command, check=True)

if __name__ == "__main__":
    script_path = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\blender_fbx_test.py"
    fbx_file_path = r"C:\Users\higaz\OneDrive\Desktop\Animation Package\processed\Zombie Walking.fbx"
    run_blender_script(script_path, fbx_file_path)