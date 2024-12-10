import os
import subprocess
import tempfile

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

def render_animation(fbx_file, animation, output_dir, character_fbx_file):
    # Create a subdirectory for the current animation within the output directory
    animation_name = os.path.splitext(os.path.basename(fbx_file))[0]
    temp_dir = os.path.join(output_dir, f"{animation_name}_frames")
    os.makedirs(temp_dir, exist_ok=True)
    # Create a temporary Python script for Blender
    script_content = f"""
import bpy
import os
import math

def render_animation(character_fbx_file, animation_fbx_file, animation, output_dir):
    print(f"Starting render_animation function")
    print(f"Character FBX file: {{character_fbx_file}}")
    print(f"Animation FBX file: {{animation_fbx_file}}")
    print(f"Animation: {{animation}}")
    print(f"Output directory: {{output_dir}}")

    # Set up the Blender scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import the character FBX file
    bpy.ops.import_scene.fbx(filepath=character_fbx_file)
    
    # Find the imported armature and mesh
    armature = None
    body_mesh = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
        elif obj.type == 'MESH' and obj.name == 'Wolf3D_Body':
            body_mesh = obj
        if armature and body_mesh:
            break
    
    if not (armature and body_mesh):
        print("Error: Armature or Wolf3D_Body mesh not found in the imported FBX.")
        return
    
    print(f"Armature found: {{armature.name}}")
    print(f"Body mesh found: {{body_mesh.name}}")
    
    # Store existing objects
    existing_objects = set(bpy.data.objects.keys())
    
    # Import the animation FBX file
    bpy.ops.import_scene.fbx(filepath=animation_fbx_file)
    
    # Find the imported armature from the animation FBX
    fbx_armature = None
    for obj in bpy.data.objects:
        if obj.name not in existing_objects and obj.type == 'ARMATURE':
            fbx_armature = obj
            break
    
    if not fbx_armature:
        print("Error: No armature found in imported animation FBX.")
        return
    
    print(f"FBX Armature found: {{fbx_armature.name}}")
    
    # Transfer animation from FBX armature to character armature
    if fbx_armature.animation_data and fbx_armature.animation_data.action:
        action = fbx_armature.animation_data.action
        action.name = "Transferred_Action"
        
        # Ensure the character armature has animation_data
        if not armature.animation_data:
            armature.animation_data_create()
        
        # Apply the action to the character armature
        armature.animation_data.action = action
        print(f"Applied action: {{action.name}}")
    else:
        print("Error: No animation data found in FBX armature.")
        return
    
    # Delete the imported animation FBX objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name not in existing_objects:
            obj.select_set(True)
    bpy.ops.object.delete()
    
    # Manually set the 3D cursor to the center of the body mesh
    bpy.context.scene.cursor.location = body_mesh.location
    
    # Add a camera and parent it to the armature
    bpy.ops.object.camera_add(location=(0, -3.75, 0.8))  # Move the camera forward and higher up
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(90), 0, 0)  # Rotate 45 degrees to be slightly tilted
    
    # Set the camera as the active camera for rendering
    bpy.context.scene.camera = camera
    
    
    # Add lighting
    bpy.ops.object.light_add(type='SUN', location=(0, -5, 5))  # Move the sun in front of the character
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    sun.rotation_euler = (math.radians(45), 0, 0)  # Adjust the rotation to face the character
    
    # Add a point light near the character
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 2))  # Adjust the location as needed
    point_light = bpy.context.active_object
    point_light.data.energy = 5.0  # Adjust the energy as needed
    
    # Add a plane for the ground
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    plane = bpy.context.active_object
    
    # Create a new material with the darker and more saturated purple color
    mat = bpy.data.materials.new(name="PurpleMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.5, 0.0, 1.0, 1.0)  # Darker and more saturated purple color
    
    # Assign the material to the plane
    if plane.data.materials:
        plane.data.materials[0] = mat
    else:
        plane.data.materials.append(mat)
    
    # Set up rendering parameters
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.eevee.taa_render_samples = 16
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 720
    scene.render.resolution_y = 1280
    
    # Set the background color to darker and more saturated purple (#8000FF)
    bpy.context.scene.world.use_nodes = True
    bg_node = bpy.context.scene.world.node_tree.nodes['Background']
    bg_node.inputs['Color'].default_value = (0.5, 0.0, 1.0, 1.0)  # Darker and more saturated purple background
    bg_node.inputs['Strength'].default_value = 0.1  # Reduce the strength of the background light
    
    # Set frame range
    scene.frame_start = animation["start"]
    scene.frame_end = animation["end"]
    
    # Ensure all objects are visible
    for obj in bpy.data.objects:
        obj.hide_render = False
        obj.hide_viewport = False
    
    # Render the animation
    for frame in range(animation["start"], animation["end"] + 1):
        scene.frame_set(frame)
        scene.render.filepath = os.path.join(output_dir, f"frame_{{frame:04d}}")
        bpy.ops.render.render(write_still=True)

    print(f"Rendering completed. Frames saved in {{output_dir}}")

# Call the function
render_animation({repr(character_fbx_file)}, {repr(fbx_file)}, {repr(animation)}, {repr(temp_dir)})
"""  # Closing the triple-quoted f-string literal

    # Write the script to a file in the temporary directory
    script_path = os.path.join(temp_dir, f"{animation_name}_blender_script.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Run Blender with the script
    subprocess.run([BLENDER_PATH, "--background", "--python", script_path])
    
    # The frames should now be in the temporary directory
    frames = [os.path.join(temp_dir, f"frame_{frame:04d}.png") for frame in range(animation["start"], animation["end"] + 1)]
    return frames, temp_dir